import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# CORREDORES BTS 💜
# =====================================================================

CORREDORES = {
    "rm":       "🦋",
    "jin":      "🐹",
    "suga":     "🐱",
    "jhope":    "🌻",
    "jimin":    "🐥",
    "v":        "🐻",
    "jungkook": "🐰",
}

# Mapa emoji -> key para parsear /apostar_carrera con emoji
EMOJI_A_KEY = {v: k for k, v in CORREDORES.items()}

PISTA_LARGO = 20

# =====================================================================
# SESION
# =====================================================================

sesion_carrera = {}

# =====================================================================
# HELPERS
# =====================================================================

def get_saldo(user_id: int) -> int:
    datos = sesion_puntos["jugadores"].get(user_id)
    return datos["robux"] if datos else 0

def restar_robux(user_id: int, cantidad: int, detalle: str):
    if user_id in sesion_puntos["jugadores"]:
        sesion_puntos["jugadores"][user_id]["robux"] -= cantidad
        sesion_puntos["jugadores"][user_id]["detalle"].append(detalle)
        guardar_sesion()

def build_pista(posiciones: dict) -> str:
    lineas = ["🏁 *CARRERA BTS* 💜\n"]
    for key, emoji in CORREDORES.items():
        pos = posiciones.get(key, 0)
        avance = "❯" * pos
        resto = "─" * (PISTA_LARGO - pos)
        lineas.append(f"{emoji} `{avance}{resto}` 🏁")
    return "\n".join(lineas)

def sala_apuestas_txt(chat_id: int) -> str:
    apuestas = sesion_carrera[chat_id]["apuestas"]
    lineas = [
        "🏇 *CARRERA BTS* 💜",
        "¡Apuesta a tu favorito y gana x2!\n",
        "*Corredores:*",
    ]
    for key, emoji in CORREDORES.items():
        apostadores = [d["nombre"] for d in apuestas.values() if d["corredor"] == key]
        if apostadores:
            lineas.append(f"{emoji} — {', '.join(apostadores)}")
        else:
            lineas.append(f"{emoji}")

    lineas.append("\n📝 *¿Cómo apostar?*")
    lineas.append("`/apostar_carrera <emoji> <cantidad>`")
    lineas.append("Ej: `/apostar_carrera 🐰 50`\n")
    lineas.append("*Corredores:* 🦋 · 🐹 · 🐱 · 🌻 · 🐥 · 🐻 · 🐰")
    lineas.append("\n⏳ Esperando jugadores... El host arranca con `/start_carrera`")
    return "\n".join(lineas)

# =====================================================================
# /carrera — Abre la sala
# =====================================================================

async def cmd_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa. Usa /new_session primero.")
        return

    if chat_id in sesion_carrera and sesion_carrera[chat_id]["activa"]:
        await update.message.reply_text("⚠️ Ya hay una carrera abierta en este chat.")
        return

    sesion_carrera[chat_id] = {
        "activa": True,
        "corriendo": False,
        "apuestas": {},
        "msg_id": None,
    }

    msg = await update.message.reply_text(
        sala_apuestas_txt(chat_id),
        parse_mode="Markdown"
    )
    sesion_carrera[chat_id]["msg_id"] = msg.message_id

# =====================================================================
# /apostar_carrera <emoji> <cantidad>
# =====================================================================

async def cmd_apostar_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna sesión activa.")
        return

    estado = sesion_carrera.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna carrera abierta. El host debe usar /carrera primero.")
        return

    if estado["corriendo"]:
        await update.message.reply_text("⚠️ ¡La carrera ya arrancó! No puedes apostar ahora.")
        return

    if user_id in estado["apuestas"]:
        await update.message.reply_text("⚠️ Ya apostaste en esta carrera. ¡Espera el resultado!")
        return

    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Uso: `/apostar_carrera <emoji> <cantidad>`\n"
            "Ej: `/apostar_carrera 🐰 50`",
            parse_mode="Markdown"
        )
        return

    emoji_arg = args[0].strip()
    corredor_key = EMOJI_A_KEY.get(emoji_arg)

    if not corredor_key:
        await update.message.reply_text(
            "❌ Emoji inválido. Los corredores son:\n🦋 · 🐹 · 🐱 · 🌻 · 🐥 · 🐻 · 🐰",
        )
        return

    try:
        cantidad = int(args[1])
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

    estado["apuestas"][user_id] = {
        "corredor": corredor_key,
        "cantidad": cantidad,
        "nombre": nombre_usuario(user),
    }

    await update.message.reply_text(
        f"✅ *{nombre_usuario(user)}* apostó *{cantidad} Robux 🟥* a {emoji_arg}",
        parse_mode="Markdown"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=sala_apuestas_txt(chat_id),
            parse_mode="Markdown"
        )
    except Exception:
        pass

# =====================================================================
# /start_carrera — El host arranca la carrera
# =====================================================================

async def cmd_start_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_carrera.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna carrera abierta.")
        return

    if estado["corriendo"]:
        await update.message.reply_text("⚠️ La carrera ya está en curso.")
        return

    if not estado["apuestas"]:
        await update.message.reply_text("⚠️ Nadie apostó aún.")
        return

    estado["corriendo"] = True
    posiciones = {key: 0 for key in CORREDORES}

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text="🏁 *¡Las apuestas están cerradas!* La carrera está por comenzar... 💨",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await asyncio.sleep(1.5)

    msg_pista = await context.bot.send_message(
        chat_id=chat_id,
        text=build_pista(posiciones),
        parse_mode="Markdown"
    )

    ganador_key = None
    while ganador_key is None:
        await asyncio.sleep(1.2)

        for key in CORREDORES:
            avance = random.randint(0, 2)
            posiciones[key] = min(posiciones[key] + avance, PISTA_LARGO)

        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_pista.message_id,
                text=build_pista(posiciones),
                parse_mode="Markdown"
            )
        except Exception:
            pass

        llegaron = [key for key, pos in posiciones.items() if pos >= PISTA_LARGO]
        if llegaron:
            ganador_key = random.choice(llegaron)

    # ---- RESULTADO ----
    emoji_ganador = CORREDORES[ganador_key]
    ganadores_txt = []
    perdedores_txt = []

    for user_id, datos in estado["apuestas"].items():
        nombre = datos["nombre"]
        cantidad = datos["cantidad"]
        corredor_apostado = datos["corredor"]

        if corredor_apostado == ganador_key:
            ganancia = cantidad * 2
            sumar_robux(user_id, nombre, ganancia, f"Carrera 🏇 (+x2)")
            ganadores_txt.append(f"  {nombre} → +{ganancia} Robux 🟥")
        else:
            restar_robux(user_id, cantidad, f"Carrera 🏇: -{cantidad} 🟥")
            perdedores_txt.append(f"  {nombre} apostó a {CORREDORES[corredor_apostado]}")

    resultado = [f"🏆 *¡{emoji_ganador} GANÓ LA CARRERA!* 💜\n"]
    if ganadores_txt:
        resultado.append("*🎉 Ganadores:*")
        resultado.extend(ganadores_txt)
    if perdedores_txt:
        resultado.append("\n*💸 Perdedores:*")
        resultado.extend(perdedores_txt)

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado),
        parse_mode="Markdown"
    )

    del sesion_carrera[chat_id]

# =====================================================================
# /cancelar_carrera
# =====================================================================

async def cmd_cancelar_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_carrera.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("⚠️ No hay ninguna carrera abierta.")
        return

    if estado["corriendo"]:
        await update.message.reply_text("⚠️ La carrera ya está en curso, no se puede cancelar.")
        return

    del sesion_carrera[chat_id]
    await update.message.reply_text("❌ Carrera cancelada. No se descontó nada a nadie.")
