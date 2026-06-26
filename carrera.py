import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# CORREDORES BTS 💜
# =====================================================================

CORREDORES = {
    "rm":       {"nombre": "RM",       "emoji": "🦋"},
    "jin":      {"nombre": "Jin",      "emoji": "🐹"},
    "suga":     {"nombre": "Suga",     "emoji": "🐱"},
    "jhope":    {"nombre": "J-Hope",   "emoji": "🌻"},
    "jimin":    {"nombre": "Jimin",    "emoji": "🐥"},
    "v":        {"nombre": "V",        "emoji": "🐻"},
    "jungkook": {"nombre": "Jungkook", "emoji": "🐰"},
}

PISTA_LARGO = 12  # casillas hasta la meta

# =====================================================================
# SESION
# =====================================================================

# Estado global de la carrera (solo una por chat a la vez)
# chat_id -> {
#   "activa": bool,
#   "corriendo": bool,
#   "apuestas": { user_id: { "corredor": str, "cantidad": int, "nombre": str } },
#   "msg_id": int,   # mensaje de la sala de apuestas
# }
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
    """Construye el texto de la pista con las posiciones actuales."""
    lineas = ["🏁 *CARRERA BTS* 💜\n"]
    for key, corredor in CORREDORES.items():
        pos = posiciones.get(key, 0)
        avance = "❯❯❯❯" * pos
        resto = "════════" * (PISTA_LARGO - pos)
        lineas.append(f"{corredor['emoji']} `{avance}{resto}` {corredor['nombre']}")
    lineas.append("\n🚩 Meta")
    return "\n".join(lineas)

def sala_apuestas_txt(chat_id: int) -> str:
    """Texto del mensaje de sala de apuestas."""
    apuestas = sesion_carrera[chat_id]["apuestas"]
    lineas = [
        "🏇 *CARRERA BTS* 💜",
        "¡Apuesta a tu favorito y gana x2!\n",
        "*Corredores:*",
    ]
    for key, corredor in CORREDORES.items():
        apostadores = [d["nombre"] for d in apuestas.values() if d["corredor"] == key]
        if apostadores:
            lista = ", ".join(apostadores)
            lineas.append(f"{corredor['emoji']} *{corredor['nombre']}* — {lista}")
        else:
            lineas.append(f"{corredor['emoji']} *{corredor['nombre']}*")

    lineas.append("\n📝 *¿Cómo apostar?*")
    lineas.append("`/apostar_carrera <corredor> <cantidad>`")
    lineas.append("Ej: `/apostar_carrera jungkook 50`\n")
    lineas.append("*Corredores válidos:* rm · jin · suga · jhope · jimin · v · jungkook")
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
        await update.message.reply_text("⚠️ Ya hay una carrera en curso en este chat.")
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
# /apostar_carrera <corredor> <cantidad>
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
            "❌ Uso correcto: `/apostar_carrera <corredor> <cantidad>`\n"
            "Ej: `/apostar_carrera jungkook 50`",
            parse_mode="Markdown"
        )
        return

    corredor_key = args[0].lower()
    if corredor_key not in CORREDORES:
        validos = " · ".join(CORREDORES.keys())
        await update.message.reply_text(
            f"❌ Corredor inválido. Los válidos son:\n`{validos}`",
            parse_mode="Markdown"
        )
        return

    try:
        cantidad = int(args[1])
    except ValueError:
        await update.message.reply_text("❌ La cantidad debe ser un número. Ej: `/apostar_carrera jungkook 50`", parse_mode="Markdown")
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

    # Registrar apuesta
    estado["apuestas"][user_id] = {
        "corredor": corredor_key,
        "cantidad": cantidad,
        "nombre": nombre_usuario(user),
    }

    corredor = CORREDORES[corredor_key]
    await update.message.reply_text(
        f"✅ *{nombre_usuario(user)}* apostó *{cantidad} Robux 🟥* a "
        f"{corredor['emoji']} *{corredor['nombre']}*",
        parse_mode="Markdown"
    )

    # Actualizar mensaje de sala
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
        await update.message.reply_text("⚠️ Nadie apostó aún. Espera que apuesten antes de arrancar.")
        return

    estado["corriendo"] = True

    # Inicializar posiciones
    posiciones = {key: 0 for key in CORREDORES}

    # Editar mensaje de sala para cerrar apuestas
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text="🏁 *¡Las apuestas están cerradas!* La carrera está por comenzar... 🐎💨",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await asyncio.sleep(1.5)

    # Mandar mensaje de pista
    msg_pista = await context.bot.send_message(
        chat_id=chat_id,
        text=build_pista(posiciones),
        parse_mode="Markdown"
    )

    # ---- LOOP DE CARRERA ----
    ganador_key = None
    while ganador_key is None:
        await asyncio.sleep(1.2)

        # Avanzar corredores aleatoriamente
        for key in CORREDORES:
            avance = random.randint(0, 2)  # 0, 1 o 2 casillas por turno
            posiciones[key] = min(posiciones[key] + avance, PISTA_LARGO)

        # Editar pista
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_pista.message_id,
                text=build_pista(posiciones),
                parse_mode="Markdown"
            )
        except Exception:
            pass

        # Ver si alguien llegó a la meta
        llegaron = [key for key, pos in posiciones.items() if pos >= PISTA_LARGO]
        if llegaron:
            ganador_key = random.choice(llegaron)  # si empataron, se elige al azar

    # ---- RESULTADO ----
    ganador = CORREDORES[ganador_key]
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
            perdedores_txt.append(f"  {nombre} apostó a {CORREDORES[corredor_apostado]['emoji']} {CORREDORES[corredor_apostado]['nombre']}")

    resultado = [
        f"🏆 *¡{ganador['emoji']} {ganador['nombre']} GANÓ LA CARRERA!* 💜\n"
    ]
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

    # Limpiar sesión
    del sesion_carrera[chat_id]

# =====================================================================
# /cancelar_carrera — El host cancela (devuelve apuestas)
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

    # Nadie perdió nada así que solo limpiamos
    del sesion_carrera[chat_id]
    await update.message.reply_text("❌ Carrera cancelada. No se descontó nada a nadie.")
