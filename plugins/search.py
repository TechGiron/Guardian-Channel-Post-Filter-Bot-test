import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import re
import itertools

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if f_sub==False:
       return     
    channels = (await get_group(message.chat.id))["channels"]
    if bool(channels)==False:
       return     
    if message.text.startswith("/"):
       return    
    query = message.text.lower()  # Convert the query to lowercase
    query_words = query.split()  # Split the query into individual words
    filtered_query_words = [word for word in query_words if word not in ["the", "dubbed", "movie", "download", "movies", "hindi", "english", "punjabi", "marathi", "tamil", "gujarati", "bengali", "Kannada", "Telugu", "Malayalam"]and not re.match(r'^\d+$', word)]
    combinations = []
    # Generate combinations of filtered query words
    for r in range(1, len(filtered_query_words) + 1):
        combinations += list(itertools.combinations(filtered_query_words, r)) 
    # Add individual filtered query words to combinations
    combinations += [[word] for word in filtered_query_words]
    # Flatten the combinations list and remove duplicates
    flattened_combinations = list(set([combo for sublist in combinations for combo in sublist]))
    head    = "<u>Here is the results 👇\n\nContact To </u> <b><I>@Botz_Guardian_Update</I></b>\n\n"
    results = ""
    try:
       for channel in channels:
           for word in flattened_combinations:
               async for msg in User.search_messages(chat_id=channel, query=query):
                   name = (msg.text or msg.caption).split("\n")[0]
                   if name in results:
                       continue 
                   results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"                                                      
       if bool(results)==False:
          movies = await search_imdb(query)
          buttons = []
          for movie in movies: 
              buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
          msg = await message.reply_text(text="<b><I>I Couldn't find anything related to Your Query😕.\nDid you mean any of these?</I></b>", 
                                          reply_markup=InlineKeyboardMarkup(buttons))
       else:
          msg = await message.reply_text(text=head+results, disable_web_page_preview=True)
       _time = (int(time()) + (15*60))
       await save_dlt_message(msg, _time)
    except:
       pass
       


@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete(2)       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    m=await update.message.edit("Searching...💥")
    id      = update.data.split("_")[-1]
    query   = await search_imdb(id)
    channels = (await get_group(update.message.chat.id))["channels"]
    head    = "<u>I Have Searched Movie With Wrong Spelling But Take care next time 👇\n\nPowered By </u> <b><I>@Botz_Guardian_Update</I></b>\n\n"
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"<b><I>♻️🍿 {name}</I></b>\n\n🔗 {msg.link}</I></b>\n\n"
       if bool(results)==False:          
          return await update.message.edit("Still no results found! Please Request To Group Admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))
       await update.message.edit(text=head+results, disable_web_page_preview=True)
    except Exception as e:
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

    admin = (await get_group(update.message.chat.id))["user_id"]
    id    = update.data.split("_")[1]
    name  = await search_imdb(id)
    url   = "https://www.imdb.com/title/tt"+id
    text  = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)
