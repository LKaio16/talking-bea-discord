import discord
from discord.ext import commands
from discord import app_commands
from config import CATALOGO_LOJA, HEIST_CHANCES
import datetime
import random

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
        """Edita a mensagem para mostrar a tela inicial da loja novamente."""
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_coins = user_data.get("coins", 0)
        embed = discord.Embed(
            title="🛒 Loja da Bea",
            description="Bem-vindo(a)! Gaste suas moedas suadas em itens incríveis. GASTA AI BTL GASTA AI",
            color=discord.Color.gold()
        )
        embed.add_field(name="Seu Saldo Atual", value=f"{user_coins} moedas 🪙")
        
        await interaction.response.edit_message(embed=embed, view=ShopView(self.bot))

# --- VIEW PRINCIPAL DA LOJA ---
class ShopView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot"):
        super().__init__(timeout=300)
        self.bot = bot

    # --- LÓGICA DE CLIQUE CORRIGIDA E UNIFICADA ---
    async def handle_category_click(self, interaction: discord.Interaction, item_type: str):
        await interaction.response.defer(ephemeral=True)
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        
        available_items = []
        all_category_items = CATALOGO_LOJA.get(item_type, {})
        user_purchases = user_data.get("purchased_items", {})

        for item_id, data in all_category_items.items():
            # Define quais itens são de compra única (permanentes)
            is_permanent = (
                item_type in ["backgrounds", "bea_skins", "titles"] or 
                item_id == "unlock_privacy"
            )

            if is_permanent:
                # Para itens permanentes, verifica se o usuário já os possui na lista correta
                owned_items_list = user_purchases.get(item_type, [])
                if item_id not in owned_items_list:
                    available_items.append({"id": item_id, **data})
            else:
                # Para itens consumíveis ou de uso imediato (como o roubo), sempre mostra
                available_items.append({"id": item_id, **data})

        if not available_items:
            embed = discord.Embed(title="🛒 Categoria Vazia", description="Você já possui todos os itens desta categoria ou não há nada novo.", color=discord.Color.orange())
            await interaction.followup.send(embed=embed, view=BackToShopView(self.bot), ephemeral=True)
            return
            
        # Decide qual view mostrar com base no tipo de item
        if item_type in ["backgrounds", "bea_skins"]:
            view = CarouselView(self.bot, item_type, available_items, user_data)
            await view.send(interaction)
        else: # Para "titles" e "acoes"
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
        
    @discord.ui.button(label="Ações", style=discord.ButtonStyle.danger, emoji="⚡")
    async def actions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_category_click(interaction, "acoes")

# --- VIEW DE CARROSSEL ---
class CarouselView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_type: str, items: list, user_data: dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.item_type = item_type
        self.user_id = user_data.get("user_id", str(user_data["_id"]))
        self.items = items
        self.user_coins = user_data.get("coins", 0)
        self.current_index = 0

    async def send(self, interaction: discord.Interaction):
        self.update_buttons_state()
        embed = self.create_embed()
        await interaction.followup.send(embed=embed, view=self, ephemeral=True)

    def update_buttons_state(self):
        self.prev_button.disabled = self.current_index == 0
        self.next_button.disabled = self.current_index >= len(self.items) - 1
        current_item = self.items[self.current_index]
        self.buy_button.disabled = self.user_coins < current_item["preco"]

    def create_embed(self) -> discord.Embed:
        item = self.items[self.current_index]
        embed = discord.Embed(title=f"🛒 {item['nome']}", description=f"**Preço:** {item['preco']} moedas 🪙\n**Seu saldo:** {self.user_coins} moedas", color=discord.Color.blurple())
        if item.get("imagem_url"): embed.set_image(url=item["imagem_url"])
        embed.set_footer(text=f"Item {self.current_index + 1} de {len(self.items)}")
        return embed

    async def update_message(self, interaction: discord.Interaction):
        self.update_buttons_state()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️ Anterior", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index > 0: self.current_index -= 1
        await self.update_message(interaction)

    @discord.ui.button(label="Comprar", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        item_to_buy = self.items[self.current_index]

        await self.bot.inventories.update_one({"user_id": self.user_id}, {"$inc": {"coins": -item_to_buy["preco"]}, "$push": {f"purchased_items.{self.item_type}": item_to_buy["id"]}}, upsert=True)
        self.user_coins -= item_to_buy["preco"]
        
        await interaction.delete_original_response()

        await interaction.followup.send(f"✅ Parabéns! Você comprou '{item_to_buy['nome']}'!", ephemeral=True)
        
       

    @discord.ui.button(label="Próximo ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_index < len(self.items) - 1: self.current_index += 1
        await self.update_message(interaction)

    @discord.ui.button(label="Fechar", style=discord.ButtonStyle.red, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_response()

# --- VIEW PARA ESCOLHER A RARIDADE DO ROUBO ---
class HeistRarityView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_data: dict, thief: discord.Member, target: discord.Member):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_data = item_data
        self.thief = thief
        self.target = target

        # Opções de raridade para o dropdown
        rarity_options = [discord.SelectOption(label=r, value=r) for r in HEIST_CHANCES.keys()]
        self.rarity_select = discord.ui.Select(placeholder="Escolha a raridade da receita para roubar...", options=rarity_options)
        self.rarity_select.callback = self.rarity_select_callback
        self.add_item(self.rarity_select)

    async def rarity_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_rarity = interaction.data['values'][0]
        
        # --- A LÓGICA DO ROUBO ---
        thief_id = str(self.thief.id)
        target_id = str(self.target.id)
        
        # 1. Verifica se o ladrão tem dinheiro
        thief_data = await self.bot.inventories.find_one({"user_id": thief_id})
        if thief_data.get("coins", 0) < self.item_data['preco']:
            await interaction.followup.send("Você não tem mais moedas suficientes para esta operação!", ephemeral=True)
            await interaction.message.delete()
            return

        # 2. Debita as moedas do ladrão
        await self.bot.inventories.update_one({"user_id": thief_id}, {"$inc": {"coins": -self.item_data['preco']}})

        # 3. Verifica se o alvo tem cartas da raridade escolhida
        target_data = await self.bot.inventories.find_one({"user_id": target_id})
        target_cards_of_rarity = [card for card in target_data.get("inventory", []) if card['raridade'] == selected_rarity]

        if not target_cards_of_rarity:
            # Falha automática se o alvo não tem cartas daquela raridade
            await interaction.channel.send(f"😂 **ROUBO FRACASSADO!** {self.thief.mention} tentou roubar uma receita **{selected_rarity}** de {self.target.mention}, mas o alvo não tinha nenhuma! O dinheiro foi perdido.")
            await interaction.message.delete()
            return
            
        # 4. Rola o dado da sorte
        success_chance = HEIST_CHANCES[selected_rarity]
        if random.random() < success_chance:
            # SUCESSO!
            stolen_card = random.choice(target_cards_of_rarity)
            
            # Remove 1 da quantidade do alvo
            if stolen_card['quantidade'] > 1:
                await self.bot.inventories.update_one(
                    {"user_id": target_id, "inventory.titulo": stolen_card['titulo']},
                    {"$inc": {"inventory.$.quantidade": -1}}
                )
            else:
                await self.bot.inventories.update_one(
                    {"user_id": target_id},
                    {"$pull": {"inventory": {"titulo": stolen_card['titulo']}}}
                )
            
            # Adiciona 1 para o ladrão
            await self.bot.inventories.update_one(
                {"user_id": thief_id, "inventory.titulo": stolen_card['titulo']},
                {"$inc": {"inventory.$.quantidade": 1}},
                upsert=False # Não usa upsert, pois o user precisa existir
            )
            # Se o ladrão não tinha a carta, adiciona ela com quantidade 1
            thief_has_card = await self.bot.inventories.count_documents({"user_id": thief_id, "inventory.titulo": stolen_card['titulo']})
            if thief_has_card == 0:
                 await self.bot.inventories.update_one(
                    {"user_id": thief_id},
                    {"$push": {"inventory": {"titulo": stolen_card['titulo'], "raridade": stolen_card['raridade'], "quantidade": 1}}}
                )
            
            await interaction.followup.send(f"🤫 **Sucesso!** Você roubou **1x {stolen_card['titulo']}** de {self.target.display_name}!", ephemeral=True)
        else:
            # FALHA!
             
            # --- MODIFIED: Send embed instead of raw link ---
            mute_embed = discord.Embed(
                title="ROUBO FRACASSADO! 🤫",
                description=f"**{self.thief.name}**({self.thief.mention}) foi pego tentando roubar uma receita **{selected_rarity}** de **{self.target.name}**({self.target.mention}) e falhou miseravelmente!",
                color=discord.Color.red()
            )
            mute_embed.set_image(url="https://media.discordapp.net/attachments/1388606897774530570/1388666048571641927/chaves-seu-madruga.gif?ex=6861cf8a&is=68607e0a&hm=e53ce95268377fdd3a352567201f3b5026b1d46891df251993f9c94152d98caf&=&width=467&height=338")
            
            await interaction.channel.send(embed=mute_embed)
        
           # await interaction.channel.send(f"🚨 **ROUBO FRACASSADO!** {self.thief.mention} foi pego tentando roubar uma receita **{selected_rarity}** de {self.target.mention} e falhou miseravelmente!")

        await interaction.message.delete()


# --- VIEW PARA ESCOLHER O ALVO DO ROUBO ---
class HeistTargetView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_data: dict):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_data = item_data
        self.user_select = discord.ui.UserSelect(placeholder="Selecione o alvo do seu roubo...")
        self.user_select.callback = self.user_select_callback
        self.add_item(self.user_select)

    async def user_select_callback(self, interaction: discord.Interaction):
        target_member = self.user_select.values[0]
        if target_member.id == interaction.user.id:
            await interaction.response.send_message("Você não pode roubar de si mesmo, espertinho.", ephemeral=True, delete_after=5)
            return
        
        # Passa para a próxima etapa: escolher a raridade
        view = HeistRarityView(self.bot, self.item_data, interaction.user, target_member)
        await interaction.response.edit_message(content=f"Alvo selecionado: **{target_member.display_name}**. Agora, escolha a raridade que deseja tentar roubar:", view=view)

# --- VIEW DE LISTA PARA "TÍTULOS" E "AÇÕES" ---
class ItemListView(discord.ui.View):
    def __init__(self, bot: "TalkingBeaBot", item_type: str, items: list, user_data: dict):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_type = item_type
        self.items = items
        self.user_id = user_data.get("user_id", str(user_data["_id"]))
        self.user_data = user_data
        self.build_view()

    def build_view(self):
        self.clear_items()
        select_options = [discord.SelectOption(label=item["nome"], description=f"Preço: {item['preco']} moedas 🪙", value=item["id"]) for item in self.items]
        
        if not select_options:
            select_options.append(discord.SelectOption(label="Nenhum item disponível nesta categoria.", value="none", default=True, emoji="😔"))

        select_menu = discord.ui.Select(placeholder="Selecione um item para comprar...", options=select_options, disabled=not bool(select_options))
        select_menu.callback = self.purchase_callback
        self.add_item(select_menu)
        
        back_button = discord.ui.Button(label="⬅️ Voltar para a Loja", style=discord.ButtonStyle.grey, row=1)
        back_button.callback = self.back_to_shop_callback
        self.add_item(back_button)

        close_button = discord.ui.Button(label="Fechar", style=discord.ButtonStyle.red, row=1)
        close_button.callback = self.close_button_callback
        self.add_item(close_button)

    async def send(self, interaction: discord.Interaction):
        await interaction.followup.send(content=f"Itens disponíveis na categoria '{self.item_type}'", view=self, ephemeral=True)

    async def purchase_callback(self, interaction: discord.Interaction):
        selected_item_id = interaction.data['values'][0]
        
        if selected_item_id == "none":
            await interaction.response.defer()
            return
    
        item_data = next((item for item in self.items if item["id"] == selected_item_id), None)
        
        if not item_data:
            await interaction.response.send_message("Este item não está mais disponível.", ephemeral=True, delete_after=5)
            return

        current_user_data = await self.bot.inventories.find_one({"user_id": self.user_id}) or {}
        if current_user_data.get("coins", 0) < item_data["preco"]:
            await interaction.response.send_message("Você não tem moedas suficientes!", ephemeral=True, delete_after=5)
            return

        if selected_item_id == 'ticket_mute':
            await interaction.response.edit_message(
                content=f"Você está comprando **{item_data['nome']}**. Selecione o alvo abaixo:",
                view=MuteTargetView(self.bot, item_data, interaction.message)
            )
            return
        
              
        if selected_item_id == 'tentativa_roubo':
            await interaction.response.edit_message(
                content=f"Você está iniciando uma **{item_data['nome']}**. Preço da operação: {item_data['preco']} moedas. Selecione o alvo:",
                view=HeistTargetView(self.bot, item_data)
            )
            return

        await interaction.response.defer()
        
        update_query = {"$inc": {"coins": -item_data["preco"]}}
        
        if self.item_type == "acoes":
            if selected_item_id == "ticket_spy":
                update_query["$inc"]["purchased_items.acoes.ticket_spy"] = 1
            elif selected_item_id == "unlock_privacy":
                update_query["$set"] = {"purchased_items.acoes.unlock_privacy": True}
        elif self.item_type == "titles":
            update_query["$push"] = {f"purchased_items.{self.item_type}": selected_item_id}

        await self.bot.inventories.update_one({"user_id": self.user_id}, update_query, upsert=True)
        await interaction.followup.send(f"✅ Parabéns! Você comprou '{item_data['nome']}'!", ephemeral=True)
        
        self.user_data["coins"] = current_user_data.get("coins", 0) - item_data["preco"]

        if selected_item_id == "unlock_privacy" or self.item_type == "titles":
            self.items = [item for item in self.items if item["id"] != selected_item_id]

        if not self.items:
            await interaction.delete_original_response()
        else:
            self.build_view()
            await interaction.message.edit(view=self)
            
    async def back_to_shop_callback(self, interaction: discord.Interaction):
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_coins = user_data.get("coins", 0)
        embed = discord.Embed(
            title="🛒 Loja da Bea",
            description="Bem-vindo(a)! Gaste suas moedas suadas em itens incríveis. Escolha uma categoria.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Seu Saldo Atual", value=f"{user_coins} moedas 🪙")
        await interaction.response.edit_message(embed=embed, view=ShopView(self.bot))

    async def close_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.delete_original_response()

class MuteTargetView(discord.ui.View):
    def __init__(self, bot: commands.Bot, item_data: dict, original_shop_message: discord.Message):
        super().__init__(timeout=180)
        self.bot = bot
        self.item_data = item_data
        self.original_shop_message = original_shop_message

        self.user_select = discord.ui.UserSelect(
            placeholder="Selecione o membro para aplicar o castigo..."
        )
        self.user_select.callback = self.user_select_callback
        self.add_item(self.user_select)

        # O botão de voltar foi removido por simplicidade, já que esta é uma ação final.
        # Se quiser, pode adicioná-lo de volta.

    async def user_select_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_member = self.user_select.values[0]
        user_id = str(interaction.user.id)
        
        # --- VERIFICAÇÕES DE SEGURANÇA QUE PERMANECEM ---
        if target_member.id == interaction.user.id:
            await interaction.followup.send("Você não pode castigar a si mesmo!", ephemeral=True)
            return

        if target_member.id == self.bot.user.id:
            await interaction.followup.send("Não tente me castigar, eu sou a Bea! 😠", ephemeral=True)
            return

        # VERIFICAÇÃO DE PERMISSÃO DO USUÁRIO FOI REMOVIDA DAQUI.

        # Verifica se o BOT tem permissão
        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.followup.send("Eu não tenho a permissão de 'Moderar Membros' para castigar usuários.", ephemeral=True)
            return

        # Verifica a hierarquia de cargos
        if target_member.top_role >= interaction.guild.me.top_role:
            await interaction.followup.send(f"Não posso castigar {target_member.display_name}. O cargo dele(a) é mais alto que o meu.", ephemeral=True)
            return

        # Verifica se o comprador tem moedas
        user_data = await self.bot.inventories.find_one({"user_id": user_id})
        if user_data.get("coins", 0) < self.item_data['preco']:
            await interaction.followup.send("Opa! Parece que você não tem mais moedas suficientes para esta operação.", ephemeral=True)
            return
            
        # --- EXECUÇÃO DA AÇÃO ---
        try:
            timeout_duration = datetime.timedelta(minutes=5)
            await target_member.timeout(timeout_duration, reason=f"Castigado via Loja por {interaction.user.name}")
            
            # Debita as moedas do comprador
            await self.bot.inventories.update_one(
                {"user_id": user_id}, {"$inc": {"coins": -self.item_data['preco']}}
            )
            
            # Envia o embed público
            mute_embed = discord.Embed(
                title="Mandou calar a boca! 🤫",
                description=f"A pedido de {interaction.user.mention}, o usuário {target_member.mention} foi colocado em um momento de paz por 5 minutos.",
                color=discord.Color.red()
            )
            mute_embed.set_image(url="https://media.discordapp.net/attachments/1388606897774530570/1388606964501708952/toma.gif?ex=68619883&is=68604703&hm=a2b183092394d9f815f87dec846a3a49ff400da06cb136cf2f97b9b4284d5106&=&width=467&height=351")
            await interaction.channel.send(embed=mute_embed)

            # Envia a confirmação privada
            # await interaction.followup.send(f"Ação executada com sucesso! {target_member.display_name} foi castigado(a).", ephemeral=True)


        except discord.Forbidden:
            await interaction.followup.send("Ocorreu um erro de permissão. Provavelmente o cargo do alvo é mais alto que o meu.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Ocorreu um erro inesperado: {e}", ephemeral=True)

# --- CLASSE PRINCIPAL DO COG ---
class ShopCog(commands.Cog):
    def __init__(self, bot: "TalkingBeaBot"):
        self.bot = bot

    @app_commands.command(name="loja", description="Abre a loja para comprar itens de personalização.")
    async def loja(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_data = await self.bot.inventories.find_one({"user_id": str(interaction.user.id)}) or {}
        user_coins = user_data.get("coins", 0)
        embed = discord.Embed(title="🛒 Loja da Bea", description="Gasta teu dinheiro ai mah, gasta ai la, namoral gasta ai pelo amor de deus", color=discord.Color.gold())
        embed.add_field(name="Seu Saldo Atual", value=f"{user_coins} moedas 🪙")
        await interaction.followup.send(embed=embed, view=ShopView(self.bot), ephemeral=True)

# --- FUNÇÃO SETUP PARA CARREGAR O COG ---
async def setup(bot: "TalkingBeaBot"):
    await bot.add_cog(ShopCog(bot))