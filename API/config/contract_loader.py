import json
from pathlib import Path
from .provider import get_provider

def load_contract(contract_name: str):
    web3 = get_provider()
    
    # Caminhos base
    base_path = Path(__file__).parent.parent / "contracts"
    abi_path = base_path / "abi" / f"{contract_name}.json"
    address_path = base_path / "addresses.json"
    
    # 1. Verificação de existência dos arquivos
    if not abi_path.exists():
        raise FileNotFoundError(f"Arquivo ABI não encontrado em: {abi_path}")
    
    if not address_path.exists():
        raise FileNotFoundError(f"Arquivo de endereços não encontrado em: {address_path}")

    # 2. Leitura segura do ABI
    try:
        abi_content = abi_path.read_text()
        if not abi_content.strip(): raise ValueError("Arquivo ABI vazio")
        abi_full = json.loads(abi_content)
        abi = abi_full["abi"]
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Erro ao ler JSON do ABI ({contract_name}): {str(e)}")

    # 3. Leitura segura do Endereço
    try:
        addr_content = address_path.read_text()
        addresses = json.loads(addr_content)
        contract_address = addresses.get(contract_name)
    except json.JSONDecodeError:
        raise ValueError(f"Arquivo addresses.json está corrompido.")

    if not contract_address:
        raise ValueError(f"Endereço do contrato '{contract_name}' não encontrado no arquivo addresses.json.")

    print("✅ Contrato instanciado")
    # Retorna o contrato instanciado
    contract = web3.eth.contract(address=contract_address, abi=abi)
    return contract