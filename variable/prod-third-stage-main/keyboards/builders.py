from __future__ import annotations

import aiogram.utils.keyboard


def reply(items: str | list):
    builder = aiogram.utils.keyboard.ReplyKeyboardBuilder()

    if isinstance(items, str):
        items = [items]

    for item in items:
        builder.button(text=item)

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_username_keyboard(message: aiogram.types.Message):
    return (
        reply(message.from_user.username)
        if message.from_user.username
        else None
    )
