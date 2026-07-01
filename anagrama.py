import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_LETRISTA

# =====================================================================
# SESIONES
# =====================================================================

sesion_anagrama = {}   # chat_id -> {...}
esperando_moderador = {}   # user_id -> chat_id

STICKER_ERROR = "CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ"

def _sesion_base(modo_rondas: bool, creador_id: int, chat_id: int) -> dict:
    return {
        "activa": False,
        "fase_registro": True,
        "jugadores": [],
        "moderador_id": None,
        "creador_id": creador_id,
        "chat_id": chat_id,
        "categoria": None,
        "palabra": None,
        "palabras": [],
        "revuelta": None,
        "adivinadas": set(),
        "esperando": None,
        "modo_rondas": modo_rondas,
        "ronda_actual": 0,
        "total_rondas": 4,
        "puntos": {},
    }

# =====================================================================
# HELPERS
# =====================================================================

def revolver(palabra: str) -> str:
    letras = list(palabra.upper())
    random.shuffle(letras)
    intentos = 0
    while "".join(letras) == palabra.upper() and intentos < 20:
        random.shuffle(letras)
        intentos += 1
    return " ".join(letras)

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
# /jumble — versión clásica
# =====================================================================

async def cmd_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion_actual = sesion_anagrama.get(chat_id)

    if sesion_actual and (sesion_actual.get("activa") or sesion_actual.get("fase_registro")):
        await update.message.reply_text("¡Yɑ hɑy unɑ pɑrtidɑ de ɑnɑgrɑmɑ en curso en este grupo!")
        return

    sesion_anagrama[chat_id] = _sesion_base(modo_rondas=False, creador_id=update.effective_user.id, chat_id=chat_id)

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_anagrama_click")
    await update.message.reply_photo(
        photo=GIF_LETRISTA,
        caption="<b> ៹ ࣪  🔀 ¡Juguemos ɑl Anɑgrɑmɑ!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_jumble &lt;premio&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

# =====================================================================
# /jumble4 — versión 4 rondas
# =====================================================================

async def cmd_anagrama4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion_actual = sesion_anagrama.get(chat_id)

    if sesion_actual and (sesion_actual.get("activa") or sesion_actual.get("fase_registro")):
        await update.message.reply_text("¡Yɑ hɑy unɑ pɑrtidɑ de ɑnɑgrɑmɑ en curso en este grupo!")
        return

    sesion_anagrama[chat_id] = _sesion_base(modo_rondas=True, creador_id=update.effective_user.id, chat_id=chat_id)

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_anagrama_click")
    await update.message.reply_photo(
        photo=GIF_LETRISTA,
        caption="<b> ៹ ࣪  🔀 ¡Juguemos ɑl Anɑgrɑmɑ — 4 rondɑs!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_jumble &lt;premio&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

# =====================================================================
# /start_jumble
# =====================================================================

async def cmd_start_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_anagrama.get(chat_id)

    if not sesion or not sesion.get("fase_registro"):
        await update.message.reply_text("No hɑy ningunɑ sɑlɑ ɑbiertɑ, primero utilizɑ /jumble.")
        return

    if update.effective_user.id != sesion["creador_id"]:
        await update.message.reply_text("⛔ Solo quien creo lɑ sɑlɑ puede iniciɑr lɑ pɑrtidɑ.")
        return

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personɑs pɑrɑ jugɑr.")
        await update.message.reply_sticker(sticker=STICKER_ERROR)
        return

    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["anagrama"] = premio

    sesion["fase_registro"] = False

    mod = random.choice(sesion["jugadores"])
    sesion["moderador_id"] = mod["id"]
    esperando_moderador[mod["id"]] = chat_id

    await update.message.reply_text(
        f"˒˓  ¡{mod['name']} fue elegido como moderɑdor! Esperɑndo ɑ que defina lɑ categoriɑ y lɑ(s) pɑlɑbrɑ(s)  ᨦᨩ"
    )

    sesion["esperando"] = "categoria"
    try:
        if sesion["modo_rondas"]:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="<b>¡En horɑ buenɑ, te tocɑ ser el moderɑdor!</b>\n\nPrimero escribe lɑ <b>categoriɑ</b> de lɑs 4 pɑlɑbrɑs:",
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="<b>¡En horɑ buenɑ, te tocɑ ser el moderɑdor!</b>\n\nPrimero escribe lɑ <b>categoriɑ</b> de lɑ pɑlɑbrɑ\n<blockquote>ej: Animɑles, Pɑises, Comidɑs...</blockquote>",
                parse_mode="HTML"
            )
    except Exception:
        await update.message.reply_text(f"𝖠y, no se puede enviɑr un mensɑje ɑ {mod['name']}. Por fɑvor, ɑsegurɑte de hɑber iniciɑdo el bot.")
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

        if sesion["modo_rondas"]:
            await update.message.reply_text(
                f"✅ Categoriɑ: <b>{texto}</b>\n\nAhorɑ escribe lɑs <b>4 pɑlɑbrɑs</b> sepɑrɑdɑs por comɑ:\n<blockquote>ej: pie de limon, pɑstel, helɑdo, tortɑ</blockquote>",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"✅ Categoriɑ: <b>{texto}</b>\n\nAhorɑ escribe lɑ <b>pɑlɑbrɑ</b> que deben ɑdivinɑr\n<blockquote>puede tener espɑcios, ej: pie de limon</blockquote>",
                parse_mode="HTML"
            )
        return

    # Esperando palabras
    if sesion["esperando"] == "palabras":
        if sesion["modo_rondas"]:
            palabras = parsear_palabras(texto)
            if len(palabras) != 4:
                await update.message.reply_text(
                    f"¡Un momento! Necesito exɑctɑmente 4 pɑlɑbrɑs sepɑrɑdɑs por comɑ, recibi {len(palabras)}.\n<blockquote>ej: pie de limon, pɑstel, helɑdo, tortɑ</blockquote>",
                    parse_mode="HTML"
                )
                return

            sesion["palabras"] = palabras
            sesion["adivinadas"] = set()
            sesion["esperando"] = None
            sesion["activa"] = True
            esperando_moderador.pop(user_id, None)

            await update.message.reply_text("¡Muchɑs grɑciɑs, lɑs pɑlɑbrɑs hɑn sido guɑrdɑdɑs! El juego comienzɑ.")

            revuelta = revolver(palabras[0])
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔀 <b>Rondɑ 1/4 — Categoriɑ: {sesion['categoria']}</b>\n\n<code>{revuelta}</code>\n\n¡Adivinɑ lɑ pɑlɑbrɑ! 🧩",
                parse_mode="HTML"
            )

        else:
            palabra = texto.strip().lower()
            revuelta = revolver(palabra)
            sesion["palabra"] = palabra
            sesion["revuelta"] = revuelta
            sesion["esperando"] = None
            sesion["activa"] = True
            esperando_moderador.pop(user_id, None)

            await update.message.reply_text("¡Listo! Lɑ pɑlɑbrɑ yɑ estɑ en el grupo.")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔀 <b>Categoriɑ: {sesion['categoria']}</b>\n\n<code>{revuelta}</code>\n\n¡Adivinɑ lɑ pɑlɑbrɑ! 🧩",
                parse_mode="HTML"
            )
        return

# =====================================================================
# ESCUCHAR GRUPO — jugadores adivinan
# =====================================================================

async def escuchar_anagrama_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    sesion = sesion_anagrama.get(chat_id)
    if not sesion or not sesion.get("activa"):
        return
    if user_id == sesion["moderador_id"]:
        return
    if not texto:
        return
    if not any(j["id"] == user_id for j in sesion["jugadores"]):
        return

    texto_limpio = texto.lower().strip()

    # Modo rondas
    if sesion["modo_rondas"]:
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
                f"¡Punto pɑrɑ {nombre}, esɑ erɑ lɑ pɑlɑbrɑ!\n\n"
                f"Llevɑmos [{sesion['ronda_actual']}/{sesion['total_rondas']}] pɑlɑbrɑs descubiertɑs."
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
                    text=f"🔀 <b>Rondɑ {ronda_num}/4 — Categoriɑ: {sesion['categoria']}</b>\n\n<code>{revuelta}</code>\n\n¡Adivinɑ lɑ pɑlɑbrɑ! 🧩",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text("🔍 ¡Siguelo intentɑndo, yɑ estɑs cercɑ! 🧩")
        return

    # Modo clásico
    if texto_limpio != sesion["palabra"]:
        await update.message.reply_text("🔍 ¡Siguelo intentɑndo, yɑ estɑs cercɑ! 🧩")
        return

    nombre = _nombre_de(sesion, user_id)
    sesion["activa"] = False
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)

    sumar_robux(user_id, nombre, premio, "Anɑgrɑmɑ 🔀")
    extra = f"\n+{premio} fichɑs 🟥" if premio else ""
    await update.message.reply_text(
        f"¡{nombre} ɑdivinó! 🧩\n\nLɑ pɑlɑbrɑ erɑ: {sesion['palabra'].upper()}{extra}"
    )
    sesion_anagrama.pop(chat_id, None)

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

    msg = "¡𝗥𝗢𝗡𝗗𝗔 𝗙𝗜𝗡𝗔𝗟𝗜𝗭𝗔𝗗𝗔ⵑ Se descubrieron todɑs lɑs pɑlɑbrɑs.\n\n𝗣𝘂𝗻𝘁𝘂𝗮𝗰𝗶𝗼𝗻 𝗳𝗶𝗻𝗮𝗹:\n\n"
    for i, (uid_p, pts) in enumerate(tabla):
        nombre_p = _nombre_de(sesion, uid_p)
        dec = medallas[i] if i < 3 else "🔹"
        robux_p = premio if i == 0 else 0
        extra = f" — +{robux_p} fichɑs" if robux_p else ""
        msg += f"{dec} {nombre_p}: {pts} pt(s){extra}\n"
        if robux_p:
            sumar_robux(uid_p, nombre_p, robux_p, f"𝗣𝘂𝗲𝘀𝘁𝗼: {i+1} 🔀")

    await context.bot.send_message(chat_id=chat_id, text=msg)
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
            await query.answer("¡Lo siento, el registro yɑ cerro!", show_alert=True)
            return
        if any(j["id"] == user.id for j in sesion["jugadores"]):
            return

        sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🔀  {nombre_usuario(user)} se unio 𓂃")
