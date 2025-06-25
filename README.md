# 🤖 talking-bea-discord

> Um bot multifuncional para o Discord, com a personalidade única da Bea, criado para um servidor de amigos.

Este é um projeto de bot para Discord desenvolvido em Python com a biblioteca `discord.py`. O bot, carinhosamente chamado de "Bea", foi criado para ser o coração de um servidor, trazendo entretenimento, utilidades e muitas piadas internas.

## ✨ Funcionalidades

* **Sistema de Gacha de Comida:** Colecione "cartas" de receitas (algumas bem-sucedidas, outras nem tanto) através de um sistema de sorteio com raridades e probabilidades.
* **Inventário Pessoal:** Cada usuário possui seu próprio inventário para ver as receitas que já coletou e acompanhar o progresso para completar a coleção.
* **Interação por Voz:** A Bea pode entrar, sair e tocar áudios em canais de voz, tanto de forma aleatória quanto por comandos específicos no chat.
* **Comandos de Utilidade e Moderação:** Inclui comandos para facilitar a vida no servidor, como exibir informações de parceiros e moderar usuários.
* **Personalidade Reativa:** O bot reage a diversas palavras-chave e menções no chat, participando ativamente das conversas.

## 🚀 Comandos

Aqui está uma lista de todos os comandos que a Bea entende:

### 🎮 Jogo
* `/cozinhar`: Prepara uma receita aleatória para sua coleção. Se for uma receita nova, você recebe uma notificação especial!
* `/inventario`: Mostra todas as receitas que você já coletou, a quantidade de cada uma e seu progresso para completar a coleção.

### 🎙️ Voz e Áudio
* `/entrar`: Faz a Bea entrar no seu canal de voz atual.
* `/sair`: Faz a Bea sair do canal de voz (e para qualquer áudio que estiver tocando).
* `/fala_bea`: Inicia a tarefa que faz a Bea tocar áudios aleatórios da pasta `audio/` em intervalos de 2 a 10 segundos.
* `/calaboca_bea`: Para a tarefa de áudios aleatórios.

### 🔧 Utilidade e Moderação
* `/ajuda`: Mostra esta mensagem de ajuda com todos os comandos.
* `/dvinalle`: Exibe um cardápio informativo da D'vinalle Pizzaria, com status de funcionamento (aberta/fechada) em tempo real.
* `/bea`: Muda o seu apelido no servidor para "bea".
* `/paz`: Aplica um "castigo" (timeout) de 5 minutos em um usuário específico, impedindo-o de falar e digitar.

## 💬 Interações Automáticas

Além dos comandos com `/`, a Bea está sempre de olho no chat!

* **Reage com 🎂** em mensagens que contêm a palavra `bolo`.
* **Envia uma foto de pão** quando alguém fala `pão`.
* **Toca sons específicos** (da pasta `audio-chat/`) quando as palavras `pedreiro` ou `preconceito` são ditas (se ela estiver na call).
* **Responde com uma frase** quando mencionam o `Luizão` ou o ID dele.
* **Responde com uma de suas frases clássicas** quando a mencionam (`bea` ou `@talking bea`).
* Tem **20% de chance** de responder com uma frase aleatória para qualquer mensagem no chat, apenas para participar da conversa.

## 🛠️ Configuração e Instalação

Para rodar sua própria instância deste bot, siga os passos:

1.  **Pré-requisitos:**
    * [Python 3.10+](https://www.python.org/downloads/)
    * [Git](https://git-scm.com/downloads/)
    * **FFmpeg:** Essencial para funcionalidades de áudio. Siga um guia para instalá-lo e adicioná-lo ao PATH do seu sistema.

2.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/LKaio16/talking-bea-discord.git](https://github.com/LKaio16/talking-bea-discord.git)
    cd talking-bea-discord
    ```

3.  **Crie um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No Linux/macOS
    source venv/bin/activate
    ```

4.  **Instale as Dependências:**
    Crie um arquivo `requirements.txt` com o seguinte conteúdo:
    ```
    discord.py
    python-dotenv
    pytz
    pynacl
    ```
    E então instale com o pip:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure o Token:**
    * Crie um arquivo chamado `.env` na pasta principal do projeto.
    * Dentro dele, adicione a linha: `DISCORD_TOKEN=SEU_TOKEN_AQUI`
    * Substitua `SEU_TOKEN_AQUI` pelo token do seu bot, que você pode pegar no [Portal de Desenvolvedores do Discord](https://discord.com/developers/applications).

6.  **Estrutura de Pastas de Áudio:**
    * Certifique-se de ter as pastas `audio/` e `audio-chat/` na raiz do projeto com seus respectivos arquivos `.mp3` dentro.

7.  **Rode o Bot:**
    ```bash
    python bot_bea.py
    ```

## 👤 Autor

* **LKaio16** - [GitHub](https://github.com/LKaio16)
