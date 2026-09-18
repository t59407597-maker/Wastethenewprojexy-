# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import re

Devs = [8299512910, 8375982233]
Owner = int(8299512910)
Sudos = [8299512910, 8375982233]

res_devs = "SHIVANSHDEVS|STRANGERDEVS|ITSZ_SHIVANSH|SHASHANKDEVS"

res_grps = [-1002006121442, -1002018556839,- -1001778120979, -1001863207668]

def user_errors(error):
    if '[400 USERNAME_NOT_OCCUPIED]' in str(error):
       return "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ"
    elif '[400 USERNAME_INVALID]' in str(error):
       return "Username is invalid"
    elif '[400 PEER_ID_INVALID]' in str(error):
       return "ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ!"
    else:
       return f"**ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ:** \n\n {error}"
       
       
async def delete_reply(message, editor, text):
   try:
     await editor.edit_text(text)
   except:
     await editor.delete()
     await message.reply_text(text)

async def user_only(client, message, Owner, Sudos):
    try:
       args = message.text.split(" ", 1)[1].split(" ", 1)
    except IndexError:
       args = None

    if message.reply_to_message and message.reply_to_message.from_user:
       user = message.reply_to_message.from_user

    elif args:
       user_ = args[0]
       if user_.isnumeric():
           user_ = int(user_)
       if not user_:
           await message.reply_text("ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ʏᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴀʙᴏᴜᴛ, ʏᴏᴜ'ʀᴇ ɢᴏɪɴɢ ᴛᴏ ɴᴇᴇᴅ ᴛᴏ sᴘᴇᴄɪғʏ ᴀ ᴜsᴇʀ.!")
           return
       try:
           user = await client.get_users(user_)
       except (TypeError, ValueError):
           await message.reply_text("ʟᴏᴏᴋs ʟɪᴋᴇ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴄᴏɴᴛʀᴏʟ ᴏᴠᴇʀ ᴛʜᴀᴛ ᴜsᴇʀ, ᴏʀ ᴛʜᴇ ɪᴅ ɪsɴ'ᴛ ᴀ ᴠᴀʟɪᴅ ᴏɴᴇ. ɪғ ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ ᴏғ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇs, ɪ'ʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇᴍ.")
           return
    else:
        await message.reply_text("ɪ ᴅᴏɴ'ᴛ ᴋɴᴏᴡ ᴡʜᴏ ʏᴏᴜ'ʀᴇ ᴛᴀʟᴋɪɴɢ ᴀʙᴏᴜᴛ, ʏᴏᴜ'ʀᴇ ɢᴏɪɴɢ ᴛᴏ ɴᴇᴇᴅ to sᴘᴇᴄɪғʏ ᴀ ᴜsᴇʀ...!")
        return 

    if int(user.id) in Devs:
        await message.reply_text(f"{user.mention} ɪs ᴏᴡɴᴇʀ/ᴅᴇᴠ ᴏғ @ii_jpexo_ii")
        return
    if int(user.id) == Owner:
        await message.reply_text(f"{user.mention} ɪs ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇsᴇ ʙᴏᴛs!")
        return
    if int(user.id) in Sudos:
      if message.from_user.id != Owner:
         await message.reply_text(f"{user.mention} ɪs sᴜᴅᴏ ᴜsᴇʀ!")
         return

    return user
