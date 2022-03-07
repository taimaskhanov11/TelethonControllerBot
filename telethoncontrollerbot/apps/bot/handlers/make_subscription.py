import re

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from loguru import logger

from telethoncontrollerbot.apps.bot.filters.payment_filters import (
    ViewSubscriptionFilter,
    SubscribeFilter,
    RejectPaymentFilter,
    AcceptPaymentFilter,
)
from telethoncontrollerbot.apps.bot.markups.subscribe_menu import (
    get_subscribe_menu_view,
    get_subscribe_payment,
    get_subscribe_menu_pay,
)
from telethoncontrollerbot.apps.bot.payments.payment_processes import check_payment
from telethoncontrollerbot.apps.bot.payments.yookassa_async import YooPayment
from telethoncontrollerbot.apps.bot.utils.subscription_info import SUBSCRIPTIONS_INFO
from telethoncontrollerbot.db.models import DbUser, Billing


class BuySubscription(StatesGroup):
    start = State()


async def buy_sub(call: types.CallbackQuery):
    try:
        await call.message.delete()
        await call.message.answer("❗️Выберите подписку", reply_markup=get_subscribe_menu_view())
    except Exception as e:
        logger.critical(e)
        await call.message.answer("Нет подписок")


async def view_subscription(call: types.CallbackQuery):
    try:
        sub_info = SUBSCRIPTIONS_INFO.get(int(re.findall(r"view_buy_(\d*)", call.data)[0]))
        await call.message.delete()
        await call.message.answer(f"{sub_info}", reply_markup=get_subscribe_menu_pay(sub_info.pk))
    except ValueError as e:
        logger.critical(e)
        await call.message.answer("Нет подписок")


@logger.catch
async def create_subscribe(call: types.CallbackQuery, db_user: DbUser):
    logger.critical(db_user)
    bill_db = await Billing.get_or_none(db_user=db_user).select_related("subscription")
    if bill_db:
        bill = await YooPayment.get(bill_db.bill_id)
        await call.message.delete()
        await call.message.answer(
            f"❗️Ожидание оплаты предыдущей подписки\n" f"{bill_db.subscription.title}",
            reply_markup=get_subscribe_payment(bill.confirmation.confirmation_url),
        )
    else:
        sub_info = SUBSCRIPTIONS_INFO.get(int(re.findall(r"_(\d*)", call.data)[0]))
        payment = await YooPayment.create_payment(sub_info.title, sub_info.price)
        db_bill = await Billing.create_bill(db_user, payment.id, sub_info)  # todo 2/26/2022 7:07 PM taima:

        await call.message.delete()
        await call.message.answer(
            f"✅ Счёт на оплату {sub_info.title} сформирован.\n",
            reply_markup=get_subscribe_payment(payment.confirmation.confirmation_url),
        )
        # await check_payment(bill.bill_id, db_user.user_id)


@logger.catch
async def reject_payment(call: types.CallbackQuery, db_user: DbUser):
    bill_obj = await Billing.get(db_user=db_user).select_related("subscription")

    # bill = await p2p.reject(bill_obj.bill_id)  # todo 3/5/2022 7:37 PM taima:
    bill = await YooPayment.get(bill_obj.bill_id)

    await bill_obj.delete()
    await bill_obj.subscription.delete()
    await call.message.delete()

    logger.info(f"{call.from_user.id}|Оплата {bill_obj.bill_id}|{bill.status} отменена ")
    await call.message.answer(f"Оплата {bill_obj.subscription.title} отменена ")


async def accept_payment(call: types.CallbackQuery, db_user: DbUser):
    db_bill = await Billing.get(db_user=db_user).select_related("subscription")
    is_paid = await check_payment(db_bill.bill_id, db_user)

    if is_paid == "succeeded":
        await call.message.delete()
        await call.message.answer(f"Подписка {db_bill.subscription.title} успешно оплачена!")
    elif is_paid == "canceled":
        await call.message.delete()
        await call.message.answer(
            f"Чек на подписку {db_bill.subscription.title} отменен, пожалуйста сделайте запрос еще раз"
        )
    else:
        await call.answer("❗️ Платеж не найден")


def register_subscriptions_handlers(dp: Dispatcher):
    # dp.register_callback_query_handler(subscribe, text_startswith="subscribe_")
    dp.register_callback_query_handler(buy_sub, text="buy_sub")
    dp.register_callback_query_handler(view_subscription, ViewSubscriptionFilter())
    dp.register_callback_query_handler(create_subscribe, SubscribeFilter())
    dp.register_callback_query_handler(reject_payment, RejectPaymentFilter())
    dp.register_callback_query_handler(accept_payment, AcceptPaymentFilter())

    # dp.register_callback_query_handler(subscribe_month, text="subscribe_month")
