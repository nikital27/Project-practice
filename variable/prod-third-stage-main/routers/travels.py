import aiogram
import aiogram.exceptions
import aiogram.filters
import aiogram.fsm.context
import sqlalchemy.engine.base
import sqlalchemy.orm

import callback.enum
import keyboards.fabrics
import keyboards.inline
import keyboards.reply
import models.travels
import models.users
import states.form
import strings
import validators.core
import validators.travels

router = aiogram.Router()


@router.callback_query(keyboards.fabrics.TravelPagination.filter())
async def travels(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.TravelPagination,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await call.message.edit_text(
        strings.TRAVELS,
        reply_markup=keyboards.fabrics.paginated_travels(
            db_engine,
            call.from_user.id,
            callback_data.page,
        ),
    )


@router.callback_query(keyboards.fabrics.LocationPagination.filter())
async def locations(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.TravelPagination,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await call.message.edit_text(
        strings.LOCATIONS_LIST,
        reply_markup=keyboards.fabrics.paginated_locations(
            db_engine,
            callback_data.travel_id,
            callback_data.page,
        ),
    )


@router.callback_query(
    keyboards.fabrics.LocationCallback.filter(aiogram.F.action == 'delete'),
)
async def callback_delete_location(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.LocationCallback,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        location: models.travels.Location = db_session.query(
            models.travels.Location,
        ).get(callback_data.id)

        db_session.delete(location)
        db_session.commit()

    await call.message.edit_text(
        strings.LOCATIONS_LIST,
        reply_markup=keyboards.fabrics.paginated_locations(
            db_engine,
            callback_data.travel_id,
        ),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'delete'),
)
async def callback_delete(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.TravelCallback,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel: models.travels.Travel = db_session.query(
            models.travels.Travel,
        ).get(callback_data.id)

        db_session.delete(travel)
        db_session.commit()

    await call.message.edit_text(
        strings.TRAVELS,
        reply_markup=keyboards.fabrics.paginated_travels(
            db_engine,
            call.from_user.id,
        ),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'edit'),
)
async def callback_edit(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.TravelCallback,
):
    await call.message.edit_text(
        strings.EDIT_TRAVEL,
        reply_markup=keyboards.fabrics.travel_edit(callback_data.id),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'map'),
)
async def callback_map(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.TravelCallback,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await call.message.edit_text(
        strings.MAPS,
        reply_markup=keyboards.fabrics.maps(callback_data.id, db_engine),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'edit_name'),
)
async def callback_edit_name(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    callback_data: keyboards.fabrics.TravelCallback,
):
    await state.update_data(travel_id=callback_data.id)
    await state.set_state(states.form.EditTravel.edit_travel_name)
    await call.message.edit_text(
        strings.ENTER_TRAVEL_NAME,
        reply_markup=keyboards.fabrics.travel_back(callback_data.id),
    )


@router.message(
    states.form.EditTravel.edit_travel_name,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_edit_travel_name(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        name = validators.travels.validate_name(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    data = await state.get_data()

    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel = db_session.query(models.travels.Travel).get(data['travel_id'])
        travel.name = name
        db_session.commit()
        db_session.refresh(travel)

    await state.clear()
    await message.answer(
        get_travel_str(travel),
        reply_markup=keyboards.fabrics.travel(
            data['travel_id'],
            db_engine,
        ),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(
        aiogram.F.action == 'edit_description',
    ),
)
async def callback_edit_description(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    callback_data: keyboards.fabrics.TravelCallback,
):
    await state.update_data(travel_id=callback_data.id)
    await state.set_state(states.form.EditTravel.edit_travel_description)
    await call.message.edit_text(
        strings.ENTER_TRAVEL_DESCRIPTION,
        reply_markup=keyboards.fabrics.travel_back(callback_data.id),
    )


@router.message(
    states.form.EditTravel.edit_travel_description,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_edit_travel_description(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        description = validators.travels.validate_description(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    data = await state.get_data()

    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel = db_session.query(models.travels.Travel).get(data['travel_id'])
        travel.description = description
        db_session.commit()
        db_session.refresh(travel)

    await state.clear()
    await message.answer(
        get_travel_str(travel),
        reply_markup=keyboards.fabrics.travel(
            data['travel_id'],
            db_engine,
        ),
    )


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'add'),
)
async def callback_add(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
):
    await state.set_state(states.form.AddTravel.name)
    await call.message.edit_text(
        strings.ENTER_NEW_TRAVEL,
        reply_markup=keyboards.inline.BACK_TO_TRAVEL,
    )


@router.message(
    states.form.AddTravel.name,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def add_travel(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    try:
        name = validators.travels.validate_name(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    await state.update_data(travel=name)
    await state.set_state(states.form.AddTravel.description)
    await message.answer(
        strings.TRAVEL_NAME_IS_SET_TO.format(name),
        reply_markup=keyboards.inline.BACK_TO_TRAVEL,
    )


@router.message(
    states.form.AddTravel.description,
    aiogram.filters.Command('skip'),
)
async def form_description_skip(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await create_travel(message, state, db_engine)


@router.message(
    states.form.AddTravel.description,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_description(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        description = validators.travels.validate_description(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return
    await state.update_data(description=description)
    await create_travel(message, state, db_engine)


async def create_travel(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    data = await state.get_data()

    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel = models.travels.Travel(
            name=data.get('travel'),
            description=data.get('description'),
        )
        travel.users.append(
            db_session.query(models.users.User).get(message.from_user.id),
        )
        db_session.add(travel)
        db_session.commit()
        db_session.refresh(travel)

    await message.answer(
        get_travel_str(travel),
        reply_markup=keyboards.fabrics.travel(travel.id, db_engine),
    )
    await state.clear()


@router.callback_query(
    keyboards.fabrics.TravelCallback.filter(aiogram.F.action == 'view'),
)
async def callback_back(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    callback_data: keyboards.fabrics.TravelCallback,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel: models.travels.Travel = db_session.query(
            models.travels.Travel,
        ).get(callback_data.id)

    await call.message.edit_text(
        get_travel_str(travel),
        reply_markup=keyboards.fabrics.travel(
            callback_data.id,
            db_engine,
        ),
    )
    await state.clear()


def get_travel_str(travel: models.travels.Travel) -> str:
    return strings.SHOW_TRAVEL.format(
        travel.name,
        travel.description if travel.description else '-',
        ', '.join([u.login for u in travel.users]),
    )


def get_location_str(location: models.travels.Location) -> str:
    return strings.SHOW_LOCATION.format(
        name=location.name,
        start=location.start.strftime('%H:%M %d.%m.%Y'),
        end=location.end.strftime('%H:%M %d.%m.%Y'),
    )


@router.callback_query(
    keyboards.fabrics.LocationCallback.filter(aiogram.F.action == 'add'),
)
async def callback_add_location(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.LocationCallback,
    state: aiogram.fsm.context.FSMContext,
):
    await state.update_data(travel_id=callback_data.travel_id)
    await state.set_state(states.form.AddLocation.name)
    await call.message.edit_text(
        strings.ENTER_LOCATION_NAME,
        reply_markup=keyboards.fabrics.location_back(callback_data.travel_id),
    )


@router.message(
    states.form.AddLocation.name,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def add_location(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    query_message = await message.answer(strings.LOADING)

    try:
        name, display_name, lat, lon = validators.travels.validate_location(
            message.text,
        )
    except validators.core.ValidationError as e:
        await query_message.edit_text(str(e))
        return

    await state.update_data(name=name, lat=lat, lon=lon)
    await query_message.edit_text(
        f'`{display_name}` - правильно?',
        reply_markup=keyboards.inline.YES_NO,
    )


@router.callback_query(
    states.form.AddLocation.name,
    aiogram.F.data == callback.enum.CallbackStatus.NO,
)
async def callback_location_no(call: aiogram.types.CallbackQuery):
    await call.message.edit_text(text=strings.LOCATION_CANCELED)


@router.callback_query(
    states.form.AddLocation.name,
    aiogram.F.data == callback.enum.CallbackStatus.YES,
)
async def callback_location_yes(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
):
    data = await state.get_data()

    await call.message.edit_text(
        strings.LOCATION_NAME_IS_SET_TO.format(name=data['name']),
        reply_markup=None,
    )
    await state.set_state(states.form.AddLocation.start)


@router.message(
    states.form.AddLocation.start,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def add_location_start(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    try:
        start = validators.travels.validate_start(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return
    await state.update_data(start=start)
    await state.set_state(states.form.AddLocation.end)
    await message.answer(
        strings.LOCATION_START_IS_SET_TO.format(start=start),
    )


@router.message(
    states.form.AddLocation.end,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def add_location_end(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    data = await state.get_data()

    try:
        end = validators.travels.validate_end(data['start'], message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    with sqlalchemy.orm.Session(db_engine) as db_session:
        travel: models.travels.Travel = db_session.query(
            models.travels.Travel,
        ).get(data['travel_id'])
        location = models.travels.Location(
            name=data.get('name'),
            lat=data.get('lat'),
            lon=data.get('lon'),
            start=data.get('start'),
            end=end,
        )
        travel.locations.append(location)
        db_session.commit()
        db_session.refresh(travel)

    await message.answer(
        get_location_str(location),
        reply_markup=keyboards.fabrics.location(
            location.id,
            data['travel_id'],
            db_engine,
        ),
    )
    await state.clear()


@router.callback_query(
    keyboards.fabrics.LocationCallback.filter(aiogram.F.action == 'view'),
)
async def callback_view_location(
    call: aiogram.types.CallbackQuery,
    callback_data: keyboards.fabrics.LocationCallback,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        location: models.travels.Location = db_session.query(
            models.travels.Location,
        ).get(callback_data.id)

    await call.message.edit_text(
        get_location_str(location),
        reply_markup=keyboards.fabrics.location(
            callback_data.id,
            callback_data.travel_id,
            db_engine,
        ),
    )
    await state.clear()
