import aiogram.types

REMOVE = aiogram.types.ReplyKeyboardRemove()

LOCATION = aiogram.types.ReplyKeyboardMarkup(
    keyboard=[
        [
            aiogram.types.KeyboardButton(
                text='Поделиться местоположением',
                request_location=True,
            ),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Поделиться местоположением',
)
