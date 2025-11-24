# config/__init__.py
from .provider import get_provider
from .signer import get_signer
from .contract_loader import load_contract
import os
from dotenv import load_dotenv

load_dotenv()  # carrega as variáveis do .env

# Configurações globais
web3 = get_provider()
if not web3.is_connected():
    raise ConnectionError("❌ Não foi possível conectar ao Anvil.")
else:
    print("✅ Conectado à blockchain:", os.getenv("PROVIDER_URL"))
private_key = os.getenv("ANVIL_PRIVATE_KEY")
api_signer = get_signer(private_key)

# Contrato principal
contrato = load_contract("Unidata")