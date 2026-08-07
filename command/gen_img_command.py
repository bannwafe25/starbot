import os
import httpx
import base64
import shutil
import traceback
import uuid
import requests
import aiofiles
import aiohttp
import asyncio
import random
import io
from io import BytesIO
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import InputMediaPhoto
from pyrogram.types import Message
from helpers import Bing, Emoji, Tools, animate_proses
from logs import logger
from datetime import datetime

async def quote_cmd(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        await message.edit_text("❌ Silakan *reply* ke pesan yang ingin dijadikan Quotly.")
        return

    # 1. Parsing Warna
    bg_color = "#1b1429" 
    if len(message.command) > 1:
        bg_color = message.command[1]

    progress = await message.edit_text(f"⏳ [1/4] Menyiapkan data... (Warna: {bg_color})")

    # 2. Ambil Data Pengguna
    user = reply.from_user or reply.sender_chat
    first_name = user.first_name if hasattr(user, 'first_name') and user.first_name else (user.title or "User")
    last_name = user.last_name if hasattr(user, 'last_name') and user.last_name else ""
    username = user.username if hasattr(user, 'username') and user.username else ""

    # 3. Ambil Foto Profil
    await progress.edit_text("⏳ [2/4] Mengunduh foto profil...")
    avatar_url = f"https://ui-avatars.com/api/?name={first_name.replace(' ', '+')}&background=random"
    if user and hasattr(user, 'photo') and user.photo:
        try:
            photo_bytes = await client.download_media(user.photo.big_file_id, in_memory=True)
            if photo_bytes:
                avatar_url = f"data:image/jpeg;base64,{base64.b64encode(photo_bytes.getvalue()).decode('utf-8')}"
        except Exception as e:
            print(f"Gagal mengunduh foto profil: {e}")

    text = reply.text or reply.caption or ""

    # 4. Susun Payload Standar LyoSU
    message_data = {
        "from": {
            "id": user.id if user else 1,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "photo": { "url": avatar_url }
        },
        "text": text,
        "avatar": True,
        "entities": [] 
    }

    if reply.reply_to_message:
        replied_to = reply.reply_to_message
        r_user = replied_to.from_user or replied_to.sender_chat
        r_first_name = r_user.first_name if hasattr(r_user, 'first_name') and r_user.first_name else (r_user.title or "User")
        r_last_name = r_user.last_name if hasattr(r_user, 'last_name') and r_user.last_name else ""
        
        message_data["replyMessage"] = {
            "name": f"{r_first_name} {r_last_name}".strip(),
            "text": replied_to.text or replied_to.caption or "🖼 Media",
            "chatId": r_user.id if r_user else 0,
            "entities": [],
            "from": {
                "id": r_user.id if r_user else 0,
                "first_name": r_first_name,
                "last_name": r_last_name,
                "username": r_user.username if hasattr(r_user, 'username') and r_user.username else ""
            }
        }

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": bg_color,
        "width": 512,
        "height": 768,
        "scale": 2,
        "emojiBrand": "apple",
        "messages": [message_data]
    }

    # 5. Eksekusi Request ke API
    await progress.edit_text("⏳ [3/4] Menghubungi API Quotly...")
    try:
        # Menambahkan User-Agent agar tidak dicurigai sebagai bot oleh Cloudflare/Server
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with httpx.AsyncClient(timeout=20.0) as http_client:
            response = await http_client.post(
                "https://quote.yuri.ly/quote/generate", 
                json=payload, 
                headers=headers
            )
            
            if response.status_code != 200:
                await progress.edit_text(f"❌ API Error ({response.status_code}):\n`{response.text[:100]}`")
                return

            res_data = response.json()
            if "error" in res_data:
                await progress.edit_text(f"❌ Error Server: `{res_data['error']}`")
                return
            
            if "image" not in res_data:
                await progress.edit_text("❌ API tidak mengembalikan data gambar yang valid.")
                return

            await progress.edit_text("⏳ [4/4] Memproses stiker...")
            
            # Decode Base64
            image_bytes = base64.b64decode(res_data["image"])
            sticker_data = BytesIO(image_bytes)
            sticker_data.name = "quotly.webp" 

            # Kirim stiker dan hapus pesan progress
            await message.reply_sticker(sticker=sticker_data)
            await progress.delete()

    except httpx.ReadTimeout:
        await progress.edit_text("❌ Timeout: API memakan waktu terlalu lama untuk merespons.")
    except Exception as e:
        await progress.edit_text(f"❌ Terjadi kesalahan: `{e}`")


async def brat_cmd(client, message):
    em = Emoji(client)
    await em.get()

    command = message.command[0]
    prompt = client.get_text(message)

    if not prompt:
        return await message.reply(
            f"{em.gagal}**Please reply to a message containing the prompt!**\n"
            f"Example: `{command} aku ganteng`"
        )

    proses = await animate_proses(message, em.proses)

    try:
        url = "https://api.siputzx.my.id/api/m/brat"
        params = {
            "text": prompt,
            "delay": 500
        }

        response = await Tools.fetch.get(url, params=params)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")

        # Membaca gambar dari response ke dalam memori
        img_data = BytesIO(response.content)
        
        # Buka gambar menggunakan PIL dan konversi ke RGBA (mendukung transparansi)
        img = Image.open(img_data).convert("RGBA")
        
        # Telegram mewajibkan stiker muat dalam kotak 512x512
        img.thumbnail((512, 512))

        # Menyiapkan file stiker di dalam memori
        sticker = BytesIO()
        sticker.name = "brat_sticker.webp"
        
        # Simpan sebagai format WEBP (format wajib stiker statis Telegram)
        img.save(sticker, "WEBP", quality=100)
        sticker.seek(0)

        # Mengirim langsung sebagai stiker
        await client.send_sticker(
            chat_id=message.chat.id,
            sticker=sticker
        )

        # Menghapus pesan "proses..."
        await proses.delete()

    except Exception as e:
        await proses.edit(f"{em.gagal}**ERROR:**\n`{e}`")

async def bratv2_cmd(client, message):
    if not message.reply_to_message:
        return await message.edit("Balas pesan yang ingin dibuat fake chat iPhone.")

    reply = message.reply_to_message

    # 1. Menentukan waktu pesan (jam & menit)
    # Jika pesan memiliki tanggal, gunakan itu. Jika tidak, gunakan waktu saat ini.
    if reply.date:
        msg_time = reply.date.strftime("%H.%M")
    else:
        msg_time = datetime.now().strftime("%H.%M")

    # 2. Mengekstrak foto jika ada (untuk diisi ke imageUrl)
    image_url = ""
    if reply.photo:
        try:
            # Unduh foto ke memori dan konversi ke base64 URI
            photo_file = await client.download_media(reply, in_memory=True)
            image_url = "data:image/jpeg;base64," + base64.b64encode(photo_file.getvalue()).decode()
        except Exception:
            pass # Abaikan jika gagal mengunduh foto

    # 3. Menyiapkan teks
    text = reply.text or reply.caption or ""
    
    # Menghindari error jika pesan hanya berupa media tanpa caption
    if not text and not image_url:
        return await message.edit("Pesan tidak mengandung teks atau gambar yang valid.")

    # 4. Membangun Payload JSON
    payload = {
        "sender": "other", # "other" (kiri) atau "me" (kanan)
        "message": text,
        "imageUrl": image_url, # Berisi base64 gambar jika ada, atau kosong jika tidak
        "timestamp": msg_time,
        "time": msg_time,
        "status": {
            "carrierName": "INDOSAT OORE...",
            "batteryPercentage": 88,
            "signalStrength": 4,
            "wifi": True
        },
        "backgroundUrl": "",
        "readStatus": True,
        "emojiStyle": "apple"
    }

    # 5. Mengirim Request & Mengirim Gambar
    try:
        await message.edit("⏳ Membuat fake chat iPhone...")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://brat.siputzx.my.id/v2/iphone-quoted",
                json=payload,
                timeout=60
            ) as r:
                if r.status != 200:
                    error_text = await r.text()
                    return await message.edit(f"Gagal membuat fake chat:\n{error_text}")
                
                content = await r.read()

        # Output fake chat biasanya lebih cocok dikirim sebagai Foto (screenshot) bukan Stiker WEBP
        img_io = BytesIO(content)
        img_io.name = "iphone_fakechat.png"

        await message.reply_photo(img_io)
        await message.delete()

    except Exception as e:
        await message.edit(f"Error: {e}")

async def bingimg_cmd(client, message):
    emo = Emoji(client)
    await emo.get()

    prompt = client.get_text(message)

    if not prompt:
        return await message.reply(
            f"{emo.gagal}<b>Give the query you want to search!\n\n"
            f"Example:\n<code>{message.text.split()[0]} kucing</code></b>"
        )

    pros = await message.reply(
        f"{emo.proses}<b>Searching image <code>{prompt}</code> ..</b>"
    )

    try:
        api = "https://api.siputzx.my.id/api/s/bimg"

        async with aiohttp.ClientSession() as session:

            async with session.post(
                api,
                json={"query": prompt},
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30
            ) as resp:

                if resp.status != 200:
                    return await pros.edit(
                        f"{emo.gagal}<b>API error: {resp.status}</b>"
                    )

                result = await resp.json()


            if not result.get("status"):
                return await pros.edit(
                    f"{emo.gagal}<b>Failed get image.</b>"
                )


            imgs = result.get("data", [])

            if not imgs:
                return await pros.edit(
                    f"{emo.gagal}<b>Images not found.</b>"
                )


            media_group = []


            async def download_image(url, first=False):
                try:
                    async with session.get(
                        url,
                        headers={
                            "User-Agent": "Mozilla/5.0"
                        },
                        timeout=15
                    ) as r:

                        if r.status != 200:
                            return None

                        data = await r.read()

                        # skip file kecil/error page
                        if len(data) < 5000:
                            return None


                        img = Image.open(
                            io.BytesIO(data)
                        )

                        img.verify()


                        img = Image.open(
                            io.BytesIO(data)
                        )

                        img = img.convert("RGB")


                        buffer = io.BytesIO()

                        img.save(
                            buffer,
                            format="JPEG",
                            quality=90
                        )

                        buffer.seek(0)


                        caption = None

                        if first:
                            caption = (
                                f"{emo.sukses}<b>Bing Image Result</b>\n\n"
                                f"<blockquote>"
                                f"🔎 <b>Query:</b> <code>{prompt}</code>\n"
                                f"🖼️ <b>Result:</b> <code>{len(imgs)}</code> images\n"
                                f"⚡ <b>Source:</b> Bing"
                                f"</blockquote>"
                            )


                        return InputMediaPhoto(
                            media=buffer,
                            caption=caption
                        )


                except Exception as e:
                    logger.warning(
                        f"Failed image {url}: {e}"
                    )
                    return None



            tasks = []

            for i, img in enumerate(imgs[:10]):
                tasks.append(
                    download_image(
                        img,
                        first=(i == 0)
                    )
                )


            results = await asyncio.gather(*tasks)


            for item in results:
                if item:
                    media_group.append(item)


            if not media_group:
                return await pros.edit(
                    f"{emo.gagal}<b>No valid images found.</b>"
                )


            await client.send_media_group(
                chat_id=message.chat.id,
                media=media_group,
                reply_to_message_id=message.id
            )


            await pros.delete()


    except Exception as e:
        logger.error(
            f"Bing IMG error:\n{traceback.format_exc()}"
        )

        await pros.edit(
            f"{emo.gagal}<b>Error:</b>\n"
            f"<blockquote><code>{e}</code></blockquote>"
        )

    return


async def maker_img_cmd(client, message):
    em = Emoji(client)
    await em.get()
    if len(message.command) < 2:
        return await message.reply(
            f"{em.gagal}**Please give me command and reply to photo!!\nExample: `{message.text.split()[0]} nude` (reply photo).**"
        )
    proses = await animate_proses(message, em.proses)
    reply = message.reply_to_message
    if message.command[1] == "sertifikat":
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please give text!!\nExample: `{message.text.split()[0]} sertifikat anak babi`.**"
            )
        text = " ".join(message.command[2:])
        params = {"text": text}
        url = "https://api.siputzx.my.id/api/m/sertifikat-tolol"
        response = await Tools.fetch.post(url, json=params)
        if response.status_code == 200:
            if not response.content:
                return await proses.edit(f"{em.gagal}**Please try again.**")
            file_path = f"sertifikat_{uuid.uuid4().hex}.jpg"
            with open(file_path, "wb") as f:
                f.write(response.content)
            await message.reply_photo(
                file_path, caption=f"{em.sukses}<b>Succesfully generate image.</b>"
            )
            os.remove(file_path)
            return await proses.delete()
        else:
            return await proses.edit(
                f"{em.gagal}<b>Failed to generate image. Please try again later.</b>"
            )
    elif message.command[1] == "xnxx":
        if len(message.command) < 3:
            return await proses.edit(
                f"{em.gagal}**Please give text!!\nExample: `{message.text.split()[0]} xnxx skandal viral`.**"
            )
        text = " ".join(message.command[2:])
        if not message.reply_to_message.media:
            return await proses.edit(f"{em.gagal}**Please reply photo!!**")
        media = await reply.download()
        async with aiofiles.open(media, mode="rb") as file:
            file_data = await file.read()
        url = "https://api.siputzx.my.id/api/canvas/xnxx"
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("title", text)
            form.add_field(
                "image", file_data, filename="image.jpg", content_type="image/jpeg"
            )

            async with session.post(url, data=form) as response:
                if response.status != 200:
                    return await proses.edit(f"{em.gagal}**Please try again later!!**")
                file_path = f"canvas{uuid.uuid4().hex}.jpg"
                with open(file_path, "wb") as f:
                    f.write(await response.read())
                await proses.delete()
                return await message.reply_photo(file_path)
    else:
        return await proses.edit(
            f"{em.gagal}**Please give me command and reply to photo!!\nExample: `{message.text.split()[0]} nude` (reply photo).**"
        )