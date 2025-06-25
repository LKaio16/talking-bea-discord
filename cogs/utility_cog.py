# cogs/utility_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz # Importa a biblioteca de fuso horário

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDO DE AJUDA ---
    @app_commands.command(name="ajuda", description="Mostra tudo que a Bea sabe fazer!")
    async def ajuda(self, interaction: discord.Interaction):
        # Cria a base da mensagem embed
        embed = discord.Embed(
            title="Ajuda da Bea | Meus Comandos",
            description="Olá! Eu sou a Bea. Aqui está uma lista de tudo que eu posso fazer no servidor:",
            color=discord.Color.from_rgb(255, 105, 180)  # Um rosa bonitinho
        )

        # Adiciona o avatar do bot como uma miniatura
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Categoria de Jogo
        embed.add_field(
            name="🎮 Comandos de Jogo",
            value=(
                "`/cozinhar`: Prepara uma receita aleatória para sua coleção.\n"
                "`/inventario`: Mostra todas as receitas que você já coletou e seu progresso."
            ),
            inline=False
        )

        # Categoria de Voz e Áudio
        embed.add_field(
            name="🎙️ Comandos de Voz e Áudio",
            value=(
                "`/entrar`: Eu entro no seu canal de voz.\n"
                "`/sair`: Eu saio do canal de voz.\n"
                "`/fala_bea`: Começo a tocar áudios aleatórios na call.\n"
                "`/calaboca_bea`: Paro de tocar os áudios aleatórios."
            ),
            inline=False
        )
        
        # Categoria de Utilidade
        embed.add_field(
            name="🔧 Comandos de Utilidade",
            value=(
                "`/dvinalle`: Mostra as informações da D'vinalle Pizzaria.\n"
                "`/bea`: Muda seu apelido para 'bea'.\n"
                "`/paz`: Aplica um momento de paz em um usuário."
            ),
            inline=False
        )

        # Seção para as interações automáticas
        embed.add_field(
            name="💬 Interações Automáticas",
            value=(
                "Além dos comandos, eu também reajo a palavras no chat! Fique de olho quando alguém falar sobre `bolo`, `pão`, `Luizão` ou me mencionar. Também posso tocar sons para `pedreiro` e `preconceito` se eu estiver na call!"
            ),
            inline=False
        )

        embed.set_footer(text="Bot da Bea - Criado com muito carinho!")

        # Envia a mensagem de ajuda de forma que só quem pediu veja
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="bea", description="bea.")
    async def bea(self, interaction: discord.Interaction):
        try:
            # Tenta editar o apelido do usuário que executou o comando
            await interaction.user.edit(nick="bea")
            await interaction.response.send_message("bea", ephemeral=True)
        except discord.Forbidden:
            # Avisa se o bot não tiver permissão para isso
            await interaction.response.send_message(
                "me da permisao ai",
                ephemeral=True
            )

    @app_commands.command(name="paz", description="Acala boca alison")
    async def paz(self, interaction: discord.Interaction):
        # ID do usuário que será "pacificado"
        TARGET_USER_ID = 537471265284423680

        # Duração do "momento de paz" (5 minutos)
        timeout_duration = datetime.timedelta(minutes=5)

        # Medida de segurança: Verifica se o autor do comando tem permissão para moderar membros
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("tu nem pode", ephemeral=True)
            return

        # Busca o membro no servidor pelo ID
        target_member = interaction.guild.get_member(TARGET_USER_ID)

        if not target_member:
            await interaction.response.send_message("ele nao ta aqui graças a deus", ephemeral=True)
            return
            
        try:
            # Aplica o "castigo" (timeout) no membro
            await target_member.timeout(timeout_duration, reason=f"cala boca ai gay")
            await interaction.response.send_message(
                f"{target_member.mention} cala boca viadin"
            )
        except discord.Forbidden:
            # Avisa se o bot não tiver a permissão necessária
            await interaction.response.send_message(
                "me da permisao",
                ephemeral=True
            )

    @app_commands.command(name="dvinalle", description="Mostra as informações da D'vinalle Pizzaria!")
    async def dvinalle(self, interaction: discord.Interaction):
        # --- Lógica do Status (Aberto/Fechado) ---
        timezone_fortaleza = pytz.timezone('America/Fortaleza')
        horario_atual = datetime.datetime.now(timezone_fortaleza)
        hora = horario_atual.hour

        # Horário de funcionamento: 18:00 (incluso) até 23:00 (excluso)
        if 18 <= hora < 23:
            status_texto = "🟢 **Aberta agora!** Pode pedir!"
            cor_embed = discord.Color.green()
        else:
            status_texto = "🔴 **Fechada no momento.** Abrimos às 18h!"
            cor_embed = discord.Color.red()

        # --- Montagem da Mensagem (Embed) ---
        embed = discord.Embed(
            title="🍕 D'vinalle Pizzaria 🍕",
            description="As melhores pizzas da Messejana estão aqui!",
            color=cor_embed
        )
        
        embed.set_image(url="https://i.imgur.com/OFJc9ov.jpeg")

        # Adiciona os campos de informação
        embed.add_field(name="Status", value=status_texto, inline=False)
        embed.add_field(name="⏰ Horário", value="Segunda a Domingo\n18:00 - 23:00", inline=True)
        embed.add_field(name="📍 Endereço", value="Rua Angelica Gurgel, 629b\nMessejana, Fortaleza - CE", inline=True)
        
        links = (
            "[Instagram](https://www.instagram.com/dvinallepizzaria/) | "
            "[WhatsApp](https://wa.me/558598712151)"
        )
        embed.add_field(name="🔗 Peça agora!", value=links, inline=False)
        
        embed.set_footer(text="Qualidade e sabor que você merece!")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(UtilityCog(bot))