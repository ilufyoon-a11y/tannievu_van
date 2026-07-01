import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_CASERIA

# ================= DICCIONARIO =================

sesion_caseria = {}   # chat_id -> {...}

POOL_EMOJIS_CASERIA = [
    "😀","😂","😍","🥰","😎","🤩","😜","🥳","😇","🤯",
    "👻","💀","🤖","👾","🎃","🐶","🐱","🐭","🐹","🐰",
    "🦊","🐻","🐼","🐨","🐯","🦁","🐮","🐷","🐸","🐵",
    "🌸","🌺","🌻","🌹","🍀","🍁","🌴","🌵","🎄","🌊",
    "🍎","🍊","🍋","🍇","🍓","🍒","🍑","🥝","🍕","🍔",
    "🍦","🎂","🍩","🍪","🍭","🎮","🎯","🎲","🎸","🎺",
    "⚽","🏀","🎾","🏆","🥇","🚀","✈️","🚂","🚢","🎡",
    "💎","🔮","🧲","🪄","🎭","🌈","⭐","🌙","☀️","❄️",
]

# ================= HELPERS =================

def construir_teclado_tablero(tablero: list) -> InlineKeyboardMarkup:
    botones = []
    for fila in range(6):
        row = []
        for col in range(8):
            idx = fila * 8 + col
            emoji = tablero[idx]
            row.append(InlineKeyboardButton(emoji, callback_data=f"caseria_tablero_{idx}"))
        botones.append(row)
    return InlineKeyboardMarkup(botones)

def construir_texto_cartilla(cartilla: list, marcados: set) -> str:
    lineas = []
    fila = []
    for emoji in cartilla:
        marca = " ✓ " if emoji in marcados else " ☐ "
        fila.append(f"{emoji}{marca}")
        if len(fila) == 3:
            lineas.append("  ".join(fila))
            fila = []
    if fila:
        lineas.append("  ".join(fila))
    return "\n".join(lineas)

# ================= CODIGO PRINCIPAL =================

async def unirse_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    sesion_caseria[chat_id] = {
        "activa": False,
        "fase_registro": True,
        "jugadores": [],
        "tablero": [],
        "tablero_msg_id": None,
    }

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_caseria_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="<b> ៹ ࣪  🔎 ¡Juguemos ɑ Cɑceriɑ!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_hunt &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_caseria.get(chat_id)

    if not sesion or not sesion.get("fase_registro"):
        await update.message.reply_text("No hɑy ningunɑ sɑlɑ ɑbiertɑ, primero utilizɑ /hunt.")
        return

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["caseria"] = int(args[0]) if args else 0
    except ValueError:
        pass

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personɑs pɑrɑ jugɑr.")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    TAMANIO_TABLERO = 48
    TAMANIO_CARTILLA = 6

    sesion["fase_registro"] = False
    sesion["activa"] = True

    pool = random.sample(POOL_EMOJIS_CASERIA, TAMANIO_TABLERO)
    sesion["tablero"] = pool

    for jugador in sesion["jugadores"]:
        elegidos = random.sample(pool, TAMANIO_CARTILLA)
        jugador["cartilla"] = elegidos
        jugador["marcados"] = set()
        jugador["cartilla_msg_id"] = None

    markup = construir_teclado_tablero(pool)
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="🎯 ¡𝗧𝗔𝗕𝗟𝗘𝗥𝗢 𝗗𝗘 𝗖𝗔𝗖𝗘𝗥𝗜𝗔ⵑ\n\nEncuentrɑ los 6 emojis de tu cɑrtillɑ y presionɑlos. ¡El primero en completɑrlɑ gɑnɑ! 🏆",
        reply_markup=markup
    )
    sesion["tablero_msg_id"] = msg.message_id

    for jugador in sesion["jugadores"]:
        texto_cartilla = construir_texto_cartilla(jugador["cartilla"], jugador["marcados"])
        msg_cartilla = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {jugador['name']}:\n\n{texto_cartilla}"
        )
        jugador["cartilla_msg_id"] = msg_cartilla.message_id

# ================= MANEJO DE BOTONES =================

async def manejar_botones_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_caseria_click":
        await query.answer()
        sesion = sesion_caseria.get(chat_id)
        if not sesion:
            return
        if sesion.get("activa"):
            await query.answer("¡Lo siento, yɑ hɑy unɑ pɑrtidɑ en curso!", show_alert=True)
            return
        if any(j["id"] == user.id for j in sesion["jugadores"]):
            await query.answer("¡Yɑ estɑs dentro de lɑ listɑ de esperɑ, ɑmiko! 😎", show_alert=True)
            return
        sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🎰 ֹ  {nombre_usuario(user)} se unio 𓂃")

    elif query.data.startswith("caseria_tablero_"):
        sesion = sesion_caseria.get(chat_id)
        if not sesion or not sesion.get("activa"):
            await query.answer("No hɑy ningunɑ pɑrtidɑ ɑctivɑ.", show_alert=True)
            return

        jugador = next((j for j in sesion["jugadores"] if j["id"] == user.id), None)
        if not jugador:
            await query.answer("Lo siento, no puedes pɑrticipɑr en estɑ pɑrtidɑ.", show_alert=True)
            return

        idx = int(query.data.split("_")[2])
        emoji_pulsado = sesion["tablero"][idx]
        cartilla = jugador["cartilla"]
        marcados = jugador["marcados"]

        if emoji_pulsado not in cartilla:
            await query.answer("¡𝖠y, ese emoji no formɑ pɑrte de tu cɑrtillɑ!", show_alert=True)
            return
        if emoji_pulsado in marcados:
            await query.answer("¡Cuidɑdo, yɑ mɑrcɑste ese emoji ɑnteriormente!", show_alert=True)
            return

        marcados.add(emoji_pulsado)
        await query.answer(f"¡Sigue ɑsi, llevɑs ({len(marcados)}/6) objetos completɑdos!", show_alert=False)

        texto_cartilla = construir_texto_cartilla(cartilla, marcados)
        if jugador.get("cartilla_msg_id"):
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=jugador["cartilla_msg_id"],
                    text=f"🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {jugador['name']}:\n\n{texto_cartilla}"
                )
            except Exception:
                pass

        if len(marcados) == 6:
            sesion["activa"] = False
            premio_cas = sesion_puntos.get("premio_actual", {}).get("caseria", 0)
            sumar_robux(user.id, jugador["name"], premio_cas, "Caceria 🔎")
            extra_cas = f"\n\n+{premio_cas} fichɑs" if premio_cas else ""
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🎉 ¡𝗕𝗜𝗡𝗚𝗢, 𝗬𝗔 𝗧𝗘𝗡𝗘𝗠𝗢𝗦 𝗨𝗡 𝗚𝗔𝗡𝗔𝗗𝗢𝗥/𝗔ⵑ 🏆\n\n"
                     f"✨ {jugador['name']} fue quien completo su cɑrtillɑ primero. ¡Felicidɑdes!{extra_cas}"
            )
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
    )
