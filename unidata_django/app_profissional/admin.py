from django.contrib import admin
from .models import Profissional
import requests
from django.contrib import messages

API_URL = "http://localhost:8000"

# Register your models here.

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "email", "cpf", "autorizado", "is_admin")
    search_fields = ("nome", "email", "cpf")
    list_filter = ("autorizado", "is_admin")

    def save_model(self, request, obj, form, change):
        """Chamado quando o admin clica em SALVAR no painel."""

        # Detectar se o campo 'autorizado' mudou
        autorizado_anterior = False
        if change:  # edição (não criação)
            antigo = Profissional.objects.get(pk=obj.pk)
            autorizado_anterior = antigo.autorizado

        # Rodar normalmente o save, mas só depois de verificar
        super().save_model(request, obj, form, change)

        # Caso o admin tenha marcado "autorizado" agora
        if not autorizado_anterior and obj.autorizado:
            resp = requests.post(f"{API_URL}/autorizar-profissional", json={
                "address_profissional": obj.endereco_eth,
                "bool": True
            })

            if resp.status_code == 200:
                messages.success(request, f"Profissional {obj.nome} autorizado também na blockchain.")
            else:
                messages.error(request, "Erro ao autorizar na blockchain. Permissão só foi alterada no banco Django.")