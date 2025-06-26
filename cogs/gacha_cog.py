# cogs/gacha_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import RARIDADES, LISTA_DE_CARTAS, CARACTERE_INVISIVEL

class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Dentro da classe GachaCog, em cogs/gacha_cog.py

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
            await self.bot.inventories.update_one(
                {"user_id": user_id, "inventory.titulo": carta_sorteada['titulo']},
                {"$inc": {"inventory.$.quantidade": 1}}
            )
        else:
            is_new_card = True
            nova_carta = {"titulo": carta_sorteada['titulo'], "raridade": carta_sorteada['raridade'], "quantidade": 1}
            await self.bot.inventories.update_one(
                {"user_id": user_id},
                {"$push": {"inventory": nova_carta}, "$setOnInsert": {"user_name": interaction.user.name}},
                upsert=True
            )

        raridade_info = RARIDADES[carta_sorteada['raridade']]
        embed = discord.Embed(title=carta_sorteada['titulo'], description=f"**Nota da Chef Bea:**\n*{carta_sorteada['descricao']}*", color=raridade_info['cor'])
        embed.set_author(name=raridade_info['estrelas'])
        embed.set_image(url=carta_sorteada['foto'])
        embed.set_footer(text=f"Prato preparado para: {interaction.user.name}" + CARACTERE_INVISIVEL * 12)
        
        await interaction.edit_original_response(content="", embed=embed)

        if is_new_card:
            await interaction.followup.send("🎉 **NOVA RECEITA DESCOBERTA!** 🎉", )

        # --- NOVO: Alerta especial para cartas amaldiçoadas ---
        if carta_sorteada['raridade'] == 'AMALDIÇOADO':
            # Envia uma nova mensagem PÚBLICA no canal marcando @everyone
            alerta = (
                "🚨 CUIDADO, @everyone! 🚨\n\n"
                f"O desastre aconteceu! **{interaction.user.mention}** acaba de preparar uma receita **AMALDIÇOADA**! 💀"
            )
            await interaction.channel.send(alerta)

            
    @app_commands.command(name="inventario", description="Mostra todas as suas cartas de receitas coletadas.")
    async def inventario(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # Busca os dados do usuário diretamente do banco de dados
        user_data = await self.bot.inventories.find_one({"user_id": user_id})
        user_inventory = user_data.get('inventory', []) if user_data else []

        if not user_inventory:
            await interaction.response.send_message("Seu inventário está vazio!", ephemeral=True)
            return
            
        cartas_descobertas = len(user_inventory)
        total_de_cartas = len(LISTA_DE_CARTAS)
        cartas_faltando = total_de_cartas - cartas_descobertas
        
        rarity_order = ["AMALDIÇOADO", "HOLO", "LENDARIO", "RARO", "COMUM"]
        user_inventory.sort(key=lambda x: rarity_order.index(x['raridade']))
        
        embed = discord.Embed(title=f"Inventário de {interaction.user.name}", description=f"Você descobriu **{cartas_descobertas}** de **{total_de_cartas}** receitas!\nFaltam **{cartas_faltando}**.", color=discord.Color.green())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        
        for item in user_inventory:
            raridade_estrelas = RARIDADES[item['raridade']]['estrelas']
            embed.add_field(name=f"{item['titulo']} (x{item['quantidade']})", value=raridade_estrelas, inline=False)
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GachaCog(bot))