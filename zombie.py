import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_ZOMBIE, GIF_ERROR, GIF_CERO

# ================= DICCIONARIO =================

sesion_zombie = {
    "jugadores": [],
    "activa": False,
    "zombies": [],
    "vivos": [],
    "fase": None,
    "votos": {},
    "mensaje_voto_id": None,
    "ultimo_zombie_id": None,
}

# ================= CODIGO PRINCIPAL =================

async def unirse_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_zombie["jugadores"] = []
    sesion_zombie["zombies"] = []
    sesion_zombie["vivos"] = []
    sesion_zombie["votos"] = {}
    sesion_zombie["activa"] = False
    sesion_zombie["fase"] = None

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_zombie_click")
    await update.message.reply_photo(
        photo=GIF_ZOMBIE,
        caption="<b>๑ ꞈ 𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝗁𝖺 𝗅𝗅𝖾𝗀𝖺𝖽𝗈 𝗒 𝗅𝗈𝗌 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 𝖾𝗌𝗍𝖺𝗇 𝗌𝖺𝗅𝗂𝖾𝗇𝖽𝗈. ¡𝖠𝗉𝗋𝖾𝗌𝗎𝗋𝖺𝗍𝖾 𝖺 𝗌𝗎𝖻𝗂𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌! ⋆ ٠</b>\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_zombie &lt;pz ps&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    if len(args) >= 2:
        try:
            sesion_puntos["premio_actual"]["zombie_surv"] = int(args[0])
            sesion_puntos["premio_actual"]["zombie_zombie"] = int(args[1])
        except ValueError:
            pass
    elif len(args) == 1:
        try:
            sesion_puntos["premio_actual"]["zombie_surv"] = int(args[0])
        except ValueError:
            pass

    if sesion_zombie["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈 ᵎᵎ")
        return

    if len(sesion_zombie["jugadores"]) < 3:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟥 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    sesion_zombie["activa"] = True
    sesion_zombie["fase"] = "infeccion"
    sesion_zombie["vivos"] = [j["id"] for j in sesion_zombie["jugadores"]]

    ultimo_zombie = sesion_zombie.get("ultimo_zombie_id")
    candidatos = [uid for uid in sesion_zombie["vivos"] if uid != ultimo_zombie]
    paciente_cero_id = random.choice(candidatos if candidatos else sesion_zombie["vivos"])
    sesion_zombie["ultimo_zombie_id"] = paciente_cero_id
    sesion_zombie["zombies"].append(paciente_cero_id)
    sesion_zombie["vivos"].remove(paciente_cero_id)

    paciente_cero_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == paciente_cero_id)

    await update.message.reply_text(
        "Ꜥ ¡𝖴𝗇 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝗌𝖾 𝖼𝗈𝗅𝗈! ⸝⸝\n\n𝖴𝗇𝗈 𝖽𝖾 𝗎𝗌𝗍𝖾𝖽𝖾𝗌 𝖿𝗎𝖾 𝗆𝗈𝗋𝖽𝗂𝖽𝗈 𝗉𝗈𝗋 𝗎𝗇 𝗓𝗈𝗆𝖻𝗂𝖾 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗌𝗎𝖻𝗂𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌, 𝖾𝗅 𝖻𝗋𝗈𝗍𝖾 𝗁𝖺 𝖼𝗈𝗆𝖾𝗇𝗓𝖺𝖽𝗈..."
    )
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjCWpC_HERlalQGI7HXrVJOdOI2sDJAAIZCQAC36pAROiuTUHK1uCmPAQ"
    )

    botones_ataque = [
        [InlineKeyboardButton(f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {next(j for j in sesion_zombie['jugadores'] if j['id'] == humano_id)['name']}",
                              callback_data=f"morder:{humano_id}:{chat_id}")]
        for humano_id in sesion_zombie["vivos"]
    ]

    try:
        await context.bot.send_photo(
            chat_id=paciente_cero_id,
            photo=GIF_CERO,
            caption="𝖥𝗎𝗂𝗌𝗍𝖾 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝖾𝗇𝗍𝗋𝖺𝗋 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝗒 𝖺𝗁𝗈𝗋𝖺 𝗌𝗂𝖾𝗇𝗍𝖾𝗌 𝗎𝗇𝖺 𝗇𝖾𝖼𝖾𝗌𝗂𝖽𝖺𝖽 𝗂𝗇𝗍𝖾𝗇𝗌𝖺 𝖽𝖾 𝖼𝖺𝗋𝗇𝖾. ¿𝖰𝗎𝗂𝖾𝗇 𝗌𝖾𝗋𝖺 𝗍𝗎 𝗉𝗋𝖾𝗌𝖺?",
            reply_markup=InlineKeyboardMarkup(botones_ataque)
        )
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"ⓘ ˖ ࣪ 𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({paciente_cero_obj['name']}). 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 ᵎᵎ"
        )
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        sesion_zombie["activa"] = False

async def abrir_votacion_zombie(chat_id, context):
    sesion_zombie["fase"] = "votacion"
    sesion_zombie["votos"] = {}

    botones_voto = [
        [InlineKeyboardButton(f"𝖤𝗑𝗉𝗎𝗅𝗌𝖺𝗋 𝖺 {j['name']}", callback_data=f"voto_z:{j['id']}")]
        for j in sesion_zombie["jugadores"]
    ]

    msg_voto = await context.bot.send_message(
        chat_id=chat_id,
        text="𐑺 ៸ 𝗥𝗘𝗨𝗡𝗜𝗢𝗡 𝗗𝗘 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗜𝗔 ◝ .\n\n𝖠𝗅𝗀𝗎𝗂𝖾𝗇 𝗒𝖺 𝖿𝗎𝖾 𝗆𝗈𝗋𝖽𝗂𝖽𝗈, 𝖺𝗌𝗂 𝗊𝗎𝖾 𝖽𝖾𝖻𝖾𝗇 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝗋 𝖺𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝗆𝗎𝖾𝗋𝖽𝖺 𝖺 𝗈𝗍𝗋𝖺 𝗉𝖾𝗋𝗌𝗈𝗇𝖺.\n\n𝖲𝗈𝗅𝗈 𝖼𝗎𝖾𝗇𝗍𝖺𝗇 𝖼𝗈𝗇 𝟨𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝗉𝗈𝗇𝖾𝗋𝗌𝖾 𝖽𝖾 𝖺𝖼𝗎𝖾𝗋𝖽𝗈 𝗒 𝗏𝗈𝗍𝖺𝗋",
        reply_markup=InlineKeyboardMarkup(botones_voto)
    )
    sesion_zombie["mensaje_voto_id"] = msg_voto.message_id
    asyncio.create_task(timer_votacion_zombie(chat_id, context))

async def timer_votacion_zombie(chat_id, context):
    await asyncio.sleep(60)
    if sesion_zombie["activa"] and sesion_zombie["fase"] == "votacion":
        await procesar_resultados_votacion(chat_id, context)

async def procesar_resultados_votacion(chat_id, context):
    if sesion_zombie["fase"] != "votacion":
        return
    sesion_zombie["fase"] = None

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=sesion_zombie["mensaje_voto_id"])
    except Exception:
        pass

    if not sesion_zombie["votos"]:
        await context.bot.send_message(chat_id=chat_id, text="𝖭𝖺𝖽𝗂𝖾 𝗏𝗈𝗍𝗈 𝖺 𝗍𝗂𝖾𝗆𝗉𝗈, 𝖾𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝗌𝗂𝗀𝗎𝖾 𝖺𝗊𝗎ı́, 𝖾𝗅 𝖺𝗍𝖺𝗊𝗎𝖾 𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝖺...")
        await pasar_a_siguiente_ataque(chat_id, context)
        return

    conteo = {}
    for vid in sesion_zombie["votos"].values():
        conteo[vid] = conteo.get(vid, 0) + 1

    mas_votado_id = max(conteo, key=conteo.get)
    max_votos = conteo[mas_votado_id]
    empates = [k for k, v in conteo.items() if v == max_votos]

    if len(empates) > 1:
        await context.bot.send_message(chat_id=chat_id, text="¡𝖧𝗎𝖻𝗈 𝗎𝗇 𝖾𝗆𝗉𝖺𝗍𝖾 𝗒 𝗇𝖺𝖽𝗂𝖾 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈!")
        await pasar_a_siguiente_ataque(chat_id, context)
        return

    eliminado_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == mas_votado_id)

    if mas_votado_id in sesion_zombie["zombies"]:
        sesion_zombie["zombies"].remove(mas_votado_id)
        sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != mas_votado_id]
        await context.bot.send_message(chat_id=chat_id,
            text=f"{eliminado_obj['name']} 𝗈𝖻𝗍𝗎𝗏𝗈 {max_votos} 𝗏𝗈𝗍𝗈𝗌 𝗒 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌.\n\n¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌, 𝗌𝖾 𝖽𝖾𝗌𝗁𝗂𝖼𝗂𝖾𝗋𝗈𝗇 𝖽𝖾𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈!")
    else:
        sesion_zombie["vivos"].remove(mas_votado_id)
        sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != mas_votado_id]
        await context.bot.send_message(chat_id=chat_id,
            text=f"{eliminado_obj['name']} 𝗈𝖻𝗍𝗎𝗏𝗈 {max_votos} 𝗏𝗈𝗍𝗈𝗌 𝗒 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌.\n\n𝖤𝗋𝖺 𝗎𝗇 𝗁𝗎𝗆𝖺𝗇𝗈 𝗉𝖾𝗋𝖿𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 𝗌𝖺𝗇𝗈...")

    if not sesion_zombie["zombies"]:
        ganadores_obj = [j for j in sesion_zombie["jugadores"] if j["id"] in sesion_zombie["vivos"]]
        ganadores = [j["name"] for j in ganadores_obj]
        premio_surv = sesion_puntos.get("premio_actual", {}).get("zombie_surv", 0)
        for j in ganadores_obj:
            sumar_robux(j["id"], j["name"], premio_surv, "𝖲𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝖾𝗇𝗍𝖾 𝖽𝖾𝗅 𝗓𝗈𝗆𝖻𝗂𝖾")
        extra_surv = f" (+{premio_surv} 𝖿𝗂𝖼𝗁𝖺𝗌 𝖼/𝗎)" if premio_surv else ""
        await context.bot.send_message(chat_id=chat_id,
            text=f"𐑺 ៸ 𝗦𝗢𝗕𝗥𝗘𝗩𝗜𝗩𝗜𝗘𝗥𝗢𝗡 ◝ .\n\n𝖤𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖿𝗎𝖾 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝗒 𝖺𝗁𝗈𝗋𝖺 {', '.join(ganadores)} 𝗉𝗎𝖾𝖽𝖾𝗇 𝗏𝗈𝗅𝗏𝖾𝗋 𝖺 𝖼𝖺𝗌𝖺")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0Y1sWpDGFQQHzwJSrB9YNUygD0j8YEuAAI5BgACxL5BRIsEuKAHC3RbPAQ")
        
        sesion_zombie["activa"] = False
    elif len(sesion_zombie["vivos"]) <= 1:
        zombie_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == sesion_zombie["zombies"][0])
        premio_z2 = sesion_puntos.get("premio_actual", {}).get("zombie_zombie", 0)
        sumar_robux(zombie_obj["id"], zombie_obj["name"], premio_z2, "𝖹𝗈𝗆𝖻𝗂𝖾:")
        extra_z2 = f" (+{premio_z2} 𝖿𝗂𝖼𝗁𝖺𝗌)" if premio_z2 else ""
        await context.bot.send_message(chat_id=chat_id,
            text=f"𐑺 ៸ 𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦 ◝ .\n\n{zombie_obj['name']} 𝗆𝗈𝗋𝖽𝗂𝗈 𝖺 𝗍𝗈𝖽𝗈𝗌 𝗒 𝖼𝗈𝗇𝗏𝗂𝗋𝗍𝗂𝗈 𝖺𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌 𝖾𝗇 𝗈𝗍𝗋𝗈 𝖿𝗈𝖼𝗈 𝖽𝖾 𝗂𝗇𝖿𝖾𝖼𝖼𝗂𝗈𝗇 🧟‍♂️")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE")
        
        sesion_zombie["activa"] = False
    else:
        await pasar_a_siguiente_ataque(chat_id, context)

async def pasar_a_siguiente_ataque(chat_id, context):
    sesion_zombie["fase"] = "infeccion"
    for z_id in sesion_zombie["zombies"]:
        botones_ataque = [
            [InlineKeyboardButton(
                f"𝖬𝗈𝗋𝖽𝖾𝗋 𝖺 {next(j for j in sesion_zombie['jugadores'] if j['id'] == humano_id)['name']}",
                callback_data=f"morder:{humano_id}:{chat_id}"
            )]
            for humano_id in sesion_zombie["vivos"]
        ]
        try:
            await context.bot.send_message(chat_id=z_id,
                text="𝖮𝗍𝗋𝖺 𝗏𝖾𝗓 𝗌𝗂𝖾𝗇𝗍𝖾𝗌 𝖺𝗇𝗌𝗂𝖾𝖽𝖺𝖽 𝗉𝗈𝗋 𝗉𝗋𝗈𝖻𝖺𝗋 𝖼𝖺𝗋𝗇𝖾. 𝖤𝗅𝗂𝗀𝗎𝖾 𝖺 𝗍𝗎 𝗌𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝖼𝗈𝗇 𝗉𝗋𝖾𝖼𝖺𝗎𝖼𝗂𝗈𝗇.",
                reply_markup=InlineKeyboardMarkup(botones_ataque))
        except Exception:
            pass
    await context.bot.send_message(chat_id=chat_id,
        text="𝖫𝖺 𝗇𝗈𝖼𝗁𝖾 𝖼𝖺𝖾 𝗒 𝗌𝖾 𝖽𝖾𝖻𝖾𝗇 𝗉𝖺𝗀𝖺𝗋 𝗅𝖺𝗌 𝗅𝗎𝖼𝖾𝗌 𝖽𝖾𝗅 𝖺𝗎𝗍𝗈𝖻𝗎𝗌... 𝖤𝗅 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖾𝗌𝗍𝖺 𝖺𝗅 𝖺𝖼𝖾𝖼𝗁𝗈.")

# ================= MANEJO DE BOTONES =================

async def manejar_botones_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_zombie_click":
        await query.answer()
        if sesion_zombie.get("activa", False):
            await query.answer("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈 ᵎᵎ", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_zombie["jugadores"]):
            sesion_zombie["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"— {nombre_usuario(user)} 𝗌𝖾 𝗎𝗇𝗂𝗈 𝅄 𖹭' ა")

    elif query.data.startswith("morder:"):
        await query.answer()
        partes = query.data.split(":")
        victima_id = int(partes[1])
        grupo_chat_id = int(partes[2])

        if sesion_zombie.get("activa") and sesion_zombie.get("fase") == "infeccion":
            if user.id in sesion_zombie.get("zombies", []):
                if victima_id in sesion_zombie["vivos"]:
                    victima_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == victima_id)
                    sesion_zombie["vivos"].remove(victima_id)
                    sesion_zombie["jugadores"] = [j for j in sesion_zombie["jugadores"] if j["id"] != victima_id]

                    try:
                        await query.edit_message_caption(caption=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text=f"𝖠𝗍𝖺𝗊𝗎𝖾 𝖾𝗑𝗂𝗍𝗈𝗌𝗈. 𝖧𝖺𝗌 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝖺 {victima_obj['name']}.")

                    await context.bot.send_message(chat_id=grupo_chat_id,
                        text=f"¡𝗨𝗡 𝗔𝗧𝗔𝗤𝗨𝗘 𝗛𝗔 𝗢𝗖𝗨𝗥𝗥𝗜𝗗𝗢ⵑ\n\n{victima_obj['name']} 𝗁𝖺 𝗌𝗂𝖽𝗈 𝖺𝗍𝖺𝖼𝖺𝖽𝗈 𝖾𝗇 𝗅𝖺 𝗈𝗌𝖼𝗎𝗋𝗂𝖽𝖺𝖽 𝗉𝗈𝗋 𝗎𝗇 𝗓𝗈𝗆𝖻𝗂𝖾 𝗒 𝗌𝖾 𝖾𝗌𝗍𝖺 𝗍𝗋𝖺𝗇𝗌𝖿𝗈𝗋𝗆𝖺𝗇𝖽𝗈, 𝗍𝗎𝗏𝗈 𝗊𝗎𝖾 𝗌𝖾𝗋 𝖾𝗑𝗉𝗎𝗅𝗌𝖺𝖽𝗈 𝖽𝖾 𝗂𝗇𝗆𝖾𝖽𝗂𝖺𝗍𝗈.")
                    await asyncio.sleep(2)

                    if len(sesion_zombie["vivos"]) <= 1:
                        zombie_obj = next(j for j in sesion_zombie["jugadores"] if j["id"] == sesion_zombie["zombies"][0])
                        premio_z = sesion_puntos.get("premio_actual", {}).get("zombie_zombie", 0)
                        sumar_robux(zombie_obj["id"], zombie_obj["name"], premio_z, "𝖹𝗈𝗆𝖻𝗂𝖾:")
                        extra_z = f" (+{premio_z} 𝖿𝗂𝖼𝗁𝖺𝗌)" if premio_z else ""
                        await context.bot.send_message(chat_id=grupo_chat_id,
                            text=f"𐑺 ៸ 𝗬𝗔 𝗡𝗢 𝗤𝗨𝗘𝗗𝗔𝗡 𝗛𝗨𝗠𝗔𝗡𝗢𝗦 ◝ . {zombie_obj['name']} 𝗆𝗈𝗋𝖽𝗂𝗈 𝖺 𝗍𝗈𝖽𝗈𝗌 𝗒 𝗀𝖺𝗇𝗈 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺")
                        sesion_zombie["activa"] = False
                    else:
                        await abrir_votacion_zombie(grupo_chat_id, context)
                else:
                    try:
                        await query.edit_message_caption(caption="ⓘ ˖ ࣪ 𝖤𝗌𝗍𝖺 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾 ᵎᵎ")
                    except Exception:
                        await context.bot.send_message(chat_id=user.id, text="ⓘ ˖ ࣪ 𝖤𝗌𝗍𝖺 𝗏𝗂𝖼𝗍𝗂𝗆𝖺 𝗒𝖺 𝗇𝗈 𝖾𝗌𝗍𝖺 𝖽𝗂𝗌𝗉𝗈𝗇𝗂𝖻𝗅𝖾 ᵎᵎ")

    elif query.data.startswith("voto_z:"):
        await query.answer()
        votado_id = int(query.data.split(":")[1])
        if sesion_zombie.get("activa") and sesion_zombie.get("fase") == "votacion":
            if any(j["id"] == user.id for j in sesion_zombie["jugadores"]):
                sesion_zombie["votos"][user.id] = votado_id
                await query.answer("𝖵𝗈𝗍𝗈 𝖾𝗆𝗂𝗍𝗂𝖽𝗈 ✓", show_alert=True)
                await context.bot.send_message(chat_id=chat_id,
                    text=f"{nombre_usuario(user)} 𝖺𝖼𝖺𝖻𝖺 𝖽𝖾 𝖾𝗆𝗂𝗍𝗂𝗋 𝗌𝗎 𝗏𝗈𝗍𝗈.\n\n"
                         f"{len(sesion_zombie['votos'])}/{len(sesion_zombie['jugadores'])}  𝗏𝗈𝗍𝗈𝗌 𝖾𝗆𝗂𝗍𝗂𝖽𝗈𝗌")
                if len(sesion_zombie["votos"]) >= len(sesion_zombie["jugadores"]):
                    await procesar_resultados_votacion(chat_id, context)
            else:
                await query.answer("𝖴𝗉𝗌, 𝗍𝗎 𝗇𝗈 𝖾𝗌𝗍𝖺𝗌 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗇𝖽𝗈 𝖾𝗇 𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.", show_alert=True)
