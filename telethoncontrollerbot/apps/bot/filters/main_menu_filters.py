from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from telethoncontrollerbot.db.models import DbUser


class MainPaymentFilter(BoundFilter):
    async def check(self, call: types.CallbackQuery):
        db_user = await DbUser.get_or_new(call.from_user.id, call.from_user.username)
        # translation = TRANSLATIONS[db_user.language]
        return {
            "db_user": db_user,
            # "translation": translation
        }


class ProfileFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "profile":
            return await super().check(call)

