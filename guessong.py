import random
import requests
import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_SONG

# ================= DICCIONARIOS Y CONFIG =================

lovers = ["BTS", "RM", "Agust D", "j-hope", "Jimin", "V", "Jung Kook", "Jin"]

# Igual que en box.py: una sesión por chat_id, jugadores guardados como
# lista de dicts {id, name, username}. Así el bot reconoce a la persona
# por su id real de Telegram y no por su first_name (que puede repetirse
# o cambiar).
sesion_song = {}   # chat_id -> {"jugadores": [...], "activa": bool, ...}

def reset_guessong_chat(chat_id: int):
    """Apaga y limpia la partida de Adivina la Canción de un chat puntual (usado por /off_van)."""
    sesion_song.pop(chat_id, None)

# ================= MOTOR DE AUDIO (iTunes & Pydub) =================

def obtener_canciones(excluir_ids=None):
    excluir_ids = excluir_ids or set()
    all_songs = []

    # Se busca en TODOS los miembros (no solo 4 random) para tener pool
    # suficiente y que aguante las 10 rondas sin quedarse sin canciones.
    for artista in lovers:
        try:
            url = f"https://itunes.apple.com/search?term={artista}&entity=song&limit=25"
            response = requests.get(url).json()
            canciones_validas = [
                track for track in response.get('results', [])
                if track.get('previewUrl') and _es_artista_valido(track.get('artistName', ''))
            ]
            all_songs.extend(canciones_validas)
        except Exception:
            continue

    if len(all_songs) < 6:
        url = "https://itunes.apple.com/search?term=BTS&entity=song&limit=50"
        response = requests.get(url).json()
        extra = [
            track for track in response.get('results', [])
            if track.get('previewUrl') and _es_artista_valido(track.get('artistName', ''))
        ]
        all_songs.extend(extra)

    if not all_songs:
        # Último recurso: traer canciones de BTS sin filtrar para que el
        # juego no se rompa, aunque sea menos preciso.
        url = "https://itunes.apple.com/search?term=BTS&entity=song&limit=50"
        response = requests.get(url).json()
        all_songs = [track for track in response.get('results', []) if track.get('previewUrl')]

    # Quitar duplicados (mismo trackId puede salir varias veces al combinar búsquedas)
    vistos = set()
    unicos = []
    for c in all_songs:
        if c['trackId'] not in vistos:
            vistos.add(c['trackId'])
            unicos.append(c)
    all_songs = unicos

    # Evitar repetir canciones ya usadas en la partida actual, si hay opciones suficientes
    disponibles = [c for c in all_songs if c['trackId'] not in excluir_ids]
    if len(disponibles) >= 4:
        all_songs = disponibles

    random.shuffle(all_songs)
    correcta = random.choice(all_songs)

    falsas_filtradas = []
    for c in all_songs:
        if c['trackId'] != correcta['trackId'] and c['trackName'].lower() != correcta['trackName'].lower():
            if c['trackName'] not in [f['trackName'] for f in falsas_filtradas]:
                falsas_filtradas.append(c)

    if len(falsas_filtradas) < 3:
        falsas_filtradas = [c for c in all_songs if c['trackId'] != correcta['trackId']]

    # Guard final: si aun asi no alcanzan 3 opciones distintas, se rellena
    # con reemplazo para que el sample de abajo nunca truene.
    if len(falsas_filtradas) < 3:
        faltan = 3 - len(falsas_filtradas)
        relleno_pool = [c for c in all_songs if c['trackId'] != correcta['trackId']] or [correcta]
        falsas_filtradas += random.choices(relleno_pool, k=faltan)

    falsas = random.sample(falsas_filtradas, 3) if len(falsas_filtradas) >= 3 else falsas_filtradas
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
    if nombre in _ARTISTAS_VALIDOS:
        return True
    if "bts" in nombre or "방탄소년단" in nombre:
        return True
    # Coincidencia parcial para casos como "RM (Feat. ...)" o nombres con
    # paréntesis/colaboraciones, siempre que el nombre del miembro sea
    # razonablemente largo (evita falsos positivos con "v" suelto).
    for valido in _ARTISTAS_VALIDOS:
        if len(valido) > 2 and valido in nombre:
            return True
    return False


def descargar_y_recortar_audio(url_audio, chat_id):
    # Nombres de archivo únicos por chat para evitar que dos partidas
    # simultáneas se pisen entre sí.
    archivo_temporal = f"temp_itunes_{chat_id}.m4a"
    archivo_final = f"reto_van_{chat_id}.mp3"

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
        usadas = sesion.setdefault("usadas_ids", set())
        correcta, opciones = obtener_canciones(excluir_ids=usadas)
        usadas.add(correcta['trackId'])

        archivo_reto = descargar_y_recortar_audio(correcta['previewUrl'], chat_id)

        sesion["correcta"] = correcta['trackName'].lower().strip()
        # callback_data usa índice en vez del nombre completo de la canción,
        # porque Telegram limita callback_data a 64 bytes y algunos nombres
        # (feats, colaboraciones, etc.) se pasan de eso.
        sesion["opciones_nombres"] = {str(i): c['trackName'].lower().strip() for i, c in enumerate(opciones)}

        botones = [[InlineKeyboardButton(cancion['trackName'], callback_data=f"mu_{i}")] for i, cancion in enumerate(opciones)]
        reply_markup = InlineKeyboardMarkup(botones)

        with open(archivo_reto, 'rb') as audio:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio,
                caption=f"¡𝗥𝗢𝗡𝗗𝗔 {sesion['ronda']}/10ⵑ\n\n¿𝖫𝗈𝗀𝗋𝖺𝗌𝗍𝖾 𝗂𝖽𝖾𝗇𝗍𝗂𝖿𝗂𝖼𝖺𝗋 𝗊𝗎𝖾 𝖼𝖺𝗇𝖼𝗂𝗈𝗇 𝖾𝗌?",
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
        photo=GIF_SONG,
        caption="<b> ៹ ࣪  📦 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗅𝖺 𝖼𝖺𝗇𝖼𝗂𝗈𝗇!</b>\n\n𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗎𝗅𝗌𝖾 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗌𝖾 𝖺 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺  ֪   𓂃\n\n<blockquote>𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝗎𝗍𝗂𝗅𝗂𝖼𝖾𝗇 <code>/start_guess &lt;p1 p2 p3&gt;</code> 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def manejar_boton_unirse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Agrega jugadores por id (igual que box), evitando duplicados aunque cambien de nombre."""
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if chat_id not in sesion_song:
        await query.answer()
        return

    sesion = sesion_song[chat_id]

    if sesion["activa"]:
        await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
        return

    if any(j["id"] == user.id for j in sesion["jugadores"]):
        await query.answer()
        return

    sesion["jugadores"].append({"id": user.id, "name": nombre_usuario(user), "username": user.username})
    await query.answer()
    await query.message.reply_text(f"🎧  {nombre_usuario(user)} se unio 𓂃")

async def iniciar_adivina_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valida los requisitos minimos y arranca la primera ronda"""
    chat_id = update.effective_chat.id

    if chat_id not in sesion_song or len(sesion_song[chat_id]["jugadores"]) < 2:
        await update.message.reply_text("𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈.")
        await update.message.reply_sticker(sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ")
        return

    sesion = sesion_song[chat_id]

    args = context.args or []
    try:
        sesion_puntos["premio_actual"]["adivina_1"] = int(args[0]) if len(args) > 0 else 0
        sesion_puntos["premio_actual"]["adivina_2"] = int(args[1]) if len(args) > 1 else 0
        sesion_puntos["premio_actual"]["adivina_3"] = int(args[2]) if len(args) > 2 else 0
    except ValueError:
        pass

    sesion["activa"] = True
    sesion["ronda"] = 1
    sesion["puntajes"] = {j["id"]: 0 for j in sesion["jugadores"]}
    sesion["usadas_ids"] = set()

    await context.bot.send_message(
        chat_id=chat_id,
        text="Ꜥ ¡𝖤𝗅 𝗃𝗎𝖾𝗀𝗈 𝗁𝖺 𝖼𝗈𝗆𝖾𝗇𝗓𝖺𝖽𝗈! 𝖲𝖾 𝖾𝗌𝗍𝖺𝗇 𝖾𝗑𝗍𝗋𝖺𝗒𝖾𝗇𝖽𝗈 𝗅𝗈𝗌 𝖼𝗅𝗂𝗉𝗌, 𝖾𝗌𝗍𝖾𝗇 𝖺𝗍𝖾𝗇𝗍𝗈𝗌 ⸝⸝",
    )
    await context.bot.send_sticker(
        chat_id=chat_id,
        sticker="CAACAgEAAxkBA03buWpMPa84qd5D0emGjcvqtROUTAnVAAJCBgACs9RARFFhqS0WdEdWPAQ")

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
        await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
        return

    idx = query.data.replace("mu_", "")
    cancion_elegida = sesion.get("opciones_nombres", {}).get(idx, "")
    cancion_correcta = sesion["correcta"]

    # --- CASO 1: ¡ACERTÓ! (Termina la ronda) ---
    if cancion_elegida == cancion_correcta:
        await query.answer(f"¡𝖲𝗂, 𝖺𝖼𝖾𝗋𝗍𝖺𝗌𝗍𝖾, {user_name}!")
        sesion["puntajes"][user.id] = sesion["puntajes"].get(user.id, 0) + 1

        texto_resultado = f"🎉 ¡𝖯𝗎𝗇𝗍𝗈 𝗉𝖺𝗋𝖺 {user_name}!\n\n𝖫𝖺 𝖼𝖺𝗇𝖼𝗂𝗈𝗇 𝖾𝗋𝖺: {cancion_correcta.title()}"
        await query.edit_message_caption(caption=texto_resultado)

        if sesion["ronda"] < 10:
            sesion["ronda"] += 1
            await enviar_siguiente_ronda(chat_id, context)
        else:
            sesion["activa"] = False
            tabla = sorted(sesion["puntajes"].items(), key=lambda x: x[1], reverse=True)
            medallas = ["🥇", "🥈", "🥉"]
            premios_adivina = [
                sesion_puntos.get("premio_actual", {}).get("adivina_1", 0),
                sesion_puntos.get("premio_actual", {}).get("adivina_2", 0),
                sesion_puntos.get("premio_actual", {}).get("adivina_3", 0),
            ]

            texto_final = "¡𝖲𝖾 𝗂𝖽𝖾𝗇𝗍𝗂𝖿𝗂𝖼𝖺𝗋𝗈𝗇 𝗍𝗈𝖽𝖺𝗌 𝗅𝖺𝗌 𝖼𝖺𝗇𝖼𝗂𝗈𝗇𝖾𝗌!\n\n𝗣𝗨𝗡𝗧𝗨𝗔𝗖𝗜𝗢𝗡 𝗙𝗜𝗡𝗔𝗟:\n\n"
            for i, (uid_p, pts) in enumerate(tabla):
                jugador_obj = next((j for j in sesion["jugadores"] if j["id"] == uid_p), None)
                nombre_p = jugador_obj["name"] if jugador_obj else f"ID {uid_p}"
                dec = medallas[i] if i < 3 else "🔹"
                robux_p = premios_adivina[i] if i < 3 else 0
                extra = f" —› {robux_p} fichɑs" if robux_p else ""
                texto_final += f"{dec} {nombre_p}: {pts} 𝗉𝗍(𝗌){extra}\n"
                if robux_p and jugador_obj:
                    sumar_robux(jugador_obj["id"], jugador_obj["name"], robux_p, f"𝗣𝘂𝗲𝘀𝘁𝗼: {i+1} 🎧")
            await context.bot.send_message(chat_id=chat_id, text=texto_final)
            await context.bot.send_sticker(
                chat_id=chat_id,
                sticker="CAACAgIAAxkBA0Y_BGpDJx8fjT0XysClgbwsbIDR6Y8kAAI2bAEAAWOLRgw-W-3HHw-_YjwE"
            )

    # --- CASO 2: SE EQUIVOCÓ (La ronda NO se muere, los demás continúan) ---
    else:
        await query.answer()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"¡𝖤𝗌𝖺 𝗇𝗈 𝖾𝗌 𝗅𝖺 𝗋𝖾𝗌𝗉𝗎𝖾𝗌𝗍𝖺, {user_name}!. ¡𝖳𝗎 𝗉𝗎𝖾𝖽𝖾𝗌, 𝗌𝗂𝗀𝗎𝖾 𝗂𝗇𝗍𝖾𝗇𝗍𝖺𝗇𝖽𝗈!",
        )
