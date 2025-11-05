import json

from contrato import ProntuarioContract

# Carrega o sistema de prontuários (externo ao contrato)
with open("dados/prontuarios.json") as f:
    banco_prontuarios = json.load(f)

# Instancia "smart contract"
contrato = ProntuarioContract()

# Simula registro
contrato.criar_prontuario("paciente_001", "CID123")

# Consulta os CIDs do contrato
cids = contrato.listar_cids("paciente_001")
print(f"🗂️ CIDs do paciente: {cids}")

# Agora vamos buscar o conteúdo do prontuário do JSON
for cid in cids:
    conteudo = banco_prontuarios.get(cid)
    print(f"\n📄 Conteúdo do prontuário {cid}:")
    print(json.dumps(conteudo, indent=2, ensure_ascii=False))
