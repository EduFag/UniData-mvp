from fastapi import FastAPI
from routes import prontuario_root  # importa o arquivo que tem as rotas

app = FastAPI()

# adiciona as rotas do arquivo base.py
app.include_router(prontuario_root.router)
