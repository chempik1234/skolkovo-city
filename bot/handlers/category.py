from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_functions.category import handle_category, send_category

router = Router()


@router.callback_query(F.data.startswith('category_'))
async def category_callback_handler(callback: CallbackQuery, state: FSMContext):
    category_id = callback.data.replace('category_', '')
    if category_id == 'None':
        category_id = None
    elif category_id.isdigit():
        category_id = int(category_id)
    else:
        await callback.answer(f"Неверный id: должен быть либо 'None', либо из цифр, здесь - {category_id}",
                              show_alert=True)
        return
    await handle_category(current_category_id=category_id, state=state,
                          category_message=callback.message, chat_id=None)
