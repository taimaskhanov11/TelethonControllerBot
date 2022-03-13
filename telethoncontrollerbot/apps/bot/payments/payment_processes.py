from datetime import datetime

from loguru import logger

from telethoncontrollerbot.apps.bot.payments.yookassa_async import YooPayment
from telethoncontrollerbot.apps.controller.triggers_data import TRIGGERS_COLLECTION, TriggerCollection
from telethoncontrollerbot.db.models import Billing, TZ, DbPayment, DbTriggerCollection
from telethoncontrollerbot.loader import bot


@logger.catch
async def check_payment(bill_id, db_user):  # todo 2/28/2022 8:53 PM taima: поправить
    bill = await YooPayment.get(bill_id=bill_id)

    if bill.status == "succeeded":
        logger.info(f"{db_user.user_id}|{bill.id} успешно оплачен")
        db_bill = await Billing.get(bill_id=bill_id).prefetch_related("subscription")

        await DbPayment.create(db_user=db_user, date=datetime.now(TZ), amount=db_bill.amount)
        if db_user.subscription.title == db_bill.subscription.title:
            db_user.subscription.duration += db_bill.subscription.days_duration

            await db_user.subscription.save()
            await db_user.save()
            await db_bill.subscription.delete()
            await db_bill.delete()

            logger.info("Обновлена существующая подписка")
            await bot.send_message(db_user.user_id, "Обновлена существующая подписка")

            tr_col = TRIGGERS_COLLECTION.get(db_user.from_user.id)
            if not tr_col:
                db_trigger_coll = await DbTriggerCollection.get_or_none(db_user=db_user)
                if db_trigger_coll:
                    trigger_coll = TriggerCollection(**dict(db_trigger_coll))
                    TRIGGERS_COLLECTION[db_user.user_id] = trigger_coll
        else:
            db_bill.subscription.is_paid = True
            db_bill.subscription.is_subscribe = True
            old_sub = db_user.subscription
            db_user.subscription = db_bill.subscription

            await db_user.subscription.save()
            await db_user.save()
            await db_bill.delete()
            await old_sub.delete()
            logger.info("Создана новая подписка")



        logger.info("Информация о подписке успешно обновлена")

    elif bill.status == "canceled":
        logger.info(f"{db_user.user_id}|{bill.description} отменен")
        db_bill = await Billing.get(bill_id=bill_id).prefetch_related("subscription")

        await db_bill.subscription.delete()
        await db_bill.delete()
        logger.info("Шаблон подписки отменен")

    return bill.status
