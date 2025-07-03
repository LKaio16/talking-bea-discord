# bot_bea.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import motor.motor_asyncio
import logging
import traceback

# --- Imports das IAs ---
import google.generativeai as genai
from deepseek_ai import DeepSeekAI
from groq import Groq

# --- Importa as Configurações ---
from config import BEA_PERSONA, DEFAULT_AI_PROVIDER

# --- Carregar variáveis de ambiente ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# --- Configuração de Logging ---
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='errors.log', encoding='utf-8', mode='a')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# --- Configuração Inicial do Bot ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# --- Classe do Bot para Organização ---
class BeaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        # Trava para garantir que a configuração inicial rode apenas uma vez
        self.initial_setup_done = False
        
        # Atributos para as conexões
        self.mongo_client = None
        self.db = None
        self.inventories = None
        
        # Atributos para as IAs
        self.gemini_model = None
        self.deepseek_client = None
        self.current_ai = DEFAULT_AI_PROVIDER # Define a IA padrão na inicialização

    async def setup_hook(self):
        """Esta função é chamada uma vez quando o bot está se preparando para conectar."""
        if not self.initial_setup_done:
            print("Executando configuração inicial...")
            
            # 1. Conecta ao MongoDB
            print("Conectando ao MongoDB...")
            self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
            self.db = self.mongo_client["BeaBotDB"]
            self.inventories = self.db["inventories"]
            print("Conectado ao MongoDB com sucesso!")

            # 2. Configura a IA do Gemini
            print("Configurando a IA do Gemini...")
            if GEMINI_API_KEY:
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    self.gemini_model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=BEA_PERSONA
                    )
                    print("IA do Gemini configurada com sucesso!")
                except Exception as e:
                    print(f"ERRO ao configurar o Gemini: {e}")
                    self.gemini_model = None
            else:
                self.gemini_model = None
                print("AVISO: Chave da API do Gemini não encontrada.")

            # 3. Configura a IA do DeepSeek
            print("Configurando a IA do DeepSeek...")
            if DEEPSEEK_API_KEY:
                try:
                    self.deepseek_client = DeepSeekAI(api_key=DEEPSEEK_API_KEY, timeout=300.0)
                    print("Cliente do DeepSeek configurado com sucesso!")
                except Exception as e:
                    print(f"ERRO ao configurar o DeepSeek: {e}")
                    self.deepseek_client = None
            else:
                self.deepseek_client = None
                print("AVISO: Chave da API do DeepSeek não encontrada.")
                
            # 4. Configura a IA do Groq
            print("Configurando a IA do Groq...")
            if GROQ_API_KEY:
                try:
                    self.groq_client = Groq(api_key=GROQ_API_KEY)
                    print("Cliente do Groq configurado com sucesso!")
                except Exception as e:
                    print(f"ERRO ao configurar o Groq: {e}")
                    self.groq_client = None
            else:
                self.groq_client = None
                print("AVISO: Chave da API do Groq não encontrada.")

            # 5. Carrega todos os cogs
            print("Carregando cogs...")
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"Cog {filename} carregado.")
                    except Exception as e:
                        print(f"Falha ao carregar o cog {filename}: {e}")
            
            self.initial_setup_done = True

    async def on_ready(self):
        print("-" * 20)
        print(f'Logado como {self.user}!')
        print(f'IA Ativa no momento: {self.current_ai.upper()}')
        print("-" * 20)
        
        # Sincroniza os comandos de barra com o Discord
        try:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos. A Bea está online e pronta!")
        except Exception as e:
            print(f"Falha ao sincronizar comandos: {e}")

# --- Instancia o bot ---
bot = BeaBot()

# --- Manipulador de Erros Global ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    error_message = f"Erro no comando '{interaction.data.get('name', 'desconhecido')}':"
    print(error_message)
    traceback.print_exc()
    logger.error(f"{error_message}\n{traceback.format_exc()}")
    error_text = "Ocorreu um erro ao processar o comando. A equipe de desenvolvimento já foi notificada!"
    if interaction.response.is_done():
        await interaction.followup.send(error_text, ephemeral=True)
    else:
        await interaction.response.send_message(error_text, ephemeral=True)

# --- Função Principal para Rodar o Bot ---
async def main():
    if TOKEN:
        await bot.start(TOKEN)
    else:
        print("Erro: O token do Discord não foi encontrado no arquivo .env")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot desligado.")