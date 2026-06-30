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
            canciones_validas = [
                track for track in response.get('results', [])
                if track.get('previewUrl') and _es_artista_valido(track.get('artistName', ''))
            ]
            all_songs.extend(canciones_validas)
        except Exception:
            continue

    if len(all_songs) < 4:
        url = "https://itunes.apple.com/search?term=BTS&entity=song&limit=30"
        response = requests.get(url).json()
        all_songs = [
            track for track in response.get('results', [])
            if track.get('previewUrl') and _es_artista_valido(track.get('artistName', ''))
        ]

    if not all_songs:
        # Último recurso: traer canciones de BTS sin filtrar para que el
        # juego no se rompa, aunque sea menos preciso.
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

# Nombres de artista "tal cual" aparecen en iTunes para BTS y sus miembros
# (en minúsculas, para comparar). Esto evita que el término de búsqueda
# genérico ("V", "RM", "Jin"...) traiga canciones de artistas que no
# tienen nada que ver (ej. Maroon 5).
_ARTISTAS_VALIDOS = {
    "bts", "rm", "agust d", "j-hope", "jimin", "v", "jung kook", "jungkook", "jin",
}

def _es_artista_valido(artist_name: str) -> bool:
    nombre = artist_name.lower().strip()
    # Coincidencia exacta o "bts" como parte del nombre del artista
    # (ej. "BTS", "j-hope (방탄소년단)" suele incluir bts en algún punto,
    # pero para evitar falsos positivos solo aceptamos match exacto o
    # que contenga explícitamente "bts").
    if nombre in _ARTISTAS_VALIDOS:
        return True
    if "bts" in nombre or "방탄소년단" in nombre:
        return True
    return False


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

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_adivina_click")
    await update.message.reply_photo(
        photo=GIF_CASERIA,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ Adivinɑr lɑ cɑncion!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_guess &lt;premio&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
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
        await query.answer("¡Lo siento, yɑ hɑy unɑ pɑrtidɑ en curso!", show_alert=True)
        return

    if any(j["id"] == user.id for j in sesion["jugadores"]):
        return

    sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
    await query.message.reply_text(f"🎧  {nombre_usuario(user)} se unio 𓂃")

async def iniciar_adivina_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valida los requisitos minimos y arranca la primera ronda"""
    chat_id = update.effective_chat.id

    if chat_id not in sesion_song or len(sesion_song[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("Se requiere un minimo de 2 personɑs pɑrɑ jugɑr.")
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
        text="🎧 ¡El juego hɑ comenzɑdo! Se estɑn extrɑyendo los clips, esten ɑtentos",
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
        await query.answer("🛑 Lo siento, yɑ hɑy unɑ rondɑ ejecutɑndose, esperɑ ɑ que se hɑgɑ unɑ nuevɑ", show_alert=True)
        return

    cancion_elegida = query.data.replace("mu_", "").lower().strip()
    cancion_correcta = sesion["correcta"]

    # --- CASO 1: ¡ACERTÓ! (Termina la ronda) ---
    if cancion_elegida == cancion_correcta:
        await query.answer(f"¡Acertɑste, {user_name}!")
        sesion["puntajes"][user.id] = sesion["puntajes"].get(user.id, 0) + 1

        # Guardar robux por ronda acertada
        premio_ronda = sesion_puntos.get("premio_actual", {}).get("adivina", 0)
        if premio_ronda > 0:
            sumar_robux(user.id, user_name, premio_ronda, f"Adivinɑ lɑ cɑncion rondɑ {sesion['ronda']}")

        texto_resultado = f"🎉 ¡Punto pɑrɑ {user_name}! \nLɑ cɑncion erɑ: {cancion_correcta.title()}"
        await query.edit_message_caption(caption=texto_resultado)

        if sesion["ronda"] < 5:
            sesion["ronda"] += 1
            tablero_corto = "\n".join([
                f"• {next((j['name'] for j in sesion['jugadores'] if j['id'] == uid), uid)}: `{pts}` pts"
                for uid, pts in sesion["puntajes"].items()
            ])
            msg_puntos = f"✨ 𝗧𝗮𝗯𝗹𝗲𝗿𝗼 𝗱𝗲 𝗽𝗼𝘀𝗶𝗰𝗶𝗼𝗻𝗲𝘀:\n\n{tablero_corto}\n\n"

            await context.bot.send_message(chat_id=chat_id, text=msg_puntos, parse_mode="Markdown")
            await enviar_siguiente_ronda(chat_id, context)
        else:
            sesion["activa"] = False
            tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
            medallas = ["🥇", "🥈", "🥉"]

            texto_final = "¡𝗙𝗜𝗡 𝗗𝗘𝗟 𝗝𝗨𝗘𝗚𝗢ⵑ 🏁\n\n🏆 𝗣𝘂𝗲𝘀𝘁𝗼𝘀:\n\n"
            for i, (uid_p, pts) in enumerate(tabla):
                jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_p), None)
                nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_p}"
                dec = medallas[i] if i < 3 else "🔹"
                texto_final += f"{dec} {nombre_p}: {pts} pt(s)s\n"
            await context.bot.send_message(chat_id=chat_id, text=texto_final, parse_mode="Markdown")

    # --- CASO 2: SE EQUIVOCÓ (La ronda NO se muere, los demás continúan) ---
    else:
        await query.answer(f"Esɑ no es lɑ respuestɑ, {user_name}...", show_alert=False)

        mencion = user.mention_markdown_v2() if user.username else f"`{user_name}`"
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Esɑ no es lɑ respuestɑ, {mencion}. ¡Sigue intentɑndo!",
        )
