import asyncio
from typing import List, Dict
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from motor.motor_asyncio import AsyncIOMotorClient
from config import OWNER_ID, MONGO_URL
from Shashank import app, LOGGER

# Logging
LOGGER.info("Connecting to your Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_URL)
    mongodb = _mongo_async_.Shukla
    LOGGER.info("Connected to your Mongo Database.")
except Exception as e:
    LOGGER.error(f"Failed to connect to your Mongo Database: {e}")
    exit()

# MongoDB collections
authdb = mongodb.adminauth
authuserdb = mongodb.authuser
chatsdb = mongodb.chats
usersdb = mongodb.tgusersdb

# Admin cache
adminlist = {}

# Database utilities
async def is_served_user(user_id: int) -> bool:
    return bool(await usersdb.find_one({"user_id": user_id}))

async def get_served_users() -> List[Dict]:
    return [user async for user in usersdb.find({"user_id": {"$gt": 0}})]

async def add_served_user(user_id: int):
    if not await is_served_user(user_id):
        await usersdb.insert_one({"user_id": user_id})

async def get_served_chats() -> List[Dict]:
    return [chat async for chat in chatsdb.find({"chat_id": {"$lt": 0}})]

async def is_served_chat(chat_id: int) -> bool:
    return bool(await chatsdb.find_one({"chat_id": chat_id}))

async def add_served_chat(chat_id: int):
    if not await is_served_chat(chat_id):
        await chatsdb.insert_one({"chat_id": chat_id})

async def _get_authusers(chat_id: int) -> Dict[str, int]:
    result = await authuserdb.find_one({"chat_id": chat_id})
    return result.get("notes", {}) if result else {}

async def get_authuser_names(chat_id: int) -> List[str]:
    return list((await _get_authusers(chat_id)).keys())

# Broadcast command
IS_BROADCASTING = False

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_message(client, message: Message):
    global IS_BROADCASTING

    if IS_BROADCASTING:
        return await message.reply_text("A broadcast is already in progress...")

    reply_msg = message.reply_to_message
    source_msg_id = reply_msg.id if reply_msg else None
    source_chat_id = message.chat.id if reply_msg else None

    query = None
    if not reply_msg:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /broadcast [message or reply]")
        query = message.text.split(None, 1)[1]
        query = query.replace("-pin", "").replace("-pinloud", "").replace("-nobot", "").replace("-user", "")
        if not query.strip():
            return await message.reply_text("Please provide some text to broadcast.")

    await message.reply_text("Started broadcasting...")
    IS_BROADCASTING = True

    # Broadcast to chats
    if "-nobot" not in message.text:
        sent, pinned = 0, 0
        chats = [int(c["chat_id"]) for c in await get_served_chats()]
        for chat_id in chats:
            try:
                msg = await (
                    app.forward_messages(chat_id, source_chat_id, source_msg_id)
                    if reply_msg else
                    app.send_message(chat_id, text=query)
                )
                if "-pin" in message.text:
                    await msg.pin(disable_notification=True)
                    pinned += 1
                elif "-pinloud" in message.text:
                    await msg.pin(disable_notification=False)
                    pinned += 1
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                LOGGER.warning(f"Error broadcasting to chat {chat_id}: {e}")
                continue
        await message.reply_text(f"Broadcasted to {sent} groups • {pinned} pins.")

    # Broadcast to users
    if "-user" in message.text:
        user_sent = 0
        users = [int(u["user_id"]) for u in await get_served_users()]
        for user_id in users:
            try:
                await (
                    app.forward_messages(user_id, source_chat_id, source_msg_id)
                    if reply_msg else
                    app.send_message(user_id, text=query)
                )
                user_sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                LOGGER.warning(f"Error broadcasting to user {user_id}: {e}")
                continue
        await message.reply_text(f"Broadcasted to {user_sent} users.")

    IS_BROADCASTING = False
