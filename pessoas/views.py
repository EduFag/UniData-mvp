from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .models import Pessoa
from .forms import PessoaForm
import sys
import os

# Adiciona o diretório API ao path para importar o wallet_service
api_path = os.path.join(settings.BASE_DIR, 'API')
if api_path not in sys.path:
    sys.path.insert(0, api_path)
from services.wallet_service import criar_carteira


def cadastrar_pessoa(request):
    """View para cadastrar uma nova pessoa."""
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, f'Pessoa {pessoa.nome} cadastrada com sucesso!')
            return redirect('pessoas:listar_pessoas')
    else:
        form = PessoaForm()
    
    return render(request, 'pessoas/cadastrar_pessoa.html', {'form': form})


def listar_pessoas(request):
    """View para listar todas as pessoas cadastradas."""
    pessoas = Pessoa.objects.all()
    return render(request, 'pessoas/listar_pessoas.html', {'pessoas': pessoas})


def gerar_carteira(request, pessoa_id):
    """View para gerar uma carteira para uma pessoa."""
    pessoa = get_object_or_404(Pessoa, id=pessoa_id)
    
    # Verifica se a pessoa já tem uma carteira
    if pessoa.endereco_carteira:
        messages.warning(request, f'A pessoa {pessoa.nome} já possui uma carteira: {pessoa.endereco_carteira}')
        return redirect('pessoas:listar_pessoas')
    
    try:
        # Gera a carteira usando o wallet_service
        resultado = criar_carteira(pessoa.cpf)
        
        # Atualiza a pessoa com o endereço da carteira
        pessoa.endereco_carteira = resultado['endereco']
        pessoa.save()
        
        messages.success(request, f'Carteira gerada com sucesso para {pessoa.nome}!')
        messages.info(request, f'Endereço da carteira: {resultado["endereco"]}')
        
    except ValueError as e:
        messages.error(request, f'Erro ao gerar carteira: {str(e)}')
    except Exception as e:
        messages.error(request, f'Erro inesperado: {str(e)}')
    
    return redirect('pessoas:listar_pessoas')


def gerar_carteira_form(request):
    """View para exibir formulário de seleção de pessoa para gerar carteira."""
    pessoas = Pessoa.objects.filter(endereco_carteira__isnull=True)
    
    if request.method == 'POST':
        pessoa_id = request.POST.get('pessoa_id')
        if pessoa_id:
            return redirect('pessoas:gerar_carteira', pessoa_id=pessoa_id)
        else:
            messages.error(request, 'Por favor, selecione uma pessoa.')
    
    return render(request, 'pessoas/gerar_carteira.html', {'pessoas': pessoas})

