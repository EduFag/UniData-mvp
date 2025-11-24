from django import forms
from .models import Pessoa
import re


class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ['cpf', 'nome', 'email', 'telefone', 'data_nascimento']
        widgets = {
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite apenas números',
                'maxlength': '11'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemplo@email.com'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'cpf': 'CPF',
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'telefone': 'Telefone',
            'data_nascimento': 'Data de Nascimento',
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf = re.sub(r'\D', '', cpf)
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve conter 11 dígitos.')
        return cpf


class PacienteLoginForm(forms.Form):
    cpf = forms.CharField(
        label="CPF",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite apenas números',
            'maxlength': '11'
        })
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf = re.sub(r'\D', '', cpf)
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve conter 11 dígitos.')
        return cpf


class PacienteCadastroForm(forms.Form):
    nome = forms.CharField(
        label="Nome Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome completo'
        })
    )
    cpf = forms.CharField(
        label="CPF",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite apenas números',
            'maxlength': '11'
        })
    )
    email = forms.EmailField(
        label="E-mail",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@email.com'
        })
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf = re.sub(r'\D', '', cpf)
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve conter 11 dígitos.')
        return cpf




