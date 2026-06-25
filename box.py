import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, extraer_emojis, GIF_JITB, GIF_ERROR, GIF_ENCUBRIDOR, GIF_RECHAZADO

# ================= DICCIONARIO =================

sesion_box = {}
esperando_elementos = {}   # user_id -> chat_id

# ================= CODIGO PRINCIPAL =================

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

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["box"] = int(args[0])
        except ValueError:
            pass

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

# ================= MANEJO DE MENSAJES =================

async def manejar_mensajes_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Llama esto desde manejar_mensajes en main.py cuando chat_type == private y user_id in esperando_elementos"""
    user_id = update.effective_user.id
    texto = update.message.text.strip() if update.message.text else ""
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

async def adivinar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Llama esto desde manejar_mensajes cuando hay sesion_box activa en el grupo"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = nombre_usuario(update.effective_user)
    texto = update.message.text.strip() if update.message.text else ""

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
        premio_box = sesion_puntos.get("premio_actual", {}).get("box", 0)
        for i, (uid_b, pts) in enumerate(tabla):
            jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_b), None)
            nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_b}"
            dec = medallas[i] if i < 3 else "🔹"
            msg += f"{dec} {nombre_p}: {pts} pt(s)\n"
        if tabla and premio_box:
            gan = next((j for j in sesion["jugadores"] if j["id"] == tabla[0][0]), None)
            if gan:
                sumar_robux(gan["id"], gan["name"], premio_box, "Box 📦")
                msg += f"\n+{premio_box} Robux 🟥 para {gan['name']}"
        await context.bot.send_message(chat_id=chat_id, text=msg)

# ================= MANEJO DE BOTONES =================

async def manejar_botones_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_box_click":
        await query.answer()
        if chat_id not in sesion_box:
            sesion_box[chat_id] = {"jugadores": [], "activa": False}
        if sesion_box[chat_id]["activa"]:
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_box[chat_id]["jugadores"]):
            sesion_box[chat_id]["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
            await query.message.reply_text(f"📦  {nombre_usuario(user)} se unió 𓂃")
