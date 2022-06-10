from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

from telethoncontrollerbot.apps.bot.markups import main_menu
from telethoncontrollerbot.apps.bot.markups.subscribe_menu import renew_subscription
from telethoncontrollerbot.db.models import DbUser


class LangChoice(StatesGroup):
    start = State()


@logger.catch
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("👷 Используйте кнопки меню:", reply_markup=main_menu.main_menu_common)


async def profile(message: types.Message, db_user: DbUser, state: FSMContext):
    # duration: datetime.timedelta = db_user.subscription.duration - datetime.datetime.now(TZ)
    await state.finish()
    await message.answer(
        f"🔑 ID: {db_user.user_id}\n"
        f"👤 Логин: @{db_user.username}\n"
        f"💵 Вид подписки - {db_user.subscription.title}\n"
        f"🕜 Осталось до завершения подписки - {db_user.subscription.duration}.\n",
        reply_markup=renew_subscription(db_user.subscription.title) if db_user.subscription.is_subscribe else None,
    )


def register_common_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
    # dp.register_callback_query_handler(profile, ProfileFilter())
    dp.register_message_handler(profile, text_startswith="👤", state="*")
