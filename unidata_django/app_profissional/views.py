from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CadastroForm, LoginForm
from .models import Profissional
from django.contrib.auth import logout as django_logout
import requests

API_URL = "http://localhost:8001"  # exemplo

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)

        if form.is_valid():
            profissional = form.save(commit=False)
            profissional.set_password(form.cleaned_data["password"])

            # 1. Cria a carteira via API
            resp = requests.post(f"{API_URL}/gerar-carteira", json={
                "cpf": profissional.email  # ou outro identificador único
            })

            if resp.status_code != 200:
                form.add_error(None, "Erro ao gerar carteira na API.")
                return render(request, "cadastro.html", {"form": form})

            carteira = resp.json()

            # 2. Salva endereço ETH no Django
            profissional.endereco_eth = carteira["endereco"]

            # 3. profissional.autorizado = False (não pode se autorizar)
            profissional.save()

            return redirect("login")

    else:
        form = CadastroForm()

    return render(request, "app_profissional/cadastro.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("dashboard")
    else:
        form = LoginForm()

    return render(request, "app_profissional/login.html", {"form": form})

def logout(request):
    django_logout(request)
    return redirect("login")