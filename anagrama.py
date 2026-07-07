import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_AHORCADO

# =====================================================================
# SESIONES
# =====================================================================

sesion_anagrama = {}   # chat_id -> {...}
esperando_moderador = {}   # user_id -> chat_id

STICKER_ERROR = "CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ"

def _sesion_base(creador_id: int, chat_id: int) -> dict:
    return {
        "activa": False,
        "fase_registro": True,
        "jugadores": [],
        "moderador_id": None,
        "creador_id": creador_id,
        "chat_id": chat_id,
        "categoria": None,
        "palabras": [],
        "adivinadas": set(),
        "esperando": None,
        "ronda_actual": 0,
        "total_rondas": 4,
        "puntos": {},
    }

# =====================================================================
# HELPERS
# =====================================================================

def revolver(palabra: str) -> str:
    """Revuelve cada palabra por separado, respetando los espacios."""
    def _mezclar(letras: list) -> list:
        original = list(letras)
        random.shuffle(letras)
        intentos = 0
        while letras == original and intentos < 20:
            random.shuffle(letras)
            intentos += 1
        return letras

    partes = palabra.upper().split()
    bloques = [" ".join(_mezclar(list(p))) for p in partes]
    return "  ".join(bloques)

def parsear_palabras(texto: str) -> list:
    import re
    partes = re.split(r'[,\-]', texto)
    return [p.strip().lower() for p in partes if p.strip()]

def _nombre_de(sesion: dict, user_id: int) -> str:
    jugador = next((j for j in sesion["jugadores"] if j["id"] == user_id), None)
    return jugador["name"] if jugador else f"ID {user_id}"

def reset_anagrama_chat(chat_id: int):
    """Apaga y limpia la partida de Anagrama de un chat puntual (usado por /off_van)."""
    sesion = sesion_anagrama.pop(chat_id, None)
    if sesion and sesion.get("moderador_id"):
        esperando_moderador.pop(sesion["moderador_id"], None)

# =====================================================================
# /jumble
# =====================================================================

async def cmd_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion_actual = sesion_anagrama.get(chat_id)

    if sesion_actual and (sesion_actual.get("activa") or sesion_actual.get("fase_registro")):
        await update.message.reply_text("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈 ᵎᵎ")
        return

    sesion_anagrama[chat_id] = _sesion_base(creador_id=update.effective_user.id, chat_id=chat_id)

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_anagrama_click")
    await update.message.reply_photo(
        photo=GIF_AHORCADO,
        caption="<b>๑ ꞈ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺𝗅 𝖣𝖾𝗌𝗈𝗋𝖽𝖾𝗇 𝖽𝖾 𝖫𝖾𝗍𝗋𝖺𝗌! ⋆ ٠</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_jumble &lt;premio&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

# Alias por si main.py llama a cmd_anagrama4
cmd_anagrama4 = cmd_anagrama

# =====================================================================
# /start_jumble
# =====================================================================

async def cmd_start_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_anagrama.get(chat_id)

    if not sesion or not sesion.get("fase_registro"):
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /jumble 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ")
        return

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["anagrama"] = premio

    sesion["fase_registro"] = False

    mod = random.choice(sesion["jugadores"])
    sesion["moderador_id"] = mod["id"]
    esperando_moderador[mod["id"]] = chat_id

    await update.message.reply_text(
        f"Ꜥ ¡{mod['name']} 𝖿𝗎𝖾 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝖼𝗈𝗆𝗈 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋! 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝖺 𝗊𝗎𝖾 𝖺𝗌𝗂𝗀𝗇𝖾 𝗅𝖺 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂𝖺 𝗒 𝗅𝖺𝗌 𝟦 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 ⸝⸝"
    )
    await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgEAAxkBA0YjCWpC_HERlalQGI7HXrVJOdOI2sDJAAIZCQAC36pAROiuTUHK1uCmPAQ"
    )

    sesion["esperando"] = "categoria"
    try:
        await context.bot.send_message(
            chat_id=mod["id"],
            text="<b>¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋!</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝗂𝗆𝖾𝗋𝗈, 𝖺𝗌𝗂𝗀𝗇𝖺 𝗅𝖺 <b>𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂𝖺</b> 𝖽𝖾 𝗅𝖺𝗌 𝟦 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌:",
            parse_mode="HTML"
        )
        
        await context.bot.send_sticker(
            chat_id=mod["id"],
            sticker="CAACAgEAAxkBA0WkVGpCeFxv3hOINwnldaJhBC_FXDhhAAIbCQAC-nQYRn3vKswkIhekPAQ"
        )
    
    except Exception:
        await update.message.reply_text(f"ⓘ ˖ ࣪ 𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 {mod['name']}. 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 ᵎᵎ")
        await update.message.reply_sticker(sticker=STICKER_ERROR)
        esperando_moderador.pop(mod["id"], None)
        sesion_anagrama.pop(chat_id, None)

# =====================================================================
# ESCUCHAR PRIVADO — moderador da categoría y palabras
# =====================================================================

async def escuchar_anagrama_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    chat_id = esperando_moderador.get(user_id)
    if chat_id is None:
        return

    sesion = sesion_anagrama.get(chat_id)
    if not sesion or user_id != sesion.get("moderador_id"):
        return
    if not texto:
        return

    # Esperando categoría
    if sesion["esperando"] == "categoria":
        sesion["categoria"] = texto
        sesion["esperando"] = "palabras"
        await update.message.reply_text(
            f"𝖢𝖠𝖳𝖤𝖦𝖮𝖱𝖨𝖠: <b>{texto}</b>\n\n𝖠𝗁𝗈𝗋𝖺, 𝖾𝗌𝖼𝗋𝗂𝖻𝖾 𝗅𝖺𝗌 <b>𝟦 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌</b>, 𝖼𝖺𝖽𝖺 𝗎𝗇𝖺 𝗌𝖾𝗉𝖺𝗋𝖺𝖽𝖺 𝗉𝗈𝗋 𝗎𝗇𝖺 𝖼𝗈𝗆𝖺:\n<blockquote>𝖤𝗃: 𝖯𝗂𝖾 𝖽𝖾 𝗅𝗂𝗆𝗈𝗇, 𝗉𝖺𝗌𝗍𝖾𝗅, 𝗁𝖾𝗅𝖺𝖽𝗈, 𝖼𝗁𝗎𝗋𝗋𝗈.</blockquote>",
            parse_mode="HTML"
        )
        return

    # Esperando palabras
    if sesion["esperando"] == "palabras":
        palabras = parsear_palabras(texto)
        if len(palabras) != 4:
            await update.message.reply_text(
                f"ⓘ ¡𝖴𝗇 𝗆𝗈𝗆𝖾𝗇𝗍𝗈! 𝖭𝖾𝖼𝖾𝗌𝗂𝗍𝗈 𝟦 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝗌𝖾𝗉𝖺𝗋𝖺𝖽𝖺𝗌 𝗉𝗈𝗋 𝗎𝗇𝖺 𝖼𝗈𝗆𝖺, 𝗍𝗎 𝗁𝖺𝗌 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝗈 {len(palabras)}. \n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗂𝗇𝗍𝖾𝗇𝗍𝖺𝗅𝗈 𝖽𝖾 𝗇𝗎𝖾𝗏𝗈.",
                parse_mode="HTML"
            )
            return

        sesion["palabras"] = palabras
        sesion["adivinadas"] = set()
        sesion["esperando"] = None
        sesion["activa"] = True
        esperando_moderador.pop(user_id, None)

        await update.message.reply_text("¡𝖬𝗎𝖼𝗁𝖺𝗌 𝗀𝗋𝖺𝖼𝗂𝖺𝗌, 𝗅𝖺𝗌 𝟦 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝗁𝖺𝗇 𝗌𝗂𝖽𝗈 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝖺𝗌!")

        revuelta = revolver(palabras[0])
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"<b>𐑺 ៸ 𝖱𝖮𝖭𝖣𝖠 1/4 — 𝖢𝖠𝖳𝖤𝖦𝖮𝖱𝖨𝖠: {sesion['categoria']} ◝ .</b>\n\n<code>{revuelta}</code>\n\n¡𝖠𝗉𝗋𝖾𝗌𝗎𝗋𝖺𝗍𝖾, 𝗈𝗋𝖽𝖾𝗇𝖺 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺!",
            parse_mode="HTML"
        )

# =====================================================================
# ESCUCHAR GRUPO — jugadores adivinan
# =====================================================================

async def escuchar_anagrama_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    sesion = sesion_anagrama.get(chat_id)
    if not sesion or not sesion.get("activa"):
        return
    if not texto:
        return

    # Advertencia si el moderador intenta adivinar
    if user_id == sesion["moderador_id"]:
        await update.message.reply_text("¡𝖧𝖾𝗒, 𝗍𝗎 𝖾𝗋𝖾𝗌 𝖾𝗅 𝖾𝗇𝖼𝗎𝖻𝗋𝗂𝖽𝗈𝗋, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝗃𝗎𝗀𝖺𝗋!")
        return

    if not any(j["id"] == user_id for j in sesion["jugadores"]):
        return

    texto_limpio = texto.lower().strip()
    palabras = sesion["palabras"]
    puntos = sesion["puntos"]
    adivinadas = sesion.get("adivinadas", set())
    nombre = _nombre_de(sesion, user_id)

    if texto_limpio in palabras and texto_limpio not in adivinadas:
        adivinadas.add(texto_limpio)
        sesion["adivinadas"] = adivinadas
        puntos[user_id] = puntos.get(user_id, 0) + 1
        sesion["ronda_actual"] += 1

        await update.message.reply_text(
            f"¡𝖯𝗎𝗇𝗍𝗈 𝗉𝖺𝗋𝖺 {nombre}, 𝖺𝖽𝗂𝗏𝗂𝗇𝗈 𝖼𝗈𝗋𝗋𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺!\n\n"
            f"𝖫𝗅𝖾𝗏𝖺𝗆𝗈𝗌 [{sesion['ronda_actual']}/{sesion['total_rondas']}] 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝗈𝗋𝖽𝖾𝗇𝖺𝖽𝖺𝗌!"
        )

        if sesion["ronda_actual"] >= sesion["total_rondas"]:
            sesion["activa"] = False
            await _fin_rondas(context, chat_id)
        else:
            siguiente = next(p for p in palabras if p not in adivinadas)
            ronda_num = sesion["ronda_actual"] + 1
            revuelta = revolver(siguiente)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"<b>𐑺 ៸ 𝖱𝖮𝖭𝖣𝖠 {ronda_num}/4 — 𝖢𝖠𝖳𝖤𝖦𝖮𝖱𝖨𝖠: {sesion['categoria']} ◝ .</b>\n\n<code>{revuelta}</code>\n\n¡𝖠𝗉𝗋𝖾𝗌𝗎𝗋𝖺𝗍𝖾, 𝗈𝗋𝖽𝖾𝗇𝖺 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺!",
                parse_mode="HTML"
            )
    else:
        await update.message.reply_text("¡𝖲𝗂𝗀𝗎𝖾𝗅𝗈 𝗂𝗇𝗍𝖾𝗇𝗍𝖺𝗇𝖽𝗈, 𝗒𝖺 𝖾𝗌𝗍𝖺𝗌 𝖼𝖾𝗋𝖼𝖺!")

# =====================================================================
# FIN DE PARTIDA
# =====================================================================

async def _fin_rondas(context, chat_id: int):
    sesion = sesion_anagrama.get(chat_id)
    if not sesion:
        return

    puntos = sesion["puntos"]
    if not puntos:
        await context.bot.send_message(chat_id=chat_id, text="¡𝗙𝗜𝗡 𝗗𝗘𝗟 𝗝𝗨𝗘𝗚𝗢ⵑ Nɑdie ɑdivinó ningunɑ. 😅")
        sesion_anagrama.pop(chat_id, None)
        return

    tabla = sorted(puntos.items(), key=lambda x: x[1], reverse=True)
    medallas = ["🥇", "🥈", "🥉"]
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)
    max_pts = tabla[0][1]

    msg = "¡𝖲𝖾 𝗁𝖺𝗇 𝗈𝗋𝖽𝖾𝗇𝖺𝖽𝗈 𝗍𝗈𝖽𝖺𝗌 𝗅𝖺𝗌 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌!\n\n"
    ganador_id, max_pts = tabla[0]
    ganador_nombre = _nombre_de(sesion, ganador_id)
    extra = f"\n+{premio} 𝖿𝗂𝖼𝗁𝖺𝗌 🟥" if premio else ""
    msg += f"( 𐃯 ) — {ganador_nombre} 𝖿𝗎𝖾 𝗊𝗎𝗂𝖾𝗇 𝗈𝗋𝖽𝖾𝗇𝗈 𝗆𝖺𝗌 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌. ¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌! 🎉"
    if premio:
        sumar_robux(ganador_id, ganador_nombre, premio, "𝐉𝐮𝐦𝐛𝐥𝐞: ")

    await context.bot.send_message(chat_id=chat_id, text=msg)
    await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
    )
    sesion_anagrama.pop(chat_id, None)

# =====================================================================
# BOTONES
# =====================================================================

async def manejar_botones_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_anagrama_click":
        await query.answer()

        sesion = sesion_anagrama.get(chat_id)
        if not sesion or not sesion.get("fase_registro"):
            await query.answer("ⓘ ˖ ࣪ 𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗋 𝖾𝗇 𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 ᵎᵎ", show_alert=True)
            return
        if any(j["id"] == user.id for j in sesion["jugadores"]):
            return

        sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"— {nombre_usuario(user)} se unio 𝅄 𖹭' ა")
