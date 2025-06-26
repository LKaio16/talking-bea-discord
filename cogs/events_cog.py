# cogs/events_cog.py

import discord
from discord.ext import commands
import random
import os
from config import FRASES_DA_BEA, IMAGENS_DE_PAO, JAILSON_VIDEOS # Importa as configurações

# Define o nome da pasta onde os áudios do chat estão
CHAT_AUDIO_FOLDER = 'audio-chat'

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



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
        # Corrigido: 'predeiro' para 'pedreiro'
        if 'pedreiro' in mensagem_lower:
            triggered_audio = 'pedreiro.mp3'
        elif 'preconceito' in mensagem_lower:
            triggered_audio = 'preconceito.mp3'

        if triggered_audio:
            if message.author.voice and message.author.voice.channel:
                voice_client = message.guild.voice_client
                if voice_client and voice_client.is_connected() and not voice_client.is_playing():
                    file_path = os.path.join(CHAT_AUDIO_FOLDER, triggered_audio)
                    if os.path.exists(file_path):
                        source = discord.FFmpegPCMAudio(file_path)
                        voice_client.play(source)
                    else:
                        print(f"AVISO: Arquivo de áudio não encontrado: {file_path}")
            return

        # --- LÓGICA DE RESPOSTAS DE TEXTO (PRIORIDADE MENOR) ---
        LUIZAO_ID = 397208306256576513
        # NOVO: ID do usuário a ser marcado no comando do Jailson
        JAILSON_TARGET_ID = 347431009895055360
        
        luizao_is_mentioned = any(mention.id == LUIZAO_ID for mention in message.mentions)

        if 'jailson' in mensagem_lower:
            # Sorteia um vídeo da lista
            video_url = random.choice(JAILSON_VIDEOS)
            # MUDANÇA: Agora a resposta marca o usuário e envia o vídeo
            mensagem_de_resposta = f"<@{JAILSON_TARGET_ID}> jailson\n{video_url}"
            await message.reply(mensagem_de_resposta)

        elif 'pão' in mensagem_lower:
            await message.channel.send(random.choice(IMAGENS_DE_PAO))
            
        elif 'luisao' in mensagem_lower or 'luizao' in mensagem_lower or luizao_is_mentioned:
            await message.reply(f"<@{LUIZAO_ID}> tu é mt foda")
            
        elif self.bot.user in message.mentions or 'bea' in mensagem_lower:
            await message.channel.send(random.choice(FRASES_DA_BEA))
            
        elif random.random() < 0.20:
            await message.channel.send(random.choice(FRASES_DA_BEA))

async def setup(bot):
    await bot.add_cog(EventsCog(bot))