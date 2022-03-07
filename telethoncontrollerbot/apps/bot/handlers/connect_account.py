import asyncio
import multiprocessing

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

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

    api_id, api_hash, number = message.text.split(":")
    await state.update_data(api_id=int(api_id), api_hash=api_hash, number=number)
    logger.info(f"{db_user.username}| Полученные данные {api_id}|{api_hash}|{number}")
    client = Controller(
        user_id=db_user.user_id, username=db_user.username, number=number, api_id=api_id, api_hash=api_hash
    )
    task = asyncio.create_task(client.start(new=True))
    SESSION_TASKS[db_user.user_id] = task
    # Thread(target=start_controller, args=(client.start, )).start()
    # Process(
    #     target=start_controller, args=(
    #         db_user.user_id, db_user.username, number, api_id, api_hash, queue)
    # ).start()

    # await state.update_data(queue=queue)
    await ConnectAccountStates.next()

    await message.answer(
        "Введите код подтверждения из сообщения Телеграмм с префиксом omega, в таком виде omega<ваш код>, Например:\n"
        "omega43123"
    )


async def connect_account_code(message: types.Message, db_user: DbUser, state: FSMContext):
    # code = message.text.replace("t", "")
    code = message.text.replace("omega", "")
    TEMP_DATA[db_user.user_id] = code

    await message.answer("Код получен, ожидайте завершения\n Вам придет сообщение в личный чат.")
    # data = await state.get_data()
    # queue: multiprocessing.Queue = data["queue"]
    # queue.put_nowait(code)

    # account = await Account.create(
    #     api_id=data["api_id"],
    #     api_hash=data["api_hash"],
    #     number=data["number"],
    # )
    # db_user.account = account
    # await db_user.save()
    await state.finish()


def register_connect_account_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(connect_account, text="connect_account")
    # dp.register_message_handler(connect_account_api_id, state=ConnectAccountStates.api_id)
    # dp.register_message_handler(connect_account_api_hash, state=ConnectAccountStates.api_hash)
    dp.register_message_handler(connect_account_number, state=ConnectAccountStates.number)
    dp.register_message_handler(connect_account_code, state=ConnectAccountStates.code)
