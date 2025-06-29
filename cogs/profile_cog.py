# cogs/profile_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import io
from PIL import Image, ImageDraw, ImageFont
from config import CATALOGO_LOJA

# --- FUNÇÃO CENTRAL PARA GERAR A IMAGEM DO PERFIL ---
async def generate_profile_image(user: discord.Member, profile_data: dict) -> io.BytesIO:
    # CORREÇÃO: Usando nomes no singular para buscar os dados
    bg_filename = profile_data.get("background")
    bea_filename = profile_data.get("bea_skin")
    
    # Lógica do "Modo Blueprint" se nada estiver equipado
    if not bg_filename and not bea_filename:
        background = Image.new("RGB", (800, 400), color=(230, 230, 230))
        draw = ImageDraw.Draw(background)
        # (código do blueprint aqui) ...
    else:
        # Lógica Normal de Geração de Imagem
        if bg_filename:
            bg_path = os.path.join("profile_assets", "backgrounds", bg_filename)
            try: background = Image.open(bg_path).convert("RGBA").resize((800, 400))
            except FileNotFoundError: background = Image.new("RGB", (800, 400), color="#2c2f33")
        else:
            background = Image.new("RGB", (800, 400), color="#2c2f33")
        if bea_filename:
            bea_path = os.path.join("profile_assets", "beas", bea_filename)
            try:
                bea_img = Image.open(bea_path).convert("RGBA")
                bea_img.thumbnail((300, 300))
                background.paste(bea_img, (400 - bea_img.width // 2, 120), bea_img)
            except FileNotFoundError: pass

    # Desenho do Card de Info
    overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    card_coords = [20, 20, 420, 100]
    draw.rounded_rectangle(card_coords, radius=20, fill=(0, 0, 0, 180))
    background = Image.alpha_composite(background, overlay)
    
    try:
        user_avatar_asset = user.display_avatar.with_size(64)
        avatar_bytes = await user_avatar_asset.read()
        user_avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    except Exception: user_avatar = Image.new("RGBA", (64, 64), color="grey")

    mask = Image.new("L", user_avatar.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, user_avatar.size[0], user_avatar.size[1]), fill=255)
    background.paste(user_avatar, (35, 28), mask)
    draw = ImageDraw.Draw(background)
    try:
        main_font = ImageFont.truetype("arialbd.ttf", size=28)
        title_font = ImageFont.truetype("arial.ttf", size=19)
    except IOError:
        main_font, title_font = ImageFont.load_default(), ImageFont.load_default()
    
    draw.text((115, 40), user.name, font=main_font, fill=(255, 255, 255), anchor="lt")
    # CORREÇÃO: Usando nome no singular para buscar o título
    profile_title = profile_data.get("title", "Cozinheiro(a) Novato(a)")
    draw.text((115, 72), profile_title, font=title_font, fill=(220, 220, 220), anchor="lt")
    
    final_buffer = io.BytesIO()
    background.save(final_buffer, format='PNG')
    final_buffer.seek(0)
    return final_buffer


# --- CLASSES DE VIEW PARA O MENU DE EDIÇÃO ---
class ProfileEditView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    async def send_profile_or_error(self, interaction: discord.Interaction, is_edit: bool = False, is_public: bool = False):
        user_id = str(interaction.user.id)
        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        profile_data = user_data.get("profile", {})
        
        missing_items = []
        if not profile_data.get("background"): missing_items.append("Fundo")
        if not profile_data.get("bea_skin"): missing_items.append("Skin da Bea")
        if not profile_data.get("title"): missing_items.append("Título")
            
        if missing_items:
            error_message = f"Seu perfil está incompleto! Equipe: **{', '.join(missing_items)}**."
            # A mensagem de erro é sempre privada
            await interaction.followup.send(content=error_message, ephemeral=True, view=self)
            return

        image_buffer = await generate_profile_image(interaction.user, profile_data)
        file = discord.File(fp=image_buffer, filename="perfil.png")

        # --- MUDANÇA NO TEXTO DA MENSAGEM ---
        if is_public:
            # Mensagem bonita para o comando /perfil público
            content = f"✨ Cartão de perfil de {interaction.user.mention}!"
        elif is_edit:
            # Mensagem para quando o perfil é atualizado (privada)
            content = "Seu perfil foi atualizado!"
        else:
            # Mensagem para o comando /editar_perfil (privada)
            content = "Use os botões abaixo para editar seu perfil:"

        # Envia a mensagem com ephemeral=False se for pública
        await interaction.followup.send(content=content, file=file, view=self, ephemeral=not is_public)

    async def get_owned_items(self, user_id: str, item_type: str):
        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        owned = user_data.get("purchased_items", {}).get(item_type + 's', [])
        if item_type == "title" and "Cozinheiro(a) Novato(a)" not in owned:
            owned.insert(0, "Cozinheiro(a) Novato(a)")
        return owned

    @discord.ui.button(label="Mudar Fundo", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def change_background(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        owned_backgrounds = await self.get_owned_items(str(interaction.user.id), "background")
        if not owned_backgrounds: await interaction.followup.send("Você não possui nenhum fundo! Visite a `/loja` para comprar.", ephemeral=True); return
        view = SelectionView(self.bot, "background", owned_backgrounds, self)
        await interaction.followup.send(content="Escolha um dos seus fundos para equipar:", view=view, ephemeral=True)

    @discord.ui.button(label="Mudar Skin", style=discord.ButtonStyle.secondary, emoji="👤")
    async def change_skin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        owned_skins = await self.get_owned_items(str(interaction.user.id), "bea_skin")
        if not owned_skins: await interaction.followup.send("Você não possui nenhuma skin! Visite a `/loja` para comprar.", ephemeral=True); return
        view = SelectionView(self.bot, "bea_skin", owned_skins, self)
        await interaction.followup.send(content="Escolha uma das suas skins para a Bea:", view=view, ephemeral=True)
            
    @discord.ui.button(label="Mudar Título", style=discord.ButtonStyle.secondary, emoji="📜")
    async def change_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        owned_titles = await self.get_owned_items(str(interaction.user.id), "title")
        view = SelectionView(self.bot, "title", owned_titles, self)
        await interaction.followup.send(content="Escolha um dos seus títulos para exibir:", view=view, ephemeral=True)

class SelectionView(discord.ui.View):
    def __init__(self, bot, item_type: str, options: list, parent_view: ProfileEditView):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_type = item_type
        self.parent_view = parent_view
        select_options = []
        for item_id in options:
            item_name = CATALOGO_LOJA.get(self.item_type + 's', {}).get(item_id, {}).get("nome", item_id)
            select_options.append(discord.SelectOption(label=item_name, value=item_id))
        self.select_menu = discord.ui.Select(placeholder=f"Escolha um novo {self.item_type} para equipar...", options=select_options)
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_value = interaction.data['values'][0]
        user_id = str(interaction.user.id)
        
        await self.bot.inventories.update_one(
            {"user_id": user_id},
            {"$set": {f"profile.{self.item_type}": selected_value}},
            upsert=True
        )
        await self.parent_view.send_profile_or_error(interaction, is_edit=True, is_public=False)

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="perfil", description="Mostra o seu cartão de perfil da Bea.")
    async def perfil(self, interaction: discord.Interaction):
        # Defer público para que a resposta seja visível para todos
        await interaction.response.defer() 
        view = ProfileEditView(self.bot)
        view.clear_items()
        # Chama a função de envio marcando como pública
        await view.send_profile_or_error(interaction, is_public=True)

    @app_commands.command(name="editar_perfil", description="Abre o menu para customizar seu cartão de perfil.")
    async def editar_perfil(self, interaction: discord.Interaction):
        # Defer privado, como estava antes
        await interaction.response.defer(ephemeral=True) 
        view = ProfileEditView(self.bot)
        # Chama a função de envio marcando como privada (is_public=False)
        await view.send_profile_or_error(interaction, is_public=False)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))