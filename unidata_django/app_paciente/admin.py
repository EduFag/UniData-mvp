from django.contrib import admin
from .models import Paciente

admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    # --- Configuração da Tabela ---
    list_display = ('get_nome', 'cpf', 'endereco_eth')
    search_fields = ('user__first_name', 'user__email', 'cpf')
    
    # Removemos as actions em massa conforme solicitado
    actions = []

    def get_nome(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_nome.short_description = 'Nome Completo'

