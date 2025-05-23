import sqlalchemy.engine.base
import sqlalchemy.orm

import models.users


def check_user_exist(
    db_engine: sqlalchemy.engine.base.Engine,
    user: int | str,
) -> bool:
    with sqlalchemy.orm.Session(db_engine) as session:
        if isinstance(user, int):
            return (
                session.query(models.users.User).filter_by(id=user).first()
                is not None
            )

        return (
            session.query(models.users.User).filter_by(login=user).first()
            is not None
        )
