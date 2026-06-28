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
        return f"🎉 *¡TRIPLE {a}!* x{PAGO_3}", ganancia
    elif a == b or b == c or a == c:
        ganancia = int(apuesta * PAGO_2)
        return f"✨ *¡Par!* x{PAGO_2}", ganancia
    else:
        return "💸 *Sin suerte...*", 0

def sala_txt(chat_id: int) -> str:
    apuestas = sesion_slots[chat_id]["apuestas"]
    lineas = [
        "🎰 *SLOTS GRUPAL*\n",
        "Apuesta con `/slots <cantidad>`\n",
    ]
    if apuestas:
        lineas.append("*Jugadores:*")
        for d in apuestas.values():
            lineas.append(f"  🎰 {d['nombre']} — {d['cantidad']} Robux 🟥")
    else:
        lineas.append("_Nadie ha apostado aún..._")
    lineas.append("\n⏳ El host revela con `/spin`")
    return "\n".join(lineas)

# =====================================================================
# /open_slots — Host abre la sala
# =====================================================================

async def cmd_open_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa. Usa /new_session primero.")
        return

    if chat_id in sesion_slots and sesion_slots[chat_id]["activa"]:
        await update.message.reply_text("⚠️ Ya hay una sala de slots abierta. Usa /spin para revelar.")
        return

    sesion_slots[chat_id] = {
        "activa": True,
        "apuestas": {},
        "msg_id": None,
    }

    msg = await update.message.reply_text(sala_txt(chat_id), parse_mode="Markdown")
    sesion_slots[chat_id]["msg_id"] = msg.message_id

# =====================================================================
# /slots <cantidad> — Apostar
# =====================================================================

async def cmd_slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa.")
        return

    estado = sesion_slots.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text(
            "⚠️ No hay ninguna sala abierta. El host debe usar /open_slots primero."
        )
        return

    args = context.args or []
    if not args:
        await update.message.reply_text(
            "🎰 Uso: `/slots <cantidad>`\n"
            "Ej: `/slots 20`\n\n"
            "*Premios:*\n"
            "3 iguales → x3 💰\n"
            "2 iguales → x1.5 ✨\n"
            "Todos diferentes → pierdes 💸",
            parse_mode="Markdown"
        )
        return

    try:
        cantidad = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número.")
        return

    if cantidad <= 0:
        await update.message.reply_text("❌ La apuesta debe ser mayor a 0.")
        return

    saldo = get_saldo(user_id)
    if saldo < cantidad:
        await update.message.reply_text(
            f"❌ No tienes suficientes Robux.\n"
            f"Tu saldo: *{saldo} Robux 🟥*",
            parse_mode="Markdown"
        )
        return

    if user_id in estado["apuestas"]:
        estado["apuestas"][user_id]["cantidad"] = cantidad
        await update.message.reply_text(
            f"🔄 *{nombre_usuario(user)}* actualizó su apuesta a *{cantidad} Robux 🟥*",
            parse_mode="Markdown"
        )
    else:
        estado["apuestas"][user_id] = {
            "nombre": nombre_usuario(user),
            "cantidad": cantidad,
        }
        await update.message.reply_text(
            f"✅ *{nombre_usuario(user)}* apostó *{cantidad} Robux 🟥*",
            parse_mode="Markdown"
        )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=sala_txt(chat_id),
            parse_mode="Markdown"
        )
    except Exception:
        pass

# =====================================================================
# /spin — Host revela
# =====================================================================

async def cmd_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_slots.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sala abierta.")
        return

    apuestas_validas = {uid: d for uid, d in estado["apuestas"].items() if d["cantidad"] > 0}
    if not apuestas_validas:
        await update.message.reply_text("⚠️ Nadie apostó aún.")
        return

    # Cerrar sala
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text="🎰 *¡Las apuestas están cerradas!* Girando ruletas... 🎲",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    resultado_lines = ["🎰 *RESULTADOS*\n"]

    for user_id, datos in apuestas_validas.items():
        nombre = datos["nombre"]
        cantidad = datos["cantidad"]

        ruletas = girar()
        display = " | ".join(ruletas)
        resultado_txt, ganancia = evaluar(ruletas, cantidad)

        if ganancia > 0:
            sumar_robux(user_id, nombre, ganancia, f"Slots 🎰 (+x{int(ganancia//cantidad)})")
            resultado_lines.append(f"*{nombre}*\n[ {display} ]\n{resultado_txt} → +{ganancia} Robux 🟥\n")
        else:
            if user_id in sesion_puntos["jugadores"]:
                sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
                sesion_puntos["jugadores"][user_id]["detalle"].append(f"Slots 🎰: -{cantidad} 🟥")
            resultado_lines.append(f"*{nombre}*\n[ {display} ]\n{resultado_txt} → -{cantidad} Robux 🟥\n")

    guardar_sesion()

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado_lines),
        parse_mode="Markdown"
    )

    del sesion_slots[chat_id]
