import asyncio
from info import *
from utils import *
from time import time 
from client import User
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
import re
import time

@Client.on_message(filters.text & filters.private & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    f_sub = await force_sub(bot, message)
    if f_sub==False:
       return     
    channels = (await get_private(message.from_user.id))["channels"]
    if bool(channels)==False:
       return     
    if message.text.startswith("/"):
       return    
    query = message.text.lower()  # Convert the query to lowercase
    query_words = query.split()  # Split the query into individual words
    filtered_query_words = [word for word in query_words if word not in ["the", "dubbed", "movie", "download", "movies", "hindi", "english", "punjabi", "marathi", "tamil", "gujarati", "bengali", "kannada", "telugu", "malayalam", "to", "of", "org", "hd", "dub", "pls", "please", "2023","2022", "new"]]
    query = " ".join(filtered_query_words)  # Reconstruct the filtered query
    sts = await message.reply('Searching...💥')
    start_time = time.time()  # Start measuring elapsed time
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"  
       elapsed_time = time.time() - start_time - 2  # Calculate elapsed time
       if bool(results)==False:
          movies = await search_imdb(query)
          buttons = []
          for movie in movies: 
              buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
          msg = await sts.edit_text(text="<b><I>I Couldn't find anything related to Your Query😕.\nDid you mean any of these?</I></b>", 
                                          reply_markup=InlineKeyboardMarkup(buttons))
       else:
          msg = await sts.edit_text(text=f"Showing results in {elapsed_time:.2f} sec\n\n{results}", disable_web_page_preview=True)
       _time = (int(time()) + (15*60))
       await save_dlt_message(msg, _time)
    except:
       pass
