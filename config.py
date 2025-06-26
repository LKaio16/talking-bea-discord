# config.py

import discord

CARACTERE_INVISIVEL = '⠀'

FRASES_DA_BEA = [
    "ei man", "que foda", "nem fudendo", "ow mannnn", "que cara foda",
    "KKKKKKKKJJKJJK ", "ei man diabe isso ai", "esse cara ai é foda",
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
    "COMUM":       {"cor": discord.Color.light_grey(), "peso": 70, "estrelas": "★☆☆☆☆ COMUM"},
    "RARO":        {"cor": discord.Color.blue(),       "peso": 20, "estrelas": "★★★☆☆ RARO"},
    "LENDARIO":    {"cor": discord.Color.gold(),       "peso": 5,  "estrelas": "✨ ★★★★★ ✨ LENDÁRIO"},
    "HOLO":        {"cor": discord.Color.purple(),     "peso": 4,  "estrelas": "✨ ★★★★★ ✨ HOLO"},
    "AMALDIÇOADO": {"cor": discord.Color.dark_red(),   "peso": 1,  "estrelas": "💀 AMALDIÇOADO 💀"},
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