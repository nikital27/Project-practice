import aiogram.types

import callback.enum
import keyboards.fabrics
import strings

YES_NO = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.YES,
                callback_data=callback.enum.CallbackStatus.YES,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.NO,
                callback_data=callback.enum.CallbackStatus.NO,
            ),
        ],
    ],
)

MAIN_MENU = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.PROFILE,
                callback_data=callback.enum.CallbackStatus.PROFILE,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.TRAVELS,
                callback_data=keyboards.fabrics.TravelPagination().pack(),
            ),
        ],
    ],
)

PROFILE = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.LOGIN,
                callback_data=callback.enum.CallbackStatus.LOGIN_EDIT,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.SEX,
                callback_data=callback.enum.CallbackStatus.SEX_EDIT,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.AGE,
                callback_data=callback.enum.CallbackStatus.AGE_EDIT,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.BIO,
                callback_data=callback.enum.CallbackStatus.BIO_EDIT,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.LOCATION,
                callback_data=callback.enum.CallbackStatus.LOCATION_EDIT,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.INTERESTS,
                callback_data=callback.enum.CallbackStatus.INTERESTS_EDIT,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.BACK,
                callback_data=callback.enum.CallbackStatus.BACK_MENU,
            ),
        ],
    ],
)

TRAVELS = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.ADD,
                callback_data=callback.enum.CallbackStatus.ADD_TRAVEL,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.SHOW,
                callback_data=callback.enum.CallbackStatus.SHOW_TRAVEL,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.BACK,
                callback_data=callback.enum.CallbackStatus.BACK_MENU,
            ),
        ],
    ],
)

CANCEL_PROFILE = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.CANCEL,
                callback_data=callback.enum.CallbackStatus.BACK_PROFILE,
            ),
        ],
    ],
)

CANCEL_TRAVEL = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.CANCEL,
                callback_data=callback.enum.CallbackStatus.BACK_TRAVEL,
            ),
        ],
    ],
)

SELECT_SEX = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.MAN,
                callback_data=callback.enum.CallbackStatus.MALE,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.WOMAN,
                callback_data=callback.enum.CallbackStatus.FEMALE,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.CANCEL,
                callback_data=callback.enum.CallbackStatus.BACK_PROFILE,
            ),
        ],
    ],
)

TRAVEL = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.LOCATIONS,
                callback_data=callback.enum.CallbackStatus.SHOW_LOCATIONS,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.EDIT,
                callback_data=callback.enum.CallbackStatus.EDIT_TRAVEL,
            ),
            aiogram.types.InlineKeyboardButton(
                text=strings.DELETE,
                callback_data=callback.enum.CallbackStatus.DELETE_TRAVEL,
            ),
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.BACK,
                callback_data=callback.enum.CallbackStatus.BACK_TRAVEL,
            ),
        ],
    ],
)


BACK_TO_TRAVEL = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [
            aiogram.types.InlineKeyboardButton(
                text=strings.BACK,
                callback_data=keyboards.fabrics.TravelPagination().pack(),
            ),
        ],
    ],
)
