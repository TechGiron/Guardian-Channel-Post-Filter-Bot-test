import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import re
import time
import logging

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    try:
        f_sub = await force_sub(bot, message)
        if not f_sub:
            return
        
        channels = (await get_group(message.chat.id))["channels"]
        if not channels:
            return
        
        if message.text.startswith("/"):
            return
        
        query = message.text.lower()
        query_words = query.split()
        filtered_query_words = [word for word in query_words if word not in ["the", "dubbed", "movie", "download", "movies", "hindi", "english", "punjabi", "marathi", "tamil", "gujarati", "bengali", "kannada", "telugu", "malayalam", "to", "of", "org", "hd", "dub", "pls", "please", "2023", "2022", "new"]]
        query = " ".join(filtered_query_words)
        
        sts = await message.reply('Searching...💥')
        start_time = time.time()
        results = ""
        
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue
                results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"
        
        elapsed_time = time.time() - start_time
        if not results:
            movies = await search_imdb(query)
            buttons = []
            for movie in movies:
                buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
            await sts.edit_text(text="<b><I>I Couldn't find anything related to Your Query😕.\nDid you mean any of these?</I></b>",
                                reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await sts.edit_text(text=f"Showing results in {elapsed_time:.2f} sec\n\n{results}", disable_web_page_preview=True)
        
        _time = int(time()) + (15 * 60)
        await save_dlt_message(sts, _time)
    
    except Exception as e:
        logging.error(f"Error in search: {e}")
        await sts.edit_text(f"❌ Error: `{e}`")

@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()
    
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)
    
    try:
        m = await update.message.edit("Searching..💥")
        start_time = time.time()
        id = update.data.split("_")[-1]
        query = await search_imdb(id)
        channels = (await get_group(update.message.chat.id))["channels"]
        head = "<u>I Have Searched Movie With Wrong Spelling But Take care next time"
        results = ""
        
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]
                if name in results:
                    continue
                results += f"<b><I>♻️🍿 {name}\n🔗 {msg.link}</I></b>\n\n"
        
        elapsed_time = time.time() - start_time
        if not results:
            await update.message.edit("Still no results found! Please Request To Group Admin",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))
        else:
            await update.message.edit(text=f"{head}\n\nShowing results in {elapsed_time:.2f} sec\n\n{results}", disable_web_page_preview=True)
    
    except Exception as e:
        logging.error(f"Error in recheck: {e}")
        await update.message.edit(f"❌ Error: `{e}`")

@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()
    
    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)
    
    try:
        admin = (await get_group(update.message.chat.id))["user_id"]
        id = update.data.split("_")[1]
        name = await search_imdb(id)
        url = f"https://www.imdb.com/title/tt{id}"
        text = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
        
        await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
        await update.answer("✅ Request Sent To Admin", show_alert=True)
        await update.message.delete()
    
    except Exception as e:
        logging.error(f"Error in request: {e}")
        await update.answer(f"❌ Error: `{e}`", show_alert=True)
