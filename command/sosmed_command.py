import os
import time
import traceback
import asyncio
from datetime import timedelta
from itertools import islice
from typing import List
from uuid import uuid4
from yt_dlp import YoutubeDL

import wget
from pyrogram import enums
from pyrogram.errors import ChatForwardsRestricted
from pyrogram.types import InputMediaAudio, InputMediaPhoto, InputMediaVideo

from clients import bot
from database import state
from helpers import (ButtonUtils, Emoji, Spotify, Tools, YoutubeSearch,
                     animate_proses, youtube)
from logs import logger


def chunk_media_group(media_list: list, chunk_size: int = 4) -> List[list]:
    """Split media list into chunks of specified size"""
    media_chunks = []
    iterator = iter(media_list)
    while chunk := list(islice(iterator, chunk_size)):
        media_chunks.append(chunk)
    return media_chunks


async def spotdl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    if arg.split("/")[-2] != "track":
        return await proses.edit(
            f"{em.gagal}**Sorry only track supported!!**\n**Example:** https://open.spotify.com/track/0pmyq5KBXP3agRdxl1SZXx?si=3k3nnok6QtCkMF-XRzBo5w",
            disable_web_page_preview=True,
        )
    now = time.time()
    url = await Spotify.track(arg)
    (
        file_path,
        info,
        title,
        duration,
        views,
        channel,
        url,
        _,
        thumb,
        data_ytp,
    ) = await youtube.download(url.get("file_path"), as_video=False)
    thumbnail = wget.download(thumb)
    caption = data_ytp.format(
        info, title, timedelta(seconds=duration), views, channel, url, client.me.mention
    )
    try:
        await message.reply_audio(
            audio=file_path,
            title=title,
            thumb=thumbnail,
            performer=channel,
            duration=duration,
            caption=caption,
            progress=youtube.progress,
            progress_args=(proses, now, f"<b>Sending request...</b>", f"{title}"),
        )
        return await proses.delete()
    except Exception:
        logger.error(f"Eror download spotify: {traceback.format_exc()}")
        return await proses.edit(f"{em.gagal}**ERROR Please contact developer.*")


async def ytvideo_cmd(client, message, proses, arg):
    try:
        emo = Emoji(client)
        await emo.get()
        await proses.edit(f"{emo.proses}**Wait a minute this takes some time...**")
        now = time.time()
        try:
            yt_search = YoutubeSearch(arg, max_results=1)
            await yt_search.fetch_results()
            link = yt_search.get_link()
            if link is None:
                link = arg
            else:
                link = link
            logger.info(f"Link: {link}")
        except Exception as error:
            return await proses.edit(
                f"{emo.gagal}<b>ERROR:</b><code>{str(error)}</code>"
            )
        try:
            (
                file_name,
                inpoh,
                title,
                duration,
                views,
                channel,
                url,
                _,
                thumb,
                data_ytp,
            ) = await youtube.download(link, as_video=True)

            if isinstance(duration, str):
                duration = duration.replace(".", "")
            duration = int(duration)

        except Exception as error:
            return await proses.edit(
                f"{emo.gagal}<b>ERROR:</b><code>{str(error)}</code>"
            )

        thumbnail = wget.download(thumb)
        kapten = data_ytp.format(
            inpoh,
            title,
            timedelta(seconds=duration),
            views,
            channel,
            url,
            bot.me.mention,
        )
        await client.send_video(
            message.chat.id,
            video=file_name,
            thumb=thumbnail,
            file_name=title,
            duration=duration,
            supports_streaming=True,
            caption=f"{kapten}",
            progress=youtube.progress,
            progress_args=(
                proses,
                now,
                f"{emo.proses}<b>Trying to upload...</b>",
                f"{file_name}",
            ),
            reply_to_message_id=message.id,
        )
        await proses.delete()
        if os.path.exists(thumbnail):
            os.remove(thumbnail)
        if os.path.exists(file_name):
            os.remove(file_name)
    except Exception as er:
        logger.error(f"Error: {traceback.format_exc()}")


async def teledl_cmd(client, message, proses, link):
    em = Emoji(client)
    await em.get()
    chat_id = message.chat.id
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    logger.info(f"Chat ID: {chat_id}\nLink: {link}")
    if link.startswith(("https", "t.me")):
        if link.endswith("?single"):
            links = link.replace("?single", "")
            logger.info(f"Link Single: {links}")
            parts = links.split("/")
            if len(parts) == 7:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[6])
            else:
                chat = parts[3]
                msg_id = int(parts[4])
            logger.info(f"Chat Single: {chat}")
            logger.info(f"Message ID Single: {msg_id}")
            try:
                await client.copy_media_group(message.chat.id, chat, msg_id)
                return await proses.delete()
            except Exception as e:
                logger.info(f"Chat Single: {chat}")
                logger.info(f"Message ID Single: {msg_id}")
                media_group = []
                mediaa = await client.get_messages(int(chat), int(msg_id))
                medias = await mediaa.get_media_group()
                for msg in medias:
                    if msg.photo:
                        media_group.append(
                            InputMediaPhoto(
                                media=await client.download_media(msg.photo.file_id),
                                caption=msg.caption,
                            )
                        )
                    elif msg.video:
                        media_group.append(
                            InputMediaVideo(
                                media=await client.download_media(msg.video.file_id),
                                caption=msg.caption,
                            )
                        )
                    else:
                        print(f"Skipping message {msg.id}: no media found.")
                if media_group:
                    await client.send_media_group(message.chat.id, media_group)
                    return await proses.delete()

                return await proses.edit(
                    f"><b>{em.gagal} Failed to Copy Message from {chat} {msg_id}: {e}</b>"
                )
        if "?single" in link:
            link = link.replace("?single", "")
        if "/s/" in link:
            user, story_id = Tools.extract_story_link(link)
            story = await client.get_stories(user, story_id)
            await Tools.download_media(story, client, proses, message, True)
            return await proses.delete()
        if "?comment=" in link:
            link_parts = link.split("?comment=")
            msg_id = int(link_parts[0].split("/")[-1])
            tlinket = int(link_parts[1].split("/")[-1])
            chid = str(link.split("/")[-2])
            chat = await client.get_discussion_message(chid, msg_id)
            try:
                get_msg = await client.get_messages(chat.chat.id, tlinket)
                try:
                    await get_msg.copy(chat_id)
                    return await proses.delete()
                except ChatForwardsRestricted:
                    return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))
        if "t.me/c/" in link:
            parts = link.split("/")
            if len(parts) == 7:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[6])
            else:
                chat = f"-100{parts[4]}"
                msg_id = int(parts[5])
            logger.info(f"Chat: {chat}")
            logger.info(f"Msg ID: {msg_id}")
            try:
                get_msg = await client.get_messages(chat, msg_id)
                try:
                    await get_msg.copy(chat_id)
                    return await proses.delete()
                except ChatForwardsRestricted:
                    return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))
        else:
            msg_id = int(link.split("/")[-1])
            get_chat = str(link.split("/")[-2])
            try:
                chat = await client.get_chat(get_chat)
                get_msg = await client.get_messages(chat.id, msg_id)
                await get_msg.copy(chat_id)
                return await proses.delete()
            except ChatForwardsRestricted:
                return await Tools.download_media(get_msg, client, proses, message)
            except Exception as e:
                return await proses.edit(str(e))

    else:
        return await proses.edit(f"{em.gagal}<b>Please give valid link!!</b>")

async def pindl_cmd(client, message, proses, arg):
    em = Emoji(client)
    await em.get()
    await proses.edit(f"{em.proses}**Wait a minute this takes some time...**")
    data_json = {"url": arg}
    url = "https://api.siputzx.my.id/api/d/pinterest"
    response = await Tools.fetch.post(url, json=data_json)

    if response.status_code != 200:
        return await proses.edit(
            f"{em.gagal}**Failed to download from the provided URL.**"
        )
    data = response.json()
    result = data["data"]["media_urls"][0]
    quality = result["quality"]
    if quality == "original":
        if result["type"] == "image":
            await message.reply_photo(
                result["url"], caption=data["data"]["title"] or ""
            )
        elif result["type"] == "video/mp4":
            await message.reply_video(
                result["video"], caption=data["data"]["title"] or ""
            )
    else:
        await message.reply(f"{em.gagal}**No original link found.**")

    return await proses.delete()

async def pinterst_search(client, message):
    em = Emoji(client)
    await em.get()
    query = client.get_text(message)
    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\nExample: `{message.text.split()[0]} bh terbang` or `{message.text.split()[0]} garam & madu`</b>"
        )
    proses = await animate_proses(message, em.proses)
    try:
        url = "https://api.siputzx.my.id/api/s/pinterest"
        data_json = {"query": query, "type": ""}
        err = ""
        media_group = []
        foto, video = 0, 0
        response = await Tools.fetch.post(url, json=data_json)
        if response.status_code != 200:
            return await proses.edit(f"{em.gagal}**Please try again later!**")
        data = response.json()["data"]
        for v in data:
            if v["video_url"]:
                media_data = await Tools.get_media_data(v["video_url"], "mp4")
                media_group.append(InputMediaVideo(media=media_data))
                video += 1
            elif v["image_url"]:
                media_data = await Tools.get_media_data(v["image_url"], "jpg")
                media_group.append(InputMediaPhoto(media=media_data))
                foto += 1
        media_chunks = chunk_media_group(media_group)
        if not media_group:
            return await proses.edit(f"{em.gagal}**No media found.**")
        await proses.delete()
        for i, chunk in enumerate(media_chunks, 1):
            try:
                await client.send_media_group(chat_id=message.chat.id, media=chunk)
            except Exception as chunk_error:
                err += f"\n❌ Error sending chunk {i}: {str(chunk_error)}"
        return await message.reply(
            f"{em.sukses}**Successfully sent {len(media_group)} media\n📸 Photos: `{foto}` | 🎥 Videos: `{video}`**\n{err}"
        )
    except Exception as er:
        logger.error(f"ttdl: {traceback.format_exc()}")
        return await message.reply(f"{em.gagal}**An error occurred:** `{str(er)}`")

def yt_search(query):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "default_search": "ytsearch10",
    }

    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(
            f"ytsearch10:{query}",
            download=False
        )


async def youtube_search(client, message):
    em = Emoji(client)
    await em.get()

    query = client.get_text(message)

    if not query:
        return await message.reply(
            f"{em.gagal}<b>Please give query\n"
            f"Example: `{message.text.split()[0]} bh terbang`</b>"
        )

    proses = await animate_proses(message, em.proses)

    try:
        result = await asyncio.to_thread(
            yt_search,
            query
        )

        data = []

        for video in result.get("entries", []):
            data.append(
                {
                    "title": video.get("title", "Unknown"),
                    "url": f"https://youtube.com/watch?v={video.get('id')}",
                    "id": video.get("id"),
                    "thumbnail": video.get("thumbnail"),
                    "channel": video.get("channel", "Unknown"),
                    "duration": video.get(
                        "duration_string",
                        "0:00"
                    ),
                }
            )

    except Exception as e:
        return await proses.edit(
            f"{em.gagal}<b>Error:</b>\n"
            f"<code>{e}</code>"
        )

    if not data:
        return await proses.edit(
            f"{em.gagal}<b>No video found!</b>"
        )

    key = str(uuid4())

    as_video = (
        message.command[0].lower() == "vsong"
        if message.command
        else False
    )

    state.set(key, key, data)
    state.set(key, "idm_ytsearch", id(message))
    state.set(key, "as_video", as_video)

    inline = await ButtonUtils.send_inline_bot_result(
        message,
        message.chat.id,
        bot.me.username,
        f"inline_youtube {key}",
    )

    if inline:
        await proses.delete()
    else:
        await proses.edit(
            f"{em.gagal}<b>ERROR Please contact developer.</b>"
        )