# cogs/admin_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import datetime
from collections import defaultdict

# Importa as configurações necessárias
from config import PATCH_NOTES_CHANNEL_ID

# ID do dono do bot
OWNER_ID = 404844681852223498

# --- MODAL PARA AS NOTAS DA ATUALIZAÇÃO ---
class PatchNotesModal(discord.ui.Modal, title="Criar Nota de Atualização"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

        self.version_input = discord.ui.TextInput(label="Versão (ex: v3.1.0)", style=discord.TextStyle.short, required=True)
        self.title_input = discord.ui.TextInput(label="Título da Atualização", style=discord.TextStyle.short, required=True)
        self.notes_input = discord.ui.TextInput(label="Notas da Atualização (use tags)", style=discord.TextStyle.paragraph, required=True)
        self.banner_input = discord.ui.TextInput(label="Link da Imagem do Banner (Opcional)", required=False)
        self.kaio_notes_input = discord.ui.TextInput(label="Suas Notas Pessoais (Opcional)", style=discord.TextStyle.paragraph, required=False)
        
        self.add_item(self.version_input)
        self.add_item(self.title_input)
        self.add_item(self.notes_input)
        self.add_item(self.banner_input)
        self.add_item(self.kaio_notes_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        versao = self.version_input.value
        titulo = self.title_input.value
        notas_raw = self.notes_input.value
        banner_url = self.banner_input.value
        kaio_notes = self.kaio_notes_input.value

        channel = self.bot.get_channel(PATCH_NOTES_CHANNEL_ID)
        if not channel:
            return await interaction.followup.send("Canal de atualizações não configurado!", ephemeral=True)

        embed = discord.Embed(
            title=f"📢 Atualização da Bea - {versao}",
            description=f"## {titulo}",
            color=discord.Color.random(),
            timestamp=datetime.datetime.now()
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        categorias = defaultdict(list)
        
        # CORREÇÃO: Removida a linha que trocava vírgulas por quebras de linha.
        # Agora o bot só separa os tópicos se você usar a tecla Enter.
        for linha in notas_raw.split('\n'):
            linha_strip = linha.strip()
            if not linha_strip: continue
            
            linha_lower = linha_strip.lower()

            if linha_lower.startswith("[novo]"):
                categorias["✨ Novidades"].append(linha_strip[len("[novo]"):].strip())
            elif linha_lower.startswith("[melhoria]"):
                categorias["🔧 Melhorias"].append(linha_strip[len("[melhoria]"):].strip())
            elif linha_lower.startswith("[correção]"):
                categorias["🐛 Correções"].append(linha_strip[len("[correção]"):].strip())
            else:
                categorias["📋 Outras Notas"].append(linha_strip)
        
        for nome_categoria, itens in categorias.items():
            if itens:
                notes_text = ""
                for item in itens:
                    notes_text += f"- {item}\n"
                embed.add_field(name=nome_categoria, value=notes_text, inline=False)
        
        if kaio_notes:
            embed.add_field(name="✍️ Uma Palavra do Desenvolvedor", value=f"*{kaio_notes}*", inline=False)

        if banner_url and banner_url.startswith("http"):
            embed.set_image(url=banner_url)
        
        embed.set_footer(text=f"Lançado por: {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

        try:
            await channel.send("@everyone", embed=embed)
            await interaction.followup.send("Nota de atualização enviada com sucesso!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Erro de permissão! Não consigo enviar mensagens no canal de atualizações.", ephemeral=True)


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="patchnotes", description="[DONO] Abre o formulário para criar uma nota de atualização.")
    async def patchnotes(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("Este é um comando restrito apenas para o meu criador!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PatchNotesModal(self.bot))


async def setup(bot):
    await bot.add_cog(AdminCog(bot))