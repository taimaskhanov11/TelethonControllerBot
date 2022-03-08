from aiogram import types

from telethoncontrollerbot.apps.bot.filters.main_menu_filters import MainPaymentFilter


class SubscribeCheckFilter(MainPaymentFilter):  # todo 3/5/2022 10:56 PM taima:
    async def check(self, call: types.CallbackQuery):
        data = await super().check(call)
        if data["db_user"].subscription.duration:
            return data
        await call.answer("Подписка закончилась. Для настройки триггеров купите подписку.")


class ConnectAccountFilterBase(SubscribeCheckFilter):
    async def check(self, call: types.CallbackQuery):
        data = await super().check(call)
        if data:
            if data["db_user"].account:
                return data
            await call.answer("Для настройки триггеров подключите аккаунт")


class ConfigureTriggersFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "configure_triggers":
            return await super().check(call)


class ConnectAccountFilter(SubscribeCheckFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "connect_account":
            return await super().check(call)


class UnlinkAccountFilter(MainPaymentFilter):
    async def check(self, call: types.CallbackQuery):
        if call.data == "unlink_account":
            return await super().check(call)


class CurrentTriggersFilter(ConnectAccountFilterBase):
    async def check(self, call: types.CallbackQuery):
        if call.data == "current_triggers":
            return await super().check(call)


class RestartControllerBotFilter(ConnectAccountFilterBase):
    async def check(self, call: types.CallbackQuery):
        if call.data == "restart_controller_bot":
            return await super().check(call)


class CreateTriggerFilter(ConnectAccountFilterBase):
    async def check(self, call: types.CallbackQuery):
        if call.data == "new_trigger":
            return await super().check(call)
