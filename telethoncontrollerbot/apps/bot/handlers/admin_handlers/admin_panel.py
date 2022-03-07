from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from telethoncontrollerbot.apps.bot.markups import admin_menu
from telethoncontrollerbot.config.config import ADMINS
from telethoncontrollerbot.db.models import DbUser


async def admin_start(message: types.Message, db_user: DbUser, state: FSMContext):  # todo 2/27/2022 12:39 PM taima:
    await state.finish()
    await message.answer("Admin menu", reply_markup=admin_menu.admin_start)
    await message.answer("Выберите опцию", reply_markup=admin_menu.menu)
    # сохранить последние изменения


async def no_admin_start(message: types.Message):
    await message.answer("Вы не администратор!")


async def bot_settings(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Admin menu", reply_markup=admin_menu.menu)


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands="admin_start", user_id=ADMINS, state="*")
    dp.register_message_handler(no_admin_start, commands="admin_start")
