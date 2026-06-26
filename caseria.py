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

def construir_teclado_tablero(tablero: list, marcados_global: set) -> InlineKeyboardMarkup:
    botones = []
    for fila in range(8):
        row = []
        for col in range(8):
            idx = fila * 8 + col
            emoji = tablero[idx]
            if emoji in marcados_global:
                row.append(InlineKeyboardButton("✅", callback_data=f"caseria_tablero_ya_{idx}"))
            else:
                row.append(InlineKeyboardButton(emoji, callback_data=f"caseria_tablero_{idx}"))
        botones.append(row)
    return InlineKeyboardMarkup(botones)

def construir_texto_cartilla(cartilla: list, marcados: set) -> str:
    lineas = []
    fila = []
    for emoji in cartilla:
        marca = "✅" if emoji in marcados else "⬜"
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

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_caseria_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="៹ ࣪  🔎 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖢𝖺𝗌𝖾𝗋𝗂́𝖺! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
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
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    TAMANIO_TABLERO = 64
    TAMANIO_CARTILLA = 8

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
        inicio = (i * TAMANIO_CARTILLA) % TAMANIO_TABLERO
        elegidos = [todos_indices[(inicio + j) % TAMANIO_TABLERO] for j in range(TAMANIO_CARTILLA)]
        random.shuffle(elegidos)
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
    markup = construir_teclado_tablero(tablero, marcados_global)
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="🎯 **¡TABLERO DE LA CASERÍA!**\n\nEncuentra los 8 emojis de tu cartilla y ¡presiónalos! El primero en completarla gana. 🏆",
        reply_markup=markup
    )
    sesion_caseria["tablero_msg_id"] = msg.message_id

    for uid, datos in sesion_caseria["jugadores"].items():
        texto_cartilla = construir_texto_cartilla(datos["cartilla"], datos["marcados"])
        nombre = datos.get("nombre", f"ID{uid}")
        msg_cartilla = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎴 **Cartilla de {nombre}:**\n\n{texto_cartilla}",
            parse_mode="Markdown"
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
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        uid = user.id
        if uid in sesion_caseria["jugadores"]:
            await query.answer("¡Ya estás dentro de la lista de espera, amiko! 😎", show_alert=True)
            return
        sesion_caseria["jugadores"][uid] = {"nombre": nombre_usuario(user)}
        await query.message.reply_text(f"🎰 ֹ  {nombre_usuario(user)} se unió a la Casería, ¡suerte! 𓂃")

    elif query.data.startswith("caseria_tablero_"):
        if not sesion_caseria.get("activa"):
            await query.answer("No hay partida activa.", show_alert=True)
            return

        if query.data.startswith("caseria_tablero_ya_"):
            await query.answer("¡Este emoji ya fue marcado por alguien! 👀", show_alert=True)
            return

        uid = user.id
        if uid not in sesion_caseria["jugadores"]:
            await query.answer("❌ No estás participando en esta partida.", show_alert=True)
            return

        idx = int(query.data.split("_")[2])
        tablero = sesion_caseria["tablero"]
        emoji_pulsado = tablero[idx]
        datos_jugador = sesion_caseria["jugadores"][uid]
        cartilla = datos_jugador["cartilla"]
        marcados = datos_jugador["marcados"]

        if emoji_pulsado not in cartilla:
            await query.answer("❌ Ese emoji no está en tu cartilla.", show_alert=True)
            return
        if emoji_pulsado in marcados:
            await query.answer("¡Ya marcaste ese emoji antes!", show_alert=True)
            return

        marcados.add(emoji_pulsado)
        await query.answer(f"✅ ¡Marcaste {emoji_pulsado}! ({len(marcados)}/8)", show_alert=False)

        texto_cartilla = construir_texto_cartilla(cartilla, marcados)
        msg_cartilla_id = datos_jugador.get("cartilla_msg_id")
        gc = sesion_caseria["chat_id"]
        nombre_jug = datos_jugador.get("nombre", nombre_usuario(user))
        if msg_cartilla_id and gc:
            try:
                await context.bot.edit_message_text(
                    chat_id=gc,
                    message_id=msg_cartilla_id,
                    text=f"🎴 **Cartilla de {nombre_jug}:**\n\n{texto_cartilla}",
                    parse_mode="Markdown"
                )
            except Exception:
                pass

        marcados_global = set()
        for d in sesion_caseria["jugadores"].values():
            if isinstance(d, dict) and "marcados" in d:
                marcados_global |= d["marcados"]
        try:
            await query.edit_message_reply_markup(
                reply_markup=construir_teclado_tablero(tablero, marcados_global)
            )
        except Exception:
            pass

        if len(marcados) == 8:
            sesion_caseria["activa"] = False
            gc = sesion_caseria["chat_id"]
            premio_cas = sesion_puntos.get("premio_actual", {}).get("caseria", 0)
            sumar_robux(uid, nombre_usuario(user), premio_cas, "Casería 🔎")
            extra_cas = f"\n\n+{premio_cas} Robux 🟥" if premio_cas else ""
            await context.bot.send_message(
                chat_id=gc,
                text=f"🎉 **¡BINGO! ¡TENEMOS GANADOR/A!** 🏆\n\n"
                     f"✨ **{nombre_usuario(user)}** completó su cartilla primero. ¡Felicidades!{extra_cas}"
            )
