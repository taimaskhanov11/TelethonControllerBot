from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

_triggers_menu_data_buttons = [
    ("Подключить аккаунт", "connect_account"),
    ("Текущие триггеры", "current_triggers"),
    ("Создать новый триггер", "new_trigger"),
    ("Перезапустить бота", "restart_controller_bot"),

]


def get_trigger_menu(db_user):
    triggers_menu_data_buttons = _triggers_menu_data_buttons[1:] if db_user.account else _triggers_menu_data_buttons
    triggers_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=data,
                )
            ]
            for text, data in triggers_menu_data_buttons
        ]
    )
    return triggers_menu


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


def triggers_choice(count: int):
    kbr = []
    pre = 0
    for i in range(count // 6):
        kbr.append(map(str, (range(pre + 1, pre + 7))))
        pre += 6
    if count:
        kbr.append(map(str, (range(pre + 1, count + 1))))

    return ReplyKeyboardMarkup(
        kbr,
        resize_keyboard=True
    )


triggers_fields = ReplyKeyboardMarkup(
    [["Фразы", "Текст ответа"]],
    resize_keyboard=True
)

# _triggers_fields_data = [
#     (),
#     (),
# ]
#
# triggers_fields = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text=text,
#                 callback_data=data,
#             )
#         ]
#         for text, data in _triggers_fields_data
#     ]
# )
