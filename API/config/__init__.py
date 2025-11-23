# config/__init__.py
from .provider import get_provider
from .signer import get_signer
from .contract_loader import load_contract
import os
from dotenv import load_dotenv

load_dotenv()  # carrega as variáveis do .env

# Configurações globais
web3 = get_provider()
private_key = os.getenv("ANVIL_PRIVATE_KEY")
api_signer = get_signer(private_key)

# Contrato principal
contrato = load_contract("Unidata")