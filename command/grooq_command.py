import asyncio

from groq import Groq
from pyrogram.enums import ParseMode

from config import GROQ_API_KEY
from helpers.emoji import Emoji


groq = Groq(api_key=GROQ_API_KEY)


async def grooq_cmd(client, message):
    em = Emoji(client)
    await em.get()

    if not message.text:
        return

    query = message.text.split(None, 1)

    if len(query) < 2:
        return await message.reply(
            f"{em.gagal} Gunakan:\n`.ai pertanyaan`"
        )

    progress = await message.edit(
        f"{em.proses} Thinking..."
    )

    try:
        def ask_groq():
            return groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": query[1]
                    }
                ]
            )

        chat = await asyncio.to_thread(
            ask_groq
        )

        result = chat.choices[0].message.content

        await progress.edit(
            f"{em.sukses}\n\n"
            f"<blockquote>{result}</blockquote>",
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        await progress.edit(
            f"{em.gagal} Terjadi kesalahan:\n`{e}`"
        )