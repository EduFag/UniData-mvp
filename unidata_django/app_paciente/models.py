from django.db import models
from django.contrib.auth.models import User


class Paciente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente')

    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF')
    endereco_eth = models.CharField(max_length=42, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.cpf})'




