from loguru import logger

from telethoncontrollerbot.db.models import SubscriptionInfo

SUBSCRIPTIONS_INFO: dict[int, SubscriptionInfo] = {}


async def init_subscriptions_info():
    # await init_db()
    for price in await SubscriptionInfo.all():
        SUBSCRIPTIONS_INFO[price.pk] = price
    logger.debug("Информация о подписках выгружена")
