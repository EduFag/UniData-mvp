from services.wallet_service import *

print(listar_carteiras())

carteira = obter_carteira("03937512012")
print(carteira["endereco"])
