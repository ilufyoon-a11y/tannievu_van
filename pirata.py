import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, es_admin_sesion, GIF_PIRATA

# ================= UTILIDAD ANTI FLOOD =================

async def _enviar_seguro(func, *args, **kwargs):
    for _ in range(3):
        try:
            return await func(*args, **kwargs)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
    return await func(*args, **kwargs)

# ================= DICCIONARIO =================

sesion_pirata = {}   # chat_id -> {...}
_tareas_turno = {}   # chat_id -> asyncio.Task

MAX_JUGADORES = 10
TOTAL_RANURAS = 25
TIEMPO_TURNO = 15

def _sesion_base() -> dict:
    return {
        "jugadores": [],
        "activa": False,
        "sobrevivientes": [],
        "turno_actual": 0,
        "agujerofake": None,
        "agujerosave": [],
    }

# ================= CODIGO PRINCIPAL =================

async def unirse_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return
    chat_id = update.effective_chat.id
    sesion_pirata[chat_id] = _sesion_base()

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_pirata_click")
    await update.message.reply_photo(
        photo=GIF_PIRATA,
        caption="<b>๑ ꞈ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖲𝖺𝗅𝗍𝖺 𝖯𝗂𝗋𝖺𝗍𝖺! ⋆ ٠</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗌𝖾𝗇 <code>/start_pirata &lt;premio&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈.</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return

    sesion = sesion_pirata.get(chat_id)

    if not sesion:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /pirata 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋  𝗎𝗇𝖺 ᵎᵎ")
        return

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["pirata"] = int(args[0]) if args else 0
    except ValueError:
        pass

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0xCcWpKcoeEBYZYhxHjkhqbGntnlJzXAAJhBgACiPVIRbbKF2KzkH0nPAQ")
        return

    sesion["activa"] = True
    sesion["sobrevivientes"] = [j["id"] for j in sesion["jugadores"]]
    random.shuffle(sesion["sobrevivientes"])
    sesion["turno_actual"] = 0
    sesion["agujerosave"] = []
    sesion["agujerofake"] = random.randint(1, TOTAL_RANURAS)

    primer_nombre = next(j["name"] for j in sesion["jugadores"] if j["id"] == sesion["sobrevivientes"][0])
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"𐑺 ៸ ¡𝗟𝗔 𝗣𝗔𝗥𝗧𝗜𝗗𝗔 𝗗𝗘 𝗣𝗜𝗥𝗔𝗧𝗔 𝗛𝗔 𝗖𝗢𝗠𝗘𝗡𝗭𝗔𝗗𝗢ⵑ ◝ .\n\n"
             f"𝖧𝖺𝗒 {TOTAL_RANURAS} 𝗋𝖺𝗇𝗎𝗋𝖺𝗌 𝖽𝖾 𝗅𝖺𝗌 𝖼𝗎𝖺𝗅𝖾𝗌 𝗎𝗇𝖺 𝖺𝖼𝗍𝗂𝗏𝖺 𝖾𝗅 𝗆𝖾𝖼𝖺𝗇𝗂𝗌𝗆𝗈. ¡𝖲𝖾 𝗉𝗋𝖾𝖼𝖺𝗏𝗂𝖽@ 𝖺𝗅 𝖾𝗌𝖼𝗈𝗀𝖾𝗋 𝖽𝗈𝗇𝖽𝖾 𝗂𝗇𝗌𝖾𝗋𝗍𝖺𝗌 𝗅𝖺 𝖾𝗌𝗉𝖺𝖽𝖺!\n\n"
             f"𝖳𝗂𝖾𝗇𝖾𝗇 {TIEMPO_TURNO} 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝗌𝖾𝗅𝖾𝖼𝖼𝗂𝗈𝗇𝖺𝗋 𝗎𝗇𝖺 𝗋𝖺𝗇𝗎𝗋𝖺 𝗈 𝗌𝖾𝗋𝖺𝗇 𝖾𝗅𝗂𝗆𝗂𝗇𝖺𝖽𝗈𝗌 ᵎᵎ"
    )
    await enviar_turno_pirata(chat_id, context)

async def enviar_turno_pirata(chat_id, context):
    sesion = sesion_pirata.get(chat_id)
    if not sesion:
        return

    tarea_actual = asyncio.current_task()
    if chat_id in _tareas_turno and not _tareas_turno[chat_id].done() and _tareas_turno[chat_id] is not tarea_actual:
        _tareas_turno[chat_id].cancel()

    if sesion["turno_actual"] >= len(sesion["sobrevivientes"]):
        sesion["turno_actual"] = 0

    actual_id = sesion["sobrevivientes"][sesion["turno_actual"]]
    nombre_actual = next(j["name"] for j in sesion["jugadores"] if j["id"] == actual_id)

    todos_los_botones = [
        InlineKeyboardButton(
            "🗡️" if i in sesion["agujerosave"] else "🕳️",
            callback_data=f"ranura_ya_usada_{i}" if i in sesion["agujerosave"] else f"pirata_clic_{i}_{actual_id}"
        )
        for i in range(1, TOTAL_RANURAS + 1)
    ]
    botones = [todos_los_botones[i:i+5] for i in range(0, len(todos_los_botones), 5)]

    await _enviar_seguro(
        context.bot.send_message,
        chat_id=chat_id,
        text=f"<b>¡{nombre_actual} 𝖾𝗌 𝗍𝗎 𝗍𝗎𝗋𝗇𝗈, 𝖾𝗌𝖼𝗈𝗀𝖾 𝗎𝗇𝖺 𝗋𝖺𝗇𝗎𝗋𝖺!</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(botones)
    )

    tarea = asyncio.create_task(_auto_skip(chat_id, actual_id, nombre_actual, context))
    _tareas_turno[chat_id] = tarea

async def _auto_skip(chat_id, jugador_id, nombre, context):
    await asyncio.sleep(TIEMPO_TURNO)
    sesion = sesion_pirata.get(chat_id)
    if not sesion or not sesion["activa"]:
        return
    if sesion["turno_actual"] >= len(sesion["sobrevivientes"]):
        return
    if sesion["sobrevivientes"][sesion["turno_actual"]] != jugador_id:
        return

    sesion["sobrevivientes"].remove(jugador_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"<b>¡𝖤𝗅 𝗍𝗂𝖾𝗆𝗉𝗈 𝗌𝖾 𝖺𝗀𝗈𝗍𝗈, {nombre} 𝖿𝗎𝖾 𝖾𝗅𝗂𝗆𝗂𝗇𝖺𝖽𝗈!</b>",
        parse_mode="HTML"
    )
    if len(sesion["sobrevivientes"]) <= 1:
        sesion["activa"] = False
        if sesion["sobrevivientes"]:
            ganador = next(j["name"] for j in sesion["jugadores"] if j["id"] == sesion["sobrevivientes"][0])
            premio_p = sesion_puntos.get("premio_actual", {}).get("pirata", 0)
            if premio_p:
                sumar_robux(sesion["sobrevivientes"][0], ganador, premio_p, "𝗣𝗶𝗿𝗮𝘁𝗮 𝘀𝗼𝗯𝗿𝗲𝘃𝗶𝘃𝗶𝗲𝗻𝘁𝗲 ")
            extra_p = f"\n+{premio_p} 𝗋𝗈𝖻𝗎𝗑" if premio_p else ""
            await context.bot.send_message(chat_id=chat_id, text=f"っ⠀˖⠀꒰⠀𝗦𝗢𝗕𝗥𝗘𝗩𝗜𝗩𝗜𝗘𝗡𝗧𝗘⠀꒱\n\n{ganador}")
            await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
            )
        else:
            await context.bot.send_message(chat_id=chat_id, text="𝖳𝗈𝖽𝗈𝗌 𝖿𝗎𝖾𝗋𝗈𝗇 𝖾𝗅𝗂𝗆𝗂𝗇𝖺𝖽𝗈𝗌 🕊️")
        sesion_pirata.pop(chat_id, None)
        return

    if sesion["turno_actual"] >= len(sesion["sobrevivientes"]):
        sesion["turno_actual"] = 0
    await enviar_turno_pirata(chat_id, context)

# ================= MANEJO DE BOTONES =================

async def manejar_botones_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    chat_id = query.message.chat.id

    if query.data == "unirme_pirata_click":
        sesion = sesion_pirata.get(chat_id)
        if not sesion:
            await query.answer()
            return
        if sesion.get("activa"):
            await query.answer("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈 ᵎᵎ", show_alert=True)
            return

        if len(sesion["jugadores"]) >= MAX_JUGADORES:
            await query.answer()
            await context.bot.send_message(
                chat_id=chat_id,
                text="ⓘ ˖ ࣪ ¡𝖫𝖺 𝗌𝖺𝗅𝖺 𝗒𝖺 𝗌𝖾 𝖾𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝗅𝗅𝖾𝗇𝖺 ᵎᵎ"
            )
            return

        if not any(j["id"] == user.id for j in sesion["jugadores"]):
            sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.answer()
            await query.message.reply_text(f"— {nombre_usuario(user)} 𝗌𝖾 𝗎𝗇𝗂𝗈 𝅄 𖹭' ა")
        else:
            await query.answer("ⓘ ˖ ࣪ ¡𝖸𝖺 𝖾𝗌𝗍𝖺𝗌 𝖾𝗇 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 ᵎᵎ", show_alert=True)

    elif query.data.startswith("pirata_clic_"):
        await query.answer()
        sesion = sesion_pirata.get(chat_id)
        if not sesion or not sesion.get("activa"):
            return

        partes = query.data.split("_")
        num_ranura = int(partes[2])
        autor_id = int(partes[3])

        actual_id = sesion["sobrevivientes"][sesion["turno_actual"]]
        if user.id != actual_id or user.id != autor_id:
            return

        if chat_id in _tareas_turno and not _tareas_turno[chat_id].done():
            _tareas_turno[chat_id].cancel()

        if num_ranura == sesion["agujerofake"]:
            sesion["activa"] = False
            ganadores = [
                next(j["name"] for j in sesion["jugadores"] if j["id"] == uid)
                for uid in sesion["sobrevivientes"] if uid != autor_id
            ]
            texto_ganadores = ", ".join(ganadores) if ganadores else "¡Nɑdie! El pirata se quedó solo en el mar"
            premio_p = sesion_puntos.get("premio_actual", {}).get("pirata", 0)
            if premio_p:
                for uid_p in sesion["sobrevivientes"]:
                    if uid_p != autor_id:
                        nom_p = next((j["name"] for j in sesion["jugadores"] if j["id"] == uid_p), f"ID{uid_p}")
                        sumar_robux(uid_p, nom_p, premio_p, "𝗣𝗶𝗿𝗮𝘁𝗮 𝘀𝗼𝗯𝗿𝗲𝘃𝗶𝘃𝗶𝗲𝗻𝘁𝗲 ")
            extra_p = f"\n{premio_p} 𝗋𝗈𝖻𝗎𝗑" if premio_p else ""
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"¡𝗝𝗨𝗘𝗚𝗢 𝗙𝗜𝗡𝗔𝗟𝗜𝗭𝗔𝗗𝗢ⵑ\n\n{nombre_usuario(user)} 𝗂𝗇𝗌𝖾𝗋𝗍𝗈 𝗅𝖺 𝖾𝗌𝗉𝖺𝖽𝖺 𝖾𝗇 𝗅𝖺 𝗋𝖺𝗇𝗎𝗋𝖺 {num_ranura}... ¡𝖸 𝖤𝖫 𝖯𝖨𝖱𝖠𝖳𝖠 𝖲𝖠𝖫𝖳𝖮!\n\n"
                     f"っ⠀˖⠀꒰⠀𝗦𝗢𝗕𝗥𝗘𝗩𝗜𝗩𝗜𝗘𝗡𝗧𝗘𝗦⠀꒱\n\n{texto_ganadores}"
            )
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgEAAxkBA0Y1sWpDGFQQHzwJSrB9YNUygD0j8YEuAAI5BgACxL5BRIsEuKAHC3RbPAQ")

        else:
            sesion["agujerosave"].append(num_ranura)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🗡️ ¡𝖤𝗌𝗉𝖺𝖽𝖺 𝗂𝗇𝗌𝖾𝗋𝗍𝖺𝖽𝖺! 𝖱𝖺𝗇𝗎𝗋𝖺 {num_ranura} 𝖺 𝗌𝖺𝗅𝗏𝗈.\n\n{nombre_usuario(user)} 𝗌𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝗈."
            )
            sesion["turno_actual"] = (sesion["turno_actual"] + 1) % len(sesion["sobrevivientes"])
            await enviar_turno_pirata(chat_id, context)

    elif query.data.startswith("ranura_ya_usada_"):
        await context.bot.send_message("¡𝖴𝗉𝗌, 𝖾𝗌𝖺 𝗋𝖺𝗇𝗎𝗋𝖺 𝗒𝖺 𝗍𝗂𝖾𝗇𝖾 𝗎𝗇𝖺 𝖾𝗌𝗉𝖺𝖽𝖺 𝗂𝗇𝗌𝖾𝗋𝗍𝖺𝖽𝖺, 𝖾𝗅𝗂𝗀𝖾 𝗈𝗍𝗋𝖺!", show_alert=True)
