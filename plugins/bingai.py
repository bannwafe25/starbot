from command import bingimg_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "bingimg"
__HELP__ = """<blockquote>Command Help **Bingai**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can generate image ai with Bingai from prompt command**
        `{0}bingimg` (prompt)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("bingimg")
async def _(client, message):
    return await bingimg_cmd(client, message)
