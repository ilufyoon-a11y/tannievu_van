import random
from telegram.ext import filters
import os
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# !!⠀⠀FLASK - PERMITE QUE RENDER HAGA FUNCIONAR EL BOT⠀ ───⠀ ⠀♥︎

app_web = Flask('')

@app_web.route('/')
def home():
    return "Van fue encendido"

# !!⠀⠀VARIABLES DE IMAGENES⠀ ───⠀ ⠀♥︎

PREFIX = filters.Regex(r'^[./]')

GIF_BIENVENIDA = "https://i.postimg.cc/T1jPgpDX/upscalemedia-transformed-(3).jpg" 
GIF_INFO       = "https://i.postimg.cc/9XgrQHCd/upscalemedia-transformed-(1).jpg" 
GIF_AHORCADO   = "https://i.postimg.cc/6qg3jBTv/1000004761.jpg"   # usado por cipher
GIF_SNOWBALL   = "https://i.postimg.cc/ryb94Wgj/1000004755.jpg" 
GIF_RATONES    = "https://i.postimg.cc/wMmHBLTM/1000004766.jpg" 
GIF_RITMOAGO   = "https://i.postimg.cc/CMXk6g3n/upscalemedia-transformed.jpg" 
GIF_ERROR      = "https://i.postimg.cc/KYS83kdr/89f242fc-1b4e-4f36-963b-6d0df8a8ba0a.jpg"

# !!⠀⠀SISTEMAS DE SESIONES GENERALES DE LOS JUEGOS⠀ ───⠀ ⠀♥︎

sesion_snowball = {"activa": False, "jugadores": {}, "ronda": 0, "turno_de": None, "orden": [], "eliminados": []}
sesion_ratones  = {"activa": False, "jugadores": {}, "quesos": 0, "trampas": 0, "tablero": []}
sesion_ritmo    = {"activa": False, "jugadores": [], "categoria": "", "historial": [], "turno_index": 0}
sesion_cipher   = {"activa": False, "codigo": "", "moderador": None, "intentos": 0}
esperando_code  = {} 

sesion_zombie   = {"activa": False, "jugadores": {}, "balas": 0, "zombies": 0, "sobrevivientes": 0}
sesion_caseria  = {"activa": False, "jugadores": {}, "tablero": [], "objetivo_actual": "", "respondio_turno": False}
sesion_box      = {"activa": False, "jugadores": {}, "retador": None, "retado": None, "turno_de": None, "hp": {}}
sesion_charada  = {"activa": False, "moderador": None, "palabra": "", "puntos": {}}
sesion_pirata   = {"activa": False, "jugadores": {}, "tesoro_x": 0, "tesoro_y": 0, "mapa_size": 5}

# !!⠀⠀LÓGICA DEL JUEGO: CIPHER⠀ ───⠀ ⠀♥︎

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

# !!⠀⠀LÓGICA DEL JUEGO: RITMO A GO GO⠀ ───⠀ ⠀♥︎

CATEGORIAS_RITMO = [
    "Frutas", "Países", "Marcas de autos", "Colores", "Animales", 
    "Nombres de varón", "Nombres de mujer", "Películas de terror", "Comidas típicas"
]

# !!⠀⠀LÓGICA DEL JUEGO: CASERÍA⠀ ───⠀ ⠀♥︎

EMOJIS_CASERIA = ["🦁", "🐯", "🐼", "🐨", "🦊", "🐰", "🐵", "🐸", "🐷", "🐧", "🐦", "🐥", "👑", "💎", "🔮", "🍀"]

# !!⠀⠀COMANDOS: CONFIGURACIONES GENERALES⠀ ───⠀ ⠀♥︎

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_BIENVENIDA,
        caption="✨ ¡𝖧𝗈𝗅𝖺! 𝖲𝗈𝗒 𝖵𝖺𝗇, 𝗍𝗎 𝖻𝗈𝗍 𝖽𝖾 𝖾𝗇𝗍𝗋𝖾𝗍𝖾𝗇𝗂𝗆𝗂𝖾𝗇𝗍𝗈 𝗒 𝗃𝗎𝖾𝗀𝗈𝗌.\n\n"
                "Usa `/help` o `/info` para ver la lista de juegos disponibles y comandos de entretenimiento."
    )

async def info_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_INFO,
        caption="📖 **𝖫𝖨𝖲𝖳𝖠 𝖣𝖤 𝖩𝖴𝖤𝖦𝖮𝖲 𝖣𝖨𝖲𝖯𝖮𝖭𝖨𝖡𝖫𝖤𝖲**\n\n"
                "❄️ **/snowball** - Guerra de nieve (Min. 2 jugadores)\n"
                "🧀 **/ratones** - Busca el queso y evita trampas\n"
                "🕺 **/ritmo** - El clásico juego de 'Ritmo a gogo'\n"
                "🕵️‍♂️ **/cipher** - Descifra el código numérico oculto\n"
                "🧟 **/zombie** - Sobrevive al apocalipsis zombie\n"
                "🎯 **/caseria** - Encuentra el emoji rápido en el tablero\n"
                "🥊 **/box** - Reta a un amigo a un duelo de boxeo\n"
                "🎭 **/charada** - Adivina la palabra oculta con pistas\n"
                "🏴‍☠️ **/pirata** - Busca el tesoro en un mapa de coordenadas\n\n"
                "💡 _Para iniciar cualquier juego usa `/start_[nombre]` luego de unirse._"
    )

# !!⠀⠀COMANDOS: REGISTROS DE UNIONES A JUEGOS⠀ ───⠀ ⠀♥︎

async def unirse_snowball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_snowball["activa"]:
        await update.message.reply_text("⚠️ Ya hay una partida en curso.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_snowball["jugadores"][uid] = {"name": uname, "nieve": 2, "hp": 3}
    await update.message.reply_text(f"❄️ {uname} se ha unido a la guerra de nieve.")

async def unirse_ratones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_ratones["activa"]:
        await update.message.reply_text("⚠️ Ya hay una partida en curso.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_ratones["jugadores"][uid] = {"name": uname, "puntos": 0, "vivo": True}
    await update.message.reply_text(f"🧀 {uname} se unió a la madriguera de ratones.")

async def unirse_ritmo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_ritmo["activa"]:
        await update.message.reply_text("⚠️ Ya hay una partida en curso.")
        return
    uname = update.effective_user.first_name
    if uname not in sesion_ritmo["jugadores"]:
        sesion_ritmo["jugadores"].append(uname)
    await update.message.reply_text(f"🕺 {uname} se unió a la pista de ritmo.")

async def unirse_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_cipher["activa"]:
        await update.message.reply_text("⚠️ El juego Cipher ya está en curso.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_cipher["moderador"] = uid
    esperando_code[uid] = update.effective_chat.id
    await update.message.reply_text(f"🕵️‍♂️ {uname} será el moderador. Te he enviado un mensaje privado para que elijas el código secreto.")
    try:
        await context.bot.send_message(chat_id=uid, text="Por favor, responde a este mensaje enviando el código numérico para el juego Cipher.")
    except Exception:
        await update.message.reply_text("❌ No pude enviarte un mensaje privado. Asegúrate de haber iniciado el bot en privado primero.")

async def unirse_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_zombie["activa"]:
        await update.message.reply_text("⚠️ Ya hay un apocalipsis en curso.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_zombie["jugadores"][uid] = {"name": uname, "rol": "Humano", "balas": 3, "vivo": True}
    await update.message.reply_text(f"🧟 {uname} se unió al refugio de sobrevivientes.")

async def unirse_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_caseria["activa"]:
        await update.message.reply_text("⚠️ Ya hay una cacería activa.")
        return
    uid = update.effective_user.id
    sesion_caseria["jugadores"][uid] = 0
    await update.message.reply_text(f"🎯 Jugador registrado para la cacería.")

async def unirse_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_box["activa"]:
        await update.message.reply_text("⚠️ Ya hay una pelea en curso en el ring.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    if not sesion_box["retador"]:
        sesion_box["retador"] = uid
        sesion_box["jugadores"][uid] = uname
        await update.message.reply_text(f"🥊 {uname} ha subido al ring esperando un oponente. ¡Usa `/box` para enfrentarlo!")
    elif uid != sesion_box["retador"] and not sesion_box["retado"]:
        sesion_box["retado"] = uid
        sesion_box["jugadores"][uid] = uname
        await update.message.reply_text(f"🥊 {uname} aceptó el reto. ¡La pelea está lista! Usa `/start_box` para iniciar.")

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_charada["activa"]:
        await update.message.reply_text("⚠️ Ya hay una charada activa.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_charada["moderador"] = uid
    await update.message.reply_text(f"🎭 {uname} es el moderador de la charada. Usa `/start_charada [palabra]` para definir la palabra secreta.")

async def unirse_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_pirata["activa"]:
        await update.message.reply_text("⚠️ Ya hay una búsqueda del tesoro activa.")
        return
    uid = update.effective_user.id
    uname = update.effective_user.first_name
    sesion_pirata["jugadores"][uid] = {"name": uname, "intentos": 0}
    await update.message.reply_text(f"🏴‍☠️ {uname} se unió a la tripulación pirata.")

# !!⠀⠀COMANDOS: INICIOS ACTIVOS DE LOS JUEGOS⠀ ───⠀ ⠀♥︎

async def iniciar_snowball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_snowball["activa"]: return
    if len(sesion_snowball["jugadores"]) < 2:
        await update.message.reply_text("⚠️ Se necesitan mínimo 2 jugadores.")
        return
    sesion_snowball["activa"] = True
    sesion_snowball["orden"] = list(sesion_snowball["jugadores"].keys())
    random.shuffle(sesion_snowball["orden"])
    sesion_snowball["turno_de"] = sesion_snowball["orden"][0]
    
    await enviar_tablero_snowball(update.effective_chat.id, context)

async def iniciar_ratones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_ratones["activa"]: return
    if not sesion_ratones["jugadores"]:
        await update.message.reply_text("⚠️ No hay jugadores unidos.")
        return
    sesion_ratones["activa"] = True
    pool = ["🧀"] * 8 + ["🪤"] * 4 + ["⬜"] * 13
    random.shuffle(pool)
    sesion_ratones["tablero"] = pool
    await enviar_tablero_ratones(update.effective_chat.id, context)

async def iniciar_ritmo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_ritmo["activa"]: return
    if len(sesion_ritmo["jugadores"]) < 2:
        await update.message.reply_text("⚠️ Se necesitan mínimo 2 jugadores.")
        return
    sesion_ritmo["activa"] = True
    sesion_ritmo["categoria"] = random.choice(CATEGORIAS_RITMO)
    sesion_ritmo["historial"] = []
    sesion_ritmo["turno_index"] = 0
    random.shuffle(sesion_ritmo["jugadores"])
    
    primero = sesion_ritmo["jugadores"][0]
    await update.message.reply_photo(
        photo=GIF_RITMOAGO,
        caption=f"🕺 **¡RITMO A GO GO!** 🕺\n\n"
                f"La categoría elegida es: **{sesion_ritmo['categoria']}**\n"
                f"Empieza el juego. Turno de: **{primero}**\n\n"
                f"💡 _Escribe tu respuesta directamente en el chat._"
    )

async def iniciar_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕵️‍♂️ El juego requiere que el moderador envíe el código en privado primero.")

async def iniciar_zombie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_zombie["activa"]: return
    if not sesion_zombie["jugadores"]:
        await update.message.reply_text("⚠️ No hay sobrevivientes en el refugio.")
        return
    sesion_zombie["activa"] = True
    uids = list(sesion_zombie["jugadores"].keys())
    zombie_inicial = random.choice(uids)
    sesion_zombie["jugadores"][zombie_inicial]["rol"] = "Zombie"
    
    await update.message.reply_text(
        "🧟 **¡EL APOCALIPSIS HA COMENZADO!** 🧟\n\n"
        f"☣️ El virus mutó y un jugador comenzó infectado: {sesion_zombie['jugadores'][zombie_inicial]['name']} es un **Zombie**.\n"
        "Los demás son **Humanos** con 3 balas en sus armas.\n\n"
        "Acciones válidas en el chat:\n"
        "🔫 Si eres Humano: Escribe `disparar` para defenderte.\n"
        "🥩 Si eres Zombie: Escribe `morder` para infectar a un humano."
    )

async def iniciar_caseria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_caseria["activa"]: return
    if not sesion_caseria["jugadores"]:
        await update.message.reply_text("⚠️ No hay jugadores registrados.")
        return
    sesion_caseria["activa"] = True
    pool = random.sample(EMOJIS_CASERIA, len(EMOJIS_CASERIA))
    sesion_caseria["tablero"] = pool
    sesion_caseria["jugadores"] = {uid: 0 for uid in sesion_caseria["jugadores"]}
    
    grid_txt = ""
    for idx, emo in enumerate(pool):
        grid_txt += emo + ("\n" if (idx + 1) % 4 == 0 else " ")
    
    await update.message.reply_text(f"🎯 **¡CASERÍA INICIADA!** 🎯\n\nEste es el tablero de juego:\n\n{grid_txt}\n\n¡Atentos al canal, enviaré los objetivos uno a uno!")
    asyncio.create_task(ronda_caseria(update.effective_chat.id, context))

async def iniciar_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_box["activa"]: return
    if not sesion_box["retado"]:
        await update.message.reply_text("⚠️ Falta un oponente en el ring.")
        return
    sesion_box["activa"] = True
    retador = sesion_box["retador"]
    retado = sesion_box["retado"]
    sesion_box["hp"] = {retador: 100, retado: 100}
    sesion_box["turno_de"] = retador
    
    await enviar_menu_box(update.effective_chat.id, context)

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_charada["activa"]: return
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Uso correcto: `/start_charada [palabra_secreta]`")
        return
    if update.effective_user.id != sesion_charada["moderador"]:
        await update.message.reply_text("⚠️ Solo el moderador registrado puede definir la palabra.")
        return
    sesion_charada["palabra"] = args[0].lower()
    sesion_charada["activa"] = True
    await update.message.reply_text("🎭 **¡CHARADA EN CURSO!** 🎭\n\nEl moderador ya definió la palabra secreta. Los demás jugadores intenten adivinar escribiendo sus opciones en el chat.")

async def iniciar_pirata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_pirata["activa"]: return
    if not sesion_pirata["jugadores"]:
        await update.message.reply_text("⚠️ No hay piratas en la tripulación.")
        return
    sesion_pirata["activa"] = True
    size = sesion_pirata["mapa_size"]
    sesion_pirata["tesoro_x"] = random.randint(1, size)
    sesion_pirata["tesoro_y"] = random.randint(1, size)
    
    await update.message.reply_text(
        f"🏴‍☠️ **¡BÚSQUEDA DEL TESORO!** 🏴‍☠️\n\n"
        f"El mapa es una cuadrícula de {size}x{size}.\n"
        f"Para buscar el cofre del tesoro, envía tus coordenadas en el formato: `X,Y` (Ejemplo: `3,2`).\n\n"
        "¡Que comience la excavación!"
    )

# !!⠀⠀FUNCIONES VISUALES: RENDERIZACIÓN DE TABLEROS EN BOTONES⠀ ───⠀ ⠀♥︎

async def enviar_tablero_snowball(chat_id, context):
    orden = sesion_snowball["orden"]
    turno = sesion_snowball["turno_de"]
    name_turno = sesion_snowball["jugadores"][turno]["name"]
    
    texto = "❄️ **GUERRA DE NIEVE** ❄️\n\n"
    botones = []
    for uid in orden:
        p = sesion_snowball["jugadores"][uid]
        estado = "💀 ELIMINADO" if uid in sesion_snowball["eliminados"] else f"❤️ {p['hp']} HP | ⚪ {p['nieve']} Nieve"
        texto += f"👤 {p['name']}: {estado}\n"
        if uid != turno and uid not in sesion_snowball["eliminados"] and turno not in sesion_snowball["eliminados"]:
            botones.append([InlineKeyboardButton(text=f"Lanzar a {p['name']}", callback_query_data=f"sb_atacar_{uid}")])
            
    if turno not in sesion_snowball["eliminados"]:
        botones.append([InlineKeyboardButton(text="Recargar Nieve ⚪", callback_query_data="sb_recargar")])
        texto += f"\n👉 Turno actual de: **{name_turno}**"
    
    await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=InlineKeyboardMarkup(botones))

async def enviar_tablero_ratones(chat_id, context):
    tablero = sesion_ratones["tablero"]
    botones = []
    fila = []
    for idx, val in enumerate(tablero):
        lbl = str(idx + 1) if val in ["🧀", "🪤", "⬜"] else val
        fila.append(InlineKeyboardButton(text=lbl, callback_query_data=f"rt_revelar_{idx}"))
        if (idx + 1) % 5 == 0:
            botones.append(fila)
            fila = []
    
    texto = "🧀 **BUSCANDO QUESO EN LA MADRIGUERA** 🧀\n\n"
    for uid, p in sesion_ratones["jugadores"].items():
        est = "🐭 Vivo" if p["vivo"] else "💀 Atrapado"
        texto += f"• {p['name']}: {p['puntos']} Pts ({est})\n"
        
    await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=InlineKeyboardMarkup(botones))

async def enviar_menu_box(chat_id, context):
    retador = sesion_box["retador"]
    retado = sesion_box["retado"]
    turno = sesion_box["turno_de"]
    name_turno = sesion_box["jugadores"][turno]
    
    texto = "🥊 **CAMPEONATO DE BOXEO** 🥊\n\n"
    texto += f"🟦 {sesion_box['jugadores'][retador]}: {sesion_box['hp'][retador]} HP\n"
    texto += f"🟥 {sesion_box['jugadores'][retado]}: {sesion_box['hp'][retado]} HP\n\n"
    texto += f"👉 Turno de golpe para: **{name_turno}**"
    
    botones = [
        [InlineKeyboardButton(text="Jab Ligero 🥊 (-10 HP / 90% Éxito)", callback_query_data="bx_atk_jab")],
        [InlineKeyboardButton(text="Gancho Fuerte 💥 (-25 HP / 65% Éxito)", callback_query_data="bx_atk_hook")],
        [InlineKeyboardButton(text="Defensa / Esquivar 🛡️ (+Éxito de Contra)", callback_query_data="bx_atk_def")]
    ]
    await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=InlineKeyboardMarkup(botones))

# !!⠀⠀BUCLE INDEPENDIENTE: MANEJADOR DINÁMICO DE CASERÍA⠀ ───⠀ ⠀♥︎

async def ronda_caseria(chat_id, context):
    tablero = sesion_caseria["tablero"]
    objetivos = random.sample(tablero, min(5, len(tablero)))

    for objetivo in objetivos:
        if not sesion_caseria["activa"]:
            break
        sesion_caseria["objetivo_actual"] = objetivo
        sesion_caseria["respondio_turno"] = False

        await context.bot.send_message(chat_id=chat_id,
            text=f"🎯 ¡Encuentra este emoji en el tablero y mándalo! → {objetivo}")

        espera = 15.0
        while espera > 0 and not sesion_caseria.get("respondio_turno", False):
            await asyncio.sleep(0.5)
            espera -= 0.5

        await asyncio.sleep(2)

    if sesion_caseria["activa"]:
        sesion_caseria["activa"] = False
        puntajes = sesion_caseria["jugadores"]
        ranking = sorted(puntajes.items(), key=lambda x: x[1], reverse=True)
        texto = "🏁 **¡CASERÍA TERMINADA!**\n\n📊 Puntaje final:\n"
        medallas = ["🥇", "🥈", "🥉"]
        for i, (uid, pts) in enumerate(ranking):
            dec = medallas[i] if i < 3 else "🔹"
            texto += f"{dec} ID {uid}: {pts} pt(s)\n"
        await context.bot.send_message(chat_id=chat_id, text=texto)

# !!⠀⠀SISTEMA CENTRALIZADO DE EVENTOS DE TEXTO (MENSAJES)⠀ ───⠀ ⠀♥︎

async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if not texto: return
    
    uid = update.effective_user.id
    user_name = update.effective_user.first_name
    is_private = update.message.chat.type == "private"

    # CIPHER: Guardar el código secreto en privado
    if is_private and uid in esperando_code:
        if not texto.isdigit():
            await update.message.reply_text("⚠️ Por favor, envía solo un número (dígitos).")
            return
            
        gid = esperando_code.pop(uid)
        sesion_cipher["codigo"] = texto
        sesion_cipher["activa"] = True

        await update.message.reply_text("¡𝖢𝗈́𝖽𝗂𝗀𝗈 𝗋𝖾𝖼𝗂𝖻𝗂𝖽𝗈! El juego comienza.")
        
        pantalla_inicial = dibujar_pantalla_code(texto, "") 
        
        await context.bot.send_message(
            chat_id=gid,
            text=f"📝 **¡CIPHER INICIADO!**\n\nAdivina el código.\n\n`{pantalla_inicial}`"
        )
        return

    # CIPHER: adivinar número del código en el grupo
    if sesion_cipher.get("activa") and texto.isdigit():
        codigo = sesion_cipher.get("codigo", "")
        
        if len(texto) != len(codigo):
            await update.message.reply_text(f"⚠️ El código debe tener exactamente {len(codigo)} dígitos.")
            return

        pantalla = dibujar_pantalla_code(codigo, texto)
        await update.message.reply_text(f"🧐 Intento de {user_name}:\n\n`{pantalla}`")
        
        if "_" not in pantalla:
            sesion_cipher["activa"] = False
            await update.message.reply_text(f"🎉 **¡{user_name} DESCIFRÓ EL CÓDIGO!** 🎉\n\nEl código era: `{codigo}`")
        return

    # RITMO A GO GO: Lector del flujo de respuestas
    if sesion_ritmo["activa"]:
        idx = sesion_ritmo["turno_index"]
        if user_name == sesion_ritmo["jugadores"][idx]:
            limpio = texto.strip().lower()
            if limpio in sesion_ritmo["historial"]:
                sesion_ritmo["activa"] = False
                await update.message.reply_text(f"❌ ¡Repetido! **{user_name}** dijo una palabra que ya se usó. ¡Pierde la ronda!")
                return
            sesion_ritmo["historial"].append(limpio)
            
            sig_idx = (idx + 1) % len(sesion_ritmo["jugadores"])
            sesion_ritmo["turno_index"] = sig_idx
            sig_jugador = sesion_ritmo["jugadores"][sig_idx]
            await update.message.reply_text(f"✅ ¡Buena! Sigue así.\n👉 Turno de: **{sig_jugador}**")
            return

    # ZOMBIE: Sistema dinámico de combate text-action
    if sesion_zombie["activa"]:
        if uid in sesion_zombie["jugadores"] and sesion_zombie["jugadores"][uid]["vivo"]:
            rol = sesion_zombie["jugadores"][uid]["rol"]
            acc = texto.strip().lower()
            
            if rol == "Humano" and acc == "disparar":
                if sesion_zombie["jugadores"][uid]["balas"] <= 0:
                    await update.message.reply_text(f"🪹 ¡{user_name}, no te quedan balas!")
                    return
                sesion_zombie["jugadores"][uid]["balas"] -= 1
                if random.random() < 0.6:
                    await update.message.reply_text(f"💥 ¡{user_name} le dio un tiro en la cabeza a un zombie!")
                else:
                    await update.message.reply_text(f"💨 ¡{user_name} disparó pero falló el tiro!")
                return
                
            elif rol == "Zombie" and acc == "morder":
                humanos = [k for k, v in sesion_zombie["jugadores"].items() if v["rol"] == "Humano" and v["vivo"]]
                if not humanos:
                    await update.message.reply_text("🧠 No quedan humanos vivos.")
                    return
                victima_id = random.choice(humanos)
                if random.random() < 0.5:
                    sesion_zombie["jugadores"][victima_id]["rol"] = "Zombie"
                    await update.message.reply_text(f"☣️ ¡{user_name} mordió a {sesion_zombie['jugadores'][victima_id]['name']}! Ahora es un **Zombie**.")
                else:
                    await update.message.reply_text(f"🏃‍♂️ ¡{user_name} intentó morder pero el humano escapó!")
                return

    # CASERÍA: Validador instantáneo de reflejos
    if sesion_caseria["activa"] and not sesion_caseria["respondio_turno"]:
        if texto.strip() == sesion_caseria["objetivo_actual"]:
            sesion_caseria["respondio_turno"] = True
            if uid not in sesion_caseria["jugadores"]:
                sesion_caseria["jugadores"][uid] = 0
            sesion_caseria["jugadores"][uid] += 1
            await update.message.reply_text(f"⚡ ¡{user_name} lo encontró primero! (+1 punto)")
            return

    # CHARADA: Validador de palabras
    if sesion_charada["activa"] and uid != sesion_charada["moderador"]:
        if texto.strip().lower() == sesion_charada["palabra"]:
            sesion_charada["activa"] = False
            await update.message.reply_text(f"🎉 ¡{user_name} ADIVINÓ LA CHARADA! La palabra era: **{sesion_charada['palabra']}**")
            return

    # PIRATA: Lector de mapas por coordenadas
    if sesion_pirata["activa"] and uid in sesion_pirata["jugadores"]:
        try:
            parts = texto.strip().split(",")
            if len(parts) == 2:
                x = int(parts[0].strip())
                y = int(parts[1].strip())
                sesion_pirata["jugadores"][uid]["intentos"] += 1
                
                if x == sesion_pirata["tesoro_x"] and y == sesion_pirata["tesoro_y"]:
                    sesion_pirata["activa"] = False
                    await update.message.reply_text(f"👑 ¡🏴‍☠️ {user_name} ENCONTRÓ EL COFRE DEL TESORO en ({x},{y})! Intentos: {sesion_pirata['jugadores'][uid]['intentos']}")
                else:
                    dist = abs(x - sesion_pirata["tesoro_x"]) + abs(y - sesion_pirata["tesoro_y"])
                    await update.message.reply_text(f"🕳️ {user_name} cavó en ({x},{y}) pero solo halló arena. Distancia al tesoro: {dist}")
        except ValueError:
            pass

# !!⠀⠀INTERFACES COMPLETA DE ACCIONES DE BOTONES (CALLBACK QUERIES)⠀ ───⠀ ⠀♥︎

async def manejar_botones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = query.from_user.id
    uname = query.from_user.first_name

    # CALLBACK JUEGO: SNOWBALL
    if data.startswith("sb_"):
        if not sesion_snowball["activa"]: return
        if uid != sesion_snowball["turno_de"]: return
        
        orden = sesion_snowball["orden"]
        idx = orden.index(uid)
        
        if data == "sb_recargar":
            sesion_snowball["jugadores"][uid]["nieve"] += 2
            await query.message.reply_text(f"⚪ {uname} recargó bolas de nieve.")
        elif data.startswith("sb_atacar_"):
            target_id = int(data.split("_")[2])
            if sesion_snowball["jugadores"][uid]["nieve"] <= 0:
                await query.message.reply_text("⚠️ No tienes nieve, ¡recarga primero!")
                return
            sesion_snowball["jugadores"][uid]["nieve"] -= 1
            if random.random() < 0.7:
                sesion_snowball["jugadores"][target_id]["hp"] -= 1
                await query.message.reply_text(f"🎯 ¡{uname} le dio un itazo de nieve a {sesion_snowball['jugadores'][target_id]['name']}!")
                if sesion_snowball["jugadores"][target_id]["hp"] <= 0:
                    sesion_snowball["eliminados"].append(target_id)
            else:
                await query.message.reply_text(f"💨 ¡{uname} falló el lanzamiento!")
                
        vivos = [k for k in orden if k not in sesion_snowball["eliminados"]]
        if len(vivos) <= 1:
            sesion_snowball["activa"] = False
            ganador = sesion_snowball["jugadores"][vivos[0]]["name"] if vivos else "Nadie"
            await query.message.reply_text(f"🏆 **🏁 GUERRA TERMINADA** 🏆\n\nEl único sobreviviente en pie es: ¡**{ganador}**!")
            return
            
        sig_idx = (idx + 1) % len(orden)
        while orden[sig_idx] in sesion_snowball["eliminados"]:
            sig_idx = (sig_idx + 1) % len(orden)
            
        sesion_snowball["turno_de"] = orden[sig_idx]
        await query.message.delete()
        await enviar_tablero_snowball(query.message.chat_id, context)

    # CALLBACK JUEGO: RATONES
    elif data.startswith("rt_"):
        if not sesion_ratones["activa"]: return
        if uid not in sesion_ratones["jugadores"] or not sesion_ratones["jugadores"][uid]["vivo"]: return
        
        idx = int(data.split("_")[2])
        val = sesion_ratones["tablero"][idx]
        if val in ["🧀", "🪤", "⬜"]:
            if val == "🧀":
                sesion_ratones["jugadores"][uid]["puntos"] += 1
                sesion_ratones["tablero"][idx] = "🧀"
                await query.message.reply_text(f"🧀 ¡{uname} encontró un queso delicioso!")
            elif val == "🪤":
                sesion_ratones["jugadores"][uid]["vivo"] = False
                sesion_ratones["tablero"][idx] = "🪤"
                await query.message.reply_text(f"💀 ¡{uname} cayó en una trampa para ratones!")
            else:
                sesion_ratones["tablero"][idx] = "❌"
                await query.message.reply_text(f"🕳️ {uname} buscó pero el nido estaba vacío.")
                
            vivos = [k for k, v in sesion_ratones["jugadores"].items() if v["vivo"]]
            quesos_restantes = any(v == "🧀" for v in sesion_ratones["tablero"])
            
            if not vivos or not quesos_restantes:
                sesion_ratones["activa"] = False
                await query.message.reply_text("🏁 **FIN DEL JUEGO** 🏁\n\nYa no quedan ratones vivos o los quesos se terminaron.")
                return
                
            await query.message.delete()
            await enviar_tablero_ratones(query.message.chat_id, context)

    # CALLBACK JUEGO: BOX
    elif data.startswith("bx_"):
        if not sesion_box["activa"]: return
        if uid != sesion_box["turno_de"]: return
        
        retador = sesion_box["retador"]
        retado = sesion_box["retado"]
        oponente = retado if uid == retador else retador
        
        tipo = data.split("_")[2]
        if tipo == "jab":
            if random.random() < 0.9:
                sesion_box["hp"][oponente] -= 10
                await query.message.reply_text(f"🥊 ¡{uname} conectó un Jab rápido en la cara de su rival! (-10 HP)")
            else:
                await query.message.reply_text(f"💨 ¡{uname} lanzó un jab pero fue esquivado!")
        elif tipo == "hook":
            if random.random() < 0.65:
                sesion_box["hp"][oponente] -= 25
                await query.message.reply_text(f"💥 ¡{uname} metió un Gancho brutal al hígado! (-25 HP)")
            else:
                await query.message.reply_text(f"💨 ¡{uname} falló el gancho y quedó vendido!")
        elif tipo == "def":
            await query.message.reply_text(f"🛡️ {uname} subió la guardia para cubrirse en el próximo turno.")
            
        if sesion_box["hp"][oponente] <= 0:
            sesion_box["activa"] = False
            await query.message.reply_text(f"🥇 ¡K.O.! **{uname}** derrotó a su oponente y es el campeón de la noche.")
            return
            
        sesion_box["turno_de"] = oponente
        await query.message.delete()
        await enviar_menu_box(query.message.chat_id, context)

# !!⠀⠀SISTEMA PRINCIPAL: CONFIGURACIÓN E INICIALIZACIÓN DEL BOT⠀ ───⠀ ⠀♥︎

if __name__ == "__main__":
    import threading
    
    # Levantar el servidor web para Render de forma independiente
    def run_web():
        app_web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
        
    threading.Thread(target=run_web, daemon=True).start()

    TOKEN = os.environ.get("TELEGRAM_TOKEN", "TU_TOKEN_AQUI")
    application = ApplicationBuilder().token(TOKEN).build()

    # Comandos iniciales generales
    application.add_handler(CommandHandler("start", start, filters=PREFIX))
    application.add_handler(CommandHandler("help",  info_help, filters=PREFIX))
    application.add_handler(CommandHandler("info",  info_help, filters=PREFIX))

    # Handlers del Servidor: Snowball
    application.add_handler(CommandHandler("snowball",       unirse_snowball,  filters=PREFIX))
    application.add_handler(CommandHandler("start_snowball", iniciar_snowball, filters=PREFIX))

    # Handlers del Servidor: Ratones
    application.add_handler(CommandHandler("ratones",       unirse_ratones,  filters=PREFIX))
    application.add_handler(CommandHandler("start_ratones", iniciar_ratones, filters=PREFIX))

    # Handlers del Servidor: Ritmo
    application.add_handler(CommandHandler("ritmo",       unirse_ritmo,  filters=PREFIX))
    application.add_handler(CommandHandler("start_ritmo", iniciar_ritmo, filters=PREFIX))

    # Handlers del Servidor: Cipher
    application.add_handler(CommandHandler("cipher",       unirse_cipher,  filters=PREFIX))
    application.add_handler(CommandHandler("start_cipher", iniciar_cipher, filters=PREFIX))

    # Handlers del Servidor: Zombie
    application.add_handler(CommandHandler("zombie",       unirse_zombie,  filters=PREFIX))
    application.add_handler(CommandHandler("start_zombie", iniciar_zombie, filters=PREFIX))

    # Handlers del Servidor: Casería
    application.add_handler(CommandHandler("caseria",       unirse_caseria,  filters=PREFIX))
    application.add_handler(CommandHandler("start_caseria", iniciar_caseria, filters=PREFIX))

    # Handlers del Servidor: Box
    application.add_handler(CommandHandler("box",       unirse_box,  filters=PREFIX))
    application.add_handler(CommandHandler("start_box", iniciar_box, filters=PREFIX))

    # Handlers del Servidor: Charada
    application.add_handler(CommandHandler("charada",       unirse_charada,  filters=PREFIX))
    application.add_handler(CommandHandler("start_charada", iniciar_charada, filters=PREFIX))

    # Handlers del Servidor: Pirata
    application.add_handler(CommandHandler("pirata",       unirse_pirata,  filters=PREFIX))
    application.add_handler(CommandHandler("start_pirata", iniciar_pirata, filters=PREFIX))

    # Handlers estructurales generales
    application.add_handler(CallbackQueryHandler(manejar_botones))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    print("Van ha sido encendido correctamente...")
    application.run_polling()
