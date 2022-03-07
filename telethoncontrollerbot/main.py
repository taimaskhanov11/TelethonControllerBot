
import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand
from loguru import logger

from telethoncontrollerbot.apps.bot.handlers.admin_handlers.admin_panel import register_admin_menu_handlers
from telethoncontrollerbot.apps.bot.handlers.admin_handlers.subscription_settings import (
    register_admin_subscription_settings_handlers,
)
from telethoncontrollerbot.apps.bot.handlers.configure_triggers import register_configure_triggers_handlers
from telethoncontrollerbot.apps.bot.handlers.connect_account import register_connect_account_handlers
from telethoncontrollerbot.apps.bot.handlers.main_menu import register_common_handlers
from telethoncontrollerbot.apps.bot.handlers.make_subscription import register_subscriptions_handlers
from telethoncontrollerbot.apps.bot.middleware.father_middleware import FatherMiddleware
from telethoncontrollerbot.apps.bot.utils.daily_processes import everyday_processes
from telethoncontrollerbot.apps.bot.utils.subscription_info import init_subscriptions_info
from telethoncontrollerbot.apps.controller.session_data import init_sessions
from telethoncontrollerbot.apps.controller.settings import init_logging
from telethoncontrollerbot.apps.controller.triggers_data import init_triggers
from telethoncontrollerbot.db.db_main import init_tortoise
from telethoncontrollerbot.loader import dp, bot

# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Главное меню"),
        BotCommand(command="/admin_start", description="Главное меню для админов"),
        # BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():
    init_logging(old_logger=True, level=logging.DEBUG)
    # Настройка логирования в stdout
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    # )
    logger.info("Starting bot")
    # Парсинг файла конфигурации
    # config = load_config("config/bot.ini")

    # Объявление и инициализация объектов бота и диспетчера
    # bot = Bot(token=TG_TOKEN)
    # dp = Dispatcher(bot, storage=MemoryStorage())
    print((await bot.get_me()).username)

    # Меню админа
    # register_admin_handlers(dp)

    # Регистрация хэндлеров
    register_common_handlers(dp)
    register_admin_menu_handlers(dp)

    register_configure_triggers_handlers(dp)
    register_connect_account_handlers(dp)
    register_subscriptions_handlers(dp)
    register_admin_subscription_settings_handlers(dp)

    # Регистрация middleware

    dp.middleware.setup(FatherMiddleware())

    # Регистрация фильтров
    # dp.filters_factory.bind(EmailFilter)

    # Установка команд бота
    await set_commands(bot)

    # Инициализация базы данных
    await init_tortoise()

    # Инициализация переводов
    # await init_translations()

    # Инициализация информации подписок
    await init_subscriptions_info()
    #
    # await init_sub_channel()
    await init_triggers()

    # Запуск задачи ежедневного обновления запросов и проверки подписки
    asyncio.create_task(everyday_processes())

    # Запуск контроллера триггеров
    asyncio.create_task(init_sessions())

    # Создание ежедневного резервного копирования
    # asyncio.create_task(making_backup(3600))

    # Запуск поллинга
    # await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
