from django.contrib import admin
from .models import Pessoa


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'email', 'endereco_carteira', 'criado_em']
    search_fields = ['nome', 'cpf', 'email']
    list_filter = ['criado_em']
    readonly_fields = ['criado_em', 'atualizado_em']




