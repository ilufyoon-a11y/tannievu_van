import random
from telegram.ext import filters
import os
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# !!⠀⠀FLASK - PERMITE QUE RENDER HAGA FUNCIONAR EL BOT⠀ ───⠀ ⠀♥︎

app_web = Flask('')

@app_web.route('/')
def home():
    return "Van fue encendido"

# !!⠀⠀VARIABLES DE IMAGENES⠀ ───⠀ ⠀♥︎

PREFIX = filters.Regex(r'^[./]')

GIF_BIENVENIDA = "https://i.postimg.cc/T1jPgpDX/upscalemedia-transformed-(3).jpg" 
GIF_INFO       = "https://i.postimg.cc/9XgrQHCd/upscalemedia-transformed-(1).jpg" 
GIF_AHORCADO   = "https://i.postimg.cc/6qg3jBTv/1000004761.jpg"   # usado por cipher
GIF_SNOWBALL   = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg" 
GIF_RATONES    = "https://i.postimg.cc/wMmHBLTM/1000004766.jpg" 
GIF_RITMOAGO   = "https://i.postimg.cc/CMXk6g3n/upscalemedia-transformed.jpg" 
GIF_ERROR      = "https://i.postimg.cc/G38XXrMW/Airbrush-IMAGE-ENHANCER-1779170852039-1779170852039.jpg" 
GIF_OFFVAN     = "https://i.postimg.cc/mZ7k066k/upscalemedia-transformed-(2).jpg" 
GIF_JITB       = "https://i.postimg.cc/fLqYbX2s/Airbrush-IMAGE-ENHANCER-1779302294635-1779302294635.jpg" 
GIF_ZOMBIE     = "https://i.postimg.cc/8PWQJWM1/1000004869.jpg" 
GIF_ENCUBRIDOR = "https://i.postimg.cc/QMmj1qZm/8a87226444e22cdd01aaff0060557a2b-(1).jpg"
GIF_CERO       = "https://i.postimg.cc/vH5TDfDZ/763aa3f517ca4e8b1b1ae10f55dfb556-(1).jpg"
GIF_LETRISTA   = "https://i.postimg.cc/Zndk78XB/Airbrush-IMAGE-ENHANCER-1779303536547-1779303536547.jpg"
GIF_RECHAZADO  = "https://i.postimg.cc/MTXZnXd8/1000005045.jpg"
GIF_COMANDOS   = "https://i.postimg.cc/6qjQHnqv/1000005043-(1).jpg"
GIF_CHARADA    = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"   # ← reemplaza con tu imagen real
GIF_CASERIA    = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"   # ← reemplaza con tu imagen real
GIF_PIRATA     = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"   # ← reemplaza con tu imagen real

# !!⠀⠀DICCIONARIOS DE JUEGOS⠀ ───⠀ ⠀♥︎

# CHARADA 🎭

DICCIONARIOS_CHARADA = {
    "peliculas_animadas": ["Coraline y la Puerta Secreta", "Kung Fu Panda", "La era del hielo", "Ratatouille",
                           "Monsters, Inc.", "Toy Story", "Up", "Intensamente", "Buscando a Nemo", "Shrek",
                           "Mi villano favorito", "Hotel Transylvania", "Rio", "Coco", "El rey león", "Enredados", "Frozen"],
    "personajes": ["Mickey Mouse", "Bugs Bunny", "Bob Esponja", "Pato Donald", "Pikachu", "Pedro Picapiedra",
                   "Las Chicas Superpoderosas", "La Pantera Rosa", "Dora la Exploradora", "Peppa Pig",
                   "Hello Kitty", "El Grinch"],
    "kpop": ["dynamite", "butter", "boy with luv", "fake love", "dna",
             "mic drop", "idol", "run bts", "spring day", "permission to dance"]
}

# !!⠀⠀SESIONES DE CADA JUEGO⠀ ───⠀ ⠀♥︎

# CIPHER 👨‍💻

sesion_cipher = {
    "jugadores": [],
    "activa": False,
    "codigo": "",
    "numeros_adivinadas": [],
    "moderador_id": None,
    "ultimo_moderador_id": None,
}

esperando_code = {}   # user_id -> chat_id  (moderador esperando enviar código)

# ZOMBIE 🧟

sesion_zombie = {
    "jugadores": [],
    "activa": False,
    "zombies": [],
    "vivos": [],
    "fase": None,
    "votos": {},
    "mensaje_voto_id": None,
    "ultimo_zombie_id": None,
}

# BOX 📦

sesion_box = {}           # chat_id -> datos de la partida
esperando_elementos = {}  # user_id -> chat_id  (encubridor esperando enviar emojis)

# CHARADA 🎭

sesion_charada = {
    "activa": False,
    "fase_registro": False,
    "jugadores": [],
    "equipo_rojo": [],
    "equipo_azul": [],
    "bando_actual": None,
    "moderador_id": None,
    "nombre_recibido": False,
    "nombre_equipo_rojo": "Equipo Rojo 🔴",
    "nombre_equipo_azul": "Equipo Azul 🔵",
    "categoria_random": "",
    "palabras_ronda": {},
    "mensaje_grupo_id": None,
    "puntos_rojo": 0,
    "puntos_azul": 0,
}

# CASERÍA 🔎

sesion_caseria = {
    "activa": False,
    "fase_registro": False,
    "jugadores": {},
    "tablero": [],
    "mensaje_grupo_id": None,
}

# PIRATA 🏴‍☠️

sesion_pirata = {
    "jugadores": [],
    "activa": False,
    "sobrevivientes": [],
    "turno_actual": 0,
    "agujerofake": None,
    "agujerosave": [],
    "respondio_turno": False,
}

# !!⠀⠀AUXILIARES⠀ ───⠀ ⠀♥︎

def extraer_emojis(texto):
    import emoji
    return [c['emoji'] for c in emoji.emoji_list(texto)]

def nombre_usuario(user):
    return f"@{user.username}" if user.username else user.first_name

def dibujar_pantalla_code(codigo_secreto, intento_usuario):
    if not intento_usuario:
        return " ".join(["_" for _ in codigo_secreto])
        
    resultado = []
    for num_secreto, num_intento in zip(codigo_secreto, intento_usuario):
        if num_secreto == " ":
            resultado.append(" ")
        elif num_secreto == num_intento:
            resultado.append(num_secreto)
        else:
            resultado.append("_")
            
    return " ".join(resultado)
    
# !!⠀⠀COMANDOS GENERALES⠀ ───⠀ ⠀♥︎

async def start_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_BIENVENIDA,
        caption="\n\n🌸ㅤㅤ⪩⪩ㅤㅤ𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝@ㅤㅤ!!ㅤㅤ☆ \n\n𝖵𝖺𝗇 𝖾𝗌 𝗎𝗇 𝖻𝗈𝗍 𝗊𝗎𝖾 𝗈𝖿𝗋𝖾𝖼𝖾 𝗎𝗇𝖺 𝗏𝖺𝗋𝗂𝖾𝖽𝖺𝖽 𝖽𝖾 𝗃𝗎𝖾𝗀𝗈𝗌, 𝖺𝗎𝗇 𝖾𝗌𝗍𝖺 𝖾𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗈 𝖽𝖾 𝗉𝗋𝗎𝖾𝖻𝖺 𝖺𝗌𝗂 𝗊𝗎𝖾 𝗌𝗂𝖾𝗇𝗍𝖾𝗍𝖾 𝖾𝗇 𝗍𝗈𝗍𝖺𝗅 𝗅𝗂𝖻𝖾𝗋𝗍𝖺𝖽 𝖽𝖾 𝖼𝗈𝗆𝗎𝗇𝗂𝖼𝖺𝗋 𝖼𝗎𝖺𝗅𝗊𝗎𝗂𝖾𝗋 𝗊𝗎𝖾𝗃𝖺/𝗌𝗎𝗀𝖾𝗋𝖾𝗇𝖼𝗂𝖺 𝖾𝗇 𝖾𝗅 𝖼𝗁𝖺𝗍 𝖽𝖾𝗅 𝖼𝖺𝗇𝖺𝗅. \n\n𝖤𝗌𝗉𝖾𝗋𝖺𝗆𝗈𝗌 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗃𝗎𝖾𝗀𝗈𝗌 𝖼𝗈𝗇𝗍𝖾𝗇𝗂𝖽𝗈𝗌 𝗌𝖾𝖺𝗇 𝖽𝖾 𝗌𝗎 𝖺𝗀𝗋𝖺𝖽𝗈! 💕"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_INFO,
        caption=("🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦     ꒱꒱\n\n"
                 "𝒊. 𝐂𝐢𝐩𝐡𝐞𝐫\n\n"
                 "𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝖾𝗅 𝖼𝗈́𝖽𝗂𝗀𝗈 𝗌𝖾𝖼𝗋𝖾𝗍𝗈 𝗇𝗎́𝗆𝖾𝗋𝗈 𝖺 𝗇𝗎́𝗆𝖾𝗋𝗈.\n\n"
                 "𝒊𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞\n\n"
                 "𝖴𝗇𝖺 𝖾𝗑𝖼𝗎𝗋𝗌𝗂𝗈́𝗇 𝗌𝖾 𝗏𝗂𝗈 𝗂𝗇𝗍𝖾𝗋𝗋𝗎𝗆𝗉𝗂𝖽𝖺 𝗉𝗈𝗋 𝗎𝗇 𝗏𝗂𝗋𝗎𝗌 𝗓𝗈𝗆𝖻𝗂𝖾. ¿𝖯𝗈𝖽𝗋𝖺́𝗇 𝗌𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝗋?\n\n"
                 "𝒊𝒊𝒊. 𝐂𝐚𝐬𝐞𝐫í𝐚\n\n"
                 "𝖤𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝗅𝗈𝗌 𝖾𝗆𝗈𝗃𝗂𝗌 𝗈𝖼𝗎𝗅𝗍𝗈𝗌 𝖾𝗇 𝖾𝗅 𝗍𝖺𝖻𝗅𝖾𝗋𝗈.\n\n"
                 "𝒊𝒗. 𝐁𝐨𝐱\n\n"
                 "𝖬𝖾𝗆𝗈𝗋𝗂𝗓𝖺 𝗅𝗈𝗌 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝖽𝖾𝗌𝖺𝗉𝖺𝗋𝖾𝗓𝖼𝖺𝗇.\n\n"
                 "𝒗. 𝐂𝐡𝐚𝐫𝐚𝐝𝐚\n\n"
                 "𝖣𝗈𝗌 𝖾𝗊𝗎𝗂𝗉𝗈𝗌 𝗌𝖾 𝖾𝗇𝖿𝗋𝖾𝗇𝗍𝖺𝗇 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗇𝖽𝗈 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝖼𝗈𝗇 𝗆𝗂́𝗆𝗂𝖼𝖺𝗌 𝗒 𝖾𝗆𝗈𝗃𝗂𝗌.\n\n"
                 "𝒗𝒊. 𝐏𝐢𝐫𝐚𝐭𝐚\n\n"
                 "𝖢𝗅𝖺𝗏𝖺 𝗅𝖺 𝖾𝗌𝗉𝖺𝖽𝖺 𝖾𝗇 𝗅𝖺 𝗋𝖺𝗇𝗎𝗋𝖺 𝖼𝗈𝗋𝗋𝖾𝖼𝗍𝖺, ¡𝗉𝖾𝗋𝗈 𝖼𝗎𝗂𝖽𝖺𝖽𝗈 𝖼𝗈𝗇 𝗅𝖺 𝗍𝗋𝖺𝗆𝗉𝖺!")
    )

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_COMANDOS,
        caption=("🎡  𖹭𖹭 ㅤ𝗖𝗼𝗺𝗮𝗻𝗱𝗼𝘀 𝗱𝗶𝘀𝗽𝗼𝗻𝗶𝗯𝗹𝗲𝘀  ꒱꒱\n\n"
                 "𝒊. 𝐂𝐢𝐩𝐡𝐞𝐫  →  /cipher  /start_cipher\n\n"
                 "𝒊𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞  →  /zombie  /start_zombie\n\n"
                 "𝒊𝒊𝒊. 𝐂𝐚𝐬𝐞𝐫í𝐚  →  /caseria  /start_caseria\n\n"
                 "𝒊𝒗. 𝐁𝐨𝐱  →  /box  /start_box\n\n"
                 "𝒗. 𝐂𝐡𝐚𝐫𝐚𝐝𝐚  →  /charada  /start_charada\n\n"
                 "𝒗𝒊. 𝐏𝐢𝐫𝐚𝐭𝐚  →  /pirata  /start_pirata\n\n"
                 "𝖠𝗇𝗍𝖾𝗌 𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝗇𝗎𝖾𝗏𝖺, 𝗎𝗌𝖺 /off_van 𝗉𝖺𝗋𝖺 𝗋𝖾𝗌𝖾𝗍𝖾𝖺𝗋.")
    )

# =====================================================================
# CIPHER 👨‍💻
# =====================================================================

async def unirse_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_cipher["jugadores"] = []
    sesion_cipher["activa"] = False
    sesion_cipher["codigo"] = ""
    sesion_cipher["numeros_adivinadas"] = []
    sesion_cipher["moderador_id"] = None

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_cipher_click")
    await update.message.reply_photo(
        photo=GIF_AHORCADO,
        caption=" ៹ ࣪  📝 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 Cipher! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪  𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(sesion_cipher["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    candidatos = list(sesion_cipher["jugadores"])
    ultimo_mod = sesion_cipher.get("ultimo_moderador_id")
    if ultimo_mod and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_mod]
        moderador = random.choice(filtrados if filtrados else candidatos)
    else:
        moderador = random.choice(candidatos)

    sesion_cipher["jugadores"].remove(moderador)
    sesion_cipher.update({
        "moderador_id": moderador["id"],
        "ultimo_moderador_id": moderador["id"],
        "activa": True,
    })

    esperando_code[moderador["id"]] = chat_id
    await update.message.reply_text("˒˓  ¡𝖬𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈! 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗊𝗎𝖾 𝖾𝗇𝗏𝗂𝖾 𝖾𝗅 𝖼𝗈́𝖽𝗂𝗀𝗈  ᨦᨩ")

    try:
        await context.bot.send_photo(
            chat_id=moderador["id"],
            photo=GIF_LETRISTA,
            caption="¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂́𝖺 𝖾𝗅 𝖼𝗈́𝖽𝗂𝗀𝗈 𝗊𝗎𝖾 𝖽𝖾𝗌𝖾𝖾𝗌 𝗊𝗎𝖾 𝖺𝖽𝗂𝗏𝗂𝗇𝖾𝗇."
        )
    except Exception:
        await context.bot.send_photo(
            chat_id=chat_id, photo=GIF_RECHAZADO,
            caption=f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({moderador['name']}). 𝖠𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈."
        )
        sesion_cipher["activa"] = False

# =====================================================================
# ZOMBIE 🧟
# =====================================================================

async def unirse_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_zombie["jugadores"] = []
    sesion_zombie["zombies"] = []
    sesion_zombie["vivos"] = []
    sesion_zombie["votos"] = {}
    sesion_zombie["activa"] = False
    sesion_zombie["fase"] = None

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_zombie_click")
    await update.message.reply_photo(
        photo=GIF_ZOMBIE,
        caption="៹ ࣪  🧟 𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝗁𝖺 𝗅𝗅𝖾𝗀𝖺𝖽𝗈 𝗒 𝗅𝗈𝗌 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 𝖾𝗌𝗍𝖺́𝗇 𝗌𝖺𝗅𝗂𝖾𝗇𝖽𝗈. ¡𝖠𝗉𝗋𝖾𝗌𝗎́𝗋𝖺𝗍𝖾 𝖺 𝗌𝗎𝖻𝗂𝗋𝗍𝖾 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌!  ֪",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if sesion_zombie["activa"]:
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return

    if len(sesion_zombie["jugadores"]) < 3:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟥 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    sesion_zombie["activa"] = True
    sesion_zombie["fase"] = "infeccion"
    sesion_zombie["vivos"] = [j["id"] for j in sesion_zombie["jugadores"]]

    ultimo_zombie = sesion_zombie.get("ultimo_zombie_id")
    candidatos = [uid for uid in sesion_zombie["vivos"] if uid != ultimo_zombie]
    paciente_cero_id = random.choice(candidatos if candidatos else sesion_zombie["vivos"])
    sesion_zombie["ultimo_zombie_id"] = paciente_cero_id
    sesion_zombie["zombies"].append(paciente_cero_id)
    sesion_zombie["vivos"].remove(paciente_cero_id)

    paciente_cero_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == paciente_cero_id)

    await update.message.reply_text(
        "¡Un infectado se coló! Uno de ustedes fue mordido por un zombie 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗌𝗎𝖻𝗂𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌, el brote ha comenzado..."
    )

    botones_ataque = []
    for humano_id in sesion_zombie["vivos"]:
        humano_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == humano_id)
        botones_ataque.append([InlineKeyboardButton(f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {humano_obj['name']}", callback_data=f"morder:{humano_id}:{chat_id}")])

    try:
        await context.bot.send_photo(
            chat_id=paciente_cero_id,
            photo=GIF_CERO,
            caption="𝖥𝗎𝗂𝗌𝗍𝖾 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝖾𝗇𝗍𝗋𝖺𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌. ¿𝖰𝗎𝗂𝖾́𝗇 𝗌𝖾𝗋𝖺́ 𝗍𝗎 𝗉𝗋𝖾𝗌𝖺?",
            reply_markup=InlineKeyboardMarkup(botones_ataque)
        )
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({paciente_cero_obj['name']}). 𝖠𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈."
        )
        sesion_zombie["activa"] = False

async def abrir_votacion_zombie(chat_id, context):
    sesion_zombie["fase"] = "votacion"
    sesion_zombie["votos"] = {}

    botones_voto = [
        [InlineKeyboardButton(f"𝖤𝗑𝗉𝗎𝗅𝗌𝖺𝗋 𝖺 {j['name']}", callback_data=f"voto_z:{j['id']}")]
        for j in sesion_zombie["jugadores"]
    ]

    msg_voto = await context.bot.send_message(
        chat_id=chat_id,
        text="¡𝗥𝗘𝗨𝗡𝗜𝗢𝗡 𝗗𝗘 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗜𝗔ⵑ\n\n𝖠𝗅𝗀𝗎𝗂𝖾𝗇 𝖿𝗎𝖾 𝗆𝗈𝗋𝖽𝗂𝖽𝗈. Deben expulsar al infectado antes de que muerda a alguien más.\n\n𝖲𝗈𝗅𝗈 𝖼𝗎𝖾𝗇𝗍𝖺𝗇 𝖼𝗈𝗇 𝟥𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌.",
        reply_markup=InlineKeyboardMarkup(botones_voto)
    )
    sesion_zombie["mensaje_voto_id"] = msg_voto.message_id
    asyncio.create_task(timer_votacion_zombie(chat_id, context))

async def timer_votacion_zombie(chat_id, context):
    await asyncio.sleep(30)
    if sesion_zombie["activa"] and sesion_zombie["fase"] == "votacion":
        await procesar_resultados_votacion(chat_id, context)

async def procesar_resultados_votacion(chat_id, context):
    if sesion_zombie["fase"] != "votacion":
        return
    sesion_zombie["fase"] = None

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=sesion_zombie["mensaje_voto_id"])
    except:
        pass

    if not sesion_zombie["votos"]:
        await context.bot.send_message(chat_id=chat_id, text="𝖭𝖺𝖽𝗂𝖾 𝗏𝗈𝗍𝗈́, el infectado sigue aquí, el ataque continúa...")
        await pasar_a_siguiente_ataque(chat_id, context)
        return

    conteo = {}
    for vid in sesion_zombie["votos"].values():
        conteo[vid] = conteo.get(vid, 0) + 1

    mas_votado_id = max(conteo, key=conteo.get)
    max_votos = conteo[mas_votado_id]
    empates = [k for k, v in conteo.items() if v == max_votos]

    if len(empates) > 1:
        await context.bot.send_message(chat_id=chat_id, text="¡𝖧𝗎𝖻𝗈 𝗎𝗇 𝖾𝗆𝗉𝖺𝗍𝖾 𝗒 𝗇𝖺𝖽𝗂𝖾 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈!")
        await pasar_a_siguiente_ataque(chat_id, context)
        return

    eliminado_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == mas_votado_id)

    if mas_votado_id in sesion_zombie["zombies"]:
        sesion_zombie["zombies"].remove(mas_votado_id)
        sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != mas_votado_id]
        await context.bot.send_message(chat_id=chat_id,
            text=f"{eliminado_obj['name']} obtuvo {max_votos} votos y fue expulsado del autobús. ¡Se deshicieron del infectado!")
    else:
        sesion_zombie["vivos"].remove(mas_votado_id)
        sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != mas_votado_id]
        await context.bot.send_message(chat_id=chat_id,
            text=f"{eliminado_obj['name']} obtuvo {max_votos} votos y fue expulsado... Era un humano perfectamente sano. 😬")

    if not sesion_zombie["zombies"]:
        ganadores = [j["name"] for j in sesion_zombie["jugadores"] if j["id"] in sesion_zombie["vivos"]]
        await context.bot.send_message(chat_id=chat_id,
            text=f"¡𝖲𝖮𝖡𝖱𝖤𝖵𝖨𝖵𝖨𝖤𝖱𝖮𝖭! El infectado fue expulsado y {', '.join(ganadores)} pueden volver a casa. 🏠")
        sesion_zombie["activa"] = False
    elif len(sesion_zombie["vivos"]) <= 1:
        zombie_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == sesion_zombie["zombies"][0])
        await context.bot.send_message(chat_id=chat_id,
            text=f"¡𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦ⵑ {zombie_obj['name']} mordió a todos 🧟‍♂️")
        sesion_zombie["activa"] = False
    else:
        await pasar_a_siguiente_ataque(chat_id, context)

async def pasar_a_siguiente_ataque(chat_id, context):
    sesion_zombie["fase"] = "infeccion"
    for z_id in sesion_zombie["zombies"]:
        botones_ataque = [
            [InlineKeyboardButton(f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {next(j for j in sesion_zombie['jugadores'] if j['id'] == humano_id)['name']}",
                                  callback_data=f"morder:{humano_id}:{chat_id}")]
            for humano_id in sesion_zombie["vivos"]
        ]
        try:
            await context.bot.send_message(chat_id=z_id,
                text="𝖮𝗍𝗋𝖺 𝗏𝖾𝗓 𝗌𝗂𝖾𝗇𝗍𝖾𝗌 𝖺𝗇𝗌𝗂𝖾𝖽𝖺𝖽 𝗉𝗈𝗋 𝗉𝗋𝗈𝖻𝖺𝗋 𝖼𝖺𝗋𝗇𝖾. 𝖤𝗅𝗂𝗀𝖾 𝗍𝗎 𝗌𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾 𝗏𝗂́𝖼𝗍𝗂𝗆𝖺 𝖼𝗈𝗇 𝗉𝗋𝖾𝖼𝖺𝗎𝖼𝗂𝗈́𝗇.",
                reply_markup=InlineKeyboardMarkup(botones_ataque))
        except:
            pass
    await context.bot.send_message(chat_id=chat_id,
        text="𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝖼𝖺𝖾 𝗒 𝗌𝖾 𝖽𝖾𝖻𝖾𝗇 𝗉𝖺𝗀𝖺𝗋 𝗅𝖺𝗌 𝗅𝗎𝖼𝖾𝗌... 𝖤𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖾𝗌𝗍𝖺́ 𝖺𝗅 𝖺𝖼𝖾𝖼𝗁𝗈.")

# =====================================================================
# CASERÍA 🔎
# =====================================================================

async def unirse_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_caseria["jugadores"] = {}
    sesion_caseria["tablero"] = []
    sesion_caseria["activa"] = False
    sesion_caseria["fase_registro"] = True
    sesion_caseria["mensaje_grupo_id"] = None

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_caseria_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="៹ ࣪  🔎 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖢𝖺𝗌𝖾𝗋𝗂́𝖺! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(sesion_caseria["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    sesion_caseria["fase_registro"] = False
    sesion_caseria["activa"] = True

    # Generar tablero de emojis
    pool = []
    rangos = [(0x1F600, 0x1F64F), (0x1F330, 0x1F37F), (0x1F400, 0x1F4D0), (0x1F910, 0x1F96B)]
    seen = set()
    while len(pool) < 25:
        rango = random.choice(rangos)
        c = chr(random.randint(rango[0], rango[1]))
        if c.isprintable() and c not in seen:
            seen.add(c)
            pool.append(c)

    sesion_caseria["tablero"] = pool
    sesion_caseria["jugadores"] = {uid: 0 for uid in sesion_caseria["jugadores"]}

    filas = [pool[i:i+5] for i in range(0, 25, 5)]
    tablero_txt = "\n".join("  ".join(fila) for fila in filas)

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔎 **¡CASERÍA INICIADA!**\n\nEncuentra los emojis que el bot irá pidiendo. ¡El primero en responder gana el punto!\n\n{tablero_txt}"
    )
    sesion_caseria["mensaje_grupo_id"] = msg.message_id

    asyncio.create_task(ronda_caseria(chat_id, context))

async def ronda_caseria(chat_id, context):
    tablero = sesion_caseria["tablero"]
    objetivos = random.sample(tablero, min(5, len(tablero)))

    for objetivo in objetivos:
        if not sesion_caseria["activa"]:
            break
        sesion_caseria["objetivo_actual"] = objetivo
        sesion_caseria["respondio_turno"] = False

        await context.bot.send_message(chat_id=chat_id,
            text=f"🎯 ¡Encuentra este emoji en el tablero y mándalo! → {objetivo}")

        espera = 15.0
        while espera > 0 and not sesion_caseria.get("respondio_turno", False):
            await asyncio.sleep(0.5)
            espera -= 0.5

# =====================================================================
# BOX 📦
# =====================================================================

async def unirse_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesion_box:
        sesion_box[chat_id] = {"jugadores": [], "activa": False}
    else:
        sesion_box[chat_id]["activa"] = False
        sesion_box[chat_id]["jugadores"] = []
        sesion_box[chat_id].pop("ultimo_encubridor_id", None)

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_box_click")
    await update.message.reply_photo(
        photo=GIF_JITB,
        caption="៹ ࣪  📦 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝗊𝗎𝖾 𝗁𝖺𝗒 𝖾𝗇 𝗅𝖺 𝖼𝖺𝗃𝖺! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesion_box or len(sesion_box[chat_id]["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    candidatos = list(sesion_box[chat_id]["jugadores"])
    ultimo_enc = sesion_box[chat_id].get("ultimo_encubridor_id")
    if ultimo_enc and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_enc]
        encubridor = random.choice(filtrados if filtrados else candidatos)
    else:
        encubridor = random.choice(candidatos)

    sesion_box[chat_id].update({
        "encubridor_id": encubridor["id"],
        "ultimo_encubridor_id": encubridor["id"],
        "activa": True,
    })

    esperando_elementos[encubridor["id"]] = chat_id
    await update.message.reply_text("˒˓  ¡𝖤𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈! Esperando que asigne los objetos  ᨦᨩ")

    try:
        await context.bot.send_photo(
            chat_id=encubridor["id"],
            photo=GIF_ENCUBRIDOR,
            caption=("¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋!\n\n"
                     "𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂́𝖺 𝖾𝗑𝖺𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝟨 𝖾𝗆𝗈𝗃𝗂𝗌 𝗌𝗂𝗇 𝖾𝗌𝗉𝖺𝖼𝗂𝗈𝗌 (🌸🌟📰...) 𝗌𝖾𝗋𝖺́𝗇 𝗆𝗈𝗌𝗍𝗋𝖺𝖽𝗈𝗌 𝖻𝗋𝖾𝗏𝖾𝗆𝖾𝗇𝗍𝖾 𝖺 𝗅𝗈𝗌 𝗃𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌.")
        )
    except Exception:
        await update.message.reply_photo(photo=GIF_RECHAZADO,
            caption=f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 @{encubridor.get('username', 'usuario')}. 𝖠𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈.")

# =====================================================================
# CHARADA 🎭
# =====================================================================

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_charada.get("fase_registro") or sesion_charada.get("activa"):
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝗈 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝗈 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return

    sesion_charada["jugadores"] = []
    sesion_charada["equipo_rojo"] = []
    sesion_charada["equipo_azul"] = []
    sesion_charada["puntos_rojo"] = 0
    sesion_charada["puntos_azul"] = 0
    sesion_charada["fase_registro"] = True
    sesion_charada["activa"] = False

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_charada_click")
    await update.message.reply_photo(
        photo=GIF_CHARADA,
        caption="៹ ࣪ 🎭 ¡𝖦𝖱𝖠𝖭 𝖢𝖧𝖠𝖱𝖠𝖣𝖠 𝖯𝖮𝖱 𝖤𝖰𝖴𝖨𝖯𝖮𝖲! 🎭\n\n"
                "Preparen sus mejores mímicas y emojis. Se armarán dos bandos y jugaremos en contrarreloj.\n\n"
                "👉 ¡Únete! Cuando estén listos, pongan `.start_charada`.",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_charada.get("fase_registro"):
        await update.message.reply_text("⚠️ No hay ninguna convocatoria abierta. Usa `.charada` primero.")
        return

    if len(sesion_charada["jugadores"]) < 4:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟦 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗋𝗆𝖺𝗋 𝗅𝗈𝗌 𝖽𝗈𝗌 𝖾𝗊𝗎𝗂𝗉𝗈𝗌.")
        return

    sesion_charada["fase_registro"] = False

    lista_ids = [j["id"] for j in sesion_charada["jugadores"]]
    random.shuffle(lista_ids)
    mitad = len(lista_ids) // 2
    sesion_charada["equipo_rojo"] = lista_ids[:mitad]
    sesion_charada["equipo_azul"] = lista_ids[mitad:]

    nombres_rojo = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_rojo"]]
    nombres_azul = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_azul"]]

    sesion_charada["nombre_equipo_rojo"] = "Equipo Rojo 🔴"
    sesion_charada["nombre_equipo_azul"] = "Equipo Azul 🔵"

    bando_inicial = random.choice(["rojo", "azul"])
    sesion_charada["bando_actual"] = bando_inicial

    id_moderador = random.choice(sesion_charada["equipo_rojo"] if bando_inicial == "rojo" else sesion_charada["equipo_azul"])
    nombre_moderador = next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == id_moderador)

    categoria = random.choice(list(DICCIONARIOS_CHARADA.keys()))
    palabras_elegidas = random.sample(DICCIONARIOS_CHARADA[categoria], 10)
    sesion_charada["palabras_ronda"] = {palabra: False for palabra in palabras_elegidas}
    sesion_charada["categoria_random"] = categoria
    sesion_charada["moderador_id"] = id_moderador
    sesion_charada["nombre_recibido"] = False

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⚔️ **¡EQUIPOS FORMADOS!** ⚔️\n\n"
             f"🔴 **EQUIPO ROJO:** {', '.join(nombres_rojo)}\n"
             f"🔵 **EQUIPO AZUL:** {', '.join(nombres_azul)}\n\n"
             f"📣 **PRIMERA RONDA:** Juega el **EQUIPO {bando_inicial.upper()}**.\n"
             f"🎙️ **Moderador:** {nombre_moderador}\n\n"
             f"👀 ¡Atento al privado, tienes 15 segundos para nombrar a tu equipo!"
    )

    try:
        await context.bot.send_message(chat_id=id_moderador,
            text="👑 **¡ERES EL MODERADOR DE TU EQUIPO!** 👑\n\n"
                 "Escribe aquí el **NOMBRE PERSONALIZADO** para tu bando.\n\n"
                 "⏱️ ¡Tienes 15 segundos o el bot pondrá un nombre random!")
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"⚠️ ¡{nombre_moderador} debes iniciar el bot en privado! Se canceló la partida.")
        return

    espera = 15.0
    while espera > 0 and not sesion_charada["nombre_recibido"]:
        await asyncio.sleep(0.5)
        espera -= 0.5

    if not sesion_charada["nombre_recibido"]:
        nombre_random = random.choice(["Los Sin Nombre 🦆", "Los Pasados de Frío ❄️", "Los Lentos de Van 🦥", "Mimos Anónimos 🎭"])
        if bando_inicial == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{nombre_random} (Rojo)"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{nombre_random} (Azul)"

    lista_texto = "\n".join([f"🔹 {p.upper()}" for p in palabras_elegidas])
    await context.bot.send_message(chat_id=id_moderador,
        text=f"🤫 **¡AQUÍ ESTÁN TUS PALABRAS SECRETAS!** 🤫\n\n"
             f"🗂️ Categoría: **{categoria.upper()}**\n\n{lista_texto}\n\n"
             f"¡Corre al grupo a meter mímicas y emojis! No escribas las palabras directamente. 💀")

    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_inicial == "rojo" else sesion_charada["nombre_equipo_azul"]
    sesion_charada["activa"] = True

    sesion_charada["mensaje_grupo_id"] = await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎮 **¡EMPIEZA EL CONTRARRELOJ!** 🎮\n\n"
             f"🔥 **Bando jugando:** ✨ {nombre_bando_jugando.upper()} ✨\n"
             f"🎙️ **Moderador:** {nombre_moderador}\n"
             f"🗂️ **Categoría:** {categoria.upper()}\n\n"
             f"¡Tienen 60 segundos para adivinar las 10 palabras! 🔥"
    )

    asyncio.create_task(reloj_charada(chat_id, context))

async def reloj_charada(chat_id, context):
    segundos = 60
    while segundos > 0 and sesion_charada["activa"]:
        await asyncio.sleep(1)
        segundos -= 1

    if sesion_charada["activa"]:
        sesion_charada["activa"] = False

        adivinadas = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)
        bando = sesion_charada["bando_actual"]
        nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando == "rojo" else sesion_charada["nombre_equipo_azul"]

        if bando == "rojo":
            sesion_charada["puntos_rojo"] += adivinadas
        else:
            sesion_charada["puntos_azul"] += adivinadas

        faltantes = [p.upper() for p, v in sesion_charada["palabras_ronda"].items() if not v]
        texto_faltantes = ", ".join(faltantes) if faltantes else "¡Ninguna, las hicieron todas! 🔥"

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏱️ **¡TIEMPO AGOTADO!** ⏱️\n\n"
                 f"El equipo **{nombre_bando_jugando.upper()}** logró adivinar **{adivinadas}/10** palabras.\n"
                 f"❌ **Faltaron:** {texto_faltantes}\n\n"
                 f"📊 **PUNTAJE GLOBAL:**\n"
                 f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                 f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts\n\n"
                 f"¡El bot queda libre para otra ronda! 🎭"
        )

# =====================================================================
# PIRATA 🏴‍☠️
# =====================================================================

async def unirse_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_pirata["jugadores"] = []
    sesion_pirata["activa"] = False
    sesion_pirata["sobrevivientes"] = []
    sesion_pirata["turno_actual"] = 0
    sesion_pirata["agujerofake"] = None
    sesion_pirata["agujerosave"] = []
    sesion_pirata["respondio_turno"] = False

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_pirata_click")
    await update.message.reply_photo(
        photo=GIF_PIRATA,
        caption="🏴‍☠️ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖯𝗂𝗋𝖺𝗍𝖺! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(sesion_pirata["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    sesion_pirata["activa"] = True
    sesion_pirata["sobrevivientes"] = [j["id"] for j in sesion_pirata["jugadores"]]
    sesion_pirata["turno_actual"] = 0
    sesion_pirata["agujerosave"] = []
    sesion_pirata["agujerofake"] = random.randint(1, 6)

    await context.bot.send_message(chat_id=chat_id,
        text="🏴‍☠️ **¡LA RULETA DEL PIRATA COMIENZA!**\n\n"
             "Hay 6 ranuras. Una tiene trampa 💀 Las demás son seguras. ¡Clava tu espada con cuidado!\n\n"
             f"El turno es de **{next(j['name'] for j in sesion_pirata['jugadores'] if j['id'] == sesion_pirata['sobrevivientes'][0])}**")

    await enviar_turno_pirata(chat_id, context)

async def enviar_turno_pirata(chat_id, context):
    if sesion_pirata["turno_actual"] >= len(sesion_pirata["sobrevivientes"]):
        sesion_pirata["turno_actual"] = 0

    actual_id = sesion_pirata["sobrevivientes"][sesion_pirata["turno_actual"]]
    nombre_actual = next(j["name"] for j in sesion_pirata["jugadores"] if j["id"] == actual_id)

    ranuras_disponibles = [i for i in range(1, 7) if i not in sesion_pirata["agujerosave"]]
    botones = [
        [InlineKeyboardButton(
            f"{'✅' if i in sesion_pirata['agujerosave'] else '🗡️'} Ranura {i}",
            callback_data=f"ranura_ya_usada_{i}" if i in sesion_pirata["agujerosave"] else f"pirata_clic_{i}_{actual_id}"
        )]
        for i in range(1, 7)
    ]

    await context.bot.send_message(chat_id=chat_id,
        text=f"🗡️ Turno de **{nombre_actual}** — ¡elige una ranura!",
        reply_markup=InlineKeyboardMarkup(botones))

# =====================================================================
# MANEJO DE BOTONES (CallbackQuery)
# =====================================================================

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    # ── CIPHER ──────────────────────────────────────────────────────
    if query.data == "unirme_cipher_click":
        await query.answer()
        if sesion_cipher["activa"]:
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_cipher["jugadores"]):
            sesion_cipher["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"📝 ֹ  {nombre_usuario(user)} se unió al cipher 𓂃")

    # ── ZOMBIE ───────────────────────────────────────────────────────
    elif query.data == "unirme_zombie_click":
        await query.answer()
        if sesion_zombie.get("activa", False):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_zombie["jugadores"]):
            sesion_zombie["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🚌 ֹ  {nombre_usuario(user)} se unió 𓂃")

    elif query.data.startswith("morder:"):
        await query.answer()
        partes = query.data.split(":")
        victima_id = int(partes[1])
        grupo_chat_id = int(partes[2])

        if sesion_zombie.get("activa") and sesion_zombie.get("fase") == "infeccion":
            if user.id in sesion_zombie.get("zombies", []):
                if victima_id in sesion_zombie["vivos"]:
                    victima_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == victima_id)
                    sesion_zombie["vivos"].remove(victima_id)
                    sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != victima_id]

                    try:
                        await query.edit_message_caption(caption=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")

                    await context.bot.send_message(chat_id=grupo_chat_id,
                        text=f"🧟 ¡𝗨𝗡 𝗔𝗧𝗔𝗤𝗨𝗘 𝗛𝗔 𝗢𝗖𝗨𝗥𝗥𝗜𝗗𝗢ⵑ 🧟\n\n{victima_obj['name']} fue atacado en la oscuridad y está transformándose.")
                    await asyncio.sleep(2)

                    if len(sesion_zombie["vivos"]) <= 1:
                        zombie_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == sesion_zombie["zombies"][0])
                        await context.bot.send_message(chat_id=grupo_chat_id,
                            text=f"¡𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦ⵑ {zombie_obj['name']} mordió a todos y ganó la partida 🧟")
                        sesion_zombie["activa"] = False
                    else:
                        await abrir_votacion_zombie(grupo_chat_id, context)
                else:
                    try:
                        await query.edit_message_caption(caption="𝖤𝗌𝗍𝖺 𝗏𝗂́𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺́ 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾.")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text="𝖤𝗌𝗍𝖺 𝗏𝗂́𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺́ 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾.")

    elif query.data.startswith("voto_z:"):
        await query.answer()
        votado_id = int(query.data.split(":")[1])
        if sesion_zombie.get("activa") and sesion_zombie.get("fase") == "votacion":
            if any(j["id"] == user.id for j in sesion_zombie["jugadores"]):
                sesion_zombie["votos"][user.id] = votado_id
                await query.answer("𝖵𝗈𝗍𝗈 𝖾𝗆𝗂𝗍𝗂𝖽𝗈 ✓", show_alert=True)
                await context.bot.send_message(chat_id=chat_id,
                    text=f"{nombre_usuario(user)} acaba de emitir su voto.\n\n"
                         f"{len(sesion_zombie['votos'])}/{len(sesion_zombie['jugadores'])} votos emitidos")
                if len(sesion_zombie["votos"]) >= len(sesion_zombie["jugadores"]):
                    await procesar_resultados_votacion(chat_id, context)
            else:
                await query.answer("𝖴𝗉𝗌, 𝗍𝗎́ 𝗇𝗈 𝖾𝗌𝗍𝖺́𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝖽𝗈.", show_alert=True)

    # ── CASERÍA ──────────────────────────────────────────────────────
    elif query.data == "unirme_caseria_click":
        await query.answer()
        if sesion_caseria.get("activa"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        uid = user.id
        if uid not in sesion_caseria["jugadores"]:
            sesion_caseria["jugadores"][uid] = 0
            await query.message.reply_text(f"🔎 ֹ  {nombre_usuario(user)} se unió 𓂃")

    # ── BOX ──────────────────────────────────────────────────────────
    elif query.data == "unirme_box_click":
        await query.answer()
        if chat_id not in sesion_box:
            sesion_box[chat_id] = {"jugadores": [], "activa": False}
        if sesion_box[chat_id]["activa"]:
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_box[chat_id]["jugadores"]):
            sesion_box[chat_id]["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
            await query.message.reply_text(f"📦 ֹ  {nombre_usuario(user)} se unió 𓂃")

    # ── CHARADA ──────────────────────────────────────────────────────
    elif query.data == "unirme_charada_click":
        await query.answer()
        if sesion_charada.get("activa"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝖾𝗌𝗍𝖺́ 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖼𝗈𝗋𝗋𝗂𝖾𝗇𝖽𝗈!", show_alert=True)
            return
        if not sesion_charada.get("fase_registro"):
            await query.answer("¡El registro ya cerró!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_charada["jugadores"]):
            sesion_charada["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🎭 ֹ  {nombre_usuario(user)} se apuntó a las mímicas 𓂃")

    # ── PIRATA ───────────────────────────────────────────────────────
    elif query.data == "unirme_pirata_click":
        await query.answer()
        if sesion_pirata.get("activa"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_pirata["jugadores"]):
            sesion_pirata["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🏴‍☠️ ֹ  {nombre_usuario(user)} se unió al barco 𓂃")

    elif query.data.startswith("pirata_clic_"):
        await query.answer()
        if not sesion_pirata.get("activa"):
            return
        partes = query.data.split("_")
        num_ranura = int(partes[2])
        autor_id = int(partes[3])

        actual_id = sesion_pirata["sobrevivientes"][sesion_pirata["turno_actual"]]
        if user.id != actual_id or user.id != autor_id:
            return

        sesion_pirata["respondio_turno"] = True

        if num_ranura == sesion_pirata["agujerofake"]:
            sesion_pirata["activa"] = False
            ganadores = [next(j["name"] for j in sesion_pirata["jugadores"] if j["id"] == uid)
                         for uid in sesion_pirata["sobrevivientes"] if uid != autor_id]
            texto_ganadores = f"✨ {', '.join(ganadores)} ✨" if ganadores else "¡Nadie! El pirata se quedó solo en el mar. 🌊"
            await context.bot.send_message(chat_id=chat_id,
                text=f"💥 ¡¡ZAZZZ!! 🚀\n\n**{nombre_usuario(user)}** metió la espada en la ranura {num_ranura}... ¡Y EL PIRATA SALTÓ! 💀\n\n"
                     f"🏆 **¡GANADORES!:** {texto_ganadores}")
        else:
            sesion_pirata["agujerosave"].append(num_ranura)
            await context.bot.send_message(chat_id=chat_id,
                text=f"🗡️ ¡*Click*! Ranura {num_ranura} a salvo. **{nombre_usuario(user)}** sobrevivió. 😮‍💨")
            sesion_pirata["turno_actual"] = (sesion_pirata["turno_actual"] + 1) % len(sesion_pirata["sobrevivientes"])
            await enviar_turno_pirata(chat_id, context)

    elif query.data.startswith("ranura_ya_usada_"):
        await query.answer("¡Esa ranura ya tiene una espada clavada, busca otra! 🗡️", show_alert=True)

# =====================================================================
# MANEJO DE MENSAJES
# =====================================================================

async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    user_name = nombre_usuario(update.effective_user)
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id
    texto = update.message.text.strip() if update.message.text else ""
    if not texto and update.message.dice:
        texto = update.message.dice.emoji

    # ── PRIVADO: moderador cipher envía código ──────────────────────
    if chat_type == "private" and user_id in esperando_code:
        gid = esperando_code[user_id]
        sesion_cipher.update({
            "codigo": texto,
            "numeros_adivinadas": [],
        })
        del esperando_code[user_id]
        await update.message.reply_text("¡𝖢𝗈́𝖽𝗂𝗀𝗈 𝗋𝖾𝖼𝗂𝖻𝗂𝖽𝗈! El juego comienza.")
        pantalla_inicial = dibujar_pantalla_code(texto, "")
        await context.bot.send_message(chat_id=gid,
            text=f"📝 **¡CIPHER INICIADO!**\n\nAdivina el código.\n\n`{pantalla_inicial}`")
        return

    # ── PRIVADO: encubridor box envía emojis ────────────────────────
    if chat_type == "private" and user_id in esperando_elementos:
        gid = esperando_elementos[user_id]
        emojis_originales = extraer_emojis(texto)
        if len(emojis_originales) != 6:
            await update.message.reply_text("¡Alto ahí! Esos no son 6 emojis, por favor vuelve a enviar.")
            return

        sesion_box[gid].update({
            "emojis_secretos": emojis_originales,
            "emojis_adivinados": [],
            "puntajes": {},
            "activa": True,
        })
        del esperando_elementos[user_id]
        await update.message.reply_text("¡𝖬𝗎𝖼𝗁𝖺𝗌 𝗀𝗋𝖺𝖼𝗂𝖺𝗌, 𝗅𝗈𝗌 𝟨 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌 𝗁𝖺𝗇 𝗌𝗂𝖽𝗈 𝗀𝗎𝖺𝗋𝖽𝖺𝖽𝗈𝗌!")

        lista_visual = " ".join(emojis_originales)
        mensaje_flash = await context.bot.send_message(chat_id=gid,
            text=f"¡𝗟𝗔 𝗖𝗔𝗝𝗔 𝗦𝗘𝗥𝗔 𝗔𝗕𝗜𝗘𝗥𝗧𝗔ⵑ\n\nMemoriza los elementos, desaparecerán en 5 segundos:\n\n{lista_visual}")
        await asyncio.sleep(5)
        try:
            await context.bot.delete_message(chat_id=gid, message_id=mensaje_flash.message_id)
        except Exception:
            pass
        await context.bot.send_message(chat_id=gid,
            text="¡𝗟𝗔 𝗖𝗔𝗝𝗔 𝗙𝗨𝗘 𝗖𝗘𝗥𝗥𝗔𝗗𝗔ⵑ\n\nEnvía tus respuestas de uno en uno. Si coincide con un objeto de la caja, ganas 1 punto.")
        return

    # ── PRIVADO: moderador charada envía nombre de equipo ───────────
    if chat_type == "private":
        await escuchar_charada_privado(update, context, user_id, texto)
        return

    # ── GRUPO: respuestas de juegos ──────────────────────────────────
    if chat_type in ["group", "supergroup"]:
        # CHARADA (no bloquea el resto)
        await escuchar_charada_grupo(update, context, user_id, texto, chat_id)

        # CIPHER: adivinar número del código
    if sesion_cipher.get("activa") and texto.isdigit():
            codigo = sesion_cipher.get("codigo", "")
            
            # 1. Validamos que el intento tenga la misma cantidad de dígitos que el código secreto
            if len(texto) != len(codigo):
                await update.message.reply_text(f"⚠️ El código debe tener exactamente {len(codigo)} dígitos.")
                return

            # 2. Comparamos el código secreto con el intento del usuario
            pantalla = dibujar_pantalla_code(codigo, texto)
            
            # 3. Mandamos el resultado (ej: __3___)
            await update.message.reply_text(f"🧐 Intento de {user_name}:\n\n`{pantalla}`")
            
            # 4. Si ya no hay guiones bajos, ¡ganó!
            if "_" not in pantalla:
                sesion_cipher["activa"] = False
                await update.message.reply_text(f"🎉 **¡{user_name} DESCIFRÓ EL CÓDIGO!** 🎉\n\nEl código era: `{codigo}`")
            return

        # BOX: adivinar emojis
        if chat_id in sesion_box and sesion_box[chat_id].get("activa"):
            sesion = sesion_box[chat_id]
            emojis_enviados = extraer_emojis(texto)
            if not emojis_enviados:
                return
            emoji_enviado = emojis_enviados[0].replace('\uFE0F', '')
            secretos_normalizados = [e.replace('\uFE0F', '') for e in sesion.get("emojis_secretos", [])]
            adivinados_normalizados = [e.replace('\uFE0F', '') for e in sesion.get("emojis_adivinados", [])]

            if emoji_enviado in adivinados_normalizados:
                await update.message.reply_text("¡𝖤𝗌𝖾 𝗈𝖻𝗃𝖾𝗍𝗈 𝖿𝗎𝖾 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈 𝖺𝗇𝗍𝖾𝗌!")
                return
            if emoji_enviado not in secretos_normalizados:
                await update.message.reply_text("¡𝖤𝗌𝖾 𝗈𝖻𝗃𝖾𝗍𝗈 𝗇𝗈 𝖾𝗌𝗍𝖺𝖻𝖺 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺!")
                return

            indice = secretos_normalizados.index(emoji_enviado)
            emoji_original = sesion["emojis_secretos"][indice]
            sesion["emojis_adivinados"].append(emoji_original)
            sesion["puntajes"][user_id] = sesion["puntajes"].get(user_id, 0) + 1
            total = len(sesion["emojis_adivinados"])

            await update.message.reply_text(
                f"¡𝖯𝗎𝗇𝗍𝗈 𝗉𝖺𝗋𝖺 {user_name}! El objeto sí estaba en la caja.\n"
                f"Llevamos [{total}/6] objetos descubiertos.")

            if total == 6:
                sesion["activa"] = False
                tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
                medallas = ["🥇", "🥈", "🥉"]
                msg = "¡𝖱𝖮𝖭𝖣𝖠 𝖥𝖨𝖭𝖠𝖫𝖨𝖹𝖠𝖣𝖠! Se descubrieron todos los objetos.\n\nPuntuación final:\n"
                for i, (uid, pts) in enumerate(tabla):
                    jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid), None)
                    nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid}"
                    dec = medallas[i] if i < 3 else "🔹"
                    msg += f"{dec} {nombre_p}: {pts} pt(s)\n"
                await context.bot.send_message(chat_id=chat_id, text=msg)

        # CASERÍA: responder emoji objetivo
        if sesion_caseria.get("activa") and sesion_caseria.get("objetivo_actual"):
            objetivo = sesion_caseria["objetivo_actual"]
            emojis_env = extraer_emojis(texto)
            if objetivo in emojis_env and not sesion_caseria.get("respondio_turno"):
                sesion_caseria["respondio_turno"] = True
                sesion_caseria["jugadores"][user_id] = sesion_caseria["jugadores"].get(user_id, 0) + 1
                await update.message.reply_text(f"✅ ¡{user_name} encontró el {objetivo}! +1 punto 🎉")

# ──────────────────────────────────────────────────────────────────────

async def escuchar_charada_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    if (not sesion_charada.get("activa") and
            sesion_charada.get("moderador_id") == user_id and
            not sesion_charada.get("nombre_recibido")):
        if not texto:
            return
        if sesion_charada["bando_actual"] == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{texto} 🔴"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{texto} 🔵"
        sesion_charada["nombre_recibido"] = True
        await update.message.reply_text(f"✅ ¡Nombre registrado! Tu equipo se llamará: **{texto.upper()}**.")

async def escuchar_charada_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_charada.get("activa"):
        return
    if user_id == sesion_charada["moderador_id"]:
        return
    if not texto:
        return

    bando_actual = sesion_charada["bando_actual"]
    lista_equipo_valido = sesion_charada["equipo_rojo"] if bando_actual == "rojo" else sesion_charada["equipo_azul"]
    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_actual == "rojo" else sesion_charada["nombre_equipo_azul"]

    if user_id not in lista_equipo_valido:
        return

    texto_limpio = texto.lower()
    if texto_limpio in sesion_charada["palabras_ronda"] and not sesion_charada["palabras_ronda"][texto_limpio]:
        sesion_charada["palabras_ronda"][texto_limpio] = True
        adivinadas_totales = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)

        await update.message.reply_text(
            f"🎉 ¡{update.effective_user.first_name} ADIVINÓ! ✨\n"
            f"✅ Palabra: **{texto_limpio.upper()}**\n"
            f"📊 {nombre_bando_jugando}: **{adivinadas_totales}/10** acertadas.")

        if adivinadas_totales == 10:
            sesion_charada["activa"] = False
            if bando_actual == "rojo":
                sesion_charada["puntos_rojo"] += 10
            else:
                sesion_charada["puntos_azul"] += 10
            await context.bot.send_message(chat_id=chat_id,
                text=f"🏆 **¡PUNTAJE PERFECTO!** 🏆\n\n"
                     f"¡El equipo **{nombre_bando_jugando.upper()}** adivinó las 10 palabras!\n\n"
                     f"📊 **PUNTAJE GLOBAL:**\n"
                     f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                     f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts")

# =====================================================================
# COMANDO DE CIERRE GENERAL
# =====================================================================

async def detener_juegos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cipher
    sesion_cipher["activa"] = False
    sesion_cipher["jugadores"] = []

    # Zombie
    sesion_zombie["activa"] = False
    sesion_zombie["jugadores"] = []
    sesion_zombie["zombies"] = []
    sesion_zombie["vivos"] = []
    sesion_zombie["fase"] = None

    # Casería
    sesion_caseria["activa"] = False
    sesion_caseria["jugadores"] = {}

    # Box
    chat_id = update.effective_chat.id
    if chat_id in sesion_box:
        sesion_box[chat_id]["activa"] = False
        sesion_box[chat_id]["jugadores"] = []

    # Charada
    sesion_charada["activa"] = False
    sesion_charada["fase_registro"] = False
    sesion_charada["jugadores"] = []

    # Pirata
    sesion_pirata["activa"] = False
    sesion_pirata["jugadores"] = []

    await update.message.reply_photo(
        photo=GIF_OFFVAN,
        caption="¡CLOSE VAN!\n\nSe cerraron todas las rondas existentes.")

# =====================================================================
# BLOQUE PRINCIPAL DE ARRANQUE
# =====================================================================

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Servidor Flask escuchando en el puerto {port}...")
    app_web.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == '__main__':
    import threading

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    token_bot = os.environ.get('TOKEN')
    if not token_bot:
        raise ValueError("❌ ¡Error crítico! No se encontró la variable 'TOKEN' en el panel de Render.")

    print("🤖 Iniciando bot de Telegram con run_polling...")
    application = ApplicationBuilder().token(token_bot).build()

    # Comandos generales
    application.add_handler(CommandHandler("start",    start_bienvenida, filters=PREFIX))
    application.add_handler(CommandHandler("info",     info,             filters=PREFIX))
    application.add_handler(CommandHandler("cmds",     comandos,         filters=PREFIX))
    application.add_handler(CommandHandler("off_van",  detener_juegos,   filters=PREFIX))

    # Cipher
    application.add_handler(CommandHandler("cipher",       unirse_cipher,  filters=PREFIX))
    application.add_handler(CommandHandler("start_cipher", iniciar_cipher, filters=PREFIX))

    # Zombie
    application.add_handler(CommandHandler("zombie",       unirse_zombie,  filters=PREFIX))
    application.add_handler(CommandHandler("start_zombie", iniciar_zombie, filters=PREFIX))

    # Casería
    application.add_handler(CommandHandler("caseria",       unirse_caseria,  filters=PREFIX))
    application.add_handler(CommandHandler("start_caseria", iniciar_caseria, filters=PREFIX))

    # Box
    application.add_handler(CommandHandler("box",       unirse_box,  filters=PREFIX))
    application.add_handler(CommandHandler("start_box", iniciar_box, filters=PREFIX))

    # Charada
    application.add_handler(CommandHandler("charada",       unirse_charada,  filters=PREFIX))
    application.add_handler(CommandHandler("start_charada", iniciar_charada, filters=PREFIX))

    # Pirata
    application.add_handler(CommandHandler("pirata",       unirse_pirata,  filters=PREFIX))
    application.add_handler(CommandHandler("start_pirata", iniciar_pirata, filters=PREFIX))

    # Handlers generales
    application.add_handler(CallbackQueryHandler(manejar_botones))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    application.run_polling(drop_pending_updates=True)
