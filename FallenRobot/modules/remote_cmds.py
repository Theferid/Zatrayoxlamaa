from telegram import ChatPermissions, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from FallenRobot import LOGGER, dispatcher
from FallenRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_bot_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from FallenRobot.modules.helper_funcs.extraction import extract_user_and_text
from FallenRobot.modules.helper_funcs.filters import CustomFilters

RBAN_ERRORS = {
    "İstifadəçi söhbətin idarəçisidir",
    "Çat tapılmadı",
    "Çat üzvünü məhdudlaşdırmaq/məhdudiyyəti aradan qaldırmaq üçün kifayət qədər hüquqlar yoxdur",
    "İstifadəçi_iştirakçı_deyil",
    "Peer_id_invalid",
    "Qrup söhbəti deaktiv edildi",
    "Onu əsas qrupdan vurmaq üçün istifadəçinin dəvətçisi olmaq lazımdır",
    "Chat_admin_tələb_olunur",
    "Yalnız əsas qrupun yaradıcısı qrup administratorlarını yumruqlaya bilər",
    "Kanal_özəl",
    "Çatda yox",
}

RUNBAN_ERRORS = {
    "İstifadəçi söhbətin idarəçisidir",
    "Çat tapılmadı",
    "Çat üzvünü məhdudlaşdırmaq/məhdudiyyəti aradan qaldırmaq üçün kifayət qədər hüquqlar yoxdur",
    "User_not_participant",
    "Peer_id_invalid",
    "Qrup söhbəti deaktiv edildi",
    "Əsas qrupdan onu vurmaq üçün istifadəçinin dəvətçisi olmaq lazımdır",
    "Söhbət_admin_tələb olunur",
    "Yalnız əsas qrupun yaradıcısı qrup administratorlarını yumruqlaya bilər",
    "Channel_private",
    "Çatda yox",
}

RKICK_ERRORS = {
    "İstifadəçi söhbətin idarəçisidir",
    "Söhbət tapılmadı",
    "Çat üzvünü məhdudlaşdırmaq/məhdudiyyəti ləğv etmək üçün kifayət qədər hüquqlar yoxdur",
    "User_not_participant",
    "Peer_id_invalid",
    "Qrup söhbəti deaktiv edildi",
    "Əsas qrupdan onu vurmaq üçün istifadəçinin dəvətçisi olmaq lazımdır",
    "Söhbət_admin_tələb olunur",
    "Yalnız əsas qrupun yaradıcısı qrup administratorlarını yumruqlaya bilər",
    "Channel_private",
    "Çatda yox",
}

RMUTE_ERRORS = {
    "İstifadəçi söhbətin idarəçisidir",
    "Söhbət tapılmadı",
    "Çat üzvünü məhdudlaşdırmaq/məhdudiyyəti ləğv etmək üçün kifayət qədər hüquqlar yoxdur",
    "User_not_participant",
    "Peer_id_invalid",
    "Qrup söhbəti deaktiv edildi",
    "Əsas qrupdan onu vurmaq üçün istifadəçinin dəvətçisi olmaq lazımdır",
    "Chat_admin_required",
    "Yalnız əsas qrupun yaradıcısı qrup administratorlarını yumruqlaya bilər",
    "Channel_private",
    "Çatda yox",
}

RUNMUTE_ERRORS = {
    "İstifadəçi söhbətin idarəçisidir",
    "Söhbət tapılmadı",
    "Çat üzvünü məhdudlaşdırmaq/məhdudiyyəti ləğv etmək üçün kifayət qədər hüquqlar yoxdur",
    "İstifadəçi_iştirakçı deyil",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Əsas qrupdan onu vurmaq üçün istifadəçinin dəvətçisi olmaq lazımdır",
    "Chat_admin_required",
    "Yalnız əsas qrupun yaradıcısı qrup administratorlarını yumruqlaya bilər",
    "Channel_private",
    "Çatda yox",
}


@bot_admin
def rban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Siz söhbətə/istifadəçiyə istinad etmirsiniz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        )
        return
    elif not chat_id:
        message.reply_text("Siz deyəsən söhbətə istinad etmirsiniz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı":
            message.reply_text(
                "Çat tapılmadı! Etibarlı söhbət ID-si daxil etdiyinizə əmin olun və mən bu söhbətin bir hissəsiyəm."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("Üzr istəyirəm, amma bu, şəxsi söhbətdir!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "Mən orada insanları məhdudlaşdıra bilmərəm! Əmin olun ki, mən adminəm və istifadəçiləri qadağan edə bilərəm."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Bu istifadəçini tapa bilmirəm")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Çox istərdim ki, adminlərə qadağa qoyulsun...")
        return

    if user_id == bot.id:
        message.reply_text("Mən özüm BAN etməyəcəyəm, sən dəlisən?")
        return

    try:
        chat.ban_member(user_id)
        message.reply_text("Söhbət qadağan edildi!")
    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text("Qadağan edilib!", quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s səbəbiylə %s istifadəçisinin %s (%s) söhbətində qadağan edilməsi XƏTASI",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lanet olsun, mən o istifadəçiyə qadağa qoya bilmərəm.")


@bot_admin
def runban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Siz söhbətə/istifadəçiyə istinad etmirsiniz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        )
        return
    elif not chat_id:
        message.reply_text("Siz deyəsən söhbətə istinad etmirsiniz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı":
            message.reply_text(
                "Çat tapılmadı! Etibarlı söhbət ID-si daxil etdiyinizə əmin olun və mən bu söhbətin bir hissəsiyəm."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("Üzr istəyirəm, amma bu, şəxsi söhbətdir!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "Mən orada insanları məhdudlaşdıra bilmərəm! Əmin olun ki, mən adminəm və istifadəçilərin qadağanını ləğv edə bilərəm."
        )
        return

    try:
        chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Bu istifadəçini orada tapa bilmirəm")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "Niyə artıq həmin söhbətdə olan birinin qadağanını uzaqdan çıxarmağa çalışırsınız??"
        )
        return

    if user_id == bot.id:
        message.reply_text("Mən özüm QABANı QİÇƏTDƏNMƏYƏCƏM, orda adminəm!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Yep, bu istifadəçi həmin söhbətə qoşula bilər!")
    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text("Unbanned!", quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s səbəbiylə %s (%s) söhbətində %s istifadəçisinin qadağasını ləğv edərkən XƏTA",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lənət olsun, mən o istifadəçinin qadağanını ləğv edə bilmərəm.")


@bot_admin
def rkick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Siz söhbətə/istifadəçiyə istinad etmirsiniz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        )
        return
    elif not chat_id:
        message.reply_text("Siz deyəsən söhbətə istinad etmirsiniz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı":
            message.reply_text(
                "Çat tapılmadı! Etibarlı söhbət ID-si daxil etdiyinizə əmin olun və mən bu söhbətin bir hissəsiyəm."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("Üzr istəyirəm, amma bu, şəxsi söhbətdir!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "Mən orada insanları məhdudlaşdıra bilmərəm! Əmin olun ki, mən adminəm və istifadəçiləri yumruqlaya bilirəm."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Bu istifadəçini tapa bilmirəm")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Çox istərdim ki, adminləri yumruqlaya biləydim...")
        return

    if user_id == bot.id:
        message.reply_text("Mən özümü yumruqlamayacağam, sən dəlisən??")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("Çatdan yumruqlanıb!")
    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text("Yumrulmuş!", quote=False)
        elif excp.message in RKICK_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "%s səbəbiylə %s (%s) adlı söhbətdə %s istifadəçisinin vurulması XƏTASI",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lənət olsun, mən o istifadəçini yumruqlaya bilmirəm.")


@bot_admin
def rmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Siz söhbətə/istifadəçiyə istinad etmirsiniz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        )
        return
    elif not chat_id:
        message.reply_text("Siz deyəsən söhbətə istinad etmirsiniz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı":
            message.reply_text(
                "Çat tapılmadı! Etibarlı söhbət ID-si daxil etdiyinizə əmin olun və mən bu söhbətin bir hissəsiyəm."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("Üzr istəyirəm, amma bu, şəxsi söhbətdir!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "Mən orada insanları məhdudlaşdıra bilmərəm! Əmin olun ki, mən adminəm və istifadəçilərin səsini söndürə bilirəm."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Bu istifadəçini tapa bilmirəm")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("Çox istərdim adminləri susdura biləydim...")
        return

    if user_id == bot.id:
        message.reply_text("Mən özümü susdurmayacağam, sən dəlisən?")
        return

    try:
        bot.restrict_chat_member(
            chat.id, user_id, permissions=ChatPermissions(can_send_messages=False)
        )
        message.reply_text("Söhbətdən səsi kəsildi!")
    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text("Muted!", quote=False)
        elif excp.message in RMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "XƏTƏ %s səbəbiylə %s (%s) söhbətində istifadəçi %s səsini söndürdü",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lənət olsun, mən o istifadəçinin səsini söndürə bilmirəm.")


@bot_admin
def runmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("Siz söhbətə/istifadəçiyə istinad etmirsiniz.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "Siz istifadəçiyə istinad etmirsiniz və ya göstərilən ID səhvdir.."
        )
        return
    elif not chat_id:
        message.reply_text("Siz deyəsən söhbətə istinad etmirsiniz.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Çat tapılmadı":
            message.reply_text(
                "Çat tapılmadı! Etibarlı söhbət ID-si daxil etdiyinizə əmin olun və mən bu söhbətin bir hissəsiyəm."
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("Üzr istəyirəm, amma bu, şəxsi söhbətdir!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "Mən orada insanları məhdudlaşdıra bilmərəm! Əmin olun ki, mən adminəm və istifadəçilərin qadağanını ləğv edə bilərəm."
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "İstifadəçi tapılmadı":
            message.reply_text("Bu istifadəçini orada tapa bilmirəm")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("Bu istifadəçi artıq həmin çatda danışmaq hüququna malikdir.")
            return

    if user_id == bot.id:
        message.reply_text("Mən özüm SESSİ AÇMAYACAQ, orda adminəm!")
        return

    try:
        bot.restrict_chat_member(
            chat.id,
            int(user_id),
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        message.reply_text("Bəli, bu istifadəçi həmin çatda danışa bilər!")
    except BadRequest as excp:
        if excp.message == "Cavab mesajı tapılmadı":
            # Do not reply
            message.reply_text("Unmuted!", quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "XƏTA %s istifadəçisi %s səbəbiylə %s (%s) söhbətindən imtina etdi",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Lənət olsun, mən o istifadəçinin səsini söndürə bilmirəm.")


RBAN_HANDLER = CommandHandler(
    "rban", rban, filters=CustomFilters.sudo_filter, run_async=True
)
RUNBAN_HANDLER = CommandHandler(
    "runban", runban, filters=CustomFilters.sudo_filter, run_async=True
)
RKICK_HANDLER = CommandHandler(
    "rpunch", rkick, filters=CustomFilters.sudo_filter, run_async=True
)
RMUTE_HANDLER = CommandHandler(
    "rmute", rmute, filters=CustomFilters.sudo_filter, run_async=True
)
RUNMUTE_HANDLER = CommandHandler(
    "runmute", runmute, filters=CustomFilters.sudo_filter, run_async=True
)

dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
dispatcher.add_handler(RKICK_HANDLER)
dispatcher.add_handler(RMUTE_HANDLER)
dispatcher.add_handler(RUNMUTE_HANDLER)
