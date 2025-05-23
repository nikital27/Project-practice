from __future__ import annotations

import aiogram.filters.callback_data
import aiogram.types
import aiogram.utils.keyboard
import sqlalchemy
import sqlalchemy.engine.base
import sqlalchemy.orm

import callback.enum
import models.travels
import models.users
import strings

MAX_ELEMENTS = 3


class TravelCallback(
    aiogram.filters.callback_data.CallbackData,
    prefix='travel',
):
    action: str
    id: int = 0


class LocationCallback(
    aiogram.filters.callback_data.CallbackData,
    prefix='location',
):
    action: str
    travel_id: int
    id: int = 0


class TravelPagination(
    aiogram.filters.callback_data.CallbackData,
    prefix='travel_pag',
):
    page: int = 0


class LocationPagination(
    aiogram.filters.callback_data.CallbackData,
    prefix='location_pag',
):
    travel_id: int
    page: int = 0


def paginated_locations(
    db_engine: sqlalchemy.engine.base.Engine,
    travel_id: int,
    page: int = 0,
):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    with sqlalchemy.orm.Session(db_engine) as db_session:
        count_locations_all = (
            db_session.query(models.travels.Location)
            .filter(
                models.travels.Location.travels.any(
                    models.travels.Travel.id == travel_id,
                ),
            )
            .count()
        )

        if page == -1:
            page = count_locations_all // MAX_ELEMENTS

        locations = (
            db_session.query(models.travels.Location)
            .filter(
                models.travels.Location.travels.any(
                    models.travels.Travel.id == travel_id,
                ),
            )
            .slice(page * MAX_ELEMENTS, (page + 1) * MAX_ELEMENTS)
            .all()
        )

    for location in locations:
        builder.button(
            text=location.name,
            callback_data=LocationCallback(
                action='view',
                travel_id=travel_id,
                id=location.id,
            ).pack(),
        )

    all_number_pages = count_locations_all // MAX_ELEMENTS
    all_number_pages += 1 if count_locations_all % MAX_ELEMENTS != 0 else 0

    if count_locations_all > MAX_ELEMENTS:
        if page != 0:
            builder.button(
                text='⬅️',
                callback_data=LocationPagination(
                    page=page - 1,
                    travel_id=travel_id,
                ).pack(),
            )
        else:
            builder.button(text=' ', callback_data='-')

        builder.button(
            text=f'{page + 1}/{all_number_pages}',
            callback_data='-',
        )

        if page + 2 <= all_number_pages:
            builder.button(
                text='➡️',
                callback_data=LocationPagination(
                    page=page + 1,
                    travel_id=travel_id,
                ).pack(),
            )
        else:
            builder.button(text=' ', callback_data='-')

    builder.button(
        text=strings.ADD,
        callback_data=LocationCallback(
            action='add',
            travel_id=travel_id,
        ),
    )
    builder.button(
        text=strings.BACK,
        callback_data=TravelCallback(
            action='view',
            id=travel_id,
        ).pack(),
    )

    builder.adjust(*[1] * len(locations) + [3, 2])
    return builder.as_markup(resize_keyboard=True)


def paginated_travels(
    db_engine: sqlalchemy.engine.base.Engine,
    user_id: int,
    page: int = 0,
):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    with sqlalchemy.orm.Session(db_engine) as db_session:
        count_travels_all = (
            db_session.query(models.travels.Travel)
            .filter(
                models.travels.Travel.users.any(
                    models.users.User.id == user_id,
                ),
            )
            .count()
        )

        if page == -1:
            page = count_travels_all // MAX_ELEMENTS

        travels = (
            db_session.query(models.travels.Travel)
            .filter(
                models.travels.Travel.users.any(
                    models.users.User.id == user_id,
                ),
            )
            .slice(page * MAX_ELEMENTS, (page + 1) * MAX_ELEMENTS)
            .all()
        )

    for travel in travels:
        builder.button(
            text=travel.name,
            callback_data=TravelCallback(
                action='view',
                id=travel.id,
                page=page,
            ).pack(),
        )

    all_number_pages = count_travels_all // MAX_ELEMENTS
    all_number_pages += 1 if count_travels_all % MAX_ELEMENTS != 0 else 0

    if count_travels_all > MAX_ELEMENTS:
        if page != 0:
            builder.button(
                text='⬅️',
                callback_data=TravelPagination(page=page - 1).pack(),
            )
        else:
            builder.button(text=' ', callback_data='-')

        builder.button(
            text=f'{page + 1}/{all_number_pages}',
            callback_data='-',
        )

        if page + 2 <= all_number_pages:
            builder.button(
                text='➡️',
                callback_data=TravelPagination(page=page + 1).pack(),
            )
        else:
            builder.button(text=' ', callback_data='-')

    builder.button(
        text=strings.ADD,
        callback_data=TravelCallback(action='add'),
    )
    builder.button(
        text=strings.BACK,
        callback_data=callback.enum.CallbackStatus.BACK_MENU,
    )

    builder.adjust(*[1] * len(travels) + [3, 2])
    return builder.as_markup(resize_keyboard=True)


def travel(travel_id: int, db_engine: sqlalchemy.engine.base.Engine):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel: models.travels.Travel = db_session.query(
            models.travels.Travel,
        ).get(travel_id)

    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text=strings.LOCATIONS,
        callback_data=LocationPagination(page=0, travel_id=travel_id).pack(),
    )

    if len(travel.locations) >= 2:
        builder.button(
            text=strings.MAP,
            callback_data=TravelCallback(
                action='map',
                id=travel.id,
            ).pack(),
        )
    builder.button(
        text=strings.EDIT,
        callback_data=TravelCallback(
            action='edit',
            id=travel.id,
        ).pack(),
    )
    builder.button(
        text=strings.DELETE,
        callback_data=TravelCallback(
            action='delete',
            id=travel.id,
        ).pack(),
    )
    builder.button(
        text=strings.BACK,
        callback_data=TravelPagination().pack(),
    )

    builder.adjust(2 if len(travel.locations) > 2 else 1, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def travel_edit(travel_id: int):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text=strings.EDIT_TRAVEL_NAME,
        callback_data=TravelCallback(
            action='edit_name',
            id=travel_id,
        ).pack(),
    )
    builder.button(
        text=strings.EDIT_TRAVEL_DESCRIPTION,
        callback_data=TravelCallback(
            action='edit_description',
            id=travel_id,
        ).pack(),
    )
    builder.button(
        text=strings.BACK,
        callback_data=TravelCallback(
            action='view',
            id=travel_id,
        ).pack(),
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


def location(
    location_id: int,
    travel_id: int,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        location: models.travels.Location = db_session.query(
            models.travels.Location,
        ).get(location_id)

    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text=strings.DELETE,
        callback_data=LocationCallback(
            action='delete',
            travel_id=travel_id,
            id=location.id,
        ).pack(),
    )
    builder.button(
        text=strings.BACK,
        callback_data=LocationPagination(travel_id=travel_id).pack(),
    )

    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


def location_back(travel_id: int):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text=strings.BACK,
        callback_data=LocationPagination(travel_id=travel_id),
    )
    return builder.as_markup(resize_keyboard=True)


def travel_back(travel_id: int):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text=strings.CANCEL,
        callback_data=TravelCallback(
            action='view',
            id=travel_id,
        ).pack(),
    )
    return builder.as_markup(resize_keyboard=True)


def url_for_map(
    travel_id: int,
    profile: str,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        locations: list[models.travels.Location] = (
            db_session.query(
                models.travels.Location,
            )
            .filter(
                models.travels.Location.travels.any(
                    models.travels.Travel.id == travel_id,
                ),
            )
            .order_by(
                models.travels.Location.end,
            )
            .all()
        )

    url = 'https://graphhopper.com/maps/?'

    for location in locations:
        url += f'point={location.lat},{location.lon}&'

    return f'{url}profile={profile}&layer=OpenStreetMap'


def maps(
    travel_id: int,
    db_engine: sqlalchemy.engine.base.Engine,
):
    builder = aiogram.utils.keyboard.InlineKeyboardBuilder()
    builder.button(
        text='Пешком',
        web_app=aiogram.types.WebAppInfo(
            url=url_for_map(travel_id, 'hike', db_engine),
        ),
    )
    builder.button(
        text='На велосипеде',
        web_app=aiogram.types.WebAppInfo(
            url=url_for_map(travel_id, 'bike', db_engine),
        ),
    )
    builder.button(
        text='На машине',
        web_app=aiogram.types.WebAppInfo(
            url=url_for_map(travel_id, 'car', db_engine),
        ),
    )
    builder.button(
        text=strings.BACK,
        callback_data=TravelCallback(
            action='view',
            id=travel_id,
        ).pack(),
    )
    builder.adjust(*[1] * 4)
    return builder.as_markup(resize_keyboard=True)
