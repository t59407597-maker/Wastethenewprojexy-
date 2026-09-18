# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import time
from datetime import datetime
import speedtest
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import Message
from Shashank import StartTime, app, SUDO_USER
from Shashank.helper.PyroHelpers import SpeedConvert
from Shashank.modules.bot.inline import get_readable_time

from Shashank.modules.help import add_command_help

class WWW:
    SpeedTest = (
        "𝐒ᴘᴇᴇᴅᴛᴇsᴛ 𝐒ᴛᴀʀᴛᴇᴅ 𝐀ᴛ `{start}`\n\n"
        "𝐏ɪɴɢ:\n{ping} ms\n\n"
        "𝐃ᴏᴡɴʟᴏᴀᴅ:\n{download}\n\n"
        "𝐔ᴘʟᴏᴀᴅ:\n{upload}\n\n"
        "𝐈sᴘ:\n__{isp}__"
    )

    NearestDC = "Country: `{}`\n" "Nearest Datacenter: `{}`\n" "This Datacenter: `{}`"

@Client.on_message(
    filters.command(["speedtest"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def speed_test(client: Client, message: Message):
    new_msg = await message.reply_text("`𝐑ᴜɴɴɪɴɢ 𝐒ᴘᴇᴇᴅ 𝐓ᴇsᴛ . . .`")
    try:
       await message.delete()
    except:
       pass
    spd = speedtest.Speedtest()

    new_msg = await new_msg.edit(
        f"`{new_msg.text}`\n" "`ɢᴇᴛᴛɪɴɢ ʙᴇsᴛ sᴇʀᴠᴇʀ ʙᴀsᴇᴅ ᴏɴ ᴘɪɴɢ . . .`"
    )
    spd.get_best_server()

    new_msg = await new_msg.edit(f"`{new_msg.text}`\n" "`ᴛᴇsᴛɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅ . . .`")
    spd.download()

    new_msg = await new_msg.edit(f"`{new_msg.text}`\n" "`ᴛᴇsᴛɪɴɢ ᴜᴘʟᴏᴀᴅ sᴘᴇᴇᴅ . . .`")
    spd.upload()

    new_msg = await new_msg.edit(
        f"`{new_msg.text}`\n" "`ɢᴇᴛᴛɪɴɢ ʀᴇsᴜʟᴛs ᴀɴᴅ ᴘʀᴇᴘᴀʀɪɴɢ ғᴏʀᴍᴀᴛᴛɪɴɢ . . .`"
    )
    results = spd.results.dict()

    await new_msg.edit(
        WWW.SpeedTest.format(
            start=results["timestamp"],
            ping=results["ping"],
            download=SpeedConvert(results["download"]),
            upload=SpeedConvert(results["upload"]),
            isp=results["client"]["isp"],
        )
    )



@Client.on_message(
    filters.command(["ping"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def pingme(client: Client, message: Message):
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    xx = await message.reply_text("**0% ▒▒▒▒▒▒▒▒▒▒**")
    try:
       await message.delete()
    except:
       pass
    await xx.edit("**20% ██▒▒▒▒▒▒▒▒**")
    await xx.edit("**40% ████▒▒▒▒▒▒**")
    await xx.edit("**60% ██████▒▒▒▒**")
    await xx.edit("**80% ████████▒▒**")
    await xx.edit("**100% ██████████**")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await xx.edit(
        f"❏ **  ❖ 𝐖𝐀𝐒𝐓𝐄 𝐗 𝐔𝐁𝐎𝐓 ╮**\n"
        f"├• ** ❖ 𝐒ᴘᴇᴇᴅ** - `%sms`\n"
        f"├• ** ❖ 𝐔ᴘᴛɪᴍᴇ** `{uptime}` \n"
        f"└• ** ❖ 𝐍ᴀᴍᴇ:** {client.me.mention}" % (duration)
    )


add_command_help(
    "ping",
    [
        ["ping", "Check bot alive or not."],
        ["speedtest", "check bot speed."],
    ],
)
