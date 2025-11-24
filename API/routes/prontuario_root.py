from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Any
from API.schemas.schemas import *
from API.config import web3, api_signer, contrato
from API.services.transaction_service import enviar_transacao
from API.services.wallet_service import *

def formatar_prontuario(dados_contrato: Any) -> dict:
    # Supondo que o contrato retorne algo como: (id, cid, paciente, medico, timestamp)
    # Adapte os índices conforme sua Struct no Solidity
    return {
        "id": dados_contrato[0],
        "cid": dados_contrato[1],
        "paciente": dados_contrato[2],
        "profissional": dados_contrato[3],
        "data_registro": dados_contrato[4] # Se for timestamp unix
    }

router = APIRouter()

@router.get("/", summary="Health Check")
def root():
    return {"status": "API Online", "servico": "Unidata"}


@router.post("/gerar-carteira")
def endpoint_gerar_carteira(dados: CarteiraRequest):
    try:
        criar_carteira(dados.cpf)
        carteira = obter_carteira(dados.cpf)
        
        if not carteira:
             raise HTTPException(status_code=500, detail="Falha ao recuperar carteira criada.")

        return {"address": carteira["endereco"], "mensagem": "Carteira criada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/cadastrar-paciente", response_model=TxResponse)
def endpoint_cadastrar_paciente(dados: PacienteRequest):
    # Recupera carteira pelo CPF
    carteira = obter_carteira(dados.cpf)
    if not carteira:
        raise HTTPException(status_code=404, detail="Carteira não encontrada para este CPF")
    
    address = carteira["endereco"]

    # Prepara transação
    func = contrato.functions.registrarPaciente(
        address
    )

    # Executa
    resultado = enviar_transacao(func, api_signer, web3)
    
    # Verifica erro no helper de transação
    if "erro" in resultado:
        raise HTTPException(status_code=500, detail=resultado["erro"])
        
    return resultado


@router.post("/autorizar-profissional", response_model=TxResponse)
def endpoint_autorizar_profissional(dados: ProfissionalAuthRequest):
    func = contrato.functions.setProfissionalAutorizado(
        dados.address_profissional,
        dados.autorizado
    )
    resultado = enviar_transacao(func, api_signer, web3)
    
    if "erro" in resultado:
        raise HTTPException(status_code=500, detail=resultado["erro"])
    
    return resultado


@router.get("/checar-consentimento")
def endpoint_checar_consentimento(address_paciente: str, address_profissional: str):
    """ Verifica na blockchain se o médico tem permissão """
    try:
        # Mapeamento: consentimento[paciente][profissional]
        permitido = contrato.functions.consentimento(address_paciente, address_profissional).call()
        return {"autorizado": permitido}
    except Exception as e:
        return {"autorizado": False, "erro": str(e)}
    

@router.post("/registrar-prontuario", response_model=TxResponse)
def endpoint_registrar_prontuario(dados: ProntuarioRequest):
    try:
        # Lógica de decisão
        if dados.id and dados.id > 0:
            # É ATUALIZAÇÃO
            func = contrato.functions.atualizarProntuario(
                dados.id, 
                dados.cid, 
                dados.endereco_profissional
            )
        else:
            # É CRIAÇÃO
            func = contrato.functions.criarProntuario(
                dados.endereco_paciente, 
                dados.cid, 
                dados.endereco_profissional
            )

        resultado = enviar_transacao(func, api_signer, web3)
        
        if "erro" in resultado:
            raise HTTPException(status_code=500, detail=resultado["erro"])
            
        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/listar-prontuarios")
def listar_prontuarios(address_paciente: str):
    """
    Retorna a lista formatada de prontuários.
    """
    try:
        # O contrato deve retornar uma lista de Structs ou Tuplas
        raw_data = contrato.functions.listarProntuarios(address_paciente).call()
        
        # O Web3 retorna structs como tuplas. Precisamos converter para JSON.
        prontuarios_formatados = [formatar_prontuario(p) for p in raw_data]
        
        return {"prontuarios": prontuarios_formatados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler blockchain: {str(e)}")
    

@router.get("/get-prontuario/{id_prontuario}")
def get_prontuario(id_prontuario: int):
    try:
        raw_data = contrato.functions.getProntuario(id_prontuario).call()
        
        # Verifica se retornou vazio
        if not raw_data or raw_data[0] == 0: 
             raise HTTPException(status_code=404, detail="Prontuário não encontrado")

        return {"prontuario": formatar_prontuario(raw_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

