# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import os
from Shashank.modules.help import add_command_help
from pyrogram import Client, filters

COMMANDS = ["op", "wow", "nice", "super"]

@Client.on_message(filters.command(COMMANDS, prefixes=["", "."]) & filters.private & filters.me)
async def self_media(client, message):
    try:
        replied = message.reply_to_message
        if not replied:
            return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴇʟғ-ᴅᴇsᴛʀᴜᴄᴛ ᴘʜᴏᴛᴏ/ᴠɪᴅᴇᴏ ᴛᴏ sᴀᴠᴇ ɪᴛ.")
        
        if not (replied.photo or replied.video):
            return await message.reply("ᴏɴʟʏ sᴇʟғ-ᴅᴇsᴛʀᴜᴄᴛ ᴘʜᴏᴛᴏ ᴏʀ ᴠɪᴅᴇᴏ ᴄᴀɴ ʙᴇ sᴀᴠᴇᴅ.")

        # Download and send to Saved Messages
        location = await client.download_media(replied)
        await client.send_document("me", location, caption="sᴀᴠᴇᴅ sᴇʟғ-ᴅᴇsᴛʀᴜᴄᴛ ᴍᴇᴅɪᴀ.")
        os.remove(location)
        await message.reply("😻 hmm")
    except Exception as e:
        await message.reply(f"ᴇʀʀᴏʀ: `{e}`")

add_command_help(
    "destruct",
    [
        [".op", "Reply to a self-destruct photo or video to save it to your Saved Messages."],
        ["🌿 More Commands", "😋🥰, wow, super, 😋😍"],
    ],
)
