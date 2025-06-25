# bot_bea.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# --- Carregar variáveis de ambiente ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- Configuração Inicial do Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- Função Principal para Rodar o Bot ---
async def main():
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