# cogs/trading_cog.py

import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict
from config import LISTA_DE_CARTAS
import re

# --- Forward declarations para type hinting ---
from typing import Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from bot_bea import TalkingBeaBot

# Dicionário para guardar o estado das trocas ativas. Chave: ID da mensagem da troca.
active_trades: Dict[int, Any] = {}

class TradeState:
    """Guarda todos os dados de uma troca em andamento."""
    def __init__(self, p1: discord.Member, p2: discord.Member, inventories: dict):
        self.p1 = p1
        self.p2 = p2
        self.inventories = inventories
        self.offers = {
            p1.id: {'coins': 0, 'recipes': defaultdict(int)},
            p2.id: {'coins': 0, 'recipes': defaultdict(int)}
        }
        self.ready_status = {
            p1.id: False,
            p2.id: False
        }

# --- MODAL (POP-UP) PARA EDITAR A PROPOSTA ---
class TradeOfferModal(discord.ui.Modal, title="Editar Proposta de Troca"):
    def __init__(self, trade_view):
        super().__init__()
        self.trade_view = trade_view
        user = trade_view.current_interaction.user
        
        is_p1 = user.id == trade_view.trade_state.p1.id
        self.offer = trade_view.trade_state.offers[user.id]
        self.inventory = trade_view.trade_state.inventories[user.id]

        self.coins_input = discord.ui.TextInput(
            label=f"Moedas (Seu saldo: {self.inventory.get('coins', 0)})",
            default=str(self.offer['coins']),
            required=False,
            placeholder="Ex: 100"
        )
        self.add_item(self.coins_input)
        
        recipes_str = ", ".join([f"{name}:{qty}" for name, qty in self.offer['recipes'].items()])
        self.recipes_input = discord.ui.TextInput(
            label="Receitas (Formato: Nome:Qtd, Nome2:Qtd)",
            style=discord.TextStyle.paragraph,
            default=recipes_str,
            required=False,
            placeholder="Ex: Pão Queimado:5, Torta Crua:1"
        )
        self.add_item(self.recipes_input)

    async def on_submit(self, interaction: discord.Interaction):
        print(f"[LOG] Modal de oferta submetido por {interaction.user}")
        try:
            # Validação das moedas
            coins_val = self.coins_input.value
            offered_coins = int(coins_val) if coins_val else 0
            if offered_coins < 0 or offered_coins > self.inventory.get('coins', 0):
                raise ValueError("Moedas inválidas ou saldo insuficiente")

            # Validação das receitas
            offered_recipes = defaultdict(int)
            if self.recipes_input.value:
                for entry in self.recipes_input.value.split(','):
                    entry = entry.strip()
                    if not entry: continue
                    parts = [p.strip() for p in entry.split(':')]
                    if len(parts) == 0: continue
                    name = parts[0]
                    qty = int(parts[1]) if len(parts) > 1 else 1
                    if qty <= 0: raise ValueError("Quantidade deve ser positiva")
                    
                    # Usa a estrutura correta do seu inventário
                    user_recipes = self.inventory.get("inventory", [])
                    item_in_inv = next((item for item in user_recipes if item['titulo'] == name), None)
                    
                    if not item_in_inv or item_in_inv.get('quantidade', 0) < qty:
                         return await interaction.response.send_message(f"Você não tem {qty}x {name}!", ephemeral=True)
                    offered_recipes[name] = qty
            
            # Atualiza o estado da troca e reseta as confirmações (anti-golpe)
            self.trade_view.update_offer(interaction.user, offered_coins, offered_recipes)
            await self.trade_view.update_message(interaction, reset_confirmations=True)

        except ValueError:
            await interaction.response.send_message("Formato inválido para moedas ou quantidades. Use apenas números positivos.", ephemeral=True)
        except Exception as e:
            print(f"[ERRO] Falha no on_submit do modal: {e}")
            await interaction.response.send_message(f"Ocorreu um erro: {e}", ephemeral=True)


# --- VIEW INTELIGENTE E ÚNICA PARA A TROCA ---
class TradeView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", author: discord.Member, target: discord.Member, inventories: dict):
        super().__init__(timeout=600)
        self.bot = bot
        self.trade_state = TradeState(author, target, inventories)
        self.current_stage = "invite"
        self.message: discord.Message = None
        self.update_components()

    def update_components(self):
        print(f"[LOG] update_components: Atualizando view para o estado '{self.current_stage}'")
        self.clear_items()
        if self.current_stage == "invite":
            accept_btn = discord.ui.Button(label="Aceitar", style=discord.ButtonStyle.green)
            decline_btn = discord.ui.Button(label="Recusar", style=discord.ButtonStyle.red)
            accept_btn.callback = self.accept_callback
            decline_btn.callback = self.decline_callback
            self.add_item(accept_btn)
            self.add_item(decline_btn)
        elif self.current_stage == "trading":
            edit_btn = discord.ui.Button(label="Editar Minha Proposta", style=discord.ButtonStyle.primary, emoji="✍️")
            confirm_btn = discord.ui.Button(label="Confirmar Troca", style=discord.ButtonStyle.success, emoji="✅")
            cancel_btn = discord.ui.Button(label="Cancelar Troca", style=discord.ButtonStyle.danger, emoji="❌")
            edit_btn.callback = self.edit_offer_callback
            confirm_btn.callback = self.confirm_callback
            cancel_btn.callback = self.cancel_callback
            self.add_item(edit_btn)
            self.add_item(confirm_btn)
            self.add_item(cancel_btn)

    def create_embed(self) -> discord.Embed:
        state = self.trade_state
        if self.current_stage == "invite":
            return discord.Embed(description=f"{state.p2.mention}, {state.p1.mention} quer trocar com você!", color=discord.Color.yellow())
        
        embed = discord.Embed(title="Mesa de Troca", color=discord.Color.blurple())
        
        p1_ready = state.ready_status[state.p1.id]
        p1_status = "✅ Confirmado" if p1_ready else "⏳ Pendente"
        p1_recipes = ", ".join([f"{qty}x {name}" for name, qty in state.offers[state.p1.id]["recipes"].items()]) or "Nenhuma"
        embed.add_field(name=f"Oferta de {state.p1.display_name}", value=f"**Moedas:** {state.offers[state.p1.id]['coins']} 🪙\n**Receitas:** {p1_recipes}\n**Status:** {p1_status}", inline=False)
        
        p2_ready = state.ready_status[state.p2.id]
        p2_status = "✅ Confirmado" if p2_ready else "⏳ Pendente"
        p2_recipes = ", ".join([f"{qty}x {name}" for name, qty in state.offers[state.p2.id]["recipes"].items()]) or "Nenhuma"
        embed.add_field(name=f"Oferta de {state.p2.display_name}", value=f"**Moedas:** {state.offers[state.p2.id]['coins']} 🪙\n**Receitas:** {p2_recipes}\n**Status:** {p2_status}", inline=False)
        
        if all(state.ready_status.values()): embed.set_footer(text="Ambos confirmaram! Processando a troca...")
        else: embed.set_footer(text="Use 'Editar' para mudar sua oferta ou 'Confirmar'. Mudar a oferta reseta as confirmações.")
        return embed

    def update_offer(self, user: discord.User, coins: int, recipes: dict):
        self.trade_state.offers[user.id] = {'coins': coins, 'recipes': recipes}

    async def update_message(self, interaction: discord.Interaction, reset_confirmations: bool = False):
        print(f"[LOG] update_message chamado por {interaction.user}. Resetar: {reset_confirmations}")
        if reset_confirmations:
            self.trade_state.ready_status = {k: False for k in self.trade_state.ready_status}
        
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in [self.trade_state.p1.id, self.trade_state.p2.id]:
            await interaction.response.send_message("Esta não é a sua troca!", ephemeral=True)
            return False
        self.current_interaction = interaction
        return True

    # Callbacks dos Botões
    async def accept_callback(self, interaction: discord.Interaction):
        print(f"[LOG] Troca aceita por {interaction.user}")
        if interaction.user.id != self.trade_state.p2.id:
            return await interaction.response.send_message("Apenas o destinatário pode aceitar.", ephemeral=True)
        self.current_stage = "trading"
        self.update_components()
        await interaction.response.edit_message(content="Troca iniciada! Usem os botões abaixo.", embed=self.create_embed(), view=self)

    async def decline_callback(self, interaction: discord.Interaction):
        print(f"[LOG] Troca recusada por {interaction.user}")
        await interaction.message.delete()
        if self.message.id in active_trades: del active_trades[self.message.id]
        self.stop()

    async def edit_offer_callback(self, interaction: discord.Interaction):
        print(f"[LOG] Botão 'Editar Proposta' clicado por {interaction.user}")
        await interaction.response.send_modal(TradeOfferModal(self))
    
    async def confirm_callback(self, interaction: discord.Interaction):
        print(f"[LOG] Botão 'Confirmar' clicado por {interaction.user}")
        self.trade_state.ready_status[interaction.user.id] = True
        
        if all(self.trade_state.ready_status.values()):
            await self.execute_trade(interaction)
        else:
            await interaction.response.send_message("Você confirmou sua oferta. Aguardando o outro jogador...", ephemeral=True, delete_after=5)
            await self.message.edit(embed=self.create_embed())

    async def cancel_callback(self, interaction: discord.Interaction):
        print(f"[LOG] Troca cancelada por {interaction.user}")
        await interaction.message.delete()
        if self.message.id in active_trades: del active_trades[self.message.id]
        self.stop()

    async def execute_trade(self, interaction: discord.Interaction):
        print(f"[LOG] execute_trade: Iniciando para a troca {self.message.id}")
        await interaction.response.edit_message(content="Processando a troca... ⏳", embed=None, view=None)
        
        state = self.trade_state
        p1_id, p2_id = str(state.p1.id), str(state.p2.id)
        
        # --- VALIDAÇÃO FINAL (ANTI-GOLPE) ---
        print("[LOG] execute_trade: Realizando validação final de inventários...")
        p1_inv = await self.bot.inventories.find_one({"user_id": p1_id})
        p2_inv = await self.bot.inventories.find_one({"user_id": p2_id})

        # Valida a oferta do Jogador 1
        if p1_inv.get('coins', 0) < state.offers[state.p1.id]['coins']:
            return await interaction.followup.send(f"Troca cancelada! {state.p1.mention} não tem moedas suficientes.", ephemeral=False)
        for recipe, qty in state.offers[state.p1.id]['recipes'].items():
            if next((item for item in p1_inv.get('inventory', []) if item['titulo'] == recipe), {}).get('quantidade', 0) < qty:
                return await interaction.followup.send(f"Troca cancelada! {state.p1.mention} não tem {qty}x {recipe}.", ephemeral=False)

        # Valida a oferta do Jogador 2
        if p2_inv.get('coins', 0) < state.offers[state.p2.id]['coins']:
            return await interaction.followup.send(f"Troca cancelada! {state.p2.mention} não tem moedas suficientes.", ephemeral=False)
        for recipe, qty in state.offers[state.p2.id]['recipes'].items():
            if next((item for item in p2_inv.get('inventory', []) if item['titulo'] == recipe), {}).get('quantidade', 0) < qty:
                return await interaction.followup.send(f"Troca cancelada! {state.p2.mention} não tem {qty}x {recipe}.", ephemeral=False)
        
        print("[LOG] execute_trade: Validação final bem-sucedida.")

        # --- EXECUÇÃO DAS TRANSFERÊNCIAS NO DB ---
        try:
            # Atualiza moedas
            print(f"[LOG] execute_trade: Atualizando moedas...")
            await self.bot.inventories.update_one({"user_id": p1_id}, {"$inc": {"coins": state.offers[state.p2.id]['coins'] - state.offers[state.p1.id]['coins']}})
            await self.bot.inventories.update_one({"user_id": p2_id}, {"$inc": {"coins": state.offers[state.p1.id]['coins'] - state.offers[state.p2.id]['coins']}})
            
            # Transfere itens do P1 para o P2
            print(f"[LOG] execute_trade: Transferindo itens de {state.p1.name} para {state.p2.name}...")
            for recipe, qty in state.offers[state.p1.id]['recipes'].items():
                # Remove do P1
                await self.bot.inventories.update_one({"user_id": p1_id, "inventory.titulo": recipe}, {"$inc": {"inventory.$.quantidade": -qty}})
                # Adiciona ao P2
                if await self.bot.inventories.count_documents({"user_id": p2_id, "inventory.titulo": recipe}) > 0:
                    await self.bot.inventories.update_one({"user_id": p2_id, "inventory.titulo": recipe}, {"$inc": {"inventory.$.quantidade": qty}})
                else:
                    raridade = next((card['raridade'] for card in LISTA_DE_CARTAS if card['titulo'] == recipe), "COMUM")
                    await self.bot.inventories.update_one({"user_id": p2_id}, {"$push": {"inventory": {"titulo": recipe, "raridade": raridade, "quantidade": qty}}})
            
            # Transfere itens do P2 para o P1
            print(f"[LOG] execute_trade: Transferindo itens de {state.p2.name} para {state.p1.name}...")
            for recipe, qty in state.offers[state.p2.id]['recipes'].items():
                # Remove do P2
                await self.bot.inventories.update_one({"user_id": p2_id, "inventory.titulo": recipe}, {"$inc": {"inventory.$.quantidade": -qty}})
                # Adiciona ao P1
                if await self.bot.inventories.count_documents({"user_id": p1_id, "inventory.titulo": recipe}) > 0:
                    await self.bot.inventories.update_one({"user_id": p1_id, "inventory.titulo": recipe}, {"$inc": {"inventory.$.quantidade": qty}})
                else:
                    raridade = next((card['raridade'] for card in LISTA_DE_CARTAS if card['titulo'] == recipe), "COMUM")
                    await self.bot.inventories.update_one({"user_id": p1_id}, {"$push": {"inventory": {"titulo": recipe, "raridade": raridade, "quantidade": qty}}})
            
            # Remove itens com quantidade zero
            print("[LOG] execute_trade: Limpando itens com quantidade zero...")
            await self.bot.inventories.update_many({}, {"$pull": {"inventory": {"quantidade": {"$lte": 0}}}})
            
            # --- FINALIZAÇÃO ---
            print("[LOG] execute_trade: Transação no DB concluída.")
            final_embed = self.create_embed()
            final_embed.title = "✅ Troca Concluída com Sucesso!"
            final_embed.color = discord.Color.green()
            await interaction.edit_original_response(content="", embed=final_embed)
            
        except Exception as e:
            print(f"[ERRO] Falha crítica ao executar a troca no DB: {e}")
            await interaction.edit_original_response(content=f"Ocorreu um erro crítico ao processar a troca. Chame um admin. Erro: {e}", embed=None, view=None)
        
        finally:
            if self.message.id in active_trades: del active_trades[self.message.id]
            self.stop()
            print(f"[LOG] execute_trade: Troca {self.message.id} finalizada e removida da lista ativa.")

        final_embed = self.create_embed()
        final_embed.title = "✅ Troca Concluída com Sucesso!"
        final_embed.color = discord.Color.green()
        await interaction.message.edit(content="", embed=final_embed)
        if self.message.id in active_trades: del active_trades[self.message.id]
        self.stop()


class TradingCog(commands.Cog):
    def __init__(self, bot: "TalkingBeaBot"):
        self.bot = bot

    @app_commands.command(name="trocar", description="Inicia uma troca com outro membro.")
    @app_commands.describe(membro="O membro com quem você quer trocar.")
    async def trocar(self, interaction: discord.Interaction, membro: discord.Member):
        print(f"[LOG] Comando /trocar usado por {interaction.user} com alvo {membro}")
        if membro.id == interaction.user.id or membro.bot:
            await interaction.response.send_message("Seleção inválida.", ephemeral=True); return

        p1_inv = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        p2_inv = await self.bot.inventories.find_one({"user_id": str(membro.id)}) or {}
        inventories = {interaction.user.id: p1_inv, membro.id: p2_inv}

        view = TradeView(self.bot, interaction.user, membro, inventories)
        embed = view.create_embed()
        
        await interaction.response.send_message(embed=embed, view=view)
        message = await interaction.original_response()
        view.message = message
        active_trades[message.id] = view.trade_state

async def setup(bot: "TalkingBeaBot"):
    await bot.add_cog(TradingCog(bot))