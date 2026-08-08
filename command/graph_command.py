import os
import asyncio
from pathlib import Path
from pyrogram import enums

from clients import bot
from helpers import Emoji, Tools, animate_proses

# Import fungsi uploader catbox dari project lain-upload[span_1](start_span)[span_1](end_span)
try:
    from lain_upload.uploader.catbox import upload as upload_catbox
except ImportError:
    pass


async def tg_cmd(client, message):
    emo = Emoji(client)
    await emo.get()
    XD = await animate_proses(message, emo.proses)
    
    if not message.reply_to_message or not message.reply_to_message.media:
        return await XD.edit(f"{emo.gagal}**Please reply to a media or file to upload to Catbox!**")
    
    data = Tools.get_file_id(message.reply_to_message)
    file_size = data.get("file_size")
    media_name = data.get("file_name") or data.get("file_unique_id")
    
    # Batasan ukuran file Catbox (maksimal 200MB)
    if file_size > 200 * 1024 * 1024:
        return await XD.edit(f"{emo.gagal}**File size is too large (Max 200MB)**")
        
    await XD.edit(f"{emo.proses}**Please wait uploading `{media_name}` to Catbox...**")
    
    file_path = None
    try:
        # 1. Download media dari Telegram ke penyimpanan lokal
        file_path = await client.download_media(message.reply_to_message)
        
        # 2. Upload menggunakan modul Catbox lain-upload di background thread agar tidak nge-lag
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(None, upload_catbox, Path(file_path))
        
        await XD.delete()
        return await message.reply(
            f"{emo.sukses}<b>Successfully Uploaded to Catbox: <a href='{url}'>{media_name}</a></b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
        )
        
    except Exception as exc:
        return await XD.edit(f"{emo.gagal}**{exc}**")
        
    finally:
        # Bersihkan file temporary setelah selesai di-upload
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
