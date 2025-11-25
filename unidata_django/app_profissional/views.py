from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import CadastroForm, LoginForm
from .models import Profissional, Atendimento
from app_paciente.models import Paciente
from django.contrib.auth.decorators import login_required
import requests
from django.contrib import messages

API_URL = "http://localhost:8000"

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=dados["email"],
                    email=dados["email"],
                    password=dados["password"],
                    first_name=dados["nome"]
                )
            except Exception as e:
                form.add_error(None, f"Erro ao criar usuário: {e}")
                return render(request, "app_profissional/cadastro.html", {"form": form})

            endpoint = f"{API_URL}/gerar-carteira"
            payload = {"cpf": dados["cpf"]} 

            try:
                resp = requests.post(endpoint, json=payload)
                
                if resp.status_code != 200:
                    user.delete()
                    print(f"Erro API: {resp.text}")
                    form.add_error(None, "Erro ao gerar carteira na API.")
                    return render(request, "app_profissional/cadastro.html", {"form": form})

                carteira = resp.json()
                endereco_eth = carteira.get("address") or carteira.get("endereco")
            
            except requests.ConnectionError:
                user.delete()
                form.add_error(None, "A API Blockchain está offline.")
                return render(request, "app_profissional/cadastro.html", {"form": form})

            Profissional.objects.create(
                user=user,  # <--- Liga ao usuário
                cpf=dados["cpf"],
                crm=dados["crm"],
                endereco_eth=endereco_eth,
                autorizado=False # Padrão é falso
            )

            # Redireciona para o login
            return redirect("login_profissional")
    else:
        form = CadastroForm()

    return render(request, "app_profissional/cadastro.html", {"form": form})


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect("dashboard_profissional")
    else:
        form = LoginForm()

    return render(request, "app_profissional/login.html", {"form": form})


def logout(request):
    auth_logout(request)
    return redirect("login_profissional")


@login_required(login_url="login")
def dashboard(request):
    # Tenta pegar o perfil profissional do usuário logado
    try:
        perfil = request.user.profissional 
    except AttributeError:
        return render(request, "app_profissional/erro_perfil.html", {
            "mensagem": "Este usuário não possui perfil de médico associado."
        })
    lista_atendimentos = perfil.atendimentos.select_related('paciente', 'paciente__user').all()

    context = {
        "usuario": request.user,      # Dados de Login (Nome, Email)
        "profissional": perfil,       # Dados Médicos (CRM, ETH Address, CPF)
        "meus_pacientes": lista_atendimentos
    }
    
    return render(request, "app_profissional/dashboard.html", context)


@login_required(login_url="login")
def ver_prontuario(request, paciente_id):
    medico = request.user.profissional
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    autorizado = False
    historico = []

    try:
        resp = requests.get(
            f"{API_URL}/checar-consentimento",
            params={
                "address_paciente": paciente.endereco_eth,
                "address_profissional": medico.endereco_eth
            },
            timeout=5
        )
        if resp.status_code == 200:
            autorizado = resp.json().get("autorizado", False)
    except requests.RequestException:
        messages.error(request, "Erro ao conectar com a Blockchain para verificar permissão.")

    if autorizado:
        try:
            resp_lista = requests.get(
                f"{API_URL}/listar-prontuarios",
                params={"address_paciente": paciente.endereco_eth},
                timeout=5
            )
            if resp_lista.status_code == 200:
                historico = resp_lista.json().get("prontuarios", [])
        except requests.RequestException:
            messages.warning(request, "Não foi possível carregar o histórico de prontuários.")

        if request.method == "POST":
            cid = request.POST.get("cid")
            id_prontuario_str = request.POST.get("id_prontuario")

            # Converte ID: string vazia vira None (criação), número vira int (atualização)
            id_prontuario = int(id_prontuario_str) if id_prontuario_str else None

            payload = {
                "id": id_prontuario,
                "endereco_paciente": paciente.endereco_eth,
                "cid": cid,
                "endereco_profissional": medico.endereco_eth
            }

            try:
                resp_save = requests.post(f"{API_URL}/registrar-prontuario", json=payload, timeout=10)
                
                if resp_save.status_code == 200:
                    data = resp_save.json()
                    tx_hash = data.get("tx_hash", "0x...")
                    tipo_msg = "atualizado" if id_prontuario else "criado"
                    
                    messages.success(request, f"Prontuário {tipo_msg} com sucesso! Tx: {tx_hash}")
                    return redirect('ver_prontuario', paciente_id=paciente.id)
                else:
                    # Tenta ler mensagem de erro da API
                    erro_msg = resp_save.json().get("detail", "Erro desconhecido na API")
                    messages.error(request, f"Falha ao salvar: {erro_msg}")

            except requests.RequestException:
                messages.error(request, "Erro de conexão ao tentar salvar na Blockchain.")

    # Renderiza o template
    return render(request, "app_profissional/prontuario.html", {
        "paciente": paciente,
        "medico": medico,
        "historico": historico,
        "autorizado": autorizado
    })


@login_required(login_url="login")
def buscar_paciente(request):
    if request.method == "POST":
        cpf_busca = request.POST.get("cpf")
        
        # Garante que temos o perfil do médico
        try:
            medico = request.user.profissional
        except AttributeError:
            messages.error(request, "Erro: Perfil médico não identificado.")
            return redirect('dashboard_profissional')

        # Tenta encontrar o paciente no banco de dados local
        try:
            # Remove pontos e traços caso o usuário tenha digitado
            cpf_limpo = cpf_busca.replace(".", "").replace("-", "").strip()            
            paciente = Paciente.objects.get(cpf=cpf_limpo)
            
            obj, created = Atendimento.objects.get_or_create(
                profissional=medico,
                paciente=paciente
            )
            
            if created:
                messages.success(request, f"Paciente {paciente.user.first_name} adicionado à sua lista!")
            
            # Redireciona direto para a tela de prontuário desse paciente
            return redirect('ver_prontuario', paciente_id=paciente.id)
            
        except Paciente.DoesNotExist:
            messages.error(request, f"Paciente com CPF {cpf_busca} não encontrado no sistema. Ele precisa se cadastrar no App do Paciente primeiro.")
            
    # Se não for POST ou der erro, volta pro dashboard
    return redirect('dashboard_profissional')