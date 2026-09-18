from datetime import datetime, timezone

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from Shashank.modules.help import add_command_help
from Shashank.modules.bot.start import subscriptions_col, OWNER_USERNAME


_ALLOWED_REACTIONS = {"👍", "❤️", "🔥", "😍", "😂", "😢", "😡", "🤯", "👏", "🎉", "💯", "👀"}


def _uid(client):
    return getattr(client, "_waste_owner_uid", None)


def _subscription(client):
    uid = _uid(client)
    if not uid:
        return None
    try:
        doc = subscriptions_col.find_one({"_id": int(uid)})
        if not doc:
            return None
        expires = doc.get("expires_at")
        if not isinstance(expires, datetime):
            return None
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= datetime.now(timezone.utc):
            subscriptions_col.delete_one({"_id": int(uid)})
            return None
        return doc
    except Exception:
        return None


@Client.on_message(filters.command("autoreact", ".") & filters.me)
async def autoreact_command(client: Client, message: Message):
    doc = _subscription(client)
    if not doc:
        return await message.reply_text(
            "🔒 **Premium Required**\n\n"
            f"Auto Reaction use karne ke liye active subscription chahiye.\n"
            f"Subscription ke liye @{OWNER_USERNAME} ko DM kare."
        )

    if len(message.command) < 2 or message.command[1].lower() == "status":
        enabled = bool(doc.get("auto_reaction_enabled"))
        emoji = doc.get("auto_reaction_emoji", "👍")
        return await message.reply_text(
            f"⚡ **Auto Reaction:** {'ON' if enabled else 'OFF'}\n"
            f"Reaction: {emoji}\n\n"
            "Use: `.autoreact on [emoji]` / `.autoreact off`"
        )

    action = message.command[1].lower()
    if action == "off":
        subscriptions_col.update_one(
            {"_id": int(_uid(client))},
            {"$set": {"auto_reaction_enabled": False}},
        )
        return await message.reply_text("🛑 **Auto Reaction disabled.**")

    if action != "on":
        return await message.reply_text("Usage: `.autoreact on [emoji]` / `.autoreact off`")

    emoji = message.command[2] if len(message.command) > 2 else doc.get("auto_reaction_emoji", "👍")
    if emoji not in _ALLOWED_REACTIONS:
        return await message.reply_text(
            "❌ Unsupported reaction. Use one of: " + " ".join(sorted(_ALLOWED_REACTIONS))
        )

    subscriptions_col.update_one(
        {"_id": int(_uid(client))},
        {"$set": {"auto_reaction_enabled": True, "auto_reaction_emoji": emoji}},
    )
    await message.reply_text(f"✅ **Auto Reaction enabled:** {emoji}")


@Client.on_message((filters.group | filters.channel) & ~filters.me, group=98)
async def auto_react_handler(client: Client, message: Message):
    doc = _subscription(client)
    if not doc or not doc.get("auto_reaction_enabled"):
        return
    emoji = doc.get("auto_reaction_emoji", "👍")
    try:
        await message.react(emoji)
    except Exception:
        # Reactions are cosmetic; never let a reaction failure affect the userbot.
        return


add_command_help("Promotion", [
    ["promotion", "Premium promotion feature. Requires an active 30-day subscription."],
    ["autoreact", "Premium only: `.autoreact on [emoji]` / `.autoreact off` for automatic reactions."],
])
