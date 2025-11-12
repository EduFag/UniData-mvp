# services/prontuario_service.py
from config import web3, signer, contrato_prontuario

def registrar_paciente(paciente_id: int, dados: str):
    """
    Cria um novo prontuário e envia para a blockchain.
    """
    tx = contrato_prontuario.functions.criarProntuario(paciente_id, dados).build_transaction({
        'from': signer.address,
        'nonce': web3.eth.get_transaction_count(signer.address),
        'gas': 2000000,
        'gasPrice': web3.to_wei('1', 'gwei')
    })

    assinado = signer.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(assinado.raw_transaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return {"transactionHash": receipt["transactionHash"].hex(), "status": receipt["status"]}


def ver_prontuario(paciente_id: int):
    """
    Faz uma leitura do prontuário (função call, sem custo).
    """
    return contrato_prontuario.functions.verProntuario(paciente_id).call()

