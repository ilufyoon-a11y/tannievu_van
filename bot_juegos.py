import random
import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- 1. DESPERTADOR PARA RENDER (FLASK) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "🥭 Sistema MANGO - Juegos Activos"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. VARIABLES GLOBALES Y DICCIONARIOS ---
sesión = {}            # Ahorcado
esperando_palabra = {} # Ahorcado (Privado)

sesión_bomba = {
    "jugadores": [], "bomba_en": None, "activa": False, "tarea_bomba": None
}

sesión_ratones = {
    "jugadores": [], "sobrevivientes": [], "esperando_click": [], "activa": False, "mensaje_id": None
}

sesión_stop = {
    "jugadores": [],        # Lista de inscritos
    "sobrevivientes": [],   # IDs de los que siguen vivos
    "turno_index": 0,       # Quién está jugando ahorita
    "palabras_dichas": [],  # Lista para que NO se repitan
    "letra_actual": "",
    "categoria_actual": "",
    "activa": False,
    "timer_task": None      # Control del reloj por turno
}

CATEGORIAS_STOP = ["FRUTA O VERDURA 🍎", "PAÍS O CIUDAD 🗺️", "ANIMAL 🦁", "COLOR 🎨", "CARRERA O PROFESIÓN 🏗️", "CANTANTE O BANDA 🎤"]

# --- 3. AUXILIARES (AHORCADO) ---
def dibujar_pantalla_ahorcado(chat_id):
    datos = sesión[chat_id]
    palabra = datos["palabra_secreta"]
    adivinadas = datos["letras_adivinadas"]
    return "".join([letra + " " if letra in adivinadas else ("  " if letra == " " else "_ ") for letra in palabra]).strip()

# --- 4. COMANDO MENÚ PRINCIPAL ---
async def start_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje_menu = (
        "🥭 **¡BIENVENIDO AL SISTEMA MANGO JUEGOS!** 🎮✨\n\n"
        "Aquí tienes el catálogo completo de diversión extrema para el grupo, chiki. "
        "Usa los comandos para unirse y empezar la masacre:\n\n"
        "🪵 **1. EL AHORCADO** (Pensar y chisme)\n"
        "➡️ `/ahorcado` - Unirse a la lista\n"
        "➡️ `/start_ahorcado` - Elegir moderador e iniciar\n\n"
        "🧨 **2. LA BOMBA EXPLOSIVA** (Puro pánico)\n"
        "➡️ `/bomba` - Entrar al búnker\n"
        "➡️ `/start_bomba` - Encender la mecha\n\n"
        "🐭 **3. RATONES BATTLE ROYALE** (Velocidad 3x3)\n"
        "➡️ `/ratones` - Entrar a la madriguera\n"
        "➡️ `/start_ratones` - Lanzar el tablero\n\n"
        "🥁 **4. RITMO A GO-GO** (Eliminación por turnos)\n"
        "➡️ `/stop` - Alistarse para el ritmo\n"
        "➡️ `/start_stop` - Lanzar letra, categoría e iniciar turnos\n\n"
        "💡 _Tip: Para los juegos de velocidad y turnos, diles a todos los causas que se unan antes de darle start o no los dejará jugar._ 💅"
    )
    await update.message.reply_text(mensaje_menu, parse_mode="Markdown")

# --- 5. JUEGO 1: AHORCADO ---
async def unirse_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boton = InlineKeyboardButton("꒦꒷ UNIRME ꒦꒷", callback_data="unirme_click")
    await update.message.reply_text("¡Ahorcado! Presiona para unirte:", reply_markup=InlineKeyboardMarkup([[boton]]))

async def iniciar_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesión or len(sesión[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("Se necesitan mínimo 2 personas, causa.")
        return 
    moderador = random.choice(sesión[chat_id]["jugadores"])
    sesión[chat_id].update({"moderador_id": moderator["id"], "activa": True})
    esperando_palabra[moderador["id"]] = chat_id
    await update.message.reply_text(f"¡Iniciado! Moderador: {moderador['name']}. Pásame la palabra al privado.")

# --- 6. JUEGO 2: LA BOMBA ---
async def unirse_bomba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesión_bomba["jugadores"] = []
    sesión_bomba["activa"] = False
    boton = InlineKeyboardButton("💣 ENTRAR AL BÚNKER 💣", callback_data="unirme_bomba_click")
    await update.message.reply_text("🚨 **¡JUEGO DE LA BOMBA!** 🚨\nEntren rápido antes de encender la mecha.", reply_markup=InlineKeyboardMarkup([[boton]]))

async def iniciar_bomba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(sesión_bomba["jugadores"]) < 2:
        await update.message.reply_text("⚠️ Necesitamos mínimo 2 causas para pasar la bomba.")
        return
    sesión_bomba["activa"] = True
    primer_jugador = random.choice(sesión_bomba["jugadores"])
    sesión_bomba["bomba_en"] = primer_jugador["id"]
    await update.message.reply_text(f"🧨 ¡LA BOMBA ESTÁ ENCENDIDA! 🧨\nSe la pasé a: **{primer_jugador['name']}**")
    sesión_bomba["tarea_bomba"] = asyncio.create_task(cuenta_regresiva_bomba(chat_id, context))

async def cuenta_regresiva_bomba(chat_id, context):
    tiempo_explotar = random.randint(10, 20)
    boton_pasar = InlineKeyboardButton("💥 ¡PASAR BOMBA! 💥", callback_data="pasar_bomba_click")
    mensaje_bomba = await context.bot.send_message(
        chat_id=chat_id, text="🔴 Tienes la bomba. ¡Presiona el botón rápido para pasarla!", reply_markup=InlineKeyboardMarkup([[boton_pasar]])
    )
    await asyncio.sleep(tiempo_explotar)
    if sesión_bomba["activa"]:
        sesión_bomba["activa"] = False
        perdedor_id = sesión_bomba["bomba_en"]
        perdedor_name = next(j['name'] for j in sesión_bomba["jugadores"] if j['id'] == perdedor_id)
        await context.bot.edit_message_text(
            chat_id=chat_id, message_id=mensaje_bomba.message_id,
            text=f"💥💥 **¡¡¡¡BOOOOOOM!!!!** 💥💥\n\nLa bomba le explotó en la cara a **{perdedor_name}**. ¡Quedaste hecho cenizas, chiki! 💀💨"
        )

# --- 7. JUEGO 3: RATONES BATTLE ROYALE (3x3) ---
async def unirse_ratones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesión_ratones["jugadores"] = []
    sesión_ratones["sobrevivientes"] = []
    sesión_ratones["activa"] = False
    boton = InlineKeyboardButton("🐭 ENTRAR A LA MADRIGUERA 🕳️", callback_data="unirme_ratones_click")
    await update.message.reply_text("🚨 **BATTLE ROYALE: APLASTA AL RATÓN** 🚨\n¡El último en aplastarlo en cada ronda queda fuera!", reply_markup=InlineKeyboardMarkup([[boton]]))

async def iniciar_ratones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(sesión_ratones["jugadores"]) < 2:
        await update.message.reply_text("⚠️ Mínimo necesitamos 2 causas para la cacería.")
        return
    sesión_ratones["activa"] = True
    sesión_ratones["sobrevivientes"] = [j["id"] for j in sesión_ratones["jugadores"]]
    await update.message.reply_text("🎬 ¡Apareciendo tablero en 3x3! Atentos...")
    asyncio.create_task(rondas_battle_royale(chat_id, context))

async def rondas_battle_royale(chat
