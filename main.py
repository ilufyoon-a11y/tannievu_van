# main.py — Punto de entrada del bot Van 🤖

import os
import threading
import asyncio

from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
)

# ── Utilidades compartidas ──────────────────────────────────────────
from utils import (
    GIF_BIENVENIDA, GIF_INFO, GIF_COMANDOS,
    sesion_puntos, nombre_usuario,
    cmd_new_session, cmd_wallet, cmd_spent, cmd_reset,
    detener_juegos,
)

# ── Juegos ──────────────────────────────────────────────────────────
from zombie import (
    unirse_zombie, iniciar_zombie,
    manejar_botones_zombie,
)
from caseria import (
    unirse_caseria, iniciar_caseria,
    manejar_botones_caseria,
)
from box import (
    unirse_box, iniciar_box,
    manejar_botones_box,
    manejar_mensajes_box, adivinar_box,
    sesion_box, esperando_elementos,
    extraer_emojis,
)
from charada import (
    unirse_charada, iniciar_charada,
    manejar_botones_charada,
    escuchar_charada_privado, escuchar_charada_grupo,
    sesion_charada,
)
from pirata import (
    unirse_pirata, iniciar_pirata,
    manejar_botones_pirata,
)
from guessong import (
    unirse_adivina, iniciar_adivina_juego,
    verificar_respuesta_musica, manejar_boton_unirse,
)
from mayoromenor import (
    cmd_mayoromenor, cmd_beat, cmd_out_card,
    sesion_mom,
)
from carrera import (
    cmd_carrera, cmd_apostar_carrera,
    cmd_start_carrera, cmd_cancelar_carrera,
)
from anagrama import (
    cmd_anagrama, cmd_anagrama4, cmd_start_anagrama,
    manejar_botones_anagrama,
    escuchar_anagrama_privado, escuchar_anagrama_grupo,
    sesion_anagrama,
)
from slots import cmd_slots, cmd_open_slots, cmd_spin, sesion_slots

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
            "\n\n🌸ㅤㅤ⪩⪩ㅤㅤ𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝@ㅤㅤ!!ㅤㅤ☆ \n\n"
            "𝖵𝖺𝗇 𝖾𝗌 𝗎𝗇 𝖻𝗈𝗍 𝗊𝗎𝖾 𝗈𝖿𝗋𝖾𝖼𝖾 𝗎𝗇𝖺 𝗏𝖺𝗋𝗂𝖾𝖽𝖺𝖽 𝖽𝖾 𝗃𝗎𝖾𝗀𝗈𝗌, 𝖺𝗎𝗇 𝖾𝗌𝗍𝖺 𝖾𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗈 𝖽𝖾 𝗉𝗋𝗎𝖾𝖻𝖺 "
            "𝖺𝗌𝗂 𝗊𝗎𝖾 𝗌𝗂𝖾𝗇𝗍𝖾𝗍𝖾 𝖾𝗇 𝗍𝗈𝗍𝖺𝗅 𝗅𝗂𝖻𝖾𝗋𝗍𝖺𝖽 𝖽𝖾 𝖼𝗈𝗆𝗎𝗇𝗂𝖼𝖺𝗋 𝖼𝗎𝖺𝗅𝗊𝗎𝗂𝖾𝗋 𝗊𝗎𝖾𝗃𝖺/𝗌𝗎𝗀𝖾𝗋𝖾𝗇𝖼𝗂𝖺 𝖾𝗇 𝖾𝗅 𝖼𝗁𝖺𝗍 𝖽𝖾𝗅 𝖼𝖺𝗇𝖺𝗅. \n\n"
            "𝖤𝗌𝗉𝖾𝗋𝖺𝗆𝗈𝗌 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗃𝗎𝖾𝗀𝗈𝗌 𝖼𝗈𝗇𝗍𝖾𝗇𝗂𝖽𝗈𝗌 𝗌𝖾𝖺𝗇 𝖽𝖾 𝗌𝗎 𝖺𝗀𝗋𝖺𝖽𝗈! 💕"
        )
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_INFO,
        caption=("🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦     ꒱꒱\n\n"
                 "𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞\n\n"
                 "𝖴𝗇𝖺 𝖾𝗑𝖼𝗎𝗋𝗌𝗂𝗈́𝗇 𝗌𝖾 𝗏𝗂𝗈 𝗂𝗇𝗍𝖾𝗋𝗋𝗎𝗆𝗉𝗂𝖽𝖺 𝗉𝗈𝗋 𝗎𝗇 𝗏𝗂𝗋𝗎𝗌 𝗓𝗈𝗆𝖻𝗂𝖾. ¿𝖯𝗈𝖽𝗋𝖺́𝗇 𝗌𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝗋?\n\n"
                 "𝒊𝒊. 𝐂𝐚𝐬𝐞𝐫í𝐚\n\n"
                 "𝖤𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝗅𝗈𝗌 𝖾𝗆𝗈𝗃𝗂𝗌 𝗈𝖼𝗎𝗅𝗍𝗈𝗌 𝖾𝗇 𝖾𝗅 𝗍𝖺𝖻𝗅𝖾𝗋𝗈.\n\n"
                 "𝒊𝒗. 𝐁𝐨𝐱\n\n"
                 "𝖬𝖾𝗆𝗈𝗋𝗂𝗓𝖺 𝗅𝗈𝗌 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝖽𝖾𝗌𝖺𝗉𝖺𝗋𝖾𝗓𝖼𝖺𝗇.\n\n"
                 "𝒗. 𝐂𝐡𝐚𝐫𝐚𝐝𝐚\n\n"
                 "𝖣𝗈𝗌 𝖾𝗊𝗎𝗂𝗉𝗈𝗌 𝗌𝖾 𝖾𝗇𝖿𝗋𝖾𝗇𝗍𝖺𝗇 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗇𝖽𝗈 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝖼𝗈𝗇 𝗆𝗂́𝗆𝗂𝖼𝖺𝗌 𝗒 𝖾𝗆𝗈𝗃𝗂𝗌.\n\n"
                 "𝒗𝒊. 𝐏𝐢𝐫𝐚𝐭𝐚\n\n"
                 "𝖢𝗅𝖺𝗏𝖺 𝗅𝖺 𝖾𝗌𝗉𝖺𝖽𝖺 𝖾𝗇 𝗅𝖺 𝗋𝖺𝗇𝗎𝗋𝖺 𝖼𝗈𝗋𝗋𝖾𝖼𝗍𝖺, ¡𝗉𝖾𝗋𝗈 𝖼𝗎𝗂𝖽𝖺𝖽𝗈 𝖼𝗈𝗇 𝗅𝖺 𝗍𝗋𝖺𝗆𝗉𝖺!\n\n"
                 "𝒗𝒊𝒊. 𝐀𝐝𝐢𝐯𝐢𝐧𝐚 𝐥𝐚 𝐜𝐚𝐧𝐜𝐢ó𝐧\n\n"
                 "𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗅𝖺 𝖼𝖺𝗇𝖼𝗂𝗈́𝗇 𝖽𝖾 𝖪-𝖯𝗈𝗉 𝖾𝗇 𝗌𝗈𝗅𝗈 𝟦 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌. 🎧")
    )

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_COMANDOS,
        caption=("🎡  𖹭𖹭 ㅤ𝗖𝗼𝗺𝗮𝗻𝗱𝗼𝘀 𝗱𝗶𝘀𝗽𝗼𝗻𝗶𝗯𝗹𝗲𝘀  ꒱꒱\n\n"
                 "𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞  →  /zombie  /start_zombie\n\n"
                 "𝒊𝒊𝒊. 𝐂𝐚𝐬𝐞𝐫í𝐚  →  /caseria  /start_caseria\n\n"
                 "𝒊𝒗. 𝐁𝐨𝐱  →  /box  /start_box\n\n"
                 "𝒗. 𝐂𝐡𝐚𝐫𝐚𝐝𝐚  →  /charada  /start_charada\n\n"
                 "𝒗𝒊. 𝐏𝐢𝐫𝐚𝐭𝐚  →  /pirata  /start_pirata\n\n"
                 "𝒗𝒊𝒊. 𝐀𝐝𝐢𝐯𝐢𝐧𝐚  →  /adivina  /start_adivina\n\n"
                 "💰 Robux  →  /new_session  /wallet  /spent  /reset\n\n"
                 "𝖯𝗋𝖾𝗆𝗂𝗈𝗌 𝖺𝗅 𝗂𝗇𝗂𝖼𝗂𝖺𝗋:\n"
                 "`.start_zombie 5 15` → 5 vivos / 15 zombie\n"
                 "`.start_caseria 10` → 10 al ganador\n"
                 "`.start_box 6` → 6 al ganador\n"
                 "`.start_pirata 5` → 5 a los sobrevivientes\n"
                 "`.start_charada 10` → 10 al equipo ganador\n"
                 "`.start_adivina 5` → 5 por canción acertada\n\n"
                 "𝖠𝗇𝗍𝖾𝗌 𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝗇𝗎𝖾𝗏𝖺, 𝗎𝗌𝖺 /off_van 𝗉𝖺𝗋𝖺 𝗋𝖾𝗌𝖾𝗍𝖾𝖺𝗋.")
    )

# =====================================================================
# HANDLER DE MENSAJES — despacha según el contexto activo
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

    # ── PRIVADO: encubridor box envía emojis ──
    if chat_type == "private" and user_id in esperando_elementos:
        await manejar_mensajes_box(update, context)
        return

    # ── PRIVADO: moderador charada envía nombre de equipo ──
    if chat_type == "private":
        await escuchar_charada_privado(update, context, user_id, texto)
        await escuchar_anagrama_privado(update, context, user_id, texto)
        return

    # ── BOX: adivinar emojis en el grupo ──
    if chat_id in sesion_box and sesion_box[chat_id].get("activa"):
        await adivinar_box(update, context)
        return

    # ── CHARADA: adivinar palabras en el grupo ──
    await escuchar_charada_grupo(update, context, user_id, texto, chat_id)
    await escuchar_anagrama_grupo(update, context, user_id, texto, chat_id)

# =====================================================================
# HANDLER DE BOTONES — despacha según callback_data
# =====================================================================

async def manejar_botones_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data if query else ""

    if data in ("unirme_zombie_click",) or data.startswith("morder:") or data.startswith("voto_z:"):
        await manejar_botones_zombie(update, context)
    elif data == "unirme_caseria_click" or data.startswith("caseria_tablero_"):
        await manejar_botones_caseria(update, context)
    elif data == "unirme_box_click":
        await manejar_botones_box(update, context)
    elif data == "unirme_charada_click":
        await manejar_botones_charada(update, context)
    elif data == "unirme_pirata_click" or data.startswith("pirata_clic_") or data.startswith("ranura_ya_usada_"):
        await manejar_botones_pirata(update, context)
    elif data == "unirme_adivina_click":
        await manejar_boton_unirse(update, context)
    elif data.startswith("mu_"):
        await verificar_respuesta_musica(update, context)
    elif data == "unirme_anagrama_click":
        await manejar_botones_anagrama(update, context)

# =====================================================================
# ARRANQUE
# =====================================================================

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Servidor Flask escuchando en el puerto {port}...")
    app_web.run(host='0.0.0.0', port=port, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    token_bot = os.environ.get('TOKEN')
    if not token_bot:
        raise ValueError("❌ ¡Error crítico! No se encontró la variable 'TOKEN'.")

    print("🤖 Iniciando bot de Telegram con run_polling...")
    application = ApplicationBuilder().token(token_bot).build()

    # Comandos generales
    application.add_handler(CommandHandler("start",   start_bienvenida, filters=PREFIX))
    application.add_handler(CommandHandler("info",    info,             filters=PREFIX))
    application.add_handler(CommandHandler("cmds",    comandos,         filters=PREFIX))
    application.add_handler(CommandHandler("off_van", detener_juegos,   filters=PREFIX))

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

    # Adivina la canción
    application.add_handler(CommandHandler("adivina",       unirse_adivina,        filters=PREFIX))
    application.add_handler(CommandHandler("start_adivina", iniciar_adivina_juego, filters=PREFIX))

    # Mayor o Menor 🃏
    application.add_handler(CommandHandler("mayoromenor", cmd_mayoromenor, filters=PREFIX))
    application.add_handler(CommandHandler("beat",        cmd_beat,        filters=PREFIX))
    application.add_handler(CommandHandler("out_card",    cmd_out_card,    filters=PREFIX))

    # Slots 🎰
    application.add_handler(CommandHandler("open_slots", cmd_open_slots, filters=PREFIX))
    application.add_handler(CommandHandler("slots",      cmd_slots,      filters=PREFIX))
    application.add_handler(CommandHandler("spin",       cmd_spin,       filters=PREFIX))

    # Anagrama 🔀
    application.add_handler(CommandHandler("anagrama",       cmd_anagrama,       filters=PREFIX))
    application.add_handler(CommandHandler("anagrama4",      cmd_anagrama4,      filters=PREFIX))
    application.add_handler(CommandHandler("start_anagrama", cmd_start_anagrama, filters=PREFIX))
    application.add_handler(CommandHandler("carrera",          cmd_carrera,          filters=PREFIX))
    application.add_handler(CommandHandler("apostar_carrera",  cmd_apostar_carrera,  filters=PREFIX))
    application.add_handler(CommandHandler("start_carrera",    cmd_start_carrera,    filters=PREFIX))
    application.add_handler(CommandHandler("cancelar_carrera", cmd_cancelar_carrera, filters=PREFIX))

    # Robux / Wallet
    application.add_handler(CommandHandler("new_session", cmd_new_session, filters=PREFIX))
    application.add_handler(CommandHandler("wallet",      cmd_wallet,      filters=PREFIX))
    application.add_handler(CommandHandler("spent",       cmd_spent,       filters=PREFIX))
    application.add_handler(CommandHandler("reset",       cmd_reset,       filters=PREFIX))

    # Handlers generales
    application.add_handler(CallbackQueryHandler(manejar_botones_main))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    application.run_polling(drop_pending_updates=True)
