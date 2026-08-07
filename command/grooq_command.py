from groq import Groq
from pyrogram import filters

from config import GROQ_API_KEY


groq = Groq(api_key=GROQ_API_KEY)


async def grooq_cmd(client, message):

    if not message.text:
        return

    query = message.text.split(None, 1)

    if len(query) < 2:
        return await message.reply(".ai pertanyaan")

    await message.edit("🤖 Thinking...")

    chat = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": query[1]
            }
        ]
    )

    result = chat.choices[0].message.content

    await message.edit(
        f"<blockquote>{result}</blockquote>",
        parse_mode="html"
    )