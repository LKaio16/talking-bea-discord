# bot_bea.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio

# --- Carregar variáveis de ambiente ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

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
    bot.db = bot.mongo_client["BeaBotDB"]
    bot.inventories = bot.db["inventories"]
    print("Conectado ao MongoDB com sucesso!")

    # Carrega todos os cogs da pasta /cogs
    print("Carregando cogs...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog {filename} carregado.")
            except Exception as e:
                print(f"Falha ao carregar o cog {filename}: {e}")
    
    # Inicia o bot
    if TOKEN:
        await bot.start(TOKEN)
    else:
        print("Erro: O token do Discord não foi encontrado no arquivo .env")


@bot.event
async def on_ready():
    print(f'Logado como {bot.user}! Sincronizando comandos...')
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos. A Bea está online e pronta!")
    except Exception as e:
        print(f"Falha ao sincronizar comandos: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado.")