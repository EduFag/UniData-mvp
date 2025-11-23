from pydantic import BaseModel

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
    endereco_paciente: str 
    cid: str
    endereco_profissional: str

class AtualizarProntuarioRequest(BaseModel):
    id: int
    cid: str
    address_profissional: str

# Modelo de Resposta para Transações
class TxResponse(BaseModel):
    tx_hash: str
    status: int
    gasUsed: int
    mensagem: str = "Transação efetuada com sucesso"