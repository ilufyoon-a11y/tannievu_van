import random
import os
import asyncio
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario

# ================= DICCIONARIO =================

sesion_pirata = {
    "jugadores": [],
    "activa": False,
    "sobrevivientes": [],
    "turno_actual": 0,
    "agujerofake": None,
    "agujerosave": [],
    "respondio_turno": False,
}

# ================= CODIGO PRINCIPAL =================

async def unirse_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_pirata["jugadores"] = []
    sesion_pirata["activa"] = False
    sesion_pirata["sobrevivientes"] = []
    sesion_pirata["turno_actual"] = 0
    sesion_pirata["agujerofake"] = None
    sesion_pirata["agujerosave"] = []
    sesion_pirata["respondio_turno"] = False

    # ===== DISEÑO QUE ACOMPAÑA EL BOTON =====
  
    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_pirata_click")
    await update.message.reply_photo(
        photo=GIF_PIRATA,
        caption="🏴‍☠️ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖯𝗂𝗋𝖺𝗍𝖺! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["pirata"] = int(args[0])
        except ValueError:
            pass

    if len(sesion_pirata["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    sesion_pirata["activa"] = True
    sesion_pirata["sobrevivientes"] = [j["id"] for j in sesion_pirata["jugadores"]]
    sesion_pirata["turno_actual"] = 0
    sesion_pirata["agujerosave"] = []
    sesion_pirata["agujerofake"] = random.randint(1, 5)

    await context.bot.send_message(chat_id=chat_id,
        text="🏴‍☠️ **¡LA RULETA DEL PIRATA COMIENZA!**\n\n"
             "Hay 20 ranuras. Una tiene trampa 💀 Las demás son seguras. ¡Clava tu espada con cuidado!\n\n"
             f"El turno es de **{next(j['name'] for j in sesion_pirata['jugadores'] if j['id'] == sesion_pirata['sobrevivientes'][0])}**")

    await enviar_turno_pirata(chat_id, context)

async def enviar_turno_pirata(chat_id, context):
    if sesion_pirata["turno_actual"] >= len(sesion_pirata["sobrevivientes"]):
        sesion_pirata["turno_actual"] = 0

    actual_id = sesion_pirata["sobrevivientes"][sesion_pirata["turno_actual"]]
    nombre_actual = next(j["name"] for j in sesion_pirata["jugadores"] if j["id"] == actual_id)

    todos_los_botones = [
        InlineKeyboardButton(
            "🗡️" if i in sesion_pirata["agujerosave"] else "🕳️",
            callback_data=f"ranura_ya_usada_{i}" if i in sesion_pirata["agujerosave"] else f"pirata_clic_{i}_{actual_id}"
        )
        for i in range(1, 21)
    ]

    botones = [todos_los_botones[i:i + 4] for i in range(0, len(todos_los_botones), 4)]

    await context.bot.send_message(chat_id=chat_id,
        text=f"🗡️ Turno de **{nombre_actual}** — ¡elige una ranura!",
        reply_markup=InlineKeyboardMarkup(botones))

# ================= CODIGO PRINCIPAL =================

