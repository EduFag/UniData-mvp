from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Any
from API.schemas.schemas import *
from API.config import web3, api_signer, contrato
from API.services.transaction_service import enviar_transacao
from API.services.wallet_service import *
from datetime import datetime

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


@router.post("/set-consentimento", response_model=TxResponse)
def endpoint_set_consentimento(dados: ConsentimentoRequest):
    """
    Permite que um paciente dê ou revogue permissão de acesso a um médico.
    """
    try:
        # Monta a chamada para a função Solidity:
        # setConsentimento(address paciente, address profissional, bool permitido)
        func = contrato.functions.setConsentimento(
            dados.address_paciente,
            dados.address_profissional,
            dados.consentimento
        )

        # Assina e envia usando a função que já corrigimos
        resultado = enviar_transacao(func, api_signer, web3)
        
        # Verifica se houve erro na transação (ex: falta de gas, erro de lógica)
        if "erro" in resultado:
            raise HTTPException(status_code=500, detail=resultado["erro"])
            
        return resultado

    except Exception as e:
        # Captura erros gerais do Python/FastAPI
        print(f"Erro ao definir consentimento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    Lógica: Busca os IDs -> Itera sobre eles -> Busca os detalhes de cada um.
    """
    try:
        # 1. Busca apenas a lista de IDs (ex: [1, 5, 8])
        lista_ids = contrato.functions.listarProntuarios(address_paciente).call()
        
        prontuarios_formatados = []

        # 2. Para cada ID, buscamos os detalhes na blockchain
        for id_prontuario in lista_ids:
            # Retorno do contrato: (paciente, cid, updatedAt, ultimoAutor)
            dados = contrato.functions.getProntuario(id_prontuario).call()
            
            # Montamos o objeto JSON
            prontuarios_formatados.append({
                "id": id_prontuario,
                "paciente": dados[0],
                "cid": dados[1],
                "data_registro": datetime.fromtimestamp(dados[2]).strftime('%d/%m/%Y às %H:%M'),
                "profissional": dados[3]
            })
        
        # Inverte a lista para mostrar os mais recentes primeiro (opcional)
        prontuarios_formatados.reverse()
        
        return {"prontuarios": prontuarios_formatados}

    except Exception as e:
        import traceback
        traceback.print_exc() # Isso ajuda a ver o erro no terminal da API se acontecer de novo
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

