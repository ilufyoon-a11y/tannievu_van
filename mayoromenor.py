import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# DECK BTS 💜
# =====================================================================

DECK = [
    {"valor": 1,  "nombre": "RM",          "imagen": "https://i.postimg.cc/placeholder_rm.jpg"},
    {"valor": 2,  "nombre": "Jin",         "imagen": "https://i.postimg.cc/placeholder_jin.jpg"},
    {"valor": 3,  "nombre": "Suga",        "imagen": "https://i.postimg.cc/placeholder_suga.jpg"},
    {"valor": 4,  "nombre": "J-Hope",      "imagen": "https://i.postimg.cc/placeholder_jhope.jpg"},
    {"valor": 5,  "nombre": "Jimin",       "imagen": "https://i.postimg.cc/placeholder_jimin.jpg"},
    {"valor": 6,  "nombre": "V",           "imagen": "https://i.postimg.cc/placeholder_v.jpg"},
    {"valor": 7,  "nombre": "Jungkook",    "imagen": "https://i.postimg.cc/placeholder_jk.jpg"},
    {"valor": 8,  "nombre": "RM + Jin",    "imagen": "https://i.postimg.cc/placeholder_rmjin.jpg"},
    {"valor": 9,  "nombre": "Suga + J-Hope","imagen": "https://i.postimg.cc/placeholder_sugahope.jpg"},
    {"valor": 10, "nombre": "Pista 🎵",    "imagen": "https://i.postimg.cc/placeholder_pista.jpg"},
    {"valor": 11, "nombre": "Dynamite ✨", "imagen": "https://i.postimg.cc/placeholder_dynamite.jpg"},
    {"valor": 12, "nombre": "Butter 🧈",   "imagen": "https://i.postimg.cc/placeholder_butter.jpg"},
    {"valor": 13, "nombre": "ARMY 💜",     "imagen": "https://i.postimg.cc/placeholder_army.jpg"},
]

# =====================================================================
# SESION
# =====================================================================

sesion_mom = {}
# user_id -> {
#   "carta_actual": { valor, nombre, imagen },
#   "apuesta": int,
#   "chat_id": int,
#   "msg_id": int,   # id del mensaje de la carta para editarlo
# }

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def carta_aleatoria(excluir_valor=None):
    opciones = [c for c in DECK if c["valor"] != excluir_valor]
    return random.choice(opciones)

# =====================================================================
# COMANDO PRINCIPAL
# =====================================================================

async def cmd_mayoromenor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa. Pide que usen /new_session primero.")
        return

    # Parsear apuesta
    args = context.args or []
    if not args:
        await update.message.reply_text(
            "💜 **Mayor o Menor BTS**\n\n"
            "Usa: `/mayoromenor <apuesta>`\n"
            "Ejemplo: `/mayoromenor 10`\n\n"
            f"Tu saldo actual: **{get_saldo(user_id)} Robux 🟥**",
            parse_mode="Markdown"
        )
        return

    try:
        apuesta = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ La apuesta debe ser un número. Ej: `/mayoromenor 10`", parse_mode="Markdown")
        return

    if apuesta <= 0:
        await update.message.reply_text("❌ La apuesta debe ser mayor a 0.")
        return

    saldo = get_saldo(user_id)
    if saldo < apuesta:
        await update.message.reply_text(
            f"❌ No tienes suficientes Robux.\n"
            f"Tu saldo: **{saldo} Robux 🟥**\n"
            f"Apuesta: **{apuesta} Robux**",
            parse_mode="Markdown"
        )
        return

    if user_id in sesion_mom:
        await update.message.reply_text("⚠️ Ya tienes una ronda en curso. ¡Responde primero!")
        return

    # Sacar carta
    carta = carta_aleatoria()
    sesion_mom[user_id] = {
        "carta_actual": carta,
        "apuesta": apuesta,
        "chat_id": update.effective_chat.id,
    }

    botones = [[
        InlineKeyboardButton("⬆️ MAYOR", callback_data=f"mom_mayor_{user_id}"),
        InlineKeyboardButton("⬇️ MENOR", callback_data=f"mom_menor_{user_id}"),
    ]]

    msg = await update.message.reply_photo(
        photo=carta["imagen"],
        caption=(
            f"💜 **MAYOR O MENOR** — {nombre_usuario(user)}\n\n"
            f"🃏 Carta actual: **{carta['nombre']}** (valor {carta['valor']})\n"
            f"💰 Apuesta: **{apuesta} Robux 🟥**\n\n"
            f"¿La siguiente carta será mayor o menor?"
        ),
        reply_markup=InlineKeyboardMarkup(botones),
        parse_mode="Markdown"
    )
    sesion_mom[user_id]["msg_id"] = msg.message_id

# =====================================================================
# MANEJO DE BOTONES
# =====================================================================

async def manejar_botones_mayoromenor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    # Extraer acción y dueño de la ronda
    partes = data.split("_")   # mom_mayor_123 o mom_menor_123
    accion = partes[1]         # "mayor" o "menor"
    dueno_id = int(partes[2])

    # Solo el dueño puede responder
    if user.id != dueno_id:
        await query.answer("¡Esta ronda no es tuya! 👀", show_alert=True)
        return

    if dueno_id not in sesion_mom:
        await query.answer("Esta ronda ya terminó.", show_alert=True)
        return

    await query.answer()

    datos = sesion_mom.pop(dueno_id)
    carta_anterior = datos["carta_actual"]
    apuesta = datos["apuesta"]

    # Sacar nueva carta (distinta a la anterior)
    carta_nueva = carta_aleatoria(excluir_valor=carta_anterior["valor"])

    # Evaluar resultado
    if accion == "mayor":
        gano = carta_nueva["valor"] > carta_anterior["valor"]
    else:
        gano = carta_nueva["valor"] < carta_anterior["valor"]

    # Empate = pierde (carta_aleatoria excluye el mismo valor, pero por si acaso)
    if carta_nueva["valor"] == carta_anterior["valor"]:
        gano = False

    nombre = nombre_usuario(user)

    if gano:
        ganancia = apuesta * 2
        sumar_robux(dueno_id, nombre, ganancia, f"Mayor o Menor 🃏 (+x2)")
        resultado_txt = (
            f"🎉 **¡ACERTASTE, {nombre.upper()}!** 💜\n\n"
            f"🃏 Carta anterior: **{carta_anterior['nombre']}** (valor {carta_anterior['valor']})\n"
            f"🃏 Carta nueva: **{carta_nueva['nombre']}** (valor {carta_nueva['valor']})\n\n"
            f"💰 Ganaste: **{ganancia} Robux 🟥** (x2)\n"
            f"Saldo actual: **{get_saldo(dueno_id)} Robux 🟥**"
        )
    else:
        # Restar del saldo
        if dueno_id in sesion_puntos["jugadores"]:
            sesion_puntos["jugadores"][dueno_id]["robux"] -= apuesta
            sesion_puntos["jugadores"][dueno_id]["detalle"].append(f"Mayor o Menor 🃏: -{apuesta} 🟥")
            guardar_sesion()
        resultado_txt = (
            f"💀 **¡FALLASTE, {nombre.upper()}!**\n\n"
            f"🃏 Carta anterior: **{carta_anterior['nombre']}** (valor {carta_anterior['valor']})\n"
            f"🃏 Carta nueva: **{carta_nueva['nombre']}** (valor {carta_nueva['valor']})\n\n"
            f"💸 Perdiste: **{apuesta} Robux 🟥**\n"
            f"Saldo actual: **{get_saldo(dueno_id)} Robux 🟥**"
        )

    await context.bot.send_photo(
        chat_id=datos["chat_id"],
        photo=carta_nueva["imagen"],
        caption=resultado_txt,
        parse_mode="Markdown"
    )

    # Editar mensaje original para quitar los botones
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=datos["chat_id"],
            message_id=datos["msg_id"],
            reply_markup=None
        )
    except Exception:
        pass
