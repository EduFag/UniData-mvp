# config/provider.py
from web3 import Web3

def get_provider():
    provider_url = "http://localhost:8545"  # Anvil rodando localmente
    web3 = Web3(Web3.HTTPProvider(provider_url))
    
    return web3
