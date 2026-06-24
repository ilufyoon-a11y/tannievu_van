
# Aquí solo se importa todo y se registran los handlers.
# Cada juego vive en su propio archivo.

import os
import threading

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
)

# ── Utilidades compartidas ──────────────────────────────────────────
from utils import (
    GIF_BIENVENIDA, GIF_INFO, GIF_COMANDOS, GIF_OFFVAN,
    sesion_puntos, sumar_robux, nombre_usuario,
    ADMIN_IDS,
)

# ── Juegos ──────────────────────────────────────────────────────────
# (importa las funciones de cada archivo de juego)
from bot_juegos import (
    # Cipher
    unirse_cipher, iniciar_cipher,
    # Zombie
    unirse_zombie, iniciar_zombie,
    # Casería
    unirse_caseria, iniciar_caseria,
    # Box
    unirse_box, iniciar_box,
    # Charada
    unirse_charada, iniciar_charada,
    # Pirata
    unirse_pirata, iniciar_pirata,
    # Handlers generales del bot_juegos
    manejar_botones, manejar_mensajes,
    # Cierre general
    detener_juegos,
    # Wallet / Robux
    cmd_new_session, cmd_wallet, cmd_spent, cmd_reset,
)

# ── Adivina la canción (archivo separado) ───────────────────────────
from adivina import (
    unirse_adivina,
    iniciar_adivina_juego,
    verificar_respuesta_musica,
    manejar_boton_unirse_adivina,
)

# =====================================================================
# FLASK — mantiene el bot vivo en Render
# =====================================================================

app_web = Flask('')

@app_web.route('/')
def home():
    return "Van fue encendido"

# =====================================================================
# COMANDOS GENERALES
# =====================================================================

PREFIX = filters.Regex(r'^[./]')

async def start_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_BIENVENIDA,
        caption=(
            "\n\n\U0001f338\u3000\u3000\u2aa9\u2aa9\u3000\u3000\U0001d401\U0001d408\U0001d404\U0001d40d\U0001d415\U0001d404\U0001d40d\U0001d408\U0001d403\u0040\u3000\u3000!!\u3000\u3000\u2606 \n\n"
            "Van es un bot que ofrece una variedad de juegos, a\u00fan est\u00e1 en proceso de prueba "
            "as\u00ed que si\u00e9ntete en total libertad de comunicar cualquier queja/sugerencia en el chat del canal. \n\n"
            "Esperamos que los juegos contenidos sean de su agrado! \U0001f495"
        )
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_INFO,
        caption=(
            "\U0001f40b    \U00010a6d\U00010a6d\u3000\U0001d017\U0001d014\U0001d005\U0001d006\U0001d00e\U0001d016 \U0001d005\U0001d008\U0001d016\U0001d00f\U0001d00e\U0001d01d\U0001d008\U0001d005\U0001d016     \u029a\u029a\n\n"
            "\U0001d456. \U0001d402\U0001d40e\U0001d413\U0001d407\U0001d404\U0001d42b\n\n"
            "Adivina el c\u00f3digo secreto n\u00famero a n\u00famero.\n\n"
            "\U0001d456\U0001d456. \U0001d419\U0001d40e\U0001d416\U0001d41b\U0001d408\U0001d404\n\n"
            "Una excursi\u00f3n se vio interrumpida por un virus zombie. \u00bfPodr\u00e1n sobrevivir?\n\n"
            "\U0001d456\U0001d456\U0001d456. \U0001d402\U0001d41a\U0001d416\U0001d404\U0001d42b\u00ed\U0001d41a\n\n"
            "Encuentra los emojis ocultos en el tablero.\n\n"
            "\U0001d456\U0001d463. \U0001d401\U0001d40e\U0001d419\n\n"
            "Memoriza los elementos de la caja antes de que desaparezcan.\n\n"
            "\U0001d463. \U0001d402\U0001d407\U0001d41a\U0001d42b\U0001d41a\U0001d41d\U0001d41a\n\n"
            "Dos equipos se enfrentan adivinando palabras con m\u00edmicas y emojis.\n\n"
            "\U0001d463\U0001d456. \U0001d40f\U0001d408\U0001d42b\U0001d41a\U0001d42b\U0001d41a\n\n"
            "Clava la espada en la ranura correcta, \u00a1pero cuidado con la trampa!\n\n"
            "\U0001d463\U0001d456\U0001d456. \U0001d400\U0001d41d\U0001d408\U0001d419\U0001d40e\U0001d40d\U0001d41a\n\n"
            "Adivina la canci\u00f3n de K-Pop en solo 4 segundos. \U0001f3a7"
        )
    )

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_COMANDOS,
        caption=(
            "\U0001f3a1  \U00010a6d\U00010a6d \u3000\U0001d402\U0001d428\U0001d426\U0001d41a\U0001d427\U0001d41d\U0001d428\U0001d42c \U0001d41d\U0001d422\U0001d42c\U0001d429\U0001d428\U0001d427\U0001d422\U0001d41d\U0001d425\U0001d41e\U0001d42c  \u029a\u029a\n\n"
            "\U0001d456. \U0001d402\U0001d40e\U0001d413\U0001d407\U0001d404\U0001d42b  \u2192  /cipher  /start_cipher\n\n"
            "\U0001d456\U0001d456. \U0001d419\U0001d40e\U0001d416\U0001d41b\U0001d408\U0001d404  \u2192  /zombie  /start_zombie\n\n"
            "\U0001d456\U0001d456\U0001d456. \U0001d402\U0001d41a\U0001d416\U0001d404\U0001d42b\u00ed\U0001d41a  \u2192  /caseria  /start_caseria\n\n"
            "\U0001d456\U0001d463. \U0001d401\U0001d40e\U0001d419  \u2192  /box  /start_box\n\n"
            "\U0001d463. \U0001d402\U0001d407\U0001d41a\U0001d42b\U0001d41a\U0001d41d\U0001d41a  \u2192  /charada  /start_charada\n\n"
            "\U0001d463\U0001d456. \U0001d40f\U0001d408\U0001d42b\U0001d41a\U0001d42b\U0001d41a  \u2192  /pirata  /start_pirata\n\n"
            "\U0001d463\U0001d456\U0001d456. \U0001d400\U0001d41d\U0001d408\U0001d419\U0001d40e\U0001d40d\U0001d41a  \u2192  /adivina  /start_adivina\n\n"
            "Robux \U0001f7e5  \u2192  /new_session  /wallet  /spent  /reset\n\n"
            "Antes de iniciar una ronda nueva, usa /off_van para resetear."
        )
    )

# =====================================================================
# HANDLER PRINCIPAL DE BOTONES (despacha a cada juego)
# =====================================================================
# manejar_botones ya viene de bot_juegos.py y maneja todos los callbacks
# existentes. Solo agregamos el de adivina aquí abajo.

async def manejar_botones_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data if query else ""

    if data == "unirme_adivina_click":
        await manejar_boton_unirse_adivina(update, context)
    elif data.startswith("mu_"):
        await verificar_respuesta_musica(update, context)
    else:
        await manejar_botones(update, context)

# =====================================================================
# ARRANQUE
# =====================================================================

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"\U0001f310 Servidor Flask escuchando en el puerto {port}...")
    app_web.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    token_bot = os.environ.get('TOKEN')
    if not token_bot:
        raise ValueError("\u274c \u00a1Error cr\u00edtico! No se encontr\u00f3 la variable 'TOKEN' en el panel de Render.")

    print("\U0001f916 Iniciando bot de Telegram con run_polling...")
    application = ApplicationBuilder().token(token_bot).build()

    # ── Comandos generales ──
    application.add_handler(CommandHandler("start",   start_bienvenida, filters=PREFIX))
    application.add_handler(CommandHandler("info",    info,             filters=PREFIX))
    application.add_handler(CommandHandler("cmds",    comandos,         filters=PREFIX))
    application.add_handler(CommandHandler("off_van", detener_juegos,   filters=PREFIX))

    # ── Cipher ──
    application.add_handler(CommandHandler("cipher",       unirse_cipher,  filters=PREFIX))
    application.add_handler(CommandHandler("start_cipher", iniciar_cipher, filters=PREFIX))

    # ── Zombie ──
    application.add_handler(CommandHandler("zombie",       unirse_zombie,  filters=PREFIX))
    application.add_handler(CommandHandler("start_zombie", iniciar_zombie, filters=PREFIX))

    # ── Casería ──
    application.add_handler(CommandHandler("caseria",       unirse_caseria,  filters=PREFIX))
    application.add_handler(CommandHandler("start_caseria", iniciar_caseria, filters=PREFIX))

    # ── Box ──
    application.add_handler(CommandHandler("box",       unirse_box,  filters=PREFIX))
    application.add_handler(CommandHandler("start_box", iniciar_box, filters=PREFIX))

    # ── Charada ──
    application.add_handler(CommandHandler("charada",       unirse_charada,  filters=PREFIX))
    application.add_handler(CommandHandler("start_charada", iniciar_charada, filters=PREFIX))

    # ── Pirata ──
    application.add_handler(CommandHandler("pirata",       unirse_pirata,  filters=PREFIX))
    application.add_handler(CommandHandler("start_pirata", iniciar_pirata, filters=PREFIX))

    # ── Adivina la canción ──
    application.add_handler(CommandHandler("adivina",       unirse_adivina,      filters=PREFIX))
    application.add_handler(CommandHandler("start_adivina", iniciar_adivina_juego, filters=PREFIX))

    # ── Robux / Wallet ──
    application.add_handler(CommandHandler("new_session", cmd_new_session, filters=PREFIX))
    application.add_handler(CommandHandler("wallet",      cmd_wallet,      filters=PREFIX))
    application.add_handler(CommandHandler("spent",       cmd_spent,       filters=PREFIX))
    application.add_handler(CommandHandler("reset",       cmd_reset,       filters=PREFIX))

    # ── Handlers generales ──
    application.add_handler(CallbackQueryHandler(manejar_botones_main))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    application.run_polling(drop_pending_updates=True)
