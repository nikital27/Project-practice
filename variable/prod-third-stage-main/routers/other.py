import aiogram
import aiogram.filters
import aiogram.fsm.context

import callback.enum
import keyboards.inline
import strings

router = aiogram.Router()


@router.message()
async def other(
    message: aiogram.types.Message,
):
    await message.answer(strings.I_DONT_UNDERSTAND)


@router.callback_query(
    aiogram.F.data == callback.enum.CallbackStatus.BACK_MENU,
)
async def callback_back(
    call: aiogram.types.CallbackQuery,
    state: aiogram.fsm.context.FSMContext,
):
    await state.clear()
    await call.message.edit_text(
        strings.MAIN_MENU,
        reply_markup=keyboards.inline.MAIN_MENU,
    )


@router.callback_query(aiogram.F.data == '-')
async def callback_nothing(call: aiogram.types.CallbackQuery):
    await call.answer()
