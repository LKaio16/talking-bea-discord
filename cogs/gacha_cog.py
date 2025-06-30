# cogs/gacha_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import RARIDADES, LISTA_DE_CARTAS, CARACTERE_INVISIVEL

# --- CLASSE DO MODAL (FORMULÁRIO POP-UP) ---
class SellQuantityModal(discord.ui.Modal, title="Vender Receita"):
    def __init__(self, bot, item_to_sell):
        super().__init__()
        self.bot = bot
        self.item_to_sell = item_to_sell
        
        self.quantity_input = discord.ui.TextInput(
            label="Quantidade para vender",
            placeholder=f"Você tem {item_to_sell['quantidade']} unidades. Digite um número...",
            required=True
        )
        self.add_item(self.quantity_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantity_to_sell = int(self.quantity_input.value)
            if quantity_to_sell <= 0:
                await interaction.response.send_message("A quantidade deve ser um número positivo.", ephemeral=True)
                return
            if quantity_to_sell > self.item_to_sell['quantidade']:
                await interaction.response.send_message(f"Você não pode vender {quantity_to_sell} unidades! Você só tem {self.item_to_sell['quantidade']}.", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message("Por favor, digite um número válido.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        valor_venda_total = RARIDADES[self.item_to_sell['raridade']]['valor'] * quantity_to_sell

        if quantity_to_sell < self.item_to_sell['quantidade']:
            await self.bot.inventories.update_one(
                {"user_id": user_id, "inventory.titulo": self.item_to_sell['titulo']},
                {"$inc": {"inventory.$.quantidade": -quantity_to_sell, "coins": valor_venda_total}}
            )
        else:
            await self.bot.inventories.update_one(
                {"user_id": user_id},
                {
                    "$pull": {"inventory": {"titulo": self.item_to_sell['titulo']}},
                    "$inc": {"coins": valor_venda_total}
                }
            )

        await interaction.response.send_message(
            f"✅ Você vendeu **{quantity_to_sell}x {self.item_to_sell['titulo']}** por **{valor_venda_total}** moedas! 🪙",
            ephemeral=True
        )

# --- CLASSE DA VIEW DE VENDA ---
class SellView(discord.ui.View):
    def __init__(self, bot, user_inventory):
        super().__init__(timeout=180)
        self.bot = bot

        options = []
        for item in user_inventory:
            raridade_info = RARIDADES[item['raridade']]
            options.append(discord.SelectOption(
                label=f"{item['titulo']} (x{item['quantidade']})",
                value=item['titulo'],
                description=f"Valor: {raridade_info['valor']} moedas cada."
            ))

        self.select_menu = discord.ui.Select(
            placeholder="Escolha uma receita para vender...",
            options=options
        )
        self.select_menu.callback = self.select_callback
        self.add_item(self.select_menu)

    async def select_callback(self, interaction: discord.Interaction):
        selected_title = interaction.data['values'][0]
        
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)})
        # Garante que temos a quantidade mais atualizada antes de abrir o modal
        item_to_sell = next((item for item in user_data['inventory'] if item['titulo'] == selected_title), None)

        if item_to_sell:
            modal = SellQuantityModal(self.bot, item_to_sell)
            await interaction.response.send_modal(modal)

# --- CLASSE PRINCIPAL DO COG ---
class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cozinhar", description="Prepara um prato aleatório para adicionar ao seu inventário.")
    async def cozinhar(self, interaction: discord.Interaction):
        await interaction.response.send_message("🍳 Preparando a cozinha, vamos ver o que sai...")
        await asyncio.sleep(2)
        cartas = LISTA_DE_CARTAS
        pesos = [RARIDADES[carta['raridade']]['peso'] for carta in cartas]
        carta_sorteada = random.choices(cartas, weights=pesos, k=1)[0]
        user_id = str(interaction.user.id)
        user_data = await self.bot.inventories.find_one({"user_id": user_id})
        is_new_card = False
        if user_data and any(item['titulo'] == carta_sorteada['titulo'] for item in user_data.get('inventory', [])):
            await self.bot.inventories.update_one({"user_id": user_id, "inventory.titulo": carta_sorteada['titulo']}, {"$inc": {"inventory.$.quantidade": 1}})
        else:
            is_new_card = True
            nova_carta = {"titulo": carta_sorteada['titulo'], "raridade": carta_sorteada['raridade'], "quantidade": 1}
            await self.bot.inventories.update_one({"user_id": user_id}, {"$push": {"inventory": nova_carta}, "$setOnInsert": {"user_name": interaction.user.name, "coins": 0}}, upsert=True)
        raridade_info = RARIDADES[carta_sorteada['raridade']]
        embed = discord.Embed(title=carta_sorteada['titulo'], description=f"**Nota da Chef Bea:**\n*{carta_sorteada['descricao']}*", color=raridade_info['cor'])
        embed.set_author(name=raridade_info['estrelas'])
        embed.set_image(url=carta_sorteada['foto'])
        embed.set_footer(text=f"Prato preparado para: {interaction.user.name}" + CARACTERE_INVISIVEL * 9)
        await interaction.edit_original_response(content="", embed=embed)
        if is_new_card: await interaction.followup.send("🎉 **NOVA RECEITA DESCOBERTA!** 🎉", ephemeral=True)
        if carta_sorteada['raridade'] == 'AMALDIÇOADO': await interaction.channel.send(f"🚨 CUIDADO, @everyone! 🚨\n\nO desastre aconteceu! **{interaction.user.mention}** acaba de preparar uma receita **AMALDIÇOADA**! 💀")

    @app_commands.command(name="inventario", description="Mostra o SEU inventário de receitas e saldo de moedas.")
    async def inventario(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        user_inventory = user_data.get('inventory', [])
        user_coins = user_data.get('coins', 0)
        
        is_private = user_data.get("profile", {}).get("inventory_is_private", False)
        print(is_private)
        
        await interaction.response.defer(ephemeral=is_private) 
        
        if not user_inventory:
            await interaction.followup.send("Seu inventário está vazio! Use `/cozinhar` para começar.", ephemeral=True)
            return
            
        cartas_descobertas = len(user_inventory)
        total_de_cartas = len(LISTA_DE_CARTAS)
        
        embed = discord.Embed(
            title=f"Inventário de {interaction.user.name}",
            description=f"Você descobriu **{cartas_descobertas}/{total_de_cartas}** receitas!\n**Saldo:** {user_coins} moedas 🪙",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.user.avatar.url)
        
        rarity_order = ["AMALDIÇOADO", "HOLO", "LENDARIO", "RARO", "COMUM"]
        user_inventory.sort(key=lambda x: rarity_order.index(x['raridade']))
        
        for item in user_inventory:
            raridade_info = RARIDADES[item['raridade']]
            embed.add_field(
                name=f"{item['titulo']} (x{item['quantidade']})",
                value=f"{raridade_info['estrelas']}\n*Valor de venda: {raridade_info['valor']} moedas*",
                inline=False
            )
        await interaction.followup.send(embed=embed, ephemeral=is_private)

    @app_commands.command(name="vender", description="Abre um menu interativo para vender suas receitas.")
    async def vender(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = str(interaction.user.id)
        user_data = await self.bot.inventories.find_one({"user_id": user_id}) or {}
        user_inventory = user_data.get('inventory', [])
        
        if not user_inventory:
            await interaction.followup.send("Você não tem nenhuma receita no inventário para vender!", ephemeral=True)
            return
            
        view = SellView(self.bot, user_inventory)
        await interaction.followup.send("Selecione a receita que você quer vender no menu abaixo:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(GachaCog(bot))