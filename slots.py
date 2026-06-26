import random
from telegram import Update
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# SÍMBOLOS Y PAGOS
# =====================================================================

SIMBOLOS = ["🍒", "🍋", "💎"]
PESOS    = [50,   35,   15]

# Todos los triples pagan x3, todos los pares x1.5
PAGO_3 = 3
PAGO_2 = 1.5

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def girar() -> list:
    return random.choices(SIMBOLOS, weights=PESOS, k=3)

def evaluar(ruletas: list, apuesta: int) -> tuple[str, int]:
    a, b, c = ruletas
    if a == b == c:
        ganancia = int(apuesta * PAGO_3)
        return f"🎉 *¡TRIPLE {a}!* x{PAGO_3}", ganancia
    elif a == b or b == c or a == c:
        ganancia = int(apuesta * PAGO_2)
        return f"✨ *¡Par!* x{PAGO_2}", ganancia
    else:
        return "💸 *Sin suerte...*", 0

# =====================================================================
# /slots <apuesta>
# =====================================================================

async def cmd_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa. Usa /new_session primero.")
        return

    args = context.args or []
    if not args:
        await update.message.reply_text(
            "🎰 *TRAGAMONEDAS*\n\n"
            "Uso: `/slots <apuesta>`\n"
            "Ej: `/slots 20`\n\n"
            f"Tu saldo: *{get_saldo(user_id)} Robux 🟥*\n\n"
            "*Símbolos:* 🍒 · 🍋 · 💎\n\n"
            "*Premios:*\n"
            "3 iguales → x3 💰\n"
            "2 iguales → x1.5 ✨\n"
            "Todos diferentes → pierdes 💸",
            parse_mode="Markdown"
        )
        return

    try:
        apuesta = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ La apuesta debe ser un número.")
        return

    if apuesta <= 0:
        await update.message.reply_text("❌ La apuesta debe ser mayor a 0.")
        return

    saldo = get_saldo(user_id)
    if saldo < apuesta:
        await update.message.reply_text(
            f"❌ No tienes suficientes Robux.\n"
            f"Tu saldo: *{saldo} Robux 🟥*",
            parse_mode="Markdown"
        )
        return

    # Girar
    ruletas = girar()
    resultado_txt, ganancia = evaluar(ruletas, apuesta)
    display = " | ".join(ruletas)

    if ganancia > 0:
        sumar_robux(user_id, nombre_usuario(user), ganancia, f"Slots 🎰 (+x{ganancia//apuesta})")
        saldo_nuevo = get_saldo(user_id)
        msg = (
            f"🎰 *{nombre_usuario(user)}*\n\n"
            f"[ {display} ]\n\n"
            f"{resultado_txt}\n"
            f"💰 Ganaste *{ganancia} Robux 🟥*\n"
            f"Saldo: *{saldo_nuevo} Robux 🟥*"
        )
    else:
        # Restar apuesta
        if user_id in sesion_puntos["jugadores"]:
            sesion_puntos["jugadores"][user_id]["robux"] -= apuesta
            sesion_puntos["jugadores"][user_id]["detalle"].append(f"Slots 🎰: -{apuesta} 🟥")
            guardar_sesion()
        saldo_nuevo = get_saldo(user_id)
        msg = (
            f"🎰 *{nombre_usuario(user)}*\n\n"
            f"[ {display} ]\n\n"
            f"{resultado_txt}\n"
            f"💸 Perdiste *{apuesta} Robux 🟥*\n"
            f"Saldo: *{saldo_nuevo} Robux 🟥*"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")
