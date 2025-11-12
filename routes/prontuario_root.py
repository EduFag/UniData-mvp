from fastapi import APIRouter
from config import web3, api_signer, contrato

router = APIRouter()

@router.get("/")
def root():
    return {"mensagem": "Bem vindo"}

@router.post("/registrar")
def registrar_paciente(endereco_paciente):
    tx = contrato.functions.registrarPaciente(endereco_paciente).build_transaction({
        "from": api_signer.address,
        "nonce": web3.eth.get_transaction_count(api_signer.address),
        "gas": 300000,
        "gasPrice": web3.to_wei("5", "gwei"),
    })

    signed_tx = api_signer.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return {"tx_hash": tx_hash.hex()}

