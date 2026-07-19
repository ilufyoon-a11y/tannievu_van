import random
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, es_admin_sesion, GIF_CASERIA

logger = logging.getLogger(__name__)

# ================= DICCIONARIO =================

sesion_caseria = {}   # chat_id -> {...}
_tareas_shuffle = {}  # chat_id -> asyncio.Task

TIEMPO_SHUFFLE = 10  # segundos entre cada mezcla del tablero

POOL_EMOJIS_CASERIA = [
    "💭", "💜", "♥️", "💙", "💚", "🩶", "🩵", "💛", "🧡", "🩷", "❤️", "🤍", "🖤", "🤎", "🗡️", 
    "⚔️", "📜", "🪤", "💣", "🚬", "🪦", "⚱️", "🏺", "📿", "🔮", "📣", "⏲️", "⏳", "🕰️", "⏰", 
    "🪧", "🗓️", "🗳️", "📮", "📯", "📦", "📬", "💌", "🗞️", "🏷️", "🗑️", "📌", "🪪", "🔖", "🗂️", 
    "📖", "📚", "✏️", "🖌️", "🖍️", "📐", "✂️", "🖇️", "🪜", "🪣", "🪝", "🧲", "🪓", "🧯", "🛰️", 
    "📡", "🧰", "🔬", "🔭", "🧬", "🩻", "🩺", "🩹", "💊", "💉", "🕶️", "🥽", "⚗️", "☂️", "🧳", 
    "💼", "👜", "👛", "🪭", "💍", "👑", "🧢", "👒", "🎩", "🎓", "🧽", "🧼", "🪮", "🪒", "🧹", 
    "🚿", "🛁", "🧸", "🚪", "🪞", "🏮", "🔦", "💡", "🕯️", "🛍️", "🛒", "🧾", "🎟️", "🎭", "📽️", 
    "📺", "📻", "📼", "🎙️", "🎧", "🎤", "🪗", "🪈", "🪇", "🪘", "🥁", "🎻", "🪕", "🎸", "🎺", 
    "🎷", "🎨", "🧶", "📷", "🎩", "🪄", "🃏", "👾", "🔫", "🕹️", "🎮", "🧩", "🪀", "🎳", "🏓", 
    "🎱", "🎣", "🩰", "⛳", "🏹", "🪃", "🪁", "🎃", "🎄", "🎋", "🎍", "🎑", "🎏", "🎐", "🪩", 
    "🪅", "🪔", "🧧", "🎁", "🎀", "🎂", "🎈", "🧨", "🧳", "🗺️", "⛺", "🏟️", "🎪", "🎠", "🎡", 
    "🛸", "🚀", "✈️", "⛵", "🧭", "🥢", "🍶", "🍹", "🍸", "🍷", "🍾", "🍺", "🧉", "🫖", "☕", 
    "🍵", "🧋", "🧃", "🥤", "🫙", "🍿", "🧀", "🥚", "🍞", "🫓", "🥜", "🍳", "🥞", "🌰", "🥳", 
    "🥯", "🥖", "🧄", "🧅", "🫒", "🥔", "🥥", "🥑", "🍠", "🥝", "🍏", "🍆", "🍇", "🫐", "🥒", 
    "🫛", "🍊", "🍐", "🍑", "🍈", "🍉", "🍋", "🌶️", "🌽", "🍅", "🍌", "🍍", "🍎", "🍒", "🥭", 
    "🍓", "🥕", "🐾", "🐛", "🦋", "🐞", "🐝", "🦗", "🐌", "🐚", "🕸️", "🫧", "🪸", "🦪", "🪼", 
    "🦑", "🐋", "🐬", "🦭", "🦢", "🐣", "🦉", "🦜", "🐦", "🪶", "🦦", "🪽", "🐿️", "🦫", "🦝", 
    "🦥", "🐑", "🐖", "🐕", "🐸", "🐷", "🐮", "🦊", "🦎", "🐉", "🐺", "🐻", "🐻‍❄️", "🐨", "🐼", 
    "🐹", "🐭", "🐰", "🦄", "🐴", "🦁", "🐯", "🐱", "🐶", "🌟", "✨", "☄️", "🪐", "🌀", "❄️", 
    "⛄", "🔥", "🌋", "🌴", "🌵", "🪴", "🍀", "🍃", "🌱", "☘️", "🌿", "🌾", "💮", "🌸", "🍄", 
    "🪷", "🍁", "🌷", "🍂", "🌺", "🌼", "🥀", "🌻", "🪻", "🌹", "💐", "🏵️", "🥰", "😗", "🥳", 
    "🤩", "🫠", "🥹", "😋", "🤭", "🫢", "🤨", "😠", "😞", "😟", "😢", "☹️", "🙁", "😨", "😧", 
    "😰", "😦", "🤯", "😖", "😵‍💫", "🥴", "🤢", "😴", "😇", "🤠", "👻", "🌞", "😻", "😼", "😽", 
    "😿", "💘", "💝", "💖", "💗", "💞", "💕", "💋", "💌"
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

def construir_mensaje_cartillas(jugadores: list) -> str:
    partes = []
    for jugador in jugadores:
        texto_cartilla = construir_texto_cartilla(jugador["cartilla"], jugador["marcados"])
        partes.append(
            f"🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 ﹕ {jugador['name']} 𔓕\n\n<code>{texto_cartilla}</code>"
        )
    return "\n\n".join(partes)

# ================= CODIGO PRINCIPAL =================

async def unirse_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return

    if chat_id in _tareas_shuffle and not _tareas_shuffle[chat_id].done():
        _tareas_shuffle[chat_id].cancel()

    sesion_caseria[chat_id] = {
        "activa": False,
        "fase_registro": True,
        "jugadores": [],
        "tablero": [],
        "tablero_msg_id": None,
        "cartillas_msg_id": None,
    }

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_caseria_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="<b>๑ ꞈ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝗅𝖺 𝖢𝖺𝖼𝖾𝗋𝗂𝖺! ⋆ ٠</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_hunt &lt;cantidad&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_caseria.get(chat_id)

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return

    if not sesion or not sesion.get("fase_registro"):
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /𝗁𝗎𝗇𝗍 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ")
        return

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["caseria"] = int(args[0]) if args else 0
    except ValueError:
        pass

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0xCcWpKcoeEBYZYhxHjkhqbGntnlJzXAAJhBgACiPVIRbbKF2KzkH0nPAQ")
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

    markup = construir_teclado_tablero(pool)
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text="𐑺 ៸ 🎯 𝗧𝗔𝗕𝗟𝗘𝗥𝗢 𝗗𝗘 𝗖𝗔𝗖𝗘𝗥𝗜𝗔 ◝ .\n\n𝖡𝗎𝗌𝖼𝖺 𝗅𝗈𝗌 𝟨 𝖾𝗆𝗈𝗃𝗂𝗌 𝖽𝖾 𝗍𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗒 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺𝗅𝗈𝗌. ¡𝖤𝗅 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝖾𝗇 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖺𝗋 𝗌𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗀𝖺𝗇𝖺!",
        reply_markup=markup
    )
    sesion["tablero_msg_id"] = msg.message_id

    tarea = asyncio.create_task(_shuffle_tablero(chat_id, context))
    _tareas_shuffle[chat_id] = tarea

    await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgEAAxkBA0zRRmpLKoWCq3L-8eG58lH9nCLMVe0jAALYCAAC9qBYRq1em0vd00mlPAQ"
    )
    msg_cartillas = await context.bot.send_message(
        chat_id=chat_id,
        text=construir_mensaje_cartillas(sesion["jugadores"]),
        parse_mode="HTML"
    )
    sesion["cartillas_msg_id"] = msg_cartillas.message_id

async def _shuffle_tablero(chat_id, context):
    while True:
        await asyncio.sleep(TIEMPO_SHUFFLE)
        sesion = sesion_caseria.get(chat_id)
        if not sesion or not sesion.get("activa"):
            return

        random.shuffle(sesion["tablero"])
        nuevo_markup = construir_teclado_tablero(sesion["tablero"])
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=sesion["tablero_msg_id"],
                reply_markup=nuevo_markup
            )
        except Exception as e:
            logger.warning(f"Caseria: fallo al mezclar tablero, reintentando ({e})")
            await asyncio.sleep(1.5)
            try:
                await context.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=sesion["tablero_msg_id"],
                    reply_markup=nuevo_markup
                )
            except Exception as e2:
                logger.error(f"Caseria: fallo definitivo al mezclar tablero ({e2})")

# ================= MANEJO DE BOTONES =================

async def manejar_botones_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_caseria_click":
        sesion = sesion_caseria.get(chat_id)
        if not sesion:
            await query.answer()
            return
        if sesion.get("activa"):
            await query.answer("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈 ᵎᵎ", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion["jugadores"]):
            sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.answer()
            await query.message.reply_text(f"— {nombre_usuario(user)} se unio 𝅄 𖹭' ა")
        else:
            await query.answer("ⓘ ˖ ࣪ ¡𝖸𝖺 𝖾𝗌𝗍𝖺𝗌 𝖾𝗇 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 ᵎᵎ", show_alert=True)

    elif query.data.startswith("caseria_tablero_"):
        sesion = sesion_caseria.get(chat_id)
        if not sesion or not sesion.get("activa"):
            await query.answer("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /𝗁𝗎𝗇𝗍 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ", show_alert=True)
            return

        jugador = next((j for j in sesion["jugadores"] if j["id"] == user.id), None)
        if not jugador:
            await query.answer("ⓘ ˖ ࣪ 𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗋 𝖾𝗇 𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 ᵎᵎ", show_alert=True)
            return

        idx = int(query.data.split("_")[2])
        emoji_pulsado = sesion["tablero"][idx]
        cartilla = jugador["cartilla"]
        marcados = jugador["marcados"]

        if emoji_pulsado not in cartilla:
            await query.answer("¡𝖢𝗎𝗂𝖽𝖺𝖽𝗈, 𝖾𝗌𝖾 𝖾𝗆𝗈𝗃𝗂 𝗇𝗈 𝖿𝗈𝗋𝗆𝖺 𝗉𝖺𝗋𝗍𝖾 𝖽𝖾 𝗍𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺!", show_alert=True)
            return
        if emoji_pulsado in marcados:
            await query.answer("¡𝖠𝗒, 𝗒𝖺 𝗆𝖺𝗋𝖼𝖺𝗌𝗍𝖾 𝖾𝗌𝖾 𝖾𝗆𝗈𝗃𝗂 𝖺𝗇𝗍𝖾𝗋𝗂𝗈𝗋𝗆𝖾𝗇𝗍𝖾!", show_alert=True)
            return

        marcados.add(emoji_pulsado)
        faltantes = [e for e in cartilla if e not in marcados]
        if faltantes:
            texto_faltantes = " ".join(faltantes)
            await query.answer(f"¡𝖡𝗂𝖾𝗇, 𝗌𝗂𝗀𝗎𝖾 𝖺𝗌𝗂, 𝗅𝗅𝖾𝗏𝖺𝗌 ({len(marcados)}/6)! 𝖥𝖺𝗅𝗍𝖺𝗇: {texto_faltantes}", show_alert=False)

        texto_cartillas = construir_mensaje_cartillas(sesion["jugadores"])
        if sesion.get("cartillas_msg_id"):
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=sesion["cartillas_msg_id"],
                    text=texto_cartillas,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"Caseria: fallo al actualizar cartillas ({e})")

        if len(marcados) == 6:
            sesion["activa"] = False
            if chat_id in _tareas_shuffle and not _tareas_shuffle[chat_id].done():
                _tareas_shuffle[chat_id].cancel()
            premio_cas = sesion_puntos.get("premio_actual", {}).get("caseria", 0)
            sumar_robux(user.id, jugador["name"], premio_cas, "𝗖𝗮𝗰𝗲𝗿𝗶𝗮 ")
            extra_cas = f"\n\n+{premio_cas} 𝖿𝗂𝖼𝗁𝖺𝗌" if premio_cas else ""
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgEAAxkBA0zRRmpLKoWCq3L-8eG58lH9nCLMVe0jAALYCAAC9qBYRq1em0vd00mlPAQ"
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"¡𝗣𝗔𝗥𝗧𝗜𝗗𝗔 𝗙𝗜𝗡𝗔𝗟𝗜𝗭𝗔𝗗𝗔, 𝗬𝗔 𝗧𝗘𝗡𝗘𝗠𝗢𝗦 𝗨𝗡 𝗚𝗔𝗡𝗔𝗗𝗢𝗥/𝗔ⵑ\n\n"
                     f"( 𐃯 ) — {jugador['name']} 𝖿𝗎𝖾 𝗊𝗎𝗂𝖾𝗇 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝗈 𝗌𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗉𝗋𝗂𝗆𝖾𝗋𝗈. ¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌! 🎉"
            )
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
            )
