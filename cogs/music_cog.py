# cogs/music_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# --- Configurações do Player ---
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0' # Força o uso de IPv4, evitando problemas em alguns hosts
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn' # -vn = Sem Vídeo
}

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dicionário para guardar a fila de cada servidor. {guild_id: [lista_de_musicas]}
        self.song_queue = {}
        # Atividade padrão do bot quando não está tocando nada
        self.default_activity = discord.Game(name="ei mah")

    @commands.Cog.listener()
    async def on_ready(self):
        """Define uma atividade inicial quando o bot liga."""
        await self.bot.change_presence(activity=self.default_activity)

    def play_next(self, interaction: discord.Interaction):
        """Função para tocar a próxima música da fila e atualizar a atividade do bot."""
        guild_id = interaction.guild.id
        if not self.song_queue.get(guild_id):
            print(f"[LOG] Fila de '{interaction.guild.name}' vazia. Limpando atividade.")
            # Garante que a corrotina para mudar a presença rode no loop de eventos principal do bot
            asyncio.run_coroutine_threadsafe(self.bot.change_presence(activity=self.default_activity), self.bot.loop)
            return

        # Pega a próxima música da fila
        song = self.song_queue[guild_id].pop(0)
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_connected():
            try:
                source = discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS)
                # Toca a música e define o 'after' para chamar esta mesma função quando a música acabar
                voice_client.play(source, after=lambda e: self.play_next(interaction))
                
                # Cria a atividade de Streaming para um Rich Presence bonito
                now_playing_activity = discord.Streaming(
                    name=song['title'], 
                    url=song['webpage_url'] # URL do vídeo no YouTube
                )
                asyncio.run_coroutine_threadsafe(self.bot.change_presence(activity=now_playing_activity), self.bot.loop)
                
                print(f"[LOG] Tocando: {song['title']}")
            except Exception as e:
                print(f"[ERRO] Falha ao tocar a música {song['title']}: {e}")
                self.play_next(interaction) # Tenta pular para a próxima em caso de erro na reprodução

    @app_commands.command(name="play", description="Toca uma música ou playlist do YouTube.")
    @app_commands.describe(busca="O nome da música, link do vídeo ou link da playlist.")
    async def play(self, interaction: discord.Interaction, busca: str):
        await interaction.response.defer()

        if not interaction.user.voice:
            await interaction.followup.send("Você precisa estar em um canal de voz para usar este comando!", ephemeral=True)
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice_client:
            voice_client = await interaction.user.voice.channel.connect()
        
        ydl_opts_to_use = YDL_OPTIONS.copy()
        # Verifica se o link é de uma playlist para ajustar as opções
        if 'list=' in busca:
            ydl_opts_to_use['noplaylist'] = False
            ydl_opts_to_use['extract_flat'] = 'in_playlist' # Pega a lista de forma rápida

        with yt_dlp.YoutubeDL(ydl_opts_to_use) as ydl:
            try:
                info = ydl.extract_info(busca, download=False)
            except Exception as e:
                await interaction.followup.send(f"Não consegui obter informações para '{busca}'. Erro: {e}")
                return

        if interaction.guild.id not in self.song_queue:
            self.song_queue[interaction.guild.id] = []
        
        # Se for uma playlist, 'entries' existirá no dicionário de info
        if 'entries' in info:
            songs_added = 0
            songs_skipped = 0
            playlist_title = info.get('title', 'Playlist sem nome')

            for entry in info.get('entries', []):
                if entry:
                    song_info = {
                        'source': entry['url'], 
                        'title': entry.get('title', 'Título indisponível'),
                        'webpage_url': f"https://www.youtube.com/watch?v=OU97Fql2J8o7{entry.get('id', '')}"
                    }
                    self.song_queue[interaction.guild.id].append(song_info)
                    songs_added += 1
                else:
                    songs_skipped += 1
            
            embed = discord.Embed(title=f"✅ Playlist '{playlist_title}' Adicionada!", color=discord.Color.purple())
            embed.description = f"Adicionei **{songs_added}** músicas à fila."
            if songs_skipped > 0:
                embed.add_field(name="Aviso", value=f"**{songs_skipped}** músicas foram puladas (privadas/indisponíveis).")
            await interaction.followup.send(embed=embed)
        else: # Se for uma música única
            song = {
                'source': info['url'], 
                'title': info.get('title', 'Título desconhecido'),
                'webpage_url': info.get('webpage_url', busca)
            }
            self.song_queue[interaction.guild.id].append(song)
            
            # Mensagem de feedback diferente se já estiver tocando ou não
            if not voice_client.is_playing():
                embed = discord.Embed(title="🎵 Tocando Agora", description=f"**{song['title']}**", color=discord.Color.green())
            else:
                embed = discord.Embed(title="✅ Adicionado à Fila", description=f"**{song['title']}**", color=discord.Color.blue())
            await interaction.followup.send(embed=embed)

        # Inicia a reprodução se o bot não estiver tocando nada
        if not voice_client.is_playing():
            self.play_next(interaction)

    @app_commands.command(name="pause", description="Pausa a música atual.")
    async def pause(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("Música pausada. ⏸️")
        else:
            await interaction.response.send_message("Não há nenhuma música tocando para pausar.", ephemeral=True)

    @app_commands.command(name="resume", description="Continua a música pausada.")
    async def resume(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.response.send_message("Continuando a música! ▶️")
        else:
            await interaction.response.send_message("Não há nenhuma música pausada para continuar.", ephemeral=True)

    @app_commands.command(name="skip", description="Pula para a próxima música da fila.")
    async def skip(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop() # O 'after' do play vai chamar o play_next automaticamente
            await interaction.response.send_message("Música pulada! ⏭️")
        else:
            await interaction.response.send_message("Não há nenhuma música tocando para pular.", ephemeral=True)

    @app_commands.command(name="queue", description="Mostra a fila de músicas atual.")
    async def queue(self, interaction: discord.Interaction):
        queue = self.song_queue.get(interaction.guild.id, [])
        if not queue:
            await interaction.response.send_message("A fila de músicas está vazia!", ephemeral=True)
            return

        embed = discord.Embed(title="Fila de Músicas 🎵", color=discord.Color.purple())
        description = ""
        for i, song in enumerate(queue[:10]):
            description += f"**{i+1}.** {song['title']}\n"
        embed.description = description
        
        if len(queue) > 10:
            embed.set_footer(text=f"... e mais {len(queue) - 10} músicas.")
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop", description="Para a música, limpa a fila e desconecta.")
    async def stop(self, interaction: discord.Interaction):
        if interaction.guild.id in self.song_queue:
            self.song_queue[interaction.guild.id].clear()

        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice_client and voice_client.is_connected():
            voice_client.stop()
            await voice_client.disconnect()
            await self.bot.change_presence(activity=self.default_activity) # Limpa a atividade
            await interaction.response.send_message("Tudo parado! Fila limpa e bot desconectado.")
        else:
            await interaction.response.send_message("Eu não estou em um canal de voz.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicCog(bot))