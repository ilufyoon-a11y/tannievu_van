# =====================================================================
# LIBRERIAS IMPORTADAS
# =====================================================================

import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes)

# =====================================================================
# UTILIDADES COMPARTIDAS (Utils.py)
# =====================================================================

from utils import (
    GIF_BIENVENIDA, GIF_INFO, GIF_COMANDOS,
    sesion_puntos, nombre_usuario,
    cmd_new_session, cmd_wallet, cmd_spent, cmd_reset, cmd_saldo_final,
    detener_juegos, cmd_add, cmd_claim, cmd_export, cmd_import  
)

# =====================================================================
# JUEGOS DISPONIBLES
# =====================================================================

# ── BOX ✔️ ──────────────────────────────────────────────────────────

from box import (
    unirse_box, iniciar_box,
    manejar_botones_box,
    manejar_mensajes_box, adivinar_box,
    sesion_box, esperando_elementos,
    extraer_emojis,
)

# ── CARRERA - CASINO  ─────────────────────────────────────────────

from carrera import (
    cmd_carrera, cmd_apostar_carrera,
    cmd_start_carrera, cmd_cancelar_carrera,
)

# ── CACERIA ✔️  ──────────────────────────────────────────────────────

from caseria import (
    unirse_caseria, iniciar_caseria,
    manejar_botones_caseria,
)

# ── CHARADA ✔️  ──────────────────────────────────────────────────────

from charada import (
    unirse_charada, iniciar_charada,
    manejar_botones_charada,
    escuchar_charada_privado, escuchar_charada_grupo,
    sesion_charada,
)

# ── GUESS ✔️  ─────────────────────────────────────────────────────────

from guessong import (
    unirse_adivina, iniciar_adivina_juego,
    verificar_respuesta_musica, manejar_boton_unirse,
)

# ── JUMBLE ✔️ ─────────────────────────────────────────────────────

from anagrama import (
    cmd_anagrama, cmd_anagrama4, cmd_start_anagrama,
    manejar_botones_anagrama,
    escuchar_anagrama_privado, escuchar_anagrama_grupo,
    sesion_anagrama, esperando_moderador,
)

# ── PIRATA ✔️  ─────────────────────────────────────────────────────────  

from pirata import (
    unirse_pirata, iniciar_pirata,
    manejar_botones_pirata,
)

# ── SLOTS  ───────────────────────────────────────────────────────────  

from slots import cmd_slots, cmd_open_slots, cmd_spin, sesion_slots

# ── MAYOROMENOR - CASINO ─────────────────────────────────────────────

from mayoromenor import (
    cmd_mayoromenor, cmd_beat, cmd_out_card,
    sesion_mom,
)

# ── ZOMBIE ✔️  ──────────────────────────────────────────────────────────

from zombie import (
    unirse_zombie, iniciar_zombie,
    manejar_botones_zombie,
)

# =====================================================================
# COMANDOS GENERALES
# =====================================================================

async def start_bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_BIENVENIDA,
        caption=(
            "\n\n🌸ㅤㅤ⪩⪩ㅤㅤ𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝@ㅤㅤ!!ㅤㅤ☆ \n\n"
            "𝖵𝖺𝗇 𝖾𝗌 𝗎𝗇 𝖻𝗈𝗍 𝗊𝗎𝖾 𝗈𝖿𝗋𝖾𝖼𝖾 𝗎𝗇𝖺 𝗏𝖺𝗋𝗂𝖾𝖽𝖺𝖽 𝖽𝖾 𝗃𝗎𝖾𝗀𝗈𝗌, 𝖺𝗎𝗇 𝖾𝗌𝗍𝖺 𝖾𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗈 𝖽𝖾 𝗉𝗋𝗎𝖾𝖻𝖺 "
            "𝖺𝗌𝗂 𝗊𝗎𝖾 𝗌𝗂𝖾𝗇𝗍𝖾𝗍𝖾 𝖾𝗇 𝗍𝗈𝗍𝖺𝗅 𝗅𝗂𝖻𝖾𝗋𝗍𝖺𝖽 𝖽𝖾 𝖼𝗈𝗆𝗎𝗇𝗂𝖼𝖺𝗋 𝖼𝗎𝖺𝗅𝗊𝗎𝗂𝖾𝗋 𝗊𝗎𝖾𝗃𝖺/𝗌𝗎𝗀𝖾𝗋𝖾𝗇𝖼𝗂𝖺 𝖾𝗇 𝖾𝗅 𝖼𝗁𝖺𝗍 𝖽𝖾𝗅 𝖼𝖺𝗇𝖺𝗅. \n\n"
            "𝖤𝗌𝗉𝖾𝗋𝖺𝗆𝗈𝗌 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗃𝗎𝖾𝗀𝗈𝗌 𝖼𝗈𝗇𝗍𝖾𝗇𝗂𝖽𝗈𝗌 𝗌𝖾𝖺𝗇 𝖽𝖾 𝗌𝗎 𝖺𝗀𝗋𝖺𝖽𝗈! 💕"
        )
    )

PAGINAS_INFO = [
    # ── PAGINA 1  ───────────────────
    ("<b>🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦  ꒱꒱</b>\n\n"
     "<b>𝒊. 𝐁𝐨𝐱</b>\n\n"
     "𝖨𝗇𝗌𝗉𝗂𝗋𝖺𝖽𝗈 𝖾𝗇 𝖵𝖺𝗋𝗂𝖾𝗍𝗒 𝖲𝗁𝗈𝗐𝗌 𝗈𝖿 𝖬𝖾𝗆𝗈𝗋𝗂𝖾𝗌: 𝖯𝖺𝗋𝗍 𝟣, 𝗍𝖾𝗇𝖽𝗋𝖺𝗇 𝗌𝗈𝗅𝗈 𝟧 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌 𝗉𝖺𝗋𝖺 𝗆𝖾𝗆𝗈𝗋𝗂𝗓𝖺𝗋 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖽𝖾𝗇𝗍𝗋𝗈 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗃𝖺. ¡𝖠 𝗆𝖺𝗒𝗈𝗋 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝖽𝗈𝗌, 𝗆𝖺𝗒𝗈𝗋 𝗉𝗎𝗇𝗍𝖺𝗃𝖾!\n\n"
     "<blockquote>/box</blockquote>\n\n"
     "<b>𝒊𝒊. 𝐂𝐚𝐜𝐞𝐫𝐢𝐚</b>\n\n"
     "𝖴𝗇𝖺 𝗏𝖺𝗋𝗂𝖺𝖼𝗂𝗈𝗇 𝖽𝖾 𝖡𝗂𝗇𝗀𝗈, 𝗌𝖾 𝗉𝗋𝖾𝗌𝖾𝗇𝗍𝖺𝗋𝖺 𝗎𝗇 𝗍𝖺𝖻𝗅𝖾𝗋𝗈 𝗒 𝖼𝖺𝖽𝖺 𝗎𝗇𝗈 𝗈𝖻𝗍𝖾𝗇𝖽𝗋𝖺 𝗎𝗇𝖺 𝗉𝗅𝖺𝗇𝗍𝗂𝗅𝗅𝖺 𝖼𝗈𝗇 𝟨 𝗈𝖻𝗃𝖾𝗍𝗈𝗌. ¡𝖤𝗅 𝗉𝗋𝗂𝗆𝖾𝗋 𝖾𝗇 𝖾𝗇𝖼𝗈𝗇𝗍𝗋𝖺𝗋 𝗅𝗈𝗌 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝖾𝗇 𝖾𝗅 𝗍𝖺𝖻𝗅𝖾𝗋𝗈 𝗒 𝖼𝗈𝗆𝗉𝗅𝖾𝗍𝖺𝗋 𝗌𝗎 𝖼𝖺𝗋𝗍𝗂𝗅𝗅𝖺 𝗀𝖺𝗇𝖺!\n\n"
     "<blockquote>/hunt</blockquote>\n\n"),
     # ── PAGINA 2  ───────────────────
    ("<b>🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦  ꒱꒱</b>\n\n"
     "<b>𝒊𝒊𝒊. 𝐂𝐡𝐚𝐫𝐚𝐝𝐚</b>\n\n"
     "𝖱𝖾𝗉𝗋𝖾𝗌𝖾𝗇𝗍𝖺 𝖿𝗋𝖺𝗌𝖾𝗌 𝗈 𝗉𝖾𝗅ı́𝖼𝗎𝗅𝖺𝗌 𝖼𝗈𝗇 𝗉𝖺𝗅𝖺𝖻𝗋𝖺𝗌 𝗒 𝖾𝗆𝗈𝗃𝗂𝗌. ¡𝖧𝖺𝗓 𝗊𝗎𝖾 𝗍𝗎 𝖾𝗊𝗎𝗂𝗉𝗈 𝖺𝖽𝗂𝗏𝗂𝗇𝖾 𝗅𝖺 𝗆𝖺𝗒𝗈𝗋 𝖼𝖺𝗇𝗍𝗂𝖽𝖺𝖽 𝖺𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝖾𝗅 𝗍𝗂𝖾𝗆𝗉𝗈 𝖺𝖼𝖺𝖻𝖾!\n\n"
     "<blockquote>/charada</blockquote>\n\n"
     "<b>𝒊𝒗. 𝐆𝐮𝐞𝐬𝐬 𝐒𝐨𝐧𝐠</b>\n\n"
     "𝖨𝖽𝖾𝗇𝗍𝗂𝖿𝗂𝖼𝖺 𝖾𝗅 𝗇𝗈𝗆𝖻𝗋𝖾 𝖽𝖾 𝗅𝖺 𝖼𝖺𝗇𝖼𝗂𝗈𝗇 𝖺 𝗉𝖺𝗋𝗍𝗂𝗋 𝖽𝖾 𝗉𝗂𝗌𝗍𝖺𝗌 𝖽𝖾 𝟦 𝗌𝖾𝗀𝗎𝗇𝖽𝗈𝗌. ¡𝖠 𝗆𝖺𝗒𝗈𝗋 𝖼𝖺𝗇𝖼𝗂𝗈𝗇𝖾𝗌 𝖺𝖽𝗂𝗏𝗂𝗇𝖺𝖽𝖺𝗌, 𝗆𝖺𝗒𝗈𝗋 𝗉𝗎𝗇𝗍𝖺𝗃𝖾!\n\n"
     "<blockquote>/guess</blockquote>\n\n"
     "<b>𝒗. 𝐉𝐮𝐦𝐛𝐥𝐞</b>\n\n"
     "𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗅𝖺 𝗉𝖺𝗅𝖺𝖻𝗋𝖺 𝗊𝗎𝖾 𝖽𝗂𝗈 𝗂𝗇𝗂𝖼𝗂𝗈 𝖺𝗅 𝖾𝗇𝗋𝖾𝖽𝗈 𝖽𝖾 𝗅𝖾𝗍𝗋𝖺𝗌\n\n"
     "<blockquote>/jumble</blockquote>\n\n"),
     # ── PAGINA 3  ───────────────────
    ("<b>🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦  ꒱꒱</b>\n\n"
     "<b>𝒗𝒊. 𝐒𝐚𝐥𝐭𝐚 𝐏𝐢𝐫𝐚𝐭𝐚</b>\n\n"
     "𝖨𝗇𝗌𝖾𝗋𝗍𝖺 𝖾𝗌𝗉𝖺𝖽𝖺𝗌 𝖾𝗇 𝗅𝖺𝗌 𝗋𝖺𝗇𝗎𝗋𝖺𝗌 𝖽𝖾 𝗎𝗇 𝖻𝖺𝗋𝗋𝗂𝗅 𝖽𝗈𝗇𝖽𝖾 𝗌𝖾 𝖾𝗇𝖼𝗎𝖾𝗇𝗍𝗋𝖺 𝖾𝗌𝖼𝗈𝗇𝖽𝗂𝖽𝗈 𝖾𝗅 𝗉𝗂𝗋𝖺𝗍𝖺 𝗌𝖾𝗀𝗎𝗇 𝗍𝗎 𝗍𝗎𝗋𝗇𝗈. ¡𝖳𝗋𝖺𝗍𝖺 𝖽𝖾 𝗇𝗈 𝗌𝖾𝗋 𝗍𝗎 𝖾𝗅 𝗊𝗎𝖾 𝗅𝗈 𝗁𝖺𝗀𝖺𝗌 𝗏𝗈𝗅𝖺𝗋 𝗉𝗈𝗋 𝗅𝗈𝗌 𝖺𝗂𝗋𝖾𝗌!\n\n"
     "<blockquote>/pirata</blockquote>\n\n"
     "<b>𝒗𝒊𝒊. 𝐙𝐨𝐦𝐛𝐢𝐞</b>\n\n"
     "𝖴𝗇𝖺 𝖾𝗑𝖼𝗎𝗋𝗌𝗂𝗈𝗇 𝗌𝖾 𝗏𝗂𝗈 𝗂𝗇𝗍𝖾𝗋𝗋𝗎𝗆𝗉𝗂𝖽𝖺 𝗉𝗈𝗋 𝗎𝗇 𝗏𝗂𝗋𝗎𝗌 𝗓𝗈𝗆𝖻𝗂𝖾 𝗒 𝖽𝖾𝖻𝖾𝗇 𝖾𝗌𝗉𝖾𝗋𝖺𝗋 𝗁𝖺𝗌𝗍𝖺 𝗊𝗎𝖾 𝗅𝗈𝗌 𝗋𝖾𝗌𝖼𝖺𝗍𝖾𝗇, 𝗌𝗈𝗅𝗈 𝗌𝖾 𝗉𝗎𝖾𝖽𝖾𝗇 𝗋𝖾𝗌𝗀𝗎𝖺𝗋𝖽𝖺𝗋 𝖾𝗇 𝗎𝗇 𝖺𝗎𝗍𝗈𝖻𝗎𝗌, 𝗉𝖾𝗋𝗈 𝗎𝗇 𝗂𝗇𝖿𝖾𝖼𝗍𝖺𝖽𝗈 𝗌𝖾 𝖼𝗈𝗅𝗈 𝗒 𝖺𝗍𝖺𝖼𝖺 𝗉𝗈𝗋 𝗅𝖺𝗌 𝗇𝗈𝖼𝗁𝖾𝗌 𝖼𝗎𝖺𝗇𝖽𝗈 𝗅𝖺𝗌 𝗅𝗎𝖼𝖾𝗌 𝗌𝖾 𝖺𝗉𝖺𝗀𝖺𝗇 𝗉𝗈𝗋 𝗌𝖾𝗀𝗎𝗋𝗂𝖽𝖺𝖽 ¿𝖯𝗈𝖽𝗋𝖺𝗇 𝗌𝗈𝖻𝗋𝖾𝗏𝗂𝗏𝗂𝗋?\n\n"
     "<blockquote>/zombie</blockquote>\n\n"),
    # ── PAGINA 4  ───────────────────
    ("<b>🐋    𖹭𖹭ㅤ𝗝𝗨𝗘𝗚𝗢𝗦 𝗗𝗜𝗦𝗣𝗢𝗡𝗜𝗕𝗟𝗘𝗦  ꒱꒱</b>\n\n"
     "<blockquote>¡𝖯𝗋𝗈𝖼𝗎𝗋𝖺 𝗍𝖾𝗇𝖾𝗋 𝖿𝗂𝖼𝗁𝖺𝗌 𝗉𝖺𝗋𝖺 𝗉𝗈𝖽𝖾𝗋 𝗃𝗎𝗀𝖺𝗋! 𝖯𝖺𝗋𝖺 𝖼𝗈𝗇𝗌𝗎𝗅𝗍𝖺𝗋 𝗍𝗎 𝗌𝖺𝗅𝖽𝗈 𝗎𝗌𝖺 /wallet</blockquote>\n\n"
     "<b>𝒊. 𝐌𝐚𝐲𝐨𝐫 𝐨 𝐦𝐞𝐧𝐨𝐫</b>\n\n"
     "𝖠𝖽𝗂𝗏𝗂𝗇𝖺 𝗌𝗂 𝗅𝖺 𝗌𝗂𝗀𝗎𝗂𝖾𝗇𝗍𝖾 𝖼𝖺𝗋𝗍𝖺 𝖽𝖾 𝗅𝖺 𝖻𝖺𝗋𝖺𝗃𝖺 𝗌𝖾𝗋𝖺 𝗆𝖺𝗒𝗈𝗋 𝗈 𝗆𝖾𝗇𝗈𝗋 𝗊𝗎𝖾 𝗅𝖺 𝖺𝖼𝗍𝗎𝖺𝗅.\n\n"
     "<blockquote>/mom</blockquote>\n\n"
     "<b>𝒊𝒊. 𝐂𝐚𝐫𝐫𝐞𝐫𝐚</b>\n\n"
     "𝖠𝗇𝗍𝖾𝗌 𝖽𝖾 𝗊𝗎𝖾 𝗅𝗈𝗌 𝖼𝗈𝗋𝗋𝖾𝖽𝗈𝗋𝖾𝗌 𝗌𝖾 𝗆𝗎𝖾𝗏𝖺𝗇, 𝗅𝗈𝗌 𝗃𝗎𝗀𝖺𝖽𝗈𝗋𝖾𝗌 𝖺𝗉𝗎𝖾𝗌𝗍𝖺𝗇 𝗉𝗈𝗋 𝗅𝖺 𝗆𝖺𝗌𝖼𝗈𝗍𝖺 𝗊𝗎𝖾 𝖼𝗋𝖾𝖾𝗇 𝗊𝗎𝖾 𝗅𝗅𝖾𝗀𝖺𝗋𝖺́ 𝗉𝗋𝗂𝗆𝖾𝗋𝗈 𝖺 𝗅𝖺 𝗆𝖾𝗍𝖺\n\n"
     "<blockquote>/carrera</blockquote>\n\n"
     "<b>𝒊𝒊𝒊. 𝐒𝐥𝐨𝐭𝐬</b>\n\n"
     "𝖧𝖺𝗓 𝗀𝗂𝗋𝖺𝗋 𝗅𝗈𝗌 𝗋𝗈𝖽𝗂𝗅𝗅𝗈𝗌 𝗒 𝖺𝗅𝗂𝗇𝖾𝖺 𝗅𝗈𝗌 𝗌ı́𝗆𝖻𝗈𝗅𝗈𝗌 𝗀𝖺𝗇𝖺𝖽𝗈𝗋𝖾𝗌. ¡𝖴𝗇𝖺 𝖼𝗈𝗆𝖻𝗂𝗇𝖺𝖼𝗂𝗈́𝗇 𝗉𝖾𝗋𝖿𝖾𝖼𝗍𝖺 𝗉𝗈𝖽𝗋ı́𝖺 𝗁𝖺𝖼𝖾𝗋𝗍𝖾 𝗀𝖺𝗇𝖺𝗋 𝖾𝗅 𝗀𝗋𝖺𝗇 𝗃𝖺𝖼𝗄𝗉𝗈𝗍!\n\n"
     "<blockquote>/jackpot</blockquote>\n\n")
]

def botones_pagina(pagina: int) -> InlineKeyboardMarkup:
    total = len(PAGINAS_INFO)
    botones = []
    fila = []
    if pagina > 0:
        fila.append(InlineKeyboardButton("←", callback_data=f"info_pag_{pagina - 1}"))
    if pagina < total - 1:
        fila.append(InlineKeyboardButton("→", callback_data=f"info_pag_{pagina + 1}"))
    if fila:
        botones.append(fila)
    return InlineKeyboardMarkup(botones)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=GIF_INFO,
        caption=PAGINAS_INFO[0],
        reply_markup=botones_pagina(0),
        parse_mode="HTML"
    )

async def manejar_paginas_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "info_noop":
        return
    pagina = int(query.data.split("_")[-1])
    await query.edit_message_caption(
        caption=PAGINAS_INFO[pagina],
        reply_markup=botones_pagina(pagina),
        parse_mode="HTML"
    )

# =====================================================================
# HANDLER DE MENSAJES — despacha según el contexto activo
# =====================================================================

async def manejar_mensajes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    user_name = nombre_usuario(update.effective_user)
    chat_type = update.effective_chat.type
    chat_id = update.effective_chat.id
    texto = update.message.text.strip() if update.message.text else ""
    if not texto and update.message.dice:
        texto = update.message.dice.emoji

    # ── PRIVADO: moderador anagrama escribe categoría/palabras ──
    if chat_type == "private" and user_id in esperando_moderador:
        await escuchar_anagrama_privado(update, context, user_id, texto)
        return

    # ── PRIVADO: encubridor box envía emojis ──
    if chat_type == "private" and user_id in esperando_elementos:
        await manejar_mensajes_box(update, context)
        return

    # ── PRIVADO: moderador charada envía nombre de equipo ──
    if chat_type == "private":
        await escuchar_charada_privado(update, context, user_id, texto)
        return

    # ── BOX: adivinar emojis en el grupo ──
    if chat_id in sesion_box and sesion_box[chat_id].get("activa"):
        await adivinar_box(update, context)
        return

    # ── CHARADA: adivinar palabras en el grupo ──
    await escuchar_charada_grupo(update, context, user_id, texto, chat_id)
    await escuchar_anagrama_grupo(update, context, user_id, texto, chat_id)

# =====================================================================
# HANDLER DE BOTONES — despacha según callback_data
# =====================================================================

async def manejar_botones_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data if query else ""

    if data.startswith("info_"):
        await manejar_paginas_info(update, context)
    elif data in ("unirme_zombie_click",) or data.startswith("morder:") or data.startswith("voto_z:"):
        await manejar_botones_zombie(update, context)
    elif data == "unirme_caseria_click" or data.startswith("caseria_tablero_"):
        await manejar_botones_caseria(update, context)
    elif data == "unirme_box_click":
        await manejar_botones_box(update, context)
    elif data == "unirme_charada_click":
        await manejar_botones_charada(update, context)
    elif data == "unirme_pirata_click" or data.startswith("pirata_clic_") or data.startswith("ranura_ya_usada_"):
        await manejar_botones_pirata(update, context)
    elif data == "unirme_adivina_click":
        await manejar_boton_unirse(update, context)
    elif data.startswith("mu_"):
        await verificar_respuesta_musica(update, context)
    elif data == "unirme_anagrama_click":
        await manejar_botones_anagrama(update, context)

# =====================================================================
# ARRANQUE
# =====================================================================

if __name__ == '__main__':
    token_bot = os.environ.get('TOKEN')
    if not token_bot:
        raise ValueError("❌ ¡Error crítico! No se encontró la variable 'TOKEN'.")

    print("🤖 Iniciando bot de Telegram con run_polling...")
    application = ApplicationBuilder().token(token_bot).build()

    # Comandos generales
    application.add_handler(CommandHandler("start",   start_bienvenida))
    application.add_handler(CommandHandler("info",    info))
    application.add_handler(CommandHandler("off_van", detener_juegos))

    # Cacería
    application.add_handler(CommandHandler("hunt",       unirse_caseria))
    application.add_handler(CommandHandler("start_hunt", iniciar_caseria))

    # Zombie
    application.add_handler(CommandHandler("zombie",       unirse_zombie))
    application.add_handler(CommandHandler("start_zombie", iniciar_zombie))

    # Box
    application.add_handler(CommandHandler("box",       unirse_box))
    application.add_handler(CommandHandler("start_box", iniciar_box))

    # Charada
    application.add_handler(CommandHandler("charada",       unirse_charada))
    application.add_handler(CommandHandler("start_charada", iniciar_charada))

    # Pirata
    application.add_handler(CommandHandler("pirata",       unirse_pirata))
    application.add_handler(CommandHandler("start_pirata", iniciar_pirata))

    # Adivina la canción
    application.add_handler(CommandHandler("guess",       unirse_adivina))
    application.add_handler(CommandHandler("start_guess", iniciar_adivina_juego))

    # Mayor o Menor 🃏
    application.add_handler(CommandHandler("mom",      cmd_mayoromenor))
    application.add_handler(CommandHandler("beat",     cmd_beat))
    application.add_handler(CommandHandler("out_card", cmd_out_card))

    # Slots 🎰
    application.add_handler(CommandHandler("jackpot", cmd_open_slots))
    application.add_handler(CommandHandler("apostar", cmd_slots))
    application.add_handler(CommandHandler("girar",   cmd_spin))

    # Anagrama 🔀
    application.add_handler(CommandHandler("jumble",       cmd_anagrama))
    application.add_handler(CommandHandler("jumble4",      cmd_anagrama4))
    application.add_handler(CommandHandler("start_jumble", cmd_start_anagrama))
    application.add_handler(CommandHandler("carrera",          cmd_carrera))
    application.add_handler(CommandHandler("rider",  cmd_apostar_carrera))
    application.add_handler(CommandHandler("start_carrera",    cmd_start_carrera))
    application.add_handler(CommandHandler("cancelar_carrera", cmd_cancelar_carrera))

    # Robux / Wallet
    application.add_handler(CommandHandler("new_session", cmd_new_session))
    application.add_handler(CommandHandler("wallet",      cmd_wallet))
    application.add_handler(CommandHandler("spent",       cmd_spent))
    application.add_handler(CommandHandler("clean",       cmd_reset))
    application.add_handler(CommandHandler("import",  cmd_import))
    application.add_handler(CommandHandler("export",  cmd_export))
    application.add_handler(CommandHandler("claim",  cmd_claim))
    application.add_handler(CommandHandler("add",  cmd_add))
    application.add_handler(CommandHandler("pay",  cmd_saldo_final))

    # Handlers generales
    application.add_handler(CallbackQueryHandler(manejar_botones_main))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensajes))
    application.add_handler(MessageHandler(filters.Dice.ALL, manejar_mensajes))

    application.run_polling(drop_pending_updates=True)
