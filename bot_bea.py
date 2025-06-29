# bot_bea.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio
import logging
import traceback

# --- Carregar variáveis de ambiente ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

# --- NOVO: Configuração de Logging ---
# Cria um logger. O nome é opcional, mas útil para organização.
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR) # Vamos capturar apenas os erros para não poluir o arquivo.

# Cria um manipulador que escreve os logs em um arquivo chamado 'errors.log'.
# O modo 'a' (append) garante que novos erros sejam adicionados ao final do arquivo.
# O encoding 'utf-8' é importante para suportar caracteres especiais.
handler = logging.FileHandler(filename='errors.log', encoding='utf-8', mode='a')

# Define o formato da mensagem de log: tempo, nível de severidade, nome do logger e a mensagem.
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)

# Adiciona o manipulador ao logger.
logger.addHandler(handler)

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

# --- NOVO: Manipulador de Erros Global ---
# Este decorador especial captura erros que acontecem nos comandos de barra (app_commands)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # Prepara a mensagem de erro para o log
    error_message = f"Erro no comando '{interaction.data.get('name', 'desconhecido')}':"
    
    # Imprime o traceback completo no console para debug imediato
    print(error_message)
    traceback.print_exc()

    # Loga o traceback completo no arquivo 'errors.log'
    logger.error(f"{error_message}\n{traceback.format_exc()}")

    # Envia uma mensagem amigável para o usuário, se possível
    error_text = "Ocorreu um erro ao processar o comando. A equipe de desenvolvimento já foi notificada!"
    if interaction.response.is_done():
        await interaction.followup.send(error_text, ephemeral=True)
    else:
        await interaction.response.send_message(error_text, ephemeral=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado.")