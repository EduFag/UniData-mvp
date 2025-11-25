from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import CadastroForm, LoginForm
from .models import Paciente
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
    """View para cadastrar um novo paciente."""
    if request.method == 'POST':
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
                
                # Aceita 200
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
            
            Paciente.objects.create(
                user=user,  # <--- Liga ao usuário
                cpf=dados["cpf"],
                endereco_eth=endereco_eth
            )

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

