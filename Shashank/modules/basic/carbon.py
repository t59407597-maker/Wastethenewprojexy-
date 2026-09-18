# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import asyncio
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import Message
from Shashank.helper.PyroHelpers import ReplyCheck
from Shashank.modules.help import add_command_help


async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiosession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image


@Client.on_message(filters.command("carbon", ".") & filters.me)
async def carbon_func(client: Client, message: Message):
    text = (
        message.text.split(None, 1)[1]
        if len(
            message.command,
        )
        != 1
        else None
    )
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        return await message.delete()
    ex = await message.edit_text("`ᴘʀᴇᴘᴀʀɪɴɢ ᴄᴀʀʙᴏɴ . . .`")
    carbon = await make_carbon(text)
    await ex.edit("`ᴜᴘʟᴏᴀᴅɪɴɢ . . .`")
    await asyncio.gather(
        ex.delete(),
        client.send_photo(
            message.chat.id,
            carbon,
            caption=f"**ᴄᴀʀʙᴏɴɪsᴇᴅ ʙʏ** {client.me.mention}",
            reply_to_message_id=ReplyCheck(message),
        ),
    )
    carbon.close()


add_command_help(
    "carbon",
    [
        ["carbon <reply>", "Carbonize text with default settings."],
    ],
)