from eth_account import Account
import json
import os

# Caminho para armazenar as carteiras localmente
CARTEIRAS_PATH = "API/data/carteiras.json"


def _carregar_arquivo():
    """Carrega o JSON de carteiras (ou cria um novo)."""
    if not os.path.exists(CARTEIRAS_PATH):
        os.makedirs(os.path.dirname(CARTEIRAS_PATH), exist_ok=True)
        with open(CARTEIRAS_PATH, "w") as f:
            json.dump({}, f)
    with open(CARTEIRAS_PATH, "r") as f:
        return json.load(f)


def _salvar_arquivo(data):
    """Salva o dicionário atualizado de carteiras."""
    with open(CARTEIRAS_PATH, "w") as f:
        json.dump(data, f, indent=4)


def criar_carteira(cpf: str):
    """
    Cria uma nova carteira Ethereum e salva no arquivo local.
    Retorna o endereço público e a chave privada.
    """
    data = _carregar_arquivo()

    if cpf in data:
        raise ValueError("Usuário já possui uma carteira registrada.")

    conta = Account.create()

    data[cpf] = {
        "endereco": conta.address,
        "chave_privada": conta.key.hex()
    }

    _salvar_arquivo(data)

    return {
        "mensagem": "Carteira criada com sucesso!",
        "usuario": cpf,
        "endereco": conta.address
    }


def listar_carteiras():
    """Retorna todas as carteiras armazenadas (sem exibir as chaves)."""
    data = _carregar_arquivo()
    return [{"usuario": u, "endereco": d["endereco"]} for u, d in data.items()]


def obter_carteira(nome_usuario: str):
    """Retorna a carteira completa (incluindo chave privada)."""
    data = _carregar_arquivo()

    if nome_usuario not in data:
        raise ValueError("Usuário não encontrado.")

    return data[nome_usuario]
