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
    "Lo siento, ese emoji no podrɑ ser detectɑdo como respuestɑ, por fɑvor, pruebɑ con otro"
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
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ ¿Que hɑy en lɑ cɑjɑ?!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_box &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["box_1"] = int(args[0]) if len(args) > 0 else 0
        sesion_puntos["premio_actual"]["box_2"] = int(args[1]) if len(args) > 1 else 0
        sesion_puntos["premio_actual"]["box_3"] = int(args[2]) if len(args) > 2 else 0
        
    except ValueError:
        pass

    if chat_id not in sesion_box or len(sesion_box[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personɑs pɑrɑ jugɑr.")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
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
    await update..bot.send_message(
        chat_id=chat_id,
        text=f"˒˓  ¡{encubridor['name']} fue elegido como encubridor! Esperɑndo ɑ que se ɑsignen los objetos  ᨦᨩ",
        parse_mode="Markdown"
    )
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjCWpC_HERlalQGI7HXrVJOdOI2sDJAAIZCQAC36pAROiuTUHK1uCmPAQ"
        )
        
    try:    
        await context.bot.send_message(
            chat_id=encubridor["id"],
            text="<b> ¡En horɑ buenɑ, te tocɑ ser el encubridor!</b>\n\n Enviɑ exɑctɑmente 6 emojis sin espɑcios (🌸🌟📰...); se mostrɑrɑn brevemente ɑ los jugɑdores.\n\n<blockquote> Por fɑvor, evitɑ enviɑr los siguientes emojis: 🎳, 🎰, 🏀, ⚽, 🎲.</blockquote>",
            parse_mode="HTML"
        )
    
        await context.bot.send_sticker(
            chat_id=encubridor["id"],
            sticker="CAACAgEAAxkBA0WkVGpCeFxv3hOINwnldaJhBC_FXDhhAAIbCQAC-nQYRn3vKswkIhekPAQ"
        )
        
    except Exception:
        await update.message.reply_text(f"𝖠y, no se puede enviɑr un mensɑje ɑ {encubridor(user)}. Por fɑvor, ɑsegurɑte de hɑber iniciɑdo el bot.")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

# ================= MANEJO DE MENSAJES =================

async def manejar_mensajes_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Llama esto desde manejar_mensajes en main.py cuando chat_type == private y user_id in esperando_elementos"""
    user_id = update.effective_user.id
    texto = update.message.text.strip() if update.message.text else ""
    gid = esperando_elementos[user_id]

    emojis_originales = extraer_emojis(texto)
    if len(emojis_originales) != 6:
        await update.message.reply_text("¡Un momento! Esos no son 6 emojis; por fɑvor, enviɑlos de nuevo.")
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
    await update.message.reply_text("¡Muchɑs grɑciɑs, los 6 elementos hɑn sido guɑrdɑdos!")
    lista_visual = " ".join(emojis_originales)
    mensaje_flash = await context.bot.send_message(chat_id=gid,
        text=f"¡𝐋𝐀 𝐂𝐀𝐉𝐀 𝐒𝐄𝐑𝐀 𝐀𝐁𝐈𝐄𝐑𝐓𝐀ⵑ\n¡Dɑte prisɑ y memorizɑ los elementos; desɑpɑrecerɑ́n en 5 segundos:\n{lista_visual}!")
    await asyncio.sleep(5)
    try:
        await context.bot.delete_message(chat_id=gid, message_id=mensaje_flash.message_id)
    except Exception:
        pass
    await context.bot.send_message(chat_id=gid,
        text="¡𝐋𝐀 𝐂𝐀𝐉𝐀 𝐅𝐔𝐄 𝐂𝐄𝐑𝐑𝐀𝐃𝐀ⵑ\nEnviɑ tus respuestɑs unɑ por unɑ. Si coinciden con ɑlgun elemento de lɑ cɑjɑ, ¡gɑnɑs 1 punto!")

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
        await update.message.reply_text("¡Ups, ese objeto yɑ fue descubierto!")
        return
    if emoji_enviado not in secretos_normalizados:
        await update.message.reply_text("¡Ese objeto no estɑbɑ dentro de lɑ cɑjɑ!")
        return

    indice = secretos_normalizados.index(emoji_enviado)
    emoji_original = sesion["emojis_secretos"][indice]
    sesion["emojis_adivinados"].append(emoji_original)
    sesion["puntajes"][user_id] = sesion["puntajes"].get(user_id, 0) + 1
    total = len(sesion["emojis_adivinados"])

    await update.message.reply_text(
        f"¡Punto pɑrɑ {user_name}, ese objeto si estɑbɑ en lɑ cɑjɑ!\n\n"
        f"Llevɑmos [{total}/6] objetos descubiertos.")

    if total == 6:
        sesion["activa"] = False
        tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
        medallas = ["🥇", "🥈", "🥉"]
        msg = "¡𝐑𝐎𝐍𝐃𝐀 𝐅𝐈𝐍𝐀𝐋𝐈𝐙𝐀𝐃𝐀ⵑ Se descubrieron todos los objetos.\n\n𝗣𝘂𝗻𝘁𝘂𝗮𝗰𝗶𝗼𝗻 𝗳𝗶𝗻𝗮𝗹:\n\n"
        premios_box = [
            sesion_puntos.get("premio_actual", {}).get("box_1", 0),
            sesion_puntos.get("premio_actual", {}).get("box_2", 0),
            sesion_puntos.get("premio_actual", {}).get("box_3", 0),
        ]
        for i, (uid_b, pts) in enumerate(tabla):
            jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_b), None)
            nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_b}"
            robux_p = premios_box[i] if i < 3 else 0
            extra = f" — +{robux_p} fichɑs" if robux_p else ""
            msg += f"{dec} {nombre_p}: {pts} pt(s){extra}\n"
            if robux_p and jugador_obj:
                sumar_robux(jugador_obj["id"], jugador_obj["name"], robux_p, f"𝗣𝘂𝗲𝘀𝘁𝗼: {i+1} 📦")
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
            await query.answer("¡Lo siento, yɑ hɑy unɑ pɑrtidɑ en curso!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_box[chat_id]["jugadores"]):
            sesion_box[chat_id]["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
            await query.message.reply_text(f"📦  {nombre_usuario(user)} se unio 𓂃")
