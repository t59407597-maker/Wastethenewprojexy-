# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

from Shashank import SUDO_USER
from pyrogram import Client, filters
from pyrogram.types import Message

hl = "."

@Client.on_message(
    filters.command(["gm"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def gm(_, e: Message):       
      Fuk = await e.reply("🌅")
      await Fuk.edit_text(f"╭━━━┳━━━┳━━━┳━━━╮\n┃╭━╮┃╭━╮┃╭━╮┣╮╭╮┃\n┃┃╱╰┫┃╱┃┃┃╱┃┃┃┃┃┃\n┃┃╭━┫┃╱┃┃┃╱┃┃┃┃┃┃\n┃╰┻━┃╰━╯┃╰━╯┣╯╰╯┃\n╰━━━┻━━━┻━━━┻━━━╯.\n\n╱╱╱╱╱╱╱╱╱╱╭╮\n╭━━┳━┳┳┳━┳╋╋━┳┳━╮\n┃┃┃┃╋┃╭┫┃┃┃┃┃┃┃╋┃\n╰┻┻┻━┻╯╰┻━┻┻┻━╋╮┃\n╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━╯")

@Client.on_message(
    filters.command(["ga"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def ga(_, e: Message):       
      Fuk = await e.reply("🌅")
      await Fuk.edit_text(f"╭━━━┳━━━┳━━━┳━━━╮\n┃╭━╮┃╭━╮┃╭━╮┣╮╭╮┃\n┃┃╱╰┫┃╱┃┃┃╱┃┃┃┃┃┃\n┃┃╭━┫┃╱┃┃┃╱┃┃┃┃┃┃\n┃╰┻━┃╰━╯┃╰━╯┣╯╰╯┃\n╰━━━┻━━━┻━━━┻━━━╯\n╭━━━╮\n┃╭━╮┃\n┃┃╱┃┃\n┃╰━╯┃\n┃╭━╮┃\n╰╯╱╰╯\n╭━━━╮\n┃╭━━╯\n┃╰━━╮\n┃╭━━╯\n┃┃\n╰╯\n╭━━━━╮\n┃╭╮╭╮┃\n╰╯┃┃╰╯\n╱╱┃┃\n╱╱┃┃\n╱╱╰╯\n╭━━━╮\n┃╭━━╯\n┃╰━━╮\n┃╭━━╯\n┃╰━━╮\n╰━━━╯\n╭━━━╮\n┃╭━╮┃\n┃╰━╯┃\n┃╭╮╭╯\n┃┃┃╰╮\n╰╯╰━╯\n╭━╮╱╭╮\n┃┃╰╮┃┃\n┃╭╮╰╯┃\n┃┃╰╮┃┃\n┃┃╱┃┃┃\n╰╯╱╰━╯\n╭━━━╮\n┃╭━╮┃\n┃┃╱┃┃\n┃┃╱┃┃\n┃╰━╯┃\n╰━━━╯\n╭━━━╮\n┃╭━╮┃\n┃┃╱┃┃\n┃┃╱┃┃\n┃╰━╯┃\n╰━━━╯\n╭━╮╱╭╮\n┃┃╰╮┃┃\n┃╭╮╰╯┃\n┃┃╰╮┃┃\n┃┃╱┃┃┃\n╰╯╱╰━╯")

@Client.on_message(
    filters.command(["gn"], ".") & (filters.me | filters.user(SUDO_USER))
)
async def gn(_, e: Message):       
      Fuk = await e.reply("🌅")
      await Fuk.edit_text(f"╭━━━╮╱╱╱╱╱╱╱╭╮\n┃╭━╮┃╱╱╱╱╱╱╱┃┃\n┃┃╱╰╋━━┳━━┳━╯┃\n┃┃╭━┫╭╮┃╭╮┃╭╮┃\n┃╰┻━┃╰╯┃╰╯┃╰╯┃\n╰━━━┻━━┻━━┻━━╯\n╭━╮╱╭╮╱╱╱╭╮╱╭╮\n┃┃╰╮┃┃╱╱╱┃┃╭╯╰╮\n┃╭╮╰╯┣┳━━┫╰┻╮╭╯\n┃┃╰╮┃┣┫╭╮┃╭╮┃┃\n┃┃╱┃┃┃┃╰╯┃┃┃┃╰╮\n╰╯╱╰━┻┻━╮┣╯╰┻━╯\n╱╱╱╱╱╱╭━╯┃\n╱╱╱╱╱╱╰━━╯")
