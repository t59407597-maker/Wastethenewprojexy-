from datetime import datetime, timezone
from pyrogram import Client, filters
from Shashank.modules.bot.start import subscriptions_col, OWNER_USERNAME
from Shashank.modules.help import add_command_help

_ALLOWED = {"👍", "❤️", "🔥", "😍", "😂", "😢", "😡", "🤯", "👏", "🎉", "💯", "👀"}

def _active(uid):
    doc = subscriptions_col.find_one({"_id": int(uid)})
    if not doc:
        return False
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > datetime.now(timezone.utc):
            return True
        try:
            subscriptions_col.delete_one({"_id": int(uid)})
        except Exception:
            pass
    return False

@Client.on_message(filters.command("autoreact", ".") & filters.me)
async def autoreact_command(client, message):
    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        try:
            uid = client.me.id if client.me else None
        except Exception:
            uid = None

    if not uid or not _active(uid):
        return await message.reply(
            "💎 **Subscription Required**\n\n"
            f"Contact owner: @{OWNER_USERNAME}"
        )

    args = message.command[1:]
    enabled = bool(getattr(client, "_auto_react_enabled", False))
    emoji = getattr(client, "_auto_react_emoji", "👍")

    if not args or args[0].lower() == "status":
        return await message.reply(
            f"⚡ **Auto Reaction:** {'ON' if enabled else 'OFF'}\n"
            f"Reaction: {emoji}"
        )

    action = args[0].lower()
    if action == "off":
        client._auto_react_enabled = False
        return await message.reply("⚡ **Auto Reaction disabled.**")

    if action == "on":
        chosen = args[1] if len(args) > 1 else "👍"
        if chosen not in _ALLOWED:
            return await message.reply(
                "❌ Unsupported reaction.\n"
                "Allowed: " + " ".join(sorted(_ALLOWED))
            )
        client._auto_react_enabled = True
        client._auto_react_emoji = chosen
        return await message.reply(f"⚡ **Auto Reaction enabled:** {chosen}")

    return await message.reply(
        "Usage: `.autoreact on [emoji]`, `.autoreact off`, `.autoreact status`"
    )


@Client.on_message((filters.group | filters.channel) & ~filters.me)
async def auto_react_watcher(client, message):
    if not getattr(client, "_auto_react_enabled", False):
        return
    emoji = getattr(client, "_auto_react_emoji", "👍")
    try:
        await message.react(emoji)
    except Exception:
        pass


add_command_help(
    "Promotion",
    [["autoreact", "Premium-only auto reaction: `.autoreact on [emoji]` / `.autoreact off`."]],
)
