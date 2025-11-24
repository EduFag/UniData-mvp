from pydantic import BaseModel, model_validator
from typing import Optional

# --- MODELOS PYDANTIC (Data Transfer Objects) ---
# Isso garante que quem usa a API saiba exatamente o que enviar e receber

class CarteiraRequest(BaseModel):
    cpf: str

class PacienteRequest(BaseModel):
    cpf: str

class ProfissionalAuthRequest(BaseModel):
    address_profissional: str
    autorizado: bool

class ConsentimentoRequest(BaseModel):
    address_paciente: str
    address_profissional: str
    consentimento: bool

class ProntuarioRequest(BaseModel):
    id: Optional[int] = None        # Se vier ID, é Update. Se null, é Create.
    endereco_paciente: Optional[str] = None 
    cid: str
    endereco_profissional: str      # Quem está salvando (Endereço ETH do médico)

    @model_validator(mode='after')
    def verificar_dados_criacao(self):
        # Se NÃO tem ID (é criação), o endereco_paciente é OBRIGATÓRIO
        if not self.id and not self.endereco_paciente:
            raise ValueError('Para criar um novo prontuário, o endereço do paciente é obrigatório.')
        return self

# Modelo de Resposta para Transações
class TxResponse(BaseModel):
    tx_hash: str
    status: int
    gasUsed: int
    mensagem: str = "Transação efetuada com sucesso"