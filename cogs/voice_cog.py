# cogs/voice_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os # Precisamos do 'os' para listar os arquivos da pasta

running_audio_tasks = {}

# MUDANÇA 1: Define o nome da pasta onde estão os áudios
AUDIO_FOLDER = 'audio'

async def background_player(voice_client, interaction):
    try:
        # Verifica se a pasta de áudio existe
        if not os.path.isdir(AUDIO_FOLDER):
            print(f"Erro: A pasta '{AUDIO_FOLDER}' não foi encontrada.")
            await interaction.followup.send(f"Atenção: A pasta de áudios '{AUDIO_FOLDER}' não existe!", ephemeral=True)
            return

        while True:
            intervalo = random.randint(2, 10)
            await asyncio.sleep(intervalo)

            # MUDANÇA 2: Procura por todos os arquivos .mp3 na pasta de áudio
            available_sounds = [f for f in os.listdir(AUDIO_FOLDER) if f.endswith('.mp3')]

            # Se não encontrar nenhum áudio, não faz nada e espera o próximo ciclo
            if not available_sounds:
                print("Nenhum arquivo .mp3 encontrado na pasta de áudio.")
                continue

            if voice_client.is_connected() and not voice_client.is_playing():
                # MUDANÇA 3: Escolhe um arquivo de áudio aleatório da lista
                random_sound_file = random.choice(available_sounds)
                file_path = os.path.join(AUDIO_FOLDER, random_sound_file)

                # MUDANÇA 4: Cria a fonte de áudio com o caminho completo do arquivo sorteado
                source = discord.FFmpegPCMAudio(file_path)
                voice_client.play(source)

    except asyncio.CancelledError:
        print(f"Tarefa de áudio para o servidor {interaction.guild.name} foi cancelada.")
    except Exception as e:
        print(f"Erro na tarefa de áudio: {e}")

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # (Os comandos /entrar, /sair, /fala_bea, /calaboca_bea continuam aqui, sem alterações)
    @app_commands.command(name="entrar", description="Faz a Bea entrar no seu canal de voz atual.")
    async def entrar(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(channel)
                await interaction.response.send_message(f"Movi para o canal '{channel.name}'!", ephemeral=True)
            else:
                await channel.connect()
                await interaction.response.send_message(f"To indo mah '{channel.name}'!")
        else:
            await interaction.response.send_message("tu nem ta num canal abestado", ephemeral=True)

    @app_commands.command(name="sair", description="Faz a Bea sair do canal de voz e para qualquer áudio.")
    async def sair(self, interaction: discord.Interaction):
        if interaction.guild.id in running_audio_tasks:
            running_audio_tasks[interaction.guild.id].cancel()
            del running_audio_tasks[interaction.guild.id]
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Tô saindo da call, flw!")
        else:
            await interaction.response.send_message("Eu não estou em nenhum canal de voz para poder sair.", ephemeral=True)

    @app_commands.command(name="fala_bea", description="Faz a Bea começar a falar aleatoriamente no canal de voz.")
    async def fala_bea(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Eu preciso estar em um canal de voz primeiro! Use `/entrar`.", ephemeral=True)
            return
        if interaction.guild.id in running_audio_tasks:
            await interaction.response.send_message("ja to falando mah", ephemeral=True)
            return
        task = self.bot.loop.create_task(background_player(interaction.guild.voice_client, interaction))
        running_audio_tasks[interaction.guild.id] = task
        await interaction.response.send_message("to falando mah.")

    @app_commands.command(name="calaboca_bea", description="Faz a Bea parar de falar.")
    async def calaboca_bea(self, interaction: discord.Interaction):
        if interaction.guild.id in running_audio_tasks:
            running_audio_tasks[interaction.guild.id].cancel()
            del running_audio_tasks[interaction.guild.id]
            await interaction.response.send_message("bl man")
        else:
            await interaction.response.send_message("Eu nem tava falando nada...", ephemeral=True)


async def setup(bot):
    await bot.add_cog(VoiceCog(bot))