import traceback
import random
from command import (an1cb, back_home, calculator_callback, callback_alert, cancel_payment,
                     cb_help, cb_markdown, cb_notes, cek_expired_cb,
                     cek_status_akun, chat_gpt, chose_plan, cine_plax,
                     closed_bot, closed_user, confirm_pay, contact_admins,
                     copy_msg, del_userbot, dl_spot, dl_ytsearch,
                     general_plugins, get_bio, get_font, gpt_voice,
                     kurang_tambah, mari_buat_userbot, moddycb, news_,
                     next_font, nxt_spotify, nxt_ytsearch, nxtbmkg, pm_warn,
                     prev_font, prevnext_userbot, prevnext_userbot2,
                     refresh_cat, reset_costum_text, reset_emoji, reset_prefix,
                     rest_anime, rest_comic, rest_donghua, restart_userbot,
                     selected_topic, token_cmd, tools_token, tools_userbot,
                     user_aggre, viewchord, viewgempa, drakorcb, cb_page_shop, cb_shop, open_nokos, open_nokos_cb, buy_nokos_payment, cancel_nokos_payment, mari_buat_nokos)
from helpers import CMD, trigger, Message
from logs import logger
from pyrogram.helpers import ikb, kb
from config import SUDO_OWNERS
from helpers import ButtonUtils, Basic_Effect


@CMD.REGEX(trigger)
async def _(client, message):
    try:
        text = message.text
        print(repr(text))
        if text in [
            "✨ Mulai Buat Userbot",
            "✨ Pembuatan Ulang Userbot",
            "✅ Lanjutkan Buat Userbot",
        ]:
            return await mari_buat_userbot(client, message)
        elif text in ["💎 Plan Pro", "🧩 Plan Basic", "⚡ Plan Lite"]:
            return await general_plugins(client, message)
        elif text == "✅ Restock Nokos":
            return await mari_buat_nokos(client, message)
        elif text == "❓ Status Akun":
            return await cek_status_akun(client, message)
        elif text.startswith("🔄 Reset"):
            data = text.split(" ")[2]
            if data == "Emoji":
                return await reset_emoji(client, message)
            elif data == "Prefix":
                return await reset_prefix(client, message)
            elif data == "Text":
                return await reset_costum_text(client, message)
        elif text == "🔄 Restart Userbot":
            return await restart_userbot(client, message)
        elif text == "💬 Hubungi Admins":
            return await contact_admins(client, message)
        elif text == "🔑 Token":
            return await token_cmd(client, message)
        elif text == "🤖 Beli Userbot":

            if message.from_user.id in SUDO_OWNERS:
                buttons = ButtonUtils.start_menu(is_admin=True)
            else:
                buttons = ButtonUtils.start_menu(is_admin=False)

            return await message.reply(
                "Silahkan pilih menu userbot:",
                reply_markup=buttons,
                message_effect_id=random.choice(Basic_Effect),
            )

        elif text == "🛍️ Nokos":
            return await open_nokos(client, message)

        # elif query == "open_nokos":
            # return await open_nokos_cb(client, callback)

        # elif query.startswith("shop"):
            # return await cb_shop(client, callback)

        elif text == "Support":
            return await message.reply(
                "Support:\nhttps://t.me/zpsexz"
            )

        elif text == "Development":
            return await message.reply(
                "Development:\nhttps://t.me/959792624119"
            )
        elif text in ["↩️ Beranda", "🏠 Beranda"]:
            buttons = ButtonUtils.start_com_button()
            text_msg = await Message.welcome_message(client, message)

            return await message.reply(
                text_msg,
                reply_markup=buttons,
                disable_web_page_preview=True,
                message_effect_id=random.choice(Basic_Effect),
            )
        elif text == "📦 Cek Stok":
            buttons = kb(
                [
                    [
                        "ID 1",
                        "ID 2",
                    ],
                    [
                        "ID 3",
                        "ID 4",
                    ],
                    [
                        "ID 5",
                        "ID 6",
                    ],
                    [
                        "ID 7",
                        "ID 8",
                    ],
                    [
                        "ID (9DIGIT)",
                    ],
                    [
                        "⬅️ Back"
                    ]
                ],
                resize_keyboard=True
            )

            return await message.reply(
                "Pilih kategori ID:",
                reply_markup=buttons
            )

        elif text == "🛒 Order Akun":
            buttons = kb(
                [
                    [
                        "ID 1",
                        "ID 2",
                    ],
                    [
                        "ID 3",
                        "ID 4",
                    ],
                    [
                        "ID 5",
                        "ID 6",
                    ],
                    [
                        "ID 7",
                        "ID 8",
                    ],
                    [
                        "ID (9DIGIT)",
                    ],
                    [
                        "⬅️ Back"
                    ]
                ],
                resize_keyboard=True
            )

            return await message.reply(
                "Pilih kategori ID:",
                reply_markup=buttons
            )

        elif text.startswith("ID "):
            category_id = text.split(" ")[1]

            text_msg, button = await ButtonUtils.nokos(
                0,
                category_id
            )

            return await message.reply(
                text_msg,
                reply_markup=button
            )

        elif text == "⬅️ Back":
            return await open_nokos(client, message)

    except Exception as er:
        logger.error(f"Terjadi error: {str(er)}")


@CMD.CALLBACK()
async def _(client, callback):
    try:
        query = callback.data
        logger.info(f"Name callback query: {query}")
        if query == "buttonclose":
            return await closed_bot(client, callback)
        elif query == "starthome":
            return await back_home(client, callback)
        elif query == "start_home":
            return await back_awal(client, callback)

        elif query == "open_nokos":
            return await open_nokos_cb(client, callback)

        elif query == "back_home_nokos":
            buttons = ButtonUtils.start_com_button()

            text_msg = await Message.welcome_message(
                client,
                callback.message
            )
            await callback.answer()
            await callback.message.delete()

            return await callback.message.reply(
                text_msg,
                reply_markup=buttons,
                disable_web_page_preview=True,
                message_effect_id=random.choice(Basic_Effect),
            )

        elif query.startswith("shop"):
            return await cb_shop(client, callback)
 
        elif query.startswith("list_nokos_"):
            return await cb_page_shop(client, callback)

        elif query.startswith("close"):
            return await closed_user(client, callback)
        elif query.startswith("pm_warn"):
            return await pm_warn(client, callback)
        elif query.startswith("getbio_"):
            return await get_bio(client, callback)
        elif query.startswith("copymsg_"):
            return await copy_msg(client, callback)
        elif query.startswith("cb_"):
            return await cb_notes(client, callback)
        elif query.startswith("get_font"):
            return await get_font(client, callback)
        elif query.startswith("prev_font"):
            return await prev_font(client, callback)
        elif query.startswith("next_font"):
            return await next_font(client, callback)
        elif query.startswith("refresh_cat"):
            return await refresh_cat(client, callback)
        elif query.startswith("nxtspotify"):
            return await nxt_spotify(client, callback)
        elif query.startswith("dlspot"):
            return await dl_spot(client, callback)
        elif query.startswith("restanime_"):
            return await rest_anime(client, callback)
        elif query.startswith("restdonghua_"):
            return await rest_donghua(client, callback)
        elif query.startswith("restcomic_"):
            return await rest_comic(client, callback)
        elif query.startswith("news_"):
            return await news_(client, callback)
        elif query.startswith("chatgpt_"):
            return await chat_gpt(client, callback)
        elif query.startswith("gptvoice_"):
            return await gpt_voice(client, callback)
        elif query.startswith("cineplax"):
            return await cine_plax(client, callback)

        elif query == ("go_payment"):
            return await user_aggre(client, callback)
        elif query.startswith("kurang") or query.startswith("tambah"):
            return await kurang_tambah(client, callback)
        elif query.startswith("confirm"):
            return await confirm_pay(client, callback)
        elif query == ("batal_payment"):
            return await cancel_payment(client, callback)

        elif query.startswith("del_ubot"):
            return await del_userbot(client, callback)
        elif query.startswith("prev_ub") or query.startswith("next_ub"):
            return await prevnext_userbot(client, callback)
        elif query.startswith("fakeprev_ub") or query.startswith("fakenext_ub"):
            return await prevnext_userbot2(client, callback)
        elif (
            query.startswith("get_otp")
            or query.startswith("get_phone")
            or query.startswith("get_faktor")
            or query.startswith("ub_deak")
            or query.startswith("deak_akun")
        ):
            return await tools_userbot(client, callback)
        elif query.startswith("use_token") or query.startswith("revoke_token"):
            return await tools_token(client, callback)

        elif query.startswith("markdown"):
            return await cb_markdown(client, callback)
        elif query.startswith("help_"):
            return await cb_help(client, callback)
        elif query.startswith("cek_masa_aktif"):
            return await cek_expired_cb(client, callback)
        elif query.startswith("viewchord_"):
            return await viewchord(client, callback)
        elif query.startswith("viewgempa_"):
            return await viewgempa(client, callback)
        elif query.startswith("nxtbmkg_"):
            return await nxtbmkg(client, callback)
        elif query.startswith("planusers"):
            return await chose_plan(client, callback)
        elif query.startswith("alertcb_"):
            return await callback_alert(client, callback)
        elif query.startswith("an1cb_"):
            return await an1cb(client, callback)
        elif query.startswith("moddycb_"):
            return await moddycb(client, callback)
        elif query.startswith("calculatorcb_"):
            return await calculator_callback(client, callback)
        elif query.startswith("dlytsearch_"):
            return await dl_ytsearch(client, callback)
        elif query.startswith("nxtytsearch_"):
            return await nxt_ytsearch(client, callback)
        elif query.startswith("selectedtopic_"):
            return await selected_topic(client, callback)
        elif query.startswith("drakorcb_"):
            return await drakorcb(client, callback)
        elif query.startswith("list_nokos_"):
            return await cb_page_shop(client, callback)
        elif query.startswith("shop"):
            return await cb_shop(client, callback)
        elif query.startswith("buy_id_"):
            return await buy_nokos_payment(client, callback)
        elif query == "batal_nokos_payment":
            return await cancel_nokos_payment(client, callback)
    except Exception:
        logger.error(f"Callback error: {traceback.format_exc()}")
