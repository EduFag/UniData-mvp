from django import forms
from django.contrib.auth import authenticate
from .models import Profissional

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        user = authenticate(email=email, password=password)

        if not user:
            raise forms.ValidationError("Credenciais inválidas")

        if not user.autorizado:
            raise forms.ValidationError("Seu acesso ainda não foi autorizado pela administração.")

        self.user = user
        return self.cleaned_data


class CadastroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profissional
        fields = ["email", "nome", "cpf", "crm", "password"]  
        # NÃO inclui endereco_eth nem autorizado

    def save(self, commit=True):
        profissional = super().save(commit=False)
        profissional.set_password(self.cleaned_data["password"])
        if commit:
            profissional.save()
        return profissional
