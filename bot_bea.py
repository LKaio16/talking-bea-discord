# bot_bea.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio # Importa o motor

# --- Carregar variáveis de ambiente ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI') # Pega a string de conexão do .env

# --- Configuração Inicial do Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- Função Principal para Rodar o Bot ---
async def main():
    # Conecta ao MongoDB Atlas
    print("Conectando ao MongoDB...")
    bot.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    bot.db = bot.mongo_client["BeaBotDB"] # Nome do seu banco de dados
    bot.inventories = bot.db["inventories"] # Nome da sua "tabela" (coleção) de inventários
    print("Conectado ao MongoDB com sucesso!")

    # Carrega todos os cogs da pasta /cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Cog {filename} carregado.')

    # Inicia o bot com o token
    if TOKEN:
        await bot.start(TOKEN)
    else:
        print("Erro: O token do Discord não foi encontrado no arquivo .env")

if __name__ == '__main__':
    asyncio.run(main())