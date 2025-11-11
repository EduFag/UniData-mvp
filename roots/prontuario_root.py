from fastapi import APIRouter, Body

router = APIRouter()

@router.get("/{paciente_id}")
def get_prontuario(paciente_id: int):
    """Retorna os dados de um prontuário pelo ID do paciente."""
    return {"Dados do prontuário pelo ID do paciente"}

@router.post("/")
def post_prontuario(
    private_key: str = Body(...),
    paciente_id: int = Body(...),
    dados: str = Body(...)
):
    """Cria um novo prontuário e grava na blockchain."""

    return {"Sucesso"}