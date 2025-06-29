# config.py

import discord

CARACTERE_INVISIVEL = '⠀'

FRASES_DA_BEA = [
    "ei man", "que foda", "nem fudendo", "ow mannnn", "que cara foda",
    "KKKKKKKKJJKJJK ", "ei man diabe isso ai", "esse cara ai é foda", "diabe isso btl",
]
IMAGENS_DE_PAO = [
    "https://i.imgur.com/RZZPRku.png"
]

JAILSON_VIDEOS = [
    "https://cdn.discordapp.com/attachments/1386955680350601238/1387567210054029357/dizem_que_gato_preto_da_azar_azar_de_quem_nao_tem_um_preto_desse_MIAU.mp4?ex=685dd02a&is=685c7eaa&hm=1060a7b0f09c1107bbf35c43ad7790e654677879a2d93eb2b48ef7b099cee3a9&",
    "https://cdn.discordapp.com/attachments/1386955680350601238/1387567359463653416/3422559852314127690_1.mp4?ex=685dd04e&is=685c7ece&hm=a4798b6f6284a77ca22d1dd33d0c3cb497d13bd240a74075224956b8100b70f9&",
    "https://media.discordapp.net/attachments/1386955680350601238/1387567399951138826/Sem_Titulo-1-Recuperado.png?ex=685dd057&is=685c7ed7&hm=d79218c34fad3c82500770d7ff5c37bb7000e04e3f9f7c33930bdbab0c4d8634&=&format=webp&quality=lossless&width=277&height=383",
    "https://media.discordapp.net/attachments/1386955680350601238/1387567445358805093/DSC02241.jpg?ex=685dd062&is=685c7ee2&hm=b93ec9938be3f7fe71373ab5bf5b04c1c47d6421eb199ef179117f022ef29c4e&=&format=webp&width=978&height=652",
    "https://cdn.discordapp.com/attachments/1386955680350601238/1387567659742269572/jalailson.mp4?ex=685dd095&is=685c7f15&hm=9627bc2da48b91b7a6d1da6922fae2ef68489138a73b950b88f99287b9deb4c5&",
]

RARIDADES = {
    "COMUM":       {"cor": discord.Color.light_grey(), "peso": 70, "estrelas": "★☆☆☆☆ COMUM",       "valor": 10},
    "RARO":        {"cor": discord.Color.blue(),       "peso": 20, "estrelas": "★★★☆☆ RARO",        "valor": 50},
    "LENDARIO":    {"cor": discord.Color.gold(),       "peso": 5,  "estrelas": "✨ ★★★★★ ✨ LENDÁRIO", "valor": 250},
    "HOLO":        {"cor": discord.Color.purple(),     "peso": 4,  "estrelas": "✨ ★★★★★ ✨ HOLO",     "valor": 500},
    "AMALDIÇOADO": {"cor": discord.Color.dark_red(),   "peso": 1,  "estrelas": "💀 AMALDIÇOADO 💀",  "valor": 1000},
}

HEIST_CHANCES = {
    # Raridade: Chance de Sucesso (de 0.0 a 1.0)
    "COMUM":       0.75,  # 75% de chance de sucesso
    "RARO":        0.50,  # 50%
    "LENDARIO":    0.20,  # 20%
    "HOLO":        0.10,  # 10%
    "AMALDIÇOADO": 0.01   # 90% (é fácil roubar algo que ninguém quer)
}

LISTA_DE_CARTAS = [
    {"titulo": "Pão Queimado", "raridade": "COMUM", "descricao": "Tava bom, era só tirar o queimado.", "foto": "https://i.imgur.com/RZZPRku.png"},
    {"titulo": "Pão Queimado Divino", "raridade": "LENDARIO", "descricao": "A artista e a obra.", "foto": "https://i.imgur.com/0cbGVOQ.png"},
    {"titulo": "Mousse de Maracujá com Chocolate", "raridade": "HOLO", "descricao": "Tava realmente bom!", "foto": "https://i.imgur.com/fQFDqTr.png"},
    {"titulo": "Cheesecake de Limão", "raridade": "AMALDIÇOADO", "descricao": "Argamassa. 3 colheradas = morte.", "foto": "https://i.imgur.com/jp3f4Zh.png"},
    {"titulo": "Pastel Queimado", "raridade": "COMUM", "descricao": "Eu que fiz.", "foto": "https://i.imgur.com/MYknJdo.png"},
    {"titulo": "Torta Crua", "raridade": "RARO", "descricao": "O recheio prestava.", "foto": "https://i.imgur.com/Uvl8tSi.png"},
    {"titulo": "COZINHEIRA", "raridade": "HOLO", "descricao": "cuidado", "foto": "https://i.imgur.com/WPiULwq.png"},
    {"titulo": "Frango Empedrado", "raridade": "COMUM", "descricao": "...", "foto": "https://i.imgur.com/9M3CV6R.png"},
]

CATALOGO_LOJA = {
    "backgrounds": {
        "fundo_1.png": {
            "nome": "Luisao House", 
            "preco": 200, 
            "imagem_url": "https://media.discordapp.net/attachments/1388497294676066396/1388497329535058073/fundo_1.png?ex=68613268&is=685fe0e8&hm=21f8ed8def0178eb49d4b105351f487fe5b1ae3d066bdff2b7e9836fe8f08b60&=&format=webp&quality=lossless&width=600&height=300"
        },
        "fundo_2.png": {
            "nome": "Pirocon", 
            "preco": 750, 
            "imagem_url": "https://media.discordapp.net/attachments/1388497294676066396/1388497329861955776/fundo_2.png?ex=68613268&is=685fe0e8&hm=888a78b79b74cb5743809672cb4c536ac236b4e62ab809287b254715ce037cc1&=&format=webp&quality=lossless&width=600&height=300"
        },
        "fundo_3.png": {
            "nome": "Manicomio", 
            "preco": 750, 
            "imagem_url": "https://cdn.discordapp.com/attachments/1388497294676066396/1388497330201952297/fundo_3.png?ex=68613268&is=685fe0e8&hm=59495a0efd9ec7a754e869cc30835893a8fc1784f1783379cc45ca06cd43820e&"
        },
    },
    "bea_skins": {
        "bea_1.png": {
            "nome": "Bea 1", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474889958326333/bea_1.png?ex=68611d82&is=685fcc02&hm=52a3e3b67fea77a7b4b427ed12dfe543fe6d64d8a9f928a8afd4e184e3a7fe85&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_2.png": {
            "nome": "Bea 2", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474890314579978/bea_2.png?ex=68611d82&is=685fcc02&hm=f285e996a43551e7bd9b54d8421cb7617300f70037eda797e331af0da9ffb499&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_argentina.png": {
            "nome": "Bea Argentina", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474890696396820/bea_argentina.png?ex=68611d82&is=685fcc02&hm=2ae40648f55c3a74ef6b3f1680fcd0d324de01618d292d465bbd354a52afc14f&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_dcdn.png": {
            "nome": "Bea DCDN", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474890998251520/bea_dcdn.png?ex=68611d82&is=685fcc02&hm=eb0cccfc0ba5d8fdf546531f48fb868b8ad102d8d6640d9c93b82a1d3974c22e&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_desgraca.png": {
            "nome": "Bea Desgraça", 
            "preco": 300, 
            "imagem_url": "https://cdn.discordapp.com/attachments/1388474841551605790/1388474891279401020/bea_desgraca.png?ex=68611d82&is=685fcc02&hm=3b28a3d54da8a4558f2e04e44bd4327e7196a43014a90d94cd99b4b932c68d9a&"
        },
        "bea_leao.png": {
            "nome": "Bea Lion", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474891778392156/bea_leao.png?ex=68611d82&is=685fcc02&hm=db5ca7fc650e235014477720fb047577c0e0f7cddd2e77b04566e4f31d9abc56&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_patty.png": {
            "nome": "Bea e Patty", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474892122591363/bea_patty.png?ex=68611d82&is=685fcc02&hm=89232de047828e3bd6309a6b275a692ea64533ddcbcad146ede603d3b0bb8a35&=&format=webp&quality=lossless&width=300&height=300"
        },
        "bea_rango.png": {
            "nome": "Bea Rango", 
            "preco": 300, 
            "imagem_url": "https://media.discordapp.net/attachments/1388474841551605790/1388474892378312786/bea_rango.png?ex=68611d82&is=685fcc02&hm=c9abd9cd1980de6e5fae6a819f7bd986387f0e69cf237987382859c44c483e02&=&format=webp&quality=lossless&width=300&height=300"
        },
    },
    "titles": {
        # Para títulos, a chave e o nome podem ser os mesmos
        "Mestre do Pão Queimado": {"nome": "Mestre do Pão Queimado", "preco": 100},
        "Degustador de Argamassa": {"nome": "Degustador de Argamassa", "preco": 100},
        "Chef 5 Estrelas":         {"nome": "Chef 5 Estrelas", "preco": 1000},
        "A Lenda da Cozinha":      {"nome": "A Lenda da Cozinha", "preco": 2500},
    },
    "acoes": {
        "tentativa_roubo": {
            "nome": "Tentativa de Roubo", 
            "preco": 2000, 
            "descricao": "Tente roubar uma receita de outro jogador. Cuidado, você pode falhar!"
        },
        "ticket_mute": {
            "nome": "Ordem de Silêncio",
            "preco": 1500,
            "descricao": "Compre o direito de aplicar um castigo em um usuário na hora."
        },
        "ticket_spy": {
            "nome": "Ticket de Espionagem (1 uso)",
            "preco": 500,
            "descricao": "Permite usar /ver_inventario em um jogador."
        },
        "unlock_privacy": {
            "nome": "Licença de Privacidade (Permanente)",
            "preco": 5000,
            "descricao": "Libera o comando /privacidade para seu inventário."
        }
    }
}