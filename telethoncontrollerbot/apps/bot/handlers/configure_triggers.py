import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from telethoncontrollerbot.apps.bot.filters.triggers_filters import (
    CurrentTriggersFilter,
    RestartControllerBotFilter,
    CreateTriggerFilter,
)
from telethoncontrollerbot.apps.bot.markups import trigger_menu
from telethoncontrollerbot.apps.bot.markups.trigger_menu import triggers_choice, triggers_fields
from telethoncontrollerbot.apps.controller.triggers_data import TRIGGERS_COLLECTION, Trigger, TriggerCollection
from telethoncontrollerbot.db.models import DbUser, DbTrigger, DbTriggerCollection


class AllMessageTriggerStates(StatesGroup):
    start = State()


class PhrasesTriggerStates(StatesGroup):
    answer = State()
    complete = State()


class TriggersChangeStates(StatesGroup):
    choice = State()
    field = State()
    complete = State()


class TriggersDeleteStates(StatesGroup):
    delete = State()


class AllMessageAnswerChangeStates(StatesGroup):
    start = State()


async def configure_triggers_start(message: types.Message, db_user: DbUser, state: FSMContext):
    # if not db_user.subscription.duration:
    #     await message.answer(
    #         "Подписка закончилась. Выберите новую подписку ниже", reply_markup=get_subscribe_menu_view()
    #     )
    #     return
    await state.finish()
    await message.delete()
    await message.answer("🔧 Настройка ответов:", reply_markup=trigger_menu.get_trigger_menu(db_user))


async def restart_controller_bot(call: types.CallbackQuery):
    # SESSION_TASKS[db_user.user_id].cancel()
    # acc = await Account.get(db_user=db_user)
    # asyncio.create_task(start_session(acc))
    await call.message.answer("Бот успешно перезапущен ✅")


async def current_triggers(call: types.CallbackQuery, db_user: DbUser):
    try:
        tr_col = TRIGGERS_COLLECTION[db_user.user_id]
        # print(tr_col)
        await call.message.answer(
            f"{str(tr_col)}",
            # reply_markup=triggers_choice(len(tr_col.triggers))
            reply_markup=trigger_menu.change_trigger_status(tr_col),
        )

    except Exception as e:
        logger.critical(e)
        await call.message.answer("Пусто. Задайте новые фразы ✏️")


@logger.catch
async def change_trigger_status(call: types.CallbackQuery):
    field = re.findall(r"change_trigger_status_(.*)", call.data)[0]
    tr_col = TRIGGERS_COLLECTION[call.from_user.id]
    status = getattr(tr_col, field)
    setattr(tr_col, field, not status)
    db_trigger_coll = await DbTriggerCollection.get(id=tr_col.id)
    setattr(db_trigger_coll, field, not status)
    await db_trigger_coll.save()
    # await call.message.answer("Данные обновлены")
    await call.message.edit_text(f"{str(tr_col)}\n\n")
    await call.message.edit_reply_markup(trigger_menu.change_trigger_status(tr_col))

    # await call.message.answer("Данные обновлены", reply_markup=trigger_menu.change_trigger_status(tr_col))


async def triggers_delete_start(call: types.CallbackQuery):
    tr_col = TRIGGERS_COLLECTION[call.from_user.id]
    # await call.message.delete()
    await call.message.answer(
        "✏️ Выберите номер ответа, который надо удалить:\n\n" "Для отмены введите /start",
        reply_markup=triggers_choice(len(tr_col.triggers), True),
    )
    # reply_markup=triggers_choice(27))
    await TriggersDeleteStates.first()


async def triggers_delete_start_done(message: types.Message, state: FSMContext):
    try:
        tr_col = TRIGGERS_COLLECTION[message.from_user.id]
        # await call.message.delete()
        number = int(message.text)
        if number == 0:
            await message.answer(f"Нажмите на кнопки ниже", reply_markup=triggers_choice(len(tr_col.triggers), True))
            return
        trigger = tr_col.triggers[number - 1]
        tr_col.triggers.pop(number - 1)
        db_trigger = await DbTrigger.get(id=trigger.id)
        await db_trigger.delete()
        await message.answer(
            f"Ответ успешно удален ✅\n{tr_col}",
            reply_markup=trigger_menu.change_trigger_status(tr_col)
        )
        await state.finish()
    except Exception as e:
        logger.critical(e)
        await message.answer(
            "Неправильный ввод, Для отмены нажмите /start",
        )


async def triggers_change_start(call: types.CallbackQuery):
    tr_col = TRIGGERS_COLLECTION[call.from_user.id]
    # await call.message.delete()
    await call.message.answer(
        "✏️ Для именения введите номер ответа\n\n0 - ответы на все сообщения.\nНомера других заданных ответов можно посмотреть в списке, нажав 'Текущие автоответы'.\n\n" "Для отмены введите /start",
        reply_markup=triggers_choice(len(tr_col.triggers), True),
    )
    # reply_markup=triggers_choice(27))
    await TriggersChangeStates.first()


async def triggers_change_choice(message: types.Message, state: FSMContext):
    number = int(message.text)
    if number == 0:
        await message.answer(f"️ ✏️ Ведите новый текст для ответа на любой текст сообщений:")
        await AllMessageAnswerChangeStates.start.set()
        return
    trigger = TRIGGERS_COLLECTION[message.from_user.id].triggers[number - 1]
    await state.update_data(trigger=number)
    await message.answer(f"✏️ Что будем менять?\n\n{trigger}", reply_markup=triggers_fields)
    await TriggersChangeStates.next()


async def all_message_answer_change(message: types.Message, db_user: DbUser, state: FSMContext):
    trigger_coll = TRIGGERS_COLLECTION[message.from_user.id]
    trigger_coll.all_message_answer = message.text
    db_trigger_coll = await DbTriggerCollection.get(db_user=db_user)
    db_trigger_coll.all_message_answer = message.text
    await db_trigger_coll.save(update_fields=["all_message_answer"])
    await message.answer(
        f"Данные обновлены ✅\n{trigger_coll}", reply_markup=trigger_menu.change_trigger_status(trigger_coll)
    )
    await state.finish()


async def triggers_change_field(message: types.Message, state: FSMContext):
    field = "phrases" if message.text == "Фразы" else "answer"
    await state.update_data(field=field)
    if field == "phrases":
        answer = f"✏️ Введите фразы через запятую:"
    else:
        answer = f"✏️ Введите новое значение для поля {message.text}"

    await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    await TriggersChangeStates.next()


async def triggers_change_complete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    trigger = TRIGGERS_COLLECTION[message.from_user.id].triggers[data["trigger"] - 1]
    field = data["field"]
    new_value = message.text
    if field == "phrases":
        new_value = list(map(lambda x: x.strip(), message.text.split(",")))
    setattr(trigger, field, new_value)  # todo 3/7/2022 1:54 AM taima:

    db_trigger = await DbTrigger.get(id=trigger.id)
    setattr(db_trigger, field, new_value)
    await db_trigger.save(update_fields=[field])
    logger.info(f"Trigger changed {field}|{new_value}|{type(new_value)}")
    trigger_coll = TRIGGERS_COLLECTION[message.from_user.id]
    await state.finish()
    await message.answer(
        f"Данные обновлены ✅\n{trigger_coll}", reply_markup=trigger_menu.change_trigger_status(trigger_coll)
    )


async def create_new_trigger(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("💬 На какие сообщения будем отвечать?", reply_markup=trigger_menu.triggers_choice_type)


async def create_all_message_trigger(call: types.CallbackQuery):
    await call.message.answer("✏️ Введите текст ответа на все личные сообщения:")
    await AllMessageTriggerStates.start.set()


@logger.catch
async def create_all_message_trigger_complete(message: types.Message, db_user: DbUser, state: FSMContext):
    trigger_coll = TRIGGERS_COLLECTION.get(message.from_user.id)
    text = message.text
    if trigger_coll:
        trigger_coll.all_message_answer = text
        db_trigger_coll = await DbTriggerCollection.get(id=trigger_coll.id)
        db_trigger_coll.all_message_answer = text
        await db_trigger_coll.save(update_fields=["all_message_answer"])
        logger.info(f"Обновлен текст коллекции триггеров {db_user.user_id}")
        answer = f"Успешно обновлен текст коллекции триггеров {db_user.user_id}"
    else:
        db_trigger_coll, is_created = await DbTriggerCollection.get_or_create(
            db_user=db_user, defaults={"all_message_answer": text}
        )
        trigger_coll = TriggerCollection(**dict(db_trigger_coll))
        TRIGGERS_COLLECTION[db_user.user_id] = trigger_coll
        logger.info(f"Создана новая коллекция триггеров {db_user.user_id}")
        answer = f"Успешно создана новая коллекция триггеров {db_user.user_id}"
    await message.answer(f"{answer}\n{trigger_coll}", reply_markup=trigger_menu.get_trigger_menu(db_user))
    # do something #todo 3/5/2022 3:29 PM taima:
    await state.finish()


# todo 3/5/2022 3:31 PM taima: сделать форматирование настраиваемым
async def create_phrases_trigger_phrases(call: types.CallbackQuery):
    await call.message.answer("️Введите фразы, на которые бот будет отвечать через запятую:")
    await PhrasesTriggerStates.first()


async def create_phrases_trigger_answer(message: types.Message, state: FSMContext):
    await state.update_data(phrases=message.text)
    await message.answer("️✏️ Введите текст ответа:")
    await PhrasesTriggerStates.next()


async def create_phrases_trigger_complete(message: types.Message, db_user: DbUser, state: FSMContext):
    # do something #todo 3/5/2022 3:29 PM taima:
    trigger_coll = TRIGGERS_COLLECTION.get(message.from_user.id)
    text = message.text
    data = await state.get_data()

    if trigger_coll:
        db_trigger_coll = await DbTriggerCollection.get(id=trigger_coll.id)
    else:
        db_trigger_coll, is_created = await DbTriggerCollection.get_or_create(db_user=db_user)

        trigger_coll = TriggerCollection(**dict(db_trigger_coll))
        TRIGGERS_COLLECTION[db_user.user_id] = trigger_coll
        logger.info(f"Создана новая коллекция триггеров {db_user.user_id}")
    phrases = list(map(lambda x: x.strip(), data["phrases"].split(",")))
    db_trigger = await DbTrigger.create(phrases=phrases, trigger_collection=db_trigger_coll, answer=text)

    trigger = Trigger(**dict(db_trigger))
    trigger_coll.triggers.append(trigger)
    logger.info(f"Добавлены фразы {db_user.user_id}")

    await message.answer(
        f"Триггер успешно добавлен\n{trigger_coll}", reply_markup=trigger_menu.change_trigger_status(trigger_coll)
    )
    await state.finish()


def register_configure_triggers_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(configure_triggers_start, ConfigureTriggersFilter())
    dp.register_message_handler(configure_triggers_start, text_startswith="⚙", state="*")

    dp.register_callback_query_handler(restart_controller_bot, RestartControllerBotFilter())

    dp.register_callback_query_handler(current_triggers, CurrentTriggersFilter())
    dp.register_callback_query_handler(change_trigger_status, text_startswith="change_trigger_status_")

    dp.register_callback_query_handler(triggers_change_start, text="change_triggers")
    dp.register_message_handler(triggers_change_choice, state=TriggersChangeStates.choice)

    dp.register_callback_query_handler(triggers_delete_start, text="delete_triggers")
    dp.register_message_handler(triggers_delete_start_done, state=TriggersDeleteStates.delete)

    dp.register_message_handler(all_message_answer_change, state=AllMessageAnswerChangeStates.start)
    dp.register_message_handler(triggers_change_field, state=TriggersChangeStates.field)
    dp.register_message_handler(triggers_change_complete, state=TriggersChangeStates.complete)

    dp.register_callback_query_handler(create_new_trigger, CreateTriggerFilter())

    dp.register_callback_query_handler(create_all_message_trigger, text="create_trigger_all_message")
    dp.register_message_handler(create_all_message_trigger_complete, state=AllMessageTriggerStates.start)

    dp.register_callback_query_handler(create_phrases_trigger_phrases, text="create_trigger_phrases")
    dp.register_message_handler(create_phrases_trigger_answer, state=PhrasesTriggerStates.answer)
    dp.register_message_handler(create_phrases_trigger_complete, state=PhrasesTriggerStates.complete)
