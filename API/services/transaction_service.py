def enviar_transacao(funcao_contrato, signer, web3):
    """
    Monta, assina e envia uma transação EIP-1559 para a blockchain.

    Parâmetros:
        funcao_contrato:  Exemplo -> contrato.functions.criarProntuario(addr, cid)
        signer:           Conta que assina a transação
        web3:             Instância Web3 conectada ao provider

    Retorno:
        dict contendo hash, status e gas usado.
    """

    try:
        # 1. NONCE — cada transação precisa ter um índice único
        nonce = web3.eth.get_transaction_count(signer.address)

        # 2. Estimar o GAS automaticamente
        gas_estimate = funcao_contrato.estimate_gas({"from": signer.address})

        # 3. Buscar o baseFee atual da rede (EIP-1559)
        latest_block = web3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas")

        # 4. Definir priority fee (gorjeta) — 2 gwei é comum
        priority_fee = web3.to_wei(2, "gwei")

        # 5. maxFeePerGas = baseFee + priorityFee
        max_fee = base_fee + priority_fee

        # 6. Montar a transação EIP-1559
        tx = funcao_contrato.build_transaction({
            "from": signer.address,
            "nonce": nonce,
            "gas": gas_estimate,
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
            "type": 2  # ← obrigatório para EIP-1559
        })

        # 7. Assinar a transação
        signed_tx = signer.sign_transaction(tx)

        # 8. Enviar
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # 9. Esperar confirmação
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "tx_hash": tx_hash.hex(),
            "status": receipt.status,
            "gasUsed": receipt.gasUsed, # <--- CORRIGIDO AQUI (mantido CamelCase conforme o erro pediu)
        }

    except Exception as e:
        import traceback
        print("="*30)
        print("ERRO NA TRANSAÇÃO WEB3:")
        print(f"Tipo: {type(e)}")
        print(f"Erro: {e}")
        traceback.print_exc() # Imprime a linha exata onde quebrou
        print("="*30)
        return {"erro": str(e)}