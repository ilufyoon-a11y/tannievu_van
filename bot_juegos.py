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
    return "🥭 Sistema MANGO - Activo"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. VARIABLES GLOBALES ---
sesión = {}            # Para el Ahorcado
esperando_palabra = {} # Para el Ahorcado
sesión_sillas = {      # Para las Sillas Musicales
    "jugadores": [],
    "sentados": [],
    "activa": False
}

# --- 3. FUNCIONES AUXILIARES (AHORCADO) ---
def dibujar_pantalla_ahorcado(chat_id):
    datos = sesión[chat_id]
    palabra = datos["palabra_secreta"]
    adivinadas = datos["letras_adivinadas"]
    resultado = "".join([letra + " " if letra in adivinadas else ("  " if letra == " " else "_ ") for letra in palabra])
    return resultado.strip()

# --- 4. COMANDOS DEL AHORCADO ---
async def unirse_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boton = InlineKeyboardButton("꒦꒷ UNIRME ꒦꒷", callback_data="unirme_click")
    await update.message.reply_text("¡Ahorcado! Presiona para unirte:", reply_markup=InlineKeyboardMarkup([[boton]]))

async def iniciar_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesión or len(sesión[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("Mínimo 2 personas, causa.")
        return 
    moderador = random.choice(sesión[chat_id]["jugadores"])
    sesión[chat_id].update({"moderador_id": moderador["id"], "activa": True})
    esperando_palabra[moderador["id"]] = chat_id
    await update.message.reply_text(f"¡Iniciado! Moderador: {moderador['name']}. Pásame la palabra al privado.")

# --- 5. COMANDOS DE LAS SILLAS MUSICALES ---
async def unirse_sillas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usamos un botón diferente para no confundir con el ahorcado
    boton = InlineKeyboardButton("💃 ENTRAR A LA PISTA 🕺", callback_data="unirme_sillas_click")
    await update.message.reply_text("¡Sillas Musicales! ¿Quién se apunta?", reply_markup=InlineKeyboardMarkup([[boton]]))

async def iniciar_sillas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if len(sesión_sillas["jugadores"]) < 2:
        await update.message.reply_text("¡Faltan patas! Necesitamos al menos 2 para bailar.")
        return

    sesión_sillas["activa"] = True
    sesión_sillas["sentados"] = []
    num_sillas = len(sesión_sillas["jugadores"]) - 1

    await update.message.reply_text(f"🎵 ¡MÚSICA MAESTRA! Corran... hay {num_sillas} sillas.")

    # Intentamos mandar el Voice Note (asegúrate de subir el archivo 'sillas.ogg')
    try:
        with open('sillas.ogg', 'rb') as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f)
    except:
        await update.message.reply_text("🔊 (Sonando música imaginaria porque no encontré el archivo sillas.ogg...)")

    # Tiempo aleatorio de baile
    await asyncio.sleep(random.randint(10, 20))

    # Aparece el botón de sentarse
    boton = InlineKeyboardButton("🪑 ¡SIÉNTATE YA! 🪑", callback_data="sentado_click")
    await context.bot.send_message(chat_id=chat_id, text="🚫 ¡STOP! ¡EL QUE PESTAÑEA PIERDE!", reply_markup=InlineKeyboardMarkup([[boton]]))

# --- 6. MANEJADOR DE CALLBACKS (BOTONES) ---
async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id
    await query.answer()

    # Click en Unirse Ahorcado
    if query.data == "unirme_click":
        if chat_id not in sesión: sesión[chat_id] = {"jugadores": [], "activa": False}
        if not any(j['id'] == user.id for j in sesión[chat_id]["jugadores"]):
            sesión[chat_id]["jugadores"].append({"id": user.id, "name": user.first_name})
            await query.message.reply_text(f"✅ {user.first_name} listo para el ahorcado.")

    # Click en Unirse Sillas
    elif query.data == "unirme_sillas_click":
        if not any(j['id'] == user.id for j in sesión_sillas["jugadores"]):
            sesión_sillas["jugadores"].append({"id": user.id, "name": user.first_name})
            await query.message.reply_text(f"💃 {user.first_name} ya está en la pista.")

    # Click en Sentarse (Sillas)
    elif query.data == "sentado_click":
        if not sesión_sillas["activa"] or user.id in sesión_sillas["sentados"]:
            return
        
        # Solo si el usuario estaba en la lista de jugadores de sillas
        if any(j['id'] == user.id for j in sesión_sillas["jugadores"]):
            sesión_sillas["sentados"].append(user.id)
            await query.message.reply_text(f"🪑 ¡{user.first_name} se sentó!")
            
            # Si se llenaron las sillas
            if len(sesión_sillas["sentados"]) == len(sesión_sillas["jugadores"]) - 1:
                sesión_sillas["activa"] = False
                ids_total = [j['id'] for j in sesión_sillas["jugadores"]]
                perdedor_id = list(set(ids_total) - set(sesión_sillas["sentados"]))[0]
                perdedor_name = next(j['name'] for j in sesión_sillas["jugadores"] if j['id'] == perdedor_id)
                await context.bot.send_message(chat_id=chat_id, text=f"💀 ¡{perdedor_name} se quedó sin silla! Queda fuera.")

# --- 7. MANEJADOR DE MENSAJES (AHORCADO) ---
async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    chat_type = update.effective_chat.type
    texto = update.message.text.upper() if update.message.text else ""
    
    if chat_type == "private" and user_id in esperando_palabra:
        gid = esperando_palabra[user_id]
        sesión[gid].update({"palabra_secreta": texto, "letras_adivinadas": [], "jugadores_vidas": {}})
        del esperando_palabra[user_id]
        await update.message.reply_text("¡Palabra lista!")
        await context.bot.send_message(chat_id=gid, text=f"¡Adivinen!: `{' '.join(['_' if c != ' ' else ' ' for c in texto])}`", parse_mode="Markdown")
        return

    chat_id = update.effective_chat.id
    if chat_id in sesión and sesión[chat_id].get("activa") and "palabra_secreta" in sesión[chat_id]:
        if len(texto) != 1 or not texto.isalpha() or user_id == sesión[chat_id]["moderador_id"]: return
        datos = sesión[chat_id]
        if user_id not in datos["jugadores_vidas"]: datos["jugadores_vidas"][user_id] = 6
        if datos["jugadores_vidas"][user_id] <= 0: return

        if texto in datos["palabra_secreta"]:
            if texto not in datos["letras_adivinadas"]: datos["letras_adivinadas"].append(texto)
            msg = f"¡La {texto} está!"
        else:
            datos["jugadores_vidas"][user_id] -= 1
            msg = f"La {texto} no está."

        tablero = dibujar_pantalla_ahorcado(chat_id)
        await update.message.reply_text(f"Palabra: `{tablero}`\nVidas: {datos['jugadores_vidas'][user_id]}\n{msg}", parse_mode="Markdown")
        
        if "_" not in tablero:
            await update.message.reply_text(f"🏆 ¡VICTORIA DE {user_name.upper()}!")
            datos["activa"] = False

# --- 8. ARRANQUE ---
if __name__ == '__main__':
    TOKEN = os.getenv("TOKEN_TELEGRAM")
    if TOKEN:
        keep_alive()
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Handlers Ahorcado
        application.add_handler(CommandHandler("ahorcado", unirse_ahorcado))
        application.add_handler(CommandHandler("start_ahorcado", iniciar_ahorcado))
        
        # Handlers Sillas
        application.add_handler(CommandHandler("sillas", unirse_sillas))
        application.add_handler(CommandHandler("start_sillas", iniciar_sillas))
        
        # Callbacks y Mensajes
        application.add_handler(CallbackQueryHandler(manejar_botones))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
        
        print("Bot hibrido encendido... 🥭🚀")
        application.run_polling()
