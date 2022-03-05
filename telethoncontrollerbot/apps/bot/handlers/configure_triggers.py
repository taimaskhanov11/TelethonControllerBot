from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telethoncontrollerbot.apps.bot.filters.triggers_filters import ConfigureTriggersFilter
from telethoncontrollerbot.apps.bot.markups import trigger_menu
from telethoncontrollerbot.apps.bot.markups.subscribe_menu import get_subscribe_menu_view
from telethoncontrollerbot.db.models import DbUser


class AllMessageTriggerStates(StatesGroup):
    start = State()


class PhrasesTriggerStates(StatesGroup):
    answer = State()
    complete = State()




async def configure_triggers_start(call: types.CallbackQuery, db_user: DbUser):
    if not db_user.subscription.is_subscribe:
        await call.message.answer("Подписка закончилась. Выберите новую подписку ниже",
                                  reply_markup=get_subscribe_menu_view())
        return
    await call.message.delete()
    await call.message.answer("Меню настройки триггеров", reply_markup=trigger_menu.triggers_menu)


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
    dp.register_callback_query_handler(configure_triggers_start, ConfigureTriggersFilter())
    dp.register_callback_query_handler(create_new_trigger, text="new_trigger")

    dp.register_callback_query_handler(create_all_message_trigger, text="create_trigger_all_message")
    dp.register_callback_query_handler(create_all_message_trigger_complete, state=AllMessageTriggerStates.start)

    dp.register_callback_query_handler(create_phrases_trigger_phrases, text="create_trigger_phrases")
    dp.register_callback_query_handler(create_phrases_trigger_answer, state=PhrasesTriggerStates.answer)
    dp.register_callback_query_handler(create_phrases_trigger_complete, state=PhrasesTriggerStates.complete)
