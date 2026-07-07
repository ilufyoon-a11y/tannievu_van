import random
from telegram import Update
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# SÍMBOLOS Y PAGOS
# =====================================================================

SIMBOLOS = ["🍒", "🍋", "💎"]
PESOS    = [50,   35,   15]

PAGO_3 = 3
PAGO_2 = 1.5

# =====================================================================
# SESION GRUPAL
# =====================================================================

# chat_id -> {
#   "activa": bool,
#   "apuestas": { user_id: { "nombre", "cantidad" } }
# }
sesion_slots = {}

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def girar() -> list:
    return random.choices(SIMBOLOS, weights=PESOS, k=3)

def evaluar(ruletas: list, apuesta: int) -> tuple:
    a, b, c = ruletas
    if a == b == c:
        ganancia = int(apuesta * PAGO_3)
        return f"🎉 ¡𝖳𝖱𝖨𝖯𝖫𝖤 {a}! 𝗑{PAGO_3}", ganancia
    elif a == b or b == c or a == c:
        ganancia = int(apuesta * PAGO_2)
        return f"✨ ¡𝖯𝖠𝖱 𝗑{PAGO_2}!", ganancia
    else:
        return "💸 𝖲𝗂𝗇 𝗌𝗎𝖾𝗋𝗍𝖾...", 0

def sala_txt(chat_id: int) -> str:
    apuestas = sesion_slots[chat_id]["apuestas"]
    lineas = [
        "🎰 <b>SLOTS GRUPAL</b>\n",
        "<blockquote>𝖠𝗉𝗎𝖾𝗌𝗍𝖺 𝖼𝗈𝗇 <code>/apostar &lt;cantidad&gt;</code></blockquote>\n",
    ]
    if apuestas:
        lineas.append("<b>Jugadores:</b>")
        for d in apuestas.values():
            lineas.append(f"  🎰 {d['nombre']} — {d['cantidad']} 𝖿𝗂𝖼𝗁𝖺𝗌")
    else:
        lineas.append("<i>𝖭𝖺𝖽𝗂𝖾 𝗁𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝖽𝗈 𝖺𝗎𝗇...</i>")
    return "\n".join(lineas)

# =====================================================================
# /jackpot — Host abre la sala
# =====================================================================

async def cmd_open_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖼𝗍𝗂𝗏𝖺 𝖺𝗎𝗇, 𝗇𝖺𝖽𝗂𝖾 𝖼𝗎𝖾𝗇𝗍𝖺 𝖼𝗈𝗇 𝖿𝗂𝖼𝗁𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝗋. 𝖴𝗌𝖺 /new_session 𝗉𝗋𝗂𝗆𝖾𝗋𝗈.")
        return

    if chat_id in sesion_slots and sesion_slots[chat_id]["activa"]:
        await update.message.reply_text("𝖸𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗌𝖺𝗅𝖺 𝖽𝖾 𝗌𝗅𝗈𝗍𝗌 𝖺𝖻𝗂𝖾𝗋𝗍𝖺. 𝖴𝗌𝖺 /girar 𝗉𝖺𝗋𝖺 𝗋𝖾𝗏𝖾𝗅𝖺𝗋.")
        return

    sesion_slots[chat_id] = {
        "activa": True,
        "apuestas": {},
        "msg_id": None,
    }

    await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgEAAxkBA0urQGpJsaVbFkgF0QfZXwO_a7P4kHqiAAI5BQACwmFQRnvqQCAORooQPAQ")

    msg = await update.message.reply_text(sala_txt(chat_id), parse_mode="HTML")
    sesion_slots[chat_id]["msg_id"] = msg.message_id

# =====================================================================
# /apostar <cantidad> — Apostar
# =====================================================================

async def cmd_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /apostar 𝗉𝖺𝗋𝖺 𝗉𝖺𝗋𝗍𝗂𝖼𝗂𝗉𝖺𝗋.")
        return

    estado = sesion_slots.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text(
            "𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖺𝗅𝖺 𝖺𝖻𝗂𝖾𝗋𝗍𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /jackpot 𝗉𝖺𝗋𝖺 𝖺𝖻𝗋𝗂𝗋 𝗎𝗇𝖺, 𝗒 𝗅𝗎𝖾𝗀𝗈 /apostar &lt;cantidad&gt; 𝗉𝖺𝗋𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝗋."
        )
        return

    args = context.args or []
    if not args:
        await update.message.reply_text(
            "𝗣𝗿𝗲𝗺𝗶𝗼𝘀:\n"
            "𝟥 𝗂𝗀𝗎𝖺𝗅𝖾𝗌 → 𝗑𝟥 💰\n"
            "𝟤 𝗂𝗀𝗎𝖺𝗅𝖾𝗌 → 𝗑𝟣.𝟧 ✨\n"
            "𝖳𝗈𝖽𝗈𝗌 𝖽𝗂𝖿𝖾𝗋𝖾𝗇𝗍𝖾𝗌 → 𝗉𝗂𝖾𝗋𝖽𝖾𝗌 💸"
        )
        return

    try:
        cantidad = int(args[0])
    except ValueError:
        await update.message.reply_text("𝖫𝖺 𝖼𝖺𝗇𝗍𝗂𝖽𝖺𝖽 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗎𝗇 𝗇𝗎𝗆𝖾𝗋𝗈.")
        return

    if cantidad <= 0:
        await update.message.reply_text("𝖫𝖺 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗆𝖺𝗒𝗈𝗋 𝖺 𝟢")
        return

    saldo = get_saldo(user_id)
    if saldo < cantidad:
        await update.message.reply_text(
            f"❌ 𝖭𝗈 𝗍𝗂𝖾𝗇𝖾𝗌 𝗌𝗎𝖿𝗂𝖼𝗂𝖾𝗇𝗍𝖾𝗌 𝖿𝗂𝖼𝗁𝖺𝗌\n"
            f"𝖳𝗎 𝗌𝖺𝗅𝖽𝗈: {saldo} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
        return

    if user_id in estado["apuestas"]:
        estado["apuestas"][user_id]["cantidad"] = cantidad
        await update.message.reply_text(
            f"🔄 {nombre_usuario(user)} 𝖺𝖼𝗍𝗎𝖺𝗅𝗂𝗓𝗈 𝗌𝗎 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝖺 {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
    else:
        estado["apuestas"][user_id] = {
            "nombre": nombre_usuario(user),
            "cantidad": cantidad,
        }
        await update.message.reply_text(
            f"✅ {nombre_usuario(user)} 𝖺𝗉𝗈𝗌𝗍𝗈 {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=sala_txt(chat_id),
            parse_mode="HTML"
        )
    except Exception:
        pass

# =====================================================================
# /girar — Host revela
# =====================================================================

async def cmd_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_slots.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖻𝗂𝖾𝗋𝗍𝖺.")
        return

    apuestas_validas = {uid: d for uid, d in estado["apuestas"].items() if d["cantidad"] > 0}
    if not apuestas_validas:
        await update.message.reply_text("𝖭𝖺𝖽𝗂𝖾 𝗁𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝖽𝗈 𝖺𝗎𝗇.")
        return

    # Cerrar sala
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text="🎰 ¡𝖫𝖺𝗌 𝖺𝗉𝗎𝖾𝗌𝗍𝖺𝗌 𝖾𝗌𝗍𝖺𝗇 𝖼𝖾𝗋𝗋𝖺𝖽𝖺𝗌! 𝖦𝗂𝗋𝖺𝗇𝖽𝗈 𝗍𝗋𝖺𝗀𝖺 𝗆𝗈𝗇𝖾𝖽𝖺𝗌..."
        )
    except Exception:
        pass

    resultado_lines = ["🎰 𝗥𝗘𝗦𝗨𝗟𝗧𝗔𝗗𝗢𝗦:\n"]

    for user_id, datos in apuestas_validas.items():
        nombre = datos["nombre"]
        cantidad = datos["cantidad"]

        ruletas = girar()
        display = " | ".join(ruletas)
        resultado_txt, ganancia = evaluar(ruletas, cantidad)

        if ganancia > 0:
            sumar_robux(user_id, nombre, ganancia, f"Slots 🎰 (+x{int(ganancia//cantidad)})")
            resultado_lines.append(f"{nombre}\n[ {display} ]\n{resultado_txt} → +{ganancia} 𝖿𝗂𝖼𝗁𝖺𝗌\n")
        else:
            if user_id in sesion_puntos["jugadores"]:
                sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
                sesion_puntos["jugadores"][user_id]["detalle"].append(f"Slots 🎰: -{cantidad} 🟥")
            resultado_lines.append(f"{nombre}\n[ {display} ]\n{resultado_txt} → -{cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌\n")

    guardar_sesion()

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado_lines)
    )

    del sesion_slots[chat_id]
