import asyncio
import random
from datetime import datetime, timezone

from pyrogram import Client, filters
from Shashank.modules.help import add_command_help
from Shashank.modules.bot.start import subscriptions_col, settings_col, OWNER_USERNAME

TEXTS = [
    "Khana hua aap logo ka ?",
    "Ajj ka mood bekar hai ..",
    "Ajj dimag kharab hai meri",
    "Yaar aap itna kese masti kar lete ho",
    "Good morning",
    "Good night",
    "Lunch hua ?",
    "Breakfast hua ?",
    "Kal raat ko vc par masti kar rhe the na tum ?",
    "Hehe yaar itne funny kese ho tum",
]

DM_TEXT = '''ㅤㅤ𝖶𝖺𝗇𝗍 𝖸𝗈𝗎𝗋 𝖮𝗐𝗇 𝖯𝗋𝗈𝗆𝗈𝗍𝗂𝗈𝗇 𝖡𝗈𝗍
𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖡𝗈𝗍  - @WasteUserbot
𝖢𝗈𝗇𝗇𝖾𝖼𝗍 𝖸𝗈𝗎𝗋 𝖯𝗋𝗈𝗆𝗈𝗍𝗂𝗈𝗇 𝖠𝖼𝖼𝗈𝗎𝗇𝗍 𝖠𝗇𝖽 𝖲𝖾𝗇𝖽
".help" 𝖢𝗈𝗆𝗆𝖺𝗇𝖽.'''

_tasks = {}


def _uid(client):
    uid = getattr(client, "_waste_owner_uid", None)
    if uid:
        return int(uid)
    try:
        return int(client.me.id) if client.me else None
    except Exception:
        return None


def _active(uid):
    if not uid:
        return False
    doc = subscriptions_col.find_one({"_id": int(uid)})
    if not doc:
        return False
    expires = doc.get("expires_at")
    if not isinstance(expires, datetime):
        return False
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires > datetime.now(timezone.utc):
        return True
    try:
        subscriptions_col.delete_one({"_id": int(uid)})
    except Exception:
        pass
    return False


def _premium_text():
    return (
        "🔒 **Premium Required**\n\n"
        "Ye feature use karne ke liye aapko subscription ki zarurat hai.\n"
        f"Uske liye owner ko DM kare - @{OWNER_USERNAME}"
    )


async def _groups(client):
    ids = []
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if not chat:
            continue
        ctype = getattr(chat.type, "value", chat.type)
        if str(ctype) in {"group", "supergroup"}:
            ids.append(chat.id)
    return ids


async def _promo_loop(client):
    try:
        while getattr(client, "_autotextpromo_enabled", False):
            uid = _uid(client)
            if not _active(uid):
                client._autotextpromo_enabled = False
                break
            try:
                groups = await _groups(client)
                text = random.choice(TEXTS)
                # Send only once per group per cycle; next cycle gets a new random text.
                for chat_id in groups:
                    try:
                        await client.send_message(chat_id, text)
                        await asyncio.sleep(0.5)
                    except Exception:
                        continue
            except Exception:
                pass
            await asyncio.sleep(1800)
    except asyncio.CancelledError:
        raise


async def start_autotextpromo_if_enabled(client):
    if not getattr(client, "_autotextpromo_enabled", False):
        return
    uid = _uid(client)
    if not _active(uid):
        client._autotextpromo_enabled = False
        return
    old = _tasks.get(id(client))
    if old and not old.done():
        return
    _tasks[id(client)] = asyncio.create_task(_promo_loop(client))


async def stop_autotextpromo(client):
    client._autotextpromo_enabled = False
    task = _tasks.pop(id(client), None)
    if task and not task.done():
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@Client.on_message(filters.command("promotion", ".") & filters.me)
async def promotion_command(client, message):
    uid = _uid(client)
    if not _active(uid):
        return await message.reply(_premium_text())
    text = message.text.split(None, 1)[1] if message.text and len(message.text.split(None, 1)) > 1 else None
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        return await message.reply("Usage: `.promotion <promotion text>` or reply to a text message.")
    await message.reply(f"📢 **PROMOTION**\n\n{text}")


@Client.on_message(filters.command("autotextpromo", ".") & filters.me)
async def autotextpromo_command(client, message):
    uid = _uid(client)
    if not _active(uid):
        return await message.reply(_premium_text())
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"
    if action == "on":
        client._autotextpromo_enabled = True
        settings_col.update_one({"_id": uid}, {"$set": {"autotextpromo": True}}, upsert=True)
        await start_autotextpromo_if_enabled(client)
        return await message.reply("✅ **AutoTextPromo ON**\nRandom text will be sent every 30 minutes in your groups.")
    if action == "off":
        settings_col.update_one({"_id": uid}, {"$set": {"autotextpromo": False}}, upsert=True)
        await stop_autotextpromo(client)
        return await message.reply("🛑 **AutoTextPromo OFF**")
    return await message.reply(f"📊 **AutoTextPromo:** {'🟢 ON' if getattr(client, '_autotextpromo_enabled', False) else '🔴 OFF'}\nUsage: `.autotextpromo on/off`")


@Client.on_message(filters.private & ~filters.me)
async def promotion_dm_reply(client, message):
    try:
        await message.reply_text(DM_TEXT)
    except Exception:
        pass


add_command_help("Promotion", [
    ["promotion", "Premium promotion command. Requires an active subscription."],
    ["autotextpromo", "Premium: `.autotextpromo on/off` — sends a different casual text every 30 minutes."],
])
