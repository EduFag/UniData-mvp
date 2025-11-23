from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profissional(models.Model):
    # O OneToOneField diz: "Cada Usuário tem apenas UM Perfil Profissional"
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profissional')
    
    cpf = models.CharField(max_length=11, unique=True)
    crm = models.CharField(max_length=20)
    endereco_eth = models.CharField(max_length=42, null=True, blank=True)
    autorizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr(a). {self.user.first_name} - {self.crm}"