import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, extraer_emojis, GIF_JITB, GIF_ERROR, GIF_ENCUBRIDOR, GIF_RECHAZADO

# ================= DICCIONARIO =================

sesion_box = {}
esperando_elementos = {}   # user_id -> chat_id

EMOJIS_PROHIBIDOS = {"🎳", "🎰", "🏀", "⚽", "🎲"}

ERRORES_PROHIBIDOS = [
    "𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗎𝗇𝗈 𝖽𝖾 𝖾𝗌𝗈𝗌 𝖾𝗆𝗈𝗃𝗂𝗌 𝗇𝗈 𝗉𝗈𝖽𝗋𝖺 𝗌𝖾𝗋 𝖽𝖾𝗍𝖾𝖼𝗍𝖺𝖽𝗈 𝖼𝗈𝗆𝗈 𝗋𝖾𝗌𝗉𝗎𝖾𝗌𝗍𝖺; 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝗎𝖾𝖻𝖺 𝖼𝗈𝗇 𝗈𝗍𝗋𝗈."
]

# ================= CODIGO PRINCIPAL =================

async def unirse_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sesion_box:
        sesion_box[chat_id] = {"jugadores": [], "activa": False}
    else:
        sesion_box[chat_id]["activa"] = False
        sesion_box[chat_id]["jugadores"] = []
        sesion_box[chat_id].pop("ultimo_encubridor_id", None)

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_box_click")
    await update.message.reply_photo(
        photo=GIF_JITB,
        caption="<b>๑ ꞈ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 ¿𝖰𝗎𝖾 𝗁𝖺𝗒 𝖾𝗇 𝗅𝖺 𝖼𝖺𝗃𝖺?! ⋆ ٠</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_box &lt;f s t&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id not in sesion_box:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /𝖻𝗈𝗑 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ")
        return

    if len(sesion_box[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0xCcWpKcoeEBYZYhxHjkhqbGntnlJzXAAJhBgACiPVIRbbKF2KzkH0nPAQ")
        return

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["box_1"] = int(args[0]) if len(args) > 0 else 0
        sesion_puntos["premio_actual"]["box_2"] = int(args[1]) if len(args) > 1 else 0
        sesion_puntos["premio_actual"]["box_3"] = int(args[2]) if len(args) > 2 else 0
        
    except ValueError:
        pass


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
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Ꜥ ¡{encubridor['name']} 𝖿𝗎𝖾 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝖼𝗈𝗆𝗈 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋! ⸝⸝\n\n𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝖺 𝗊𝗎𝖾 𝖺𝗌𝗂𝗀𝗇𝖾 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌.  .  .",
    )
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA1QAAaRqUwu5n3oGAo9Cs_xd1rPRRobkzAACgwYAAtz6uUQbnfNeh5189TwE"
        )
        
    try:    
        await context.bot.send_message(
            chat_id=encubridor["id"],
            text="<b>¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋!</b>\n\n𝖤𝗇𝗏𝗂𝖺 𝖾𝗑𝖺𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝟩 𝖾𝗆𝗈𝗃𝗂𝗌 𝗌𝗂𝗇 𝖽𝖾𝗃𝖺𝗋 𝖾𝗌𝗉𝖺𝖼𝗂𝗈𝗌 (🌸🌟📰...); 𝖾𝗌𝗍𝗈𝗌 𝗌𝖾 𝗆𝗈𝗌𝗍𝗋𝖺𝗋𝖺𝗇 𝖻𝗋𝖾𝗏𝖾𝗆𝖾𝗇𝗍𝖾 𝖺 𝗅𝗈𝗌 𝗃𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌.\n\n<blockquote>𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗏𝗂𝗍𝖺 𝖾𝗇𝗏𝗂𝖺𝗋 𝗅𝗈𝗌 𝗌𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾𝗌 𝖾𝗆𝗈𝗃𝗂𝗌: 🎳, 🎰, 🏀, ⚽, 🎲.</blockquote>",
            parse_mode="HTML"
        )
    
        await context.bot.send_sticker(
            chat_id=encubridor["id"],
            sticker="CAACAgEAAxkBA0WkVGpCeFxv3hOINwnldaJhBC_FXDhhAAIbCQAC-nQYRn3vKswkIhekPAQ"
        )
        
    except Exception:
        await update.message.reply_text(f"ⓘ ˖ ࣪ 𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 {encubridor['name']}. \n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 ᵎᵎ")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA08s3mpNqQrISXcnzmYG_9fOSF9e-8cBAAKNBwAC7QJBRHEkAAHybHUSQDwE")
        return

# ================= MANEJO DE MENSAJES =================

async def manejar_mensajes_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Llama esto desde manejar_mensajes en main.py cuando chat_type == private y user_id in esperando_elementos"""
    user_id = update.effective_user.id
    texto = update.message.text.strip() if update.message.text else ""
    gid = esperando_elementos[user_id]

    emojis_originales = extraer_emojis(texto)
    if len(emojis_originales) != 7:
        await update.message.reply_text("ⓘ ¡𝖴𝗇 𝗆𝗈𝗆𝖾𝗇𝗍𝗈! 𝖤𝗌𝗈𝗌 𝗇𝗈 𝗌𝗈𝗇 𝟩 𝖾𝗆𝗈𝗃𝗂𝗌; 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗂𝗇𝗍𝖾𝗇𝗍𝖺𝗅𝗈 𝖽𝖾 𝗇𝗎𝖾𝗏𝗈.")
        return

    # Normalizar para comparación consistente
    emojis_originales = [normalizar_emoji(e) for e in emojis_originales]

    prohibidos_encontrados = [e for e in emojis_originales if e in EMOJIS_PROHIBIDOS]
    if prohibidos_encontrados:
        await update.message.reply_text(random.choice(ERRORES_PROHIBIDOS))
        return

    sesion_box[gid].update({
        "emojis_secretos": emojis_originales,
        "emojis_adivinados": [],
        "puntajes": {},
        "activa": True,
    })
    del esperando_elementos[user_id]
    await update.message.reply_text("¡𝖬𝗎𝖼𝗁𝖺𝗌 𝗀𝗋𝖺𝖼𝗂𝖺𝗌, 𝗅𝗈𝗌 𝟩 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌 𝗁𝖺𝗇 𝗌𝗂𝖽𝗈 𝗀𝗎𝖺𝗋𝖽𝖺𝖽𝗈𝗌!")
    lista_visual = " ".join(emojis_originales)
    mensaje_flash = await context.bot.send_message(chat_id=gid,
        text=f"¡𝗔𝗧𝗘𝗡𝗖𝗜𝗢𝗡, 𝗟𝗔 𝗖𝗔𝗝𝗔 𝗙𝗨𝗘 𝗔𝗕𝗜𝗘𝗥𝗧𝗔ⵑ\n\n¡𝖣𝖺𝗍𝖾 𝗉𝗋𝗂𝗌𝖺 𝗒 𝗆𝖾𝗆𝗈𝗋𝗂𝗓𝖺 𝗅𝗈𝗌 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈𝗌; 𝖽𝖾𝗌𝖺𝗉𝖺𝗋𝖾𝖼𝖾𝗋𝖺𝗇 𝖾𝗇 𝟣𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌!\n\n{lista_visual}")
    await asyncio.sleep(10)
    try:
        await context.bot.delete_message(chat_id=gid, message_id=mensaje_flash.message_id)
    except Exception:
        pass
    await context.bot.send_message(chat_id=gid,
        text="¡𝗟𝗔 𝗖𝗔𝗝𝗔 𝗙𝗨𝗘 𝗖𝗘𝗥𝗥𝗔𝗗𝗔ⵑ\n\n𝖤𝗇𝗏𝗂𝖺 𝗍𝗎𝗌 𝗋𝖾𝗌𝗉𝗎𝖾𝗌𝗍𝖺𝗌 𝗎𝗇𝖺 𝗉𝗈𝗋 𝗎𝗇𝖺. 𝖲𝗂 𝖼𝗈𝗂𝗇𝖼𝗂𝖽𝖾𝗇 𝖼𝗈𝗇 𝗎𝗇 𝖾𝗅𝖾𝗆𝖾𝗇𝗍𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗌𝗂𝗅𝗅𝖺, ¡𝗀𝖺𝗇𝖺𝗌 𝟣 𝗉𝗎𝗇𝗍𝗈!")

def normalizar_emoji(e: str) -> str:
    """Normaliza un emoji removiendo variantes de presentación."""
    return e.replace('\uFE0F', '').replace('\u200D', '').strip()

async def adivinar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Llama esto desde manejar_mensajes cuando hay sesion_box activa en el grupo"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = nombre_usuario(update.effective_user)
    texto = update.message.text.strip() if update.message.text else ""

    sesion = sesion_box[chat_id]
    # Advertencia si el encubridor intenta adivinar
    if user_id == sesion.get("encubridor_id"):
        await update.message.reply_text("¡𝖧𝖾𝗒, 𝗍𝗎 𝖾𝗋𝖾𝗌 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝗃𝗎𝗀𝖺𝗋!")
        return

    emojis_enviados = extraer_emojis(texto)
    if not emojis_enviados:
        return

    emoji_enviado = normalizar_emoji(emojis_enviados[0])
    secretos_normalizados = [normalizar_emoji(e) for e in sesion.get("emojis_secretos", [])]
    adivinados_normalizados = [normalizar_emoji(e) for e in sesion.get("emojis_adivinados", [])]

    if emoji_enviado in EMOJIS_PROHIBIDOS:
        await update.message.reply_text(random.choice(ERRORES_PROHIBIDOS))
        return

    if emoji_enviado in adivinados_normalizados:
        await update.message.reply_text("¡𝖴𝗉𝗌, 𝖾𝗌𝖾 𝗈𝖻𝗃𝖾𝗍𝗈 𝗒𝖺 𝖿𝗎𝖾 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈!")
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
        f"¡𝖯𝗎𝗇𝗍𝗈 𝗉𝖺𝗋𝖺 {user_name}, 𝖾𝗌𝖾 𝖺𝗋𝗍ı́𝖼𝗎𝗅𝗈 𝗌𝗂 𝖾𝗌𝗍𝖺𝖻𝖺 𝖾𝗇 𝗅𝖺 𝖼𝖺𝗃𝖺!\n\n"
        f"𝖫𝗅𝖾𝗏𝖺𝗆𝗈𝗌 [{total}/𝟩] 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈𝗌.")

    if total == 6:
        sesion["activa"] = False
        tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
        medallas = ["🥇", "🥈", "🥉"]
        msg = "¡𝖲𝖾 𝗁𝖺𝗇 𝖽𝖾𝗌𝖼𝗎𝖻𝗂𝖾𝗋𝗍𝗈 𝗍𝗈𝖽𝗈𝗌 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌!\n\nっ⠀˖⠀꒰⠀𝗣𝗨𝗡𝗧𝗨𝗔𝗖𝗜𝗢𝗡 𝗙𝗜𝗡𝗔𝗟⠀꒱\n\n"
        premios_box = [
            sesion_puntos.get("premio_actual", {}).get("box_1", 0),
            sesion_puntos.get("premio_actual", {}).get("box_2", 0),
            sesion_puntos.get("premio_actual", {}).get("box_3", 0),
        ]
        for i, (uid_b, pts) in enumerate(tabla):
            jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_b), None)
            nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_b}"
            dec = medallas[i] if i < 3 else "🔹"
            robux_p = premios_box[i] if i < 3 else 0
            extra = f" ➜ {robux_p} 𝗋𝗈𝖻𝗎𝗑" if robux_p else ""
            msg += f"{dec} — {nombre_p}: {pts} 𝗉𝗍(𝗌)\n"
            if robux_p and jugador_obj:
                sumar_robux(jugador_obj["id"], jugador_obj["name"], robux_p, f"𝗣𝘂𝗲𝘀𝘁𝗼 - 𝗯𝗼𝘅 {i+1}")
        await context.bot.send_message(chat_id=chat_id, text=msg)
        await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgEAAxkBA0Y1sWpDGFQQHzwJSrB9YNUygD0j8YEuAAI5BgACxL5BRIsEuKAHC3RbPAQ")

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
            await query.answer("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈! ᵎᵎ", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_box[chat_id]["jugadores"]):
            sesion_box[chat_id]["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
            await query.message.reply_text(f"— {nombre_usuario(user)} se unio 𝅄 𖹭' ა")
