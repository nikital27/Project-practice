import aiogram.fsm.state


class Register(aiogram.fsm.state.StatesGroup):
    login = aiogram.fsm.state.State()
    age = aiogram.fsm.state.State()
    sex = aiogram.fsm.state.State()
    location = aiogram.fsm.state.State()
    bio = aiogram.fsm.state.State()
    interests = aiogram.fsm.state.State()


class Profile(aiogram.fsm.state.StatesGroup):
    login_edit = aiogram.fsm.state.State()
    age_edit = aiogram.fsm.state.State()
    sex_edit = aiogram.fsm.state.State()
    location_edit = aiogram.fsm.state.State()
    bio_edit = aiogram.fsm.state.State()
    interests_edit = aiogram.fsm.state.State()


class AddTravel(aiogram.fsm.state.StatesGroup):
    name = aiogram.fsm.state.State()
    description = aiogram.fsm.state.State()


class AddLocation(aiogram.fsm.state.StatesGroup):
    name = aiogram.fsm.state.State()
    start = aiogram.fsm.state.State()
    end = aiogram.fsm.state.State()


class EditTravel(aiogram.fsm.state.StatesGroup):
    edit_travel_name = aiogram.fsm.state.State()
    edit_travel_description = aiogram.fsm.state.State()
