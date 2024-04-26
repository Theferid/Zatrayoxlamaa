from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown

import FallenRobot.modules.sql.rules_sql as sql
from FallenRobot import dispatcher
from FallenRobot.modules.helper_funcs.chat_status import connection_status, user_admin
from FallenRobot.modules.helper_funcs.string_handling import markdown_parser


@connection_status
def get_rules(update: Update, context: CallbackContext):
    args = context.args
    here = args and args[0] == "here"
    chat_id = update.effective_chat.id
    # connection_status sets update.effective_chat
    real_chat = update.effective_message.chat
    dest_chat = real_chat.id if here else None
    send_rules(update, chat_id, real_chat.type == real_chat.PRIVATE or here, dest_chat)


# Do not async - not from a handler
def send_rules(update, chat_id, from_pm=False, dest_chat=None):
    bot = dispatcher.bot
    user = update.effective_user  # type: Optional[User]
    reply_msg = update.message.reply_to_message
    dest_chat = dest_chat or user.id
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı" and from_pm:
            bot.send_message(
                dest_chat,
                "Bu söhbət üçün qaydalar qısayolu düzgün qurulmayıb! Adminlərdən soruşun"
                "bunu düzəldin.\nOla bilsin ID-də defisi unudublar",
            )
            return
        else:
            raise

    rules = sql.get_rules(chat_id)
    text = f"üçün qaydalar *{escape_markdown(chat.title)}* are:\n\n{rules}"

    if from_pm and rules:
        bot.send_message(
            dest_chat,
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif from_pm:
        bot.send_message(
            dest_chat,
            "Qrup adminləri bu söhbət üçün hələ heç bir qayda təyin etməyiblər. "
            "Bu, yəqin ki, o demək deyil ki, qanuna zidd deyil...!",
        )
    elif rules and reply_msg:
        reply_msg.reply_text(
            "Qaydaları əldə etmək üçün aşağıdakı düymələrə klikləyin.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• Qaydalar •",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    elif rules:
        update.effective_message.reply_text(
            "Qaydaları əldə etmək üçün aşağıdakı düymələrə klikləyin.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• Qaydalar •",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    else:
        update.effective_message.reply_text(
            "Qrup adminləri bu söhbət üçün hələ heç bir qayda təyin etməyiblər. "
            "Bu, yəqin ki, o demək deyil ki, qanuna zidd deyil...!",
        )


@connection_status
@user_admin
def set_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    raw_text = msg.text
    args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
    txt = entities = None
    if len(args) == 2:
        txt = args[1]
        entities = msg.parse_entities()
    elif msg.reply_to_message:
        txt = msg.reply_to_message.text
        entities = msg.reply_to_message.parse_entities()
    if txt:
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(
            txt,
            entities=entities,
            offset=offset,
        )

        sql.set_rules(chat_id, markdown_rules)
        update.effective_message.reply_text("Bu qrup üçün qaydaları uğurla təyin edin.")
    else:
        update.effective_message.reply_text("Heç bir qayda yoxdur?")


@connection_status
@user_admin
def clear_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    update.effective_message.reply_text("Qaydalar uğurla silindi!")


def __stats__():
    return f"• {sql.num_chats()} qrupların qaydaları var."


def __import_data__(chat_id, data):
    # set chat rules
    rules = data.get("info", {}).get("rules", "")
    sql.set_rules(chat_id, rules)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"Bu söhbətin qaydaları müəyyən edilib: `{bool(sql.get_rules(chat_id))}`"


__help__ = """
 ‣ `/rules`*:* bu söhbətin qaydalarını əldə edin.
 ‣ `/rules here`*:* bu söhbətin qaydalarını əldə edin, lakin onu söhbətə göndərin.
*Yalnız adminlər:*
 ‣ `/setrules <your rules here>`*:* bu söhbət üçün qaydaları təyin edin.
 ‣ `/clearrules`*:* bu söhbət üçün qaydaları təmizləyin.
"""

__mod_name__ = "Rᴜʟᴇs"

GET_RULES_HANDLER = CommandHandler("rules", get_rules, run_async=True)
SET_RULES_HANDLER = CommandHandler("setrules", set_rules, run_async=True)
RESET_RULES_HANDLER = CommandHandler("clearrules", clear_rules, run_async=True)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
