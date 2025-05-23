from __future__ import annotations

import datetime

import sqlalchemy
import sqlalchemy.orm

import models.core
import models.users

users_travels_table = sqlalchemy.Table(
    'users_travels',
    models.core.Base.metadata,
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('travel_id', sqlalchemy.ForeignKey('travels.id')),
)

locations_travels_table = sqlalchemy.Table(
    'locations_travels',
    models.core.Base.metadata,
    sqlalchemy.Column('location_id', sqlalchemy.ForeignKey('locations.id')),
    sqlalchemy.Column('travel_id', sqlalchemy.ForeignKey('travels.id')),
)


class Travel(models.core.Base):
    __tablename__ = 'travels'
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        primary_key=True,
    )
    name: sqlalchemy.orm.Mapped[str]
    description: sqlalchemy.orm.Mapped[str] = sqlalchemy.orm.mapped_column(
        nullable=True,
    )
    users: sqlalchemy.orm.Mapped[
        list[models.users.User]
    ] = sqlalchemy.orm.relationship(
        secondary=users_travels_table,
        back_populates='travels',
        lazy='subquery',
    )
    locations: sqlalchemy.orm.Mapped[
        list[Location]
    ] = sqlalchemy.orm.relationship(
        secondary=locations_travels_table,
        back_populates='travels',
        lazy='subquery',
    )

    def __str__(self) -> str:
        return self.name


class Location(models.core.Base):
    __tablename__ = 'locations'
    id: sqlalchemy.orm.Mapped[int] = sqlalchemy.orm.mapped_column(
        primary_key=True,
    )
    name: sqlalchemy.orm.Mapped[str]
    travels: sqlalchemy.orm.Mapped[list[Travel]] = sqlalchemy.orm.relationship(
        secondary=locations_travels_table,
        back_populates='locations',
        lazy='subquery',
    )
    start: sqlalchemy.orm.Mapped[datetime.datetime]
    end: sqlalchemy.orm.Mapped[datetime.datetime]
    lat: sqlalchemy.orm.Mapped[float]
    lon: sqlalchemy.orm.Mapped[float]

    def __str__(self) -> str:
        return self.name
