# ================= LIBRERIAS =================

import random
import requests
import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ================= DICCIONARIOS Y CONFIG =================

lovers = ["BTS", "RM", "Agust D", "j-hope", "Jimin", "V", "Jung Kook", "Jin"]

partida_song = {}

# ================= EL MOTOR DE CANCIONES =================

def obtener_canciones():
    "Atencion, estamos seleccionando las canciones"
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
    recorte = audio[:4000] # 4 segundos hardcore
    recorte.export(archivo_final, format="mp3")
    
    if os.path.exists(archivo_temporal):
        os.remove(archivo_temporal)
    return archivo_final

# ================= ENVIAR NUEVA RONDA =================

async def enviar_siguiente_ronda(chat_id, context: ContextTypes.DEFAULT_TYPE):
    """Función interna para mandar la siguiente ronda sin repetir código"""
    estado = partida_song[chat_id]
    
    try:
        correcta, opciones = obtener_canciones()
        archivo_reto = descargar_y_recortar_audio(correcta['previewUrl'])
        
        # Actualizamos la canción correcta en el estado
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
            
        if os.path.exists(archivo_reto):
            os.remove(archivo_reto)
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al pasar a la siguiente ronda: {e}")
        partida_song.pop(chat_id, None)

# ================= INTERFAZ DE TELEGRAM =================

async def iniciar_adivina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el juego configurando las 7 rondas"""
    chat_id = update.effective_chat.id
    
    # Inicializamos el estado con los puntos como un diccionario vacío
    partida_song[chat_id] = {
        "ronda": 1,
        "puntos": {},  # Aquí guardaremos los puntos individuales: {"Nombre": score}
        "correcta": ""
    }
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="🎧 **¡Inicia el Maratón de Trivia de Van!** 🌸\nSerán **7 canciones entreveradas**. ¡El más rápido en presionar el botón se lleva el punto!",
        parse_mode="Markdown"
    )
    
    await enviar_siguiente_ronda(chat_id, context)

async def verificar_respuesta_musica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los puntos individuales y avanza las rondas"""
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user_first_name = update.effective_user.first_name  # Quién presionó el botón
    
    if chat_id not in partida_song:
        return
        
    estado = partida_song[chat_id]
    cancion_elegida = query.data.replace("mu_", "").lower().strip()
    cancion_correcta = estado["correcta"]
    
    # Comprobamos si acertó
    if cancion_elegida == cancion_correcta:
        # Si el usuario no estaba en la tabla, lo agregamos con 0 puntos
        if user_first_name not in estado["puntos"]:
            estado["puntos"][user_first_name] = 0
        
        # Le sumamos su punto individual
        estado["puntos"][user_first_name] += 1
        texto_resultado = f"🎉 **¡PUNTO PARA {user_first_name.upper()}!** 🌸\nAcertó: `{cancion_correcta.title()}`"
    else:
        texto_resultado = f"💀 **¡Fallo! {user_first_name} se equivocó.** Van ganó esta ronda.\nLa canción era: `{cancion_correcta.title()}` 🤖"
        
    # Editamos el mensaje quitando los botones para congelar la ronda
    await query.edit_message_caption(caption=texto_resultado, parse_mode="Markdown")
    
    # Control de rondas
    if estado["ronda"] < 7:
        estado["ronda"] += 1
        
        # Armamos un mini tablero rápido para mostrar cómo van en esta ronda
        tablero_corto = "\n".join([f"• {jugador}: `{pts}` pts" for jugador, pts in estado["puntos"].items()])
        msg_puntos = f"✨ **Tabla de posiciones actual:**\n{tablero_corto if tablero_corto else '• Nadie ha sumado puntos aún.'}\n\n¡Siguiente canción! 👇"
        
        await context.bot.send_message(chat_id=chat_id, text=msg_puntos, parse_mode="Markdown")
        await enviar_siguiente_ronda(chat_id, context)
    else:
        # --- FIN DEL JUEGO: ARMA EL PODIO FINAL ---
        texto_final = "🏁 **¡FIN DEL JUEGO!** 🏁\n\n🏆 **RESULTADOS FINALES:**\n"
        
        if estado["puntos"]:
            # Ordenamos a los jugadores de mayor a menor puntaje
            jugadores_ordenados = sorted(estado["puntos"].items(), key=lambda x: x[1], reverse=True)
            
            # El top 1 se lleva la corona
            texto_final += f"🥇 **{jugadores_ordenados[0][0]}** con `{jugadores_ordenados[0][1]}` puntos ✨\n"
            
            # Los demás puestos si existen
            for jugador, pts in jugadores_ordenados[1:]:
                texto_final += f"• {jugador}: `{pts}` puntos\n"
        else:
            texto_final += "💀 Increíble... nadie logró hacer ni un solo punto. Van barrió con todos. 🤖"
            
        texto_final += "\n¿Quieren revancha? Usen `/adivina` de nuevo. 😏🔥"
        
        await context.bot.send_message(chat_id=chat_id, text=texto_final, parse_mode="Markdown")
        partida_song.pop(chat_id, None)  # Limpiamos memoria
