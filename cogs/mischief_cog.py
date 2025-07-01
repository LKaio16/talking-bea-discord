# cogs/mischief_cog.py

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# --- CONFIGURAÇÃO ---
# ID do dono do bot, o único que poderá usar este comando
OWNER_ID = 404844681852223498
# IDs dos dois canais de voz para onde o usuário será movido
CHANNEL_ID_1 = 1080978059559190568
CHANNEL_ID_2 = 880881664983715865
# Duração do "liquidificador" em segundos
DURATION = 120 # 2 minutos

class MischiefCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kkkkkkkk", description="[DONO] Prende um usuário no liquidificador de canais de voz.")
    @app_commands.describe(alvo="A vítima que será chacoalhada.")
    async def liquidificador(self, interaction: discord.Interaction, alvo: discord.Member):
        print(f"[LOG] Comando /liquidificador usado por {interaction.user} no alvo {alvo.name}")
        # 1. Checa se quem usou é o dono do bot
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("Apenas meu mestre pode usar uma ferramenta de tortura tão poderosa.", ephemeral=True)

        # 2. Checagens de segurança sobre o alvo
        if not alvo.voice or not alvo.voice.channel:
            return await interaction.response.send_message(f"O alvo ({alvo.display_name}) não está em um canal de voz.", ephemeral=True)
        if alvo.id == self.bot.user.id:
            return await interaction.response.send_message("Não posso fazer isso comigo mesma!", ephemeral=True)
       # if alvo.id == interaction.user.id:
        #    return await interaction.response.send_message("Não seja masoquista.", ephemeral=True)
            
        # 3. Checa se o bot tem permissão para mover o alvo
        if not interaction.guild.me.guild_permissions.move_members:
            return await interaction.response.send_message("Eu não tenho a permissão de 'Mover Membros' neste servidor!", ephemeral=True)
        if alvo.top_role >= interaction.guild.me.top_role:
             return await interaction.response.send_message(f"Não posso mover {alvo.display_name}, o cargo dele(a) é mais alto que o meu.", ephemeral=True)

        # 4. Pega os objetos dos canais
        channel1 = self.bot.get_channel(CHANNEL_ID_1)
        channel2 = self.bot.get_channel(CHANNEL_ID_2)
        if not channel1 or not channel2:
            return await interaction.response.send_message("Um ou ambos os canais configurados para o liquidificador não foram encontrados.", ephemeral=True)

        await interaction.response.send_message(f"Ligando o liquidificador para **{alvo.display_name}** por {DURATION} segundos... 😈", ephemeral=True)
        
        # --- O LOOP DO CAOS ---
        end_time = asyncio.get_event_loop().time() + DURATION
        current_channel = 1

        while asyncio.get_event_loop().time() < end_time:
            # Se o alvo desconectar no meio do processo, o loop para
            target_member = interaction.guild.get_member(alvo.id) # Pega o estado mais recente do membro
            if not target_member or not target_member.voice:
                print(f"[LOG] Alvo {alvo.name} desconectou, parando o liquidificador.")
                await interaction.followup.send(f"{alvo.display_name} escapou do liquidificador desconectando!", ephemeral=False)
                break
            
            try:
                if current_channel == 1:
                    print(f"[LOG] Movendo {alvo.name} para o canal 1")
                    await target_member.move_to(channel1, reason="Liquidificador da Bea")
                    current_channel = 2
                else:
                    print(f"[LOG] Movendo {alvo.name} para o canal 2")
                    await target_member.move_to(channel2, reason="Liquidificador da Bea")
                    current_channel = 1
            except discord.Forbidden:
                print("[ERRO] Perdi a permissão de mover no meio do loop.")
                await interaction.followup.send("Perdi a permissão para mover o usuário no meio da operação!", ephemeral=True)
                break
            except Exception as e:
                print(f"[ERRO] Erro inesperado no loop do liquidificador: {e}")
                break

            # Pausa entre os movimentos
            await asyncio.sleep(0.2) # Intervalo de 1 segundo entre cada movimento
        
        else: # Este 'else' só executa se o 'while' terminar sem um 'break'
            print(f"[LOG] Liquidificador para {alvo.name} terminou o tempo.")
            await interaction.followup.send(f"O tempo de {alvo.display_name} no liquidificador acabou. Sobreviveu.", ephemeral=False)


async def setup(bot):
    await bot.add_cog(MischiefCog(bot))