import discord
from discord.ext import commands
from discord import app_commands
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import random
import io
import traceback
from PIL import Image

from config import FRIENDS_PERSONAS, BEA_PERSONA

OWNER_ID = 404844681852223498

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chat_sessions = {}
        self.full_training_data = self._load_training_data()
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def _load_training_data(self) -> list:
        print("[LOG] Carregando 'treinamento_bea.txt'...")
        history = []
        try:
            with open('treinamento_bea.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if not line.strip(): continue
                    if line.lower().startswith("kaio:"):
                        history.append({'role': 'user', 'parts': [line[len("kaio:"):].strip()]})
                    elif line.lower().startswith("bea:"):
                        history.append({'role': 'model', 'parts': [line[len("bea:"):].strip()]})
            print(f"[LOG] Arquivo de treinamento carregado com {len(history)} linhas.")
            return history
        except Exception as e:
            print(f"[ERRO] Falha ao carregar arquivo de treinamento: {e}")
            return []

    # A função de amostragem agora aceita um 'sample_size' para flexibilidade
    def get_context_sample(self, sample_size: int = 20) -> list:
        if not self.full_training_data: return []
        
        if len(self.full_training_data) <= sample_size: return self.full_training_data
        
        max_start_index = len(self.full_training_data) - sample_size
        if max_start_index <= 0: return self.full_training_data

        start_index = random.randint(0, max_start_index)
        # Garante que a amostra comece com uma mensagem de 'user' para manter a ordem do diálogo
        if self.full_training_data[start_index]['role'] != 'user':
            start_index = max(0, start_index - 1)
            
        return self.full_training_data[start_index : start_index + sample_size]

    @app_commands.command(name="conversar", description="Converse com a Bea (ela se lembra da conversa).")
    @app_commands.describe(pergunta="O que você quer me perguntar, man?")
    async def conversar(self, interaction: discord.Interaction, pergunta: str):
        active_ai = self.bot.current_ai
        if (active_ai == "gemini" and self.bot.gemini_model is None) or \
          (active_ai == "deepseek" and self.bot.deepseek_client is None) or \
          (active_ai == "groq" and self.bot.groq_client is None):
            return await interaction.response.send_message(f"Desculpa, man, meu cérebro ({active_ai.upper()}) não tá funcionando.", ephemeral=True)

        await interaction.response.defer()
        user_id_str = str(interaction.user.id)
        
        try:
            full_question = pergunta

            if active_ai == "gemini":
                # A lógica do Gemini já é robusta e pode ser mantida.
                print(f"[LOG] Usando Gemini para {interaction.user.display_name}")
                if user_id_str not in self.chat_sessions:
                    print(f"[LOG] Criando nova sessão Gemini para {user_id_str}")
                    user_context = FRIENDS_PERSONAS.get(user_id_str, "")
                    initial_user_prompt = f"{BEA_PERSONA}\n\n{user_context}"
                    
                    conversa_inicial = [
                        {'role': 'user', 'parts': [initial_user_prompt]},
                        {'role': 'model', 'parts': ["entendido btl. pode mandar."]}
                    ]
                    # O Gemini se beneficia de um histórico de exemplos maior
                    self.chat_sessions[user_id_str] = conversa_inicial + self.get_context_sample(sample_size=1000)
                
                chat_session = self.bot.gemini_model.start_chat(history=self.chat_sessions[user_id_str])
                response = await chat_session.send_message_async(full_question, safety_settings=self.safety_settings)
                raw_text = response.text
                
                self.chat_sessions[user_id_str].append({'role': 'user', 'parts': [full_question]})
                self.chat_sessions[user_id_str].append({'role': 'model', 'parts': [raw_text]})

            elif active_ai in ["deepseek", "groq"]:
                # <--- ARQUITETURA DE SUPER-CONTEXTO PARA GROQ/DEEPSEEK --- >
                print(f"[LOG] Usando {active_ai.upper()} para {interaction.user.display_name}")

                # 1. Monta a string de exemplos de forma explícita
                example_history = self.get_context_sample(sample_size=50) # Amostra pequena e direta
                example_str = "A seguir, exemplos de como você deve conversar:\n---\n"
                for msg in example_history:
                    # Assume que o user dos exemplos é o Kaio para consistência
                    speaker = "Kaio" if msg['role'] == 'user' else "Bea"
                    example_str += f"{speaker}: {msg['parts'][0]}\n"
                example_str += "---"

                # 2. Constrói o "Prompt de Super-Contexto"
                user_context = FRIENDS_PERSONAS.get(user_id_str)
                system_prompt = f"{BEA_PERSONA}\n\n"
                if user_context:
                    system_prompt += (f"INSTRUÇÃO CRÍTICA: Você está falando com {interaction.user.display_name}. "
                                      f"Use este contexto sobre ele: {user_context}\n\n")
                
                system_prompt += f"{example_str}\n\nAgora, responda ao usuário de forma natural, seguindo a persona e os exemplos."

                # 3. Gerencia o histórico da sessão (agora começa vazio)
                if user_id_str not in self.chat_sessions:
                    print(f"[LOG] Criando nova sessão {active_ai.upper()} para {user_id_str}")
                    self.chat_sessions[user_id_str] = []

                # Adiciona a pergunta atual ao histórico da sessão
                self.chat_sessions[user_id_str].append({'role': 'user', 'parts': [full_question]})

                # Formata o histórico da sessão ATUAL para a API
                session_history_for_api = []
                for msg in self.chat_sessions[user_id_str]:
                    session_history_for_api.append({'role': 'user' if msg['role'] == 'user' else 'assistant', 'content': msg['parts'][0]})

                # 4. Monta a carga final, com o super-contexto no system prompt
                messages_for_api = [
                    {"role": "system", "content": system_prompt}
                ] + session_history_for_api
                
                # 5. Chama a API
                if active_ai == "deepseek":
                    response = self.bot.deepseek_client.chat.completions.create(model="deepseek-chat", messages=messages_for_api)
                elif active_ai == "groq":
                    response = self.bot.groq_client.chat.completions.create(model="llama3-8b-8192", messages=messages_for_api)
                
                raw_text = response.choices[0].message.content
                
                # Adiciona a resposta da IA ao histórico da sessão para manter a memória
                self.chat_sessions[user_id_str].append({'role': 'model', 'parts': [raw_text]})
            
            # Processamento final
            processed_text = raw_text.strip().replace("Bea:", "").lower()
            print(f"[LOG] Resposta da IA ({active_ai.upper()}): '{processed_text}'")
            await interaction.followup.send(f"> {pergunta}\n\n{processed_text}")

        except Exception as e:
            print(f"[ERRO] Falha ao gerar resposta da IA: {e}")
            traceback.print_exc()
            await interaction.followup.send("diabeisso, deu um erro aqui na minha cabeça. tenta de novo aí.")

    # O resto do código permanece o mesmo
    @app_commands.command(name="set_ia", description="[DONO] Troca o modelo de IA que a Bea está usando.")
    @app_commands.choices(modelo=[
        app_commands.Choice(name="Gemini (Google)", value="gemini"),
        app_commands.Choice(name="DeepSeek (Alternativo)", value="deepseek"),
        app_commands.Choice(name="Groq (Rápido)", value="groq"),
    ])
    async def set_ia(self, interaction: discord.Interaction, modelo: app_commands.Choice[str]):
        if interaction.user.id != OWNER_ID:
            return await interaction.response.send_message("só meu chefe pode mexer no meu cérebro, mah.", ephemeral=True)
        
        self.bot.current_ai = modelo.value
        self.chat_sessions.clear()
        await interaction.response.send_message(f"beleza, man. troquei meu cérebro pro **{modelo.name}**. todas as conversas foram reiniciadas.", ephemeral=True)

    @app_commands.command(name="limpar_conversa", description="Limpa o histórico da sua conversa atual com a Bea.")
    async def limpar_conversa(self, interaction: discord.Interaction):
        user_id_str = str(interaction.user.id)
        if user_id_str in self.chat_sessions:
            del self.chat_sessions[user_id_str]
            await interaction.response.send_message("pronto, man. esqueci de tudo que a gente conversou.", ephemeral=True)
        else:
            await interaction.response.send_message("ué, a gente nem tava conversando.", ephemeral=True)

    @app_commands.command(name="ver", description="Mande uma imagem para a Bea e faça uma pergunta sobre ela (só funciona com Gemini).")
    async def ver(self, interaction: discord.Interaction, imagem: discord.Attachment, pergunta: str):
        if self.bot.current_ai != "gemini":
            return await interaction.response.send_message("essa parada de ver imagem só funciona quando eu to usando meu cérebro do google, man.", ephemeral=True)
        if not self.bot.gemini_model:
            return await interaction.response.send_message("minha cabeça não tá funcionando agora.", ephemeral=True)
        
        await interaction.response.defer()
        try:
            image_bytes = await imagem.read()
            img = Image.open(io.BytesIO(image_bytes))
            prompt_com_persona = [f"Responda como a Bea, seguindo esta persona: {BEA_PERSONA}\n\nPergunta: {pergunta}", img]
            response = await self.bot.gemini_model.generate_content_async(prompt_com_persona, safety_settings=self.safety_settings)
            cleaned_response = response.text.strip().replace("Bea:", "").lower()
            embed = discord.Embed(title="Bea Analisando a Cena...", description=f"**Sua pergunta:** *{pergunta}*\n\n**Minha resposta:**\n{cleaned_response}", color=discord.Color.orange())
            embed.set_image(url=imagem.url)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[ERRO] Falha ao analisar a imagem: {e}")
            await interaction.followup.send("egua, não consegui ver essa imagem direito.")

async def setup(bot):
    await bot.add_cog(AICog(bot))