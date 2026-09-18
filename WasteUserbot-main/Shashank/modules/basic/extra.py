# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import os, sys, asyncio, re
from random import choice
from pyrogram import Client, filters
from pyrogram.types import Message
from Shashank.modules.help import add_command_help
from Shashank.helper.functions import user_only, user_errors, delete_reply, Owner, Sudos, Devs, res_grps, res_devs
from cache.data2 import *


handler = "."

unlimited = False 

@Client.on_message(filters.user(Sudos) & filters.command(["uspam"], prefixes=handler))
@Client.on_message(filters.me & filters.command(["uspam"], prefixes=handler))
async def uspam(client: Client, e: Message):
    global unlimited
    unlimited = True
    if int(e.chat.id) in res_grps:
        await e.reply_text("**sᴏʀʀʏ !! ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ʜᴇʀᴇ.**")
        return
    msg = str(e.text[6:]) 
    if not msg:
        await e.reply("ɢɪᴠᴇ ᴍᴇ ᴀ sᴘᴀᴍ ᴍᴇssᴀɢᴇ, ʙʀᴜʜ!")
        return
    if re.search(res_devs.lower(), msg.lower()):
        await e.reply("**sᴏʀʀʏ !!** ɪ ᴄᴀɴ'ᴛ sᴘᴀᴍ ɪɴ @lll_TOXICC_PAPA_lll ᴏᴡɴᴇʀ")
        return

    try:
        while unlimited:
            await client.send_message(e.chat.id, msg)
    except Exception as ex:
        print(ex)
        await e.reply_text(f"ᴇʀʀᴏʀ -!\n\n{ex}")


@Client.on_message(filters.user(Sudos) & filters.command(["uraid"], prefixes=handler))
@Client.on_message(filters.me & filters.command(["uraid"], prefixes=handler))
async def uraid(client: Client, e: Message):
    global unlimited
    unlimited = True
    user = await user_only(client, e, Owner, Sudos)
    mention = user.mention
    try:
        while unlimited:
            raid = choice(raids.raid)
            raid_msg = f"{mention} {raid}"
            await client.send_message(e.chat.id, raid_msg)
    except Exception as f:
        await e.reply_text(f"Error -!\n\n{f}")


@Client.on_message(filters.user(Sudos) & filters.command(["abuse", "gali"], prefixes=handler))
@Client.on_message(filters.me & filters.command(["abuse", "gali"], prefixes=handler))
async def abuse(client: Client, e: Message): 
    sex = e.text[7:]
    if sex:
        counts = int(sex)
        if int(e.chat.id) in res_grps:
            return await e.reply_text("**sᴛᴏʀʏ !! ɪɴ ᴄᴀɴ'ᴛ sᴘᴀᴍ ᴡʜᴇʀᴇ.**")
        for _ in range(counts):
            msg = choice(one_word)
            await client.send_message(e.chat.id, msg)
            await asyncio.sleep(0.2)
    else:
        global unlimited
        unlimited = True
        if int(e.chat.id) in res_grps:
            return await e.reply_text("**sᴛᴏʀʏ !! ɪɴ ᴄᴀɴ'ᴛ sᴘᴀᴍ ᴡʜᴇʀᴇ.**")
        try:
            while unlimited:
                msg = choice(one_word)
                await client.send_message(e.chat.id, msg)
        except Exception as ex:
            print(ex)
            await e.reply_text(f"Error -!\n\n{ex}")


@Client.on_message(filters.user(Sudos) & filters.command(["stop"], prefixes=handler))
@Client.on_message(filters.me & filters.command(["stop"], prefixes=handler))
async def stop(_, e: Message):
    global unlimited
    unlimited = False
    await e.reply_text("Kalap gya madarchod ya aur pelu")


@Client.on_message(filters.user(Sudos) & filters.command(["echo", "repeat"], prefixes=handler))
@Client.on_message(filters.me & filters.command(["echo", "repeat"], prefixes=handler))
async def echo_(client: Client, message: Message):
    txt = ' '.join(message.command[1:])
    if message.reply_to_message:
        msg = message.reply_to_message.text.markdown
    elif txt:
        msg = str(txt)
    else:
        await message.reply_text(f"**ᴡʀᴏɴɢ ᴜsᴀɢᴇ!** \n\nsʏɴᴛᴀx: {handler}echo (message or ʀᴇᴘʟʏ ᴛᴏ ᴍᴇssᴀɢᴇ)")
        return

    try:
        await message.delete()
        await client.send_message(message.chat.id, msg)
    except Exception as a:
        await client.send_message(message.chat.id, msg)
        print(str(a))
