# cogs/events_cog.py

import discord
from discord.ext import commands
import random
import os
from config import FRASES_DA_BEA, IMAGENS_DE_PAO # Importa as configurações

# Define o nome da pasta onde os áudios do chat estão
CHAT_AUDIO_FOLDER = 'audio-chat'

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logado como {self.bot.user}! A Bea está online.')
        try:
            synced = await self.bot.tree.sync()
            print(f"Sincronizados {len(synced)} comandos.")
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignora as próprias mensagens e de outros bots
        if message.author.bot:
            return
        
        mensagem_lower = message.content.lower()
        
        # A reação de bolo pode acontecer independentemente de qualquer outra resposta
        if 'bolo' in mensagem_lower:
            await message.add_reaction('🎂')
        
        # --- LÓGICA DE ÁUDIO (PRIORIDADE MÁXIMA) ---
        triggered_audio = None
        if 'predeiro' in mensagem_lower:
            triggered_audio = 'predeiro.mp3'
        elif 'preconceito' in mensagem_lower:
            triggered_audio = 'preconceito.mp3'

        if triggered_audio:
            # Verifica se o autor da mensagem está em um canal de voz
            if message.author.voice and message.author.voice.channel:
                voice_client = message.guild.voice_client
                # Verifica se o bot está conectado e não está tocando nada
                if voice_client and voice_client.is_connected() and not voice_client.is_playing():
                    file_path = os.path.join(CHAT_AUDIO_FOLDER, triggered_audio)
                    if os.path.exists(file_path):
                        source = discord.FFmpegPCMAudio(file_path)
                        voice_client.play(source)
                    else:
                        print(f"AVISO: Arquivo de áudio não encontrado: {file_path}")
            # Após tentar tocar o áudio, paramos aqui para não enviar outras respostas de texto
            return

        # --- LÓGICA DE RESPOSTAS DE TEXTO (PRIORIDADE MENOR) ---
        LUIZAO_ID = 397208306256576513
        luizao_is_mentioned = any(mention.id == LUIZAO_ID for mention in message.mentions)

        if 'pão' in mensagem_lower:
            await message.channel.send(random.choice(IMAGENS_DE_PAO))
        elif 'luisao' in mensagem_lower or 'luizao' in mensagem_lower or luizao_is_mentioned:
            await message.reply(f"<@{LUIZAO_ID}> tu é mt foda")
        elif self.bot.user in message.mentions or 'bea' in mensagem_lower:
            await message.channel.send(random.choice(FRASES_DA_BEA))
        elif random.random() < 0.20:
            await message.channel.send(random.choice(FRASES_DA_BEA))

async def setup(bot):
    await bot.add_cog(EventsCog(bot))