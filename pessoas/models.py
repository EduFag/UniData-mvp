from django.db import models


class Pessoa(models.Model):
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF')
    nome = models.CharField(max_length=200, verbose_name='Nome Completo')
    email = models.EmailField(verbose_name='E-mail', blank=True, null=True)
    telefone = models.CharField(max_length=20, verbose_name='Telefone', blank=True, null=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento', blank=True, null=True)
    endereco_carteira = models.CharField(max_length=42, verbose_name='Endereço da Carteira', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} ({self.cpf})'




