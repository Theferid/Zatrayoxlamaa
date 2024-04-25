import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from FallenRobot import BOT_NAME, BOT_USERNAME, dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler


def handwrite(update: Update, context: CallbackContext):
    message = update.effective_message
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:
        text = update.effective_message.text.split(None, 1)[1]
    m = message.reply_text("Mətnin yazılması...")
    req = requests.get(f"https://api.sdbots.tk/write?text={text}").url
    message.reply_photo(
        photo=req,
        caption=f"""
Uğurla Yazılı Mətn 💘

✨ **Müəllif :** [{BOT_NAME}](https://t.me/{BOT_USERNAME})
🥀 **tərəfindən tələb edilmişdir :** {update.effective_user.first_name}
❄ **Link :** `{req}`""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("• ᴛᴇʟᴇɢʀᴀᴩʜ •", url=req),
                ],
            ]
        ),
    )
    m.delete()


__help__ = """
 Verilmiş mətni qələmlə ağ vərəqə yazır 🖊

❍ /write <text> *:*Verilmiş mətni yazır.
"""

WRITE_HANDLER = DisableAbleCommandHandler("write", handwrite, run_async=True)
dispatcher.add_handler(WRITE_HANDLER)

__mod_name__ = "WʀɪᴛᴇTᴏᴏʟ"

__command_list__ = ["write"]
__handlers__ = [WRITE_HANDLER]
