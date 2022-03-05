from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from telethoncontrollerbot.apps.bot.filters.main_menu_filters import MainPaymentFilter
from telethoncontrollerbot.db.models import DbUser



class ViewSubscriptionFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("view_buy_"):
            return await super().check(call)


class SubscribeFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data.startswith("subscribe_"):
            return await super().check(call)


class RejectPaymentFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "reject_payment":
            return await super().check(call)


class AcceptPaymentFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "accept_payment":
            return await super().check(call)
