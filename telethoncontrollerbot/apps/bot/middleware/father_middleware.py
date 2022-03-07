from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from telethoncontrollerbot.db.models import DbUser


class FatherMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        # logger.info(f"3.Process Message, {data=}")
        db_user = await DbUser.get_or_new(message.from_user.id, message.from_user.username)
        data["db_user"] = db_user
        logger.info(f"{db_user.username}[{db_user.user_id}]")
