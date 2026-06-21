import random
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

GIF_BIENVENIDA = "https://i.postimg.cc/T1jPgpDX/upscalemedia-transformed-(3).jpg" 
GIF_INFO       = "https://i.postimg.cc/9XgrQHCd/upscalemedia-transformed-(1).jpg" 
GIF_AHORCADO   = "https://i.postimg.cc/6qg3jBTv/1000004761.jpg" 
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

# !!⠀⠀DICCIONARIO DE CADA JUEGO⠀ ───⠀ ⠀♥︎

# CIPHER 😵

sesión_ahorcado = {
    "jugadores": [], 
    "activa": False,     
    "code": "",       
    "codes_tries": [],   
    "mensaje_juego_id": None, 
    "turno_de": None
    }

esperando_code = {}

# ZOMBIE 🧟

sesión_zombie = {
    "jugadores": [],        
    "activa": False,        
    "zombies": [],          
    "vivos": [],            
    "fase": None,           
    "votos": {},            
    "mensaje_voto_id": None,
    "ultimo_zombie_id": None
    }

esperando_mordida = {}     

# BOX 📦

sesión_jitb = {}

# CHARADA 

WIKI_CHARADA = {
    "peliculas_animadas": ["Coraline y la Puerta Secreta", "Kung Fu Panda", "La era del hielo", "Ratatouille", "Monsters, Inc.", "Toy Story", "Up", "Intensamente", "Buscando a Nemo", "Shrek", 
    "Mi villano favorito", "Hotel Transylvania", "Rio", "Coco", "El rey león", "Enredados", "Frozen"],

    "personajes": ["Mickey Mouse", "Bugs Bunny", "Bob Esponja", "Pato Donald", "Pikachu", "Pedro Picapiedra", "Las Chicas Superpoderosas", "La Pantera Rosa", "Dora la Exploradora", "Peppa Pig",
                  "Hello Kitty", "El Grinch" ],
    "kpop": ["dynamite", "butter", "boy with luv", "fake love", "dna", 
        "mic drop", "idol", "run bts", "spring day", "permission to dance"]

sesion_charada = {
    "activa": False,         
    "fase_registro": False, 
    "jugadores": [], 
    
    "equipo_hyung": [],    
    "equipo_maknae": [],      
    
    "bando_actual": None,   
    "moderador_id": None,     
    "categoria_random": "",    
    "palabras_ronda": {},    
    "respondio_turno": False, 
    "mensaje_grupo_id": None,
    
    "puntos_hyung": 0,
    "puntos_maknae": 0
}


    
# !!⠀⠀AUXILIARES⠀ ───⠀ ⠀♥︎

# DIBUJAR EL MENU DE CODE - SE ACTUALIZA CADA QUE SE ADIVINA UN NUMERO 

def dibujar_pantalla_code(chat_id):
    if chat_id not in sesión: return ""
    datos = sesión[chat_id]
    codigo = datos.get("codigo", "")
    adivinadas = datos.get("numeros_adivinadas", []) 
    
    resultado = []
    
    for i in range(len(codigo)):
        num = codigo[i]
        identificador = f"{i}_{num}"
        
        if identificador in adivinadas:
            resultado.append(num + " ")
        elif num == " ":
            resultado.append("  ")
        else:
            resultado.append("_ ")
            
    return "".join(resultado).strip()

# PERMITE QUE LOS EMOJIS DE BOX SEAN DETECTADOS 

def extraer_emojis(texto):
    import emoji
    return [c['emoji'] for c in emoji.emoji_list(texto)]

# EXTRAER EL ARROBA DE LOS USUARIOS - PERMITE QUE SEAN ARROBADOS EN LOS TEXTOS 

def nombre_usuario(user):
    return f"@{user.username}" if user.username else user.first_name
    
# !!⠀⠀CODIGO DE START EN EL BOT⠀ ───⠀ ⠀♥︎

async def start_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = GIF_BIENVENIDA,
        caption = "\n\n🌸ㅤㅤ⪩⪩ㅤㅤ𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝@ㅤㅤ!!ㅤㅤ☆ \n\n𝖵𝖺𝗇 𝖾𝗌 𝗎𝗇 𝖻𝗈𝗍 𝗊𝗎𝖾 𝗈𝖿𝗋𝖾𝖼𝖾 𝗎𝗇𝖺 𝗏𝖺𝗋𝗂𝖾𝖽𝖺𝖽 𝖽𝖾 𝗃𝗎𝖾𝗀𝗈𝗌, 𝖺𝗎𝗇 𝖾𝗌𝗍𝖺 𝖾𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗈 𝖽𝖾 𝗉𝗋𝗎𝖾𝖻𝖺 𝖺𝗌𝗂 𝗊𝗎𝖾 𝗌𝗂𝖾𝗇𝗍𝖾𝗍𝖾 𝖾𝗇 𝗍𝗈𝗍𝖺𝗅 𝗅𝗂𝖻𝖾𝗋𝗍𝖺𝖽 𝖽𝖾 𝖼𝗈𝗆𝗎𝗇𝗂𝖼𝖺𝗋 𝖼𝗎𝖺𝗅𝗊𝗎𝗂𝖾𝗋 𝗊𝗎𝖾𝗃𝖺/𝗌𝗎𝗀𝖾𝗋𝖾𝗇𝖼𝗂𝖺 𝖾𝗇 𝖾𝗅 𝖼𝗁𝖺𝗍 𝖽𝖾𝗅 𝖼𝖺𝗇𝖺𝗅. \n\n𝖤𝗌𝗉𝖾𝗋𝖺𝗆𝗈𝗌 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗃𝗎𝖾𝗀𝗈𝗌 𝖼𝗈𝗇𝗍𝖾𝗇𝗂𝖽𝗈𝗌 𝗌𝖾𝖺𝗇 𝖽𝖾 𝗌𝗎 𝖺𝗀𝗋𝖺𝖽𝗈! 💕"
    )
    
# !!⠀⠀CODIGO DE INFO DEL BOT⠀ ───⠀ ⠀♥︎

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_photo(
        photo = GIF_INFO,
        caption = ("🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦     ꒱꒱\n\n"
            "𝒊. 𝐀𝐡𝐨𝐫𝐜𝐚𝐝𝐨\n\n"
            "𝖤𝗅 𝗃𝗎𝖾𝗀𝗈 𝖼𝗅𝖺𝗌𝗂𝖼𝗈 𝗊𝗎𝖾 𝗍𝗈𝖽𝗈𝗌 𝖼𝗈𝗇𝗈𝖼𝖾𝗇\n\n"
            "𝒗. 𝐖𝐡𝐚𝐭'𝐬 𝐢𝐧 𝐭𝐡𝐞 𝐛𝐨𝐱\n\n"
            "𝖨𝗇𝗌𝗉𝗂𝗋𝖺𝖽𝗈 𝖾𝗇 𝖵𝖺𝗋𝗂𝖾𝗍𝗒 𝖲𝗁𝗈𝗐𝗌 𝗈𝖿 𝖬𝖾𝗆𝗈𝗋𝗂𝖾𝗌: 𝖯𝖺𝗋𝗍 𝟣, 𝗍𝖾𝗇𝖽𝗋𝖺𝗇 𝗌𝗈𝗅𝗈 𝟧 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝗆𝖾𝗆𝗈𝗋𝗂𝗓𝖺𝗋 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺. ¡𝖠 𝗆𝖺𝗒𝗈𝗋 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝖽𝗈𝗌, 𝗆𝖺𝗒𝗈𝗋 𝗉𝗎𝗇𝗍𝖺𝗃𝖾!\n\n"
            "𝒗𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞\n\n"
            "𝖴𝗇𝖺 𝖾𝗑𝖼𝗎𝗋𝗌𝗂𝗈𝗇 𝗌𝖾 𝗏𝗂𝗈 𝗂𝗇𝗍𝖾𝗋𝗋𝗎𝗆𝗉𝗂𝖽𝖺 𝗉𝗈𝗋 𝗎𝗇 𝗏𝗂𝗋𝗎𝗌 𝗓𝗈𝗆𝖻𝗂𝖾 𝗒 𝖽𝖾𝖻𝖾𝗇 𝖾𝗌𝗉𝖾𝗋𝖺𝗋 𝗁𝖺𝗌𝗍𝖺 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗋𝖾𝗌𝖼𝖺𝗍𝖾𝗇, 𝗌𝗈𝗅𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾𝗇 𝗋𝖾𝗌𝗀𝗎𝖺𝗋𝖽𝖺𝗋 𝖾𝗇 𝗎𝗇 𝖺𝗎𝗍𝗈𝖻𝗎𝗌, 𝗉𝖾𝗋𝗈 𝗎𝗇 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝗌𝖾 𝖼𝗈𝗅𝗈 𝗒 𝖺𝗍𝖺𝖼𝖺 𝗉𝗈𝗋 𝗅𝖺𝗌 𝗇𝗈𝖼𝗁𝖾𝗌 𝖼𝗎𝖺𝗇𝖽𝗈 𝗅𝖺𝗌 𝗅𝗎𝖼𝖾𝗌 𝗌𝖾 𝖺𝗉𝖺𝗀𝖺𝗇 𝗉𝗈𝗋 𝗌𝖾𝗀𝗎𝗋𝗂𝖽𝖺𝖽 ¿𝖯𝗈𝖽𝗋𝖺𝗇 𝗌𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝗋?\n\n"
                  )       
        )

# !!⠀⠀CODIGO DE LOS COMANDOS DEL BOT⠀ ───⠀ ⠀♥︎

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo = GIF_COMANDOS,
        caption = ("🎡  𖹭𖹭 ㅤ𝗖𝗼𝗺𝗮𝗻𝗱𝗼𝘀 𝗱𝗶𝘀𝗽𝗼𝗻𝗶𝗯𝗹𝗲𝘀  ꒱꒱\n\n"
            "𝒊. 𝐀𝐡𝐨𝐫𝐜𝐚𝐝𝐨\n\n"
            "𝖢𝗈𝗆𝖺𝗇𝖽𝗈𝗌: /ahorcado, /start_ahorcado\n\n"
            "𝒗. 𝐖𝐡𝐚𝐭'𝐬 𝐢𝐧 𝐭𝐡𝐞 𝐛𝐨𝐱\n\n"
            "𝖢𝗈𝗆𝖺𝗇𝖽𝗈𝗌: /box, /start_box\n\n"
            "𝒗𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞\n\n"
            "𝖢𝗈𝗆𝖺𝗇𝖽𝗈𝗌: /zombie, /start_zombie\n\n" 
            "𝖠𝗇𝗍𝖾𝗌 𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝗇𝗎𝖾𝗏𝖺 𝗈 𝗁𝖺𝖻𝖾𝗋𝗌𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝗆𝖺𝗌 𝖽𝖾 𝗎𝗇𝖺 𝗉𝗈𝗋 𝖾𝗊𝗎𝗂𝗏𝗈𝖼𝖺𝖼𝗂𝗈𝗇, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗃𝖾𝖼𝗎𝗍𝖾 /off_van 𝗉𝖺𝗋𝖺 𝗋𝖾𝗌𝖾𝗍𝖾𝖺𝗋 𝖾𝗅 𝖼𝗈𝖽𝗂𝗀𝗈 𝗒 𝖾𝗏𝗂𝗍𝖺𝗋 𝖾𝗋𝗋𝗈𝗋𝖾𝗌"
                  )
    )

# !!⠀⠀⠀CODIGO DE CIPHER⠀ ───⠀ ⠀♥︎

async def unirse_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesión: 
        sesión[chat_id] = {"jugadores": [], "activa": False}
    else:
        sesión[chat_id]["activa"] = False
        sesión[chat_id]["jugadores"] = []
        
    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_click")
    await update.message.reply_photo(
        photo = GIF_AHORCADO,
        caption = "\n\n ៹ ࣪  📝 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 cipher! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesión or len(sesión[chat_id]["jugadores"]) < 2:
        await update.message.reply_photo(
            photo = GIF_ERROR,
            caption = "𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋. 𝖣𝖾 𝗍𝗋𝖺𝗍𝖺𝗋𝗌𝖾 𝗎𝗇 𝖾𝗋𝗋𝗈𝗋, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗏𝗎𝖾𝗅𝗏𝖾 𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈."
        )        
        return 
        
    candidatos = list(sesión[chat_id]["jugadores"])
    ultimo_mod = sesión[chat_id].get("ultimo_moderador_id")
    if ultimo_mod and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_mod]
        if filtrados:
            moderador = random.choice(filtrados)
        else:
            moderador = random.choice(candidatos)
    else:
        moderador = random.choice(candidatos)
    
    sesión[chat_id]["jugadores"].remove(moderador)
    sesión[chat_id].update({
        "moderador_id": moderador["id"], 
        "ultimo_moderador_id": moderador["id"], 
        "activa": True
    })
    
    esperando_palabra[moderador["id"]] = chat_id
    await update.message.reply_text(f"˒˓  ¡𝖬𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈!. 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗊𝗎𝖾 𝗌𝖾 𝖺𝗌𝗂𝗀𝗇𝖾 el codigo 𝗉𝖺𝗋𝖺 𝗉𝗈𝖽𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈  ᨦᨩ") 

    try: 
        await context.bot.send_photo(
            chat_id = moderador["id"],
            photo = GIF_LETRISTA,
            caption = "¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂𝖺 el codigo 𝗊𝗎𝖾 𝖽𝖾𝗌𝗌𝖾𝗌 𝗌𝖾𝖺 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝖽o"
        )

    except Exception:
        await context.bot.send_photo(
            chat_id = chat_id,
            photo = GIF_RECHAZADO,
            caption = f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({moderador['name']}). 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈"
        )
        sesión[chat_id]["activa"] = False

# !!⠀⠀⠀CODIGO DE PIRATA⠀ ───⠀ ⠀♥︎
­
async def unirse_ratones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesión_ratones["jugadores"] = []
    sesión_ratones["sobrevivientes"] = []
    sesión_ratones["activa"] = False
    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_ratones_click")
    await update.message.reply_photo(
        photo = GIF_RATONES,
        caption = "៹ ࣪  🐭 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 atrapar al ratón! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

# !!⠀⠀⠀CODIGO DE BOX⠀ ───⠀ ⠀♥︎

async def unirse_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in sesión_box:
        sesión_box[chat_id] = {
            "jugadores": [],            
            "activa": False,             
        }
    else:
        sesión_box[chat_id]["activa"] = False
        sesión_box[chat_id]["ultimo_encubridor_id"] = None
        sesión_box[chat_id]["jugadores"] = []

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_box_click")
    await update.message.reply_photo(
        photo = GIF_JITB,
        caption = "៹ ࣪  📦 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝗊𝗎𝖾 𝗁𝖺𝗒 𝖾𝗇 𝗅𝖺 𝖼𝖺𝗃𝖺! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesión_box or len(sesión_box[chat_id]["jugadores"]) < 2:
        await update.message.reply_photo(
            photo = GIF_ERROR,
            caption = "𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋. 𝖣𝖾 𝗍𝗋𝖺𝗍𝖺𝗋𝗌𝖾 𝗎𝗇 𝖾𝗋𝗋𝗈𝗋, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗏𝗎𝖾𝗅𝗏𝖾 𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈."
        )

        return     

    candidatos = list(sesión_box[chat_id]["jugadores"])
    ultimo_encubridor = sesión_box[chat_id].get("ultimo_encubridor_id")
    if ultimo_encubridor and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_encubridor]
        if filtrados:
            encubridor = random.choice(filtrados)
        else:
            encubridor = random.choice(candidatos)
    else:
        encubridor = random.choice(candidatos)
    
    sesión_box[chat_id].update({
        "encubridor_id": encubridor["id"], 
        "ultimo_encubridor_id": encubridor["id"], 
        "activa": True
    })
    
    esperando_elementos[encubridor["id"]] = chat_id
    await update.message.reply_text(
        f"˒˓   ¡𝖤𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈!. 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗊𝗎𝖾 𝗌𝖾 𝖺𝗌𝗂𝗀𝗇𝖾𝗇 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝗉𝖺𝗋𝖺 𝗉𝗈𝖽𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈  ᨦᨩ")

    try:
        await context.bot.send_photo(
            chat_id = encubridor["id"],
            photo = GIF_ENCUBRIDOR, 
            caption = (
               "¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋!\n\n"
                "𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂𝖺 𝖾𝗑𝖺𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝟨 𝖾𝗆𝗈𝗃𝗂𝗌, 𝗉𝗋𝗈𝖼𝗎𝗋𝖺 𝗇𝗈 𝖽𝖾𝗃𝖺𝗋 𝖾𝗌𝗉𝖺𝖼𝗂𝗈𝗌 𝖾𝗇𝗍𝗋𝖾 𝖾𝗅𝗅𝗈𝗌 (🌸🌟📰...), 𝗌𝖾𝗋𝖺𝗇 𝗆𝗈𝗌𝗍𝗋𝖺𝖽𝗈𝗌 𝖻𝗋𝖾𝗏𝖾𝗆𝖾𝗇𝗍𝖾 𝖺 𝗅𝗈𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺"
            )

        )
    except Exception as e:
        await update.message.reply_photo(
            photo = GIF_RECHAZADO, 
            caption = (
            f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 @{encubridor.get('username', 'usuario')}. "
            f"𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈."))

# !!⠀⠀⠀CODIGO DE CHARADA⠀ ───⠀ ⠀♥︎

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_zombie_click")
    await update.message.reply_photo(
        photo = GIF_ZOMBIE, 
        caption = "៹ ࣪  🧟 𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝗁𝖺 𝗅𝗅𝖾𝗀𝖺𝖽𝗈 𝗒 𝗅𝗈𝗌 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 𝖾𝗌𝗍𝖺𝗇 𝖾𝗆𝗉𝖾𝗓𝖺𝖽𝗈 𝖺 𝗌𝖺𝗅𝗂𝗋 ¡𝖠𝗉𝗋𝖾𝗌𝗎𝗋𝖺𝗍𝖾 𝖺 𝗌𝗎𝖻𝗂𝗋𝗍𝖾 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌!  ֪",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )
    
async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if sesion_charada.get("fase_registro") or sesion_charada.get("activa"):
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝗈 𝗎𝗇 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝗈 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return

    # Limpieza total para la nueva partida
    sesion_charada["jugadores"] = []
    sesion_charada["equipo_rojo"] = []
    sesion_charada["equipo_azul"] = []
    sesion_charada["fase_registro"] = True
    sesion_charada["activa"] = False

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_charada_click")
    
    await update.message.reply_photo(
        photo = GIF_CHARADA,  # Reemplázalo por tu variable de imagen
        caption = "៹ ࣪ 🎭 **¡𝖦𝖱𝖠𝖭 𝖢𝖧𝖠𝖱𝖠𝖣𝖠 𝖯𝖮𝖱 𝖤𝖰𝖴𝖨𝖯𝖮𝖲!** 🎭\n\n"
                  "Preparen sus mejores mímicas y emojis, causas. Se armarán dos bandos pasados de vueltas y jugaremos en modo contrarreloj.\n\n"
                  "👉 ¡Apresúrate a unirte al elenco! Cuando estén listos, pongan `.iniciar_charada`.",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if not sesion_charada.get("fase_registro"):
        await update.message.reply_text("⚠️ No hay ninguna convocatoria abierta. Usa `.charada` primero.")
        return

    # 🛡️ Validación: Mínimo 4 personas (2 vs 2) para que tenga sentido el juego
    if len(sesion_charada["jugadores"]) < 4:
        await update.message.reply_photo(
            photo = GIF_ERROR, # Reemplázalo por tu variable de error
            caption = "𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟦 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗋𝗆𝖺𝗋 𝗅𝗈𝗌 𝖽𝗈𝗌 𝖾𝗊𝗎𝗂𝗉𝗈𝗌. ¡𝖨𝗇𝗏𝗂𝗍𝖺 𝖺 𝗆𝖺́𝗌 𝖼𝖺𝗎𝗌𝖺𝗌 𝗒 𝗏𝗎𝖾𝗅𝗏𝖾 𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋!"
        )        
        return 

    sesion_charada["fase_registro"] = False

    # 🔀 Mezcla aleatoria y división exacta a la mitad
    lista_ids = [j["id"] for j in sesion_charada["jugadores"]]
    random.shuffle(lista_ids)
    mitad = len(lista_ids) // 2
    sesion_charada["equipo_rojo"] = lista_ids[:mitad]
    sesion_charada["equipo_azul"] = lista_ids[mitad:]

    nombres_rojo = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_rojo"]]
    nombres_azul = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_azul"]]

    # Reset de los nombres base
    sesion_charada["nombre_equipo_rojo"] = "Equipo Rojo 🔴"
    sesion_charada["nombre_equipo_azul"] = "Equipo Azul 🔵"

    # Seleccionar qué bando arranca y quién será su moderador
    bando_inicial = random.choice(["rojo", "azul"])
    sesion_charada["bando_actual"] = bando_inicial

    if bando_inicial == "rojo":
        id_moderador = random.choice(sesion_charada["equipo_rojo"])
    else:
        id_moderador = random.choice(sesion_charada["equipo_azul"])

    nombre_moderador = next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == id_moderador)

    # Selección de los 10 retos aleatorios
    categoria = random.choice(list(DICCIONARIOS_CHARADA.keys()))
    palabras_elegidas = random.sample(DICCIONARIOS_CHARADA[categoria], 10)

    sesion_charada["palabras_ronda"] = {palabra: False for palabra in palabras_elegidas}
    sesion_charada["categoria_random"] = categoria
    sesion_charada["moderador_id"] = id_moderador
    sesion_charada["nombre_recibido"] = False 

    await context.bot.send_message(
        chat_id = chat_id,
        text = f"⚔️ **¡𝖤𝖰𝖴𝖨𝖯𝖮𝖲 𝖠𝖱𝖬𝖠𝖲𝖮𝖲 𝖠𝖫 𝖠𝖹𝖠𝖱!** ⚔️\n\n"
               f"🔴 **𝖤𝖰𝖴𝖨𝖯𝖮 𝖱𝖮𝖩𝖮:** {', '.join(nombres_rojo)}\n"
               f"🔵 **𝖤𝖰𝖴𝖨𝖯𝖮 𝖠𝖹𝖴𝖫:** {', '.join(nombres_azul)}\n\n"
               f"📣 **𝖯𝖱𝖨𝖬𝖤𝖱𝖠 𝖱𝖮𝖭𝖣𝖠:** Juega el **𝖤𝖰𝖴𝖨𝖯𝖮 {bando_inicial.upper()}**.\n"
               f"🎙️ **𝖬𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋:** {nombre_moderador}\n\n"
               f"👀 ¡Atento al privado, causa! Tienes 15 segundos para darle un nombre personalizado a tu equipo."
    )

    # 🤫 Petición de nombre privado al Moderador
    try:
        await context.bot.send_message(
            chat_id = id_moderador,
            text = f"👑 **¡ERES EL MODERADOR DE TU EQUIPO!** 👑\n\n"
                   f"Antes de darte las palabras, escribe aquí abajo el **NOMBRE PERSONALIZADO** que quieras para tu bando.\n\n"
                   f"⏱️ ¡Tienes 15 segundos o el bot les pondrá un nombre random!"
        )
    except Exception:
        await context.bot.send_message(
            chat_id = chat_id,
            text = f"⚠️ ¡{nombre_moderador} debes iniciar el bot en privado! Se canceló la partida."
        )
        return

    # ⏱️ Espera activa de 15 segundos
    espera = 15.0
    while espera > 0 and not sesion_charada["nombre_recibido"]:
        await asyncio.sleep(0.5)
        espera -= 0.5

    # Si se durmió, le asignamos uno chistoso por defecto
    if not sesion_charada["nombre_recibido"]:
        nombre_random = random.choice(["Los Sin Nombre 🦆", "Los Pasados de Frío ❄️", "Los Lentos de Van 🦥", "Mimos Anónimos 🎭"])
        if bando_inicial == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{nombre_random} (Rojo)"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{nombre_random} (Azul)"

    # Se envían las 10 palabras secretas
    lista_texto = "\n".join([f"🔹 {p.upper()}" for p in palabras_elegidas])
    await context.bot.send_message(
        chat_id = id_moderador,
        text = f"🤫 **¡AQUÍ ESTÁN TUS PALABRAS SECRETAS!** 🤫\n\n"
               f"🗂️ Categoria: **{categoria.upper()}**\n\n{lista_texto}\n\n"
               f"¡Corre al grupo a meter mímicas y emojis! No escribas las palabras o quedas descalificado. 💀"
    )

    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_inicial == "rojo" else sesion_charada["nombre_equipo_azul"]
    sesion_charada["activa"] = True

    # Arranque oficial en el grupo
    sesion_charada["mensaje_grupo_id"] = await context.bot.send_message(
        chat_id = chat_id,
        text = f"🎮 **¡EMPIEZA EL CONTRARRELOJ!** 🎮\n\n"
               f"🔥 **Bando jugando:** ✨ {nombre_bando_jugando.upper()} ✨\n"
               f"🎙️ **Moderador:** {nombre_moderador}\n"
               f"🗂️ **Categoría:** {categoria.upper()}\n\n"
               f"¡Tienen 60 segundos para reventar el chat adivinando las 10 palabras! ¡Mete emojis, moderador! 🔥"
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
            chat_id = chat_id,
            text = f"⏱️ **¡TIEMPO AGOTADO!** ⏱️\n\n"
                   f"El equipo **{nombre_bando_jugando.upper()}** logró adivinar **{adivinadas}/10** palabras.\n"
                   f"❌ **Faltaron:** {texto_faltantes}\n\n"
                   f"📊 **PUNTAJE GLOBAL:**\n"
                   f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                   f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts\n\n"
                   f"¡Buen intento! El bot queda libre para otra ronda. 🎭"
        )

# !!⠀⠀⠀CODIGO DE ZOMBIE⠀ ───⠀ ⠀♥︎

async def unirse_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    sesión_zombie["jugadores"] = []
    sesión_zombie["zombies"] = []
    sesión_zombie["vivos"] = []
    sesión_zombie["votos"] = {}
    sesión_zombie["activa"] = False
    sesión_zombie["fase"] = None
    
    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_zombie_click")
    await update.message.reply_photo(
        photo = GIF_ZOMBIE, 
        caption = "៹ ࣪  🧟 𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝗁𝖺 𝗅𝗅𝖾𝗀𝖺𝖽𝗈 𝗒 𝗅𝗈𝗌 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 𝖾𝗌𝗍𝖺𝗇 𝖾𝗆𝗉𝖾𝗓𝖺𝖽𝗈 𝖺 𝗌𝖺𝗅𝗂𝗋 ¡𝖠𝗉𝗋𝖾𝗌𝗎𝗋𝖺𝗍𝖾 𝖺 𝗌𝗎𝖻𝗂𝗋𝗍𝖾 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌!  ֪",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if sesión_zombie["activa"]:
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return
        
    if len(sesión_zombie["jugadores"]) < 3:
        await update.message.reply_animation(
            animation = GIF_ERROR,
            caption = "𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟥 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋. 𝖣𝖾 𝗍𝗋𝖺𝗍𝖺𝗋𝗌𝖾 𝗎𝗇 𝖾𝗋𝗋𝗈𝗋, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗏𝗎𝖾𝗅𝗏𝖾 𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 "
        )

        return

    sesión_zombie["activa"] = True
    sesión_zombie["fase"] = "infeccion"
    sesión_zombie["vivos"] = [j["id"] for j in sesión_zombie["jugadores"]]
    
    ultimo_zombie = sesión_zombie.get("ultimo_zombie_id")
    candidatos = [uid for uid in sesión_zombie["vivos"] if uid != ultimo_zombie]
    paciente_cero_id = random.choice(candidatos if candidatos else sesión_zombie["vivos"])
    sesión_zombie["ultimo_zombie_id"] = paciente_cero_id
    sesión_zombie["zombies"].append(paciente_cero_id)
    sesión_zombie["vivos"].remove(paciente_cero_id)
    
    paciente_cero_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == paciente_cero_id)
    
    await update.message.reply_text(
        "¡Un infectado se colo! Uno de ustedes fue mordido por un zombie 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗌𝗎𝖻𝗂𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌, el brote ha comenzado..."
    )
    
    botones_ataque = []
    for humano_id in sesión_zombie["vivos"]:
        humano_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == humano_id)
        botones_ataque.append([InlineKeyboardButton(f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {humano_obj['name']}", callback_data=f"morder:{humano_id}:{chat_id}")])
        
    try:
        await context.bot.send_photo(
            chat_id = paciente_cero_id,
            photo = GIF_CERO, 
            caption = "𝖥𝗎𝗂𝗌𝗍𝖾 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝖾𝗇𝗍𝗋𝖺𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝗒 𝖺𝗁𝗈𝗋𝖺 𝗌𝗂𝖾𝗇𝗍𝖾𝗌 𝗎𝗇𝖺 𝗇𝖾𝖼𝖾𝗌𝗂𝖽𝖺𝖽 𝗂𝗇𝗍𝖾𝗇𝗌𝖺 𝖽𝖾 𝖼𝖺𝗋𝗇𝖾. ¿𝖰𝗎𝗂𝖾𝗇 𝗌𝖾𝗋𝖺 𝗍𝗎 𝗉𝗋𝖾𝗌𝖺?",
            reply_markup = InlineKeyboardMarkup(botones_ataque)
        )
    except Exception:
        await context.bot.send_message(
            chat_id = chat_id,
            text = f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({paciente_cero_obj['name']}). 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈"
        )

        sesión_zombie["activa"] = False

async def abrir_votacion_zombie(chat_id, context):
    sesión_zombie["fase"] = "votacion"
    sesión_zombie["votos"] = {} 
    
    botones_voto = []
    for jugador in sesión_zombie["jugadores"]:
        botones_voto.append([InlineKeyboardButton(f"𝖤𝗑𝗉𝗎𝗅𝗌𝖺𝗋 𝖺 {jugador['name']}", callback_data=f"voto_z:{jugador['id']}")])
    
    msg_voto = await context.bot.send_message(
        chat_id = chat_id,
        text = (
            "¡𝗥𝗘𝗨𝗡𝗜𝗢𝗡 𝗗𝗘 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗜𝗔ⵑ\n\n𝖠𝗅𝗀𝗎𝗂𝖾𝗇 𝗒𝖺 𝖿𝗎𝖾 𝗆𝗈𝗋𝖽𝗂𝖽𝗈, 𝖺𝗌𝗂 𝗊𝗎𝖾 𝖽𝖾𝖻𝖾𝗇 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝗋 𝖺𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝗆𝗎𝖾𝗋𝖽𝖺 𝖺 𝗈𝗍𝗋𝖺 𝗉𝖾𝗋𝗌𝗈𝗇𝖺.\n\n𝖲𝗈𝗅𝗈 𝖼𝗎𝖾𝗇𝗍𝖺𝗇 𝖼𝗈𝗇 𝟥𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝗉𝗈𝗇𝖾𝗋𝗌𝖾 𝖽𝖾 𝖺𝖼𝗎𝖾𝗋𝖽𝗈 𝗒 𝗏𝗈𝗍𝖺𝗋"
        ),

        reply_markup = InlineKeyboardMarkup(botones_voto)
    )
    sesión_zombie["mensaje_voto_id"] = msg_voto.message_id
    
    asyncio.create_task(timer_votacion_zombie(chat_id, context))

async def timer_votacion_zombie(chat_id, context):
    await asyncio.sleep(30)
    if sesión_zombie["activa"] and sesión_zombie["fase"] == "votacion":
        await procesar_resultados_votacion(chat_id, context)

async def procesar_resultados_votacion(chat_id, context):
    if sesión_zombie["fase"] != "votacion":
        return
    sesión_zombie["fase"] = None
    
    try: await context.bot.delete_message(chat_id=chat_id, message_id=sesión_zombie["mensaje_voto_id"])
    except: pass
    
    if not sesión_zombie["votos"]:
        await context.bot.send_message(chat_id=chat_id, text="𝖭𝖺𝖽𝗂𝖾 𝗏𝗈𝗍𝗈 𝖺 𝗍𝗂𝖾𝗆𝗉𝗈, 𝖾𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝗌𝗂𝗀𝗎𝖾 𝖺𝗊𝗎ı́, 𝖾𝗅 𝖺𝗍𝖺𝗊𝗎𝖾 𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝖺...")
        await pasar_a_siguiente_ataque(chat_id, context)
        return

    conteo = {}
    for vid in sesión_zombie["votos"].values():
        conteo[vid] = conteo.get(vid, 0) + 1
        
    mas_votado_id = max(conteo, key=conteo.get)
    max_votos = conteo[mas_votado_id]
    
    empates = [k for k, v in conteo.items() if v == max_votos]
    if len(empates) > 1:
        await context.bot.send_message(chat_id=chat_id, text="¡𝖧𝗎𝖻𝗈 𝗎𝗇 𝖾𝗆𝗉𝖺𝗍𝖾 𝗒 𝗇𝖺𝖽𝗂𝖾 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈!")
        await pasar_a_siguiente_ataque(chat_id, context)
        return
        
    eliminado_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == mas_votado_id)
    
    if mas_votado_id in sesión_zombie["zombies"]:
        sesión_zombie["zombies"].remove(mas_votado_id)
        sesión_zombie["jugadores"] = [j for j in sesión_zombie["jugadores"] if j["id"] != mas_votado_id]
        
        await context.bot.send_message(
            chat_id = chat_id,
            text = f"{eliminado_obj['name']} 𝗈𝖻𝗍𝗎𝗏𝗈 {max_votos} 𝗏𝗈𝗍𝗈𝗌 𝗒 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌. ¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌, 𝗌𝖾 𝖽𝖾𝗌𝗁𝗂𝖼𝗂𝖾𝗋𝗈𝗇 𝖽𝖾𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈!"
        )
    else:
        sesión_zombie["vivos"].remove(mas_votado_id)
        sesión_zombie["jugadores"] = [j for j in sesión_zombie["jugadores"] if j["id"] != mas_votado_id]
        
        await context.bot.send_message(
            chat_id = chat_id,
            text = f"{eliminado_obj['name']} 𝗈𝖻𝗍𝗎𝗏𝗈 {max_votos} 𝗏𝗈𝗍𝗈𝗌 𝗒 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌. 𝖤𝗋𝖺 𝗎𝗇 𝗁𝗎𝗆𝖺𝗇𝗈 𝗉𝖾𝗋𝖿𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝗌𝖺𝗇𝗈..."
        )

    if not sesión_zombie["zombies"]:
        ganadores = [j["name"] for j in sesión_zombie["jugadores"] if j["id"] in sesión_zombie["vivos"]]
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"¡𝖲𝖮𝖡𝖱𝖤𝖵𝖨𝖵𝖨𝖤𝖱𝖮𝖭!. 𝖤𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝗒 𝖺𝗁𝗈𝗋𝖺 {', '.join(ganadores)} 𝗉𝗎𝖾𝖽𝖾𝗇 𝗏𝗈𝗅𝗏𝖾𝗋 𝖺 𝖼𝖺𝗌𝖺")
        sesión_zombie["activa"] = False
    elif len(sesión_zombie["vivos"]) <= 1:
        zombie_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == sesión_zombie["zombies"][0])
        await context.bot.send_message(chat_id=chat_id, text=f"¡𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦ⵑ. {zombie_obj['name']} 𝗆𝗈𝗋𝖽𝗂𝗈 𝖺 𝗍𝗈𝖽𝗈𝗌 𝗒 𝖼𝗈𝗇𝗏𝗂𝗋𝗍𝗂𝗈 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝖾𝗇 𝗈𝗍𝗋𝗈 𝖿𝗈𝖼𝗈 𝖽𝖾 𝗂𝗇𝖿𝖾𝖼𝖼𝗂𝗈𝗇 🧟‍♂️")
        sesión_zombie["activa"] = False
    else:
        await pasar_a_siguiente_ataque(chat_id, context)

async def pasar_a_siguiente_ataque(chat_id, context):
    sesión_zombie["fase"] = "infeccion"
    
    for z_id in sesión_zombie["zombies"]:
        botones_ataque = []
        for humano_id in sesión_zombie["vivos"]:
            humano_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == humano_id)
            botones_ataque.append([InlineKeyboardButton(f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {humano_obj['name']}", callback_data=f"morder:{humano_id}:{chat_id}")])
            
        try:
            await context.bot.send_message(
                chat_id = z_id,
                text = "𝖮𝗍𝗋𝖺 𝗏𝖾𝗓 𝗌𝗂𝖾𝗇𝗍𝖾𝗌 𝖺𝗇𝗌𝗂𝖾𝖽𝖺𝖽 𝗉𝗈𝗋 𝗉𝗋𝗈𝖻𝖺𝗋 𝖼𝖺𝗋𝗇𝖾. 𝖤𝗅𝗂𝗀𝗎𝖾 𝖺 𝗍𝗎 𝗌𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝖼𝗈𝗇 𝗉𝗋𝖾𝖼𝖺𝗎𝖼𝗂𝗈𝗇",
                reply_markup = InlineKeyboardMarkup(botones_ataque)
            )
        except: pass
    
    await context.bot.send_message(chat_id=chat_id, text="𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝖼𝖺𝖾 𝗒 𝗌𝖾 𝖽𝖾𝖻𝖾𝗇 𝗉𝖺𝗀𝖺𝗋 𝗅𝖺𝗌 𝗅𝗎𝖼𝖾𝗌 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌... 𝖤𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖾𝗌𝗍𝖺 𝖺𝗅 𝖺𝖼𝖾𝖼𝗁𝗈")
        
# !!⠀⠀⠀MANEJO DE CALLBACKS⠀- BOTONES ───⠀ ⠀♥︎

# PIRATA 

elif query.data == "unirme_pirata_click":
        await query.answer()
        if sesion_pirata.get("activa", False):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗍𝖾 𝗉𝗎𝖾𝖽𝖾𝗌 𝗎𝗇𝗂𝗋, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j['id'] == user.id for j in sesion_pirata["jugadores"]):
            sesion_pirata["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🏴‍☠️ ֹ  {nombre_usuario(user)} se unió al barco 𓂃")

    elif query.data.startswith("pirata_clic_"):
        await query.answer()
        
        if not sesion_pirata.get("activa", False):
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
            ganadores = [next(j['name'] for j in sesion_pirata["jugadores"] if j['id'] == uid) 
                         for uid in sesion_pirata["sobrevivientes"] if uid != autor_id]
            
            if not ganadores:
                texto_ganadores = "¡Nadie! El pirata se quedó solo en el mar. 🌊"
            else:
                texto_ganadores = f"✨ {', '.join(ganadores)} ✨"

            await context.bot.send_message(
                chat_id = chat_id,
                text = f"💥 ¡¡𝖹𝖠𝖹𝖹𝖹𝖹!! 🚀\n\n**{nombre_usuario(user)}** metió la espada en la ranura {num_ranura}... ¡𝖸 𝖤𝖫 𝖯𝖨𝖱𝖠𝖳𝖠 𝖲𝖠𝖫𝖳𝖮́ 𝖯𝖮𝖱 𝖫𝖮𝖲 𝖠𝖨𝖱𝖤𝖲! 🩸💀\n\n"
                       f"🏆 **¡𝖦𝖠𝖭𝖠𝖣𝖮𝖱𝖤𝖲!:**\n{texto_ganadores}"
            )
            
        else:
            sesion_pirata["agujerosave"].append(num_ranura)
            await context.bot.send_message(
                chat_id = chat_id,
                text = f"🗡️ ¡*Click*! Ranura {num_ranura} a salvo. **{nombre_usuario(user)}** metió su espada con éxito. 😮‍💨"
            )
            sesion_pirata["turno_actual"] += 1

    elif query.data.startswith("ranura_ya_usada_"):
        await query.answer("¡Esa ranura ya tiene una espada clavada, busca otra! 🗡️", show_alert=True)

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

# CHARADA 
async def manejar_botones_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if query.data == "unirme_charada_click":
        await query.answer()
        if sesion_charada.get("activa", False):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝖾𝗌𝗍𝖺́ 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖼𝗈𝗋𝗋𝗂𝖾𝗇𝖽𝗈!", show_alert=True)
            return
        if not sesion_charada.get("fase_registro", False):
            await query.answer("¡El registro ya cerró, amiko!", show_alert=True)
            return
            
        if not any(j['id'] == user.id for j in sesion_charada["jugadores"]):
            sesion_charada["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🎭 ֹ  {nombre_usuario(user)} se apuntó a las mímicas 𓂃")
            
# BOX 

    elif query.data == "unirme_box_click":
        await query.answer()
        if chat_id not in sesión_jitb:
            sesión_jitb[chat_id] = {"jugadores": [], "activa": False}
        if sesión_jitb[chat_id]["activa"]:
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗍𝖾 𝗉𝗎𝖾𝖽𝖾𝗌 𝗎𝗇𝗂𝗋, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j['id'] == user.id for j in sesión_jitb[chat_id]["jugadores"]):
            sesión_jitb[chat_id]["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
            await query.message.reply_text(f"📦 ֹ  {nombre_usuario(user)} se unió 𓂃")

# ZOMBIE 

    elif query.data == "unirme_zombie_click":
        if sesión_zombie.get("activa", False):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗍𝖾 𝗉𝗎𝖾𝖽𝖾𝗌 𝗎𝗇𝗂𝗋, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j['id'] == user.id for j in sesión_zombie["jugadores"]):
            sesión_zombie["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🚌 ֹ  {nombre_usuario(user)} se unió 𓂃")
        await query.answer()

    elif query.data.startswith("morder:"):
        await query.answer()
        partes = query.data.split(":")
        victima_id = int(partes[1])
        grupo_chat_id = int(partes[2])
        
        if sesión_zombie.get("activa", False) and sesión_zombie.get("fase") == "infeccion":
            if user.id in sesión_zombie.get("zombies", []):
                if victima_id in sesión_zombie["vivos"]:
                    victima_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == victima_id)
                    sesión_zombie["vivos"].remove(victima_id)
                    sesión_zombie["jugadores"] = [j for j in sesión_zombie["jugadores"] if j["id"] != victima_id]
                
                    try: 
                        await query.edit_message_caption(caption=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")
                
                    await context.bot.send_message(
                        chat_id = grupo_chat_id,
                        text = f" 🧟 ¡𝗨𝗡 𝗔𝗧𝗔𝗤𝗨𝗘 𝗛𝗔 𝗢𝗖𝗨𝗥𝗥𝗜𝗗𝗢ⵑ 🧟\n\n{victima_obj['name']} 𝗁𝖺 𝗌𝗂𝖽𝗈 𝖺𝗍𝖺𝖼𝖺𝖽𝗈 𝖾𝗇 𝗅𝖺 𝗈𝗌𝖼𝗎𝗋𝗂𝖽𝖺𝖽 𝗉𝗈𝗋 𝗎𝗇 𝗓𝗈𝗆𝖻𝗂𝖾 𝗒 𝗌𝖾 𝖾𝗌𝗍𝖺 𝗍𝗋𝖺𝗇𝗌𝖿𝗈𝗋𝗆𝖺𝗇𝖽𝗈, 𝗍𝗎𝗏𝗈 𝗊𝗎𝖾 𝗌𝖾𝗋 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾 𝗂𝗇𝗆𝖾𝖽𝗂𝖺𝗍𝗈"
                    )

                    await asyncio.sleep(2)

                    if len(sesión_zombie["vivos"]) <= 1:
                        zombie_obj = next(j for j in sesión_zombie["jugadores"] if j["id"] == sesión_zombie["zombies"][0])
                        await context.bot.send_message(
                            chat_id=grupo_chat_id,
                            text=f"¡𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦ⵑ. {zombie_obj['name']} 𝗆𝗈𝗋𝖽𝗂𝗈 𝖺 𝗍𝗈𝖽𝗈𝗌 𝗒 𝗀𝖺𝗇𝗈 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🧟"
                        )
                        sesión_zombie["activa"] = False
                    else: 
                        await abrir_votacion_zombie(grupo_chat_id, context)
                else:
                    try:
                        await query.edit_message_caption(caption="𝖤𝗌𝗍𝖺 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾.")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text="𝖤𝗌𝗍𝖺 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾.")

    elif query.data.startswith("voto_z:"):
        await query.answer()
        votado_id = int(query.data.split(":")[1])
    
        if sesión_zombie.get("activa", False) and sesión_zombie.get("fase") == "votacion":
            if any(j['id'] == user.id for j in sesión_zombie["jugadores"]):
                sesión_zombie["votos"][user.id] = votado_id
                await query.answer(f"𝖵𝗈𝗍𝗈 𝖾𝗆𝗂𝗍𝗂𝖽𝗈 ✓", show_alert=True)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{nombre_usuario(user)} 𝖺𝖼𝖺𝖻𝖺 𝖽𝖾 𝖾𝗆𝗂𝗍𝗂𝗋 𝗌𝗎 𝗏𝗈𝗍𝗈. \n\n{len(sesión_zombie['votos'])}/{len(sesión_zombie['jugadores'])} 𝗏𝗈𝗍𝗈𝗌 𝖾𝗆𝗂𝗍𝗂𝖽𝗈𝗌"
                )
                if len(sesión_zombie["votos"]) >= len(sesión_zombie["jugadores"]):
                    await procesar_resultados_votacion(chat_id, context)
            else:
                await query.answer("𝖴𝗉𝗌, 𝗍𝗎 𝗇𝗈 𝖾𝗌𝗍𝖺𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝖽𝗈 𝖾𝗇 𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.", show_alert=True)

# !!⠀⠀⠀MANEJO DE MENSAJES⠀ ───⠀ ⠀♥︎

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

    # 🎭 PUENTES DIRECTOS PARA LA CHARADA 
    if chat_type == "private":
        await escuchar_charada_privado(update, context, user_id, texto)
        return  # Cortamos el flujo en privados de la charada para que no interfiera

    if chat_type in ["group", "supergroup"]:
        await escuchar_charada_grupo(update, context, user_id, texto, chat_id)
        # Aquí NO se pone return para que otros comandos/juegos del grupo sigan leyendo normal

# CHARADA

async def escuchar_charada_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    # Capturar el nombre del equipo enviado por el moderador en privado
    if not sesion_charada.get("activa", False) and sesion_charada.get("moderador_id") == user_id and not sesion_charada.get("nombre_recibido", False):
        if not texto:
            return

        if sesion_charada["bando_actual"] == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{texto} 🔴"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{texto} 🔵"
            
        sesion_charada["nombre_recibido"] = True
        await update.message.reply_text(f"✅ ¡Nombre registrado! Tu equipo se llamará: **{texto.upper()}**.")

async def escuchar_charada_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_charada.get("activa", False):
        return

    # El moderador no puede soplar en el chat general
    if user_id == sesion_charada["moderador_id"]:
        return

    if not texto:
        return

    bando_actual = sesion_charada["bando_actual"]
    lista_equipo_valido = sesion_charada["equipo_rojo"] if bando_actual == "rojo" else sesion_charada["equipo_azul"]
    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_actual == "rojo" else sesion_charada["nombre_equipo_azul"]

    # Validamos que quien escriba sea del bando actual
    if user_id not in lista_equipo_valido:
        return 

    texto_limpio = texto.lower()

    # El bot busca en toda la bolsa de 10 palabras (Acepta cualquier orden)
    if texto_limpio in sesion_charada["palabras_ronda"]:
        if not sesion_charada["palabras_ronda"][texto_limpio]:
            sesion_charada["palabras_ronda"][texto_limpio] = True
            adivinadas_totales = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)
            
            await update.message.reply_text(
                f"🎉 ¡{update.effective_user.first_name} ADIVINÓ! ✨\n"
                f"✅ Palabra: **{texto_limpio.upper()}**\n"
                f"📊 {nombre_bando_jugando}: **{adivinadas_totales}/10** acertadas."
            )
            
            # Si se completan las 10 palabras antes del contrarreloj
            if adivinadas_totales == 10:
                sesion_charada["activa"] = False 
                
                if bando_actual == "rojo":
                    sesion_charada["puntos_rojo"] += 10
                else:
                    sesion_charada["puntos_azul"] += 10

                await context.bot.send_message(
                    chat_id = chat_id,
                    text = f"🏆 **¡PUNTAJE PERFECTO!** 🏆\n\n"
                           f"¡El equipo **{nombre_bando_jugando.upper()}** destruyó el juego adivinando las 10 palabras completas antes del tiempo!\n\n"
                           f"📊 **PUNTAJE GLOBAL:**\n"
                           f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                           f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts"
                )

# BOX

    if chat_type == "private" and user_id in esperando_elementos:
        gid = esperando_elementos[user_id]

        emojis_originales = extraer_emojis(texto)
        if len(emojis_originales) != 6:
            await update.message.reply_text("¡Alto ahi! Esos no son 6 elementos, por favor, vuelve a enviar")
            return      
        
        sesion_box[gid].update({
            "emojis_secretos": emojis_originales,    
            "emojis_adivinados": [],               
            "puntajes": {},                     
            "activa": True
        })

        del esperando_elementos[user_id]
        await update.message.reply_text("¡𝖬𝗎𝖼𝗁𝖺𝗌 𝗀𝗋𝖺𝖼𝗂𝖺𝗌, 𝗅𝗈𝗌 𝟨 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌 𝗁𝖺𝗇 𝗌𝗂𝖽𝗈 𝗀𝗎𝖺𝗋𝖽𝖺𝖽𝗈𝗌!")
        
        lista_visual = " ".join(emojis_originales)
        mensaje_flash = await context.bot.send_message(
            chat_id=gid,
            text=f"¡𝗟𝗔 𝗖𝗔𝗝𝗔 𝗦𝗘𝗥𝗔 𝗔𝗕𝗜𝗘𝗥𝗧𝗔ⵑ \n\n 𝖬𝖾𝗆𝗈𝗋𝗂𝗓𝖺 𝖻𝗂𝖾𝗇 𝗅𝗈𝗌 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌, 𝖽𝖾𝗌𝖺𝗉𝖺𝗋𝖾𝖼𝖾𝗋𝖺𝗇 𝖾𝗇 5 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌:\n\n{lista_visual}"
        )
        
        await asyncio.sleep(5)

        try:
            await context.bot.delete_message(chat_id=gid, message_id=mensaje_flash.message_id)
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=gid,
            text="¡𝗟𝗔 𝗖𝗔𝗝𝗔 𝗙𝗨𝗘 𝗖𝗘𝗥𝗥𝗔𝗗𝗔ⵑ\n\nEnvia tus respuestas de uno en uno.\n\n𝖲𝗂 𝖼𝗈𝗂𝗇𝖼𝗂𝖽𝖾𝗌 𝖼𝗈𝗇 𝗎𝗇𝗈 𝗊𝗎𝖾 𝖾𝗌𝗍𝖺𝖻𝖺 𝖾𝗇 𝗅𝖺 𝖼𝖺𝗃𝖺, 𝗍𝖾 𝗅𝗅𝖾𝗏𝖺𝗌 𝟣 𝗉𝗎𝗇𝗍𝗈."
        )
        return

# BOX 

    if chat_type != "private" and chat_id in sesión_box and sesión_box[chat_id].get("activa"):
        sesion = sesión_box[chat_id]
        emojis_enviados = extraer_emojis(texto)

        if not emojis_enviados:
            return

        emoji_enviado = emojis_enviados[0].replace('\uFE0F', '')
        secretos_normalizados = [e.replace('\uFE0F', '') for e in sesion.get("emojis_secretos", [])]
        adivinados_normalizados = [e.replace('\uFE0F', '') for e in sesion.get("emojis_adivinados", [])]

        if emoji_enviado in adivinados_normalizados:
            await update.message.reply_text(f"¡𝖤𝗌𝖾 𝗈𝖻𝗃𝖾𝗍𝗈 𝖿𝗎𝖾 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈 𝖺𝗇𝗍𝖾𝗌!")
            return

        if emoji_enviado not in secretos_normalizados:
            await update.message.reply_text(f"¡𝖤𝗌𝖾 𝗈𝖻𝗃𝖾𝗍𝗈 𝗇𝗈 𝖾𝗌𝗍𝖺𝖻𝖺 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺!")
            return

        indice = secretos_normalizados.index(emoji_enviado)
        emoji_original = sesion["emojis_secretos"][indice]
        sesion["emojis_adivinados"].append(emoji_original)
        sesion["puntajes"][user_id] = sesion["puntajes"].get(user_id, 0) + 1

        total_adivinados = len(sesion["emojis_adivinados"])
        await update.message.reply_text(
            f"¡𝖯𝗎𝗇𝗍𝗈 𝗉𝖺𝗋𝖺 {user_name}! 𝖤𝗅 𝗈𝖻𝗃𝖾𝗍𝗈 𝗌𝗂 𝖾𝗌𝗍𝖺𝖻𝖺 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺\n"
            f"𝖫𝗅𝖾𝗏𝖺𝗆𝗈𝗌 [{total_adivinados} - 6] 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈𝗌."
        )

        if total_adivinados == 6:
            sesion["activa"] = False

            tabla_posiciones = []
            for uid, pts in sesion["puntajes"].items():
                jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid), None)
                nombre_pantalla = jugador_obj["name"] if jugador_obj else f"Jugador ID: {uid}"
                tabla_posiciones.append((nombre_pantalla, pts))

            tabla_posiciones.sort(key=lambda x: x[1], reverse=True)

            mensaje_recuento = "¡𝖱𝖮𝖭𝖣𝖠 𝖥𝖨𝖭𝖠𝖫𝖨𝖹𝖠𝖣𝖠! 𝖲𝖾 𝖽𝖾𝗌𝖼𝗎𝖻𝗋𝗂𝖾𝗋𝗈𝗇 𝗍𝗈𝖽𝗈𝗌 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝗊𝗎𝖾 𝗁𝖺𝖻𝗂𝖺𝗇 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺. \n\n"
            mensaje_recuento += "𝖯𝗎𝗇𝗍𝗎𝖺𝖼𝗂𝗈𝗇 𝖿𝗂𝗇𝖺𝗅: \n"

            medallas = ["🥇", "🥈", "🥉"]
            for index, (nombre, puntos) in enumerate(tabla_posiciones):
                decorador = medallas[index] if index < len(medallas) else "🔹"
                mensaje_recuento += f"{decorador} {nombre}: {puntos} pt(s)\n"

            await context.bot.send_message(chat_id=chat_id, text=mensaje_recuento)
        return

# =====================================================================
# 11. COMANDO DE CIERRE GENERAL
# =====================================================================
async def detener_juegos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # 1. 🎯 APAGÓN TOTAL AL AHORCADO
    if chat_id in sesión:
        sesión[chat_id]["activa"] = False
        sesión[chat_id]["jugadores"] = []
        if "palabra_secreta" in sesión[chat_id]:
            del sesión[chat_id]["palabra_secreta"]
            
    # 2. 💣 APAGÓN TOTAL A LA BOMBA
    sesión_bomba["activa"] = False
    sesión_bomba["jugadores"] = []
    if sesión_bomba.get("tarea_bomba"):
        try: sesión_bomba["tarea_bomba"].cancel()
        except: pass

    # 5. 📦 APAGÓN TOTAL A JACK IN THE BOX
    if chat_id in sesión_box:
        sesión_box[chat_id]["activa"] = False
        sesión_box[chat_id]["jugadores"] = []

    # 7. 🧟 APAGÓN TOTAL A INFECCIÓN ZOMBIE
    sesión_zombie["activa"] = False
    sesión_zombie["jugadores"] = []
    sesión_zombie["zombies"] = []
    sesión_zombie["vivos"] = []
    sesión_zombie["fase"] = None
    sesión_zombie["ultimo_zombie_id"] = None

    await update.message.reply_photo(
        photo = GIF_OFFVAN,
        caption = "¡CLOSE VAN!\n\nSe cerraron todas las rondas existentes.")


# =====================================================================
# 12. BLOQUE PRINCIPAL DE ARRANQUE
# =====================================================================
def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Servidor Flask escuchando en el puerto {port}...")
    # use_reloader=False evita que Render duplique el proceso del bot
    app_web.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == '__main__':
    import threading
    import os
    
    # 1. Lanzamos Flask en un hilo separado para que Render detecte el puerto rápido
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    token_bot = os.environ.get('TOKEN')
    
    if not token_bot:
        raise ValueError("❌ ¡Error crítico! No se encontró la variable 'TOKEN' en el panel de Render.")
    
    print("🤖 Iniciando bot de Telegram con run_polling...")
    application = ApplicationBuilder().token(token_bot).build()

    # !!⠀⠀DEFINIMOS LOS COMANDOS⠀ ───⠀ ⠀♥︎
    
    application.add_handler(CommandHandler("start", start_bienvenida, prefix='.'))
    application.add_handler(CommandHandler("info", info, prefix='.'))
    application.add_handler(CommandHandler("cmds", comandos, prefix='.'))
    application.add_handler(CommandHandler("off_van", detener_juegos, prefix='.'))


    # Handlers JUEGO : PIRATA 
    app.add_handler(CommandHandler("pirata", unirse_pirata, prefix='.'))
    app.add_handler(CommandHandler("start_pirata", iniciar_pirata, prefix='.'))

    # Handlers JUEGO : CHARADA 

    app.add_handler(CommandHandler("pirata", unirse_pirata, prefix='.'))
    app.add_handler(CommandHandler("start_pirata", iniciar_pirata, prefix='.'))

    # Handlers JUEGO : BOX 
    application.add_handler(CommandHandler("box", unirse_box, prefix='.'))
    application.add_handler(CommandHandler("start_box", iniciar_box, prefix='.'))

    # Handlers JUEGO : Infección Zombie
    application.add_handler(CommandHandler("zombie", unirse_zombie))
    application.add_handler(CommandHandler("start_zombie", iniciar_zombie))

    # Handlers de Botones y Mensajes Generales
    application.add_handler(CallbackQueryHandler(manejar_botones))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    # 3. Arrancamos el bot en el hilo principal
    application.run_polling(drop_pending_updates=True)
