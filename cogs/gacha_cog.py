# cogs/gacha_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import json
import asyncio
from config import RARIDADES, LISTA_DE_CARTAS, CARACTERE_INVISIVEL # Importa as configurações

INVENTORY_FILE = 'inventarios.json'

def carregar_inventarios():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return {}
    return {}

def salvar_inventarios(inventarios):
    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventarios, f, indent=4)

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
        inventarios = carregar_inventarios()
        user_id = str(interaction.user.id)
        user_inventory = inventarios.get(user_id, [])
        is_new_card = False
        carta_existente = next((item for item in user_inventory if item['titulo'] == carta_sorteada['titulo']), None)
        if carta_existente:
            carta_existente['quantidade'] += 1
        else:
            is_new_card = True
            nova_carta = {"titulo": carta_sorteada['titulo'], "raridade": carta_sorteada['raridade'], "quantidade": 1}
            user_inventory.append(nova_carta)
        inventarios[user_id] = user_inventory
        salvar_inventarios(inventarios)
        raridade_info = RARIDADES[carta_sorteada['raridade']]
        embed = discord.Embed(title=carta_sorteada['titulo'], description=f"**Nota da Chef Bea:**\n*{carta_sorteada['descricao']}*", color=raridade_info['cor'])
        embed.set_author(name=raridade_info['estrelas'])
        embed.set_image(url=carta_sorteada['foto'])
        embed.set_footer(text=f"Prato preparado para: {interaction.user.name}" + CARACTERE_INVISIVEL * 10)
        await interaction.edit_original_response(content="", embed=embed)
        if is_new_card:
            await interaction.followup.send("🎉 **NOVA RECEITA DESCOBERTA!** 🎉", ephemeral=True)

    @app_commands.command(name="inventario", description="Mostra todas as suas cartas de receitas coletadas.")
    async def inventario(self, interaction: discord.Interaction):
        inventarios = carregar_inventarios()
        user_id = str(interaction.user.id)
        user_inventory = inventarios.get(user_id, [])
        if not user_inventory:
            await interaction.response.send_message("Seu inventário está vazio!", ephemeral=True)
            return
        cartas_descobertas = len(user_inventory)
        total_de_cartas = len(LISTA_DE_CARTAS)
        cartas_faltando = total_de_cartas - cartas_descobertas
        rarity_order = list(RARIDADES.keys())
        rarity_order.reverse()
        user_inventory.sort(key=lambda x: rarity_order.index(x['raridade']))
        embed = discord.Embed(title=f"Inventário de {interaction.user.name}", description=f"Você descobriu **{cartas_descobertas}** de **{total_de_cartas}** receitas!\nFaltam **{cartas_faltando}**.", color=discord.Color.green())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        for item in user_inventory:
            raridade_estrelas = RARIDADES[item['raridade']]['estrelas']
            embed.add_field(name=f"{item['titulo']} (x{item['quantidade']})", value=raridade_estrelas, inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GachaCog(bot))