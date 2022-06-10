from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from telethoncontrollerbot.apps.controller.triggers_data import TriggerCollection


def get_trigger_menu(db_user):
    _triggers_menu_data_buttons = [
        ("➖ Отвязать аккаунт", "unlink_account") if db_user.account else ("➕ Подключить аккаунт", "connect_account"),
        ("💬 Текущие автоответы", "current_triggers"),
        ("📝 Создать новый автоответ", "new_trigger"),
        ("🔁 Перезапустить бота", "restart_controller_bot"),
    ]

    triggers_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data)] for text, data in _triggers_menu_data_buttons
        ]
    )
    return triggers_menu


_triggers_choice_type_buttons = (
    ("Все сообщения", "create_trigger_all_message"),
    ("По заданным фразам", "create_trigger_phrases"),
)

triggers_choice_type = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=data)] for text, data in _triggers_choice_type_buttons
    ]
)


def triggers_choice(count: int, add=False):
    kbr = []
    pre = 0
    for i in range(count // 6):
        kbr.append(map(str, (range(pre + 1, pre + 7))))
        pre += 6
    if count:
        kbr.append(map(str, (range(pre + 1, count + 1))))
    if add:
        kbr.append(["0"])
    return ReplyKeyboardMarkup(kbr, resize_keyboard=True)


triggers_fields = ReplyKeyboardMarkup([["Фразы", "Текст ответа"]], resize_keyboard=True)


def change_trigger_status(tr_col: TriggerCollection):
    _change_triggers_status_data = [
        (
            f"{'Отключить' if tr_col.reply_to_phrases else 'Включить'} ответ на фразы",
            "change_trigger_status_reply_to_phrases",
        ),
        (
            f"{'Отключить' if tr_col.reply_to_all else 'Включить'} ответ на любой текст сообщения",
            "change_trigger_status_reply_to_all",
        ),
        (
            f"{'Отключить' if tr_col.reply_to_groups else 'Включить'} ответ на сообщения из групп",
            "change_trigger_status_reply_to_groups",
        ),
        (
            f"{'Отключить' if tr_col.reply_to_channels else 'Включить'} ответ на сообщения из каналов",
            "change_trigger_status_reply_to_channels",
        ),
        ("Создать новый ответ", "new_trigger"),
        ("Изменить данные", "change_triggers"),
        ("Удалить ответ", "delete_triggers"),
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data)] for text, data in _change_triggers_status_data
        ]
    )
