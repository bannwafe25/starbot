__MODULES__ = "Claude"
__HELP__ = """<blockquote>Command Help **Deepseek**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer question to deepseek ai** 
        `{0}ask` (question)</blockquote>
<b>   {1}</b>
"""

from command import deepseek_cmd
from helpers import CMD

IS_PRO = True


@CMD.UBOT("ask")
async def _(client, message):
    return await claude_cmd(client, message)
