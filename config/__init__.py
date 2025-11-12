# config/__init__.py
from .provider import get_provider
from .signer import get_signer
from .contract_loader import load_contract

# Configurações globais
web3 = get_provider()
private_key = "CHAVE_PRIVADA_DO_ANVIL"
api_signer = get_signer(private_key)

# Contrato principal
contrato = load_contract("Prontuario")