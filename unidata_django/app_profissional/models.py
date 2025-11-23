from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class ProfissionalManager(BaseUserManager):
    def create_user(self, email, nome, cpf, password=None):
        if not email:
            raise ValueError("O profissional precisa de um email")

        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
            cpf=cpf
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, cpf, password=None):
        user = self.create_user(email, nome, cpf, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Profissional(AbstractBaseUser):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=11, unique=True)
    crm = models.CharField(max_length=20, blank=True, null=True)

    # ETH
    endereco_eth = models.CharField(max_length=255, blank=True, null=True)

    # Status de permissão na blockchain
    autorizado = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = ProfissionalManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cpf']

    def __str__(self):
        return self.nome

    @property
    def is_staff(self):
        return self.is_admin