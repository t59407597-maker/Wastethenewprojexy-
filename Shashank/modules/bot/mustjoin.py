from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from Shashank import app

MUST_JOIN1 = "JP_NETWORK"
MUST_JOIN2 = "WASTESUPPORT"

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    try:
        await app.get_chat_member(MUST_JOIN1, msg.from_user.id)
        await app.get_chat_member(MUST_JOIN2, msg.from_user.id)
    except UserNotParticipant:
        support_link = f"https://t.me/{MUST_JOIN1}"
        update_link = f"https://t.me/{MUST_JOIN2}"
        try:
            await msg.reply_photo(
                photo="https://files.catbox.moe/zuufvl.jpg",
                caption=(
                    "🔴 **FORCE JOIN REQUIRED** 🔴\n\n"
                    "🟢 1. Join the Support channel\n"
                    "🔵 2. Join the Update channel\n\n"
                    "✅ After joining both, send /start again."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔴 SUPPORT", url=support_link)],
                    [InlineKeyboardButton("🟢 UPDATE", url=update_link)],
                    [InlineKeyboardButton("🔵 CHECK AGAIN", callback_data="force_check")],
                ])
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
    except ChatAdminRequired:
        print(f"⚠️ Please promote me as admin in both {MUST_JOIN1} and {MUST_JOIN2}!")

@app.on_callback_query(filters.regex("^force_check$"))
async def force_check(_, query):
    try:
        await app.get_chat_member(MUST_JOIN1, query.from_user.id)
        await app.get_chat_member(MUST_JOIN2, query.from_user.id)
        await query.answer("🟢 Verified! Send /start again.", show_alert=True)
    except UserNotParticipant:
        await query.answer("🔴 Please join both channels first.", show_alert=True)
    except Exception as exc:
        await query.answer(f"⚠️ {exc}", show_alert=True)
