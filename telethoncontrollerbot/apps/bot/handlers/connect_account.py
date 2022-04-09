import asyncio
import multiprocessing

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from telethoncontrollerbot.apps.bot.filters.triggers_filters import ConnectAccountFilter, UnlinkAccountFilter
from telethoncontrollerbot.apps.bot.markups import trigger_menu
from telethoncontrollerbot.apps.controller.controller import Controller
from telethoncontrollerbot.apps.controller.session_data import SESSION_TASKS
from telethoncontrollerbot.config.config import TEMP_DATA
from telethoncontrollerbot.db.models import DbUser

queue = multiprocessing.Queue()


class ConnectAccountStates(StatesGroup):
    # api_id = State()
    # api_hash = State()
    number = State()
    code = State()


async def connect_account(call: types.CallbackQuery):
    await call.message.answer(
        "Для подключения аккаунта создайте приложение"
        " по ссылке https://my.telegram.org/auth?to=apps и сохраните api_id, api_hash.\n"
        # "Как закончите введите сюда ваш api_id"
        "Как закончите введите сюда ваши данные в формате  api_id:api_hash:номер телефона. Пример\n"
        "123445:asdf31234fads:79622231741"
    )
    # await ConnectAccountStates.api_id.set()
    await ConnectAccountStates.first()


async def connect_account_number(message: types.Message, db_user: DbUser, state: FSMContext):
    # data = await state.get_data()
    try:
        api_id, api_hash, number = message.text.split(":")
        api_id, api_hash, number = api_id.strip(), api_hash.strip(), number.strip()

        await state.update_data(api_id=int(api_id), api_hash=api_hash, number=number)
        logger.info(f"{db_user.username}| Полученные данные {api_id}|{api_hash}|{number}")
        client = Controller(
            user_id=db_user.user_id, username=db_user.username, number=number, api_id=api_id, api_hash=api_hash
        )
        task = asyncio.create_task(client.start(new=True))
        SESSION_TASKS[db_user.user_id] = task

        await ConnectAccountStates.next()

        await message.answer(
            "Введите код подтверждения из сообщения Телеграмм с префиксом code, в таком виде code<ваш код>, Например:\n"
            "code43123"
        )
    except Exception as e:
        logger.critical(e)
        await message.answer("Неправильный ввод")


async def connect_account_code(message: types.Message, db_user: DbUser, state: FSMContext):
    # code = message.text.replace("t", "")
    code = message.text.replace("code", "")
    TEMP_DATA[db_user.user_id] = code

    await message.answer("Код получен, ожидайте завершения\n Вам придет сообщение в личный чат.")

    await state.finish()


async def unlink_account(call: types.CallbackQuery, db_user: DbUser):
    task = SESSION_TASKS.get(db_user.user_id)
    if task:
        task.cancel()
        del SESSION_TASKS[db_user.user_id]

    # delete_session(db_user.user_id)
    db_user = await DbUser.get(user_id=db_user.user_id).select_related("account")
    await db_user.account.delete()
    db_user.account = None
    await db_user.save()

    await call.message.edit_reply_markup(trigger_menu.get_trigger_menu(db_user))
    # print(db_user.account)
    # await call.message.delete()
    await call.message.answer(
        "Аккаунт успешно отвязан",
        # reply_markup=trigger_menu.get_trigger_menu(db_user)
    )


def register_connect_account_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(connect_account, ConnectAccountFilter())
    dp.register_callback_query_handler(unlink_account, UnlinkAccountFilter())

    # dp.register_callback_query_handler(unlink_account, text="unlink_account")
    # dp.register_message_handler(connect_account_api_id, state=ConnectAccountStates.api_id)
    # dp.register_message_handler(connect_account_api_hash, state=ConnectAccountStates.api_hash)
    dp.register_message_handler(connect_account_number, state=ConnectAccountStates.number)
    dp.register_message_handler(connect_account_code, state=ConnectAccountStates.code)
