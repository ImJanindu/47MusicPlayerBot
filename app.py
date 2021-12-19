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
from pytgcalls.types import AudioPiped, AudioVideoPiped, GroupCall
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

CHATS = []

OWNER_ID = int(os.environ["OWNER_ID"])

@bot.on_message(filters.command("play") & filters.group)
async def play(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    try:
       query = message.text.split(None, 1)[1]
    except:
       return await message.reply_text("<b>Usage:</b> <code>/play [query]</code>")
    chat_id = message.chat.id
    m = await message.reply_text("Processing...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        yt = YouTube(link)
        aud = yt.streams.get_by_itag(140).download()
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if str(chat_id) in CHATS:
            await app.change_stream(
                chat_id,
                AudioPiped(aud)
            )
            await m.edit("Playing...")
            os.remove(aud)
        else:            
            await app.join_group_call(
                chat_id,
                AudioPiped(aud)
            )
            CHATS.append(str(chat_id))
            await m.edit("Playing...")
            os.remove(aud)
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command("stream") & filters.group)
async def stream_video(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    try:
       query = message.text.split(None, 1)[1]
    except:
       return await message.reply_text("<b>Usage:</b> <code>/stream [query]</code>")
    chat_id = message.chat.id
    m = await message.reply_text("Processing...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        yt = YouTube(link)
        vid = yt.streams.get_by_itag(18).download()
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if str(chat_id) in CHATS:
            await app.change_stream(
                chat_id,
                AudioVideoPiped(vid)
            )
            await m.edit("Playing...")
            os.remove(vid)
        else:            
            await app.join_group_call(
                chat_id,
                AudioVideoPiped(vid)
            )
            CHATS.append(str(chat_id))
            await m.edit("Playing...")
            os.remove(vid)
    except Exception as e:
        return await m.edit(str(e)) 
    

@bot.on_message(filters.command("stop") & filters.group)
async def end(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        await app.leave_group_call(chat_id)
        CHATS.clear()
        await message.reply_text("Stopped streaming.")
    else:
        await message.reply_text("Nothing is playing.")
        

@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("Paused streaming.")
        except:
            await message.reply_text("Nothing is playing.")
    else:
        await message.reply_text("Nothing is playing.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("Resumed streaming.")
        except:
            await message.reply_text("Nothing is playing.")
    else:
        await message.reply_text("Nothing is playing.")
    

app.start()   
bot.run()
idle()
