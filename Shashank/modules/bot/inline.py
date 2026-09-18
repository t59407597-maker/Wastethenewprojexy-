# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import time
import traceback
from sys import version as pyver
import os
import shlex
import textwrap
from typing import Tuple
import asyncio 
from pyrogram import Client
from pyrogram import __version__ as pyrover
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from Shashank import CMD_HELP, StartTime, app
from Shashank.helper.data import Data
from Shashank.helper.inline import inline_wrapper, paginate_help

async def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "Jam", "Hari"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


async def alive_function(message: Message, answers):
    uptime = await get_readable_time((time.time() - StartTime))
    msg = f"""
<b> — ʜᴇʏ, ɪ ᴀᴍ ᴀʟɪᴠᴇ.</b>

<b> • sᴛʀᴀɴɢᴇʀ :</b> {message.from_user.mention}
<b> • ᴘʟᴜɢɪɴs :</b> <code>{len(CMD_HELP)} ᴍᴏᴅᴜʟᴇs</code>
<b> • ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ :</b> <code>{pyver.split()[0]}</code>
<b> • ᴘʏʀᴏɢʀᴀᴍ ᴠᴇʀsɪᴏɴ :</b> <code>{pyrover}</code>
<b> • ʙᴏᴛ ᴜᴘᴛɪᴍᴇ :</b> <code>{uptime}</code>

<b> — ʙᴏᴛ ᴠᴇʀsɪᴏɴ: 2.0</b>
"""
    answers.append(
        InlineQueryResultArticle(
            title="Alive",
            description="ᴄʜᴇᴄᴋ ʙᴏᴛ's sᴛᴀᴛs",
            thumb_url="https://graph.org/file/c6a2ed96648fd03377dc9.jpg",
            input_message_content=InputTextMessageContent(
                msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("──「 ˹ɪsʜᴀ ꭙ ᴛᴏxɪᴄ˼ 」──", callback_data="helper")]]
            ),
        )
    )
    return answers


async def help_function(answers):
    bttn = paginate_help(0, CMD_HELP, "helpme")
    answers.append(
        InlineQueryResultArticle(
            title="ʜᴇʟᴘ ᴀʀᴛɪᴄʟᴇ!",
            description="ᴄʜᴇᴄᴋ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ & ʜᴇʟᴘ",
            thumb_url="https://files.catbox.moe/1u0lf7.jpg",
            input_message_content=InputTextMessageContent(
                Data.text_help_menu.format(len(CMD_HELP))
            ),
            reply_markup=InlineKeyboardMarkup(bttn),
        )
    )
    return answers


@app.on_inline_query()
@inline_wrapper
async def inline_query_handler(client: Client, query):
    try:
        text = query.query.strip().lower()
        string_given = query.query.lower()
        answers = []
        if text.strip() == "":
            return
        elif text.split()[0] == "alive":
            answerss = await alive_function(query, answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif string_given.startswith("helper"):
            answers = await help_function(answers)
            await client.answer_inline_query(query.id, results=answers, cache_time=0)
    except Exception as e:
        e = traceback.format_exc()
        print(e, "InLine")
