import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_CASERIA, GIF_ERROR

# ================= DICCIONARIO =================

sesion_caseria = {
    "activa": False,
    "fase_registro": False,
    "jugadores": {},
    "tablero": [],
    "tablero_msg_id": None,
    "chat_id": None,
}

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
    sesion_caseria["jugadores"] = {}
    sesion_caseria["tablero"] = []
    sesion_caseria["tablero_msg_id"] = None
    sesion_caseria["activa"] = False
    sesion_caseria["fase_registro"] = True
    sesion_caseria["chat_id"] = None

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_caseria_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ Cɑceriɑ!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_hunt &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["caseria"] = int(args[0])
        except ValueError:
            pass

    if len(sesion_caseria["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personɑs pɑrɑ jugɑr.")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    TAMANIO_TABLERO = 48
    TAMANIO_CARTILLA = 6

    sesion_caseria["fase_registro"] = False
    sesion_caseria["activa"] = True
    sesion_caseria["chat_id"] = chat_id

    pool = random.sample(POOL_EMOJIS_CASERIA, TAMANIO_TABLERO)
    tablero = pool[:TAMANIO_TABLERO]
    sesion_caseria["tablero"] = tablero

    uid_list = list(sesion_caseria["jugadores"].keys())
    n = len(uid_list)
    todos_indices = list(range(TAMANIO_TABLERO))
    random.shuffle(todos_indices)

    cartillas_asignadas = []
    for i in range(n):
        elegidos = random.sample(todos_indices, TAMANIO_CARTILLA)
        cartillas_asignadas.append(elegidos)

    for i, uid in enumerate(uid_list):
        cartilla_emojis = [tablero[idx] for idx in cartillas_asignadas[i]]
        sesion_caseria["jugadores"][uid] = {
            "cartilla": cartilla_emojis,
            "marcados": set(),
            "nombre": sesion_caseria["jugadores"][uid].get("nombre", f"ID{uid}"),
            "cartilla_msg_id": None,
        }

    marcados_global = set()
    markup = construir_teclado_tablero(tablero)
    msg = await context.bot.send_message(
    chat_id=chat_id,
    text="🎯 ¡𝗧𝗔𝗕𝗟𝗘𝗥𝗢 𝗗𝗘 𝗖𝗔𝗖𝗘𝗥𝗜𝗔ⵑ\n\nEncuentrɑ los 6 emojis de tu cɑrtillɑ y presionɑlos. ¡El primero en completɑrlɑ gɑnɑ! 🏆",
    reply_markup=markup
    )

    sesion_caseria["tablero_msg_id"] = msg.message_id

    for uid, datos in sesion_caseria["jugadores"].items():
        texto_cartilla = construir_texto_cartilla(datos["cartilla"], datos["marcados"])
        nombre = datos.get("nombre", f"ID{uid}")
        msg_cartilla = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {nombre}:\n\n{texto_cartilla}"
        )
        datos["cartilla_msg_id"] = msg_cartilla.message_id

# ================= MANEJO DE BOTONES =================

async def manejar_botones_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_caseria_click":
        await query.answer()
        if sesion_caseria.get("activa"):
            await query.answer("¡Lo siento, yɑ hɑy unɑ pɑrtidɑ en curso!", show_alert=True)
            return
        uid = user.id
        if uid in sesion_caseria["jugadores"]:
            await query.answer("¡Ya estás dentro de la lista de espera, amiko! 😎", show_alert=True)
            return
        sesion_caseria["jugadores"][uid] = {"nombre": nombre_usuario(user)}
        await query.message.reply_text(f"🎰 ֹ  {nombre_usuario(user)} se unio 𓂃")

    elif query.data.startswith("caseria_tablero_"):
        if not sesion_caseria.get("activa"):
            await query.answer("No hɑy ningunɑ pɑrtidɑ ɑctivɑ.", show_alert=True)
            return

        uid = user.id
        if uid not in sesion_caseria["jugadores"]:
            await query.answer("Lo siento, no puedes pɑrticipɑr en estɑ pɑrtidɑ", show_alert=True)
            return

        idx = int(query.data.split("_")[2])
        tablero = sesion_caseria["tablero"]
        emoji_pulsado = tablero[idx]
        datos_jugador = sesion_caseria["jugadores"][uid]
        cartilla = datos_jugador["cartilla"]
        marcados = datos_jugador["marcados"]

        if emoji_pulsado not in cartilla:
            await query.answer("¡𝖠y, ese emoji no formɑ pɑrte de tu cɑrtillɑ!", show_alert=True)
            return
        if emoji_pulsado in marcados:
            await query.answer("¡Cuidɑdo, yɑ mɑrcɑste ese emoji ɑnteriormente!", show_alert=True)
            return

        marcados.add(emoji_pulsado)
        await query.answer(f"✅ ¡Mɑrcɑste {emoji_pulsado}!. ¡Sigue ɑsi, llevɑs ({len(marcados)}/6) objetos completɑdos!", show_alert=False)

        texto_cartilla = construir_texto_cartilla(cartilla, marcados)
        msg_cartilla_id = datos_jugador.get("cartilla_msg_id")
        gc = sesion_caseria["chat_id"]
        nombre_jug = datos_jugador.get("nombre", nombre_usuario(user))
        if msg_cartilla_id and gc:
            try:
                await context.bot.edit_message_text(
                    chat_id=gc,
                    message_id=msg_cartilla_id,
                    text=f"🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {nombre_jug}:\n\n{texto_cartilla}"
                )
            except Exception:
                pass

        if len(marcados) == 6:
            sesion_caseria["activa"] = False
            gc = sesion_caseria["chat_id"]
            premio_cas = sesion_puntos.get("premio_actual", {}).get("caseria", 0)
            sumar_robux(uid, nombre_usuario(user), premio_cas, "Casería 🔎")
            extra_cas = f"\n\n+{premio_cas} fichɑs" if premio_cas else ""
            await context.bot.send_message(
                chat_id=gc,
                text=f"🎉 ¡𝗕𝗜𝗡𝗚𝗢, 𝗬𝗔 𝗧𝗘𝗡𝗘𝗠𝗢𝗦 𝗨𝗡 𝗚𝗔𝗡𝗔𝗗𝗢𝗥/𝗔ⵑ 🏆\n\n"
                     f"✨ {nombre_usuario(user)} fue quien completo su cɑrtillɑ primero. ¡Felicidɑdes!{extra_cas}"
            )
