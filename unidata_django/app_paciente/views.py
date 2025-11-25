from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import CadastroForm, LoginForm
from .models import Paciente
from app_profissional.models import Profissional, Atendimento
from django.contrib.auth.decorators import login_required
import requests

from django.contrib import messages
from django.conf import settings
import sys
import os

# Adiciona o diretório raiz do projeto ao path para importar o wallet_service
project_root = os.path.abspath(os.path.join(str(settings.BASE_DIR), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from API.services.wallet_service import criar_carteira, obter_carteira

API_URL = "http://localhost:8000"


def cadastro(request):
    """View para cadastrar um novo paciente e registrá-lo na Blockchain."""
    if request.method == 'POST':
        form = CadastroForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data
            
            # 1. Cria o Usuário no Django (Auth)
            try:
                user = User.objects.create_user(
                    username=dados["email"],
                    email=dados["email"],
                    password=dados["password"],
                    first_name=dados["nome"]
                )
            except Exception as e:
                form.add_error(None, f"Erro ao criar usuário: {e}")
                return render(request, "app_paciente/cadastro.html", {"form": form})
            
            # Preparação para chamadas na API
            payload = {"cpf": dados["cpf"]}
            endereco_eth = None

            try:
                # 2. Gera a Carteira (API)
                endpoint_gerar = f"{API_URL}/gerar-carteira"
                resp_gerar = requests.post(endpoint_gerar, json=payload, timeout=10)
                
                if resp_gerar.status_code not in [200, 201]:
                    user.delete() # Rollback: apaga usuário se falhar na API
                    erro_msg = resp_gerar.json().get('detail') or resp_gerar.text
                    form.add_error(None, f"Erro ao gerar carteira: {erro_msg}")
                    return render(request, "app_paciente/cadastro.html", {"form": form})

                carteira = resp_gerar.json()
                endereco_eth = carteira.get("address") or carteira.get("endereco")

                # 3. Registra na Blockchain (API -> Smart Contract)
                endpoint_registro = f"{API_URL}/cadastrar-paciente"
                resp_registro = requests.post(endpoint_registro, json=payload, timeout=30) # Timeout maior pois blockchain demora

                if resp_registro.status_code != 200:
                    user.delete() # Rollback
                    erro_msg = resp_registro.json().get('detail') or "Erro desconhecido na blockchain"
                    form.add_error(None, f"Falha no registro Blockchain: {erro_msg}")
                    return render(request, "app_paciente/cadastro.html", {"form": form})

            except requests.RequestException as e:
                user.delete() # Rollback
                form.add_error(None, f"A API Blockchain está offline ou instável: {str(e)}")
                return render(request, "app_paciente/cadastro.html", {"form": form}) 
            
            # 4. Salva no Banco Local
            Paciente.objects.create(
                user=user,
                cpf=dados["cpf"],
                endereco_eth=endereco_eth
            )

            # Mensagem de sucesso
            messages.success(request, "Cadastro realizado e identidade registrada na Blockchain!")
            return redirect('login_paciente')
            
    else:
        form = CadastroForm()
    
    return render(request, 'app_paciente/cadastro.html', {'form': form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect("dashboard_paciente")
    else:
        form = LoginForm()

    return render(request, "app_paciente/login.html", {"form": form})

login_required(login_url="login_paciente")
def dashboard(request):
    """Dashboard do paciente - mostra informações da carteira."""
    # 1. Tenta pegar o perfil do paciente ligado ao usuário logado
    try:
        paciente = request.user.paciente
    except AttributeError:
        # Se o usuário logado for um médico ou admin (não tem perfil Paciente)
        messages.error(request, "Este usuário não é um paciente.")
        return redirect('login_paciente')

    # 2. Monta o contexto pegando dados do Banco de Dados (via ORM)
    context = {
        'cpf': paciente.cpf,
        'endereco': paciente.endereco_eth,
        'nome': request.user.first_name, # Nome vem do User
        'email': request.user.email,     # Email vem do User
        'paciente': paciente             # Passamos o objeto inteiro se precisar
    }
    
    return render(request, "app_paciente/dashboard.html", context)

def logout(request):
    """Logout do paciente - limpa a sessão."""
    auth_logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('login_paciente')

@login_required(login_url="login_paciente")
def historico_paciente(request):
    """
    Busca o histórico médico do paciente logado na Blockchain via API.
    """
    try:
        paciente = request.user.paciente
    except AttributeError:
        return redirect('login_paciente')

    historico = []
    erro_api = None

    try:
        # Chama o endpoint que criamos anteriormente
        response = requests.get(
            f"{API_URL}/listar-prontuarios",
            params={"address_paciente": paciente.endereco_eth},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            historico = data.get("prontuarios", [])
        else:
            erro_api = "Não foi possível sincronizar com a Blockchain."
            
    except requests.RequestException:
        erro_api = "API Blockchain indisponível."

    return render(request, "app_paciente/historico.html", {
        "historico": historico,
        "erro_api": erro_api,
        "paciente": paciente
    })


@login_required(login_url="login_paciente")
def gerenciar_autorizacoes(request):
    """
    Gerencia as permissões de acesso aos dados médicos.
    Usa a tabela 'Atendimento' para listar médicos vinculados.
    """
    
    # 1. Identifica o Paciente
    try:
        paciente = request.user.paciente
    except AttributeError:
        messages.error(request, "Perfil de paciente não encontrado.")
        return redirect('login_paciente')

    query = request.GET.get('q')
    
    if query:
        # Remove espaços que o usuário possa ter digitado sem querer
        crm_limpo = query.strip()
        
        # Filtra APENAS pelo CRM
        # icontains = permite digitar só uma parte do número (LIKE)
        lista_medicos_db = Profissional.objects.filter(
            crm__icontains=crm_limpo
        ).select_related('user')
        
        titulo_secao = f"Resultados para CRM '{crm_limpo}'"
    else:
        # Lista apenas médicos que já atenderam ou vão atender o paciente (Tabela Atendimento)
        atendimentos = Atendimento.objects.filter(paciente=paciente).select_related('profissional', 'profissional__user')
        
        lista_medicos_db = [a.profissional for a in atendimentos]
        titulo_secao = "Profissionais Vinculados"

    if request.method == "POST":
        medico_id = request.POST.get("medico_id")
        acao = request.POST.get("acao") # 'autorizar' ou 'revogar'
        
        try:
            medico_alvo = Profissional.objects.get(id=medico_id)
            nova_permissao = True if acao == "autorizar" else False
            
            # Lógica Inteligente:
            # Se o paciente pesquisou um médico NOVO (via busca) e clicou em 'Autorizar',
            # criamos o vínculo na tabela Atendimento.
            # Assim, da próxima vez, esse médico já aparece na lista principal.
            if query and nova_permissao:
                Atendimento.objects.get_or_create(
                    profissional=medico_alvo,
                    paciente=paciente
                )

            # --- CHAMADA PARA API (POST) ---
            payload = {
                "address_paciente": paciente.endereco_eth,
                "address_profissional": medico_alvo.endereco_eth,
                "consentimento": nova_permissao
            }
            
            try:
                response = requests.post(f"{API_URL}/set-consentimento", json=payload, timeout=30)
                
                if response.status_code == 200:
                    tx_hash = response.json().get("tx_hash", "")
                    msg_tipo = "concedida" if nova_permissao else "revogada"
                    messages.success(request, f"Permissão {msg_tipo} com sucesso! (Tx enviada)")
                else:
                    # Tenta pegar o erro detalhado
                    erro_msg = response.json().get('detail') or response.text
                    messages.error(request, f"Falha na Blockchain: {erro_msg}")
                    
            except requests.RequestException:
                messages.error(request, "Erro de conexão com a API Blockchain.")

        except Profissional.DoesNotExist:
            messages.error(request, "Médico inválido.")
            
        # Redireciona para a mesma página (limpa o POST)
        return redirect('gerenciar_autorizacoes')

    lista_final = []

    for medico in lista_medicos_db:
        if not medico.endereco_eth:
            continue # Pula médicos sem carteira configurada

        tem_acesso = False
        
        # --- CHAMADA PARA API (GET) ---
        try:
            resp = requests.get(
                f"{API_URL}/checar-consentimento",
                params={
                    "address_paciente": paciente.endereco_eth,
                    "address_profissional": medico.endereco_eth
                },
                timeout=2 # Timeout rápido para não travar a lista
            )
            
            if resp.status_code == 200:
                tem_acesso = resp.json().get("autorizado", False)
        except requests.RequestException:
            pass # Se a API falhar na leitura, assume False por segurança

        # Adiciona na lista que vai pro template
        lista_final.append({
            "obj": medico,
            "tem_acesso": tem_acesso
        })

    return render(request, "app_paciente/autorizacoes.html", {
        "lista_medicos": lista_final,
        "titulo": titulo_secao,
        "query_atual": query
    })