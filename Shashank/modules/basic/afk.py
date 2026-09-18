# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import asyncio
from datetime import datetime
import humanize
from pyrogram import filters, Client
from pyrogram.types import Message
from Shashank.helper.PyroHelpers import GetChatID, ReplyCheck
from Shashank.modules.help import add_command_help

AFK = False
AFK_REASON = ""
AFK_TIME = ""
USERS = {}
GROUPS = {}


def subtract_time(start, end):
    subtracted = humanize.naturaltime(start - end)
    return str(subtracted)


@Client.on_message(
    ((filters.group & filters.mentioned) | filters.private) & ~filters.me & ~filters.service, group=3
)
async def collect_afk_messages(bot: Client, message: Message):
    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME)
        is_group = True if message.chat.type in ["supergroup", "group"] else False
        CHAT_TYPE = GROUPS if is_group else USERS

        if GetChatID(message) not in CHAT_TYPE:
            text = (
                f"`ʙᴇᴇɴ ʙᴏᴏᴘ. ᴛʜɪs ɪs ᴀɴ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴍᴇssᴀɢᴇ.\n"
                f"ɪ ᴀᴍ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ʀɪɢʜᴛ ɴᴏᴡ.\n"
                f"ʟᴀsᴛ sᴇᴇɴ: {last_seen}\n"
                f"ʀᴇᴀsᴏɴ: ```{AFK_REASON.upper()}```\n"
                f"sᴇᴇ ʏᴏᴜ ᴀғᴛᴇʀ ɪ'ᴍ ᴅᴏɴᴇ ᴅᴏɪɴɢ ᴡʜᴀᴛᴇᴠᴇʀ ɪ'ᴍ ᴅᴏɪɴɢ.`"
            )
            await bot.send_message(
                chat_id=GetChatID(message),
                text=text,
                reply_to_message_id=ReplyCheck(message),
            )
            CHAT_TYPE[GetChatID(message)] = 1
            return
        elif GetChatID(message) in CHAT_TYPE:
            if CHAT_TYPE[GetChatID(message)] == 50:
                text = (
                    f"`ᴛʜɪs ɪs ᴀɴ ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴍᴇssᴀɢᴇ\n"
                    f"ʟᴀsᴛ sᴇᴇɴ: {last_seen}\n"
                    f"ᴛʜɪs ɪs ᴛʜᴇ 10ᴛʜ ᴛɪᴍᴇ ɪ'ᴠᴇ ᴛᴏʟᴅ ʏᴏᴜ I'ᴍ AFK ʀɪɢʜᴛ ɴᴏᴡ..\n"
                    f"I'ʟʟ ɢᴇᴛ ᴛᴏ ʏᴏᴜ ᴡʜᴇɴ ɪ ɢᴇᴛ ᴛᴏ ʏᴏᴜ.\n"
                    f"ɴᴏ ᴍᴏʀᴇ ᴀᴜᴛᴏ ᴍᴇssᴀɢᴇs ғᴏʀ ʏᴏᴜ`"
                )
                await bot.send_message(
                    chat_id=GetChatID(message),
                    text=text,
                    reply_to_message_id=ReplyCheck(message),
                )
            elif CHAT_TYPE[GetChatID(message)] > 50:
                return
            elif CHAT_TYPE[GetChatID(message)] % 5 == 0:
                text = (
                    f"`ʜᴇʏ I'ᴍ sᴛɪʟʟ ɴᴏᴛ ʙᴀᴄᴋ ʏᴇᴛ.\n"
                    f"ʟᴀsᴛ sᴇᴇɴ: {last_seen}\n"
                    f"sᴛɪʟʟ ʙᴜsʏ: ```{AFK_REASON.upper()}```\n"
                    f"ᴛʀʏ ᴘɪɴɢɪɴɢ ᴀ ʙɪᴛ ʟᴀᴛᴇʀ.`"
                )
                await bot.send_message(
                    chat_id=GetChatID(message),
                    text=text,
                    reply_to_message_id=ReplyCheck(message),
                )

        CHAT_TYPE[GetChatID(message)] += 1


@Client.on_message(filters.command("afk", ".") & filters.me, group=3)
async def afk_set(bot: Client, message: Message):
    global AFK_REASON, AFK, AFK_TIME

    cmd = message.command
    afk_text = ""

    if len(cmd) > 1:
        afk_text = " ".join(cmd[1:])

    if isinstance(afk_text, str):
        AFK_REASON = afk_text

    AFK = True
    AFK_TIME = datetime.now()

    await message.delete()


@Client.on_message(filters.command("afk", "!") & filters.me, group=3)
async def afk_unset(bot: Client, message: Message):
    global AFK, AFK_TIME, AFK_REASON, USERS, GROUPS

    if AFK:
        last_seen = subtract_time(datetime.now(), AFK_TIME).replace("ago", "").strip()
        await message.edit(
            f"`ᴡʜɪʟᴇ ʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ (for {last_seen}), ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ {sum(USERS.values()) + sum(GROUPS.values())} "
            f"ᴍᴇssᴀɢᴇs ғʀᴏᴍ {len(USERS) + len(GROUPS)} ᴄʜᴀᴛs`"
        )
        AFK = False
        AFK_TIME = ""
        AFK_REASON = ""
        USERS = {}
        GROUPS = {}
        await asyncio.sleep(5)

    await message.delete()

if AFK:
   @Client.on_message(filters.me, group=3)
   async def auto_afk_unset(bot: Client, message: Message):
       global AFK, AFK_TIME, AFK_REASON, USERS, GROUPS

       if AFK:
           last_seen = subtract_time(datetime.now(), AFK_TIME).replace("ago", "").strip()
           reply = await message.reply(
               f"`ᴡʜɪʟᴇ ʏᴏᴜ ᴡᴇʀᴇ ᴀᴡᴀʏ (for {last_seen}), ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ {sum(USERS.values()) + sum(GROUPS.values())} "
               f"ᴍᴇssᴀɢᴇs ғʀᴏᴍ {len(USERS) + len(GROUPS)} ᴄʜᴀᴛs`"
           )
           AFK = False
           AFK_TIME = ""
           AFK_REASON = ""
           USERS = {}
           GROUPS = {}
           await asyncio.sleep(5)
           await reply.delete()


add_command_help(
    "afk",
    [
        [".afk", "ᴀᴄᴛɪᴠᴀᴛᴇs AFK ᴍᴏᴅᴇ ᴡɪᴛʜ ʀᴇᴀsᴏɴ ᴀs ᴀɴʏᴛʜɪɴɢ ᴀғᴛᴇʀ .afk\ɴᴜsᴀɢᴇ: ```.afk <reason>```"],
        ["!afk", "ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇs AFK ᴍᴏᴅᴇ."],
    ],
)
