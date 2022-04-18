import asyncio
import datetime

from loguru import logger

from telethoncontrollerbot.apps.controller.triggers_data import TRIGGERS_COLLECTION
from telethoncontrollerbot.config.config import TZ
from telethoncontrollerbot.db.db_main import init_tortoise
from telethoncontrollerbot.db.models import Subscription
from telethoncontrollerbot.loader import bot


@logger.catch
async def everyday_processes(start=True):
    update_date = datetime.timedelta(hours=24, minutes=0, seconds=0)
    if start:
        dt = datetime.datetime.now(TZ)
        dttd = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
        update_date = update_date - dttd
    total_seconds = update_date.total_seconds()
    logger.debug(f"Ожидание ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")

    # await asyncio.sleep(10)  # todo 2/27/2022 2:06 PM taima:
    await asyncio.sleep(total_seconds)  # todo 2/27/2022 2:06 PM taima:

    logger.debug(f"Обновление ежедневного лимита запросов  |{start=}|{update_date}|{total_seconds}s")
    # await asyncio.sleep(10)
    # now_dt = datetime.datetime.now(TZ)
    for sub in await Subscription.all().select_related("db_user"):
        if sub.is_paid:
            if sub.db_user:
                logger.debug(f"Проверка подписки|\n{sub.db_user.username}|{sub.db_user.user_id}")
                if sub.duration > 0:
                    sub.duration -= 1
                    # Проверка подписки
                    if sub.duration == 0:
                        if sub.db_user.user_id in TRIGGERS_COLLECTION:
                            del TRIGGERS_COLLECTION[sub.db_user.user_id]
                        logger.debug(f"Подписка закончилась {repr(sub.db_user)} ")
                        # await bot.send_message(sub.db_user.user_id, f"Подписка {sub.title} закончилась")
                        try:
                            await bot.send_message(sub.db_user.user_id, f"Подписка закончилась")
                        except Exception as e:
                            logger.critical(e)

                        # sub.db_user.subscription = await Subscription.create()
                        # await sub.db_user.save()
                        # await sub.delete()
                        # continue
                    await sub.save()
                    # await bot.send_message(
                    #     sub.db_user.user_id,
                    #     f"Дневной лимит запросов обновлен.\n" f"У вас сейчас {sub.daily_limit}",
                    # )

    logger.debug("Дневные процессы обновлены")
    logger.info(
        f"Ежедневный лимит запросов обновлен |{start=}|{update_date}|{total_seconds}s. Следующая проверка через 24 часа"
    )
    asyncio.create_task(everyday_processes(start=False))


async def main():
    await init_tortoise()
    await everyday_processes()


if __name__ == "__main__":
    asyncio.run(main())
