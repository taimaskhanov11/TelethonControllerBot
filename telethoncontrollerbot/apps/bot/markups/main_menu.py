from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

_main_menu_buttons = (
    # ("Начать тестовый период","1" ),
    ("👤 Мой профиль", "profile"),
    ("💳 Купить подписку", "buy_sub"),
    # ("Продлить подписку","2"),
    ("⚙ Настроить автоответы", "configure_triggers"),
)
main_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=data)] for text, data in _main_menu_buttons]
)

main_menu_common = ReplyKeyboardMarkup(
    [[btn[0] for btn in _main_menu_buttons[:2]], ["⚙ Настроить автоответы"]], resize_keyboard=True
)
