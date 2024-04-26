from gpytranslate import SyncTranslator
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from FallenRobot import dispatcher
from FallenRobot.modules.disable import DisableAbleCommandHandler

trans = SyncTranslator()


def totranslate(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text(
            "Mesajlara cavab verin və ya nəzərdə tutulan dilə tərcümə etmək üçün başqa dillərdən mesajlar yazın\n\n"
            "Example: `/tr en-hi` ingilis dilindən hind dilinə tərcümə etmək\n"
            "Or use: `/tr en` avtomatik aşkarlanması və ingilis dilinə tərcüməsi üçün.\n"
            "Baxmaq üçün bura klikləyin [Mövcud Dil Kodlarının siyahısı](https://te.legra.ph/LANGUAGE-CODES-05-23-2).",
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = trans(to_translate, sourcelang=source, targetlang=dest)
    reply = (
        f"<b>ᴛʀᴀɴsʟᴀᴛᴇᴅ ғʀᴏᴍ {source} ᴛᴏ {dest}</b> :\n"
        f"<code>{translation.text}</code>"
    )

    message.reply_text(reply, parse_mode=ParseMode.HTML)


__help__ = """
 ❍ /tr or /tl (dil kodu) uzun mesaja cavab olaraq
*Example:* 
 ❍ /tr en*:* bir şeyi ingilis dilinə tərcümə edir
 ❍ /tr hi-en*:* hindi dilini ingilis dilinə tərcümə edir

[ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs](https://te.legra.ph/LANGUAGE-CODES-05-23-2)
"""
__mod_name__ = "Tʀᴀɴsʟᴀᴛᴏʀ"

TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], totranslate, run_async=True)

dispatcher.add_handler(TRANSLATE_HANDLER)

__command_list__ = ["tr", "tl"]
__handlers__ = [TRANSLATE_HANDLER]
