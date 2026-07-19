import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, es_admin_sesion, GIF_CHARADA, GIF_ERROR
# ================= DICCIONARIO =================

DICCIONARIOS_CHARADA = {
    "peliculas_animadas": [
        "Blancanieves y los Siete Enanitos", "La Cenicienta", "La Bella Durmiente", "La Sirenita",
        "La Bella y la Bestia", "Aladdín", "El Rey León"", "Mulan", "Tarzán", "Hércules",
        "Lilo & Stitch", "Los Increíbles", "Buscando a Nemo", "Toy Story", "Cars", "Ratatouille",
        "Up", "Valiente", "Frozen", "Enredados", "Moana", "Coco", "Zootopia",
        "Intensamente", "Monsters, Inc.", "Toy Story", "El Jorobado de Notre Dame", 
        "Pinocho", "Dumbo", "Bambi", "Peter Pan", "La Dama y el Vagabundo", "101 Dálmatas",
        "El Libro de la Selva", "Robin Hood", "Los Aristogatos", "Winnie Pooh", "Chicken Little", "Bolt", "Ralph El Demoledor",
        "Rompe Ralph 2", "Mi villano favorito", "Kung Fu Panda", "La era del hielo",
        "Hotel Transylvania", "Rio", "Shrek", "Coraline y la Puerta Secreta",
    ],
    "peliculas": [
        "Titanic", "Jurassic Park", "Star Wars", "El Padrino", "Rocky", "Terminator", "Matrix",
        "Avatar", "Gladiador", "Forrest Gump", "El Señor de los Anillos", "Harry Potter",
        "Piratas del Caribe", "Misión Imposible", "Batman", "Superman", "Spider-Man", "Iron Man",
        "Los Vengadores", "Tiburón", "E.T.", "Volver al Futuro", "Indiana Jones", "King Kong",
        "Godzilla", "Los Cazafantasmas", "Karate Kid", "Rambo", "Duro de Matar", "Top Gun",
        "Origen", "Interestelar", "El Exorcista", "Psicosis", "La La Land", "Pulp Fiction",
        "El Discurso del Rey", "Slumdog Millionaire", "300", "El Gran Gatsby", "Bohemian Rhapsody",
        "Joker", "Parásitos", "Náufrago", "El Silencio de los Inocentes", "Scarface",
        "Pretty Woman", "Grease", "El Diario de Noa", "La Milla Verde", "El Club de la Pelea",
        "Kill Bill", "Django sin Cadenas", "Érase una Vez en Hollywood", "Ford v Ferrari",
        "Whiplash", "La Vida es Bella", "Dunkerque", "1917", "Mad Max: Fury Road",
        "Mi Pobre Angelito", "El Diablo Viste a la Moda", "Chicago", "Moulin Rouge",
        "Corre Lola Corre", "Rápidos y Furiosos", "John Wick",
    ],
    "superheroes__villanos": [
        "Superman", "Batman", "Spider-Man", "Iron Man", "Capitán América", "Thor", "Hulk",
        "Viuda Negra", "Ojo de Halcón", "Mujer Maravilla", "Flash", "Aquaman", "Linterna Verde",
        "Wolverine", "Deadpool", "Doctor Extraño", "Pantera Negra", "Guasón", "Lex Luthor",
        "Thanos", "Darth Vader", "Loki", "Magneto", "Venom", "Duende Verde", "Doctor Octopus",
        "Catwoman", "Harley Quinn", "Bane", "El Pingüino", "Enigma", "Ant-Man", "Capitana Marvel",
        "Star-Lord", "Groot", "Rocket Raccoon", "Doctor Doom", "Ultrón", "Cíclope", "Tormenta",
        "Bestia", "Jean Grey", "Profesor X", "Robin", "Batgirl", "Nightwing", "Shazam", "Cyborg",
        "Flecha Verde", "Los 4 Fantásticos", "Antorcha Humana", "La Mole", "Mujer Invisible",
        "Hombre Elástico", "Kingpin", "Red Skull", "Two-Face", "Riddler",
    ],
    "profesiones": [
        "Médico", "Enfermero", "Maestro", "Bombero", "Policía", "Abogado", "Chef", "Piloto",
        "Ingeniero", "Arquitecto", "Peluquero", "Dentista", "Veterinario", "Electricista",
        "Plomero", "Carpintero", "Pintor", "Fotógrafo", "Periodista", "Cantante", "Actor",
        "Bailarín", "Músico", "Escritor", "Científico", "Astronauta", "Granjero", "Pescador",
        "Panadero", "Sastre", "Mecánico", "Taxista", "Camionero", "Cartero", "Juez", "Militar",
        "Marinero", "Payaso", "Mago", "Detective", "Guardaespaldas", "Modelo", "Diseñador",
        "Programador", "Contador", "Psicólogo", "Farmacéutico", "Barbero", "Jardinero",
        "Albañil", "Soldador", "Salvavidas", "Cirujano", "Traductor", "Guía turístico",
        "Locutor", "DJ", "Entrenador personal", "Costurera", "Chofer", "Recepcionista",
        "Vendedor", "Camarero", "Portero", "Notario", "Analista", "Auditor",
    ],
    "paises": [
        "Argentina", "México", "España", "Estados Unidos", "Brasil", "Francia", "Italia",
        "Alemania", "Reino Unido", "China", "Japón", "Corea del Sur", "India", "Rusia",
        "Canadá", "Australia", "Egipto", "Grecia", "Turquía", "Perú", "Chile", "Colombia",
        "Venezuela", "Ecuador", "Bolivia", "Uruguay", "Paraguay", "Cuba", "República Dominicana",
        "Puerto Rico", "Portugal", "Países Bajos", "Bélgica", "Suiza", "Austria", "Suecia",
        "Noruega", "Dinamarca", "Finlandia", "Polonia", "Irlanda", "Escocia", "Marruecos",
        "Sudáfrica", "Kenia", "Nigeria", "Arabia Saudita", "Israel", "Tailandia", "Vietnam",
        "Filipinas", "Indonesia", "Malasia", "Singapur", "Nueva Zelanda", "Islandia", "Panamá",
        "Costa Rica", "Guatemala", "Honduras", "El Salvador", "Nicaragua", "Jamaica", "Haití",
        "Croacia", "Ucrania", "Hungría", "República Checa",
    ],
    "videojuegos": [
        "Mario Bros", "Zelda", "Pokemon", "Minecraft", "Fortnite", "Among Us", "Roblox",
        "Call of Duty", "FIFA", "GTA", "Tetris", "Pac-Man", "Sonic", "Street Fighter",
        "Mortal Kombat", "Overwatch", "League of Legends", "Valorant", "Counter-Strike", "Halo",
        "Assassin's Creed", "Resident Evil", "Final Fantasy", "Kingdom Hearts", "The Sims",
        "Animal Crossing", "Angry Birds", "Candy Crush", "World of Warcraft", "Fall Guys",
        "Apex Legends", "Rocket League", "Just Dance", "Wii Sports", "Dark Souls", "Elden Ring",
        "God of War", "Uncharted", "The Last of Us", "Cyberpunk 2077", "Red Dead Redemption",
        "Super Smash Bros", "Donkey Kong", "Kirby", "Metroid", "Splatoon", "Genshin Impact",
        "Clash Royale", "Clash of Clans", "Free Fire", "PUBG", "Stardew Valley", "Terraria",
        "Rainbow Six", "Bloodborne", "Skyrim", "Portal", "Doom", "Silent Hill",
    ],
    "series": [
        "Friends", "Breaking Bad", "Game of Thrones", "Stranger Things", "The Office",
        "La Casa de Papel", "Grey's Anatomy", "The Walking Dead", "How I Met Your Mother",
        "Los Simpson", "Family Guy", "South Park", "Bob Esponja", "Rick and Morty",
        "Peaky Blinders", "Vikingos", "Sherlock", "Doctor Who", "Black Mirror", "The Crown",
        "Narcos", "El Chavo del Ocho", "Rebelde", "Élite", "Euphoria", "Wednesday", "You",
        "El Juego del Calamar", "Todos Vivos", "Dark", "The Witcher", "Bridgerton",
        "Emily in Paris", "Outer Banks", "Riverdale", "13 Reasons Why", "Gossip Girl",
        "Pretty Little Liars", "Two and a Half Men", "Modern Family", "Brooklyn Nine-Nine",
        "The Big Bang Theory", "Sex and the City", "Prison Break", "Lost", "Supernatural",
        "Criminal Minds", "CSI", "Bones", "House", "Scrubs", "ER", "Anatomía de Grey",
    ],
    "personajes_animados": [
        "Mickey Mouse", "Bugs Bunny", "Bob Esponja", "Pato Donald", "Pikachu", "Pedro Picapiedra",
        "Las Chicas Superpoderosas", "La Pantera Rosa", "Dora la Exploradora", "Peppa Pig",
        "Hello Kitty", "El Grinch", "Goku", "Naruto", "Luffy", "Sailor Moon", "Doraemon",
        "Shin Chan", "Ash Ketchum", "Totoro", "Sasuke", "Ichigo", "Light Yagami", "Eren Yeager",
        "Levi Ackerman", "Deku", "All Might", "Tanjiro", "Nezuko", "Anya", "Homero Simpson",
        "Bart Simpson", "Peter Griffin", "Stewie Griffin", "Scooby-Doo", "Tom y Jerry",
        "El Coyote y el Correcaminos", "Popeye", "Betty Boop", "El Pájaro Loco",
        "Los Picapiedra", "Los Supersónicos", "Los Padrinos Mágicos", "Jimmy Neutron",
        "Dexter", "Ed, Edd y Eddy", "Hora de Aventura", "Steven Universe", "Gravity Falls",
        "El Increíble Mundo de Gumball", "Patricio Estrella", "Calamardo", "Kirby",
        "Astro Boy", "Speed Racer",
    ],
    "cuentos_infantiles": [
        "Caperucita Roja", "Blancanieves", "Cenicienta", "La Bella Durmiente", "Hansel y Gretel",
        "Los Tres Cerditos", "El Patito Feo", "Pulgarcito", "Ricitos de Oro", "El Gato con Botas",
        "La Sirenita", "Rapunzel", "Peter Pan", "Alicia en el País de las Maravillas",
        "El Mago de Oz", "Pinocho", "El Flautista de Hamelín", "Jack y las Habichuelas Mágicas",
        "La Bella y la Bestia", "El Rey Rana", "El Traje Nuevo del Emperador",
        "La Cigarra y la Hormiga", "El Soldadito de Plomo", "La Reina de las Nieves",
        "Robin Hood", "Merlín", "El Rey Arturo", "Excalibur", "Dragón", "Unicornio",
        "Hada Madrina", "Bruja", "Duende", "Gigante", "Sirena", "Vampiro", "Hombre Lobo",
        "Zombie", "Fantasma", "Genio de la Lámpara", "Alfombra Mágica", "Espejo Mágico",
        "Varita Mágica", "Poción Mágica", "Ogro", "Elfo", "Centauro", "Fénix",
    ],
    "festividades": [
        "Navidad", "Año Nuevo", "Halloween", "San Valentín", "Pascua", "Día de la Madre",
        "Día del Padre", "Día del Niño", "Acción de Gracias", "Día de los Muertos", "Carnaval",
        "Semana Santa", "Cumpleaños", "Independencia", "Hanukkah", "Ramadán",
        "Día de San Patricio", "Oktoberfest", "Día de Reyes", "Nochebuena", "Nochevieja",
        "Día del Trabajo", "Día de la Amistad", "Boda", "Graduación", "Baby Shower",
        "Quinceañera", "Bautizo", "Aniversario", "Día de la Tierra",
    ],
    "discografia_de_BTS": [
        "No More Dream", "N.O", "Boy in Luv", "Danger", "War of Hormone", "Just One Day",
        "I Need U", "Run", "Dope", "Fire", "Save Me", "Blood Sweat & Tears", "Spring Day",
        "Not Today", "DNA", "Mic Drop", "Fake Love", "Idol", "Boy With Luv", "Dionysus",
        "ON", "Black Swan", "Dynamite", "Life Goes On", "Butter", "Permission to Dance",
        "My Universe", "Yet To Come", "Take Two", "For You", "Airplane pt.2", "Lights",
        "Film Out", "Stay Gold", "Bird", "Best of Me", "Mikrokosmos", "Epiphany",
        "Serendipity", "Euphoria", "Singularity", "Home", "Trivia: Just Dance",
        "Trivia: Love", "Trivia: Seesaw", "Make It Right", "Interlude: Shadow", "Outro: Ego",
        "Proof", "Run BTS", "Telepathy", "Dis-ease", "Blue & Grey",
        "We Are Bulletproof: The Eternal", "Whalien 52", "Baepsae", "Am I Wrong",
        "21st Century Girl", "Go Go", "Anpanman", "Magic Shop", "Answer: Love Myself",
        "Waste It On Me", "The Truth Untold", "Chicken Noodle Soup", "Filter", "Louder Than Bombs",
        "Black Swan (Art Film)", "Stay", "So What", "Zero O'Clock", "Respect", "We Are Bulletproof Pt.2",
    ],
}

sesion_charada = {
    "activa": False,
    "fase_registro": False,
    "juego_en_curso": False,
    "jugadores": [],
    "equipo_rojo": [],
    "equipo_azul": [],
    "bando_actual": None,
    "moderador_id": None,
    "nombre_equipo_rojo": "Equipo Rojo 🔴",
    "nombre_equipo_azul": "Equipo Azul 🔵",
    "categoria_random": "",
    "palabras_ronda": {},
    "reloj_task": None,
    "mensaje_grupo_id": None,
    "puntos_rojo": 0,
    "puntos_azul": 0,
    "ronda": 1,
}

# ================= CODIGO PRINCIPAL =================

async def unirse_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝖼𝗋𝖾𝖺𝗋 𝗎𝗇𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return
    if sesion_charada.get("fase_registro") or sesion_charada.get("activa") or sesion_charada.get("juego_en_curso"):
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
    sesion_charada["juego_en_curso"] = False

    task_previa = sesion_charada.get("reloj_task")
    if task_previa and not task_previa.done():
        task_previa.cancel()
    sesion_charada["reloj_task"] = None

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝗨𝗡𝗜𝗥𝗠𝗘ㅤㅤ!¡", callback_data="unirme_charada_click")
    await update.message.reply_photo(
        photo=GIF_CHARADA,
        caption="<b> ៹ ࣪  📦 ¡Juguemos ɑ lɑs Chɑrɑdɑs!</b>\n\nPor fɑvor, pulse el boton pɑrɑ unirse ɑ lɑ pɑrtidɑ.  ֪   𓂃\n\n<blockquote>Cuɑndo esten listos, utilicen <code>/start_charada &lt;cantidad&gt;</code> pɑrɑ inicɑr el juego</blockquote>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_charada(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not es_admin_sesion(update.effective_user.id):
        await update.message.reply_text("𝖲𝗈𝗅𝗈 𝗊𝗎𝗂𝖾𝗇 𝗂𝗇𝗂𝖼𝗂𝗈 𝗅𝖺 𝗌𝖾𝗌𝗂𝗈𝗇 𝗉𝗎𝖾𝖽𝖾 𝗂𝗇𝗂𝖼𝗂𝖺𝗋 𝗅𝖺 𝗉𝖺𝗋𝗍𝗂𝖽𝖺 🚫")
        return

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
    sesion_charada["juego_en_curso"] = True

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
             f"𝗘𝗤𝗨𝗜𝗣𝗢 𝗥𝗢𝗝𝗢: {', '.join(nombres_rojo)}\n\n"
             f"𝗘𝗤𝗨𝗜𝗣𝗢 𝗔𝗭𝗨𝗟: {', '.join(nombres_azul)}\n\n"
             f"𝖤𝗅 𝗃𝗎𝖾𝗀𝗈 𝗌𝖾 𝗃𝗎𝖾𝗀𝖺 𝖾𝗇 𝟤 𝗋𝗈𝗇𝖽𝖺𝗌: 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝗎𝗇 𝖾𝗊𝗎𝗂𝗉𝗈, 𝗅𝗎𝖾𝗀𝗈 𝖾𝗅 𝗈𝗍𝗋𝗈. ¡𝖦𝖺𝗇𝖺 𝗊𝗎𝗂𝖾𝗇 𝗍𝖾𝗇𝗀𝖺 𝗆𝖺𝗌 𝗉𝗎𝗇𝗍𝗈𝗌 𝖺𝗅 𝖿𝗂𝗇𝖺𝗅!"
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
        text=f"𝗥𝗢𝗡𝗗𝗔 {numero_ronda}: 𝖩𝗎𝖾𝗀𝖺 𝖾𝗅 𝗘𝗤𝗨𝗜𝗣𝗢 {bando.upper()}.\n"
             f"𝗠𝗼𝗱𝗲𝗿𝗮𝗱𝗼𝗿 𝗲𝗹𝗲𝗴𝗶𝗱𝗼: {nombre_moderador}"
    )

    lista_texto = "\n".join([f"🔹 {p.upper()}" for p in palabras_elegidas])
    try:
        await context.bot.send_message(chat_id=id_moderador,
            text=f"¡𝗔𝗤𝗨Ɩ́ 𝗘𝗦𝗧𝗔́𝗡 𝗧𝗨𝗦 𝗣𝗔𝗟𝗔𝗕𝗥𝗔𝗦 𝗦𝗘𝗖𝗥𝗘𝗧𝗔𝗦ⵑ\n\n"
                 f"𝗖𝗔𝗧𝗘𝗚𝗢𝗥𝗜𝗔: {categoria.upper()}\n\n{lista_texto}\n\n"
                 f"¡𝖢𝗈𝗋𝗋𝖾 𝖺𝗅 𝗀𝗋𝗎𝗉𝗈! 𝖯𝗎𝖾𝖽𝖾𝗌 𝗎𝗌𝖺𝗋 𝖾𝗆𝗈𝗃𝗂𝗌 𝗒/𝗈 𝖻𝗋𝖾𝗏𝖾𝗌 𝖽𝖾𝗌𝖼𝗋𝗂𝗉𝖼𝗂𝗈𝗇𝖾𝗌 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾 𝗍𝗎 𝖾𝗊𝗎𝗂𝗉𝗈 𝖺𝖽𝗂𝗏𝗂𝗇𝖾. 𝖯𝗋𝗈𝖼𝗎𝗋𝖺 𝗇𝗈 𝖽𝖾𝖼𝗂𝗋 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺 𝗇𝗂 𝗉𝖺𝗋𝗍𝖾𝗌 𝗊𝗎𝖾 𝗅𝖺 𝖼𝗈𝗇𝖿𝗈𝗋𝗆𝖾𝗇")
    except Exception:
        await context.bot.send_message(chat_id=chat_id,
            text=f"𝖠𝗒, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 {nombre_moderador}. 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖺𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍.")
        return

    nombre_bando_jugando = sesion_charada["nombre_equipo_rojo"] if bando == "rojo" else sesion_charada["nombre_equipo_azul"]

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"𝗘𝗤𝗨𝗜𝗣𝗢 {nombre_bando_jugando.upper()}, {nombre_moderador} 𝘆𝗮 𝘁𝗶𝗲𝗻𝗲 𝘀𝘂𝘀 𝗽𝗮𝗹𝗮𝗯𝗿𝗮𝘀.\n"
             f"𝗧𝗶𝗲𝗻𝗲𝗻 𝟯𝟬 𝘀𝗲𝗴𝘂𝗻𝗱𝗼𝘀 𝗽𝗮𝗿𝗮 𝗽𝗿𝗲𝗽𝗮𝗿𝗮𝗿𝘀𝗲... ¡𝗲𝗹 𝗰𝗼𝗻𝘁𝗿𝗮𝗿𝗿𝗲𝗹𝗼𝗷 𝘆𝗮 𝗮𝗿𝗿𝗮𝗻𝗰𝗮!"
    )

    await asyncio.sleep(30)

    # Si en el medio de la espera alguien reinició/canceló el juego, no arrancamos el timer
    if not sesion_charada.get("juego_en_curso") or sesion_charada.get("moderador_id") != id_moderador:
        return

    sesion_charada["activa"] = True

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"¡𝗘𝗠𝗣𝗜𝗘𝗭𝗔 𝗘𝗟 𝗖𝗢𝗡𝗧𝗥𝗔𝗥𝗥𝗘𝗟𝗢𝗝ⵑ\n\n"
             f"𝗘𝗤𝗨𝗜𝗣𝗢 𝗔𝗖𝗧𝗨𝗔𝗟: {nombre_bando_jugando.upper()}\n"
             f"𝗠𝗢𝗗𝗘𝗥𝗔𝗗𝗢𝗥: {nombre_moderador}\n"
             f"𝗖𝗔𝗧𝗘𝗚𝗢𝗥𝗜𝗔: {categoria.upper()}\n\n"
             f"¡𝖳𝗂𝖾𝗇𝖾𝗇 𝟪𝟢 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋 𝗅𝖺𝗌 𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌!"
    )

    task_anterior = sesion_charada.get("reloj_task")
    if task_anterior and not task_anterior.done():
        task_anterior.cancel()

    sesion_charada["reloj_task"] = asyncio.create_task(reloj_charada(chat_id, context))

async def reloj_charada(chat_id, context):
    try:
        segundos = 80
        while segundos > 0 and sesion_charada["activa"]:
            await asyncio.sleep(1)
            segundos -= 1
    except asyncio.CancelledError:
        # Nos cancelaron porque arrancó una ronda nueva o terminó el juego, no hacemos nada
        return

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
        texto_faltantes = ", ".join(faltantes) if faltantes else "¡𝖥𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌, 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋𝗈𝗇 𝗍𝗈𝖽𝖺𝗌 𝗅𝖺𝗌 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌!"

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"¡𝗧𝗜𝗘𝗠𝗣𝗢 𝗔𝗚𝗢𝗧𝗔𝗗𝗢ⵑ\n\n"
                 f"𝖤𝗅 𝖾𝗊𝗎𝗂𝗉𝗈 {nombre_bando_jugando.upper()} 𝗅𝗈𝗀𝗋𝗈 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝗋 {adivinadas}/𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌.\n"
                 f"𝗙𝗮𝗹𝘁𝗮𝗿𝗼𝗻: {texto_faltantes}\n\n"
                 f"𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗚𝗟𝗢𝗕𝗔𝗟:\n"
                 f"{sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} 𝗉𝗍𝗌\n"
                 f"{sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} 𝗉𝗍𝗌\n\n"
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
            text=f"¡𝗘𝗠𝗣𝗔𝗧𝗘ⵑ 🤝\n\n"
                 f"𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗙𝗜𝗡𝗔𝗟:\n"
                 f"{sesion_charada['nombre_equipo_rojo']}: {pts_r} 𝗉𝗍𝗌\n"
                 f"{sesion_charada['nombre_equipo_azul']}: {pts_a} 𝗉𝗍𝗌\n\n"
                 f"¡𝖭𝗈 𝗁𝗎𝖻𝗈 𝗋𝖾𝗉𝖺𝗋𝗍𝗈 𝖽𝖾 𝖿𝗂𝖼𝗁𝖺𝗌, 𝖾𝗆𝗉𝖺𝗍𝖺𝗋𝗈𝗇!"
        )
    else:
        equipo_ganador_ids = sesion_charada["equipo_rojo"] if pts_r > pts_a else sesion_charada["equipo_azul"]
        nombre_ganador = sesion_charada["nombre_equipo_rojo"] if pts_r > pts_a else sesion_charada["nombre_equipo_azul"]

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"¡𝗝𝗨𝗘𝗚𝗢 𝗧𝗘𝗥𝗠𝗜𝗡𝗔𝗗𝗢ⵑ 🏆\n\n"
                 f"𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗙𝗜𝗡𝗔𝗟:\n"
                 f"{sesion_charada['nombre_equipo_rojo']}: {pts_r} 𝗉𝗍𝗌\n"
                 f"{sesion_charada['nombre_equipo_azul']}: {pts_a} 𝗉𝗍𝗌\n\n"
                 f"¡𝗘𝗤𝗨𝗜𝗣𝗢 𝗚𝗔𝗡𝗔𝗗𝗢𝗥: {nombre_ganador.upper()}!"
        )

        premio = sesion_puntos.get("premio_actual", {}).get("charada", 0)
        if premio > 0:
            for uid in equipo_ganador_ids:
                nombre = next((j["name"] for j in sesion_charada["jugadores"] if j["id"] == uid), str(uid))
                sumar_robux(uid, nombre, premio, f"𝗖𝗵𝗮𝗿𝗮𝗱𝗮: ({nombre_ganador})")

    task_previa = sesion_charada.get("reloj_task")
    if task_previa and not task_previa.done():
        task_previa.cancel()
    sesion_charada["reloj_task"] = None

    sesion_charada["activa"] = False
    sesion_charada["fase_registro"] = False
    sesion_charada["juego_en_curso"] = False

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

    texto_limpio = texto.strip().lower()
    if texto_limpio in sesion_charada["palabras_ronda"] and not sesion_charada["palabras_ronda"][texto_limpio]:
        sesion_charada["palabras_ronda"][texto_limpio] = True
        adivinadas_totales = sum(1 for v in sesion_charada["palabras_ronda"].values() if v)

        await update.message.reply_text(
            f"¡{nombre_usuario(update.effective_user)} 𝖺𝖽𝗂𝗏𝗂𝗇𝗈 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺!\n"
            f"𝗣𝗮𝗹𝗮𝗯𝗿𝗮: {texto_limpio.upper()}\n"
            f"{nombre_bando_jugando}: {adivinadas_totales}/𝟣𝟢 𝖺𝖼𝖾𝗋𝗍𝖺𝖽𝖺𝗌.")

        if adivinadas_totales == 10:
            sesion_charada["activa"] = False
            if bando_actual == "rojo":
                sesion_charada["puntos_rojo"] += 10
            else:
                sesion_charada["puntos_azul"] += 10
            await context.bot.send_message(chat_id=chat_id,
                text=f"¡𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗣𝗘𝗥𝗙𝗘𝗖𝗧𝗢ⵑ\n\n"
                     f"¡𝖤𝗅 𝖾𝗊𝗎𝗂𝗉𝗈 {nombre_bando_jugando.upper()} 𝖺𝖽𝗂𝗏𝗂𝗇𝗈 𝗅𝖺𝗌 𝟣𝟢 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌!\n\n"
                     f"𝗣𝗨𝗡𝗧𝗔𝗝𝗘 𝗚𝗟𝗢𝗕𝗔𝗟:\n"
                     f"{sesion_charada['nombre_equipo_rojo']}: {sesion_charada['puntos_rojo']} 𝗉𝗍𝗌\n"
                     f"{sesion_charada['nombre_equipo_azul']}: {sesion_charada['puntos_azul']} 𝗉𝗍𝗌")

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
            await query.message.reply_text(f"— {nombre_usuario(user)} se unio 𝅄 𖹭' ა")
