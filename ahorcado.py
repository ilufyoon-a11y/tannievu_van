import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter
from telegram.ext import ContextTypes

from utils import (
    GIF_AHORCADO, GIF_ERROR, GIF_RECHAZADO, GIF_LETRISTA,
    sesion_puntos, sumar_robux, nombre_usuario, es_admin_sesion,
)

# !!  MANEJO SEGURO DE FLOOD CONTROL  ───  ♥︎

async def _enviar_seguro(func, *args, **kwargs):
    for _ in range(3):
        try:
            return await func(*args, **kwargs)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
    return await func(*args, **kwargs)

# !!  STICKERS DEL AHORCADO (0 a 6 fallos)  ───  ♥︎

STICKERS_AHORCADO = [
    "CAACAgEAAxkBA1p40mpaoI-_k_InC_aydY5-juIUA5euAAL0BgAC5D7QRnWYDw4FgkBQPQQ",                     # 0 fallos
    "CAACAgEAAxkBA1p41GpaoJAAATNFXHx6gea5gZCuagz8MgAC5AsAAqoQ2EZWnL4acVJYxj0E",
    "CAACAgEAAxkBA1p41mpaoJGyWPLOv4PGA_1k8BeYJH_kAAMIAAI-TdhGR7_bqNKN8BQ9BA",
    "CAACAgEAAxkBA1p42GpaoJIUuHFng17PLKmgNlg7UvK5AAJXCQACQQvRRrLm7ICclZa7PQQ",
    "CAACAgEAAxkBA1p43GpaoJMX2CIPhkEOwS9c_gxi-OyHAAJcCAACvv7ZRmN7xK5ybM7qPQQ",
    "CAACAgEAAxkBA1p44GpaoJbUUdOqudBO-8zZYgzO5kKqAALgBgACgiPZRsSp0w-MktcFPQQ",
    "CAACAgEAAxkBA1p43mpaoJUy-4xgZ5oZ3RoUAAE10qO1OwACJQcAAkF_2Uako4EHnBEruj0E",   # eliminado
]

MAX_FALLOS = len(STICKERS_AHORCADO) - 1  # 6 fallos = eliminado

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


def _letras_intentadas(incorrectas: set) -> str:

    if not incorrectas:
        return ""
    lista = ", ".join(c.upper() for c in sorted(incorrectas))
    return f"\n\n<blockquote>𝗟𝗲𝘁𝗿𝗮𝘀 𝗲𝗿𝗿𝗼𝗻𝗲𝗮𝘀: {lista}</blockquote>"


# =====================================================================
# COMANDOS
# =====================================================================

async def unirse_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return
        
    if sesion_ahorcado["activa"]:
        await _enviar_seguro(update.message.reply_text, "¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
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
    await _enviar_seguro(
        update.message.reply_photo,
        photo=GIF_AHORCADO,
        caption="๑ ꞈ ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺𝗅 𝖠𝗁𝗈𝗋𝖼𝖺𝖽𝗈! ⋆ ٠\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺.\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_ahorcado &lt;f s t&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )


async def iniciar_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["ahorcado"] = int(args[0])
        except ValueError:
            pass

    if len(sesion_ahorcado["jugadores"]) < 2:
        await _enviar_seguro(
            update.message.reply_text,
            "ⓘ ˖ ࣪ 𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈 ᵎᵎ")
        await _enviar_seguro(
            update.message.reply_sticker,
            sticker="CAACAgEAAxkBA0xCcWpKcoeEBYZYhxHjkhqbGntnlJzXAAJhBgACiPVIRbbKF2KzkH0nPAQ")
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
    await _enviar_seguro(
        update.message.reply_text,
        f"Ꜥ ¡{moderador['name']} 𝖿𝗎𝖾 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝖼𝗈𝗆𝗈 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋! ⸝⸝\n\n𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝖺 𝗊𝗎𝖾 𝖾𝗇𝗏𝗂𝖾 𝗅𝖺 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂́𝖺 𝗒 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺")
    await _enviar_seguro(
        context.bot.send_sticker,
        chat_id=chat_id,
        sticker="CAACAgEAAxkBA1QAAaRqUwu5n3oGAo9Cs_xd1rPRRobkzAACgwYAAtz6uUQbnfNeh5189TwE"
    )

    try:
        await _enviar_seguro(
            context.bot.send_message,
            chat_id=moderador["id"],
            text=("<b>¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋!</b>\n\n"
                  "𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂𝖺 𝗅𝖺 𝖼𝖺𝗍𝖾𝗀𝗈𝗋𝗂𝖺 𝗒 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺 𝗈 𝖿𝗋𝖺𝗌𝖾 𝗌𝖾𝗉𝖺𝗋𝖺𝖽𝖺𝗌 𝗉𝗈𝗋 𝗎𝗇 𝗀𝗎𝗂𝗈𝗇 '-'.\n\n"
                  "<blockquote>𝖤𝗃𝖾𝗆𝗉𝗅𝗈: Fruta - Manzana</blockquote>"),
            parse_mode="HTML"
        )
        await _enviar_seguro(
            context.bot.send_sticker,
            chat_id=moderador["id"],
            sticker="CAACAgEAAxkBA0WkVGpCeFxv3hOINwnldaJhBC_FXDhhAAIbCQAC-nQYRn3vKswkIhekPAQ"
        )

    except Exception:
        await _enviar_seguro(
            update.message.reply_text,
            f"ⓘ ˖ ࣪ 𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 {moderador['name']}. \n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 ᵎᵎ")
        await _enviar_seguro(
            context.bot.send_sticker,
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA08s3mpNqQrISXcnzmYG_9fOSF9e-8cBAAKNBwAC7QJBRHEkAAHybHUSQDwE")
        sesion_ahorcado["activa"] = False
        return

# =====================================================================
# BOTONES
# =====================================================================

async def manejar_botones_ahorcado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    await query.answer()

    if sesion_ahorcado.get("activa"):
        await query.answer("ⓘ ˖ ࣪ ¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈! ᵎ", show_alert=True)
        return
    if not any(j["id"] == user.id for j in sesion_ahorcado["jugadores"]):
        sesion_ahorcado["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
        await _enviar_seguro(query.message.reply_text, f"— {nombre_usuario(user)} se unio 𝅄 𖹭' ა")


# =====================================================================
# EL MODERADOR ENVÍA CATEGORÍA + PALABRA (EN PRIVADO)
# =====================================================================

async def escuchar_ahorcado_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    gid = esperando_palabra_ahorcado[user_id]

    if "-" not in texto:
        await _enviar_seguro(
            update.message.reply_text,
            "Formato inválido. Usa: `categoria-palabra`")
        return

    categoria, palabra = texto.split("-", 1)
    categoria = categoria.strip()
    palabra = _normalizar(palabra)

    if not palabra:
        await _enviar_seguro(update.message.reply_text, "⚠️ La palabra no puede estar vacía. Intenta de nuevo.")
        return

    sesion_ahorcado["categoria"] = categoria
    sesion_ahorcado["palabra"] = palabra
    del esperando_palabra_ahorcado[user_id]

    await _enviar_seguro(update.message.reply_text, "¡𝖯𝖺𝗅𝖺𝖻𝗋𝖺 𝗋𝖾𝖼𝗂𝖻𝗂𝖽𝖺! El juego comienza en el grupo.")

    pantalla = _pantalla_ahorcado(palabra, set())
    await _enviar_seguro(
        context.bot.send_message,
        chat_id=gid,
        text=(f"¡𝖤𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋 𝖺𝖼𝖺𝖻𝖺 𝖽𝖾 𝖽𝖺𝗋 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺!\n\n"
              f"𝗖𝗔𝗧𝗘𝗚𝗢𝗥𝗜𝗔: {categoria.upper()}\n\n"
              f"𝗧𝗔𝗕𝗟𝗘𝗥𝗢: {pantalla}\n\n"
              f"𝗜𝗡𝗧𝗘𝗡𝗧𝗢𝗦 𝗣𝗢𝗥 𝗝𝗨𝗚𝗔𝗗𝗢𝗥: {MAX_FALLOS}\n\n"
              f"¡𝖤𝗌𝖼𝗋𝗂𝖻𝖾 𝗎𝗇𝖺 𝗅𝖾𝗍𝗋𝖺 𝗈 𝗎𝗇 𝗇𝗎𝗆𝖾𝗋𝗈 𝗉𝖺𝗋𝖺 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋!"
              f"{_letras_intentadas(set())}"),
        parse_mode="HTML"
    )


# =====================================================================
# ADIVINAR LETRAS/NÚMEROS EN EL GRUPO
# =====================================================================

async def escuchar_ahorcado_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_ahorcado.get("activa") or not sesion_ahorcado.get("palabra"):
        return
    if user_id == sesion_ahorcado.get("moderador_id"):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        except Exception:
            pass  # el bot puede no tener permisos de borrado en ese chat
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

    if intento in correctas:
        await _enviar_seguro(
            update.message.reply_text,
            f"𝖠𝗒, <b>{intento.upper()}</b> 𝗒𝖺 𝖾𝗌𝗍𝖺 𝖾𝗇 𝖾𝗅 𝗍𝖺𝖻𝗅𝖾𝗋𝗈.",
            parse_mode="HTML"
        )
        return

    ya_habia_fallado = intento in incorrectas
    nombre = nombre_usuario(update.effective_user)

    if intento in palabra:
        correctas.add(intento)
        pantalla = _pantalla_ahorcado(palabra, correctas)

        if _palabra_completa(palabra, correctas):
            sesion_ahorcado["activa"] = False
            premio = sesion_puntos.get("premio_actual", {}).get("ahorcado", 0)
            sumar_robux(user_id, nombre_usuario(update.effective_user), premio, "𝗔𝗵𝗼𝗿𝗰𝗮𝗱𝗼")
            extra = f" (+ {premio} 𝗋𝗈𝖻𝗎𝗑)" if premio else ""
            await _enviar_seguro(
                update.message.reply_text,
                f"<b>¡{nombre} 𝖠𝖣𝖨𝖵𝖨𝖭𝖮 𝖫𝖠 𝖯𝖠𝖫𝖠𝖡𝖱𝖠!</b>\n\n"
                f"𝖫𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺 𝖾𝗋𝖺: <b>{palabra.upper()}</b>",
                parse_mode="HTML"
            )
            await _enviar_seguro(
                context.bot.send_sticker,
                chat_id=chat_id,
                sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
            )
            return

        vidas_restantes = sesion_ahorcado["vidas"][user_id]
        await _enviar_seguro(
            update.message.reply_text,
            f"𝗧𝗔𝗕𝗟𝗘𝗥𝗢: {pantalla}\n\n"
            f"{nombre}, 𝖼𝗎𝖾𝗇𝗍𝖺𝗌 𝖼𝗈𝗇 {vidas_restantes} 𝗂𝗇𝗍𝖾𝗇𝗍𝗈𝗌."
            f"{_letras_intentadas(incorrectas)}",
            parse_mode="HTML"
        )
    else:
        incorrectas.add(intento)
        sesion_ahorcado["vidas"][user_id] -= 1
        vidas_restantes = sesion_ahorcado["vidas"][user_id]
        fallos_jugador = MAX_FALLOS - vidas_restantes
        sticker_etapa = STICKERS_AHORCADO[min(fallos_jugador, MAX_FALLOS)]

        if vidas_restantes <= 0:
            sesion_ahorcado["eliminados"].add(user_id)
            aviso_repetida = (
                f" (𝖠𝗒, 𝖾𝗌𝖺 𝗅𝖾𝗍𝗋𝖺 𝗒𝖺 𝗌𝖾 𝗌𝖺𝖻𝗂𝖺 𝗊𝗎𝖾 𝗇𝗈 𝖿𝗈𝗋𝗆𝖺𝖻𝖺 𝗉𝖺𝗋𝗍𝖾 𝖽𝖾 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺)" if ya_habia_fallado else ""
            )
            await _enviar_seguro(
                update.message.reply_text,
                f"¡{nombre} 𝖺𝗀𝗈𝗍𝗈 𝗍𝗈𝖽𝗈𝗌 𝗌𝗎𝗌 𝗂𝗇𝗍𝖾𝗇𝗍𝗈𝗌, 𝗊𝗎𝖾𝖽𝖺 𝖾𝗅𝗂𝗆𝗂𝗇𝖺𝖽𝗈!{aviso_repetida}"
            )
            if sticker_etapa:
                await _enviar_seguro(context.bot.send_sticker, chat_id=chat_id, sticker=sticker_etapa)

            activos = [uid for uid in sesion_ahorcado["vidas"] if uid not in sesion_ahorcado["eliminados"]]
            if not activos:
                sesion_ahorcado["activa"] = False
                await _enviar_seguro(
                    context.bot.send_message,
                    chat_id=chat_id,
                    text=f"¡𝗡𝗔𝗗𝗜𝗘 𝗟𝗢𝗚𝗥𝗢 𝗔𝗗𝗜𝗩𝗜𝗡𝗔𝗥ⵑ\n\nLa palabra era: <b>{palabra.upper()}</b>",
                    parse_mode="HTML"
                )
            return

        pantalla = _pantalla_ahorcado(palabra, correctas)
        aviso_repetida = (
            f"\n<i>(𝖠𝗒, {nombre} 𝖾𝗌𝖺 𝗅𝖾𝗍𝗋𝖺 𝗒𝖺 𝗌𝖾 𝗌𝖺𝖻𝗂𝖺 𝗊𝗎𝖾 𝗇𝗈 𝖿𝗈𝗋𝗆𝖺𝖻𝖺 𝗉𝖺𝗋𝗍𝖾 𝖽𝖾 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺)</i>"
            if ya_habia_fallado else ""
        )
        await _enviar_seguro(
            update.message.reply_text,
            f"<b>{intento.upper()}</b> 𝗇𝗈 𝖿𝗈𝗋𝗆𝖺 𝗉𝖺𝗋𝗍𝖾 𝖽𝖾 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺.\n\n"
            f"𝗧𝗔𝗕𝗟𝗘𝗥𝗢: {pantalla}\n\n"
            f"{nombre}, 𝖼𝗎𝖾𝗇𝗍𝖺𝗌 𝖼𝗈𝗇 {vidas_restantes} 𝗂𝗇𝗍𝖾𝗇𝗍𝗈𝗌.{aviso_repetida}"
            f"{_letras_intentadas(incorrectas)}",
            parse_mode="HTML"
        )
        if sticker_etapa:
            await _enviar_seguro(context.bot.send_sticker, chat_id=chat_id, sticker=sticker_etapa)
