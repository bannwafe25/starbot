import re
from math import ceil
from typing import List, Optional, Tuple
from uuid import uuid4

from pyrogram import enums
from pyrogram.errors import QueryIdInvalid, RPCError
from pyrogram.helpers import ikb, kb
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import dB, state, db

COLUMN_SIZE = 4  # Controls the button number of height
NUM_COLUMNS = 2  # Controls the button number of width


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, is_bot=False):
    modules = sorted(
        [
            EqInlineKeyboardButton(
                x["module"].__MODULES__,
                callback_data="{}_module({},{})".format(
                    prefix, x["module"].__MODULES__.lower(), page_n
                ),
            )
            for x in module_dict.values()
            if hasattr(x["module"], "__MODULES__")
        ]
    )
    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if is_bot:
        if len(pairs) > COLUMN_SIZE:
            pairs = pairs[
                modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)
            ] + [
                (
                    EqInlineKeyboardButton(
                        "⬅️",
                        callback_data="{}_prev({})".format(
                            prefix,
                            modulo_page - 1 if modulo_page > 0 else max_num_pages - 1,
                        ),
                    ),
                    EqInlineKeyboardButton("❌", callback_data="buttonclose"),
                    EqInlineKeyboardButton(
                        "➡️",
                        callback_data="{}_next({})".format(prefix, modulo_page + 1),
                    ),
                )
            ]
        else:
            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "🔙 Back",
                        callback_data="{}_help_back({})",
                    ),
                ]
            )
    else:
        if len(pairs) > COLUMN_SIZE:
            pairs = pairs[
                modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)
            ] + [
                (
                    EqInlineKeyboardButton(
                        "⬅️",
                        callback_data="{}_prev({})".format(
                            prefix,
                            modulo_page - 1 if modulo_page > 0 else max_num_pages - 1,
                        ),
                    ),
                    EqInlineKeyboardButton("❌", callback_data="close help"),
                    EqInlineKeyboardButton(
                        "➡️",
                        callback_data="{}_next({})".format(prefix, modulo_page + 1),
                    ),
                )
            ]
        else:
            pairs.append(
                [
                    EqInlineKeyboardButton(
                        "🔙 Back",
                        callback_data="{}_help_back({})",
                    ),
                ]
            )

    return pairs


class ButtonUtils:
    # Compile regex patterns for better performance
    URL_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})+(?:[/?]\S+)?|tg://\S+"
    )
    BUTTON_PATTERN = re.compile(r"\[(.*?)\|(.*?)\]")
    FORMAT_TAGS = {
        "<b>": "**",
        "<i>": "__",
        "<strike>": "~~",
        "<spoiler>": "||",
        "<u>": "--",
    }

    @staticmethod
    def is_url(text: str) -> bool:
        """Check if text is a URL."""
        # return bool(ButtonUtils.URL_PATTERN.match(text))
        return bool(re.search(ButtonUtils.URL_PATTERN, text))

    @staticmethod
    def is_number(text: str) -> bool:
        """Check if text is a number."""
        return text.isdigit()

    @staticmethod
    def is_copy(text: str) -> bool:
        pattern = r"copy:"

        return bool(re.search(pattern, text))

    @staticmethod
    def is_alert(text: str) -> bool:
        pattern = r"alert:"

        return bool(re.search(pattern, text))

    @staticmethod
    def is_web(text: str) -> bool:
        pattern = r"web:"

        return bool(re.search(pattern, text))

    @staticmethod
    def cek_tg(text):
        tg_pattern = r"https?:\/\/files\.catbox\.moe\/\S+"
        match = re.search(tg_pattern, text)

        if match:
            tg_link = match.group(0)
            non_tg_text = text.replace(tg_link, "").strip()
            return tg_link, non_tg_text
        else:
            return (None, text)

    @staticmethod
    def parse_msg_buttons(texts: str) -> Tuple[str, List[List]]:
        btn = []
        for z in ButtonUtils.BUTTON_PATTERN.findall(texts):
            text, url = z
            urls = url.split("|")
            url = urls[0]
            if len(urls) > 1:
                btn[-1].append([text, url])
            else:
                btn.append([[text, url]])

        txt = texts
        for z in re.findall(r"\[.+?\|.+?\]", texts):
            txt = txt.replace(z, "")

        return txt.strip(), btn

    @staticmethod
    async def create_button(
        text: str,
        data: str,
        with_suffix: str = "",
        style=None,
        icon_custom_emoji_id=None,
    ) -> InlineKeyboardButton:
        """Create InlineKeyboardButton with style and custom emoji support."""

        data = data.strip()

        kwargs = {
            "text": text,
        }

        # Telegram button style
        if style:
            kwargs["style"] = style

        # Custom emoji icon
        if icon_custom_emoji_id:
            kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id

        if ButtonUtils.is_url(data):
            kwargs["url"] = data

        elif ButtonUtils.is_number(data):
            kwargs["user_id"] = int(data)

        elif ButtonUtils.is_copy(data):
            kwargs["copy_text"] = data.replace(
                "copy:",
                ""
            )

        elif ButtonUtils.is_alert(data):
            alert_text = data.replace(
                "alert:",
                ""
            )

            uniq = str(uuid4().int)[:8]

            await dB.set_var(
                int(uniq),
                int(uniq),
                alert_text
            )

            kwargs["callback_data"] = f"alertcb_{uniq}"

        else:
            kwargs["callback_data"] = (
                f"{data}_{with_suffix}"
                if with_suffix
                else data
            )

        return InlineKeyboardButton(**kwargs)


    @staticmethod
    async def create_inline_keyboard(
        buttons,
        suffix: str = ""
    ) -> InlineKeyboardMarkup:
        """
        Support format:

        [
            [
                ("Buy", "buy"),
                ("Cancel", "cancel")
            ]
        ]

        With style:

        [
            [
                ("Confirm", "ok", enums.ButtonStyle.SUCCESS),
                ("Cancel", "no", enums.ButtonStyle.DANGER)
            ]
        ]

        With icon:

        [
            [
                (
                    "Buy",
                    "buy",
                    None,
                    5789175442628350606
                )
            ]
        ]
        """

        keyboard = []

        for row in buttons:
            new_row = []

            for item in row:

                text = item[0]
                data = item[1]

                style = None
                icon = None

                if len(item) >= 3:
                    style = item[2]

                if len(item) >= 4:
                    icon = item[3]

                button = await ButtonUtils.create_button(
                    text,
                    data,
                    suffix,
                    style,
                    icon
                )

                new_row.append(button)

            keyboard.append(new_row)

        return InlineKeyboardMarkup(keyboard)

    """Pre-defined keyboard templates for Pyrogram."""

    @staticmethod
    def start_menu(is_admin: bool = False) -> kb:
        """Generate start menu keyboard."""
        common_buttons = [
            ["✨ Mulai Buat Userbot"],
            ["❓ Status Akun"],
            [("⚡ Plan Lite"), ("🧩 Plan Basic"), ("💎 Plan Pro")],
            ["🔑 Token"],
            [
                ("🔄 Reset Emoji"),
                ("🔄 Reset Prefix"),
            ],
            [
                ("🔄 Restart Userbot"),
                ("🔄 Reset Text"),
            ],
            ["↩️ Beranda"],
        ]

        if not is_admin:
            common_buttons.extend([["💬 Hubungi Admins"]])

        return kb(common_buttons, resize_keyboard=True, one_time_keyboard=True)

    @staticmethod
    def start_com_button() -> kb:
        buttons = [
            [
                "🤖 Beli Userbot",
                "🛍️ Nokos",
            ],
            [
                "Support",
                "Development",
            ],
        ]

        return kb(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False,
        )

    @staticmethod
    def userbot(user_id, count):
        button = ikb(
            [
                [
                    (
                        "Delete User",
                        f"del_ubot {int(user_id)}",
                    ),
                    (
                        "Check Phone",
                        f"get_phone {int(count)}",
                    ),
                ],
                [
                    (
                        "Check Expired",
                        f"cek_masa_aktif {int(user_id)}",
                    )
                ],
                [
                    (
                        "Get Otp",
                        f"get_otp {int(count)}",
                    ),
                    (
                        "Get V2L",
                        f"get_faktor {int(count)}",
                    ),
                ],
                [
                    (
                        "Delete Account",
                        f"ub_deak {int(count)}",
                    )
                ],
                [
                    ("❮", f"prev_ub {int(count)}"),
                    ("Close", "buttonclose"),
                    ("❯", f"next_ub {int(count)}"),
                ],
            ]
        )
        return button

    @staticmethod
    def user_nokos(user_id, count):
        button = ikb(
            [
                [
                    (
                        "Check Phone",
                        f"get_phone {int(count)}",
                    ),
                ],
                [
                    (
                        "Get Otp",
                        f"get_otp {int(count)}",
                    ),
                    (
                        "Get V2L",
                        f"get_faktor {int(count)}",
                    ),
                ],
                [
                    ("❮", f"prev_ub {int(count)}"),
                    ("Close", "buttonclose"),
                    ("❯", f"next_ub {int(count)}"),
                ],
            ]
        )
        return button

    @staticmethod
    def fake_userbot(user_id, count):
        button = ikb(
            [
                [
                    (
                        "Delete User",
                        f"del_ubot {int(user_id)}",
                    ),
                ],
                [
                    (
                        "Check Expired",
                        f"cek_masa_aktif {int(user_id)}",
                    )
                ],
                [
                    ("❮", f"fakeprev_ub {int(count)}"),
                    ("Close", "buttonclose"),
                    ("❯", f"fakenext_ub {int(count)}"),
                ],
            ]
        )
        return button

    @staticmethod
    def deak(user_id, count):
        button = ikb(
            [[("⬅️", f"prev_ub {int(count)}"), ("Approve", f"deak_akun {int(count)}")]]
        )
        return button

    @staticmethod
    async def generate_inline_query(message, chat_id, bot_username, query):
        try:
            client = message._client
            results = await client.get_inline_bot_results(bot_username, query)
            if results and results.results:
                return {
                    "query_id": results.query_id,
                    "result_id": results.results[0].id,
                    "results": results.results,
                    "query": query,
                }
            return None
        except Exception:
            return None

    @staticmethod
    async def send_inline_bot_result(
        message,
        chat_id,
        bot_username,
        query,
        reply_to_message_id: Optional[int] = None,
    ) -> bool:
        client = message._client
        try:
            query_results = await ButtonUtils.generate_inline_query(
                message, chat_id, bot_username, query
            )

            if not query_results:
                return False

            data = await client.send_inline_bot_result(
                chat_id,
                query_results["query_id"],
                query_results["result_id"],
                reply_to_message_id=reply_to_message_id,
                message_thread_id=message.message_thread_id or None,
            )
            inline_id = {
                "chat": chat_id,
                "_id": data.id,
                "me": client.me.id,
                "idm": id(message),
            }
            state.set(query, query, inline_id)
            return True
        except RPCError:
            raise
        except QueryIdInvalid:
            raise
        except Exception:
            raise

    @staticmethod
    def build_buttons(data, uniq, callback, closed):
        buttons = []
        row = []
        for idx, _ in enumerate(data):
            row.append((str(idx + 1), f"{callback}{idx}_{uniq}"))
            if len(row) == 5:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([("❌ Close", f"close {closed} {uniq}")])
        return ikb(buttons)

    @staticmethod
    def plus_minus(bulan, harga, plan):
        button = ikb(
            [
                [
                    ("⁻1 bulan", f"kurang {bulan} {harga} {plan}"),
                    ("⁺1 bulan", f"tambah {bulan} {harga} {plan}"),
                ],
                [("Konfirmasi", f"confirm {bulan} {harga} {plan}")],
                [("Batal", "buttonclose")],
            ]
        )
        return button

    @staticmethod
    def chose_plan():
        button = ikb(
            [
                [
                    ("🧩 Plan Basic", f"planusers basic"),
                    ("💎 Plan Pro", f"planusers is_pro"),
                ],
                [("⚡ Plan Lite", f"planusers lite")],
                [("Batal", "buttonclose")],
            ]
        )
        return button

    @staticmethod
    def create_font_keyboard(font_list, get_id, current_batch):
        keyboard = []
        for font_dict in font_list:
            for key, value in font_dict.items():
                keyboard.append(
                    InlineKeyboardButton(
                        key, callback_data=f"get_font {get_id} {value}"
                    )
                )

        rows = [keyboard[i : i + 2] for i in range(0, len(keyboard), 2)]

        while len(rows) < 3:
            rows.append([])

        rows.append(
            [
                InlineKeyboardButton(
                    "⬅️", callback_data=f"prev_font {get_id} {current_batch}"
                ),
                InlineKeyboardButton("❌", callback_data=f"close inline_font {get_id}"),
                InlineKeyboardButton(
                    "➡️", callback_data=f"next_font {get_id} {current_batch}"
                ),
            ]
        )
        return rows


    @staticmethod
    async def nokos(page: int = 0, category_id: str = None):
        list_nokos = await db.get_nokos()

        if category_id:
            list_nokos = [
                x for x in list_nokos
                if str(x.get("_id")).startswith(str(category_id))
            ]

        if not list_nokos:
            return (
                "<blockquote><b>📱 Beli Akun Telegram</b></blockquote>\n\n"
                "❌ Tidak ada stok tersedia.",
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🏠 Beranda",
                                callback_data="back_home_nokos"
                            )
                        ]
                    ]
                )
            )

        items_page = 4
        total_items = len(list_nokos)

        max_pages = ceil(total_items / items_page)

        page = max(0, min(page, max_pages - 1))

        start = page * items_page
        end = start + items_page

        current_items = list_nokos[start:end]

        text = (
            "<blockquote><b>📱 Beli Akun Telegram</b></blockquote>\n\n"
            f"<b>📊 Total:</b> <code>{total_items}</code>\n"
            f"<b>📄 Page:</b> <code>{page + 1}/{max_pages}</code>\n\n"
        )

        buttons = []

        for num, doc in enumerate(current_items, start=start + 1):
            _id = doc.get("_id")
            price = doc.get("price")

            text += (
                f"┏ <b>{num}. Nokos Telegram</b>\n"
                f"┣ <b>ID:</b> <code>{_id}</code>\n"
                f"┣ <b>Harga:</b> <code>{price}</code>\n"
                f"┗ <b>Status:</b> Available\n\n"
            )

            buttons.append(
                InlineKeyboardButton(
                    str(num),
                    callback_data=f"buy_id_{_id}"
                )
            )

        keyboard = []

        if buttons:
            keyboard.extend(
                [
                    buttons[i:i + 4]
                    for i in range(0, len(buttons), 4)
                ]
            )

        nav_row = []

        if page > 0:
            nav_row.append(
                InlineKeyboardButton(
                    "⬅️",
                    callback_data=f"list_nokos_{page - 1}_{category_id or 'all'}"
                )
            )

        nav_row.append(
            InlineKeyboardButton(
                "🏠 Back",
                callback_data="open_nokos"
            )
        )

        if page < max_pages - 1:
            nav_row.append(
                InlineKeyboardButton(
                    "➡️",
                    callback_data=f"list_nokos_{page + 1}_{category_id or 'all'}"
                )
            )

        keyboard.append(nav_row)

        return text, InlineKeyboardMarkup(keyboard)
