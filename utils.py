# utils.py — Variables y funciones compartidas entre todos los juegos

import json
import os
import psycopg2
from telegram import Update
from telegram.ext import ContextTypes

# =====================================================================
# SUPABASE / POSTGRESQL
# =====================================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

def _get_conn():
    return psycopg2.connect(DATABASE_URL)

def _init_db():
    """Crea la tabla si no existe."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sesion (
                id TEXT PRIMARY KEY,
                datos JSONB NOT NULL
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error iniciando DB: {e}")

# !!  VARIABLES DE IMÁGENES  ───  ♥︎

GIF_BIENVENIDA = "https://i.postimg.cc/T1jPgpDX/upscalemedia-transformed-(3).jpg"
GIF_INFO       = "https://i.postimg.cc/9XgrQHCd/upscalemedia-transformed-(1).jpg"
GIF_AHORCADO   = "https://i.postimg.cc/6qg3jBTv/1000004761.jpg"
GIF_SNOWBALL   = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"
GIF_RATONES    = "https://i.postimg.cc/wMmHBLTM/1000004766.jpg"
GIF_RITMOAGO   = "https://i.postimg.cc/CMXk6g3n/upscalemedia-transformed.jpg"
GIF_ERROR      = "https://i.postimg.cc/G38XXrMW/Airbrush-IMAGE-ENHANCER-1779170852039-1779170852039.jpg"
GIF_OFFVAN     = "https://i.postimg.cc/mZ7k066k/upscalemedia-transformed-(2).jpg"
GIF_JITB       = "https://i.postimg.cc/fLqYbX2s/Airbrush-IMAGE-ENHANCER-1779302294635-1779302294635.jpg"
GIF_ZOMBIE     = "https://i.postimg.cc/8PWQJWM1/1000004869.jpg"
GIF_ENCUBRIDOR = "https://i.postimg.cc/QMmj1qZm/8a87226444e22cdd01aaff0060557a2b-(1).jpg"
GIF_CERO       = "https://i.postimg.cc/vH5TDfDZ/763aa3f517ca4e8b1b1ae10f55dfb556-(1).jpg"
GIF_LETRISTA   = "https://i.postimg.cc/Zndk78XB/Airbrush-IMAGE-ENHANCER-1779303536547-1779303536547.jpg"
GIF_RECHAZADO  = "https://i.postimg.cc/MTXZnXd8/1000005045.jpg"
GIF_COMANDOS   = "https://i.postimg.cc/6qjQHnqv/1000005043-(1).jpg"
GIF_CHARADA    = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"
GIF_CASERIA    = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"
GIF_PIRATA     = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"
GIF_MAYOROMENOR = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg"

# !!  SISTEMA DE ROBUX 💰  ───  ♥︎

ADMIN_IDS = set()

def _sesion_default():
    return {
        "activa": False,
        "jugadores": {},
        "premio_actual": {},
        "admin_id": None,
    }

def _cargar_sesion():
    """Carga la sesión desde Supabase."""
    try:
        _init_db()
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT datos FROM sesion WHERE id = 'principal'")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            datos = row[0]
            datos["jugadores"] = {int(k): v for k, v in datos.get("jugadores", {}).items()}
            return datos
    except Exception as e:
        print(f"⚠️ Error cargando sesión: {e}")
    return _sesion_default()

def _guardar_sesion():
    """Guarda la sesión en Supabase."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sesion (id, datos)
            VALUES ('principal', %s::jsonb)
            ON CONFLICT (id) DO UPDATE SET datos = EXCLUDED.datos
        """, (json.dumps(sesion_puntos, ensure_ascii=False),))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error guardando sesión: {e}")

# Cargar sesión al arrancar
sesion_puntos = _cargar_sesion()

def guardar_sesion():
    """Wrapper público para guardar la sesión desde otros módulos."""
    _guardar_sesion()

def sumar_robux(user_id: int, nombre: str, cantidad: int, concepto: str):
    """Suma robux al jugador si hay sesión activa."""
    if not sesion_puntos["activa"] or cantidad <= 0:
        return
    if user_id not in sesion_puntos["jugadores"]:
        sesion_puntos["jugadores"][user_id] = {"nombre": nombre, "robux": 0, "detalle": []}
    sesion_puntos["jugadores"][user_id]["robux"] += cantidad
    sesion_puntos["jugadores"][user_id]["detalle"].append(f"{concepto}: +{cantidad} \U0001f7e5")
    sesion_puntos["jugadores"][user_id]["nombre"] = nombre
    _guardar_sesion()

# !!  AUXILIARES  ───  ♥︎

def nombre_usuario(user):
    return f"@{user.username}" if user.username else user.first_name

def extraer_emojis(texto):
    import regex
    # Detecta todos los emojis sin diccionarios:
    # banderas, emojis compuestos (ZWJ), skin tones, símbolos, etc.
    patron_emoji = regex.compile(r'\p{Emoji}+', regex.UNICODE)
    patron_grafemas = regex.compile(r'\X', regex.UNICODE)
    grafemas = patron_grafemas.findall(texto)
    return [g for g in grafemas if patron_emoji.search(g) and not g.strip().isalnum()]

def dibujar_pantalla_code(codigo_secreto, intento_usuario):
    if not intento_usuario:
        return " ".join(["_" for _ in codigo_secreto])
    resultado = []
    for num_secreto, num_intento in zip(codigo_secreto, intento_usuario):
        if num_secreto == " ":
            resultado.append(" ")
        elif num_secreto == num_intento:
            resultado.append(num_secreto)
        else:
            resultado.append("_")
    return " ".join(resultado)

# =====================================================================
# COMANDOS ROBUX / WALLET
# =====================================================================

from telegram import Update
from telegram.ext import ContextTypes

async def cmd_new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_puntos["activa"]:
        await update.message.reply_text("𝖸𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈́𝗇 𝖺𝖼𝗍𝗂𝗏𝖺. 𝖴𝗌𝖺 /clean 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗎𝗇 𝗇𝗎𝖾𝗏𝗈 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝗈.")
        return
    sesion_puntos["activa"] = True
    sesion_puntos["jugadores"] = {}
    sesion_puntos["premio_actual"] = {}
    sesion_puntos["admin_id"] = update.effective_user.id
    _guardar_sesion()
    await update.message.reply_text(
        "¡𝖲𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺!\n\n"
        "𝖲𝖾 𝖾𝗆𝗉𝖾𝗓𝖺𝗋𝖺𝗇 𝖺 𝗀𝗎𝖺𝗋𝖽𝖺𝗋 𝗅𝖺𝗌 𝖿𝗂𝖼𝗁𝖺𝗌 𝗀𝖺𝗇𝖺𝖽𝖺𝗌 𝖾𝗇 𝖼𝖺𝖽𝖺 𝗃𝗎𝖾𝗀𝗈.\n"
    )
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")

async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sesion_puntos["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖼𝗍𝗂𝗏𝖺 𝖺𝗎𝗇. 𝖤𝗌𝗉𝖾𝗋𝖺 𝖺 𝗊𝗎𝖾 𝗎𝗇 𝖺𝖽𝗆𝗂𝗇 𝗊𝗎𝖾 𝗎𝗌𝖾 /𝗇𝖾𝗐_𝗌𝖾𝗌𝗌𝗂𝗈𝗇 𝗉𝖺𝗋𝖺 𝖾𝗆𝗉𝖾𝗓𝖺𝗋 𝖼𝗈𝗇 𝖾𝗅 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝗈.")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return
    uid = update.effective_user.id
    datos = sesion_puntos["jugadores"].get(uid)
    if not datos or datos["robux"] == 0:
        await update.message.reply_text("¡𝖠𝗎𝗇 𝗇𝗈 𝖼𝗎𝖾𝗇𝗍𝖺𝗌 𝖼𝗈𝗇 𝖿𝗂𝖼𝗁𝖺𝗌, 𝗌𝖾𝗀𝗎𝗋𝗈 𝗊𝗎𝖾 𝖾𝗇 𝖾𝗅 𝗉𝗋𝗈𝗑𝗂𝗆𝗈 𝗃𝗎𝖾𝗀𝗈 𝖼𝗈𝗇𝗌𝗂𝗀𝗎𝖾𝗌, 𝖻𝗎𝖾𝗇𝖺 𝗌𝗎𝖾𝗋𝗍𝖾!")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return
    detalle = "\n".join(datos["detalle"])
    await update.message.reply_text(
        f"𝖧𝗈𝗅𝖺, {nombre_usuario(update.effective_user)}:\n\n"
        f"{detalle}\n\n"
        f"𝖳𝗎 𝖿𝗈𝗋𝗍𝗎𝗇𝖺 𝖺𝗌𝖼𝗂𝖾𝗇𝖽𝖾 𝖺 {datos['robux']} 𝖿𝗂𝖼𝗁𝖺𝗌"
    )
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")

async def cmd_spent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("𝖤𝗌𝗍𝖾 𝖼𝗈𝗆𝖺𝗇𝖽𝗈 𝗌𝗈𝗅𝗈 𝖿𝗎𝗇𝖼𝗂𝗈𝗇𝖺 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈 𝗒 𝖾𝗌 𝖽𝖾 𝗎𝗌𝗈 𝖾𝗑𝖼𝗅𝗎𝗌𝗂𝗏𝗈 𝖽𝖾 𝗅𝖺 𝗉𝖾𝗋𝗌𝗈𝗇𝖺 𝗊𝗎𝖾 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇, 𝗅𝗈 𝗌𝗂𝖾𝗇𝗍𝗈")
        return
    if not sesion_puntos["activa"]:
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝖺𝖼𝗍𝗂𝗏𝖺.")
        return
    if update.effective_user.id != sesion_puntos.get("admin_id"):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝗏𝖾𝗋 𝖾𝗌𝗍𝗈.")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")

        return
    if not sesion_puntos["jugadores"]:
        await update.message.reply_text("𝖭𝖺𝖽𝗂𝖾 𝗁𝖺 𝗀𝖺𝗇𝖺𝖽𝗈 𝗋𝗈𝖻𝗎𝗑 𝗍𝗈𝖽𝖺𝗏𝗂𝖺.")
        return
    tabla = sorted(sesion_puntos["jugadores"].items(), key=lambda x: x[1]["robux"], reverse=True)
    medallas = ["🥇", "🥈", "🥉"]
    msg = "𝗥𝗲𝘀𝘂𝗺𝗲𝗻 𝗱𝗲 𝗹𝗼𝘀 𝗴𝗮𝗻𝗮𝗱𝗼𝗿𝗲𝘀 𝗽𝗼𝗿 𝗷𝘂𝗲𝗴𝗼:\n\n"
    total = 0
    for i, (uid, datos) in enumerate(tabla):
        dec = medallas[i] if i < 3 else "🔹"
        msg += f"{dec} {datos['nombre']}: **{datos['robux']} Robux**\n"
        total += datos["robux"]
    msg += f"\n𝖣𝖾𝗌𝖾𝗆𝖻𝗈𝗅𝗌𝖺 𝖾𝗌𝗈𝗌 {total} 𝗋𝗈𝖻𝗎𝗑 𝖼𝗁𝗂𝗄𝗂"
    await update.message.reply_text(msg)
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_puntos["activa"] = False
    sesion_puntos["jugadores"] = {}
    sesion_puntos["premio_actual"] = {}
    _guardar_sesion()
    await update.message.reply_text("¡𝖫𝗈𝗌 𝖽𝖺𝗍𝗈𝗌 𝗁𝖺𝗇 𝗌𝗂𝖽𝗈 𝖻𝗈𝗋𝗋𝖺𝖽𝗈𝗌 𝖼𝗈𝗋𝗋𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾, 𝖾𝗌𝗉𝖾𝗋𝗈 𝗏𝖾𝗋𝗇𝗈𝗌 𝗉𝗋𝗈𝗇𝗍𝗈!")

async def detener_juegos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from zombie import sesion_zombie
    from caseria import sesion_caseria
    from box import sesion_box
    from charada import sesion_charada
    from pirata import sesion_pirata
    from mayoromenor import sesion_mom
    from carrera import sesion_carrera
    from anagrama import reset_anagrama_chat
    from guessong import reset_guessong_chat
    from slots import sesion_slots

    chat_id = update.effective_chat.id

    sesion_zombie["activa"] = False
    sesion_zombie["jugadores"] = []
    sesion_zombie["zombies"] = []
    sesion_zombie["vivos"] = []
    sesion_zombie["fase"] = None
    from caseria import sesion_caseria
    if chat_id in sesion_caseria:
        del sesion_caseria[chat_id]
    if chat_id in sesion_box:
        sesion_box[chat_id]["activa"] = False
        sesion_box[chat_id]["jugadores"] = []
    sesion_charada["activa"] = False
    sesion_charada["fase_registro"] = False
    sesion_charada["jugadores"] = []
    sesion_pirata["activa"] = False
    sesion_pirata["jugadores"] = []
    if chat_id in sesion_mom:
        del sesion_mom[chat_id]
    if chat_id in sesion_carrera:
        del sesion_carrera[chat_id]
    if chat_id in sesion_slots:
        del sesion_slots[chat_id]
    reset_anagrama_chat(chat_id)
    reset_guessong_chat(chat_id)

    await update.message.reply_text("𝖲𝖾 𝖼𝖾𝗋𝗋𝖺𝗋𝗈𝗇 𝗍𝗈𝖽𝖺𝗌 𝗅𝖺𝗌 𝗉𝖺𝗋𝗍𝗂𝖽𝖺𝗌 𝖺𝖼𝗍𝗂𝗏𝖺𝗌")
    await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
