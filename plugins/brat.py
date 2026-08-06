from command import brat_cmd, bratv2_cmd
from helpers import CMD

__MODULES__ = "Brat"
__HELP__ = """<blockquote>Command Help **Brat**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can make brat using costum text**
        `{0}brat` (text)
    **You can make brat v2 using costum text**
        `{0}brat2` (text)</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("brat|vbrat")
async def _(client, message):
    return await brat_cmd(client, message)

@CMD.UBOT("brat2")
async def _(client, message):
    return await bratv2_cmd(client, message)