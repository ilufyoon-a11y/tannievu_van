import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_ERROR

# =====================================================================
# SESIONES
# =====================================================================

sesion_anagrama = {
    "activa": False,
    "fase_registro": False,
    "jugadores": [],        # [{"id": int, "name": str}]
    "moderador_id": None,
    "creador_id": None,
    "chat_id": None,
    "msg_sala_id": None,
    "categoria": None,
    "palabra": None,
    "revuelta": None,
    "esperando": None,      # "categoria" | "palabra"
    # rondas
    "modo_rondas": False,
    "ronda_actual": 0,
    "total_rondas": 4,
    "puntos": {},           # nombre -> int
    "palabras_ronda": [],   # lista de palabras dadas por el mod
    "categorias_ronda": [], # lista de categorías
}

# =====================================================================
# HELPER
# =====================================================================

def revolver(palabra: str) -> str:
    letras = list(palabra.upper())
    random.shuffle(letras)
    # Evitar que quede igual
    intentos = 0
    while "".join(letras) == palabra.upper() and intentos < 20:
        random.shuffle(letras)
        intentos += 1
    return " ".join(letras)

def sala_txt() -> str:
    jugadores = sesion_anagrama["jugadores"]
    lista = "\n".join([f"  {i+1}. {j['name']}" for i, j in enumerate(jugadores)]) or "  _(esperando jugadores...)_"
    modo = "4 Rondas 🔄" if sesion_anagrama["modo_rondas"] else "Clásico 🎯"
    return (
        f"🔀 *ANAGRAMA — {modo}*\n\n"
        f"👥 *Jugadores:*\n{lista}\n\n"
        f"Cuando estén listos, el host usa `/start_anagrama`"
    )

# =====================================================================
# /anagrama — versión clásica
# =====================================================================

async def cmd_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_anagrama.get("activa") or sesion_anagrama.get("fase_registro"):
        await update.message.reply_text("⚠️ Ya hay una partida en curso.")
        return

    _reset_sesion(modo_rondas=False)
    sesion_anagrama["creador_id"] = update.effective_user.id
    sesion_anagrama["chat_id"] = update.effective_chat.id
    sesion_anagrama["fase_registro"] = True

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_anagrama_click")
    msg = await update.message.reply_text(
        sala_txt(),
        reply_markup=InlineKeyboardMarkup([[boton]]),
        parse_mode="Markdown"
    )
    sesion_anagrama["msg_sala_id"] = msg.message_id

# =====================================================================
# /anagrama4 — versión 4 rondas
# =====================================================================

async def cmd_anagrama4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_anagrama.get("activa") or sesion_anagrama.get("fase_registro"):
        await update.message.reply_text("⚠️ Ya hay una partida en curso.")
        return

    _reset_sesion(modo_rondas=True)
    sesion_anagrama["creador_id"] = update.effective_user.id
    sesion_anagrama["chat_id"] = update.effective_chat.id
    sesion_anagrama["fase_registro"] = True

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_anagrama_click")
    msg = await update.message.reply_text(
        sala_txt(),
        reply_markup=InlineKeyboardMarkup([[boton]]),
        parse_mode="Markdown"
    )
    sesion_anagrama["msg_sala_id"] = msg.message_id

# =====================================================================
# /start_anagrama
# =====================================================================

async def cmd_start_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_anagrama.get("fase_registro"):
        await update.message.reply_text("⚠️ No hay ninguna sala abierta. Usa /anagrama primero.")
        return

    if update.effective_user.id != sesion_anagrama["creador_id"]:
        await update.message.reply_text("⛔ Solo el creador de la sala puede iniciar.")
        return

    if len(sesion_anagrama["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="Se necesitan mínimo 2 personas para jugar.")
        return

    # Parsear premio
    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["anagrama"] = premio

    sesion_anagrama["fase_registro"] = False

    # Elegir moderador aleatorio
    mod = random.choice(sesion_anagrama["jugadores"])
    sesion_anagrama["moderador_id"] = mod["id"]

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔀 *¡ANAGRAMA INICIADO!*\n\n"
             f"🎙️ El moderador es: *{mod['name']}*\n"
             f"👀 Esperando que defina la categoría y la palabra...",
        parse_mode="Markdown"
    )

    # Pedir categoría al moderador en privado
    sesion_anagrama["esperando"] = "categoria"
    try:
        if sesion_anagrama["modo_rondas"]:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="🎙️ *¡Eres el moderador!*\n\n"
                     "Vas a dar *4 palabras* una por una.\n\n"
                     "Empieza escribiendo aquí la *categoría* de la ronda 1:"
            )
        else:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="🎙️ *¡Eres el moderador!*\n\n"
                     "Primero escribe aquí la *categoría* de la palabra\n"
                     "_(ej: Animales, Países, Comidas...)_"
            )
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"⚠️ {mod['name']} necesita iniciar el bot en privado primero. Partida cancelada.")
        _reset_sesion()

# =====================================================================
# ESCUCHAR PRIVADO — moderador da categoría y palabra
# =====================================================================

async def escuchar_anagrama_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    if not sesion_anagrama.get("activa") and not sesion_anagrama.get("esperando"):
        return
    if user_id != sesion_anagrama.get("moderador_id"):
        return
    if not texto:
        return

    chat_id = sesion_anagrama["chat_id"]

    # ── Esperando categoría ──
    if sesion_anagrama["esperando"] == "categoria":
        sesion_anagrama["categoria"] = texto
        sesion_anagrama["esperando"] = "palabra"
        ronda = sesion_anagrama["ronda_actual"] + 1 if sesion_anagrama["modo_rondas"] else ""
        ronda_txt = f" (ronda {ronda}/4)" if sesion_anagrama["modo_rondas"] else ""
        await update.message.reply_text(
            f"✅ Categoría registrada: *{texto}*\n\n"
            f"Ahora escribe la *palabra*{ronda_txt} que deben adivinar:",
            parse_mode="Markdown"
        )
        return

    # ── Esperando palabra ──
    if sesion_anagrama["esperando"] == "palabra":
        palabra = texto.strip()
        if len(palabra.split()) > 1:
            await update.message.reply_text("❌ Solo una palabra por ronda, sin espacios.")
            return

        revuelta = revolver(palabra)
        sesion_anagrama["palabra"] = palabra.lower()
        sesion_anagrama["revuelta"] = revuelta
        sesion_anagrama["esperando"] = None
        sesion_anagrama["activa"] = True

        if sesion_anagrama["modo_rondas"]:
            sesion_anagrama["palabras_ronda"].append(palabra.lower())
            sesion_anagrama["categorias_ronda"].append(sesion_anagrama["categoria"])

        ronda_txt = f"Ronda {sesion_anagrama['ronda_actual'] + 1}/4 — " if sesion_anagrama["modo_rondas"] else ""

        await update.message.reply_text(f"✅ ¡Listo! La palabra está en el grupo.")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔀 *{ronda_txt}Categoría: {sesion_anagrama['categoria']}*\n\n"
                 f"```\n{revuelta}\n```\n\n"
                 f"¡Adivina la palabra! 🧩",
            parse_mode="Markdown"
        )
        return

# =====================================================================
# ESCUCHAR GRUPO — jugadores adivinan
# =====================================================================

async def escuchar_anagrama_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_anagrama.get("activa"):
        return
    if chat_id != sesion_anagrama.get("chat_id"):
        return
    if user_id == sesion_anagrama["moderador_id"]:
        return
    if not texto:
        return

    # Verificar si está en la sala
    if not any(j["id"] == user_id for j in sesion_anagrama["jugadores"]):
        return

    if texto.lower().strip() != sesion_anagrama["palabra"]:
        return

    # ¡Acertó!
    nombre = next(j["name"] for j in sesion_anagrama["jugadores"] if j["id"] == user_id)
    sesion_anagrama["activa"] = False
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)

    # ── Modo clásico ──
    if not sesion_anagrama["modo_rondas"]:
        sumar_robux(user_id, nombre, premio, "Anagrama 🔀")
        extra = f"\n+{premio} Robux 🟥" if premio else ""
        await update.message.reply_text(
            f"🎉 *¡{nombre.upper()} ADIVINÓ!* 🧩\n\n"
            f"La palabra era: *{sesion_anagrama['palabra'].upper()}*{extra}",
            parse_mode="Markdown"
        )
        _reset_sesion()
        return

    # ── Modo rondas ──
    sesion_anagrama["puntos"][nombre] = sesion_anagrama["puntos"].get(nombre, 0) + 1
    sesion_anagrama["ronda_actual"] += 1

    await update.message.reply_text(
        f"🎉 *¡{nombre.upper()} ADIVINÓ!* ✨\n"
        f"La palabra era: *{sesion_anagrama['palabra'].upper()}*\n\n"
        f"📊 *Puntos:* " + " | ".join([f"{n}: {p}" for n, p in sesion_anagrama["puntos"].items()]),
        parse_mode="Markdown"
    )

    if sesion_anagrama["ronda_actual"] >= sesion_anagrama["total_rondas"]:
        # Fin del juego
        await _fin_rondas(context, chat_id)
    else:
        # Siguiente ronda — pedir nueva categoría al moderador
        sesion_anagrama["esperando"] = "categoria"
        ronda_sig = sesion_anagrama["ronda_actual"] + 1
        await context.bot.send_message(
            chat_id=sesion_anagrama["moderador_id"],
            text=f"✅ Ronda {sesion_anagrama['ronda_actual']}/4 terminada!\n\n"
                 f"Ahora escribe la *categoría* de la ronda {ronda_sig}/4:"
        )

async def _fin_rondas(context, chat_id: int):
    puntos = sesion_anagrama["puntos"]
    if not puntos:
        await context.bot.send_message(chat_id=chat_id, text="🏁 ¡Fin del juego! Nadie adivinó ninguna. 😅")
        _reset_sesion()
        return

    max_pts = max(puntos.values())
    ganadores = [n for n, p in puntos.items() if p == max_pts]
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)

    # Pagar a todos los ganadores
    for uid_ganador in [j["id"] for j in sesion_anagrama["jugadores"] if j["name"] in ganadores]:
        nombre_g = next(j["name"] for j in sesion_anagrama["jugadores"] if j["id"] == uid_ganador)
        sumar_robux(uid_ganador, nombre_g, premio, "Anagrama 4 rondas 🔀")

    tabla = "\n".join([f"  {'🏆' if p == max_pts else '🔹'} {n}: {p} pts" for n, p in sorted(puntos.items(), key=lambda x: -x[1])])
    ganadores_txt = ", ".join(ganadores)
    extra = f"\n\n+{premio} Robux 🟥 para cada ganador" if premio else ""

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🏁 *¡FIN DEL ANAGRAMA!* 🔀\n\n"
             f"📊 *Resultados:*\n{tabla}\n\n"
             f"🏆 *Ganador{'es' if len(ganadores) > 1 else ''}: {ganadores_txt}*{extra}",
        parse_mode="Markdown"
    )
    _reset_sesion()

# =====================================================================
# BOTONES
# =====================================================================

async def manejar_botones_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if query.data == "unirme_anagrama_click":
        await query.answer()
        if not sesion_anagrama.get("fase_registro"):
            await query.answer("¡El registro ya cerró!", show_alert=True)
            return
        if any(j["id"] == user.id for j in sesion_anagrama["jugadores"]):
            await query.answer("¡Ya estás dentro!", show_alert=True)
            return
        sesion_anagrama["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🔀 {nombre_usuario(user)} se unió al Anagrama 𓂃")

        # Actualizar mensaje de sala
        try:
            await context.bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=sesion_anagrama["msg_sala_id"],
                text=sala_txt(),
                reply_markup=query.message.reply_markup,
                parse_mode="Markdown"
            )
        except Exception:
            pass

# =====================================================================
# RESET
# =====================================================================

def _reset_sesion(modo_rondas=False):
    sesion_anagrama.update({
        "activa": False,
        "fase_registro": False,
        "jugadores": [],
        "moderador_id": None,
        "creador_id": None,
        "chat_id": None,
        "msg_sala_id": None,
        "categoria": None,
        "palabra": None,
        "revuelta": None,
        "esperando": None,
        "modo_rondas": modo_rondas,
        "ronda_actual": 0,
        "total_rondas": 4,
        "puntos": {},
        "palabras_ronda": [],
        "categorias_ronda": [],
    })
