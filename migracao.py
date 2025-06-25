# migracao.py

import os
import json
import asyncio
from dotenv import load_dotenv
import motor.motor_asyncio

async def main():
    """
    Este script lê os dados do inventarios.json e os insere no MongoDB Atlas.
    """
    print("Iniciando script de migração...")

    # --- 1. Carregar configurações ---
    load_dotenv()
    MONGO_URI = os.getenv('MONGO_URI')

    if not MONGO_URI:
        print("ERRO: A variável MONGO_URI não foi encontrada no seu arquivo .env.")
        return

    # --- 2. Conectar ao MongoDB ---
    try:
        print("Conectando ao MongoDB Atlas...")
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client["BeaBotDB"]
        inventories_collection = db["inventories"]
        print("Conectado com sucesso!")
    except Exception as e:
        print(f"ERRO ao conectar ao MongoDB: {e}")
        return

    # --- 3. Carregar os dados do arquivo JSON ---
    json_file_path = 'inventarios.json'
    if not os.path.exists(json_file_path):
        print(f"ERRO: O arquivo '{json_file_path}' não foi encontrado.")
        return

    print(f"Lendo dados de '{json_file_path}'...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        dados_antigos = json.load(f)
    print(f"Encontrados dados de {len(dados_antigos)} usuários no arquivo JSON.")

    # --- 4. Migrar os dados para o MongoDB ---
    documentos_para_inserir = []
    for user_id, inventory_list in dados_antigos.items():
        # Transforma o formato antigo para o novo formato do MongoDB
        documento = {
            "user_id": user_id,
            "user_name": f"Usuário {user_id}", # Não temos o nome, então usamos um placeholder
            "inventory": inventory_list
        }
        documentos_para_inserir.append(documento)

    if not documentos_para_inserir:
        print("Nenhum dado para migrar. Encerrando.")
        return

    try:
        # Limpa a coleção antiga para evitar duplicatas, caso você rode o script mais de uma vez
        print("Limpando coleção antiga no MongoDB para garantir uma migração limpa...")
        await inventories_collection.delete_many({})
        
        # Insere todos os novos documentos de uma vez
        print(f"Inserindo {len(documentos_para_inserir)} documentos no MongoDB...")
        await inventories_collection.insert_many(documentos_para_inserir)
        
        print("\n-----------------------------------------")
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO! ✅")
        print("-----------------------------------------")
        print("Todos os dados do arquivo JSON foram importados para o MongoDB.")

    except Exception as e:
        print(f"ERRO durante a inserção no MongoDB: {e}")

if __name__ == '__main__':
    asyncio.run(main())