import asyncio

from loguru import logger
from tortoise import Tortoise

from telethoncontrollerbot.config.config import DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_DB_NAME


async def init_tortoise(username=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, db_name=DB_DB_NAME):
    logger.debug(f"Инициализация BD {host}")
    try:
        await Tortoise.init(  # todo
            # _create_db=True,
            db_url=f"postgres://{username}:{password}@{host}:{port}/{db_name}",
            modules={"models": ["telethoncontrollerbot.db.models"]},
        )
        await Tortoise.generate_schemas()
        logger.debug(f"База данных {db_name} инициализирована")
    except Exception as e:
        logger.critical(e)
        await Tortoise.init(  # todo
            _create_db=True,
            db_url=f"postgres://{username}:{password}@{host}:{port}/{db_name}",
            modules={"models": ["telethoncontrollerbot.db.models"]},
        )
        await Tortoise.generate_schemas()
        logger.debug(f"База данных {db_name} инициализирована")


if __name__ == "__main__":
    asyncio.run(init_tortoise())
