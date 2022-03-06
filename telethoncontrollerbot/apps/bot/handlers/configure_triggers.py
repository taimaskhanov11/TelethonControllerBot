import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from telethoncontrollerbot.apps.bot.filters.triggers_filters import ConfigureTriggersFilter, CurrentTriggersFilter, \
    RestartControllerBotFilter
from telethoncontrollerbot.apps.bot.markups import trigger_menu
from telethoncontrollerbot.apps.bot.markups.subscribe_menu import get_subscribe_menu_view
from telethoncontrollerbot.apps.bot.markups.trigger_menu import triggers_choice, triggers_fields
from telethoncontrollerbot.apps.controller.controller_data import USERS_TRIGGERS_COLLECTION
from telethoncontrollerbot.apps.controller.session_data import SESSION_TASKS, start_session
from telethoncontrollerbot.db.models import DbUser, Account


class AllMessageTriggerStates(StatesGroup):
    start = State()


class PhrasesTriggerStates(StatesGroup):
    answer = State()
    complete = State()


class TriggersChangeStates(StatesGroup):
    choice = State()
    field = State()
    complete = State()


async def current_triggers(call: types.CallbackQuery, db_user: DbUser):
    triggers_str = ""
    tr_col = USERS_TRIGGERS_COLLECTION[call.from_user.id]
    await call.message.answer(f"{str(tr_col)}\n\nВыберите цифру для изменения",
                              reply_markup=triggers_choice(len(tr_col.triggers)))
    # reply_markup=triggers_choice(27))
    await TriggersChangeStates.first()


async def triggers_change_choice(message: types.Message, state: FSMContext):
    number = int(message.text) - 1
    trigger = USERS_TRIGGERS_COLLECTION[message.from_user.id].triggers[number]
    await state.update_data(trigger=trigger)
    await message.answer(f"Выберите поле для изменения\n{trigger}", reply_markup=triggers_fields)
    await TriggersChangeStates.next()


async def triggers_change_field(message: types.Message, state: FSMContext):
    field = "phrases" if message.text == "Фразы" else "answer"
    await state.update_data(field=field)
    if field == "phrases":
        answer = f"Введите фразы через запятую"
    else:
        answer = f"Ведите новое значение для поля {message.text}"

    await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    await TriggersChangeStates.next()


async def triggers_change_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    trigger = data["trigger"]
    field = data["field"]
    if field == "phrases":
        phrases = map(lambda x: x.strip(), message.text.split(","))
        setattr(trigger, field, phrases)  # todo 3/7/2022 1:54 AM taima:
    else:
        setattr(trigger, field, message.text)  # todo 3/7/2022 1:54 AM taima:
    await message.answer(f"Данные обновлены\n{trigger}")


async def restart_controller_bot(call: types.CallbackQuery, db_user: DbUser):
    SESSION_TASKS[db_user.user_id].cancel()
    acc = await Account.get(db_user=db_user)
    asyncio.create_task(start_session(acc))
    await call.message.answer("Бот успешно перезапущены")


async def configure_triggers_start(call: types.CallbackQuery, db_user: DbUser):
    if not db_user.subscription.duration:
        await call.message.answer("Подписка закончилась. Выберите новую подписку ниже",
                                  reply_markup=get_subscribe_menu_view())
        return
    await call.message.delete()
    await call.message.answer("Меню настройки триггеров", reply_markup=trigger_menu.get_trigger_menu(db_user))


async def create_new_trigger(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Выберите на какие сообщения отвечать", reply_markup=trigger_menu.triggers_choice_type)


async def create_all_message_trigger(message: types.Message):
    await message.answer("Выберите текст ответа на все личные сообщения!")
    await AllMessageTriggerStates.start.set()


async def create_all_message_trigger_complete(message: types.Message, state: FSMContext):
    # do something #todo 3/5/2022 3:29 PM taima:
    await state.finish()


# todo 3/5/2022 3:31 PM taima: сделать форматирование настраиваемым
async def create_phrases_trigger_phrases(call: types.CallbackQuery, ):
    await call.message.answer("Задайте фразы через запятую")
    await PhrasesTriggerStates.first()


async def create_phrases_trigger_answer(message: types.Message, ):
    await message.answer("Задайте текст ответа")
    await PhrasesTriggerStates.next()


async def create_phrases_trigger_complete(call: types.CallbackQuery, state: FSMContext):
    # do something #todo 3/5/2022 3:29 PM taima:
    await call.message.answer("Триггер успешно добавлен")
    await state.finish()


def register_configure_triggers_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(restart_controller_bot, RestartControllerBotFilter())

    dp.register_callback_query_handler(current_triggers, CurrentTriggersFilter())
    dp.register_message_handler(triggers_change_choice, state=TriggersChangeStates.choice)
    dp.register_message_handler(triggers_change_field, state=TriggersChangeStates.field)
    dp.register_message_handler(triggers_change_complete, state=TriggersChangeStates.complete)

    dp.register_callback_query_handler(configure_triggers_start, ConfigureTriggersFilter())
    dp.register_callback_query_handler(create_new_trigger, text="new_trigger")

    dp.register_callback_query_handler(create_all_message_trigger, text="create_trigger_all_message")
    dp.register_callback_query_handler(create_all_message_trigger_complete, state=AllMessageTriggerStates.start)

    dp.register_callback_query_handler(create_phrases_trigger_phrases, text="create_trigger_phrases")
    dp.register_callback_query_handler(create_phrases_trigger_answer, state=PhrasesTriggerStates.answer)
    dp.register_callback_query_handler(create_phrases_trigger_complete, state=PhrasesTriggerStates.complete)
