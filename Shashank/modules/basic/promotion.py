from datetime import datetime, timezone
from pyrogram import Client, filters
from Shashank.modules.help import add_command_help
from Shashank.modules.bot.start import subscriptions_col, OWNER_USERNAME


def _owner_uid(client):
    return getattr(client, "_waste_owner_uid", None)


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
    if expires <= datetime.now(timezone.utc):
        subscriptions_col.delete_one({"_id": int(uid)})
        return False
    return True

@Client.on_message(filters.command("promotion", ".") & filters.me)
async def promotion_command(client: Client, message):
    uid = _owner_uid(client)
    if not _active(uid):
        return await message.reply(
            "🔒 **Premium Required**\n\n"
            "Ye feature use karne ke liye aapko subscription ki zarurat hai.\n"
            f"Subscription ke liye owner ko DM kare - @{OWNER_USERNAME}"
        )
    text = message.text.split(None, 1)[1] if message.text and len(message.text.split(None, 1)) > 1 else None
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        return await message.reply("Usage: `.promotion <promotion text>` or reply to a text message.")
    await message.reply(f"📢 **PROMOTION**\n\n{text}")

add_command_help("Promotion", [
    ["promotion", "Premium promotion feature. Requires an active 30-day subscription."],
])
