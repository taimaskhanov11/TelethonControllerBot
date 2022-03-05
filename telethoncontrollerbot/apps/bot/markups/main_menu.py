from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

_main_menu_buttons = (
    # ("Начать тестовый период","1" ),
    ("Мой профиль", "profile"),
    ("Купить подписку", "buy_sub"),
    # ("Продлить подписку","2"),
    ("Настроить тригерры", "configure_triggers"),
)
main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=data,
            )
        ]
        for text, data in _main_menu_buttons
    ]
)
