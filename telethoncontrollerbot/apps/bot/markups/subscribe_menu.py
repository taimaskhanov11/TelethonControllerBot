from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from telethoncontrollerbot.apps.bot.utils.subscription_info import SUBSCRIPTIONS_INFO


def get_subscribe_menu_pay(pk: int):
    btn_pay = [InlineKeyboardButton(text="✅ Перейти к оплате", callback_data=f"subscribe_{pk}")]

    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=[btn_pay],
        # row_width=3
    )
    return subscribe_menu


def get_subscribe_menu_view():
    btns_subscribe = [
        [InlineKeyboardButton(text=sub.title, callback_data=f"view_buy_{pk}")] for pk, sub in SUBSCRIPTIONS_INFO.items()
    ]
    subscribe_menu = InlineKeyboardMarkup(
        inline_keyboard=btns_subscribe,
        # row_width=3
    )

    return subscribe_menu


def get_subscribe_payment(url):
    qiwi_menu = InlineKeyboardMarkup()
    btn_url = InlineKeyboardButton(text="✅ Перейти к оплате", url=url)
    btn_accept = InlineKeyboardButton(
        text="⌛️Я ОПЛАТИЛ", callback_data="accept_payment"  # todo 2/28/2022 6:15 PM taima:
    )
    btn_reject = InlineKeyboardButton(text="❌ Отменить", callback_data="reject_payment")
    qiwi_menu.add(btn_url)
    qiwi_menu.add(btn_accept)
    qiwi_menu.add(btn_reject)
    return qiwi_menu


def renew_subscription(title):  # todo 3/2/2022 3:21 PM taima:

    for pk, item in SUBSCRIPTIONS_INFO.items():
        if item.title == title:
            break
    else:
        return
    btn_renew = [[InlineKeyboardButton(text="Продлить подписку", callback_data=f"view_buy_{pk}")]]

    renew = InlineKeyboardMarkup(
        inline_keyboard=btn_renew
        # row_width=3
    )
    return renew
