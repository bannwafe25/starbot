import os
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
from helpers import Bing, Emoji, Tools, animate_proses
from logs import logger
from datetime import datetime

async def quote_cmd(client, message):
    em = Emoji(client)
    await em.get()

    command = message.command[0]

    # Ambil teks dari argumen teks langsung atau dari pesan yang di-reply
    prompt = client.get_text(message)
    if not prompt and message.reply_to_message:
        reply_msg = message.reply_to_message
        prompt = reply_msg.text or reply_msg.caption

    # Jika tidak ada teks sama sekali
    if not prompt:
        return await message.reply(
            f"{em.gagal}**Silakan balas sebuah pesan atau masukkan teks!**\n"
            f"Contoh: `{command} Jangan menyerah`"
        )

    # Tentukan data pengirim berdasarkan reply atau akun sendiri
    if message.reply_to_message and message.reply_to_message.from_user:
        sender = message.reply_to_message.from_user
        user_id = sender.id
        first_name = sender.first_name or "User"
        last_name = sender.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
    else:
        user_id = client.me.id
        first_name = client.me.first_name or "User"
        last_name = client.me.last_name or ""
        full_name = client.me.full_name or first_name

    proses = await animate_proses(message, em.proses)

    try:
        url = "https://brat.siputzx.my.id/quoted"

        # Susun payload JSON POST sesuai struktur API quoted
        payload = {
            "messages": [
                {
                    "from": {
                        "id": user_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "name": full_name,
                        "photo": {"url": "https://dummyimage.com/100x100"}
                    },
                    "text": prompt,
                    "entities": [],
                    "avatar": True,
                    "media": {"url": ""},
                    "mediaType": "",
                    "replyMessage": {
                        "name": "",
                        "text": "",
                        "entities": [],
                        "chatId": user_id
                    }
                }
            ],
            "backgroundColor": "#313244",
            "width": 512,
            "height": 512,
            "scale": 2,
            "type": "quote",
            "format": "webp",
            "emojiStyle": "apple"
        }

        # Gunakan method POST dengan JSON payload
        response = await Tools.fetch.post(
            url,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(
                f"Kesalahan API: {response.status_code}"
            )

        content_type = response.headers.get(
            "Content-Type",
            ""
        )

        if "webp" in content_type:
            ext = "webp"
        elif "gif" in content_type:
            ext = "gif"
        else:
            ext = "png"

        file_path = f"quoted_{uuid.uuid4().hex}.{ext}"

        with open(file_path, "wb") as f:
            f.write(response.content)

        # Kirim hasil sebagai dokumen/stiker tergantung formatnya
        if ext == "webp":
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"{em.sukses}**Dibuat oleh {client.me.mention}**"
            )
        else:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=file_path,
                caption=f"{em.sukses}**Dibuat oleh {client.me.mention}**"
            )

        os.remove(file_path)
        await proses.delete()

    except Exception as e:
        await proses.edit(
            f"{em.gagal}**TERJADI KESALAHAN:**\n`{e}`"
        )


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