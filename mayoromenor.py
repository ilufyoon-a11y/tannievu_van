import random
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion, migrar_si_existe_fake

# =====================================================================
# DECK BTS 💜
# =====================================================================

DECK = [
    {"valor": 1,  "nombre": "1",  "sticker": "CAACAgEAAxkBA06XtWpNDS11VmwviUkjHjFx35IKkcyXAAJuBwAC3-tpRuYEP-zDFRyDPAQ"},
    {"valor": 2,  "nombre": "2",  "sticker": "CAACAgEAAxkBA06XxmpNDTUhAtaCwUnwz0JuVbh0ckiXAAKFBwACMD9pRmvNtf0SvmsiPAQ"},
    {"valor": 3,  "nombre": "3",  "sticker": "CAACAgEAAxkBA06XzWpNDTkR92uIL-sJmAABAVYYdslLKAACOAcAAuoZYUanP913qO_KyjwE"},
    {"valor": 4,  "nombre": "4",  "sticker": "CAACAgEAAxkBA06Xz2pNDTtufesmFIgnTQnQpwAB8_uJ5AACiAcAAuYgaEa3q89_azqK1TwE"},
    {"valor": 5,  "nombre": "5",  "sticker": "CAACAgEAAxkBA06X12pNDTwCn4qvpkg_NVtPSAHSCWySAAJvCAACNVlgRmVRHb-o5woLPAQ"},
    {"valor": 6,  "nombre": "6",  "sticker": "CAACAgEAAxkBA06X22pNDT1Q2daV20-c2uCAlLRXZUI6AAJiBgACf0hgRqXl_7f0Q4dtPAQ"},
    {"valor": 7,  "nombre": "7",  "sticker": "CAACAgEAAxkBA06X3WpNDT5my8VxNmOrrKZgOStwt9J1AALvBwACH5NgRtwEsYKUjiA3PAQ"},
    {"valor": 8,  "nombre": "8",  "sticker": "CAACAgEAAxkBA06X4GpNDUC4SclZrbhkNM3hMGnHiFRVAAIlCAACRXVgRtMor_JJcvVwPAQ"},
    {"valor": 9,  "nombre": "9",  "sticker": "CAACAgEAAxkBA06X42pNDUEgacDeoUyRVdctmqLXZaT8AAICCgAClrtpRmIg7SNkYkZLPAQ"},
    {"valor": 10, "nombre": "10", "sticker": "CAACAgEAAxkBA06X5mpNDUPDNKnCq2U8BPKni9q9f5KyAAIBCAACwLNgRh4AAZicbHgWmjwE"},
    {"valor": 11, "nombre": "11", "sticker": "CAACAgEAAxkBA06X6GpNDUTe67UwkJa6Zvb9Nw7vojnHAAJ4BgACyPVoRuaMKS0JGRjRPAQ"},
    {"valor": 12, "nombre": "12", "sticker": "CAACAgEAAxkBA06X6mpNDUV26bGTWqxN1wWcaNYFq-PlAAKBCAACHCRoRhKxD7xMFZYpPAQ"},
]

# =====================================================================
# SESION GRUPAL
# =====================================================================

# chat_id -> {
#   "activa": bool,
#   "carta_actual": { valor, nombre, sticker },
#   "sticker_msg_id": int,
#   "sala_msg_id": int,
#   "apuestas": { user_id: { "nombre", "eleccion", "cantidad" } }
# }
sesion_mom = {}

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def carta_aleatoria(excluir_valor=None):
    opciones = [c for c in DECK if c["valor"] != excluir_valor]
    return random.choice(opciones)

def texto_sala(chat_id: int) -> str:
    estado = sesion_mom[chat_id]
    carta = estado["carta_actual"]
    apuestas = estado["apuestas"]
    lineas = [
        f"<b>๑ ꞈ 𝗠𝗔𝗬𝗢𝗥 𝗢 𝗠𝗘𝗡𝗢𝗥 ⋆ ٠\n</b>",
        "<blockquote>𝖠𝗉𝗎𝖾𝗌𝗍𝖺 𝖼𝗈𝗇: <code>/beat mayor &lt;cantidad&gt;</code> 𝗈 <code>/beat menor &lt;cantidad&gt;</code></blockquote>\n",
    ]

# =====================================================================
# /mayoromenor — Host abre la ronda
# =====================================================================

async def cmd_mayoromenor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖼𝗍𝗂𝗏𝖺 𝖺𝗎𝗇, 𝗇𝖺𝖽𝗂𝖾 𝖼𝗎𝖾𝗇𝗍𝖺 𝖼𝗈𝗇 𝖿𝗂𝖼𝗁𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝗋.\n\n𝖴𝗌𝖺 /new_session 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 ᵎᵎ")
        return

    if chat_id in sesion_mom and sesion_mom[chat_id]["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖸𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗌𝖺𝗅𝖺 𝖺𝖻𝗂𝖾𝗋𝗍𝖺. \n\n𝖴𝗌𝖺 /out_card 𝗉𝖺𝗋𝖺 𝗋𝖾𝗏𝖾𝗅𝖺𝗋 ᵎᵎ")
        return

    carta = carta_aleatoria()
    sesion_mom[chat_id] = {
        "activa": True,
        "carta_actual": carta,
        "sticker_msg_id": None,
        "sala_msg_id": None,
        "apuestas": {},
    }

    sticker_msg = await update.message.reply_sticker(sticker=carta["sticker"])
    sesion_mom[chat_id]["sticker_msg_id"] = sticker_msg.message_id

    msg = await update.message.reply_text(
        texto_sala(chat_id)
    )
    sesion_mom[chat_id]["sala_msg_id"] = msg.message_id

# =====================================================================
# /beat <mayor|menor> <cantidad>
# =====================================================================

async def cmd_beat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = migrar_si_existe_fake(user)
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 `/mom` 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ")
        return

    estado = sesion_mom.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 `/mom` 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 ᵎᵎ")
        return

    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text(
            "𝖠𝗉𝗎𝖾𝗌𝗍𝖺 𝖼𝗈𝗇: <code>/beat mayor &lt;cantidad&gt;</code> 𝗈 <code>/beat menor &lt;cantidad&gt;</code></blockquote>",
            parse_mode="HTML"
        )
        return

    eleccion = args[0].lower()
    if eleccion not in ("mayor", "menor"):
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖣𝖾𝖻𝖾𝗌 𝖾𝗌𝖼𝗋𝗂𝖻𝗂𝗋 mayor 𝗈 menor ᵎᵎ")
        return

    try:
        cantidad = int(args[1])
    except ValueError:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖫𝖺 𝖼𝖺𝗇𝗍𝗂𝖽𝖺𝖽 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗎𝗇 𝗇𝗎𝗆𝖾𝗋𝗈 ᵎᵎ")
        return

    if cantidad <= 0:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖫𝖺 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗆𝖺𝗒𝗈𝗋 𝖺 𝟢 ᵎᵎ")
        return

    saldo = get_saldo(user_id)
    if saldo < cantidad:
        await update.message.reply_text(
            f"ⓘ ˖ ࣪ 𝖭𝗈 𝗍𝗂𝖾𝗇𝖾𝗌 𝗌𝗎𝖿𝗂𝖼𝗂𝖾𝗇𝗍𝖾𝗌 𝖿𝗂𝖼𝗁𝖺𝗌 ᵎᵎ\n"
            f"𝗦𝗮𝗹𝗱𝗼: {saldo} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
        return

    if user_id in estado["apuestas"]:
        # Actualizar apuesta existente
        estado["apuestas"][user_id]["eleccion"] = eleccion
        estado["apuestas"][user_id]["cantidad"] = cantidad
        await update.message.reply_text(
            f"— {nombre_usuario(user)} 𝖺𝖼𝗍𝗎𝖺𝗅𝗂𝗓𝗈 𝗌𝗎 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝖺 "
            f"{'MAYOR' if eleccion == 'mayor' else 'MENOR'} — {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌 𝅄 𖹭' ა"
        )
    else:
        estado["apuestas"][user_id] = {
            "nombre": nombre_usuario(user),
            "eleccion": eleccion,
            "cantidad": cantidad,
        }
        await update.message.reply_text(
            f"— {nombre_usuario(user)} 𝖺𝗉𝗈𝗌𝗍𝗈 {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌 𝖺 "
            f"{'MAYOR' if eleccion == 'mayor' else 'MENOR'} 𝅄 𖹭' ა"
        )

    # Actualizar mensaje de sala
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["sala_msg_id"],
            text=texto_sala(chat_id)
        )
    except Exception:
        pass

# =====================================================================
# /out_card — Host revela la carta y liquida
# =====================================================================

async def cmd_out_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_mom.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖻𝗂𝖾𝗋𝗍𝖺 ᵎᵎ")
        return

    apuestas_validas = {uid: d for uid, d in estado["apuestas"].items() if d["cantidad"] > 0}
    if not apuestas_validas:
        await update.message.reply_text("𝖭𝖺𝖽𝗂𝖾 𝗁𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝖽𝗈 𝖺𝗎𝗇.")
        return

    carta_anterior = estado["carta_actual"]
    carta_nueva = carta_aleatoria(excluir_valor=carta_anterior["valor"])

    await context.bot.send_sticker(chat_id=chat_id, sticker=carta_nueva["sticker"])

    ganadores = []
    perdedores = []

    for user_id, datos in apuestas_validas.items():
        nombre = datos["nombre"]
        cantidad = datos["cantidad"]
        eleccion = datos["eleccion"]

        gano = (eleccion == "mayor" and carta_nueva["valor"] > carta_anterior["valor"]) or \
               (eleccion == "menor" and carta_nueva["valor"] < carta_anterior["valor"])

        if gano:
            ganancia = cantidad * 2
            sumar_robux(user_id, nombre, ganancia, "𝗠𝗔𝗬𝗢𝗥 𝗢 𝗠𝗘𝗡𝗢𝗥 🃏 (x2)")
            ganadores.append(f"  {'⬆️' if eleccion == 'mayor' else '⬇️'} {nombre} ➜ +{ganancia} 𝖿𝗂𝖼𝗁𝖺𝗌")
        else:
            if user_id in sesion_puntos["jugadores"]:
                sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
                sesion_puntos["jugadores"][user_id]["detalle"].append(f"𝗠𝗔𝗬𝗢𝗥 𝗢 𝗠𝗘𝗡𝗢𝗥 🃏: -{cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌")
            perdedores.append(f"  {'⬆️' if eleccion == 'mayor' else '⬇️'} {nombre} ➜ -{cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌")

    guardar_sesion()

    resultado = [
        f"🃏 𝗖𝗮𝗿𝘁𝗮 𝗮𝗻𝘁𝗲𝗿𝗶𝗼𝗿: {carta_anterior['nombre']} (valor {carta_anterior['valor']})\n"
        f"🃏 𝗖𝗮𝗿𝘁𝗮 𝗻𝘂𝗲𝘃𝗮: {carta_nueva['nombre']} (valor {carta_nueva['valor']})\n"
    ]
    if ganadores:
        resultado.append("っ⠀˖⠀꒰⠀𝗚𝗔𝗡𝗔𝗗𝗢𝗥𝗘𝗦⠀꒱\n")
        resultado.extend(ganadores)
    if perdedores:
        resultado.append("\n\nっ⠀˖⠀꒰⠀𝗣𝗘𝗥𝗗𝗘𝗗𝗢𝗥𝗘𝗦⠀꒱")
        resultado.extend(perdedores)

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado)
    )

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=estado["sala_msg_id"],
            reply_markup=None
        )
    except Exception:
        pass

    del sesion_mom[chat_id]
