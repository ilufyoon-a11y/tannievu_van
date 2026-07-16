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
    "nombre_equipo_rojo": "Equipo Rojo 🔴",
    "nombre_equipo_azul": "Equipo Azul 🔵",
    "categoria_random": "",
    "palabras_ronda": {},
    "mensaje_grupo_id": None,
    "puntos_rojo": 0,
    "puntos_azul": 0,
    "ronda": 1,
}

# ================= CODIGO PRINCIPAL =================

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sesion_charada.get("fase_registro") or sesion_charada.get("activa"):
        await update.message.reply_text("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!!")
        return

    sesion_charada["jugadores"] = []
    sesion_charada["equipo_rojo"] = []
    sesion_charada["equipo_azul"] = []
    sesion_charada["puntos_rojo"] = 0
    sesion_charada["puntos_azul"] = 0
    sesion_charada["nombre_equipo_rojo"] = "Equipo Rojo 🔴"
    sesion_charada["nombre_equipo_azul"] = "Equipo Azul 🔵"
    sesion_charada["ronda"] = 1
    sesion_charada["fase_registro"] = True
    sesion_charada["activa"] = False

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_charada_click")
    await update.message.reply_photo(
        photo=GIF_CHARADA,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ lɑs Chɑrɑdɑs!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_charada &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not sesion_charada.get("fase_registro"):
        await update.message.reply_text("𝖭𝗈 𝗁𝖺𝗒 𝗇𝗂𝗇𝗀𝗎𝗇𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝖺, 𝗉𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗎𝗍𝗂𝗅𝗂𝗓𝖺 /charada 𝗉𝖺𝗋𝖺 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺.")
        return

    if len(sesion_charada["jugadores"]) < 4:
        await update.message.reply_text("𝖲𝖾 𝗋𝖾𝗊𝗎𝗂𝖾𝗋𝖾 𝗎𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝖽𝖾 𝟦 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝖾𝗅 𝗃𝗎𝖾𝗀𝗈.")
        await context.bot.send_sticker(
            chat_id=chat_id,
            sticker="CAACAgEAAxkBA0YjA2pC_GvuE3HlS-TBssS4FfvQWCQhAAKIBQAChFVARKjsu2IDSstPPAQ"
        )
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

    bando_inicial = random.choice(["rojo", "azul"])
    sesion_charada["ronda"] = 1

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"⚔️ 𝗘𝗤𝗨𝗜𝗣𝗢𝗦 𝗙𝗢𝗥𝗠𝗔𝗗𝗢𝗦 ⚔️\n\n"
             f"🔴 𝗘𝗤𝗨𝗜𝗣𝗢 𝗥𝗢𝗝𝗢: {', '.join(nombres_rojo)}\n"
             f"🔵 𝗘𝗤𝗨𝗜𝗣𝗢 𝗔𝗭𝗨𝗟: {', '.join(nombres_azul)}\n\n"
             f"📣 𝖤𝗅 𝗃𝗎𝖾𝗀𝗈 𝗌𝖾 𝗃𝗎𝖾𝗀𝖺 𝖾𝗇 𝟤 𝗋𝗈𝗇𝖽𝖺𝗌: 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝗎𝗇 𝖾𝗊𝗎𝗂𝗉𝗈, 𝗅𝗎𝖾𝗀𝗈 𝖾𝗅 𝗈𝗍𝗋𝗈. ¡𝖦𝖺𝗇𝖺 𝗊𝗎𝗂𝖾𝗇 𝗍𝖾𝗇𝗀𝖺 𝗆𝖺𝗌 𝗉𝗎𝗇𝗍𝗈𝗌 𝖺𝗅 𝖿𝗂𝗇𝖺𝗅!"
    )

    await iniciar_ronda(chat_id, context, bando_inicial, 1)

async def iniciar_ronda(chat_id, context, bando, numero_ronda):
    """Prepara y arranca una ronda (1 o 2) para el equipo indicado."""
    sesion_charada["bando_actual"] = bando
    sesion_charada["ronda"] = numero_ronda

    equipo_ids = sesion_charada["equipo_rojo"] if bando == "rojo" else sesion_charada["equipo_azul"]
    id_moderador = random.choice(equipo_ids)
    nombre_moderador = next(j["name"] for j in sesion_charada["jugadores"] if j["id"] == id_moderador)

    categoria = random.choice(list(DICCIONARIOS_CHARADA.keys()))
    palabras_elegidas = random.sample(DICCIONARIOS_CHARADA[categoria], 10)
    sesion_charada["palabras_ronda"] = {palabra.lower(): False for palabra in palabras_elegidas}
    sesion_charada["palabras_originales"] = palabras_elegidas
    sesion_charada["categoria_random"] = categoria
    sesion_charada["moderador_id"] = id_moderador

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"📣 𝗥𝗢𝗡𝗗𝗔 {numero_ronda}: 𝖩𝗎𝖾𝗀𝖺 𝖾𝗅 𝗘𝗤𝗨𝗜𝗣𝗢 {bando.upper()}.\n"
             f"🎙️ 𝗠𝗼𝗱𝗲𝗿𝗮𝗱𝗼𝗿: {nombre_moderador}"
    )

    lista_texto = "\n".join([f"🔹 {p.upper()}" for p in palabras_elegidas])
    try:
        await context.bot.send_message(chat_id=id_moderador,
            text=f"🤫 ¡𝗔𝗤𝗨Ɩ́ 𝗘𝗦𝗧𝗔́𝗡 𝗧𝗨𝗦 𝗣𝗔𝗟𝗔𝗕𝗥𝗔𝗦 𝗦𝗘𝗖𝗥𝗘𝗧𝗔𝗦ⵑ 🤫\n\n"
                 f"🗂️ 𝗖𝗮𝘁𝗲𝗴𝗼𝗿𝗶𝗮: {categoria.upper()}\n\n{lista_texto}\n\n"
                 f"¡𝖢𝗈𝗋𝗋𝖾 𝖺𝗅 𝗀𝗋𝗎𝗉𝗈, 𝗉𝗎𝖾𝖽𝖾𝗌 𝗎𝗌𝖺𝗋 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝗈 𝖾𝗆𝗈𝗃𝗂𝗌 𝗉𝖺𝗋𝖺 𝗅𝗈𝗀𝗋𝖺𝗋 𝗊𝗎𝖾 𝗍𝗎 𝖾𝗊𝗎𝗂𝗉𝗈 𝖺𝖽𝗂𝗏𝗂𝗇𝖾! 𝖭𝗈 𝖾𝗌𝖼𝗋𝗂𝖻𝖺𝗌 𝗅𝖺𝗌 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝖽𝗂𝗋𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 💀")
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 {nombre_moderador}. 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍.")
        return

    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando == "rojo" else sesion_charada["nombre_equipo_azul"]
    sesion_charada["activa"] = True

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🎮 ¡𝗘𝗠𝗣𝗜𝗘𝗭𝗔 𝗘𝗟 𝗖𝗢𝗡𝗧𝗥𝗔𝗥𝗥𝗘𝗟𝗢𝗝ⵑ 🎮\n\n"
             f"🔥 𝗘𝗾𝘂𝗶𝗽𝗼 𝗮𝗰𝘁𝘂𝗮𝗹: ✨ {nombre_bando_jugando.upper()} ✨\n"
             f"🎙️ 𝗠𝗼𝗱𝗲𝗿𝗮𝗱𝗼𝗿: {nombre_moderador}\n"
             f"🗂️ 𝗖𝗮𝘁𝗲𝗴𝗼𝗿𝗶𝗮: {categoria.upper()}\n\n"
             f"¡𝖳𝗂𝖾𝗇𝖾𝗇 𝟪𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋 𝗅𝖺𝗌 𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌! 🔥"
    )

    asyncio.create_task(reloj_charada(chat_id, context))

async def reloj_charada(chat_id, context):
    segundos = 80
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

        faltantes = [p.upper() for p in sesion_charada["palabras_originales"] if not sesion_charada["palabras_ronda"][p.lower()]]
        texto_faltantes = ", ".join(faltantes) if faltantes else "¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌, 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋𝗈𝗇 𝗍𝗈𝖽𝖺𝗌 𝗅𝖺𝗌 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌! 🔥"

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏱️ ¡𝗧𝗜𝗘𝗠𝗣𝗢 𝗔𝗚𝗢𝗧𝗔𝗗𝗢ⵑ ⏱️\n\n"
                 f"𝖤𝗅 𝖾𝗊𝗎𝗂𝗉𝗈 {nombre_bando_jugando.upper()} 𝗅𝗈𝗀𝗋𝗈 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋 {adivinadas}/𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌.\n"
                 f"❌ 𝖥𝖺𝗅𝗍𝖺𝗋𝗈𝗇: {texto_faltantes}\n\n"
                 f"📊 𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗚𝗟𝗢𝗕𝗔𝗟:\n"
                 f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} 𝗉𝗍𝗌\n"
                 f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} 𝗉𝗍𝗌\n\n"
        )

        await avanzar_o_finalizar(chat_id, context)

async def avanzar_o_finalizar(chat_id, context):
    """Si acaba de terminar la ronda 1, arranca la ronda 2 con el otro equipo.
    Si ya se jugaron las 2 rondas, determina al ganador y reparte el premio."""
    if sesion_charada["ronda"] == 1:
        bando_anterior = sesion_charada["bando_actual"]
        siguiente_bando = "azul" if bando_anterior == "rojo" else "rojo"
        await iniciar_ronda(chat_id, context, siguiente_bando, 2)
    else:
        await finalizar_juego(chat_id, context)

async def finalizar_juego(chat_id, context):
    pts_r = sesion_charada["puntos_rojo"]
    pts_a = sesion_charada["puntos_azul"]

    if pts_r == pts_a:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🤝 ¡𝗘𝗠𝗣𝗔𝗧𝗘ⵑ 🤝\n\n"
                 f"📊 𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗙𝗜𝗡𝗔𝗟:\n"
                 f"🔴 {sesion_charada['nombre_equipo_rojo']}: {pts_r} 𝗉𝗍𝗌\n"
                 f"🔵 {sesion_charada['nombre_equipo_azul']}: {pts_a} 𝗉𝗍𝗌\n\n"
                 f"¡𝖭𝗈 𝗁𝗎𝖻𝗈 𝗋𝖾𝗉𝖺𝗋𝗍𝗈 𝖽𝖾 𝖿𝗂𝖼𝗁𝖺𝗌, 𝖾𝗆𝗉𝖺𝗍𝖺𝗋𝗈𝗇!"
        )
    else:
        equipo_ganador_ids = sesion_charada["equipo_rojo"] if pts_r > pts_a else sesion_charada["equipo_azul"]
        nombre_ganador = sesion_charada["nombre_equipo_rojo"] if pts_r > pts_a else sesion_charada["nombre_equipo_azul"]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🏆 ¡𝗝𝗨𝗘𝗚𝗢 𝗧𝗘𝗥𝗠𝗜𝗡𝗔𝗗𝗢ⵑ 🏆\n\n"
                 f"📊 𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗙𝗜𝗡𝗔𝗟:\n"
                 f"🔴 {sesion_charada['nombre_equipo_rojo']}: {pts_r} 𝗉𝗍𝗌\n"
                 f"🔵 {sesion_charada['nombre_equipo_azul']}: {pts_a} 𝗉𝗍𝗌\n\n"
                 f"✨ ¡𝖦𝖺𝗇𝖺𝖽𝗈𝗋: {nombre_ganador.upper()}! ✨"
        )

        premio = sesion_puntos.get("premio_actual", {}).get("charada", 0)
        if premio > 0:
            for uid in equipo_ganador_ids:
                nombre = next((j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid), str(uid))
                sumar_robux(uid, nombre, premio, f"𝖢𝗁𝖺𝗋𝖺𝖽𝖺 🎭 ({nombre_ganador})")

    sesion_charada["activa"] = False
    sesion_charada["fase_registro"] = False

# ================= MANEJO DE MENSAJES =================


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
            f"🎉 ¡{update.effective_user.first_name} 𝖺𝖽𝗂𝗏𝗂𝗇𝗈 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺! ✨\n"
            f"✅ 𝖯𝖺𝗅𝖺𝖻𝗋𝖺: {texto_limpio.upper()}\n"
            f"📊 {nombre_bando_jugando}: {adivinadas_totales}/𝟣𝟢 𝖺𝖼𝖾𝗋𝗍𝖺𝖽𝖺𝗌.")

        if adivinadas_totales == 10:
            sesion_charada["activa"] = False
            if bando_actual == "rojo":
                sesion_charada["puntos_rojo"] += 10
            else:
                sesion_charada["puntos_azul"] += 10
            await context.bot.send_message(chat_id=chat_id,
                text=f"🏆 ¡𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗣𝗘𝗥𝗙𝗘𝗖𝗧𝗢ⵑ 🏆\n\n"
                     f"¡𝖤𝗅 𝖾𝗊𝗎𝗂𝗉𝗈 {nombre_bando_jugando.upper()} 𝖺𝖽𝗂𝗏𝗂𝗇𝗈 𝗅𝖺𝗌 𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌!\n\n"
                     f"📊 𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗚𝗟𝗢𝗕𝗔𝗟:\n"
                     f"🔴 {sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} 𝗉𝗍𝗌\n"
                     f"🔵 {sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} 𝗉𝗍𝗌")

            await avanzar_o_finalizar(chat_id, context)

# ================= MANEJO DE BOTONES =================

async def manejar_botones_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if query.data == "unirme_charada_click":
        await query.answer()
        if sesion_charada.get("activa"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not sesion_charada.get("fase_registro"):
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_charada["jugadores"]):
            sesion_charada["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"🎭 ֹ  {nombre_usuario(user)} se unio 𓂃")
