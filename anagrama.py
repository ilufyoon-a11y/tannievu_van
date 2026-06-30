import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_ERROR

# =====================================================================
# SESIONES
# =====================================================================

# Igual que en box.py / guessong.py: una sesión POR chat_id, así varios
# grupos pueden jugar Anagrama al mismo tiempo sin pisarse entre ellos.
sesion_anagrama = {}   # chat_id -> {...}

# Para saber a qué chat pertenece el moderador cuando escribe en privado
# (igual patrón que esperando_elementos en box.py)
esperando_moderador = {}   # user_id -> chat_id

def _sesion_base(modo_rondas: bool, creador_id: int, chat_id: int) -> dict:
    return {
        "activa": False,
        "fase_registro": True,
        "jugadores": [],
        "moderador_id": None,
        "creador_id": creador_id,
        "chat_id": chat_id,
        "msg_sala_id": None,
        "categoria": None,
        "palabra": None,          # palabra actual (modo clásico o ronda actual)
        "palabras": [],           # lista de palabras (modo rondas, todas de una)
        "revuelta": None,
        "adivinadas": set(),
        "esperando": None,        # "categoria" | "palabras"
        "modo_rondas": modo_rondas,
        "ronda_actual": 0,
        "total_rondas": 4,
        "puntos": {},              # user_id -> puntos
    }

# =====================================================================
# HELPERS
# =====================================================================

def revolver(palabra: str) -> str:
    letras = list(palabra.upper())
    random.shuffle(letras)
    intentos = 0
    while "".join(letras) == palabra.upper() and intentos < 20:
        random.shuffle(letras)
        intentos += 1
    return " ".join(letras)

def sala_txt(sesion: dict) -> str:
    jugadores = sesion["jugadores"]
    lista = "\n".join([f"  {i+1}. {j['name']}" for i, j in enumerate(jugadores)]) or "  _(esperando jugadores...)_"
    modo = "4 Rondas 🔄" if sesion["modo_rondas"] else "Clásico 🎯"
    return (
        f"🔀 *ANAGRAMA — {modo}*\n\n"
        f"👥 *Jugadores:*\n{lista}\n\n"
        f"Cuando estén listos, el host usa `/start_anagrama`"
    )

def parsear_palabras(texto: str) -> list:
    """Separa palabras por coma o guion."""
    import re
    partes = re.split(r'[,\-]', texto)
    return [p.strip().lower() for p in partes if p.strip()]

def _nombre_de(sesion: dict, user_id: int) -> str:
    jugador = next((j for j in sesion["jugadores"] if j["id"] == user_id), None)
    return jugador["name"] if jugador else f"ID {user_id}"

def reset_anagrama_chat(chat_id: int):
    """Apaga y limpia la partida de Anagrama de un chat puntual (usado por /off_van)."""
    sesion = sesion_anagrama.pop(chat_id, None)
    if sesion and sesion.get("moderador_id"):
        esperando_moderador.pop(sesion["moderador_id"], None)

# =====================================================================
# /anagrama — versión clásica
# =====================================================================

async def cmd_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion_actual = sesion_anagrama.get(chat_id)

    if sesion_actual and (sesion_actual.get("activa") or sesion_actual.get("fase_registro")):
        await update.message.reply_text("⚠️ Ya hay una partida en curso en este grupo.")
        return

    sesion_anagrama[chat_id] = _sesion_base(modo_rondas=False, creador_id=update.effective_user.id, chat_id=chat_id)

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_anagrama_click")
    msg = await update.message.reply_text(
        sala_txt(sesion_anagrama[chat_id]),
        reply_markup=InlineKeyboardMarkup([[boton]]),
        parse_mode="Markdown"
    )
    sesion_anagrama[chat_id]["msg_sala_id"] = msg.message_id

# =====================================================================
# /anagrama4 — versión 4 rondas
# =====================================================================

async def cmd_anagrama4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion_actual = sesion_anagrama.get(chat_id)

    if sesion_actual and (sesion_actual.get("activa") or sesion_actual.get("fase_registro")):
        await update.message.reply_text("⚠️ Ya hay una partida en curso en este grupo.")
        return

    sesion_anagrama[chat_id] = _sesion_base(modo_rondas=True, creador_id=update.effective_user.id, chat_id=chat_id)

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_anagrama_click")
    msg = await update.message.reply_text(
        sala_txt(sesion_anagrama[chat_id]),
        reply_markup=InlineKeyboardMarkup([[boton]]),
        parse_mode="Markdown"
    )
    sesion_anagrama[chat_id]["msg_sala_id"] = msg.message_id

# =====================================================================
# /start_anagrama
# =====================================================================

async def cmd_start_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sesion = sesion_anagrama.get(chat_id)

    if not sesion or not sesion.get("fase_registro"):
        await update.message.reply_text("⚠️ No hay ninguna sala abierta. Usa /anagrama primero.")
        return

    if update.effective_user.id != sesion["creador_id"]:
        await update.message.reply_text("⛔ Solo el creador de la sala puede iniciar.")
        return

    if len(sesion["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="Se necesitan mínimo 2 personas para jugar.")
        return

    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["anagrama"] = premio

    sesion["fase_registro"] = False

    mod = random.choice(sesion["jugadores"])
    sesion["moderador_id"] = mod["id"]
    esperando_moderador[mod["id"]] = chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔀 *¡ANAGRAMA INICIADO!*\n\n"
             f"🎙️ El moderador es: *{mod['name']}*\n"
             f"👀 Esperando que defina la categoría y las palabras...",
        parse_mode="Markdown"
    )

    sesion["esperando"] = "categoria"
    try:
        if sesion["modo_rondas"]:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="🎙️ *¡Eres el moderador!*\n\n"
                     "Primero escribe la *categoría* de las 4 palabras:",
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=mod["id"],
                text="🎙️ *¡Eres el moderador!*\n\n"
                     "Primero escribe la *categoría* de la palabra\n"
                     "_(ej: Animales, Países, Comidas...)_",
                parse_mode="Markdown"
            )
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"⚠️ {mod['name']} necesita iniciar el bot en privado primero. Partida cancelada.")
        esperando_moderador.pop(mod["id"], None)
        sesion_anagrama.pop(chat_id, None)

# =====================================================================
# ESCUCHAR PRIVADO — moderador da categoría y palabras
# =====================================================================

async def escuchar_anagrama_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    chat_id = esperando_moderador.get(user_id)
    if chat_id is None:
        return

    sesion = sesion_anagrama.get(chat_id)
    if not sesion or user_id != sesion.get("moderador_id"):
        return
    if not texto:
        return

    # ── Esperando categoría ──
    if sesion["esperando"] == "categoria":
        sesion["categoria"] = texto
        sesion["esperando"] = "palabras"

        if sesion["modo_rondas"]:
            await update.message.reply_text(
                f"✅ Categoría: *{texto}*\n\n"
                f"Ahora escribe las *4 palabras* separadas por coma:\n"
                f"_(ej: pie de limon, pastel, helado, torta)_",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"✅ Categoría: *{texto}*\n\n"
                f"Ahora escribe la *palabra* que deben adivinar\n"
                f"_(puede tener espacios, ej: pie de limon)_",
                parse_mode="Markdown"
            )
        return

    # ── Esperando palabras ──
    if sesion["esperando"] == "palabras":
        if sesion["modo_rondas"]:
            palabras = parsear_palabras(texto)
            if len(palabras) != 4:
                await update.message.reply_text(
                    f"❌ Necesito exactamente 4 palabras separadas por coma. Recibí {len(palabras)}.\n"
                    f"Ej: `pie de limon, pastel, helado, torta`",
                    parse_mode="Markdown"
                )
                return

            sesion["palabras"] = palabras
            sesion["palabra"] = palabras[0]
            sesion["adivinadas"] = set()
            sesion["esperando"] = None
            sesion["activa"] = True
            esperando_moderador.pop(user_id, None)

            await update.message.reply_text("✅ ¡Palabras registradas! El juego comienza.")

            # Mostrar solo la primera ronda
            revuelta = revolver(palabras[0])
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔀 *Ronda 1/4 — Categoría: {sesion['categoria']}*\n\n"
                     f"```\n{revuelta}\n```\n\n"
                     f"¡Adivina la palabra! 🧩",
                parse_mode="Markdown"
            )

        else:
            # Modo clásico — permite espacios
            palabra = texto.strip().lower()
            revuelta = revolver(palabra)
            sesion["palabra"] = palabra
            sesion["revuelta"] = revuelta
            sesion["esperando"] = None
            sesion["activa"] = True
            esperando_moderador.pop(user_id, None)

            await update.message.reply_text("✅ ¡Listo! La palabra está en el grupo.")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔀 *Categoría: {sesion['categoria']}*\n\n"
                     f"```\n{revuelta}\n```\n\n"
                     f"¡Adivina la palabra! 🧩",
                parse_mode="Markdown"
            )
        return

# =====================================================================
# ESCUCHAR GRUPO — jugadores adivinan
# =====================================================================

async def escuchar_anagrama_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    sesion = sesion_anagrama.get(chat_id)
    if not sesion or not sesion.get("activa"):
        return
    if user_id == sesion["moderador_id"]:
        return
    if not texto:
        return

    if not any(j["id"] == user_id for j in sesion["jugadores"]):
        return

    texto_limpio = texto.lower().strip()

    # ── Modo rondas — verificar contra todas las palabras pendientes ──
    if sesion["modo_rondas"]:
        palabras = sesion["palabras"]
        puntos = sesion["puntos"]

        # Verificar si la respuesta corresponde a alguna palabra no adivinada aún
        adivinadas = sesion.get("adivinadas", set())
        nombre = _nombre_de(sesion, user_id)

        if texto_limpio in palabras and texto_limpio not in adivinadas:
            adivinadas.add(texto_limpio)
            sesion["adivinadas"] = adivinadas
            puntos[user_id] = puntos.get(user_id, 0) + 1
            sesion["ronda_actual"] += 1

            tablero = " | ".join([f"{_nombre_de(sesion, uid)}: {p}" for uid, p in puntos.items()])
            await update.message.reply_text(
                f"🎉 *¡{nombre.upper()} ADIVINÓ!* ✨\n"
                f"La palabra era: *{texto_limpio.upper()}*\n\n"
                f"📊 *Puntos:* {tablero}",
                parse_mode="Markdown"
            )

            if sesion["ronda_actual"] >= sesion["total_rondas"]:
                sesion["activa"] = False
                await _fin_rondas(context, chat_id)
            else:
                # Revelar siguiente palabra
                siguiente = next(p for p in palabras if p not in adivinadas)
                ronda_num = sesion["ronda_actual"] + 1
                revuelta = revolver(siguiente)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔀 *Ronda {ronda_num}/4 — Categoría: {sesion['categoria']}*\n\n"
                         f"```\n{revuelta}\n```\n\n"
                         f"¡Adivina la palabra! 🧩",
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text("🔍 ¡Síguelo intentando, ya estás cerca! 🧩")
        return

    # ── Modo clásico ──
    if texto_limpio != sesion["palabra"]:
        await update.message.reply_text("🔍 ¡Síguelo intentando, ya estás cerca! 🧩")
        return

    nombre = _nombre_de(sesion, user_id)
    sesion["activa"] = False
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)

    sumar_robux(user_id, nombre, premio, "Anagrama 🔀")
    extra = f"\n+{premio} Robux 🟥" if premio else ""
    await update.message.reply_text(
        f"🎉 *¡{nombre.upper()} ADIVINÓ!* 🧩\n\n"
        f"La palabra era: *{sesion['palabra'].upper()}*{extra}",
        parse_mode="Markdown"
    )
    sesion_anagrama.pop(chat_id, None)

async def _fin_rondas(context, chat_id: int):
    sesion = sesion_anagrama.get(chat_id)
    if not sesion:
        return

    puntos = sesion["puntos"]
    if not puntos:
        await context.bot.send_message(chat_id=chat_id, text="🏁 ¡Fin del juego! Nadie adivinó ninguna. 😅")
        sesion_anagrama.pop(chat_id, None)
        return

    max_pts = max(puntos.values())
    ganadores_ids = [uid for uid, p in puntos.items() if p == max_pts]
    premio = sesion_puntos.get("premio_actual", {}).get("anagrama", 0)

    for uid_ganador in ganadores_ids:
        nombre_g = _nombre_de(sesion, uid_ganador)
        sumar_robux(uid_ganador, nombre_g, premio, "Anagrama 4 rondas 🔀")

    tabla = "\n".join([
        f"  {'🏆' if p == max_pts else '🔹'} {_nombre_de(sesion, uid)}: {p} pts"
        for uid, p in sorted(puntos.items(), key=lambda x: -x[1])
    ])
    ganadores_txt = ", ".join(_nombre_de(sesion, uid) for uid in ganadores_ids)
    extra = f"\n\n+{premio} Robux 🟥 para cada ganador" if premio else ""

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🏁 *¡FIN DEL ANAGRAMA!* 🔀\n\n"
             f"📊 *Resultados:*\n{tabla}\n\n"
             f"🏆 *Ganador{'es' if len(ganadores_ids) > 1 else ''}: {ganadores_txt}*{extra}",
        parse_mode="Markdown"
    )
    sesion_anagrama.pop(chat_id, None)

# =====================================================================
# BOTONES
# =====================================================================

async def manejar_botones_anagrama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_anagrama_click":
        await query.answer()

        sesion = sesion_anagrama.get(chat_id)
        if not sesion or not sesion.get("fase_registro"):
            await query.answer("¡El registro ya cerró!", show_alert=True)
            return
        if any(j["id"] == user.id for j in sesion["jugadores"]):
            await query.answer("¡Ya estás dentro!", show_alert=True)
            return

        sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🔀 {nombre_usuario(user)} se unió al Anagrama 𓂃")

        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=sesion["msg_sala_id"],
                text=sala_txt(sesion),
                reply_markup=query.message.reply_markup,
                parse_mode="Markdown"
            )
        except Exception:
            pass
