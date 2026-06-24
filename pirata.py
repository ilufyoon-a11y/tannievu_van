import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_PIRATA, GIF_ERROR

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
    sesion_pirata["agujerofake"] = random.randint(1, 20)

    await context.bot.send_message(chat_id=chat_id,
        text="🏴‍☠️ **¡LA RULETA DEL PIRATA COMIENZA!**\n\n"
             "Hay 20 ranuras. Una tiene trampa 💀 Las demás son seguras. ¡Clava tu espada con cuidado!\n\n"
             f"El turno es de **{next(j['name'] for j in sesion_pirata['jugadores'] if j['id'] == sesion_pirata['sobrevivientes'][0])}**",
        parse_mode="Markdown")

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

    botones = [todos_los_botones[i:i+4] for i in range(0, len(todos_los_botones), 4)]

    await context.bot.send_message(chat_id=chat_id,
        text=f"🗡️ Turno de **{nombre_actual}** — ¡elige una ranura!",
        reply_markup=InlineKeyboardMarkup(botones),
        parse_mode="Markdown")

# ================= MANEJO DE BOTONES (CallbackQuery) =================

async def manejar_botones_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat.id

    if query.data == "unirme_pirata_click":
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
            premio_p = sesion_puntos.get("premio_actual", {}).get("pirata", 0)
            if premio_p:
                for uid_p in sesion_pirata["sobrevivientes"]:
                    if uid_p != autor_id:
                        nom_p = next((j["name"] for j in sesion_pirata["jugadores"] if j["id"] == uid_p), f"ID{uid_p}")
                        sumar_robux(uid_p, nom_p, premio_p, "Pirata sobreviviente 🏴‍☠️")
            extra_p = f"\n+{premio_p} Robux 🟥 c/u" if premio_p else ""
            await context.bot.send_message(chat_id=chat_id,
                text=f"💥 ¡¡ZAZZZ!! 🚀\n\n**{nombre_usuario(user)}** metió la espada en la ranura {num_ranura}... ¡Y EL PIRATA SALTÓ! 💀\n\n"
                     f"🏆 **¡GANADORES!:** {texto_ganadores}{extra_p}",
                parse_mode="Markdown")
        else:
            sesion_pirata["agujerosave"].append(num_ranura)
            await context.bot.send_message(chat_id=chat_id,
                text=f"🗡️ ¡*Click*! Ranura {num_ranura} a salvo. **{nombre_usuario(user)}** sobrevivió. 😮‍💨",
                parse_mode="Markdown")
            sesion_pirata["turno_actual"] = (sesion_pirata["turno_actual"] + 1) % len(sesion_pirata["sobrevivientes"])
            await enviar_turno_pirata(chat_id, context)

    elif query.data.startswith("ranura_ya_usada_"):
        await query.answer("¡Esa ranura ya tiene una espada clavada, busca otra! 🗡️", show_alert=True)
