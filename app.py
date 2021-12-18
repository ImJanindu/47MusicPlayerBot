"""
MIT License

Copyright (c) 2021 Janindu Malshan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import logging
from pytube import YouTube
from youtube_search import YoutubeSearch
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

bot = Client(
    "Music Stream Bot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)

client = Client(os.environ["SESSION_NAME"], int(os.environ["API_ID"]), os.environ["API_HASH"])

app = PyTgCalls(client)

@bot.on_message(filters.command("play") & filters.group)
async def play(_, message):
    try:
       query = message.text.split(None, 1)[1]
    except:
       return await message.reply_text("Usage:\n - <code>/play [query]</code>")
    chat_id = message.chat.id
    m = await message.reply_text("Processing...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        yt = YouTube(link)
        aud = yt.streams.get_by_itag(140).download()
        path = "{}".format(aud)
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        await app.join_group_call(
            chat_id,
            AudioPiped(aud)
        )
        await m.edit("Playing...")
    except Exception as e:
        return await m.edit(str(e))

app.start()   
bot.run()
idle()
