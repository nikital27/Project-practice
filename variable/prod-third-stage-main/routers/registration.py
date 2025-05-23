import aiogram
import aiogram.filters
import aiogram.filters.callback_data
import aiogram.fsm.context
import aiogram.types
import sqlalchemy.engine.base
import sqlalchemy.orm

import callback.enum
import filters.user
import keyboards.builders
import keyboards.inline
import keyboards.reply
import models.users
import states.form
import strings
import validators.core
import validators.user

MAX_NAME_LENGTH = 64

router = aiogram.Router()


@router.message(aiogram.filters.CommandStart(), filters.user.Unregistered())
async def start_registration(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    await message.answer(
        strings.WELCOME.format(message.from_user.full_name),
        reply_markup=keyboards.builders.get_username_keyboard(message),
    )
    await state.set_state(states.form.Register.login)


@router.message(
    states.form.Register.login,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_name(
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
        user = models.users.User(
            id=message.from_user.id,
            login=login,
        )
        db_session.add(user)
        db_session.commit()

    await state.update_data(login=login)
    await state.set_state(states.form.Register.age)
    await message.answer(
        strings.LOGIN_IS_SET_TO.format(login),
        reply_markup=keyboards.reply.REMOVE,
    )


@router.message(
    states.form.Register.age,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_age(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    try:
        age = validators.user.validate_age(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    await state.update_data(age=age)
    await state.set_state(states.form.Register.sex)
    await message.answer(
        strings.AGE_IS_SET_TO.format(age),
        reply_markup=keyboards.builders.reply([strings.MAN, strings.WOMAN]),
    )


@router.message(
    states.form.Register.sex,
    aiogram.F.text.lower().in_([strings.MAN.lower(), strings.WOMAN.lower()]),
)
async def form_sex(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    sex = message.text.lower() == strings.MAN.lower()

    await state.update_data(sex=sex)
    await state.set_state(states.form.Register.location)
    await message.answer(
        strings.SEX_IS_SET_TO.format(message.text),
        reply_markup=keyboards.reply.LOCATION,
    )


@router.message(states.form.Register.sex)
async def incorrect_form_sex(
    message: aiogram.types.Message,
):
    await message.answer(strings.SEX_INCORRECT_INPUT)


@router.message(
    states.form.Register.location,
    aiogram.F.content_type.in_(
        (aiogram.types.ContentType.TEXT, aiogram.types.ContentType.LOCATION),
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
    states.form.Register.location,
    aiogram.F.data == callback.enum.CallbackStatus.NO,
)
async def callback_location_no(call: aiogram.types.CallbackQuery):
    await call.message.edit_text(text=strings.LOCATION_CANCELED)


@router.callback_query(
    states.form.Register.location,
    aiogram.F.data == callback.enum.CallbackStatus.YES,
)
async def callback_location_yes(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
):
    data = await state.get_data()
    await call.message.edit_text(
        text=strings.LOCATION_IS_SET_TO.format(data['city'], data['country']),
        reply_markup=None,
    )
    await state.set_state(states.form.Register.bio)


@router.message(
    states.form.Register.bio,
    aiogram.filters.Command('skip'),
)
async def form_bio_skip(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    await state.set_state(states.form.Register.interests)
    await message.answer(strings.BIO_SKIPPED)


@router.message(
    states.form.Register.bio,
    aiogram.F.content_type == aiogram.types.ContentType.TEXT,
)
async def form_bio(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
):
    try:
        bio = validators.user.validate_bio(message.text)
    except validators.core.ValidationError as e:
        await message.answer(str(e))
        return

    await state.update_data(bio=bio)
    await state.set_state(states.form.Register.interests)
    await message.answer(strings.BIO_IS_SET_TO.format(bio))


@router.message(
    states.form.Register.interests,
    aiogram.filters.Command('skip'),
)
async def form_interests_skip(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    await create_user(message, state, db_engine)


@router.message(
    states.form.Register.interests,
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

    await state.update_data(interests=interests)
    await create_user(message, state, db_engine)


async def create_user(
    message: aiogram.types.Message,
    state: aiogram.fsm.context.FSMContext,
    db_engine: sqlalchemy.engine.base.Engine,
):
    state_data = await state.get_data()

    with sqlalchemy.orm.Session(db_engine) as db_session:
        user = db_session.query(models.users.User).get(message.from_user.id)

        user.age = state_data.get('age')
        user.sex = state_data.get('sex')
        user.city = state_data.get('city')
        user.country = state_data.get('country')
        user.bio = state_data.get('bio')

        interests = state_data.get('interests', [])

        for item in interests:
            interest = (
                db_session.query(models.users.Interest)
                .filter_by(name=item)
                .first()
            )

            if not interest:
                interest = models.users.Interest(name=item)

            user.interests.append(interest)

        db_session.add(user)
        db_session.commit()

    await state.clear()
    await message.answer(
        strings.INTERESTS_IS_SET_TO.format(', '.join(interests)),
        reply_markup=keyboards.reply.REMOVE,
    )
    await message.answer(
        strings.MAIN_MENU,
        reply_markup=keyboards.inline.MAIN_MENU,
    )
