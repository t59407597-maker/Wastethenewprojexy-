# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import asyncio
from pyrogram import filters, Client
from Shashank.modules.help import *
from Shashank.helper.utility import get_arg
from pyrogram.types import *
from pyrogram import __version__
import os
import sys
import asyncio
import re
from random import choice
from pyrogram import Client, filters
from pyrogram.types import Message
from cache.data import *
from Shashank.database.rraid import *
from Shashank import SUDO_USER
from pyrogram import Client, errors, filters
from pyrogram.types import ChatPermissions, Message
DEVS = int(6762113050)
from Shashank.helper.PyroHelpers import get_ub_chats
from Shashank.modules.basic.profile import extract_user, extract_user_and_reason
SUDO_USERS = SUDO_USER
RAIDS = []


@Client.on_message(
    filters.command(["hiraid"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def hiraid(xspam: Client, e: Message):  
      Shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)
      if len(Shashank) == 2:
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          ok = await xspam.get_users(Shashank[1])
          id = ok.id
#          try:
#              userz = await xspam.get_users(id)
#          except:
#              await e.reply(f"`404 : User Doesn't Exists In This Chat !`")
#              return #remove # to enable this
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉"
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(HIRAID)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      elif e.reply_to_message:
          msg_id = e.reply_to_message.from_user.id
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          user_id = e.reply_to_message.from_user.id
          ok = await xspam.get_users(user_id)
          id = ok.id
          try:
              userz = await xspam.get_users(id)
          except:
              await e.reply(f"`404 : ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !`")
              return
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉."
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(HIRAID)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      else:
          await e.reply_text("Usage: .hiraid count username")




@Client.on_message(
    filters.command(["pbraid"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def pbraid(xspam: Client, e: Message):  
      Shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)
      if len(Shashank) == 2:
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          ok = await xspam.get_users(Shashank[1])
          id = ok.id
#          try:
#              userz = await xspam.get_users(id)
#          except:
#              await e.reply(f"`404 : User Doesn't Exists In This Chat !`")
#              return #remove # to enable this
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉"
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(PBIRAID)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      elif e.reply_to_message:
          msg_id = e.reply_to_message.from_user.id
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          user_id = e.reply_to_message.from_user.id
          ok = await xspam.get_users(user_id)
          id = ok.id
          try:
              userz = await xspam.get_users(id)
          except:
              await e.reply(f"`404 : ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !`")
              return
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉."
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(PBIRAID)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      else:
          await e.reply_text("Usage: .pbraid count username")



@Client.on_message(
    filters.command(["mraid"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def mraid(xspam: Client, e: Message):  
      Shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)
      if len(Shashank) == 2:
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          ok = await xspam.get_users(Shashank[1])
          id = ok.id
#          try:
#              userz = await xspam.get_users(id)
#          except:
#              await e.reply(f"`404 : User Doesn't Exists In This Chat !`")
#              return #remove # to enable this
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉"
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(LOVE)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      elif e.reply_to_message:
          msg_id = e.reply_to_message.from_user.id
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          user_id = e.reply_to_message.from_user.id
          ok = await xspam.get_users(user_id)
          id = ok.id
          try:
              userz = await xspam.get_users(id)
          except:
              await e.reply(f"`404 : ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !`")
              return
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉."
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(LOVE)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      else:
          await e.reply_text("Usage: .mraid count username")



@Client.on_message(
    filters.command(["eraid"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def eraid(xspam: Client, e: Message):  
      Shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)
      if len(Shashank) == 2:
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          ok = await xspam.get_users(Shashank[1])
          id = ok.id
#          try:
#              userz = await xspam.get_users(id)
#          except:
#              await e.reply(f"`404 : User Doesn't Exists In This Chat !`")
#              return #remove # to enable this
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉"
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(EMOJI)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      elif e.reply_to_message:
          msg_id = e.reply_to_message.from_user.id
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          user_id = e.reply_to_message.from_user.id
          ok = await xspam.get_users(user_id)
          id = ok.id
          try:
              userz = await xspam.get_users(id)
          except:
              await e.reply(f"`404 : ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !`")
              return
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉."
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(EMOJI)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      else:
          await e.reply_text("Usage: .eraid count username")



@Client.on_message(
    filters.command(["randi"], ".", "") & (filters.me | filters.user(SUDO_USER))
)
async def wordraid(xspam: Client, e: Message):  
      Shashank = "".join(e.text.split(maxsplit=1)[1:]).split(" ", 2)
      if len(Shashank) == 2:
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          ok = await xspam.get_users(Shashank[1])
          id = ok.id
#          try:
#              userz = await xspam.get_users(id)
#          except:
#              await e.reply(f"`404 : User Doesn't Exists In This Chat !`")
#              return #remove # to enable this
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉"
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(OneWord)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      elif e.reply_to_message:
          msg_id = e.reply_to_message.from_user.id
          counts = int(Shashank[0])
          if int(e.chat.id) in GROUP:
               return await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
          user_id = e.reply_to_message.from_user.id
          ok = await xspam.get_users(user_id)
          id = ok.id
          try:
              userz = await xspam.get_users(id)
          except:
              await e.reply(f"`404 : ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ !`")
              return
          if int(id) in VERIFIED_USERS:
                text = f"ᴄʜᴀʟ ᴄʜᴀʟ ʙᴀᴀᴘ ᴋᴏ ᴍᴀᴛ sɪᴋʜᴀ😈"
                await e.reply_text(text)
          elif int(id) in SUDO_USERS:
                text = f"ᴀʙᴇ ʟᴀᴡᴅᴇ ᴛʜᴀᴛ ɢᴜʏ ᴘᴀʀᴛ ᴏғ ◉ 𝐓𝐎𝐗𝐈𝐂 ◉."
                await e.reply_text(text)
          else:
              fname = ok.first_name
              mention = f"[{fname}](tg://user?id={id})"
              for _ in range(counts):
                    reply = choice(OneWord)
                    msg = f"{mention} {reply}"
                    await xspam.send_message(e.chat.id, msg)
                    await asyncio.sleep(0.10)
      else:
          await e.reply_text("Usage: .randi count username")
