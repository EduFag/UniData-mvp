from fastapi import APIRouter
from API.config import web3, api_signer, contrato
from API.services.transaction_service import enviar_transacao
from API.services.wallet_service import *

router = APIRouter()

@router.get("/")
def root():
    return {"mensagem": "Bem vindo"}

router.post("/gerar-carteira")
def gerar_carteira(cpf):
    criar_carteira(cpf)

    carteira = obter_carteira(cpf)
    address = carteira["endereco"]

    return {"address": address}


@router.post("/cadastrar-paciente")
def cadastrar_paciente(cpf: str):
    carteira = obter_carteira(cpf)
    address = carteira["endereco"]

    func = contrato.functions.registrarPaciente(
        address
    )
    
    return enviar_transacao(func, api_signer, web3)

@router.post("/autorizar-profissional")
def autorizar_profissional(address_profissional: str, autorizado: bool):
    func = contrato.functions.setProfissionalAutorizado(
        address_profissional,
        autorizado
    )

    return enviar_transacao(func, api_signer, web3)

@router.post("/set-consentimento")
def set_consentimento(address_paciente: str, address_profissional: str, consentimento: bool):
    func = contrato.functions.setConsentimento(
        address_paciente,
        address_profissional,
        consentimento
    )

    return enviar_transacao(func, api_signer, web3)

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

@router.post("/atualizar-prontuario")
def atualizar_prontuario(id: int, cid: str, address_profissional: str):
    func = contrato.functions.atualizarProntuario(
        id,
        cid,
        address_profissional
    )

    return enviar_transacao(func, api_signer, web3)

@router.get("/listar-prontuarios")
def listar_prontuarios(address_paciente: str):
    try:
        prontuarios = contrato.functions.listarProntuarios(address_paciente).call()
        return {"prontuarios": prontuarios}
    except Exception as e:
        return {"erro": str(e)}
    
@router.get("/get-prontuario")
def get_prontuario(id: int):
    try:
        prontuario = contrato.functions.getProntuario(id).call()
        return {"prontuario": prontuario}
    except Exception as e:
        return {"erro": str(e)}



