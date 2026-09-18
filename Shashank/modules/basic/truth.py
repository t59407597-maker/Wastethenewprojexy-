# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import asyncio
from random import choice
from pyrogram import Client, filters
from pyrogram.types import Message
from Shashank import SUDO_USER
from cache.data2 import *

@Client.on_message(
    filters.command(["truth"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def truth(x: Client, e: Message):
      shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)

      if len(shashank) == 2:
          ok = await x.get_users(shashank[1])
          counts = int(shashank[0])
          for _ in range(counts):
                reply = choice(TRUTH)
                msg = f"[{ok.first_name}](tg://user?id={ok.id}) {reply}"
                await x.send_message(e.chat.id, msg)
                await asyncio.sleep(0.1)

      elif e.reply_to_message:
          user_id = e.reply_to_message.from_user.id
          ok = await x.get_users(user_id)
          counts = int(shashank[0])
          for _ in range(counts):
                reply = choice(TRUTH)
                msg = f"[{ok.first_name}](tg://user?id={ok.id}) {reply}"
                await x.send_message(e.chat.id, msg)
                await asyncio.sleep(0.1)

      else:
            await e.reply_text(".ᴛʀᴜᴛʜ 10 <ʀᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ ᴏʀ ᴜꜱᴇʀɴᴀᴍᴇ>")  
