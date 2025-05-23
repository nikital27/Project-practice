import asyncio
import logging

import aiogram
import aiogram.client.bot
import aiogram.exceptions
import aiogram.fsm.storage.redis
import sqlalchemy

import config
import models.core
import routers.menu
import routers.other
import routers.profile
import routers.registration
import routers.travels


async def main():
    logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.ERROR)

    engine = sqlalchemy.create_engine(config.DB_URL, echo=False)
    models.core.Base.metadata.create_all(engine)

    bot = aiogram.Bot(
        config.TOKEN,
        default=aiogram.client.bot.DefaultBotProperties(parse_mode='Markdown'),
    )

    storage = (
        None
        if config.DEBUG
        else aiogram.fsm.storage.redis.RedisStorage.from_url(
            config.REDIS_URL,
        )
    )

    dp = aiogram.Dispatcher(storage=storage)

    dp.include_routers(
        routers.travels.router,
        routers.profile.router,
        routers.registration.router,
        routers.menu.router,
        routers.other.router,
    )

    if config.DROP_PENDING_UPDATES:
        await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, db_engine=engine)


if __name__ == '__main__':
    asyncio.run(main())
