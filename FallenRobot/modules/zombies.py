from asyncio import sleep

from pyrogram import filters
from pyrogram.types import Message

from FallenRobot import pbot
from FallenRobot.utils.admins import can_restrict


@pbot.on_message(filters.command(["zombies", "ghosts"]))
@can_restrict
async def ban_zombies(_, message: Message):
    del_zom = 0
    no_z = "`Bu söhbətdə 0 silinmiş hesab tapıldı.`"
    try:
        clean = message.text.split(None, 1)[1]
    except:
        clean = None
    if clean != "clean":
        check = await message.reply_text("`Silinmiş hesablar axtarılır...`")
        async for user in pbot.get_chat_members(message.chat.id):
            if user.user.is_deleted:
                del_zom += 1
                await sleep(1)
        if del_zom > 0:
            return await check.edit_text(
                f"`{del_zom}` bu söhbətdə tapıldı.\nOnları təmizləyin /zombies təmiz"
            )
        else:
            return await check.edit_text(no_z)
    cleaner = await message.reply_text("`Bu söhbətdən silinmiş hesabların təmizlənməsi...`")
    deleted_u = []
    banned = 0
    failed = 0
    async for user in pbot.get_chat_members(message.chat.id):
        if user.user.is_deleted:
            deleted_u.append(int(user.user.id))
    if len(deleted_u) > 0:
        for deleted in deleted_u:
            try:
                await message.chat.ban_member(deleted)
                banned += 1
            except:
                continue
                failed += 1
        return await cleaner.edit_text(
            f"Cleaned `{banned}` Bu söhbətdən zombilər.\nSilmək alınmadı `{failed}` admin zombi."
        )
    else:
        return await check.edit_text(no_z)


__help__ = """
*Silinmiş hesabları silin*

 ❍ /zombies *:* Qrupda silinmiş hesabları axtarmağa başlayır.
 ❍ /zombies clean *:* Silinmiş hesabları qrupdan silir.
"""

__mod_name__ = "Zᴏᴍʙɪᴇ"
