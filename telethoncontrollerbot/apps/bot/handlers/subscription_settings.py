import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from telethoncontrollerbot.apps.bot.markups import admin_menu
from telethoncontrollerbot.apps.bot.markups.admin_menu import KBRSubscriptionField
from telethoncontrollerbot.apps.bot.utils.subscription_info import SUBSCRIPTIONS_INFO
from telethoncontrollerbot.db.models import SubscriptionInfo


class CreateSubscriptionState(StatesGroup):
    title = State()
    duration = State()
    price = State()


class ChangeSubscriptionState(StatesGroup):
    choice_field = State()
    edit_field = State()


async def view_all_subscriptions(call: types.CallbackQuery):
    subscription_info = ""
    for pk, sub_info in SUBSCRIPTIONS_INFO.items():
        subscription_info += f"{sub_info}\n"
    await call.message.delete()
    await call.message.answer(
        f"Текущие подписки {len(SUBSCRIPTIONS_INFO)}.\n"
        f" Для изменения нажмите на соответствующую подписку\n",
        reply_markup=admin_menu.get_current_sub_info(),
    )
    # await call.message.edit_text(f"Текущие подписки {len(SUBSCRIPTIONS_INFO)}:\n")
    # await call.message.edit_reply_markup(admin_menu.get_current_sub_info())


async def view_subscription_info(call: types.CallbackQuery, state: FSMContext):
    pk = int(re.findall(r"view_subscription_(.*)", call.data)[0])
    sub_info = SUBSCRIPTIONS_INFO[pk]
    await state.update_data(sub_info=sub_info)

    await call.message.delete()
    await call.message.answer(f"{sub_info}", reply_markup=admin_menu.change_field)
    await ChangeSubscriptionState.first()


async def change_subscription_info_start(call: types.CallbackQuery, state: FSMContext):
    if call.data == "delete":
        data = await state.get_data()
        sub_info: SubscriptionInfo = data["sub_info"]
        await sub_info.delete()
        del SUBSCRIPTIONS_INFO[sub_info.pk]
        await call.message.delete()
        await call.message.answer("Подписка успешно удалена")
        return
    field = call.data
    await state.update_data(field=field)
    await call.message.answer(
        f"Введите новое значение для поля {field}",
        reply_markup=getattr(KBRSubscriptionField, field, None),
    )
    await ChangeSubscriptionState.next()


async def change_subscription_info_end(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sub_info: SubscriptionInfo = data["sub_info"]
    # await sub_info.refresh_from_db()
    field = data["field"]
    new_value = message.text
    setattr(sub_info, field, new_value)
    await sub_info.save()
    await SUBSCRIPTIONS_INFO[sub_info.pk].refresh_from_db()

    await message.answer(
        f"Данные подписки успешно изменены\n{sub_info}",
        # reply_markup=admin_menu.admin_start
        reply_markup=admin_menu.change_field
    )
    await ChangeSubscriptionState.choice_field.set()


async def create_subscription_start(call: types.CallbackQuery, state: FSMContext):
    # await state.finish()
    await CreateSubscriptionState.first()
    await call.message.delete()
    await call.message.answer(
        f"1. Введите описание подписки которое будет отображаться на кнопке (не более 255 символов).\n"
    )


@logger.catch
async def create_subscription_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        "Укажите длительность подписки в днях", reply_markup=KBRSubscriptionField.days
    )
    await CreateSubscriptionState.next()


@logger.catch
async def create_subscription_duration(message: types.Message, state: FSMContext):
    await state.update_data(days=int(message.text))
    await message.answer(
        "Укажите цену за подписку", reply_markup=KBRSubscriptionField.price
    )
    await CreateSubscriptionState.next()


@logger.catch
async def create_subscription_price(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        new_sub_info = await SubscriptionInfo.create(**data, price=message.text)
        SUBSCRIPTIONS_INFO[new_sub_info.pk] = new_sub_info
        await message.answer(
            "Подписка успешно создана", reply_markup=admin_menu.admin_start
        )
        await state.finish()
    except Exception as e:
        logger.critical(e)
        await message.answer("Ошибка при создании")


def register_admin_subscription_settings_handlers(dp: Dispatcher):
    # user_id = [1985947355, 2014301618]
    dp.register_callback_query_handler(
        view_all_subscriptions, text="view_all_subscriptions"
    )
    dp.register_callback_query_handler(
        view_subscription_info, text_startswith="view_subscription_"
    )

    dp.register_callback_query_handler(
        change_subscription_info_start, state=ChangeSubscriptionState.choice_field
    )
    dp.register_message_handler(
        change_subscription_info_end, state=ChangeSubscriptionState.edit_field
    )

    dp.register_callback_query_handler(
        create_subscription_start, text="create_subscription"
    )
    dp.register_message_handler(
        create_subscription_title, state=CreateSubscriptionState.title
    )
    dp.register_message_handler(
        create_subscription_duration, state=CreateSubscriptionState.duration
    )
    dp.register_message_handler(
        create_subscription_price, state=CreateSubscriptionState.price
    )
