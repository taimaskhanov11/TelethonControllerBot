import asyncio
import time
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel, validator
from telethon import TelegramClient, events

from telethoncontrollerbot.apps.controller.triggers_data import TRIGGERS_COLLECTION
from telethoncontrollerbot.config import config
from telethoncontrollerbot.config.config import TEMP_DATA
from telethoncontrollerbot.db.models import DbUser, Account
from telethoncontrollerbot.loader import bot

# client = TelegramClient(f'_session', api_id, api_hash)

SESSION_PATH = Path(Path(__file__).parent, "sessions")


class Controller(BaseModel):
    user_id: int
    username: Optional[str]
    number: str
    api_id: int
    api_hash: str
    client: Optional[TelegramClient]

    @validator("client", always=True)
    def create_client(cls, value, values):
        if isinstance(value, TelegramClient):
            return value
        path = str(Path(SESSION_PATH, f"{values['user_id']}_{values['username']}_session.session"))
        logger.info(path)
        # exit()
        return TelegramClient(
            path,
            # f"{values.get('username')}_{values['user_id']}_session",
            values["api_id"],
            values["api_hash"],
            # proxy=("HTTP", "45.129.7.23", 8000)
        )

    class Config:
        arbitrary_types_allowed = True

    async def wait_code2(self):

        for _ in range(4):
            logger.debug(f"Ожидание кода {self.username}|{self.number}")
            code = TEMP_DATA.get(self.user_id)
            if code:
                # del TEMP_DATA[self.user_id]
                logger.warning(f"Код найден {code}")
                return int(code)
            await asyncio.sleep(5)
            # time.sleep(4)
        return

    async def wait_code(self):
        logger.debug(f"Ожидание кода {self.username}|{self.number}")
        await asyncio.sleep(20)
        code = TEMP_DATA.get(self.user_id)
        logger.warning(f"Код найден {code}")
        # del TEMP_DATA[self.user_id]
        return code

    def wait_code3(self):
        logger.debug(f"Ожидание кода {self.username}|{self.number}")
        time.sleep(20)
        code = TEMP_DATA.get(self.user_id)
        logger.warning(f"Код найден {code}")
        # del TEMP_DATA[self.user_id]
        return lambda: code

    async def connect(self, new):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            sent_code = await self.client.send_code_request(self.number)
            code = None
            for i in range(3):
                logger.info("Ожидание кода")
                await asyncio.sleep(10)
                code = TEMP_DATA.get(self.user_id)
                if code:
                    logger.success(f"Код найден {code}")
                    break
            if code:
                # await self.client.sign_in(self.number, lambda: code)
                await self.client.sign_in(phone=self.number, code=code, phone_code_hash=sent_code.phone_code_hash)

        if await self.client.is_user_authorized():
            await self.client.send_message("me", "Бот успешно запущен!")
            logger.success(f"Успешный вход {self.username}|{self.number}|{self.user_id}")
            if new:
                await bot.send_message(self.user_id, "Бот успешно подключен. Можете начать изменять триггеры в меню")
                db_user = await DbUser.get(user_id=self.user_id)
                account = await Account.create(api_id=self.api_id, api_hash=self.api_hash, number=self.number)
                db_user.account = account
                await db_user.save()
                logger.success("Данные аккаунта созданы")
            await self.client.run_until_disconnected()
        else:
            await bot.send_message(self.user_id, "Ошибка при подключении аккаунта\nПовторите попытку подключения")
            logger.warning(f"{self.user_id}|Не удалось подключиться к системе")

    @logger.catch
    async def start(self, new=False):
        """Настройка ответов на сообщения"""

        @self.client.on(events.NewMessage(incoming=True))
        async def my_event_handler(event: events.NewMessage.Event):

            if self.user_id in TRIGGERS_COLLECTION:
                if event.chat_id == config.BOT_ID:
                    logger.trace("От себя")
                    pass
                else:
                    trigger_collection = TRIGGERS_COLLECTION[self.user_id]
                    if trigger_collection.all_message_answer or trigger_collection.reply_to_phrases:
                        # message:patched.Message = event.message
                        logger.debug(f"Поиск ответа -> {event.message.text}")
                        logger.trace(event)
                        answer = trigger_collection.get_answer(event)
                        if answer:
                            logger.success(f"Answer find {answer}")
                            await self.client.send_message(await event.get_chat(), answer)

        await self.connect(new)


def delete_session(user_id: int):
    user_id = str(user_id)
    for i in SESSION_PATH.iterdir():
        if i.name.startswith(user_id):
            i.unlink()
            logger.info(f"Сессия {user_id} успешно удалена")


def start_controller(user_id, username, number, api_id, api_hash, queue):
    client = Controller(user_id=user_id, username=username, number=number, api_id=api_id, api_hash=api_hash)

    asyncio.run(client.start(queue))


if __name__ == "__main__":
    delete_session(1985947355)

    # init_logging(old_logger=True, level=logging.INFO)
    # api_id = 16629671
    # api_hash = "8bb51f9d62e259d5e893ccb02d133b2a"
    # client = Controller(user_id=5050812985, username=None, number="79647116291", api_id=api_id, api_hash=api_hash)
    # asyncio.run(client.start())
    # client.start()
