from aiogram import types

from telethoncontrollerbot.apps.bot.filters.main_menu_filters import MainPaymentFilter
from telethoncontrollerbot.loader import bot


class SubscribeCheckFilter(MainPaymentFilter):  # todo 3/5/2022 10:56 PM taima:
    async def check(self, call: types.CallbackQuery):
        data = await super().check(call)
        if data["db_user"].subscription.is_subscribe:
            return data
        else:
            bot.send_message(data["db_user"].user_id, "Купите подписку")


class ConfigureTriggersFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "configure_triggers":
            return await super().check(call)


class CurrentTriggersFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "current_triggers":
            return await super().check(call)


class RestartControllerBotFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "restart_controller_bot":
            return await super().check(call)
