import random
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

logger = logging.getLogger(__name__)

# =====================================================================
# SÍMBOLOS Y PAGOS
# =====================================================================

SIMBOLOS = ["🍒", "🍋", "💎", "🐨", "🐹", "🐱", "🐿️", "🐥", "🐻", "🐰"]
PESOS    = [13,   11,   8,    7,    7,    6,    6,    5,    5,    6]

PAGO_3 = 4
PAGO_2 = 1.8

FRAMES_ANIMACION = 4
DELAY_ANIMACION = 0.6  # segundos entre frames (evita flood control de Telegram)

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def girar() -> list:
    return random.choices(SIMBOLOS, weights=PESOS, k=3)

def markup_ruletas(simbolos: list) -> InlineKeyboardMarkup:
    """3 botones inline que simulan los rodillos de la maquina."""
    botones = [
        InlineKeyboardButton(simbolos[i], callback_data="slots_noop")
        for i in range(3)
    ]
    return InlineKeyboardMarkup([botones])

async def cb_slots_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Los botones de la ruleta son solo visuales: no hacen nada al tocarlos."""
    await update.callback_query.answer()

def evaluar(ruletas: list, apuesta: int) -> tuple:
    a, b, c = ruletas
    if a == b == c:
        ganancia = int(apuesta * PAGO_3)
        return f"¡𝗧𝗥𝗜𝗣𝗟𝗘 {a}ⵑ 𝗑{PAGO_3}", ganancia, PAGO_3
    elif a == b or b == c or a == c:
        ganancia = int(apuesta * PAGO_2)
        return f"¡𝗣𝗔𝗥 𝗑{PAGO_2}ⵑ", ganancia, PAGO_2
    else:
        return "💸 𝖲𝗂𝗇 𝗌𝗎𝖾𝗋𝗍𝖾...", 0, 0

# =====================================================================
# /jackpot <cantidad> — Juega al instante
# =====================================================================

async def cmd_jackpot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id
    nombre = nombre_usuario(user)

    if not sesion_puntos["activa"]:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /new_session 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 ᵎᵎ")
        return

    args = context.args or []
    if not args:
        await update.message.reply_text(
            "𝖴𝗌𝗈: <code>/jackpot &lt;cantidad&gt;</code>\n\n"
            "𝗣𝗿𝗲𝗺𝗶𝗼𝘀:\n"
            "𝟥 𝗂𝗀𝗎𝖺𝗅𝖾𝗌 ➜ 𝗑𝟦 💰\n"
            "𝟤 𝗂𝗀𝗎𝖺𝗅𝖾𝗌 ➜ 𝗑𝟣.𝟪 ✨\n"
            "𝖳𝗈𝖽𝗈𝗌 𝖽𝗂𝖿𝖾𝗋𝖾𝗇𝗍𝖾𝗌 ➜ 𝗉𝗂𝖾𝗋𝖽𝖾𝗌 💸",
            parse_mode="HTML"
        )
        return

    try:
        cantidad = int(args[0])
    except ValueError:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖫𝖺 𝖼𝖺𝗇𝗍𝗂𝖽𝖺𝖽 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗎𝗇 𝗇𝗎𝗆𝖾𝗋𝗈 ᵎᵎ")
        return

    if cantidad <= 0:
        await update.message.reply_text("ⓘ ˖ ࣪ 𝖫𝖺 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝖽𝖾𝖻𝖾 𝗌𝖾𝗋 𝗆𝖺𝗒𝗈𝗋 𝖺 𝟢 ᵎᵎ")
        return

    saldo = get_saldo(user_id)
    if saldo < cantidad:
        await update.message.reply_text(
            f"ⓘ ˖ ࣪ 𝖭𝗈 𝗍𝗂𝖾𝗇𝖾𝗌 𝗌𝗎𝖿𝗂𝖼𝗂𝖾𝗇𝗍𝖾𝗌 𝖿𝗂𝖼𝗁𝖺𝗌 ᵎᵎ\n𝗦𝗮𝗹𝗱𝗼: {saldo} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
        return

    # Resultado real ya calculado desde el inicio (la animación es solo visual)
    ruletas = girar()

    encabezado = f"🎰 {nombre} 𝖾𝗌𝗍𝖺 𝗀𝗂𝗋𝖺𝗇𝖽𝗈 𝗉𝗈𝗋 {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌..."
    falso_inicial = [random.choice(SIMBOLOS) for _ in range(3)]
    msg = await update.message.reply_text(
        encabezado,
        reply_markup=markup_ruletas(falso_inicial)
    )

    # Animación: mueve los "rodillos" (botones) varias veces con combinaciones al azar.
    # Si Telegram tira flood control aquí, no pasa nada grave: seguimos al resultado final.
    for _ in range(FRAMES_ANIMACION):
        falso = [random.choice(SIMBOLOS) for _ in range(3)]
        try:
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=msg.message_id,
                reply_markup=markup_ruletas(falso)
            )
        except Exception as e:
            logger.warning(f"Slots: fallo animando frame ({e})")
        await asyncio.sleep(DELAY_ANIMACION)

    # Resultado final real
    resultado_txt, ganancia, multiplicador = evaluar(ruletas, cantidad)

    if ganancia > 0:
        sumar_robux(user_id, nombre, ganancia, f"Slots 🎰 (+x{multiplicador})")
        texto_final = (
            f"🎰 {nombre}\n\n"
            f"{resultado_txt} → +{ganancia} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
    else:
        if user_id in sesion_puntos["jugadores"]:
            sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
            sesion_puntos["jugadores"][user_id]["detalle"].append(f"Slots 🎰: -{cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌")
        texto_final = (
            f"🎰 {nombre}\n\n"
            f"{resultado_txt} → -{cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )

    guardar_sesion()

    # Si falla la edición final (flood control, mensaje borrado, etc),
    # mandamos el resultado como mensaje nuevo para que NUNCA se quede sin respuesta.
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=texto_final,
            reply_markup=markup_ruletas(ruletas)
        )
    except Exception as e:
        logger.warning(f"Slots: fallo mostrando resultado final, mando mensaje nuevo ({e})")
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=texto_final,
                reply_markup=markup_ruletas(ruletas)
            )
        except Exception as e2:
            logger.error(f"Slots: fallo total al enviar resultado ({e2})")
