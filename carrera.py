import random
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, guardar_sesion

# =====================================================================
# CORREDORES BTS 💜
# =====================================================================

CORREDORES = {
    "rm":       "🐨",
    "jin":      "🦙",
    "suga":     "🍪",
    "jhope":    "🐿️",
    "jimin":    "🐕",
    "v":        "🛸",
    "jungkook": "🐇",
}

# Mapa emoji -> key para parsear /apostar_carrera con emoji
EMOJI_A_KEY = {v: k for k, v in CORREDORES.items()}

PISTA_LARGO = 15

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
    lineas = ["🏁 CARRERA 💜\n"]
    for key, emoji in CORREDORES.items():
        pos = posiciones.get(key, 0)
        avance = "█" * pos
        resto =  "░" * (PISTA_LARGO - pos)
        lineas.append(f"{emoji} `{avance}{resto}` 🏁")
    return "\n".join(lineas)

def sala_apuestas_txt(chat_id: int) -> str:
    apuestas = sesion_carrera[chat_id]["apuestas"]
    lineas = [
        "🏇 <b>CARRERA BTS</b> 💜",
        "¡𝖠𝗉𝗎𝖾𝗌𝗍𝖺 𝖺 𝗍𝗎 𝖿𝖺𝗏𝗈𝗋𝗂𝗍𝗈 𝗒 𝖽𝗎𝗉𝗅𝗂𝖼𝖺 𝗍𝗎 𝖽𝗂𝗇𝖾𝗋𝗈!\n",
        "𝖢𝗈𝗋𝗋𝖾𝖽𝗈𝗋𝖾𝗌:",
    ]
    for key, emoji in CORREDORES.items():
        apostadores = [d["nombre"] for d in apuestas.values() if d["corredor"] == key]
        if apostadores:
            lineas.append(f"{emoji} — {', '.join(apostadores)}")
        else:
            lineas.append(f"{emoji}")
    lineas.append(
        "\n<blockquote>📝 ¿𝖢𝗈́𝗆𝗈 𝖺𝗉𝗈𝗌𝗍𝖺𝗋?\n\n"
        "𝖴𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/apostar_carrera &lt;emoji&gt; &lt;cantidad&gt;</code>\n"
        "𝖤𝗃: <code>/apostar_carrera 🐰 50</code>\n\n"
        "<b>Corredores:</b> 🐨 · 🦙 · 🍪 · 🐿️ · 🐕 · 🛸 · 🐇</blockquote>"
    )
    lineas.append("\n⏳ 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗃𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌... 𝖤𝗅 𝗁𝗈𝗌𝗍 𝖺𝗋𝗋𝖺𝗇𝖼𝖺 𝖼𝗈𝗇 <code>/start_carrera</code>")
    return "\n".join(lineas)

# =====================================================================
# /carrera — Abre la sala
# =====================================================================

async def cmd_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_puntos["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖼𝗍𝗂𝗏𝖺 𝖺𝗎𝗇, 𝗇𝖺𝖽𝗂𝖾 𝖼𝗎𝖾𝗇𝗍𝖺 𝖼𝗈𝗇 𝖿𝗂𝖼𝗁𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝗋. 𝖴𝗌𝖺 /new_session 𝗉𝗋𝗂𝗆𝖾𝗋𝗈.")
        return

    if chat_id in sesion_carrera and sesion_carrera[chat_id]["activa"]:
        await update.message.reply_text("𝖸𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝖺𝖼𝗍𝗂𝗏𝖺")
        return

    sesion_carrera[chat_id] = {
        "activa": True,
        "corriendo": False,
        "apuestas": {},
        "msg_id": None,
    }

    msg = await update.message.reply_text(
        sala_apuestas_txt(chat_id)
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
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /carrera 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺.")
        return

    estado = sesion_carrera.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /carrera 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺.")
        return

    if estado["corriendo"]:
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾𝗌 𝖺𝗉𝗈𝗌𝗍𝖺𝗋!")
        return

    if user_id in estado["apuestas"]:
        await update.message.reply_text("𝖣𝖾𝗌𝖼𝗎𝗂𝖽𝖺, 𝗒𝖺 𝖿𝗎𝖾 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝖺𝖽𝖺 𝗍𝗎 𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝗉𝖺𝗋𝖺 𝖾𝗌𝗍𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺. ¡𝖤𝗌𝗉𝖾𝗋𝖺 𝖾𝗅 𝗋𝖾𝗌𝗎𝗅𝗍𝖺𝖽𝗈, 𝗆𝗎𝖼𝗁𝖺 𝗌𝗎𝖾𝗋𝗍𝖾!")
        return

    args = context.args or []
    if len(args) < 2:
        await update.message.reply_text(
            "❌ 𝖴𝗌𝗈: <code>/apostar_carrera &lt;emoji&gt; &lt;cantidad&gt;</code>\n"
            "𝖤𝗃: <code>/apostar_carrera 🐰 50</code>",
            parse_mode="HTML"
        )
        return

    emoji_arg = args[0].strip()
    corredor_key = EMOJI_A_KEY.get(emoji_arg)

    if not corredor_key:
        await update.message.reply_text(
            "𝖤𝗆𝗈𝗃𝗂 𝗂𝗇𝗏𝖺𝗅𝗂𝖽𝗈. 𝖫𝗈𝗌 𝖼𝗈𝗋𝗋𝖾𝖽𝗈𝗋𝖾𝗌 𝗌𝗈𝗇:\n🦋 · 🐹 · 🐱 · 🌻 · 🐥 · 🐻 · 🐰",
        )
        return

    try:
        cantidad = int(args[1])
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
            f"𝖳𝗎 𝗌𝖺𝗅𝖽𝗈:{saldo} 𝖿𝗂𝖼𝗁𝖺𝗌\n"
            f"𝖣𝗂𝗇𝖾𝗋𝗈 𝖺𝗉𝗈𝗌𝗍𝖺𝖽𝗈: {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌"
        )
        return

    estado["apuestas"][user_id] = {
        "corredor": corredor_key,
        "cantidad": cantidad,
        "nombre": nombre_usuario(user),
    }

    await update.message.reply_text(
        f"✅ {nombre_usuario(user)} 𝖺𝗉𝗈𝗌𝗍𝗈 {cantidad} 𝖿𝗂𝖼𝗁𝖺𝗌 𝖺 {emoji_arg}"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text=sala_apuestas_txt(chat_id)
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
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝖺𝖻𝗂𝖾𝗋𝗍𝖺.")
        return

    if estado["corriendo"]:
        await update.message.reply_text("𝖫𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝗒𝖺 𝖾𝗌𝗍𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈.")
        return

    if not estado["apuestas"]:
        await update.message.reply_text("𝖭𝖺𝖽𝗂𝖾 𝗁𝖺 𝖺𝗉𝗈𝗌𝗍𝖺𝖽𝗈 𝖺𝗎𝗇.")
        return

    estado["corriendo"] = True
    posiciones = {key: 0 for key in CORREDORES}

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=estado["msg_id"],
            text="🏁 ¡𝖫𝖺𝗌 𝖺𝗉𝗎𝖾𝗌𝗍𝖺𝗌 𝖾𝗌𝗍𝖺𝗇 𝖼𝖾𝗋𝗋𝖺𝖽𝖺𝗌! 𝖫𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝖾𝗌𝗍𝖺 𝗉𝗈𝗋 𝖼𝗈𝗆𝖾𝗇𝗓𝖺𝗋... 💨"
        )
    except Exception:
        pass

    await asyncio.sleep(1.5)

    msg_pista = await context.bot.send_message(
        chat_id=chat_id,
        text=build_pista(posiciones)
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
                text=build_pista(posiciones)
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
            sumar_robux(user_id, nombre, ganancia, f"𝖢𝖺𝗋𝗋𝖾𝗋𝖺: (+x2)")
            ganadores_txt.append(f"  {nombre} → +{ganancia} 𝖿𝗂𝖼𝗁𝖺𝗌")
        else:
            restar_robux(user_id, cantidad, f"𝖢𝖺𝗋𝗋𝖾𝗋𝖺: -{cantidad} 🟥")
            perdedores_txt.append(f"  {nombre} 𝖺𝗉𝗈𝗌𝗍𝗈 𝖺 {CORREDORES[corredor_apostado]}")

    resultado = [f"🏆 ¡{emoji_ganador} 𝗚𝗔𝗡𝗢 𝗟𝗔 𝗖𝗔𝗥𝗥𝗘𝗥𝗔ⵑ 💜\n\n"]
    if ganadores_txt:
        resultado.append("𝗚𝗔𝗡𝗔𝗗𝗢𝗥𝗘𝗦:\n")
        resultado.extend(ganadores_txt)
    if perdedores_txt:
        resultado.append("\n💸 𝗣𝗘𝗥𝗗𝗘𝗗𝗢𝗥𝗘𝗦:\n\n")
        resultado.extend(perdedores_txt)

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(resultado)
    )

    del sesion_carrera[chat_id]

# =====================================================================
# /cancelar_carrera
# =====================================================================

async def cmd_cancelar_carrera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    estado = sesion_carrera.get(chat_id)
    if not estado or not estado["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝖺𝖼𝗍𝗂𝗏𝖺")
        return

    if estado["corriendo"]:
        await update.message.reply_text("𝖫𝖺 𝖼𝖺𝗋𝗋𝖾𝗋𝖺 𝗒𝖺 𝖾𝗌𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈, 𝗇𝗈 𝗉𝗎𝖾𝖽𝖾 𝗌𝖾𝗋 𝖼𝖺𝗇𝖼𝖾𝗅𝖺𝖽𝖺")
        return

    del sesion_carrera[chat_id]
    await update.message.reply_text("𝖢𝖺𝗋𝗋𝖾𝗋𝖺 𝖼𝖺𝗇𝖼𝖾𝗅𝖺𝖽𝖺. 𝖭𝗈 𝗌𝖾 𝖽𝖾𝗌𝖼𝗈𝗇𝗍𝗈 𝗇𝖺𝖽𝖺 𝖺 𝗇𝖺𝖽𝗂𝖾.")
