# config/signer.py
from web3 import Account

def get_signer(private_key: str):
    """
    Retorna a conta configurada a partir da chave privada.
    """
    account = Account.from_key(private_key)
    return account