import requests
from django.contrib import admin
from django.contrib import messages
from .models import Profissional, Atendimento

# Ajuste se sua API estiver em outra porta/url
API_URL = "http://localhost:8000"

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    # --- Configuração da Tabela ---
    list_display = ('get_nome', 'crm', 'cpf', 'autorizado', 'endereco_eth')
    list_editable = ('autorizado',)
    list_filter = ('autorizado',)
    search_fields = ('user__first_name', 'user__email', 'crm', 'cpf')
    
    # Removemos as actions em massa conforme solicitado
    actions = []

    def get_nome(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_nome.short_description = 'Nome Completo'

    def save_model(self, request, obj, form, change):
        if 'autorizado' in form.changed_data:
            
            if not obj.endereco_eth:
                messages.error(request, f"ERRO: O médico {obj.user.first_name} não possui endereço ETH (Carteira). Não é possível autorizar na Blockchain.")
                return 

            sucesso_api = self.chamar_api_autorizacao(obj.endereco_eth, obj.autorizado)

            if sucesso_api:
                super().save_model(request, obj, form, change)
                
                estado = "AUTORIZADO" if obj.autorizado else "DESAUTORIZADO"
                messages.success(request, f"Sucesso! Profissional {estado} na Blockchain e salvo no sistema.")
            else:
                messages.error(request, "FALHA CRÍTICA: A API Blockchain retornou erro ou está offline. O status NÃO foi alterado no banco de dados.")
        
        else:
            super().save_model(request, obj, form, change)

    def chamar_api_autorizacao(self, address, status_booleano):
        endpoint = f"{API_URL}/autorizar-profissional"
        payload = {
            "address_profissional": address,
            "autorizado": status_booleano
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            
            if response.status_code == 200:
                return True
            else:
                # Loga o erro no console do servidor para debug
                print(f"Erro API Blockchain: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"Erro de Conexão: {e}")
            return False

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('profissional', 'paciente', 'data_ultimo_acesso')
    list_filter = ('data_ultimo_acesso',)