import logging
from typing import Optional

from loguru import logger

from settings import init_logging
from pydantic import BaseModel, validator
from telethon import TelegramClient, events


# client = TelegramClient(f'_session', api_id, api_hash)
class Controller(BaseModel):
    user_id: int
    username: str
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

    def start(self):
        @self.client.on(events.NewMessage(incoming=True))
        async def my_event_handler(event: events.NewMessage):
            print(event)
            await self.client.send_message(event.sender_id, event.message)
            # if event.raw_text
            # pass

        self.client.start()
        self.client.run_until_disconnected()




if __name__ == '__main__':
    init_logging(old_logger=True, level=logging.INFO)
    api_id = 15607899
    api_hash = "b5028e57a18d6a925b305047ea954f58"
    client = Controller(user_id=1985947355, username="jeraldo_me", api_id=api_id, api_hash=api_hash)
    client.start()
