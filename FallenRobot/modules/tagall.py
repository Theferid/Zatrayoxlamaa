import asyncio

from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

from FallenRobot import telethn as client

spam_chats = []


@client.on(events.NewMessage(pattern="^/tagall ?(.*)"))
@client.on(events.NewMessage(pattern="^@all ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond(
            "__Bu əmr qruplarda və kanallarda istifadə edilə bilər!__"
        )

    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Yalnız adminlər hamısını qeyd edə bilər!__")

    if event.pattern_match.group(1) and event.is_reply:
        return await event.respond("__Mənə bir arqument verin!__")
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg == None:
            return await event.respond(
                "__Mən köhnə mesajlar üçün üzvləri qeyd edə bilmərəm! (qrupa əlavə edilməzdən əvvəl göndərilən mesajlar)__"
            )
    else:
        return await event.respond(
            "__Mesaja cavab verin və ya başqalarını qeyd etmək üçün mənə mətn göndərin!__"
        )

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""
    async for usr in client.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}), "
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{msg}\n{usrtxt}"
                await client.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(3)
            usrnum = 0
            usrtxt = ""
    try:
        spam_chats.remove(chat_id)
    except:
        pass


@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if not event.chat_id in spam_chats:
        return await event.respond("__Heç bir proses getmir...__")
    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
            partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True
    if not is_admin:
        return await event.respond("__Bu əmri yalnız adminlər yerinə yetirə bilər!__")

    else:
        try:
            spam_chats.remove(event.chat_id)
        except:
            pass
        return await event.respond("__Qeyd etməyi dayandırdı.__")


__mod_name__ = "Tᴀɢ Aʟʟ"
__help__ = """
*Yalnız adminlər üçün*

❍ /tagall or @all '(mesaja cavab verin və ya başqa mesaj əlavə edin) Qrupunuzdakı bütün üzvləri istisnasız qeyd etmək.'
"""
