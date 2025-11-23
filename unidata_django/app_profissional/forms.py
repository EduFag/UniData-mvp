from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)

            if not user:
                raise forms.ValidationError("Credenciais inválidas.")

            # VERIFICAÇÃO DE SEGURANÇA:
            # 1. Checa se esse usuário é realmente um médico (tem perfil profissional)
            if not hasattr(user, 'profissional'):
                raise forms.ValidationError("Este usuário não é um médico.")

            # 2. Checa se está autorizado (acessando a relação .profissional)
            if not user.profissional.autorizado:
                raise forms.ValidationError("Seu acesso ainda não foi autorizado pela administração.")

            self.user = user
        
        return self.cleaned_data


class CadastroForm(forms.Form):
    nome = forms.CharField(label="Nome Completo")
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    
    cpf = forms.CharField(label="CPF")
    crm = forms.CharField(label="CRM")

    # Validação para não deixar criar dois emails iguais
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email