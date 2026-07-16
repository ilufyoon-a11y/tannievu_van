# ahorcado.py — Juego de Ahorcado 🪢
#
# Sigue el mismo patrón que tus otros módulos (charada.py, anagrama.py, box.py):
# un moderador elige categoría + palabra en privado, y el grupo adivina
# letras o números. Cada jugador tiene sus propias 6 vidas (no compartidas).

import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import (
    GIF_AHORCADO, GIF_ERROR, GIF_RECHAZADO, GIF_LETRISTA,
    sesion_puntos, sumar_robux, nombre_usuario,
)

# !!  ARTE ASCII DEL AHORCADO (0 a 6 fallos)  ───  ♥︎

ETAPAS_AHORCADO = [
    "```\n\n\n\n\n═══════\n```",
    "```\n│\n│\n│\n│\n═══════\n```",
    "```\n┌───┐\n│\n│\n│\n│\n═══════\n```",
    "```\n┌───┐\n│   O\n│\n│\n│\n═══════\n```",
    "```\n┌───┐\n│   O\n│   │\n│\n│\n═══════\n```",
    "```\n┌───┐\n│   O\n│  /│\n│\n│\n═══════\n```",
    "```\n┌───┐\n│   O\n│  /│\\\n│  / \\\n│\n═══════\n```",
]

MAX_FALLOS = len(ETAPAS_AHORCADO) - 1  # 6 fallos = eliminado

# !!  SESIÓN DEL AHORCADO  ───  ♥︎

sesion_ahorcado = {
    "jugadores": [],
    "activa": False,
    "palabra": "",
    "categoria": "",
    "letras_correctas": set(),
    "letras_incorrectas": set(),   # ya mencionadas por cualquiera (para no repetirlas)
    "moderador_id": None,
    "ultimo_moderador_id": None,
    "vidas": {},          # user_id -> intentos restantes (INDIVIDUAL por jugador)
    "eliminados": set(),  # user_id de quienes ya gastaron sus 6 intentos
}

esperando_palabra_ahorcado = {}  # user_id (moderador) -> chat_id


def _normalizar(texto: str) -> str:
    return texto.strip().lower()


def _pantalla_ahorcado(palabra: str, correctas: set) -> str:
    resultado = []
    for c in palabra:
        if c == " ":
            resultado.append(" ")
        elif c in correctas:
            resultado.append(c.upper())
        else:
            resultado.append("_")
    return " ".join(resultado)


def _palabra_completa(palabra: str, correctas: set) -> bool:
    return all(c in correctas or c == " " for c in palabra)


# =====================================================================
# COMANDOS
# =====================================================================

async def unirse_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_ahorcado["activa"]:
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return

    sesion_ahorcado["jugadores"] = []
    sesion_ahorcado["palabra"] = ""
    sesion_ahorcado["categoria"] = ""
    sesion_ahorcado["letras_correctas"] = set()
    sesion_ahorcado["letras_incorrectas"] = set()
    sesion_ahorcado["moderador_id"] = None
    sesion_ahorcado["vidas"] = {}
    sesion_ahorcado["eliminados"] = set()

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_ahorcado_click")
    await update.message.reply_photo(
        photo=GIF_AHORCADO,
        caption="៹ ࣪  🪢 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺𝗅 𝖠𝗁𝗈𝗋𝖼𝖺𝖽𝗈! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪   𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )


async def iniciar_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["ahorcado"] = int(args[0])
        except ValueError:
            pass

    if len(sesion_ahorcado["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    candidatos = list(sesion_ahorcado["jugadores"])
    ultimo_mod = sesion_ahorcado.get("ultimo_moderador_id")
    if ultimo_mod and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_mod]
        moderador = random.choice(filtrados if filtrados else candidatos)
    else:
        moderador = random.choice(candidatos)

    sesion_ahorcado["jugadores"].remove(moderador)
    sesion_ahorcado.update({
        "moderador_id": moderador["id"],
        "ultimo_moderador_id": moderador["id"],
        "activa": True,
        "letras_correctas": set(),
        "letras_incorrectas": set(),
        "vidas": {j["id"]: MAX_FALLOS for j in sesion_ahorcado["jugadores"]},
        "eliminados": set(),
    })

    esperando_palabra_ahorcado[moderador["id"]] = chat_id
    await update.message.reply_text("˒˓  ¡𝖬𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈! 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗊𝗎𝖾 𝖾𝗇𝗏𝗂𝖾 𝗅𝖺 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂́𝖺 𝗒 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺  ᨦᨩ")

    try:
        await context.bot.send_photo(
            chat_id=moderador["id"],
            photo=GIF_LETRISTA,
            caption=("¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋!\n\n"
                     "𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂́𝖺 𝗅𝖺 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂́𝖺 𝗒 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺/𝖿𝗋𝖺𝗌𝖾 𝗌𝖾𝗉𝖺𝗋𝖺𝖽𝖺𝗌 𝗉𝗈𝗋 𝗎𝗇 𝗀𝗎𝗂𝗈́𝗇 '-'.\n\n"
                     "𝖤𝗃𝖾𝗆𝗉𝗅𝗈: `paises-peru` 𝗈 `numero secreto-2024`\n\n"
                     "Puede tener letras, espacios y números."),
            parse_mode="Markdown"
        )
    except Exception:
        await context.bot.send_photo(
            chat_id=chat_id, photo=GIF_RECHAZADO,
            caption=f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({moderador['name']}). 𝖠𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈."
        )
        sesion_ahorcado["activa"] = False


# =====================================================================
# BOTONES
# =====================================================================

async def manejar_botones_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if sesion_ahorcado.get("activa"):
        await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
        return
    if not any(j["id"] == user.id for j in sesion_ahorcado["jugadores"]):
        sesion_ahorcado["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await query.message.reply_text(f"🪢 ֹ  {nombre_usuario(user)} se unió al ahorcado 𓂃")


# =====================================================================
# EL MODERADOR ENVÍA CATEGORÍA + PALABRA (EN PRIVADO)
# =====================================================================

async def escuchar_ahorcado_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    gid = esperando_palabra_ahorcado[user_id]

    if "-" not in texto:
        await update.message.reply_text("⚠️ Formato inválido. Usa: `categoria-palabra` (con un guión).", parse_mode="Markdown")
        return

    categoria, palabra = texto.split("-", 1)
    categoria = categoria.strip()
    palabra = _normalizar(palabra)

    if not palabra:
        await update.message.reply_text("⚠️ La palabra no puede estar vacía. Intenta de nuevo.")
        return

    sesion_ahorcado["categoria"] = categoria
    sesion_ahorcado["palabra"] = palabra
    del esperando_palabra_ahorcado[user_id]

    await update.message.reply_text("¡𝖯𝖺𝗅𝖺𝖻𝗋𝖺 𝗋𝖾𝖼𝗂𝖻𝗂𝖽𝖺! El juego comienza en el grupo.")

    pantalla = _pantalla_ahorcado(palabra, set())
    await context.bot.send_message(
        chat_id=gid,
        text=(f"🪢 **¡AHORCADO INICIADO!**\n\n"
              f"🗂️ Categoría: **{categoria.upper()}**\n\n"
              f"`{pantalla}`\n\n"
              f"{ETAPAS_AHORCADO[0]}\n"
              f"❤️ Intentos por jugador: {MAX_FALLOS}\n\n"
              f"Escribe una letra o un número en el chat para adivinar."),
        parse_mode="Markdown"
    )


# =====================================================================
# ADIVINAR LETRAS/NÚMEROS EN EL GRUPO
# =====================================================================

async def escuchar_ahorcado_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_ahorcado.get("activa") or not sesion_ahorcado.get("palabra"):
        return
    if user_id == sesion_ahorcado.get("moderador_id"):
        return
    if user_id not in sesion_ahorcado.get("vidas", {}):
        return  # no estaba entre los jugadores de esta ronda
    if user_id in sesion_ahorcado.get("eliminados", set()):
        return  # ya gastó sus intentos
    if not texto:
        return

    intento = _normalizar(texto)
    if len(intento) != 1 or not (intento.isalpha() or intento.isdigit()):
        return  # solo acepta un único caracter: letra o número

    palabra = sesion_ahorcado["palabra"]
    correctas = sesion_ahorcado["letras_correctas"]
    incorrectas = sesion_ahorcado["letras_incorrectas"]

    if intento in correctas or intento in incorrectas:
        await update.message.reply_text(f"⚠️ '{intento.upper()}' ya fue mencionado.")
        return

    nombre = update.effective_user.first_name

    if intento in palabra:
        correctas.add(intento)
        pantalla = _pantalla_ahorcado(palabra, correctas)

        if _palabra_completa(palabra, correctas):
            sesion_ahorcado["activa"] = False
            premio = sesion_puntos.get("premio_actual", {}).get("ahorcado", 0)
            sumar_robux(user_id, nombre_usuario(update.effective_user), premio, "Ahorcado 🪢")
            extra = f" (+{premio} Robux)" if premio else ""
            await update.message.reply_text(
                f"🎉 **¡{nombre} ADIVINÓ LA PALABRA!** 🎉\n\n"
                f"La palabra era: **{palabra.upper()}**{extra}",
                parse_mode="Markdown"
            )
            return

        await update.message.reply_text(
            f"✅ ¡'{intento.upper()}' está en la palabra!\n\n`{pantalla}`",
            parse_mode="Markdown"
        )
    else:
        incorrectas.add(intento)
        sesion_ahorcado["vidas"][user_id] -= 1
        vidas_restantes = sesion_ahorcado["vidas"][user_id]
        fallos_jugador = MAX_FALLOS - vidas_restantes
        etapa = ETAPAS_AHORCADO[min(fallos_jugador, MAX_FALLOS)]

        if vidas_restantes <= 0:
            sesion_ahorcado["eliminados"].add(user_id)
            await update.message.reply_text(
                f"💀 **¡{nombre} se quedó sin intentos y queda eliminado!**\n\n{etapa}",
                parse_mode="Markdown"
            )

            activos = [uid for uid in sesion_ahorcado["vidas"] if uid not in sesion_ahorcado["eliminados"]]
            if not activos:
                sesion_ahorcado["activa"] = False
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"☠️ **¡NADIE LOGRÓ ADIVINARLA!**\n\nLa palabra era: **{palabra.upper()}**",
                    parse_mode="Markdown"
                )
            return

        pantalla = _pantalla_ahorcado(palabra, correctas)
        await update.message.reply_text(
            f"❌ '{intento.upper()}' no está en la palabra.\n\n"
            f"{etapa}\n"
            f"`{pantalla}`\n"
            f"❤️ {nombre}, te quedan {vidas_restantes} intento(s).",
            parse_mode="Markdown"
        )
