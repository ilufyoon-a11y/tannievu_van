import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# DECK BTS 💜
# =====================================================================

DECK = [
    {"valor": 1,  "nombre": "1",  "sticker": "CAACAgEAAxkBA0JOY2o-CCpcElDKsSfaDRQDffJYgmnfAALeCAACMPnxRZH_1aP_xSgFPAQ"},
    {"valor": 2,  "nombre": "2",  "sticker": "CAACAgEAAxkBA0K6vWo-gOdDrp6tlzKPco6tvcn9aflkAAIbCAACQArwRV0usVlcD-HVPAQ"},
    {"valor": 3,  "nombre": "3",  "sticker": "CAACAgEAAxkBA0K6ymo-gPdXtp1ougXumlvIuIbfN4jlAAJLBwAC25XxRSXnl8LF2KdaPAQ"},
    {"valor": 4,  "nombre": "4",  "sticker": "CAACAgEAAxkBA0K63Go-gQLB0AetwN5qzd7OeM_v8iHKAAKFCgACrDnwRVE0GUO8TyYJPAQ"},
    {"valor": 5,  "nombre": "5",  "sticker": "CAACAgEAAxkBA0K65mo-gQyxEBlka9ZvUbS7o8ZXLEmOAAKzDAACphTwRWEp3q1JY49mPAQ"},
    {"valor": 6,  "nombre": "6",  "sticker": "CAACAgEAAxkBA0K672o-gRVMgV4c-5xqnjMSxzCNQKs5AAJPBwACRAAB8UXacZU9f28nuDwE"},
    {"valor": 7,  "nombre": "7",  "sticker": "CAACAgEAAxkBA0K6-mo-gR3YU2ZiIIja5frkYxv-q0LiAAIqCQACuYzwRUo7MslPG1yHPAQ"},
    {"valor": 8,  "nombre": "8",  "sticker": "CAACAgEAAxkBA0K7A2o-gSVH1OSp9C599u1z4EUjQWxWAAKMCAACQv3wReN0rglTopGjPAQ"},
    {"valor": 9,  "nombre": "9",  "sticker": "CAACAgEAAxkBA0K7Cmo-gS6b_HIa1X_lt-340qbkK53vAAKcCQACdpzwRY3foSjUNu9TPAQ"},
    {"valor": 10, "nombre": "10", "sticker": "CAACAgEAAxkBA0K7Fmo-gTaXMNgAAT_53mVAnFNHa6fQzQAC7AgAAiT68UVXXU7fF4fpuDwE"},
    {"valor": 11, "nombre": "11", "sticker": "CAACAgEAAxkBA0K7IWo-gT3M-ujSwPBNWRNVKRNG4kZMAAIrDgACspzwRdGMkNjlex7wPAQ"},
    {"valor": 12, "nombre": "12", "sticker": "CAACAgEAAxkBA0K7LGo-gUTBUZmL56rD-pEF-t_Z96mhAAKECAAChMDxRT_nWpG6uKBmPAQ"},
]

# =====================================================================
# SESION GRUPAL
# =====================================================================

# chat_id -> {
#   "activa": bool,
#   "carta_actual": { valor, nombre, sticker },
#   "msg_id": int,       # mensaje de sala (texto con apuestas)
#   "sticker_msg_id": int,  # mensaje del sticker de la carta actual
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
        f"💜 *MAYOR O MENOR* — Carta actual: *{carta['nombre']}*\n",
        "Elige con los botones y luego escribe `/apostar_mom <cantidad>`\n",
    ]
    if apuestas:
        lineas.append("*Jugadores:*")
        for d in apuestas.values():
            flecha = "⬆️" if d["eleccion"] == "mayor" else "⬇️"
            cantidad_txt = f"{d['cantidad']} Robux 🟥" if d["cantidad"] > 0 else "_(falta apuesta)_"
            lineas.append(f"{flecha} {d['nombre']} — {cantidad_txt}")
    else:
        lineas.append("_Nadie ha apostado aún..._")
    lineas.append("\n⏳ El host revela con `/out_card`")
    return "\n".join(lineas)

# =====================================================================
# /mayoromenor — Host abre la ronda
# =====================================================================

async def cmd_mayoromenor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa. Usa /new_session primero.")
        return

    if chat_id in sesion_mom and sesion_mom[chat_id]["activa"]:
        await update.message.reply_text("⚠️ Ya hay una ronda abierta. Usa /out_card para revelar.")
        return

    carta = carta_aleatoria()
    sesion_mom[chat_id] = {
        "activa": True,
        "carta_actual": carta,
        "msg_id": None,
        "sticker_msg_id": None,
        "apuestas": {},
    }

    # Mandar sticker de la carta
    sticker_msg = await update.message.reply_sticker(sticker=carta["sticker"])
    sesion_mom[chat_id]["sticker_msg_id"] = sticker_msg.message_id

    botones = [[
        InlineKeyboardButton("⬆️ MAYOR", callback_data=f"mom_mayor_{chat_id}"),
        InlineKeyboardButton("⬇️ MENOR", callback_data=f"mom_menor_{chat_id}"),
    ]]

    msg = await update.message.reply_text(
        texto_sala(chat_id),
        reply_markup=InlineKeyboardMarkup(botones),
        parse_mode="Markdown"
    )
    sesion_mom[chat_id]["msg_id"] = msg.message_id

# =====================================================================
# BOTONES — elegir mayor o menor
# =====================================================================

async def manejar_botones_mayoromenor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    partes = data.split("_")
    eleccion = partes[1]
    chat_id = int(partes[2])

    estado = sesion_mom.get(chat_id)
    if not estado or not estado["activa"]:
        await query.answer("Esta ronda ya terminó.", show_alert=True)
        return

    user_id = user.id

    if user_id in estado["apuestas"]:
        estado["apuestas"][user_id]["eleccion"] = eleccion
        await query.answer(f"Cambiaste a {'⬆️ MAYOR' if eleccion == 'mayor' else '⬇️ MENOR'}", show_alert=False)
    else:
        estado["apuestas"][user_id] = {
            "nombre": nombre_usuario(user),
            "eleccion": eleccion,
            "cantidad": 0,
        }
        await query.answer(f"{'⬆️ MAYOR' if eleccion == 'mayor' else '⬇️ MENOR'} elegido! Ahora escribe /apostar_mom <cantidad>", show_alert=True)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=texto_sala(chat_id),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬆️ MAYOR", callback_data=f"mom_mayor_{chat_id}"),
                InlineKeyboardButton("⬇️ MENOR", callback_data=f"mom_menor_{chat_id}"),
            ]]),
            parse_mode="Markdown"
        )
    except Exception:
        pass

# =====================================================================
# /apostar_mom <cantidad>
# =====================================================================

async def cmd_apostar_mom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa.")
        return

    estado = sesion_mom.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna ronda abierta. El host debe usar /mayoromenor primero.")
        return

    if user_id not in estado["apuestas"]:
        await update.message.reply_text("⚠️ Primero elige ⬆️ MAYOR o ⬇️ MENOR con los botones.")
        return

    args = context.args or []
    if not args:
        await update.message.reply_text("❌ Uso: `/apostar_mom <cantidad>`", parse_mode="Markdown")
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
            f"Tu saldo: *{saldo} Robux 🟥*\n"
            f"Apuesta: *{cantidad} Robux*",
            parse_mode="Markdown"
        )
        return

    estado["apuestas"][user_id]["cantidad"] = cantidad
    eleccion = estado["apuestas"][user_id]["eleccion"]
    flecha = "⬆️ MAYOR" if eleccion == "mayor" else "⬇️ MENOR"

    await update.message.reply_text(
        f"✅ *{nombre_usuario(user)}* apostó *{cantidad} Robux 🟥* a {flecha}",
        parse_mode="Markdown"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=texto_sala(chat_id),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬆️ MAYOR", callback_data=f"mom_mayor_{chat_id}"),
                InlineKeyboardButton("⬇️ MENOR", callback_data=f"mom_menor_{chat_id}"),
            ]]),
            parse_mode="Markdown"
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
        await update.message.reply_text("⚠️ No hay ninguna ronda abierta.")
        return

    apuestas_validas = {uid: d for uid, d in estado["apuestas"].items() if d["cantidad"] > 0}
    if not apuestas_validas:
        await update.message.reply_text("⚠️ Nadie apostó aún.")
        return

    carta_anterior = estado["carta_actual"]
    carta_nueva = carta_aleatoria(excluir_valor=carta_anterior["valor"])

    # Mandar sticker de la carta nueva
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
            sumar_robux(user_id, nombre, ganancia, "Mayor o Menor 🃏 (+x2)")
            ganadores.append(f"  {nombre} → +{ganancia} Robux 🟥")
        else:
            if user_id in sesion_puntos["jugadores"]:
                sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
                sesion_puntos["jugadores"][user_id]["detalle"].append(f"Mayor o Menor 🃏: -{cantidad} 🟥")
            perdedores.append(f"  {'⬆️' if eleccion == 'mayor' else '⬇️'} {nombre} → -{cantidad} Robux 🟥")

    guardar_sesion()

    resultado = [
        f"🃏 *Carta anterior:* *{carta_anterior['nombre']}* (valor {carta_anterior['valor']})\n"
        f"🃏 *Carta nueva:* *{carta_nueva['nombre']}* (valor {carta_nueva['valor']})\n"
    ]
    if ganadores:
        resultado.append("*🎉 Ganadores:*")
        resultado.extend(ganadores)
    if perdedores:
        resultado.append("\n*💸 Perdedores:*")
        resultado.extend(perdedores)

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado),
        parse_mode="Markdown"
    )

    # Quitar botones del mensaje de sala
    try:
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            reply_markup=None
        )
    except Exception:
        pass

    del sesion_mom[chat_id]
