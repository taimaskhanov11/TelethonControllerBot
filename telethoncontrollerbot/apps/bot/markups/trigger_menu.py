from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

_triggers_menu_data_buttons = (
    ("Подключить аккаунт", "connect_account"),
    ("Текущие триггеры", "current_triggers"),
    ("Создать новый триггер", "new_trigger"),
    # (),
    # (),
)
triggers_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=data,
            )
        ]
        for text, data in _triggers_menu_data_buttons
    ]
)

_triggers_choice_type_buttons = (
    ("Все сообщения", "create_trigger_all_message"),
    ("По заданным фразам", "create_trigger_phrases"),
)

triggers_choice_type = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=text,
                callback_data=data,
            )
        ]
        for text, data in _triggers_choice_type_buttons
    ]
)
