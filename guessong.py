import random
import requests
import os
from pydub import AudioSegment
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ================= DICCIONARIOS Y CONFIG =================

lovers = ["BTS", "RM", "Agust D", "j-hope", "Jimin", "V", "Jung Kook", "Jin"]

sesion_song = {
    "jugadores": {},       # Estructura: { "Nombre": puntos }
    "lista_nombres": [],   # Para verificar quiénes entraron a la sala
    "ronda": 1,
    "correcta": "",
    "fase_registro": False,
    "activa": False,
    "creador_id": None
}

# Recursos visuales (Puedes cambiarlos por tus variables globales si prefieres)
# Reemplaza estas dos líneas en tu guessong.py:
GIF_ADIVINA = "https://i.pinimg.com/originals/77/82/32/7782329e46a7888718991448b2660d5b.gif" 
GIF_ERROR = "https://i.pinimg.com/originals/f3/d8/51/f3d851e36f06a72477382d6032dae6df.jpg"

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
    try:
        correcta, opciones = obtener_canciones()
        archivo_reto = descargar_y_recortar_audio(correcta['previewUrl'])
        
        sesion_song["correcta"] = correcta['trackName'].lower().strip()
        
        botones = [[InlineKeyboardButton(cancion['trackName'], callback_data=f"mu_{cancion['trackName']}")] for cancion in opciones]
        reply_markup = InlineKeyboardMarkup(botones)
        
        with open(archivo_reto, 'rb') as audio:
            await context.bot.send_voice(
                chat_id=chat_id,
                voice=audio,
                caption=f"🎵 **𝖱𝖮𝖭𝖣𝖤 {sesion_song['ronda']}/5** ⏱️\n🪞 𝖳𝖨𝖤𝖭𝖤𝖲 𝖲𝖮𝖫𝖮 𝟦 𝖲𝖤𝖦𝖴𝖭𝖣𝖮𝖲... ¿𝖰𝗎𝖾́ 𝖼𝖺𝗇𝖼𝗂𝗈́𝗇 𝖾𝗌?",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        if os.path.exists(archivo_reto):
            os.remove(archivo_reto)
            
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al pasar a la siguiente ronda: {e}")
        sesion_song["activa"] = False

# ================= CONTROL DE LA SALA (CALLBACKS Y COMANDOS) =================

async def unirse_adivina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abre la sala de reclutamiento con el botón interactivo"""
    sesion_song["jugadores"] = {}
    sesion_song["lista_nombres"] = []
    sesion_song["ronda"] = 1
    sesion_song["activa"] = False
    sesion_song["fase_registro"] = True
    sesion_song["creador_id"] = update.effective_user.id

    boton = InlineKeyboardButton("੭੭  𝐔𝐍𝐈𝐑𝐌𝐄  !¡", callback_data="unirme_adivina_click")
    
    await update.message.reply_photo(
        photo=GIF_ADIVINA,
        caption="៹ ࣪  🎧 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗅𝖺 𝖢𝖺𝗇𝖼𝗂𝗈́𝗇! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝑟𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪  𓂃\n\n"
                "¡𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾́𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝖾𝗅 𝖼𝗋𝖾𝖺𝖽𝗈𝗋 𝗎𝗌𝖾 `/start_adivina`! 🔥",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def manejar_boton_unirse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Agrega a los usuarios que clickean en 'UNIRME'"""
    query = update.callback_query
    await query.answer()
    
    user_name = update.effective_user.first_name

    if not sesion_song["fase_registro"]:
        return

    if user_name in sesion_song["lista_nombres"]:
        return

    sesion_song["lista_nombres"].append(user_name)
    sesion_song["jugadores"][user_name] = 0

    lista_j = "\n".join([f"  {i+1}. {j}" for i, j in enumerate(sesion_song["lista_nombres"])])
    
    await query.message.edit_caption(
        caption=f"៹ ࣪  🎧 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗅𝖺 𝖢𝖺𝗇𝖼ioi𝗇! 𝖯𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪  𓂃\n\n"
                f"👥 **𝖩𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌 𝖾𝗇 𝗅𝖺 𝗌𝖺𝗅𝖺:**\n{lista_j}\n\n"
                f"¡𝖢𝗎𝖺𝗇𝖽𝗈 𝖾𝗌𝗍𝖾́𝗇 𝗅𝗂𝗌𝗍𝗈𝗌, 𝖾𝗅 𝖼𝗋𝖾𝖺𝖽𝗈𝗋 𝗎𝗌𝖾 `/start_adivina`! 🔥",
        reply_markup=query.message.reply_markup,
        parse_mode="Markdown"
    )

async def iniciar_adivina_juego(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Valida los requisitos mínimos y arranca la primera ronda"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not sesion_song["fase_registro"]:
        return

    # Validación idéntica a tu juego de Casería
    if len(sesion_song["lista_nombres"]) < 2:
        await update.message.reply_photo(
            photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋."
        )
        return

    if user_id != sesion_song["creador_id"]:
        await update.message.reply_text("🛑 ¡𝖲𝖺𝖼𝖺 𝗅𝖺 𝗆𝖺𝗇𝗈 𝖽𝖾 𝖺𝗁𝗂́! 𝖲𝗈𝗅𝗈 𝖾𝗅 𝖼𝗋𝖾𝖺𝖽𝗈𝗋 𝖽𝖾 𝗅𝖺 𝗌𝖺𝗅𝖺 𝗉𝗎𝖾𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈.")
        return

    sesion_song["fase_registro"] = False
    sesion_song["activa"] = True
    
    await context.bot.send_message(
        chat_id=chat_id, 
        text="🎧 **¡𝖤𝗅 𝗃𝗎𝖾𝗀𝗈 𝗁𝖺 𝖼𝗈𝗆𝖾𝗇𝗓𝖺𝖽𝗈!** 🌸\n𝖵𝖺𝗇 𝖾𝗌𝗍𝖺́ 𝗉𝗋𝖾𝗉𝖺𝗋𝖺𝗇𝖽𝗈 𝗅𝗈𝗌 𝖼𝗅𝗂𝗉𝗌 𝗁𝖺𝗋𝖽𝖼𝗈𝗋... ¡𝖯𝗋𝖾𝗉𝖺𝗋𝖾𝗇 𝗌𝗎𝗌 𝗈𝗂́𝖽𝗈𝗌!",
        parse_mode="Markdown"
    )
    
    await enviar_siguiente_ronda(chat_id, context)

async def verificar_respuesta_musica(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el botón de canción presionado por los jugadores inscritos"""
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    user_first_name = update.effective_user.first_name
    
    if not sesion_song["activa"]:
        return
        
    if user_first_name not in sesion_song["lista_nombres"]:
        return

    cancion_elegida = query.data.replace("mu_", "").lower().strip()
    cancion_correcta = sesion_song["correcta"]
    
    if cancion_elegida == cancion_correcta:
        sesion_song["jugadores"][user_first_name] += 1
        texto_resultado = f"🎉 **𝖯𝖴𝖭𝖳𝖮 𝖯𝖠𝖱𝖠 {user_first_name.upper()}!** 🌸\n𝖠𝖼𝖾𝗋𝗍𝗈́: `{cancion_correcta.title()}`"
    else:
        texto_resultado = f"💀 **𝖥𝖺𝗅𝗅𝗈! {user_first_name} 𝗌𝖾 𝖾𝗊𝗎𝗂𝗏𝗈𝖼𝗈́.** 𝖵𝖺𝗇 𝗀𝖺𝗇𝗈́ 𝖾𝗌𝗍𝖺 𝗋𝗈𝗇𝖽𝖺.\n𝖫𝖺 𝖼𝖺𝗇𝖼𝗂𝗈́𝗇 𝖾𝗋𝖺: `{cancion_correcta.title()}` 🤖"
        
    await query.edit_message_caption(caption=texto_resultado, parse_mode="Markdown")
    
    if sesion_song["ronda"] < 5:
        sesion_song["ronda"] += 1
        tablero_corto = "\n".join([f"• {jugador}: `{pts}` 𝗉𝗍𝗌" for jugador, pts in sesion_song["jugadores"].items()])
        msg_puntos = f"✨ **𝖳𝖺𝖻𝗅𝖾𝗋𝗈 𝖽𝖾 实用𝗈𝗌𝗂𝖼𝗂𝗈𝗇𝖾𝗌:**\n{tablero_corto}\n\n¡𝖲𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾 𝖼𝖺𝗇𝖼𝗂𝗈́𝗇! 👇"
        
        await context.bot.send_message(chat_id=chat_id, text=msg_puntos, parse_mode="Markdown")
        await enviar_siguiente_ronda(chat_id, context)
    else:
        texto_final = "🏁 **¡𝖥𝖨𝖭 𝖣𝖤𝖫 𝖩𝖴𝖤𝖦𝖮!** 🏁\n\n🏆 **𝖱𝖤𝖲𝖴𝖫𝖳index𝖠𝖣𝖮𝖲 𝖥𝖨𝖭𝖤𝖫𝖤𝖲:**\n"
        jugadores_ordenados = sorted(sesion_song["jugadores"].items(), key=lambda x: x[1], reverse=True)
        
        texto_final += f"🥇 **{jugadores_ordenados[0][0]}** 𝖼𝗈𝗇 `{jugadores_ordenados[0][1]}` 𝗉𝗎𝗇𝗍𝗈𝗌 ✨\n"
        for jugador, pts in jugadores_ordenados[1:]:
            texto_final += f"• {jugador}: `{pts}` 𝗉𝗎𝗇𝗍𝗈𝗌\n"
            
        texto_final += "\n¿𝖰𝗎𝗂𝖾𝗋𝖾𝗇 𝗋𝖾𝗏𝖺𝗇𝖼𝗁𝖺? 𝖠𝖻𝗋𝖺𝗇 𝗈𝗍𝗋𝖺 𝗌𝖺𝗅𝖺 𝗎𝗌𝖺𝗇𝖽𝗈 `/adivina` 👑🔥"
        await context.bot.send_message(chat_id=chat_id, text=texto_final, parse_mode="Markdown")
        sesion_song["activa"] = False
