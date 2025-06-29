import discord
from discord.ext import commands
from discord import app_commands
from config import CATALOGO_LOJA

# --- Forward declarations para type hinting ---
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot_bea import TalkingBeaBot

# --- NOVA VIEW PARA O BOTÃO DE VOLTAR ---
class BackToShopView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot"):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="⬅️ Voltar para a Loja", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_coins = user_data.get("coins", 0)
        embed = discord.Embed(
            title="🛒 Loja da Bea",
            description="Bem-vindo(a)! Gaste suas moedas suadas em itens incríveis. Escolha uma categoria.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Seu Saldo Atual", value=f"{user_coins} moedas 🪙")
        await interaction.response.edit_message(embed=embed, view=ShopView(self.bot))

# --- VIEW PRINCIPAL DA LOJA ---
class ShopView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot"):
        super().__init__(timeout=300)
        self.bot = bot

    async def handle_category_click(self, interaction: discord.Interaction, item_type: str):
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_purchases = user_data.get("purchased_items", {}).get(item_type, [])
        available_items = [{"id": item_id, **data} for item_id, data in CATALOGO_LOJA[item_type].items() if item_id not in user_purchases]

        if not available_items:
            embed = discord.Embed(
                title="🛒 Categoria Vazia",
                description="Você já possui todos os itens desta categoria!",
                color=discord.Color.orange()
            )
            await interaction.response.edit_message(embed=embed, view=BackToShopView(self.bot))
            return

        await interaction.response.defer(ephemeral=True)

        if item_type in ["backgrounds", "bea_skins"]:
            # Inicia o carrossel com a lista de itens disponíveis NO MOMENTO ATUAL
            view = CarouselView(self.bot, item_type, str(interaction.user.id))
            await view.send(interaction) # O método send agora inicia o carrossel
        else:
            view = ItemListView(self.bot, item_type, available_items, user_data)
            await view.send(interaction)

    @discord.ui.button(label="Fundos", style=discord.ButtonStyle.primary, emoji="🖼️")
    async def backgrounds_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_category_click(interaction, "backgrounds")

    @discord.ui.button(label="Skins da Bea", style=discord.ButtonStyle.primary, emoji="👤")
    async def bea_skins_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_category_click(interaction, "bea_skins")

    @discord.ui.button(label="Títulos", style=discord.ButtonStyle.primary, emoji="📜")
    async def titles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_category_click(interaction, "titles")


# vvvvvvv  A ÚNICA PARTE QUE MUDOU FOI ESTA CLASSE  vvvvvvv

# --- VIEW DE CARROSSEL COM LÓGICA "F5" (RECARREGAMENTO TOTAL) ---
class CarouselView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_type: str, user_id: str):
        super().__init__(timeout=300)
        self.bot = bot
        self.item_type = item_type
        self.user_id = user_id
        self.items = []  # A lista de itens será carregada dinamicamente
        self.current_index = 0

    async def _f5_refresh(self, interaction: discord.Interaction):
        """
        A função "F5": Busca tudo do zero no banco de dados e atualiza a view.
        Esta é a fonte da verdade para o estado da loja.
        """
        # 1. Pega os dados mais recentes do usuário no banco
        user_data = await self.bot.inventories.find_one({"user_id": self.user_id}) or {}
        user_purchases = user_data.get("purchased_items", {}).get(self.item_type, [])
        user_coins = user_data.get("coins", 0)

        # 2. Recalcula a lista de itens que o usuário PODE comprar
        self.items = [{"id": item_id, **data} for item_id, data in CATALOGO_LOJA[self.item_type].items() if item_id not in user_purchases]

        # 3. Se não houver mais itens, encerra a view.
        if not self.items:
            # Edita a mensagem original para informar que acabaram os itens e remove os botões.
            await interaction.edit_original_response(content="Você comprou todos os itens desta categoria!", embed=None, view=None)
            return

        # 4. Garante que o índice é válido para a nova lista de itens.
        if self.current_index >= len(self.items):
            self.current_index = len(self.items) - 1

        # 5. Atualiza o estado de todos os botões (habilitado/desabilitado)
        self.prev_button.disabled = self.current_index == 0
        self.next_button.disabled = self.current_index >= len(self.items) - 1
        self.buy_button.disabled = user_coins < self.items[self.current_index]["preco"]

        # 6. Cria o embed com as informações atualizadas
        item = self.items[self.current_index]
        embed = discord.Embed(
            title=f"🛒 {item['nome']}",
            description=f"**Preço:** {item['preco']} moedas 🪙\n**Seu saldo:** {user_coins} moedas",
            color=discord.Color.blurple()
        )
        if item.get("imagem_url"):
            embed.set_image(url=item["imagem_url"])
        embed.set_footer(text=f"Item {self.current_index + 1} de {len(self.items)}")
        
        # 7. Edita a mensagem com o novo embed e botões atualizados.
        await interaction.edit_original_response(embed=embed, view=self)

    async def send(self, interaction: discord.Interaction):
        """Método inicial para enviar o carrossel pela primeira vez."""
        # A interação original da ShopView já foi deferida, então usamos edit_original_response
        # para substituir a tela de "carregando" pelo carrossel.
        await self._f5_refresh(interaction)

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.current_index > 0:
            self.current_index -= 1
        await self._f5_refresh(interaction)

    @discord.ui.button(label="Comprar", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # A interação do botão precisa ser respondida antes de qualquer coisa
        await interaction.response.defer()
        
        item_to_buy = self.items[self.current_index]

        # Faz a transação no banco de dados
        await self.bot.inventories.update_one(
            {"user_id": self.user_id},
            {"$inc": {"coins": -item_to_buy["preco"]}, "$push": {f"purchased_items.{self.item_type}": item_to_buy["id"]}},
            upsert=True
        )
        
        # Envia uma mensagem de confirmação separada e temporária
        await interaction.followup.send(f"✅ Parabéns! Você comprou '{item_to_buy['nome']}'!", ephemeral=True)
        
        # Chama a função "F5" para recarregar a loja do zero a partir do banco de dados
        await self._f5_refresh(interaction)
            
    @discord.ui.button(label="Próximo ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
        await self._f5_refresh(interaction)

    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.red, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_response()

# ^^^^^^^  A ÚNICA PARTE QUE MUDOU FOI A CLASSE ACIMA  ^^^^^^^


# --- VIEW DE LISTA PARA "TÍTULOS" ---
# (Nenhuma alteração aqui, está como você mandou)
class ItemListView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_type: str, items: list, user_data: dict):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_type = item_type
        self.items = items
        self.user_id = user_data.get("user_id", str(user_data["_id"]))
        self.build_view()

    def build_view(self):
        self.clear_items()
        select_options = [discord.SelectOption(label=item["nome"], description=f"Preço: {item['preco']} moedas 🪙", value=item["id"]) for item in self.items]
        select_menu = discord.ui.Select(placeholder="Selecione um título para comprar...", options=select_options)
        select_menu.callback = self.purchase_callback
        self.add_item(select_menu)
        
        close_button = discord.ui.Button(label="Fechar", style=discord.ButtonStyle.red, row=1)
        close_button.callback = self.close_button_callback
        self.add_item(close_button)

    async def send(self, interaction: discord.Interaction):
        await interaction.followup.send(content=f"Itens disponíveis na categoria '{self.item_type}'", view=self, ephemeral=True)

    async def purchase_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        item_id = interaction.data["values"][0]
        item_data = next((item for item in self.items if item["id"] == item_id), None)
        
        user_data = await self.bot.inventories.find_one({"user_id": self.user_id}) or {}
        if user_data.get("coins", 0) < item_data["preco"]:
            await interaction.followup.send("Você não tem moedas suficientes!", ephemeral=True, delete_after=5)
            return

        await self.bot.inventories.update_one({"user_id": self.user_id}, {"$inc": {"coins": -item_data["preco"]}, "$push": {f"purchased_items.{self.item_type}": item_id}}, upsert=True)
        await interaction.followup.send(f"Parabéns! Você comprou o título '{item_data['nome']}'!", ephemeral=True)
        
        self.items = [item for item in self.items if item["id"] != item_id]
        if not self.items:
            await interaction.message.delete()
        else:
            self.build_view()
            await interaction.message.edit(view=self)
            
    async def close_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()

# --- CLASSE PRINCIPAL DO COG ---
class ShopCog(commands.Cog):
    def __init__(self, bot: "TalkingBeaBot"):
        self.bot = bot

    @app_commands.command(name="loja", description="Abre a loja para comprar itens de personalização.")
    async def loja(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_coins = user_data.get("coins", 0)
        embed = discord.Embed(title="🛒 Loja da Bea", description="Bem-vindo(a)! Gaste suas moedas suadas em itens incríveis. Escolha uma categoria.", color=discord.Color.gold())
        embed.add_field(name="Seu Saldo Atual", value=f"{user_coins} moedas 🪙")
        await interaction.followup.send(embed=embed, view=ShopView(self.bot), ephemeral=True)

# --- FUNÇÃO SETUP PARA CARREGAR O COG ---
async def setup(bot: "TalkingBeaBot"):
    await bot.add_cog(ShopCog(bot))