# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

from asyncio import gather
from os import remove
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from Shashank.helper.PyroHelpers import ReplyCheck
from Shashank.modules.basic.profile import extract_user
from Shashank.modules.help import add_command_help


@Client.on_message(filters.command(["whois", "info"], ".") & filters.me)
async def who_is(client: Client, message: Message):
    user_id = await extract_user(message)
    ex = await message.edit_text("`ᴘʀᴏᴄᴇssɪɴɢ . . .`")
    if not user_id:
        return await ex.edit(
            "**ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɪᴅ/ᴜsᴇʀɴᴀᴍᴇ/ʀᴇᴘʟʏ ᴛᴏ ɢᴇᴛ ᴛʜᴀᴛ ᴜsᴇʀ's ɪɴғᴏ.**"
        )
    try:
        user = await client.get_users(user_id)
        username = f"@{user.username}" if user.username else "-"
        first_name = f"{user.first_name}" if user.first_name else "-"
        last_name = f"{user.last_name}" if user.last_name else "-"
        fullname = (
            f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        )
        user_details = (await client.get_chat(user.id)).bio
        bio = f"{user_details}" if user_details else "-"
        h = f"{user.status}"
        if h.startswith("UserStatus"):
            y = h.replace("UserStatus.", "")
            status = y.capitalize()
        else:
            status = "-"
        dc_id = f"{user.dc_id}" if user.dc_id else "-"
        common = await client.get_common_chats(user.id)
        out_str = f"""<b>ＵＳＥＲ ＩＮＦＯＲＭＡＴＩＯＮ:</b>

🆔 <b>ᴜsᴇʀ ɪᴅ:</b> <code>{user.id}</code>
👤 <b>ғɪʀsᴛ ɴᴀᴍᴇ:</b> {first_name}
🗣️ <b>ʟᴀsᴛ ɴᴀᴍᴇ:</b> {last_name}
🌐 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}
🏛️ <b>ᴅᴄ ɪᴅ:</b> <code>{dc_id}</code>
🤖 <b>ɪs ʙᴏᴛ:</b> <code>{user.is_bot}</code>
🚷 <b>ɪs sᴄᴀᴍ:</b> <code>{user.is_scam}</code>
🚫 <b>ʀᴇsᴛʀɪᴄᴛᴇᴅ:</b> <code>{user.is_restricted}</code>
✅ <b>ᴠᴇʀɪғɪᴇᴅ:</b> <code>{user.is_verified}</code>
⭐ <b>ᴘʀᴇᴍɪᴜᴍ:</b> <code>{user.is_premium}</code>
📝 <b>ᴜsᴇʀ ʙɪᴏ:</b> {bio}

👀 <b>sᴀᴍᴇ ɢʀᴏᴜᴘs sᴇᴇɴ:</b> {len(common)}
👁️ <b>ʟᴀsᴛ sᴇᴇɴ:</b> <code>{status}</code>
🔗 <b>ᴜsᴇʀ ᴘᴇʀᴍᴀɴᴇɴᴛ link:</b> <a href='tg://user?id={user.id}'>{fullname}</a>
"""
        photo_id = user.photo.big_file_id if user.photo else None
        if photo_id:
            photo = await client.download_media(photo_id)
            await gather(
                ex.delete(),
                client.send_photo(
                    message.chat.id,
                    photo,
                    caption=out_str,
                    reply_to_message_id=ReplyCheck(message),
                ),
            )
            remove(photo)
        else:
            await ex.edit(out_str, disable_web_page_preview=True)
    except Exception as e:
        return await ex.edit(f"**ɪɴғᴏ:** `{e}`")


@Client.on_message(filters.command(["chatinfo", "cinfo", "ginfo"], ".") & filters.me)
async def chatinfo_handler(client: Client, message: Message):
    ex = await message.edit_text("`ᴘʀᴏᴄᴇssɪɴɢ...`")
    try:
        if len(message.command) > 1:
            chat_u = message.command[1]
            chat = await client.get_chat(chat_u)
        else:
            if message.chat.type == ChatType.PRIVATE:
                return await message.edit(
                    f"ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡɪᴛʜɪɴ ᴀ ɢʀᴏᴜᴘ ᴏʀ ᴜsᴇ .chatinfo [ɢʀᴏᴜᴘ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ]`"
                )
            else:
                chatid = message.chat.id
                chat = await client.get_chat(chatid)
        h = f"{chat.type}"
        if h.startswith("ChatType"):
            y = h.replace("ChatType.", "")
            type = y.capitalize()
        else:
            type = "Private"
        username = f"@{chat.username}" if chat.username else "-"
        description = f"{chat.description}" if chat.description else "-"
        dc_id = f"{chat.dc_id}" if chat.dc_id else "-"
        out_str = f"""<b>ＣＨＡＴ ＩＮＦＯＲＭＡＴＩＯＮ:</b>

🆔 <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat.id}</code>
👥 <b>ᴛɪᴛʟᴇ:</b> {chat.title}
👥 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}
📩 <b>ᴛʏᴘᴇ:</b> <code>{type}</code>
🏛️ <b>ᴅᴄ ɪᴅ:</b> <code>{dc_id}</code>
🗣️ <b>ɪs sᴄᴀᴍ:</b> <code>{chat.is_scam}</code>
🎭 <b>ɪs ғᴀᴋᴇ:</b> <code>{chat.is_fake}</code>
✅ <b>ᴠᴇʀɪғɪᴇᴅ:</b> <code>{chat.is_verified}</code>
🚫 <b>ʀᴇsᴛʀɪᴄᴛᴇᴅ:</b> <code>{chat.is_restricted}</code>
🔰 <b>ᴘʀᴏᴛᴇᴄᴛᴇᴅ:</b> <code>{chat.has_protected_content}</code>

🚻 <b>ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs:</b> <code>{chat.members_count}</code>
📝 <b>ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b>
<code>{description}</code>
"""
        photo_id = chat.photo.big_file_id if chat.photo else None
        if photo_id:
            photo = await client.download_media(photo_id)
            await gather(
                ex.delete(),
                client.send_photo(
                    message.chat.id,
                    photo,
                    caption=out_str,
                    reply_to_message_id=ReplyCheck(message),
                ),
            )
            remove(photo)
        else:
            await ex.edit(out_str, disable_web_page_preview=True)
    except Exception as e:
        return await ex.edit(f"**INFO:** `{e}`")


add_command_help(
    "info",
    [
        [
            "info <username/userid/reply>",
            "get telegram user info with full description.",
        ],
        [
            "chatinfo <username/chatid/reply>",
            "get group info with full description.",
        ],
    ],
)
