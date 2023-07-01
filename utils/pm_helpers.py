import asyncio 
from info import *
from pyrogram import enums
from imdb import Cinemagoer
from pymongo.errors import DuplicateKeyError
from pyrogram.errors import UserNotParticipant
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton

dbclient    = AsyncIOMotorClient(DATABASE_URI)
db          = dbclient["Channel-Filter"]
grp_col     = db["GROUPS"]
user_col    = db["USERS"]
dlt_col     = db["Auto-Delete"]
private_col = db["GROUPS"]

ia = Cinemagoer()

async def add_private(user_id, user_name, channels, f_sub, verified):
    data = {
        "_id": user_id,
        "user_name": user_name,
        "channels": channels,
        "f_sub": f_sub,
        "verified": verified
    }
    try:
        await private_col.insert_one(data)
    except DuplicateKeyError:
        pass

async def get_private(id):
    data = {'user_id': id}
    private = await private_col.find_one(data)
    return dict(private)

async def update_private(id, new_data):
    data = {"_id": id}
    new_value = {"$set": new_data}
    await private_col.update_one(data, new_value)

async def delete_private(id):
    data = {"_id": id}
    await private_col.delete_one(data)

async def delete_user(id):
    data = {"user_id": id}
    await private_col.delete_one(data)

async def get_privates():
    count = await private_col.count_documents({})
    cursor = private_col.find({})
    result = await cursor.to_list(length=int(count))
    return count, result

async def force_sub(bot, message):
    private = await get_private(message.from_user.id)
    f_sub = private["f_sub"]
    admin = private["user_id"]
    if f_sub == False:
        return True
    if message.from_user is None:
        return True
    try:
        f_link = (await bot.get_chat(f_sub)).invite_link
        member = await bot.get_chat_member(f_sub, message.from_user.id)
        if member.status == enums.ChatMemberStatus.BANNED:
            await message.reply(f"ꜱᴏʀʀʏ {message.from_user.mention}!\n ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ, ʏᴏᴜ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ʜᴇʀᴇ ᴡɪᴛʜɪɴ 10 ꜱᴇᴄᴏɴᴅꜱ")
            await asyncio.sleep(10)
            await bot.ban_chat_member(message.chat.id, message.from_user.id)
            return False
    except UserNotParticipant:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply(
            f"<b>🚫 ʜɪ ᴅᴇᴀʀ {message.from_user.mention}!\n\n ɪꜰ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ.. ᴛʜᴇɴ ꜰɪʀꜱᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ ʜᴇʀᴇ 💯</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("✅ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✅", url=f_link)],
                    [InlineKeyboardButton("🌀 ᴛʀʏ ᴀɢᴀɪɴ 🌀", callback_data=f"checksub_{message.from_user.id}")],
                ]
            ),
        )
        await message.delete()
        return False
    except Exception as e:
        await bot.send_message(chat_id=admin, text=f"❌ Error in Fsub:\n`{str(e)}`")
        return False
    else:
        return True
