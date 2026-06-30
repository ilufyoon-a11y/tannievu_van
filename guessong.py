import random
import requests
import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_CASERIA

# ================= DICCIONARIOS Y CONFIG =================

lovers = ["BTS", "RM", "Agust D", "j-hope", "Jimin", "V", "Jung Kook", "Jin"]

# Igual que en box.py: una sesión por chat_id, jugadores guardados como
# lista de dicts {id, name, username}. Así el bot reconoce a la persona
# por su id real de Telegram y no por su first_name (que puede repetirse
# o cambiar).
sesion_song = {}   # chat_id -> {"jugadores": [...], "activa": bool, ...}

# ================= MOTOR DE AUDIO (iTunes & Pydub) =================

def obtener_canciones():
    seleccionados = random.sample(lovers, 4)
    all_songs = []

    for artista in seleccionados:
        try:
            url = f"https://itunes.apple.com/search?term={artista}&entity=song&limit=15"
            response = requests.get(url).json()
            canciones_validas = [track for track in response.get('results', []) if track.get('previewUrl')]
            all_songs.extend(canciones_validas)
        except Exception:
            continue

    if len(all_songs) < 4:
        url = "https://itunes.apple.com/search?term=BTS&entity=song&limit=30"
        response = requests.get(url).json()
        all_songs = [track for track in response.get('results', []) if track.get('previewUrl')]

    random.shuffle(all_songs)
    correcta = random.choice(all_songs)

    falsas_filtradas = []
    for c in all_songs:
        if c['trackId'] != correcta['trackId'] and c['trackName'].lower() != correcta['trackName'].lower():
            if c['trackName'] not in [f['trackName'] for f in falsas_filtradas]:
                falsas_filtradas.append(c)

    if len(falsas_filtradas) < 3:
        falsas_filtradas = [c for c in all_songs if c['trackId'] != correcta['trackId']]

    falsas = random.sample(falsas_filtradas, 3)
    opciones = [correcta] + falsas
    random.shuffle(opciones)
    return correcta, opciones

def descargar_y_recortar_audio(url_audio):
    archivo_temporal = "temp_itunes.m4a"
    archivo_final = "reto_van.mp3"

    audio_data = requests.get(url_audio).content
    with open(archivo_temporal, "wb") as f:
        f.write(audio_data)

    audio = AudioSegment.from_file(archivo_temporal)
    recorte = audio[:4000]
    recorte.export(archivo_final, format="mp3")

    if os.path.exists(archivo_temporal):
        os.remove(archivo_temporal)
    return archivo_final

# ================= FLUJO DEL JUEGO =================

async def enviar_siguiente_ronda(chat_id, context: ContextTypes.DEFAULT_TYPE):
    sesion = sesion_song[chat_id]
    try:
        correcta, opciones = obtener_canciones()
        archivo_reto = descargar_y_recortar_audio(correcta['previewUrl'])

        sesion["correcta"] = correcta['trackName'].lower().strip()

        botones = [[InlineKeyboardButton(cancion['trackName'], callback_data=f"mu_{cancion['trackName']}")] for cancion in opciones]
        reply_markup = InlineKeyboardMarkup(botones)

        with open(archivo_reto, 'rb') as audio:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio,
                caption=f"RONDA {sesion['ronda']}/5\n\n¿Lograste identificar que canción es?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        if os.path.exists(archivo_reto):
            os.remove(archivo_reto)

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Se presento un error al pasar a la siguiente ronda, por favor, reinicia el juego: {e}")
        sesion["activa"] = False

# ================= CONTROL DE LA SALA (ESTILO BOX) =================

async def unirse_adivina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abre la sala de reclutamiento, mismo estilo y mismo manejo de jugadores que box.py"""
    chat_id = update.effective_chat.id

    sesion_song[chat_id] = {
        "jugadores": [],
        "ronda": 1,
        "correcta": "",
        "puntajes": {},
        "activa": False,
        "creador_id": update.effective_user.id,
    }

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗖𝗥𝗔ㅤㅤ!¡", callback_data="unirme_adivina_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ Adivinɑr lɑ cɑncion!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_adivina &lt;premio&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def manejar_boton_unirse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Agrega jugadores por id (igual que box), evitando duplicados aunque cambien de nombre."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    await query.answer()

    if chat_id not in sesion_song:
        return

    sesion = sesion_song[chat_id]

    if sesion["activa"]:
        await query.answer("¡Lo siento, ya hay una partida en curso!", show_alert=True)
        return

    if any(j["id"] == user.id for j in sesion["jugadores"]):
        return

    sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
    await query.message.reply_text(f"🎧  {nombre_usuario(user)} se unio 𓂃")

async def iniciar_adivina_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valida los requisitos minimos y arranca la primera ronda"""
    chat_id = update.effective_chat.id

    if chat_id not in sesion_song or len(sesion_song[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personas para jugar.")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    sesion = sesion_song[chat_id]

    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["adivina"] = premio

    sesion["activa"] = True
    sesion["ronda"] = 1
    sesion["puntajes"] = {j["id"]: 0 for j in sesion["jugadores"]}

    await context.bot.send_message(
        chat_id=chat_id,
        text="🎧 ¡El juego ha comenzado! 🌸\nPreparando los clips... ¡Preparen sus oidos!",
    )

    await enviar_siguiente_ronda(chat_id, context)

async def verificar_respuesta_musica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa las respuestas usando el id del usuario, no su first_name."""
    query = update.callback_query
    chat_id = query.message.chat.id
    user = query.from_user
    user_name = nombre_usuario(user)

    if chat_id not in sesion_song or not sesion_song[chat_id]["activa"]:
        await query.answer()
        return

    sesion = sesion_song[chat_id]

    if not any(j["id"] == user.id for j in sesion["jugadores"]):
        await query.answer("🛑 ¡No estas inscrito en esta sala, causa!", show_alert=True)
        return

    cancion_elegida = query.data.replace("mu_", "").lower().strip()
    cancion_correcta = sesion["correcta"]

    # --- CASO 1: ¡ACERTÓ! (Termina la ronda) ---
    if cancion_elegida == cancion_correcta:
        await query.answer(f"🎉 ¡Acertaste, {user_name}!")
        sesion["puntajes"][user.id] = sesion["puntajes"].get(user.id, 0) + 1

        # Guardar robux por ronda acertada
        premio_ronda = sesion_puntos.get("premio_actual", {}).get("adivina", 0)
        if premio_ronda > 0:
            sumar_robux(user.id, user_name, premio_ronda, f"Adivina la canción 🎧 ronda {sesion['ronda']}")

        texto_resultado = f"🎉 **¡PUNTO PARA {user_name.upper()}!** 🌸\nAcertó: `{cancion_correcta.title()}`"
        await query.edit_message_caption(caption=texto_resultado, parse_mode="Markdown")

        if sesion["ronda"] < 5:
            sesion["ronda"] += 1
            tablero_corto = "\n".join([
                f"• {next((j['name'] for j in sesion['jugadores'] if j['id'] == uid), uid)}: `{pts}` pts"
                for uid, pts in sesion["puntajes"].items()
            ])
            msg_puntos = f"✨ **Tablero de posiciones:**\n{tablero_corto}\n\n¡Siguiente canción! 👇"

            await context.bot.send_message(chat_id=chat_id, text=msg_puntos, parse_mode="Markdown")
            await enviar_siguiente_ronda(chat_id, context)
        else:
            sesion["activa"] = False
            tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
            medallas = ["🥇", "🥈", "🥉"]

            texto_final = "🏁 **¡FIN DEL JUEGO!** 🏁\n\n🏆 **RESULTADOS FINALES:**\n"
            for i, (uid_p, pts) in enumerate(tabla):
                jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_p), None)
                nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_p}"
                dec = medallas[i] if i < 3 else "🔹"
                texto_final += f"{dec} {nombre_p}: `{pts}` puntos\n"

            texto_final += "\n¿Quieren revancha? Abran otra sala usando `/adivina` 👑🔥"
            await context.bot.send_message(chat_id=chat_id, text=texto_final, parse_mode="Markdown")

    # --- CASO 2: SE EQUIVOCÓ (La ronda NO se muere, los demás continúan) ---
    else:
        await query.answer(f"❌ Esa no es la respuesta, {user_name}...", show_alert=False)

        mencion = user.mention_markdown_v2() if user.username else f"`{user_name}`"
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"💀 Esa no es la respuesta, {mencion} ¡Sigan intentando! 🎧",
        )
