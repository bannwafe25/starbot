import traceback
import os

import config
from helpers import Emoji, Tools, animate_proses
from logs import logger


BLACKBOX_CHAT_URL = "https://api.blackbox.ai/chat/completions"


async def blackbox_request(messages):

    headers = {
        "Authorization": f"Bearer {config.API_BLACKBOX}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "blackboxai/x-ai/grok-4.1-fast-non-reasoning",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 1000,
        "stream": False
    }

    response = await Tools.fetch.post(
        BLACKBOX_CHAT_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"BlackBox API Error {response.status_code}\n{response.text}"
        )

    data = response.json()

    return data["choices"][0]["message"]["content"]


async def blackbox_cmd(client, message):

    em = Emoji(client)
    await em.get()

    proses = await animate_proses(
        message,
        em.proses
    )

    prompt = client.get_text(message)

    if not prompt:
        return await proses.edit(
            f"{em.gagal} **Masukkan pertanyaan.**"
        )

    try:

        result = await blackbox_request(
            [
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah AI assistant Telegram. "
                        "Bantu coding, debugging, dan pertanyaan umum. "
                        "Gunakan bahasa Indonesia jika user memakai bahasa Indonesia."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        if len(result) > 4000:

            file_name = "blackbox_answer.txt"

            with open(
                file_name,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(result)


            await message.reply_document(
                file_name,
                caption=f"{em.sukses} **BlackBox AI Result**"
            )


            os.remove(file_name)

            return await proses.delete()


        return await proses.edit(
            f"<blockquote>{result}</blockquote>"
        )


    except Exception as e:

        logger.error(
            traceback.format_exc()
        )

        return await proses.edit(
            f"{em.gagal} **Error:**\n`{e}`"
        )