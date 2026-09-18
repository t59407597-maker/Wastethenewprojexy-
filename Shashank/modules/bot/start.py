import logging
import os
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pymongo import MongoClient

from config import OWNER_ID, ALIVE_PIC, MONGO_URL
from Shashank import app, API_ID, API_HASH

log = logging.getLogger(__name__)
user_sessions = {}
active_sessions = []

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["SessionDB"]
sessions_col = db["UserSessions"]
subscriptions_col = db["Subscriptions"]

OWNER_USERNAME = "II_JPEXO_II"
SUPPORT_USERNAME = "JP_NETWORK"


class Data:
    donate_button = [InlineKeyboardButton("⛈️ ᴅσηᴧᴛє ⛈️", callback_data="donate")]
    generate_single_button = [InlineKeyboardButton("⛈️ ʙᴀsɪᴄ ɢᴜɪᴅᴇ ⛈️", callback_data="guide")]
    home_buttons = [generate_single_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    back_buttons = [donate_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    guide_buttons = [[InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    buttons = [
        generate_single_button,
        [InlineKeyboardButton("🕸️ ᴡᴀsᴛᴇ", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("❔ ʜᴏᴡ ᴛᴏ ᴜꜱᴇ", callback_data="help"), InlineKeyboardButton("ᴀʙᴏᴜᴛ 🎶", callback_data="about")],
        [InlineKeyboardButton("⚡ ᴜᴘᴅᴀᴛᴇ's", url=f"https://t.me/{SUPPORT_USERNAME}"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ⛈️", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("🌿 ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🌿", url=f"https://t.me/{OWNER_USERNAME}")],
    ]
    START = """**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞‌‌‌‌★**
**┆◍ ʜᴇʏ, ɪ ᴀᴍ : [ᴡᴀsᴛᴇ ꭙ 𝐔sᴇʀвσᴛ](https://t.me/Wasteuserbot)**
**┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !**
**└────────────────────────•**
**❖ ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɪᴅ-ᴜsᴇʀ-ʙᴏᴛ**
**❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ.**
**❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ**
**•─────────────────────────•**
**❖ ʙʏ : [ᴡᴀsᴛᴇ ꭙ ᴏᴡɴᴇʀ](https://t.me/ii_jpexo_ii) 🚩**"""
    HELP = """**ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ** ⚡

**/start** - ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
**/help** - ᴏᴘᴇɴ ʜᴇʟᴘ ᴍᴇɴᴜ
**/about** - ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ᴏᴡɴᴇʀ
**/add** - ᴀᴜᴛᴏ-ʜᴏsᴛ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ
**/clone** - ᴄʟᴏɴᴇ ᴠɪᴀ sᴛʀɪɴɢ sᴇssɪᴏɴ
**/remove** - ʟᴏɢᴏᴜᴛ ғʀᴏᴍ ʙᴏᴛ

**ᴜsᴇʀʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs:** `.help`, `.help VcFight`, `.help Promotion`"""
    GUIDE = """**❖ ʜᴇʏ ᴅᴇᴀʀ, ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ɢᴜɪᴅᴇ ᴛᴏ ʜᴏsᴛɪɴɢ ᴡᴀsᴛᴇ Uꜱᴇʀʙᴏᴛ**

**1)** sᴇɴᴅ /add
**2)** sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ
**3)** sᴇɴᴅ ᴛʜᴇ ᴏᴛᴘ ᴡɪᴛʜ sᴘᴀᴄᴇs, ᴛʜᴇɴ 2ғᴀ ɪғ ᴇɴᴀʙʟᴇᴅ

**ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪʟʟ ʙᴇ ʜᴏsᴛᴇᴅ ᴀғᴛᴇʀ ʟᴏɢɪɴ.**"""
    ABOUT = """**ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ** 🌙

**ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴛᴏ ʜᴏsᴛ ᴀ ᴜsᴇʀʙᴏᴛ ᴡɪᴛʜ ᴍᴜʟᴛɪᴘʟᴇ ᴘʟᴜɢɪɴs.**

**ᴘᴏᴡᴇʀᴇᴅ ʙʏ : [ᴡᴀsᴛᴇ ꭙ ʙᴏᴛs](https://t.me/JP_NETWORK)**
**ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ᴡᴀsᴛᴇ](https://t.me/II_JPEXO_II)**"""
    DONATE = """**❖ ᴅᴏɴᴀᴛᴇ / sᴜᴘᴘᴏʀᴛ**

**• ᴜᴘɪ ɪᴅ »** `JOYZZ@FAM`
**• ᴄᴏɴᴛᴀᴄᴛ »** [ᴏᴡɴᴇʀ](https://t.me/II_JPEXO_II)"""


def _session_doc(uid):
    return sessions_col.find_one({"_id": uid})


def _is_owner(message):
    return bool(message.from_user and message.from_user.id == OWNER_ID)


def _parse_target(parts):
    user_id = None
    username = None
    for part in parts:
        p = part.strip().lstrip("@")
        if p.lstrip("-").isdigit() and user_id is None:
            user_id = int(p)
        elif p and username is None:
            username = p
    return user_id, username


def _sub_active(uid):
    doc = subscriptions_col.find_one({"_id": int(uid)})
    if not doc:
        return False, None
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > datetime.now(timezone.utc):
            return True, expires
        subscriptions_col.delete_one({"_id": int(uid)})
    return False, None


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await client.send_photo(message.chat.id, ALIVE_PIC, caption=Data.START, reply_markup=InlineKeyboardMarkup(Data.buttons))

@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(Data.HELP, reply_markup=InlineKeyboardMarkup(Data.home_buttons))

@app.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(Data.ABOUT, reply_markup=InlineKeyboardMarkup(Data.home_buttons))

@app.on_callback_query(filters.regex(r"^(home|help|about|donate|guide)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    if data == "home":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.START), reply_markup=InlineKeyboardMarkup(Data.buttons))
    elif data == "help":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.HELP), reply_markup=InlineKeyboardMarkup(Data.home_buttons))
    elif data == "about":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.ABOUT), reply_markup=InlineKeyboardMarkup(Data.home_buttons))
    elif data == "donate":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.DONATE), reply_markup=InlineKeyboardMarkup(Data.guide_buttons))
    elif data == "guide":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.GUIDE), reply_markup=InlineKeyboardMarkup(Data.back_buttons))

@app.on_message(filters.command("subscription") & filters.private & filters.user(OWNER_ID))
async def subscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /subscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("❌ User ID required. Example: /subscription 123456789 username")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    subscriptions_col.update_one({"_id": uid}, {"$set": {"user_id": uid, "username": username or "", "expires_at": expires, "activated_at": datetime.now(timezone.utc)}}, upsert=True)
    try:
        await client.send_message(uid, "✅ **Subscription Activated**\n\nYour Promotion subscription is active for **30 days**.")
    except Exception as exc:
        log.warning("Could not notify subscriber %s: %s", uid, exc)
    await message.reply_text(f"✅ Subscription activated for `{uid}` for 30 days.\nExpires: `{expires.isoformat()}`")

@app.on_message(filters.command("disubscription") & filters.private & filters.user(OWNER_ID))
async def disubscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /disubscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("❌ User ID required.")
    result = subscriptions_col.delete_one({"_id": uid})
    try:
        await client.send_message(uid, "⚠️ **Subscription Deactivated**\n\nYour Promotion subscription has ended. Contact @II_JPEXO_II to reactivate it.")
    except Exception as exc:
        log.warning("Could not notify unsubscribed user %s: %s", uid, exc)
    await message.reply_text("✅ Subscription removed." if result.deleted_count else "ℹ️ No active subscription found.")

@app.on_message(filters.command("clone") & filters.private)
async def clone(bot: Client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("Usage: /clone <session_string>")
    try:
        client = Client(name=f"Clone_{msg.from_user.id}", api_id=API_ID, api_hash=API_HASH, session_string=msg.command[1], plugins=dict(root="Shashank/modules"))
        await client.start()
        user = await client.get_me()
        setattr(client, "_waste_owner_uid", msg.from_user.id)
        active_sessions.append(client)
        await msg.reply(f"❖ ɴᴏᴡ ʏᴏᴜ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛᴏ ғɪɢʜᴛ\n\n❍ ᴀᴄᴄᴏᴜɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ\n\n❖ {user.first_name}")
    except Exception as e:
        await msg.reply(f"**ERROR:** `{e}`")

@app.on_message(filters.command("add") & filters.private)
async def add_session_command(client: Client, message: Message):
    uid = message.from_user.id
    if _session_doc(uid):
        return await message.reply("⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ. ᴜsᴇ /remove ғɪʀsᴛ.")
    await message.reply("📲 ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ (e.g. +918200000009):")
    user_sessions[uid] = {"step": "awaiting_phone"}

@app.on_message(filters.command("remove") & filters.private)
async def remove_session(client: Client, msg: Message):
    uid = msg.from_user.id
    for hosted in list(active_sessions):
        if getattr(hosted, "_waste_owner_uid", None) == uid or hosted.name == f"AutoClone_{uid}":
            try:
                await hosted.stop()
            except Exception:
                pass
            active_sessions.remove(hosted)
    result = sessions_col.delete_one({"_id": uid})
    await msg.reply("✅ ʏᴏᴜʀ sᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ." if result.deleted_count else "❌ ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ.")

@app.on_message()
async def session_handler(client: Client, msg: Message):
    if not msg.from_user or not msg.text:
        return
    uid = msg.from_user.id
    session = user_sessions.get(uid)
    if not session:
        return
    step = session.get("step")
    if step == "awaiting_phone":
        phone = msg.text.strip()
        temp = Client(name=f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
        session.update({"phone": phone, "client": temp})
        try:
            await temp.connect()
            sent = await temp.send_code(phone)
            session["phone_code_hash"] = sent.phone_code_hash
            session["step"] = "awaiting_otp"
            await msg.reply("📨 OTP sᴇɴᴛ! sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: `1 2 3 4 5`")
        except Exception as e:
            await msg.reply(f"❌ OTP error: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
    elif step == "awaiting_otp":
        temp = session["client"]
        try:
            await temp.sign_in(phone_number=session["phone"], phone_code_hash=session["phone_code_hash"], phone_code=msg.text.strip().replace(" ", ""))
        except SessionPasswordNeeded:
            session["step"] = "awaiting_2fa"
            return await msg.reply("🔐 sᴇɴᴅ ʏᴏᴜʀ 2FA ᴘᴀssᴡᴏʀᴅ.")
        except Exception as e:
            await msg.reply(f"❌ Login failed: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
            return
        await finalize_login(temp, msg, uid)
    elif step == "awaiting_2fa":
        temp = session["client"]
        try:
            await temp.check_password(msg.text.strip())
            await finalize_login(temp, msg, uid)
        except Exception as e:
            await msg.reply(f"❌ Incorrect 2FA password: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)

async def start_hosted_session(uid, string, notify=False):
    for c in active_sessions:
        if getattr(c, "_waste_owner_uid", None) == uid:
            return c
    hosted = Client(name=f"AutoClone_{uid}", api_id=API_ID, api_hash=API_HASH, session_string=string, plugins=dict(root="Shashank/modules"))
    setattr(hosted, "_waste_owner_uid", uid)
    await hosted.start()
    active_sessions.append(hosted)
    if notify:
        try:
            await app.send_message(uid, "✅ **Userbot Connected**\n\nYour account is now online with the Waste X Userbot features.")
        except Exception as exc:
            log.warning("Notification failed for %s: %s", uid, exc)
    return hosted

async def finalize_login(client: Client, msg: Message, uid: int):
    try:
        string = await client.export_session_string()
        user = await client.get_me()
        sessions_col.update_one({"_id": uid}, {"$set": {"session": string, "name": user.first_name, "user_id": user.id, "username": user.username}}, upsert=True)
        await start_hosted_session(uid, string, notify=False)
        await msg.reply(f"✅ ʟᴏɢɢᴇᴅ ɪɴ ᴀs **{user.first_name}**.\n\nᴀᴜᴛᴏ-ʜᴏsᴛ ɴᴏᴡ ᴏɴ.\n\nUss account me `.help` se commands dekho.")
    except Exception as e:
        await msg.reply(f"❌ ғɪɴᴀʟ sᴛᴇᴘ ғᴀɪʟᴇᴅ: `{e}`")
    finally:
        try: await client.disconnect()
        except Exception: pass
        user_sessions.pop(uid, None)

async def restore_saved_sessions():
    for doc in sessions_col.find({"session": {"$exists": True}}):
        uid = int(doc["_id"])
        try:
            await start_hosted_session(uid, doc["session"], notify=True)
            log.info("Restored hosted session for %s", uid)
        except Exception as exc:
            log.warning("Could not restore session for %s: %s", uid, exc)

