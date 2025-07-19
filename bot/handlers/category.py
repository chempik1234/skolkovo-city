import structlog
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_functions.category import handle_category
from utils import get_logging_extra

logger = structlog.get_logger(name="handlers.category")

router = Router()


@router.callback_query(F.data.startswith('category_'))
async def category_callback_handler(callback: CallbackQuery, state: FSMContext):
    logging_extra = get_logging_extra(callback.from_user.id)
    logging_extra["category_callback"] = callback.data

    logger.info("category click", extra_data=logging_extra)

    category_id = callback.data.replace('category_', '')
    if category_id == 'None':
        category_id = None
    elif category_id.isdigit():
        category_id = int(category_id)
    else:
        await callback.answer(f"Неверный id: должен быть либо 'None', либо из цифр, здесь - {category_id}",
                              show_alert=True)
        return

    logging_extra["category_id"] = category_id

    try:
        logger.info("handle category click", extra_data=logging_extra)
        await handle_category(current_category_id=category_id, state=state,
                              category_message=callback.message, chat_id=None)
    except Exception as e:
        logger.error("exception while trying to handle category click", extra_data=logging_extra, exc_info=e)
