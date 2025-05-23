import aiogram
import aiogram.exceptions
import aiogram.fsm.context
import sqlalchemy.engine.base
import sqlalchemy.orm

import callback.enum
import keyboards.inline
import keyboards.reply
import models.users
import states.form
import strings
import validators.core
import validators.user

router = aiogram.Router()


def get_profile_text(user: models.users.User) -> str:
    return strings.SHOW_PROFILE.format(
        login=user.login,
        age=user.age,
        sex=strings.MAN if user.sex else strings.WOMAN,
        country=user.country,
        city=user.city,
        bio=user.bio if user.bio else '-',
        interests=(
            ', '.join(map(str, user.interests)) if user.interests else '-'
        ),
    )


def get_user(
    db_engine: sqlalchemy.engine.base.Engine,
    user_id: int,
) -> models.users.User:
    with sqlalchemy.orm.Session(db_engine) as db_session:
        return db_session.query(models.users.User).get(user_id)


@router.callback_query(
    aiogram.F.data.in_(
        (
            callback.enum.CallbackStatus.PROFILE,
            callback.enum.CallbackStatus.BACK_PROFILE,
        ),
    ),
)
async def callback_profile(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await state.clear()

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            call.from_user.id,
        )

    await call.message.edit_text(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.LOGIN_EDIT,
)
async def callback_edit_login(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)
    await state.set_state(states.form.Profile.login_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_LOGIN.format(login=user.login),
        reply_markup=keyboards.inline.CANCEL_PROFILE,
    )


@router.message(
    states.form.Profile.login_edit,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_login(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        login = validators.user.validate_login(message.text, db_engine)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            message.from_user.id,
        )
        user.login = login
        db_session.commit()
        db_session.refresh(user)

    await message.answer(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.AGE_EDIT,
)
async def callback_edit_age(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)

    await state.set_state(states.form.Profile.age_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_AGE.format(age=user.age),
        reply_markup=keyboards.inline.CANCEL_PROFILE,
    )


@router.message(
    states.form.Profile.age_edit,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_age(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        age = validators.user.validate_age(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            message.from_user.id,
        )
        user.age = age
        db_session.commit()
        db_session.refresh(user)

    await message.answer(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.SEX_EDIT,
)
async def callback_edit_sex(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)
    await state.set_state(states.form.Profile.sex_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_SEX.format(
            sex=strings.MAN if user.sex else strings.WOMAN,
        ),
        reply_markup=keyboards.inline.SELECT_SEX,
    )


@router.callback_query(
    states.form.Profile.sex_edit,
    aiogram.F.data.in_(
        (
            callback.enum.CallbackStatus.MALE,
            callback.enum.CallbackStatus.FEMALE,
        ),
    ),
)
async def callback_edit_sex_set(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            call.from_user.id,
        )
        user.sex = call.data == callback.enum.CallbackStatus.MALE
        db_session.commit()
        db_session.refresh(user)

    await call.message.edit_text(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.INTERESTS_EDIT,
)
async def callback_edit_interests(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)
    await state.set_state(states.form.Profile.interests_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_INTERESTS.format(
            interests=', '.join(map(str, user.interests))
            if user.interests
            else '-',
        ),
        reply_markup=keyboards.inline.CANCEL_PROFILE,
    )


@router.message(
    states.form.Profile.interests_edit,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_interests(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        interests = validators.user.validate_interests(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            message.from_user.id,
        )
        user.interests.clear()
        for item in interests:
            interest = (
                db_session.query(models.users.Interest)
                .filter_by(name=item)
                .first()
            )

            if not interest:
                interest = models.users.Interest(name=item)

            user.interests.append(interest)

        db_session.commit()
        db_session.refresh(user)

    await message.answer(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.BIO_EDIT,
)
async def callback_edit_bio(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)
    await state.set_state(states.form.Profile.bio_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_BIO.format(bio=user.bio if user.bio else '-'),
        reply_markup=keyboards.inline.CANCEL_PROFILE,
    )


@router.message(
    states.form.Profile.bio_edit,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_bio(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    try:
        bio = validators.user.validate_bio(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            message.from_user.id,
        )
        user.bio = bio

        db_session.commit()
        db_session.refresh(user)

    await message.answer(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.LOCATION_EDIT,
)
async def callback_edit_location(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    user = get_user(db_engine, call.from_user.id)
    await state.set_state(states.form.Profile.location_edit)
    await call.message.edit_text(
        strings.ENTER_NEW_LOCATION.format(
            city=user.city,
            country=user.country,
        ),
        reply_markup=keyboards.inline.CANCEL_PROFILE,
    )


@router.message(
    states.form.Profile.location_edit,
    aiogram.F.content_type.in_(
        (
            aiogram.types.ContentType.LOCATION,
            aiogram.types.ContentType.TEXT,
        ),
    ),
)
async def form_location(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    query_message = await message.answer(strings.LOADING)
    try:
        if message.location:
            (
                city,
                country,
            ) = validators.user.validate_location_by_coords(
                message.location.latitude,
                message.location.longitude,
            )
        else:
            (
                city,
                country,
            ) = validators.user.validate_location_by_name(message.text)
    except validators.core.ValidationError as e:
        await query_message.edit_text(str(e))
        return

    await state.update_data(city=city, country=country)
    await query_message.edit_text(
        f'{city}, {country} - правильно?',
        reply_markup=keyboards.inline.YES_NO,
    )


@router.callback_query(
    states.form.Profile.location_edit,
    aiogram.F.data == callback.enum.CallbackStatus.NO,
)
async def callback_location_no(call: aiogram.types.CallbackQuery):
    await call.message.edit_text(text=strings.LOCATION_CANCELED)


@router.callback_query(
    states.form.Profile.location_edit,
    aiogram.F.data == callback.enum.CallbackStatus.YES,
)
async def callback_location_yes(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    data = await state.get_data()
    with sqlalchemy.orm.Session(db_engine) as db_session:
        user: models.users.User = db_session.query(models.users.User).get(
            call.from_user.id,
        )
        user.city = data['city']
        user.country = data['country']
        db_session.commit()
        db_session.refresh(user)

    await call.message.edit_text(
        get_profile_text(user),
        reply_markup=keyboards.inline.PROFILE,
    )
    await state.clear()
