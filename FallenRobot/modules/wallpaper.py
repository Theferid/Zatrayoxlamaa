import random

import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from FallenRobot import pbot

##TO-DO


@pbot.on_message(filters.command(["wall", "wallpaper"]))
async def wall(_, message: Message):
    try:
        text = message.text.split(None, 1)[1]
    except IndexError:
        text = None
    if not text:
        return await message.reply_text("`Zəhmət olmasa axtarış üçün bir neçə sorğu verin.`")
    m = await message.reply_text("`Divar kağızları axtarılır...`")
    try:
        url = requests.get(f"https://api.safone.me/wall?query={text}").json()["results"]
        ran = random.randint(0, 3)
        await message.reply_photo(
            photo=url[ran]["imageUrl"],
            caption=f"🥀 **tərəfindən tələb edilmişdir :** {message.from_user.mention}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("ʟɪɴᴋ", url=url[ran]["imageUrl"])],
                ]
            ),
        )
        await m.delete()
    except Exception as e:
        await m.edit_text(
            f"`Divar kağızı tapılmadı : `{text}`",
        )
