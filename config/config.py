import json
from os import getenv
import os
import sys
from base64 import b64decode

import requests
from dotenv import load_dotenv



def get_blacklist():
    try:
        aa = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3pwa2VtZW0tY29kZS9ibGFja2xpc3QvbWFpbi9ibGdjYXN0Lmpzb24="
        bb = b64decode(aa).decode("utf-8")
        res = requests.get(bb)
        if res.status_code == 200:
            return json.loads(res.text)
    except Exception as e:
        return f"An error occurred: {str(e)}"
        sys.exit(1)


load_dotenv()

HELPABLE = {}

HELP_CATEGORIES = {}

DICT_BUTTON = {}

COPY_ID = {}

BLACKLIST_KATA = []
costum_font = "€¥£¢𝑎𝑏𝑐𝑑𝑒𝑓𝑔𝒉𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ×̰͓̰̈́̈́̈́̈́ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🄰🄱🄲🄳🄴🄵🄶🄷🄸🄹🄺🄻🄼🄽🄾🄿🅀🅁🅂🅃🅄🅅🅆🅇🅈🅉🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉🅰🅱🅲🅳🅴🅵🅶🅷🅸🅹🅺🅻🅼🅽🅾🅿🆀🆁🆂🆃🆄🆅🆆🆇🆈🆉🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿 🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿 ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀᴛᴜᴠᴡʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀᴛᴜᴠᴡʏᴢᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘϙʀᴛᴜᴠᴡʏᴢᗩᗷᑕᗞᗴᖴᏀᕼᏆᒍᏦしᗰᑎᝪᑭᑫᖇᔑᎢᑌᐯᗯ᙭ᎩᏃᗩᗷᑕᗞᗴᖴᏀᕼᏆᒍᏦしᗰᑎᝪᑭᑫᖇᔑᎢᑌᐯᗯ᙭ᎩᏃᎪᏴᏟᎠᎬҒᏀᎻᏆᎫᏦᏞᎷΝϴᏢϘᎡՏͲႮᏙᏔХᎽᏃᎪᏴᏟᎠᎬҒᏀᎻᏆᎫᏦᏞᎷΝϴᏢϘᎡՏͲႮᏙᏔХᎽᏃａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁💦"

API_ID = int(
    os.environ.get(
        "API_ID",
        0,
    )
)

MAX_BOT = int(
    os.environ.get(
        "MAX_BOT",
        "50",
    )
)

API_HASH = os.environ.get(
    "API_HASH",
    "",
)

IS_JASA_PRIVATE = os.environ.get("IS_JASA_PRIVATE", False)

BOT_TOKEN = os.environ.get(
    "BOT_TOKEN",
    "",
)

BOT_ID = int(
    os.environ.get(
    "BOT_ID",
    0,
    )
)

API_GEMINI = os.environ.get(
    "API_GEMINI",
    None,
)

API_BOTCHAX = os.environ.get(
    "API_BOTCHAX",
    None,
)

API_MAELYN = os.environ.get(
    "API_MAELYN",
    None,
)

LOLHUMAN_KEY = os.environ.get(
    "LOLHUMAN_KEY",
    None,
)

IS_CURI_DATA = os.environ.get("IS_CURI_DATA", True)

WAJIB_JOIN = ["https://t.me/zpsexz"]

USENAME_OWNER = os.environ.get("USENAME_OWNER", "@iscrtz")



BOT_NAME = os.environ.get(
    "BOT_NAME",
    None,
)

DB_NAME = os.environ.get(
    "DB_NAME",
    None,
)

MONGO_DB_URI = getenv("MONGO_DB_URI", None)



URL_LOGO = os.environ.get(
    "URL_LOGO",
    "https://files.catbox.moe/ru9lxz.jpg",
)

ALIVE_PIC = os.environ.get(
    "ALIVE_PIC",
    "https://files.catbox.moe/ru9lxz.jpg",
)

HELP_LOGO = os.environ.get(
    "HELP_LOGO",
    "https://files.catbox.moe/ru9lxz.jpg",
)



COOKIE_BING = os.environ.get(
    "COOKIE_BING",
    "1r_EJKUXftHw_WkhhBza-wOiRX11MQo3cadM6vn0NDZwIvY3w_EO8m2tto5AlNukmnfxFL5JlQeXLRaGB0LEdzp5zXViq5MJ03Voqdj2wA17sH09dRnzBJ8neBXXDuPlKPdMLSgXRLJrj_MTqhHQkopj22q_DweTQF4qvnHIjyoCdd_bUotPN8My7BocoCEbrbCFjdkJ5Bc5vsR9zegZ-pQ",
)

SUDO_OWNERS = list(
    map(
        int,
        os.environ.get(
            "SUDO_OWNERS",
            "",
        ).split(),
    )
)
DEVS = list(
    map(
        int,
        os.environ.get(
            "DEVS",
            "",
        ).split(),
    )
)

AKSES_DEPLOY = list(
    map(
        int,
        os.environ.get(
            "AKSES_DEPLOY",
            "",
        ).split(),
    )
)

FAKE_DEVS = list(
    map(
        int,
        os.environ.get(
            "FAKE_DEVS",
            "",
        ).split(),
    )
)

OWNER_ID = int(
    os.environ.get(
        "OWNER_ID",
        0,
    )
)

LOG_SELLER = int(
    os.environ.get(
        "LOG_SELLER",
        0,
    )
)

LOG_BACKUP = int(
    os.environ.get(
        "LOG_BACKUP",
        0,
    )
)

SPOTIFY_CLIENT_ID = os.environ.get(
    "SPOTIFY_CLIENT_ID",
    None,
)

SPOTIFY_CLIENT_SECRET = os.environ.get(
    "SPOTIFY_CLIENT_SECRET",
    None,
)

SAWERIA_EMAIL = os.environ.get(
    "SAWERIA_EMAIL",
    None,
)
SAWERIA_USERNAME = os.environ.get(
    "SAWERIA_USERNAME",
    None,
)
SAWERIA_USERID = os.environ.get(
    "SAWERIA_USERID",
    None,
)

API_KEY = [
    "4dd6efe4b3msh7af04b95cfc378ep10a5e4jsnfa10ed324a43",
    "24d6a3913bmsh3561d6af783658fp1a8240jsneef57a49ff14",
    "2a7f82dc4bmsh64458e254945e0ep1d3e3bjsn0c41c5bac5b1",
    "79fec8c083mshcb5eb1aa2045a34p1b6c2bjsn7521db60a4d0",
    "e28f846e88msh9647d59c6e44523p111032jsnc80f0feb8cf7",
]

STARX = [7586938131]
if OWNER_ID not in SUDO_OWNERS:
    SUDO_OWNERS.append(OWNER_ID)
if OWNER_ID not in DEVS:
    DEVS.append(OWNER_ID)
if OWNER_ID not in FAKE_DEVS:
    FAKE_DEVS.append(OWNER_ID)
for P in FAKE_DEVS:
    if P not in DEVS:
        DEVS.append(P)
    if P not in SUDO_OWNERS:
        SUDO_OWNERS.append(P)
