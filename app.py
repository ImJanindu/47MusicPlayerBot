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
import glob
import logging
from pytgcalls import StreamType
from yt_dlp import YoutubeDL
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

START_TEXT = """
Hi <b>{}</b> 👋

I can play music & stream videos in Telegram group voice chats. 

<i>Only my owner can operate me. Make your own bot from the source code.</i>
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📨 Support", url="https://t.me/JaguarBots"),
            InlineKeyboardButton("📚 Source Code", url="https://github.com/ImJanindu/47MusicPlayerBot")
        ]
    ]
)

BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏹", callback_data="stop"),
            InlineKeyboardButton("🔇", callback_data="mute"),
            InlineKeyboardButton("🔊", callback_data="unmute")
        ],
        [
            InlineKeyboardButton("🗑 Close Menu", callback_data="close")
        ]
    ]
)


@bot.on_callback_query()
async def callbacks(_, cq: CallbackQuery): 
    if cq.from_user.id != OWNER_ID:
        return await cq.answer("You aren't the owner of me.")   
    chat_id = cq.message.chat.id
    data = cq.data
    if data == "close":
        return await cq.message.delete()
    if not str(chat_id) in CHATS:
        return await cq.answer("Nothing is playing.")

    if data == "pause":
        try:
            await app.pause_stream(chat_id)
            await cq.answer("Paused streaming.")
        except:
            await cq.answer("Nothing is playing.")
      
    elif data == "resume":
        try:
            await app.resume_stream(chat_id)
            await cq.answer("Resumed streaming.")
        except:
            await cq.answer("Nothing is playing.")   

    elif data == "stop":
        await app.leave_group_call(chat_id)
        CHATS.clear()
        await cq.answer("Stopped streaming.")  

    elif data == "mute":
        try:
            await app.mute_stream(chat_id)
            await cq.answer("Muted streaming.")
        except:
            await cq.answer("Nothing is playing.")
            
    elif data == "unmute":
        try:
            await app.unmute_stream(chat_id)
            await cq.answer("Unmuted streaming.")
        except:
            await cq.answer("Nothing is playing.")
            

@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    msg = START_TEXT.format(message.from_user.mention)
    await message.reply_text(text = msg,
                             reply_markup = START_BUTTONS)
    

@bot.on_message(filters.command("start") & filters.group)
async def start_group(_, message):
    await message.reply_text("🎧 <i>Music player is running.</i>")
    

@bot.on_message(filters.command("play") & filters.group)
async def music_play(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply_text("<b>Usage:</b> <code>/play [query]</code>")
    chat_id = message.chat.id
    m = await message.reply_text("🔄 Processing...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        thumb = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        ytid = link.split("=")[1]
        yt = YouTube(link)
        cap = f"🎵 <b>Playing:</b> [{yt.title}]({link}) \n\n⏳ <b>Duration:</b> {duration}"
        ydl_opts = {'format': 'ba[ext=m4a]'}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        
        aud = glob.glob(f"*{ytid}*")[0]
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if str(chat_id) in CHATS:
            await app.change_stream(
                chat_id,
                AudioPiped(aud)
            )
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
            os.remove(aud)
        else:            
            await app.join_group_call(
                chat_id,
                AudioPiped(aud)
            )
            CHATS.append(str(chat_id))
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
            os.remove(aud)
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command("video") & filters.group)
async def video_play(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply_text("<b>Usage:</b> <code>/video [query]</code>")
    chat_id = message.chat.id
    m = await message.reply_text("🔄 Processing...")
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        ytid = link.split("=")[1]
        thumb = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        yt = YouTube(link)
        cap = f"🎬 <b>Playing:</b> [{yt.title}]({link}) \n\n⏳ <b>Duration:</b> {duration}"
        ydl_opts = {'format': 'bv*[height<=480]+ba/b[height<=480] / wv*+ba/w'}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        vid = glob.glob(f"*{ytid}*")[0]            
    except Exception as e:
        return await m.edit(str(e))
    
    try:
        if str(chat_id) in CHATS:
            await app.change_stream(
                chat_id,
                AudioVideoPiped(vid)
            )
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
            os.remove(vid)
        else:            
            await app.join_group_call(
                chat_id,
                AudioVideoPiped(vid)
            )
            CHATS.append(str(chat_id))
            await message.reply_photo(thumb, caption=cap, reply_markup=BUTTONS)
            await m.delete()
            os.remove(vid)
    except Exception as e:
        return await m.edit(str(e))
    
    
@bot.on_message(filters.command(["saudio", "svideo"]) & filters.group)
async def stream_func(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    try:
        link = message.text.split(None, 1)[1]
    except:
        return await message.reply_text("<b>Usage:</b> <code>/stream [link]</code>")
    chat_id = message.chat.id
    state = message.command[0].lower()
    if state == "saudio":
        damn = AudioPiped
    elif state == "svideo":
        damn = AudioVideoPiped
    m = await message.reply_text("🔄 Processing...")
    try:
        if str(chat_id) in CHATS:
            await m.edit("❗️Voice chat is already running, please <code>/stop</code> it and then try again!")
        else:    
            await app.join_group_call(
                chat_id,
                damn(link),
                stream_type=StreamType().pulse_stream)
            CHATS.append(str(chat_id))
            await m.edit(f"✅ Started streaming: [Link]({link})", disable_web_page_preview=True)
    except Exception as e:
        return await m.edit(str(e))    
    

@bot.on_message(filters.command("stop") & filters.group)
async def end(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        await app.leave_group_call(chat_id)
        CHATS.clear()
        await message.reply_text("⏹ Stopped streaming.")
    else:
        await message.reply_text("❗Nothing is playing.")
        

@bot.on_message(filters.command("pause") & filters.group)
async def pause(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.pause_stream(chat_id)
            await message.reply_text("⏸ Paused streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("resume") & filters.group)
async def resume(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.resume_stream(chat_id)
            await message.reply_text("⏸ Resumed streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("mute") & filters.group)
async def mute(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.mute_stream(chat_id)
            await message.reply_text("🔇 Muted streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("unmute") & filters.group)
async def unmute(_, message):
    await message.delete()
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    chat_id = message.chat.id
    if str(chat_id) in CHATS:
        try:
            await app.unmute_stream(chat_id)
            await message.reply_text("🔊 Unmuted streaming.")
        except:
            await message.reply_text("❗Nothing is playing.")
    else:
        await message.reply_text("❗Nothing is playing.")
        
        
@bot.on_message(filters.command("restart"))
async def restart(_, message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        return
    await message.reply_text("🛠 <i>Restarting Music Player...</i>")
    os.system(f"kill -9 {os.getpid()} && python3 app.py")
            

app.start()
bot.run()
idle()
