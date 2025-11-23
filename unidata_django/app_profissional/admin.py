from django.contrib import admin
from .models import Profissional

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    # Campos que serão mostrados na tabela
    list_display = ('get_nome', 'get_email', 'crm', 'cpf', 'autorizado', 'endereco_eth')
    
    # Filtros laterais
    list_filter = ('autorizado',)
    
    # Campo de busca
    search_fields = ('user__first_name', 'user__email', 'crm', 'cpf')

    def get_nome(self, obj):
        return obj.user.first_name
    get_nome.short_description = 'Nome'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'E-mail'