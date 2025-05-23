import aiogram.filters
import aiogram.types
import sqlalchemy.engine.base

import utils.db


class Unregistered(aiogram.filters.Filter):
    async def __call__(
        self,
        message: aiogram.types.Message,
        db_engine: sqlalchemy.engine.base.Engine,
    ) -> bool:
        return not utils.db.check_user_exist(db_engine, message.from_user.id)


class Registered(aiogram.filters.Filter):
    async def __call__(
        self,
        message: aiogram.types.Message,
        db_engine: sqlalchemy.engine.base.Engine,
    ) -> bool:
        return utils.db.check_user_exist(db_engine, message.from_user.id)
