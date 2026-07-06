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
        caption="<b>໑ ' ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝗅𝖺 𝖢𝖺𝖼𝖾𝗋𝗂𝖺! ⑅</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_hunt &lt;cantidad&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_caseria.get(chat_id)

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
        text="🎯 ¡𝗧𝗔𝗕𝗟𝗘𝗥𝗢 𝗗𝗘 𝗖𝗔𝗖𝗘𝗥𝗜𝗔ⵑ\n\n𝖡𝗎𝗌𝖼𝖺 𝗅𝗈𝗌 𝟨 𝖾𝗆𝗈𝗃𝗂𝗌 𝖽𝖾 𝗍𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗒 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺𝗅𝗈𝗌. ¡𝖤𝗅 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝖾𝗇 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖺𝗋 𝗌𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗀𝖺𝗇𝖺!",
        reply_markup=markup
    )
    sesion["tablero_msg_id"] = msg.message_id

    for jugador in sesion["jugadores"]:
        texto_cartilla = construir_texto_cartilla(jugador["cartilla"], jugador["marcados"])
        msg_cartilla = await context.bot.send_message(
            chat_id=chat_id,
            text=f"\n🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {jugador['name']}:\n\n{texto_cartilla}"
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
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🎰 ֹ  {nombre_usuario(user)} se unio 𓂃")

    elif query.data.startswith("caseria_tablero_"):
        sesion = sesion_caseria.get(chat_id)
        if not sesion or not sesion.get("activa"):
            await query.answer("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /𝗁𝗎𝗇𝗍 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺.", show_alert=True)
            return

        jugador = next((j for j in sesion["jugadores"] if j["id"] == user.id), None)
        if not jugador:
            await query.answer("𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗋 𝖾𝗇 𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.", show_alert=True)
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
        await query.answer(f"¡𝖡𝗂𝖾𝗇, 𝗌𝗂𝗀𝗎𝖾 𝖺𝗌𝗂, 𝗅𝗅𝖾𝗏𝖺𝗌 ({len(marcados)}/6) 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝗆𝖺𝗋𝖼𝖺𝖽𝗈𝗌!", show_alert=False)

        texto_cartilla = construir_texto_cartilla(cartilla, marcados)
        if jugador.get("cartilla_msg_id"):
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=jugador["cartilla_msg_id"],
                    text=f"\n🎴 𝗖𝗮𝗿𝘁𝗶𝗹𝗹𝗮 𝗱𝗲 {jugador['name']}:\n\n{texto_cartilla}"
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
                text=f"🎉 ¡𝗣𝗔𝗥𝗧𝗜𝗗𝗔 𝗙𝗜𝗡𝗔𝗟𝗜𝗭𝗔𝗗𝗔, 𝗬𝗔 𝗧𝗘𝗡𝗘𝗠𝗢𝗦 𝗨𝗡 𝗚𝗔𝗡𝗔𝗗𝗢𝗥/𝗔ⵑ 🏆\n\n"
                     f"✨ {jugador['name']} 𝖿𝗎𝖾 𝗊𝗎𝗂𝖾𝗇 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝗈 𝗌𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗉𝗋𝗂𝗆𝖾𝗋𝗈. ¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌!"
            )
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
    )
