import json
from pathlib import Path
from .provider import get_provider

def load_contract(contract_name: str):
    web3 = get_provider()
    
    abi_path = Path(__file__).parent.parent / "contracts" / "abi" / f"{contract_name}.json"
    address_path = Path(__file__).parent.parent / "contracts" / "addresses.json"
    
    abi = json.loads(abi_path.read_text())
    addresses = json.loads(address_path.read_text())
    contract_address = addresses.get(contract_name)

    if not contract_address:
        raise ValueError(f"Endereço do contrato {contract_name} não encontrado.")

    contract = web3.eth.contract(address=contract_address, abi=abi)
    return contract
