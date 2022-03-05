import asyncio
import logging
import time
from typing import Optional

from loguru import logger

from pydantic import BaseModel, validator
from telethon import TelegramClient, events

# client = TelegramClient(f'_session', api_id, api_hash)
from telethoncontrollerbot.apps.controller.settings import init_logging
from telethoncontrollerbot.config.config import TEMP_DATA


class Controller(BaseModel):
    user_id: int
    username: str
    number: str
    api_id: int
    api_hash: str
    client: Optional[TelegramClient]

    @validator("client", always=True)
    def create_client(cls, value, values):
        if isinstance(value, TelegramClient):
            return value
        return TelegramClient(f"{values['username']}_{values['user_id']}_session", values["api_id"], values["api_hash"])

    class Config:
        arbitrary_types_allowed = True

    async def wait_code(self, ):
        for _ in range(3):
            logger.debug(f"Ожидание кода {self.username}|{self.number}")
            code = TEMP_DATA.get(self.user_id)
            if code:
                del TEMP_DATA[self.user_id]
                logger.warning(f"Код найден {code}")
                return code
            await asyncio.sleep(4)
            # time.sleep(4)
        return

    @logger.catch
    async def start(self):

        @self.client.on(events.NewMessage(incoming=True))
        async def my_event_handler(event: events.NewMessage):
            print(event)
            await self.client.send_message(await event.get_chat(), event.message)
            # if event.raw_text
            # pass


        await self.client.start(
            phone=lambda: self.number,
            code_callback=self.wait_code
            # code_callback=lambda: TEMP_DATA.get(self.user_id)
        )


        await self.client.send_message('me', 'Бот успешно запущен!')
        await self.client.run_until_disconnected()


if __name__ == '__main__':
    init_logging(old_logger=True, level=logging.INFO)
    api_id = 15607899
    api_hash = "b5028e57a18d6a925b305047ea954f58"
    client = Controller(user_id=1985947355, username="jeraldo_me1", number="79697731741", api_id=api_id,
                        api_hash=api_hash)
    asyncio.run(client.start())
    # client.start()
