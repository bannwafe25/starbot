__MODULES__ = "Blackbox"
__HELP__ = """<blockquote>Command Help **Blackbox**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can answer question to blackbox ai** 
        `{0}ask` (question)</blockquote>
<b>   {1}</b>
"""

IS_PRO = True

from command import blackbox_cmd
from helpers import CMD


@CMD.UBOT("ask")
async def _(client, message):
    return await blackbox_cmd(client, message)
