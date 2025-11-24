from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from .forms import CadastroForm, LoginForm
from .models import Profissional
from django.contrib.auth.decorators import login_required
import requests

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
                
                # Aceita 200 ou 201 como sucesso
                if resp.status_code != 201:
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
            return redirect("login")
    else:
        form = CadastroForm()

    return render(request, "app_profissional/cadastro.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect("dashboard")
    else:
        form = LoginForm()

    return render(request, "app_profissional/login.html", {"form": form})

def logout(request):
    auth_logout(request)
    return redirect("login")

@login_required(login_url="login")
def dashboard(request):
    # Tenta pegar o perfil profissional do usuário logado
    try:
        perfil = request.user.profissional 
    except AttributeError:
        return render(request, "app_profissional/erro_perfil.html", {
            "mensagem": "Este usuário não possui perfil de médico associado."
        })

    context = {
        "usuario": request.user,      # Dados de Login (Nome, Email)
        "profissional": perfil        # Dados Médicos (CRM, ETH Address, CPF)
    }
    
    return render(request, "app_profissional/dashboard.html", context)