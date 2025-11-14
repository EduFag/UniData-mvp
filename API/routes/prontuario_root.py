from fastapi import APIRouter
from config import web3, api_signer, contrato
from services.transaction_service import enviar_transacao

router = APIRouter()

@router.get("/")
def root():
    return {"mensagem": "Bem vindo"}

@router.post("/registrar-prontuario")
def registrar_prontuario(endereco_paciente: str, cid: str):
    """
    Chama a função registrarProntuario do contrato.
    A API assina a transação.
    """
    func = contrato.functions.criarProntuario(
        endereco_paciente,  # parâmetro 1 (address)
        cid                 # parâmetro 2 (string)
    )

    return enviar_transacao(func, api_signer, web3)




