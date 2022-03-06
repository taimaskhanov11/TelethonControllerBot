from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from telethoncontrollerbot.apps.bot.utils.subscription_info import SUBSCRIPTIONS_INFO



admin_start = ReplyKeyboardMarkup(
    [[KeyboardButton("/start"), KeyboardButton("/admin_start")]], resize_keyboard=True
)

admin_menu_main_data = [
    ("Общая информация о боте", "bot_info"),
    ("Вывести список всех пользователей", "all_users"),
    ("Информация о конкретном пользователе", "user_info"),
    ("Настройка работы бота", "bot_settings"),
]

admin_menu_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=data,
            )
        ]
        for text, data in admin_menu_main_data
    ]
)

admin_menu_data = [
    ("Посмотреть подписки", "view_all_subscriptions"),
    ("Создать новую подписку", "create_subscription"),
    # todo 3/1/2022 10:26 PM taima:
]
btn_admin_menu = [
    [
        InlineKeyboardButton(
            text=text,
            callback_data=data,
        )
    ]
    for text, data in admin_menu_data
]
menu = InlineKeyboardMarkup(inline_keyboard=btn_admin_menu)


# ********************
# create subscription
class KBRSubscriptionField:
    days = ReplyKeyboardMarkup([["10", "30", "45"]], resize_keyboard=True)

    daily_limit = ReplyKeyboardMarkup(
        [["20", "100", "Unlimited"]], resize_keyboard=True
    )

    price = ReplyKeyboardMarkup([["100", "500", "1500"]], resize_keyboard=True)


# ******************


def get_current_sub_info():
    current_sub_info = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=sub_info.title,
                    callback_data=f"view_subscription_{pk}",
                )
            ]
            for pk, sub_info in SUBSCRIPTIONS_INFO.items()
        ]
    )
    return current_sub_info


change_field = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=title,
                callback_data=field,
            )
        ]
        for title, field in (
            ("Изменить название", "title"),
            ("Изменить длительность подписки", "days"),
            ("Изменить цену", "price"),
            ("Удалить подписку", "delete"),
        )
    ]
)

change_user_sub_field = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=title,
                callback_data=field,
            )
        ]
        for title, field in (
            # ("Изменить название", "title"), #todo 3/3/2022 10:14 PM taima:
            ("Изменить длительность подписки", "days_duration"),
            ("Изменить дневной лимит", "daily_limit"),
            ("Изменить количество оставшихся запросов", "remaining_daily_limit"),
        )
    ]
)