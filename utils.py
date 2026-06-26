# utils.py — Variables y funciones compartidas entre todos los juegos

import json
import os
from telegram import Update
from telegram.ext import ContextTypes

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
SESION_FILE = "sesion_puntos.json"

def _sesion_default():
    return {
        "activa": False,
        "jugadores": {},
        "premio_actual": {},
    }

def _cargar_sesion():
    """Carga la sesión desde el archivo JSON si existe."""
    if os.path.exists(SESION_FILE):
        try:
            with open(SESION_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                # Las keys de jugadores vienen como string en JSON, las convertimos a int
                datos["jugadores"] = {int(k): v for k, v in datos.get("jugadores", {}).items()}
                return datos
        except Exception:
            pass
    return _sesion_default()

def _guardar_sesion():
    """Guarda la sesión actual en el archivo JSON."""
    try:
        with open(SESION_FILE, "w", encoding="utf-8") as f:
            json.dump(sesion_puntos, f, ensure_ascii=False, indent=2)
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
        await update.message.reply_text("⚠️ Ya hay una sesión activa. Usa /reset antes de abrir una nueva.")
        return
    sesion_puntos["activa"] = True
    sesion_puntos["jugadores"] = {}
    sesion_puntos["premio_actual"] = {}
    _guardar_sesion()
    await update.message.reply_text(
        "✅ **¡Sesión iniciada!** 🟥\n\n"
        "Los Robux ganados a partir de ahora se irán acumulando.\n"
        "Recuerda poner el premio al iniciar cada juego:\n\n"
        "`.start_zombie 5 15` → 5 sobrevivientes / 15 zombie\n"
        "`.start_caseria 10` → 10 al ganador\n"
        "`.start_cipher 8` → 8 al ganador\n"
        "`.start_box 6` → 6 al ganador\n"
        "`.start_pirata 5` → 5 a los sobrevivientes",
        parse_mode="Markdown"
    )

async def cmd_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not sesion_puntos["activa"]:
        await update.message.reply_text("No hay ninguna sesión activa aún. Pide a un admin que use /new_session.")
        return
    uid = update.effective_user.id
    datos = sesion_puntos["jugadores"].get(uid)
    if not datos or datos["robux"] == 0:
        await update.message.reply_text("👛 Aún no tienes Robux acumulados en esta sesión. ¡A jugar!")
        return
    detalle = "\n".join(datos["detalle"])
    await update.message.reply_text(
        f"👛 **Tu cartera, {nombre_usuario(update.effective_user)}:**\n\n"
        f"{detalle}\n\n"
        f"**Total: {datos['robux']} Robux 🟥**",
        parse_mode="Markdown"
    )

async def cmd_spent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text("⛔ Este comando solo funciona en privado.")
        return
    if not sesion_puntos["activa"]:
        await update.message.reply_text("No hay ninguna sesión activa.")
        return
    if not sesion_puntos["jugadores"]:
        await update.message.reply_text("Nadie ha ganado Robux todavía en esta sesión.")
        return
    tabla = sorted(sesion_puntos["jugadores"].items(), key=lambda x: x[1]["robux"], reverse=True)
    medallas = ["🥇", "🥈", "🥉"]
    msg = "💰 **Resumen de la sesión:**\n\n"
    total = 0
    for i, (uid, datos) in enumerate(tabla):
        dec = medallas[i] if i < 3 else "🔹"
        msg += f"{dec} {datos['nombre']}: **{datos['robux']} Robux**\n"
        total += datos["robux"]
    msg += f"\n**Total a pagar: {total} Robux 🟥**"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_puntos["activa"] = False
    sesion_puntos["jugadores"] = {}
    sesion_puntos["premio_actual"] = {}
    _guardar_sesion()
    await update.message.reply_text("🗑️ Sesión reseteada. Los datos han sido borrados.")

async def detener_juegos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from cipher import sesion_cipher
    from zombie import sesion_zombie
    from caseria import sesion_caseria
    from box import sesion_box
    from charada import sesion_charada
    from pirata import sesion_pirata

    sesion_cipher["activa"] = False
    sesion_cipher["jugadores"] = []
    sesion_zombie["activa"] = False
    sesion_zombie["jugadores"] = []
    sesion_zombie["zombies"] = []
    sesion_zombie["vivos"] = []
    sesion_zombie["fase"] = None
    sesion_caseria["activa"] = False
    sesion_caseria["jugadores"] = {}
    chat_id = update.effective_chat.id
    if chat_id in sesion_box:
        sesion_box[chat_id]["activa"] = False
        sesion_box[chat_id]["jugadores"] = []
    sesion_charada["activa"] = False
    sesion_charada["fase_registro"] = False
    sesion_charada["jugadores"] = []
    sesion_pirata["activa"] = False
    sesion_pirata["jugadores"] = []

    await update.message.reply_photo(
        photo=GIF_OFFVAN,
        caption="¡CLOSE VAN!\n\nSe cerraron todas las rondas existentes.")
