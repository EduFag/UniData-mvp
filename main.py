from fastapi import FastAPI
from roots.prontuario_root import router as prontuario_router

app = FastAPI(title="Prontuário Blockchain API")

app.include_router(prontuario_router, prefix="/prontuarios", tags=["Prontuários"])