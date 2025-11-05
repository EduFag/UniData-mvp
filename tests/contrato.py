class ProntuarioContract:

    def __init__(self):
        self.registros = {}  # paciente -> lista de cids

    def criar_prontuario(self, paciente_id, cid):
        """Armazena um 'ponteiro' em memória, simulando o smart contract."""
        if paciente_id not in self.registros:
            self.registros[paciente_id] = []
        self.registros[paciente_id].append(cid)
        print(f"✅ Prontuário com CID {cid} criado para paciente {paciente_id}")

    def listar_cids(self, paciente_id):
        """Lista os CIDs armazenados para o paciente (sem o conteúdo)."""
        return self.registros.get(paciente_id, [])
