from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .models import Pessoa
from .forms import PessoaForm, PacienteLoginForm, PacienteCadastroForm
import sys
import os
import requests

# Adiciona o diretório raiz do projeto ao path para importar o wallet_service
project_root = os.path.abspath(os.path.join(str(settings.BASE_DIR), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from API.services.wallet_service import criar_carteira, obter_carteira

API_URL = "http://localhost:8001"


def cadastrar_pessoa(request):
    """View para cadastrar uma nova pessoa."""
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, f'Pessoa {pessoa.nome} cadastrada com sucesso!')
            return redirect('pessoas:listar_pessoas')
    else:
        form = PessoaForm()
    
    return render(request, 'app_paciente/cadastrar_pessoa.html', {'form': form})


def listar_pessoas(request):
    """View para listar todas as pessoas cadastradas."""
    pessoas = Pessoa.objects.all()
    return render(request, 'app_paciente/listar_pessoas.html', {'pessoas': pessoas})


def gerar_carteira(request, pessoa_id):
    """View para gerar uma carteira para uma pessoa."""
    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    
    # Verifica se a pessoa já tem uma carteira
    if pessoa.endereco_carteira:
        messages.warning(request, f'A pessoa {pessoa.nome} já possui uma carteira: {pessoa.endereco_carteira}')
        return redirect('pessoas:listar_pessoas')
    
    try:
        # Gera a carteira usando o wallet_service
        resultado = criar_carteira(pessoa.cpf)
        
        # Atualiza a pessoa com o endereço da carteira
        pessoa.endereco_carteira = resultado['endereco']
        pessoa.save()
        
        messages.success(request, f'Carteira gerada com sucesso para {pessoa.nome}!')
        messages.info(request, f'Endereço da carteira: {resultado["endereco"]}')
        
    except ValueError as e:
        messages.error(request, f'Erro ao gerar carteira: {str(e)}')
    except Exception as e:
        messages.error(request, f'Erro inesperado: {str(e)}')
    
    return redirect('pessoas:listar_pessoas')


def gerar_carteira_form(request):
    """View para exibir formulário de seleção de pessoa para gerar carteira."""
    pessoas = Pessoa.objects.filter(endereco_carteira__isnull=True)
    
    if request.method == 'POST':
        pessoa_id = request.POST.get('pessoa_id')
        if pessoa_id:
            return redirect('pessoas:gerar_carteira', pessoa_id=pessoa_id)
        else:
            messages.error(request, 'Por favor, selecione uma pessoa.')
    
    return render(request, 'app_paciente/gerar_carteira.html', {'pessoas': pessoas})


def paciente_login(request):
    """View de login para pacientes - verifica se tem carteira cadastrada."""
    if request.method == "POST":
        form = PacienteLoginForm(request.POST)
        
        if form.is_valid():
            cpf = form.cleaned_data["cpf"]
            
            try:
                # Tenta obter a carteira existente
                carteira = obter_carteira(cpf)
                if carteira:
                    # Carteira existe, redireciona para dashboard do paciente
                    messages.success(request, f"Login realizado com sucesso!")
                    # Armazena o CPF na sessão (sem salvar no banco)
                    request.session['paciente_cpf'] = cpf
                    request.session['paciente_endereco'] = carteira["endereco"]
                    return redirect('pessoas:dashboard')
            except ValueError:
                # Carteira não existe, redireciona para cadastro
                messages.info(request, "Carteira não encontrada. Por favor, faça o cadastro primeiro.")
                return redirect('pessoas:cadastro')
            except Exception as e:
                form.add_error(None, f"Erro ao verificar carteira: {str(e)}")
    else:
        form = PacienteLoginForm()
    
    return render(request, "app_paciente/login.html", {"form": form})


def paciente_cadastro(request):
    """View de cadastro para pacientes - apenas gera carteira, não salva no banco."""
    if request.method == "POST":
        form = PacienteCadastroForm(request.POST)
        
        if form.is_valid():
            dados = form.cleaned_data
            cpf = dados["cpf"]
            
            try:
                # Gera a carteira via API
                endpoint = f"{API_URL}/gerar-carteira"
                payload = {"cpf": cpf}
                
                resp = requests.post(endpoint, json=payload, timeout=10)
                
                if resp.status_code in [200, 201]:
                    carteira = resp.json()
                    endereco_eth = carteira.get("address") or carteira.get("endereco")
                    
                    # Armazena na sessão (sem salvar no banco Django)
                    request.session['paciente_cpf'] = cpf
                    request.session['paciente_nome'] = dados["nome"]
                    request.session['paciente_email'] = dados.get("email", "")
                    request.session['paciente_endereco'] = endereco_eth
                    
                    messages.success(request, "Cadastro realizado com sucesso! Sua carteira foi criada.")
                    return redirect('pessoas:dashboard')
                else:
                    error_detail = resp.text
                    try:
                        error_json = resp.json()
                        error_detail = error_json.get("detail", error_detail)
                    except:
                        pass
                    form.add_error(None, f"Erro ao gerar carteira: {error_detail}")
                    
            except requests.ConnectionError:
                form.add_error(None, "A API Blockchain está offline. Certifique-se de que a API está rodando.")
            except requests.Timeout:
                form.add_error(None, "Timeout ao conectar com a API. Tente novamente.")
            except Exception as e:
                form.add_error(None, f"Erro inesperado: {str(e)}")
    else:
        form = PacienteCadastroForm()
    
    return render(request, "app_paciente/cadastro.html", {"form": form})


def paciente_dashboard(request):
    """Dashboard do paciente - mostra informações da carteira."""
    cpf = request.session.get('paciente_cpf')
    endereco = request.session.get('paciente_endereco')
    nome = request.session.get('paciente_nome', '')
    email = request.session.get('paciente_email', '')
    
    if not cpf or not endereco:
        messages.warning(request, "Por favor, faça login primeiro.")
        return redirect('pessoas:login')
    
    context = {
        'cpf': cpf,
        'endereco': endereco,
        'nome': nome,
        'email': email,
    }
    
    return render(request, "app_paciente/dashboard.html", context)


def paciente_logout(request):
    """Logout do paciente - limpa a sessão."""
    request.session.flush()
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('pessoas:login')

