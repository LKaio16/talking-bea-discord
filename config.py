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