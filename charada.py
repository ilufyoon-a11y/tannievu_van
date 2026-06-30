import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_CHARADA, GIF_ERROR

# ================= DICCIONARIO =================

DICCIONARIOS_CHARADA = {
    "peliculas_animadas": [
        "Coraline y la Puerta Secreta", "Kung Fu Panda", "La era del hielo", "Ratatouille",
        "Monsters, Inc.", "Toy Story", "Up", "Intensamente", "Buscando a Nemo", "Shrek",
        "Mi villano favorito", "Hotel Transylvania", "Rio", "Coco", "El rey león", "Enredados", "Frozen",
    ],
    "personajes": [
        "Mickey Mouse", "Bugs Bunny", "Bob Esponja", "Pato Donald", "Pikachu", "Pedro Picapiedra",
        "Las Chicas Superpoderosas", "La Pantera Rosa", "Dora la Exploradora", "Peppa Pig",
        "Hello Kitty", "El Grinch",
    ],
    "kpop": [
        "dynamite", "butter", "boy with luv", "fake love", "dna",
        "mic drop", "idol", "run bts", "spring day", "permission to dance",
    ],
}

sesion_charada = {
    "activa": False,
    "fase_registro": False,
    "jugadores": [],
    "equipo_rojo": [],
    "equipo_azul": [],
    "bando_actual": None,
    "moderador_id": None,
    "nombre_recibido": False,
    "nombre_equipo_rojo": "Equipo Rojo 🔴",
    "nombre_equipo_azul": "Equipo Azul 🔵",
    "categoria_random": "",
    "palabras_ronda": {},
    "mensaje_grupo_id": None,
    "puntos_rojo": 0,
    "puntos_azul": 0,
}

# ================= CODIGO PRINCIPAL =================

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_charada.get("fase_registro") or sesion_charada.get("activa"):
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝗈 𝗋𝖾𝗀𝗂𝗌𝗍𝗋𝗈 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!")
        return

    sesion_charada["jugadores"] = []
    sesion_charada["equipo_rojo"] = []
    sesion_charada["equipo_azul"] = []
    sesion_charada["puntos_rojo"] = 0
    sesion_charada["puntos_azul"] = 0
    sesion_charada["fase_registro"] = True
    sesion_charada["activa"] = False

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_box_click")
    await update.message.reply_photo(
        photo=GIF_JITB,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ lɑs Chɑrɑdɑs!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_charada &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_charada.get("fase_registro"):
        await update.message.reply_text("⚠️ No hay ninguna convocatoria abierta. Usa `.charada` primero.")
        return

    if len(sesion_charada["jugadores"]) < 4:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟦 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝖺𝗋𝗆𝖺𝗋 𝗅𝗈𝗌 𝖽𝗈𝗌 𝖾𝗊𝗎𝗂𝗉𝗈𝗌.")
        return

    sesion_charada["fase_registro"] = False

    # Parsear premio opcional: /start_charada 10
    args = context.args or []
    premio = int(args[0]) if args and args[0].isdigit() else 0
    sesion_puntos["premio_actual"]["charada"] = premio

    lista_ids = [j["id"] for j in sesion_charada["jugadores"]]
    random.shuffle(lista_ids)
    mitad = len(lista_ids) // 2
    sesion_charada["equipo_rojo"] = lista_ids[:mitad]
    sesion_charada["equipo_azul"] = lista_ids[mitad:]

    nombres_rojo = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_rojo"]]
    nombres_azul = [next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid) for uid in sesion_charada["equipo_azul"]]

    sesion_charada["nombre_equipo_rojo"] = "Equipo Rojo 🔴"
    sesion_charada["nombre_equipo_azul"] = "Equipo Azul 🔵"

    bando_inicial = random.choice(["rojo", "azul"])
    sesion_charada["bando_actual"] = bando_inicial

    id_moderador = random.choice(sesion_charada["equipo_rojo"] if bando_inicial == "rojo" else sesion_charada["equipo_azul"])
    nombre_moderador = next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == id_moderador)

    categoria = random.choice(list(DICCIONARIOS_CHARADA.keys()))
    palabras_elegidas = random.sample(DICCIONARIOS_CHARADA[categoria], 10)
    sesion_charada["palabras_ronda"] = {palabra: False for palabra in palabras_elegidas}
    sesion_charada["categoria_random"] = categoria
    sesion_charada["moderador_id"] = id_moderador
    sesion_charada["nombre_recibido"] = False

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⚔️ **¡EQUIPOS FORMADOS!** ⚔️\n\n"
             f"🔴 **EQUIPO ROJO:** {', '.join(nombres_rojo)}\n"
             f"🔵 **EQUIPO AZUL:** {', '.join(nombres_azul)}\n\n"
             f"📣 **PRIMERA RONDA:** Juega el **EQUIPO {bando_inicial.upper()}**.\n"
             f"🎙️ **Moderador:** {nombre_moderador}\n\n"
             f"👀 ¡Atento al privado, tienes 15 segundos para nombrar a tu equipo!"
    )

    try:
        await context.bot.send_message(chat_id=id_moderador,
            text="👑 **¡ERES EL MODERADOR DE TU EQUIPO!** 👑\n\n"
                 "Escribe aquí el **NOMBRE PERSONALIZADO** para tu bando.\n\n"
                 "⏱️ ¡Tienes 15 segundos o el bot pondrá un nombre random!")
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"⚠️ ¡{nombre_moderador} debes iniciar el bot en privado! Se canceló la partida.")
        return

    espera = 15.0
    while espera > 0 and not sesion_charada["nombre_recibido"]:
        await asyncio.sleep(0.5)
        espera -= 0.5

    if not sesion_charada["nombre_recibido"]:
        nombre_random = random.choice(["Los Sin Nombre 🦆", "Los Pasados de Frío ❄️", "Los Lentos de Van 🦥", "Mimos Anónimos 🎭"])
        if bando_inicial == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{nombre_random} (Rojo)"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{nombre_random} (Azul)"

    lista_texto = "\n".join([f"🔹 {p.upper()}" for p in palabras_elegidas])
    await context.bot.send_message(chat_id=id_moderador,
        text=f"🤫 **¡AQUÍ ESTÁN TUS PALABRAS SECRETAS!** 🤫\n\n"
             f"🗂️ Categoría: **{categoria.upper()}**\n\n{lista_texto}\n\n"
             f"¡Corre al grupo a meter mímicas y emojis! No escribas las palabras directamente. 💀")

    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_inicial == "rojo" else sesion_charada["nombre_equipo_azul"]
    sesion_charada["activa"] = True

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎮 **¡EMPIEZA EL CONTRARRELOJ!** 🎮\n\n"
             f"🔥 **Bando jugando:** ✨ {nombre_bando_jugando.upper()} ✨\n"
             f"🎙️ **Moderador:** {nombre_moderador}\n"
             f"🗂️ **Categoría:** {categoria.upper()}\n\n"
             f"¡Tienen 60 segundos para adivinar las 10 palabras! 🔥"
    )

    asyncio.create_task(reloj_charada(chat_id, context))

async def reloj_charada(chat_id, context):
    segundos = 60
    while segundos > 0 and sesion_charada["activa"]:
        await asyncio.sleep(1)
        segundos -= 1

    if sesion_charada["activa"]:
        sesion_charada["activa"] = False
        adivinadas = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)
        bando = sesion_charada["bando_actual"]
        nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando == "rojo" else sesion_charada["nombre_equipo_azul"]

        if bando == "rojo":
            sesion_charada["puntos_rojo"] += adivinadas
        else:
            sesion_charada["puntos_azul"] += adivinadas

        faltantes = [p.upper() for p, v in sesion_charada["palabras_ronda"].items() if not v]
        texto_faltantes = ", ".join(faltantes) if faltantes else "¡Ninguna, las hicieron todas! 🔥"

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏱️ **¡TIEMPO AGOTADO!** ⏱️\n\n"
                 f"El equipo **{nombre_bando_jugando.upper()}** logró adivinar **{adivinadas}/10** palabras.\n"
                 f"❌ **Faltaron:** {texto_faltantes}\n\n"
                 f"📊 **PUNTAJE GLOBAL:**\n"
                 f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                 f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts\n\n"
                 f"¡El bot queda libre para otra ronda! 🎭"
        )

        # Pagar robux al equipo con más puntos
        premio = sesion_puntos.get("premio_actual", {}).get("charada", 0)
        if premio > 0:
            pts_r = sesion_charada["puntos_rojo"]
            pts_a = sesion_charada["puntos_azul"]
            if pts_r != pts_a:
                equipo_ganador_ids = sesion_charada["equipo_rojo"] if pts_r > pts_a else sesion_charada["equipo_azul"]
                nombre_ganador = sesion_charada["nombre_equipo_rojo"] if pts_r > pts_a else sesion_charada["nombre_equipo_azul"]
                for uid in equipo_ganador_ids:
                    nombre = next((j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid), str(uid))
                    sumar_robux(uid, nombre, premio, f"Charada 🎭 ({nombre_ganador})")

# ================= MANEJO DE MENSAJES =================

async def escuchar_charada_privado(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str):
    if (not sesion_charada.get("activa") and
            sesion_charada.get("moderador_id") == user_id and
            not sesion_charada.get("nombre_recibido")):
        if not texto:
            return
        if sesion_charada["bando_actual"] == "rojo":
            sesion_charada["nombre_equipo_rojo"] = f"{texto} 🔴"
        else:
            sesion_charada["nombre_equipo_azul"] = f"{texto} 🔵"
        sesion_charada["nombre_recibido"] = True
        await update.message.reply_text(f"✅ ¡Nombre registrado! Tu equipo se llamará: **{texto.upper()}**.")

async def escuchar_charada_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, texto: str, chat_id: int):
    if not sesion_charada.get("activa"):
        return
    if user_id == sesion_charada["moderador_id"]:
        return
    if not texto:
        return

    bando_actual = sesion_charada["bando_actual"]
    lista_equipo_valido = sesion_charada["equipo_rojo"] if bando_actual == "rojo" else sesion_charada["equipo_azul"]
    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando_actual == "rojo" else sesion_charada["nombre_equipo_azul"]

    if user_id not in lista_equipo_valido:
        return

    texto_limpio = texto.lower()
    if texto_limpio in sesion_charada["palabras_ronda"] and not sesion_charada["palabras_ronda"][texto_limpio]:
        sesion_charada["palabras_ronda"][texto_limpio] = True
        adivinadas_totales = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)

        await update.message.reply_text(
            f"🎉 ¡{update.effective_user.first_name} ADIVINÓ! ✨\n"
            f"✅ Palabra: **{texto_limpio.upper()}**\n"
            f"📊 {nombre_bando_jugando}: **{adivinadas_totales}/10** acertadas.")

        if adivinadas_totales == 10:
            sesion_charada["activa"] = False
            if bando_actual == "rojo":
                sesion_charada["puntos_rojo"] += 10
            else:
                sesion_charada["puntos_azul"] += 10
            await context.bot.send_message(chat_id=chat_id,
                text=f"🏆 **¡PUNTAJE PERFECTO!** 🏆\n\n"
                     f"¡El equipo **{nombre_bando_jugando.upper()}** adivinó las 10 palabras!\n\n"
                     f"📊 **PUNTAJE GLOBAL:**\n"
                     f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} pts\n"
                     f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} pts")

            # Pagar robux al equipo que acaba de jugar (puntaje perfecto)
            premio = sesion_puntos.get("premio_actual", {}).get("charada", 0)
            if premio > 0:
                for uid in lista_equipo_valido:
                    nombre = next((j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid), str(uid))
                    sumar_robux(uid, nombre, premio, f"Charada 🎭 puntaje perfecto")

# ================= MANEJO DE BOTONES =================

async def manejar_botones_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if query.data == "unirme_charada_click":
        await query.answer()
        if sesion_charada.get("activa"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝖾𝗌𝗍𝖺́ 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖼𝗈𝗋𝗋𝗂𝖾𝗇𝖽𝗈!", show_alert=True)
            return
        if not sesion_charada.get("fase_registro"):
            await query.answer("¡El registro ya cerró!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_charada["jugadores"]):
            sesion_charada["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🎭 ֹ  {nombre_usuario(user)} se apuntó a las mímicas 𓂃")
