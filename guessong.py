import random
import requests
import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ================= DICCIONARIOS Y CONFIG =================

lovers = ["BTS", "RM", "Agust D", "j-hope", "Jimin", "V", "Jung Kook", "Jin"]
partida_song = {}  # Guardará: { chat_id: {"ronda": 1, "puntos": {}, "correcta": "name"} }

# ================= EL MOTOR DE CANCIONES =================

def obtener_canciones():
    print("--- [DEBUG] Buscando canciones en la API de iTunes... ---")
    seleccionados = random.sample(lovers, 4)
    all_songs = []
    
    for artista in seleccionados:
        try:
            url = f"https://itunes.apple.com/search?term={artista}&entity=song&limit=15"
            response = requests.get(url).json()
            canciones_validas = [track for track in response.get('results', []) if track.get('previewUrl')]
            all_songs.extend(canciones_validas)
        except Exception as e:
            print(f"--- [DEBUG] Error al buscar artista {artista}: {e} ---")
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
    print("--- [DEBUG] Descargando y recortando fragmento de audio... ---")
    archivo_temporal = "temp_itunes.m4a"
    archivo_final = "reto_van.mp3"
    
    audio_data = requests.get(url_audio).content
    with open(archivo_temporal, "wb") as f:
        f.write(audio_data)
        
    audio = AudioSegment.from_file(archivo_temporal)
    recorte = audio[:4000] # 4 segundos hardcore
    recorte.export(archivo_final, format="mp3")
    
    if os.path.exists(archivo_temporal):
        os.remove(archivo_temporal)
    return archivo_final

# ================= ENVIAR NUEVA RONDA =================

async def enviar_siguiente_ronda(chat_id, context: ContextTypes.DEFAULT_TYPE):
    estado = partida_song[chat_id]
    print(f"--- [DEBUG] Iniciando ronda {estado['ronda']} ---")
    
    try:
        correcta, opciones = obtener_canciones()
        archivo_reto = descargar_y_recortar_audio(correcta['previewUrl'])
        
        estado["correcta"] = correcta['trackName'].lower().strip()
        
        botones = [[InlineKeyboardButton(cancion['trackName'], callback_data=f"mu_{cancion['trackName']}")] for cancion in opciones]
        reply_markup = InlineKeyboardMarkup(botones)
        
        with open(archivo_reto, 'rb') as audio:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio,
                caption=f"🎵 **RONDA {estado['ronda']}/5** ⏱️\n🔊 ¡Tienes solo 4 segundos! ¿Qué canción es?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        print(f"--- [DEBUG] Ronda {estado['ronda']} enviada con éxito ---")
            
        if os.path.exists(archivo_reto):
            os.remove(archivo_reto)
            
    except Exception as e:
        print(f"--- [DEBUG] ERROR CRÍTICO EN ENVIAR RONDA: {e} ---")
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al pasar a la siguiente ronda: {e}")
        partida_song.pop(chat_id, None)

# ================= INTERFAZ DE TELEGRAM =================

async def iniciar_adivina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"--- [DEBUG] Comando /adivina detectado en chat_id: {chat_id} ---")
    
    partida_song[chat_id] = {
        "ronda": 1,
        "puntos": {},  # Puntos individuales {"Nombre": score}
        "correcta": ""
    }
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="🎧 **¡Inicia el Maratón de Trivia de Van!** 🌸\nSerán **5 canciones entreveradas**. ¡El más rápido en presionar el botón se lleva el punto!",
        parse_mode="Markdown"
    )
    
    await enviar_siguiente_ronda(chat_id, context)

async def verificar_respuesta_musica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user_first_name = update.effective_user.first_name
    
    if chat_id not in partida_song:
        return
        
    estado = partida_song[chat_id]
    cancion_elegida = query.data.replace("mu_", "").lower().strip()
    cancion_correcta = estado["correcta"]
    
    if cancion_elegida == cancion_correcta:
        if user_first_name not in estado["puntos"]:
            estado["puntos"][user_first_name] = 0
        estado["puntos"][user_first_name] += 1
        texto_resultado = f"🎉 **¡PUNTO PARA {user_first_name.upper()}!** 🌸\nAcertó: `{cancion_correcta.title()}`"
    else:
        texto_resultado = f"💀 **¡Fallo! {user_first_name} se equivocó.** Van ganó esta ronda.\nLa canción era: `{cancion_correcta.title()}` 🤖"
        
    await query.edit_message_caption(caption=texto_resultado, parse_mode="Markdown")
    
    if estado["ronda"] < 5:
        estado["ronda"] += 1
        tablero_corto = "\n".join([f"• {jugador}: `{pts}` pts" for jugador, pts in estado["puntos"].items()])
        msg_puntos = f"✨ **Tabla de posiciones actual:**\n{tablero_corto if tablero_corto else '• Nadie ha sumado puntos aún.'}\n\n¡Siguiente canción! 👇"
        
        await context.bot.send_message(chat_id=chat_id, text=msg_puntos, parse_mode="Markdown")
        await enviar_siguiente_ronda(chat_id, context)
    else:
        texto_final = "🏁 **¡FIN DEL JUEGO!** 🏁\n\n🏆 **RESULTADOS FINALES:**\n"
        if estado["puntos"]:
            jugadores_ordenados = sorted(estado["puntos"].items(), key=lambda x: x[1], reverse=True)
            texto_final += f"🥇 **{jugadores_ordenados[0][0]}** con `{jugadores_ordenados[0][1]}` puntos ✨\n"
            for jugador, pts in jugadores_ordenados[1:]:
                texto_final += f"• {jugador}: `{pts}` puntos\n"
        else:
            texto_final += "💀 Increíble... nadie logró hacer ni un solo punto. Van barrió con todos. 🤖"
            
        texto_final += "\n¿Quieren revancha? Usen `/adivina` de nuevo. 😏🔥"
        await context.bot.send_message(chat_id=chat_id, text=texto_final, parse_mode="Markdown")
        partida_song.pop(chat_id, None)
