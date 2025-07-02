import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ✅ Replace this with your actual channel ID (e.g., -1001234567890)
DB_CHANNEL = -1002728845034

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)


@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\n I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram. Use /upload to start. Use /stop to cancel current process.</b>")


@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("**Stopped**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('Send txt file.. ⚡️')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("**Invalid file input.**")
        os.remove(x)
        return

    await editable.edit(f"**Links found: {len(links)}**\n\nSend starting index (e.g. 1):")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("Send Batch Name:")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("Enter Resolution (144, 240, 360, 480, 720, 1080):")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        res_dict = {
            "144": "256x144",
            "240": "426x240",
            "360": "640x360",
            "480": "854x480",
            "720": "1280x720",
            "1080": "1920x1080"
        }
        res = res_dict.get(raw_text2, "UN")
    except:
        res = "UN"

    await editable.edit("Enter a caption to use:")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    highlighter = f"️ ⁪⁬⁮⁮⁮"
    MR = highlighter if raw_text3 == 'Robin' else raw_text3

    await editable.edit("Send thumbnail URL or type 'no':")
    input6: Message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = int(raw_text) if len(links) > 1 else 1

    try:
        for i in range(count - 1, len(links)):

            V = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={
                        'User-Agent': 'Mozilla/5.0'}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'videos.classplusapp' in url:
                url = requests.get(
                    f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                    headers={'x-access-token': 'your_token_here'}).json()['url']

            elif '/master.mpd' in url:
                id = url.split("/")[-2]
                url = f"https://d26g5bnklkwsh4.cloudfront.net/{id}/master.m3u8"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'

            ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]" if "youtu" in url else f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            cmd = f'yt-dlp -o "{name}.mp4" "{url}"' if "jw-prod" in url else f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'**[📽️] Vid_ID:** {str(count).zfill(3)}.** {name1}{MR}.mkv\n**Batch** » **{raw_text0}**'
                cc1 = f'**[📁] Pdf_ID:** {str(count).zfill(3)}. {name1}{MR}.pdf\n**Batch** » **{raw_text0}**'

                if "drive" in url:
                    ka = await helper.download(url, name)
                    sent = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                    await bot.forward_message(DB_CHANNEL, m.chat.id, sent.message_id)
                    count += 1
                    os.remove(ka)
                    time.sleep(1)

                elif ".pdf" in url:
                    os.system(f'yt-dlp -o "{name}.pdf" "{url}" -R 25 --fragment-retries 25')
                    sent = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                    await bot.forward_message(DB_CHANNEL, m.chat.id, sent.message_id)
                    count += 1
                    os.remove(f'{name}.pdf')

                else:
                    prog = await m.reply_text(f"**Downloading**\n📝Name: `{name}`\n🔗URL: `{url}`\n📥Quality: `{raw_text2}`")
                    res_file = await helper.download_video(url, cmd, name)
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                    await bot.send_message(DB_CHANNEL, f"✅ Uploaded\n🎞 **{name}**\n📁 Batch: {raw_text0}\n🔗 URL: `{url}`")
                    count += 1
                    time.sleep(1)

            except FloodWait as e:
                await m.reply_text(str(e))
                time.sleep(e.x)
                continue

            except Exception as e:
                await m.reply_text(f"**Download failed**\nError: {str(e)}\nName: {name}\nURL: `{url}`")
                await bot.send_message(DB_CHANNEL, f"❌ Failed to upload\n🎞 {name}\n🔗 `{url}`\nError: `{e}`")
                continue

    except Exception as e:
        await m.reply_text(str(e))

    await m.reply_text("✅ **Done!**")
    await bot.send_message(DB_CHANNEL, f"✅ Upload task completed for {m.from_user.mention} ({m.from_user.id})")


bot.run()
