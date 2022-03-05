import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from telethoncontrollerbot.apps.controller.controller import Controller
from telethoncontrollerbot.config.config import TEMP_DATA
from telethoncontrollerbot.db.models import DbUser


class ConnectAccountStates(StatesGroup):
    api_id = State()
    api_hash = State()
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
    await ConnectAccountStates.number.set()


async def connect_account_api_id(message: types.Message, state: FSMContext):
    await state.update_data(api_id=int(message.text))
    await ConnectAccountStates.next()
    await message.answer("Введите ваш api_hash")


async def connect_account_api_hash(message: types.Message, state: FSMContext):
    await state.update_data(api_hash=message.text)
    await ConnectAccountStates.next()
    await message.answer("Введите ваш номер телефона")


async def connect_account_number(message: types.Message, db_user: DbUser, state: FSMContext):
    # data = await state.get_data()

    api_id, api_hash, number = message.text.split(":")

    logger.info(f"{db_user.username}| Полученные данные {api_id}|{api_hash}|{number}")
    client = Controller(
        user_id=db_user.user_id,
        username=db_user.username,
        number=number,
        api_id=api_id,
        api_hash=api_hash
    )

    asyncio.create_task(client.start())

    await ConnectAccountStates.next()

    await message.answer("Введите код подтверждения из сообщения Телеграмм")


async def connect_account_code(message: types.Message, db_user: DbUser, state: FSMContext):
    TEMP_DATA[db_user.user_id] = message.text
    await message.answer("Код получен, ожидайте завершения")
    await state.finish()


def register_connect_account_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(connect_account, text="connect_account")
    dp.register_message_handler(connect_account_api_id, state=ConnectAccountStates.api_id)
    dp.register_message_handler(connect_account_api_hash, state=ConnectAccountStates.api_hash)
    dp.register_message_handler(connect_account_number, state=ConnectAccountStates.number)
    dp.register_message_handler(connect_account_code, state=ConnectAccountStates.code)
