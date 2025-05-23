import aiogram
import aiogram.filters

import filters.user
import keyboards.inline
import strings

router = aiogram.Router()


@router.message(aiogram.filters.CommandStart(), filters.user.Registered())
async def main_menu(
    message: aiogram.types.Message,
):
    await message.answer(
        strings.MAIN_MENU,
        reply_markup=keyboards.inline.MAIN_MENU,
    )
