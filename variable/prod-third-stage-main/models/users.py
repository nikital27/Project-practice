from __future__ import annotations

import sqlalchemy
import sqlalchemy.orm

import models.core
import models.travels

users_interests_table = sqlalchemy.Table(
    'users_interests',
    models.core.Base.metadata,
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('interest_id', sqlalchemy.ForeignKey('interests.id')),
)


class User(models.core.Base):
    __tablename__ = 'users'

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        primary_key=True,
    )
    login: sqlalchemy.orm.Mapped[str]
    sex: sqlalchemy.orm.Mapped[bool] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    age: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    city: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    country: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    bio: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    interests: sqlalchemy.orm.Mapped[
        list[Interest]
    ] = sqlalchemy.orm.relationship(
        secondary=users_interests_table,
        back_populates='users',
        lazy='subquery',
    )
    travels: sqlalchemy.orm.Mapped[
        list[models.travels.Travel]
    ] = sqlalchemy.orm.relationship(
        secondary=models.travels.users_travels_table,
        back_populates='users',
        lazy='subquery',
    )


class Interest(models.core.Base):
    __tablename__ = 'interests'

    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        primary_key=True,
    )
    name: sqlalchemy.orm.Mapped[str]
    users: sqlalchemy.orm.Mapped[list[User]] = sqlalchemy.orm.relationship(
        secondary=users_interests_table,
        back_populates='interests',
        lazy='subquery',
    )

    def __str__(self) -> str:
        return self.name
