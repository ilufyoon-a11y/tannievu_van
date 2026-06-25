import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import sesion_puntos, sumar_robux, nombre_usuario, GIF_AHORCADO, GIF_ERROR, GIF_LETRISTA, GIF_RECHAZADO, dibujar_pantalla_code

# ================= DICCIONARIO =================

sesion_cipher = {
    "jugadores": [],
    "activa": False,
    "codigo": "",
    "numeros_adivinadas": [],
    "moderador_id": None,
    "ultimo_moderador_id": None,
}
esperando_code = {}   # user_id -> chat_id

# ================= CODIGO PRINCIPAL =================

async def unirse_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sesion_cipher["jugadores"] = []
    sesion_cipher["activa"] = False
    sesion_cipher["codigo"] = ""
    sesion_cipher["numeros_adivinadas"] = []
    sesion_cipher["moderador_id"] = None

    boton = InlineKeyboardButton("੭੭ㅤㅤ𝐔𝐍𝐈𝐑𝐌𝐄ㅤㅤ!¡", callback_data="unirme_cipher_click")
    await update.message.reply_photo(
        photo=GIF_AHORCADO,
        caption=" ៹ ࣪  📝 ¡𝖩𝗎𝗀𝗎𝖾𝗆𝗈𝗌 𝖺 Cipher! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝖻𝗈𝗍𝗈𝗇 𝗉𝖺𝗋𝖺 𝗎𝗇𝗂𝗋𝗍𝖾  ֪  𓂃",
        reply_markup=InlineKeyboardMarkup([[boton]])
    )

async def iniciar_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    args = context.args or []
    if args:
        try:
            sesion_puntos["premio_actual"]["cipher"] = int(args[0])
        except ValueError:
            pass

    if len(sesion_cipher["jugadores"]) < 2:
        await update.message.reply_photo(photo=GIF_ERROR,
            caption="𝖲𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖺𝗇 𝗆𝗂𝗇𝗂𝗆𝗈 𝟤 𝗉𝖾𝗋𝗌𝗈𝗇𝖺𝗌 𝗉𝖺𝗋𝖺 𝗃𝗎𝗀𝖺𝗋.")
        return

    candidatos = list(sesion_cipher["jugadores"])
    ultimo_mod = sesion_cipher.get("ultimo_moderador_id")
    if ultimo_mod and len(candidatos) > 1:
        filtrados = [j for j in candidatos if j["id"] != ultimo_mod]
        moderador = random.choice(filtrados if filtrados else candidatos)
    else:
        moderador = random.choice(candidatos)

    sesion_cipher["jugadores"].remove(moderador)
    sesion_cipher.update({
        "moderador_id": moderador["id"],
        "ultimo_moderador_id": moderador["id"],
        "activa": True,
    })

    esperando_code[moderador["id"]] = chat_id
    await update.message.reply_text("˒˓  ¡𝖬𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋 𝖾𝗅𝖾𝗀𝗂𝖽𝗈! 𝖤𝗌𝗉𝖾𝗋𝖺𝗇𝖽𝗈 𝗊𝗎𝖾 𝖾𝗇𝗏𝗂𝖾 𝖾𝗅 𝖼𝗈́𝖽𝗂𝗀𝗈  ᨦᨩ")

    try:
        await context.bot.send_photo(
            chat_id=moderador["id"],
            photo=GIF_LETRISTA,
            caption="¡𝖤𝗇 𝗁𝗈𝗋𝖺 𝖻𝗎𝖾𝗇𝖺, 𝗍𝖾 𝗍𝗈𝖼𝖺 𝗌𝖾𝗋 𝖾𝗅 𝗆𝗈𝖽𝖾𝗋𝖺𝖽𝗈𝗋! 𝖯𝗈𝗋 𝖿𝖺𝗏𝗈𝗋, 𝖾𝗇𝗏𝗂́𝖺 𝖾𝗅 𝖼𝗈́𝖽𝗂𝗀𝗈 de 4 digitos 𝗊𝗎𝖾 𝖽𝖾𝗌𝖾𝖾𝗌 𝗊𝗎𝖾 𝖺𝖽𝗂𝗏𝗂𝗇𝖾𝗇."
        )
    except Exception:
        await context.bot.send_photo(
            chat_id=chat_id, photo=GIF_RECHAZADO,
            caption=f"𝖴𝗉𝗌, 𝗇𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾 𝖾𝗇𝗏𝗂𝖺𝗋 𝗆𝖾𝗇𝗌𝖺𝗃𝖾 𝖺 ({moderador['name']}). 𝖠𝗌𝖾𝗀𝗎𝗋𝖺𝗍𝖾 𝖽𝖾 𝗁𝖺𝖻𝖾𝗋 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈 𝖾𝗅 𝖻𝗈𝗍 𝖾𝗇 𝗉𝗋𝗂𝗏𝖺𝖽𝗈."
        )
        sesion_cipher["activa"] = False

# ================= MANEJO DE BOTONES =================

async def manejar_botones_cipher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat_id = query.message.chat.id

    if query.data == "unirme_cipher_click":
        await query.answer()
        if sesion_cipher["activa"]:
            await query.answer("¡𝖫𝗈 𝗌𝗂𝖾𝗇𝗍𝗈, 𝗒𝖺 𝗁𝖺𝗒 𝗎𝗇𝖺 𝗋𝗈𝗇𝖽𝖺 𝖾𝗇 𝖼𝗎𝗋𝗌𝗈!", show_alert=True)
            return
        if not any(j["id"] == user.id for j in sesion_cipher["jugadores"]):
            sesion_cipher["jugadores"].append({"id": user.id, "name": nombre_usuario(user)})
            await query.message.reply_text(f"📝 ֹ  {nombre_usuario(user)} se unió al cipher 𓂃")
