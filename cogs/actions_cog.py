import discord
from discord.ext import commands
from discord import app_commands
import datetime
from config import RARIDADES # Importa configs necessárias

# View para os botões de privacidade
class PrivacyView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=180)
        self.bot = bot

    async def set_privacy(self, interaction: discord.Interaction, is_private: bool):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        await self.bot.inventories.update_one(
            {"user_id": user_id},
            {"$set": {"profile.inventory_is_private": is_private}},
            upsert=True
        )
        status = "PRIVADO" if is_private else "PÚBLICO"
        await interaction.followup.send(f"A visibilidade do seu inventário foi definida como **{status}**.", ephemeral=True)
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="🔒 Privado", style=discord.ButtonStyle.red)
    async def make_private(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_privacy(interaction, True)

    @discord.ui.button(label="✅ Público", style=discord.ButtonStyle.green)
    async def make_public(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_privacy(interaction, False)

class ActionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ver_inventario", description="Use um Ticket de Espionagem para ver o inventário de outro jogador.")
    @app_commands.describe(alvo="O membro cujo inventário você quer ver.")
    async def ver_inventario(self, interaction: discord.Interaction, alvo: discord.Member):
        user_id = str(interaction.user.id)
        
        if alvo.id == interaction.user.id:
            await interaction.response.send_message("Para ver seu próprio inventário, use o comando `/inventario`!", ephemeral=True)
            return

        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        
        purchased_acoes = user_data.get("purchased_items", {}).get("acoes", {})
        owned_tickets = purchased_acoes.get("ticket_spy", 0)

        if owned_tickets < 1:
            await interaction.response.send_message("Você não possui um 'Ticket de Espionagem'! Compre na `/loja`.", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        target_id = str(alvo.id)
        target_data = await self.bot.inventories.find_one({"user_id": target_id}) or {}
        
        is_private = target_data.get("profile", {}).get("inventory_is_private", False)
        if is_private:
            await interaction.followup.send(f"Não foi possível espionar! O inventário de {alvo.display_name} é privado.", ephemeral=True)
            return

        await self.bot.inventories.update_one(
            {"user_id": user_id}, 
            {"$inc": {"purchased_items.acoes.ticket_spy": -1}}
        )
        
        target_inventory = target_data.get('inventory', [])
        # --- NEW: Get target's coins ---
        target_coins = target_data.get('coins', 0)
        # --- END NEW ---

        if not target_inventory:
            await interaction.followup.send(f"Você usou um ticket, mas o inventário de {alvo.display_name} está vazio.", ephemeral=True)
            return
            
        embed = discord.Embed(title=f"Inventário de {alvo.display_name}", color=discord.Color.blue())
        embed.set_thumbnail(url=alvo.display_avatar.url)
        # --- NEW: Add coins to embed description or field ---
        embed.description = f"**Saldo:** {target_coins} moedas 🪙"
        # --- END NEW ---

        rarity_order = ["AMALDIÇOADO", "HOLO", "LENDARIO", "RARO", "COMUM"]
        target_inventory.sort(key=lambda x: rarity_order.index(x['raridade']))

        for item in target_inventory:
            raridade_info = RARIDADES.get(item['raridade'], {"estrelas": "N/A", "valor": 0})
            embed.add_field(name=f"{item['titulo']} (x{item['quantidade']})", value=raridade_info['estrelas'], inline=False)
        await interaction.followup.send(content=f"Você usou um ticket de espionagem com sucesso!", embed=embed, ephemeral=True)

    @app_commands.command(name="privacidade", description="Define se seu inventário pode ser visto por outros.")
    async def privacidade(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        
        purchased_acoes = user_data.get("purchased_items", {}).get("acoes", {})
        if not purchased_acoes.get("unlock_privacy", False):
            await interaction.response.send_message("Você não comprou a 'Licença de Privacidade'! Adquira na `/loja`.", ephemeral=True)
            return
        
        current_status = "PRIVADO" if user_data.get("profile", {}).get("inventory_is_private", False) else "PÚBLICO"
        
        await interaction.response.send_message(f"Seu inventário está atualmente **{current_status}**. O que você deseja fazer?", view=PrivacyView(self.bot), ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActionsCog(bot))