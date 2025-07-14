from aiogram.fsm.context import FSMContext

from config import States
from init import bot, category_service
from keyboards import category_keyboard
from models.category import CategoryModel


async def send_category(category_message, chat_id: int | str | None, category: CategoryModel | None) -> None:
    """
    send | update message with category inline buttons
    :param chat_id: send to chat id (not needed if category_message is not None)
    :param category_message: ``None`` or existing Message to edit (if already surfing)
    :param category: ``CategoryModel|None`` parent category to search children for
    :return: None
    """
    if isinstance(category, CategoryModel):
        text = category.description if category.description else category.title
    else:
        text = "Главное меню"

    keyboard = await category_keyboard(category)

    if category_message is None:
        if chat_id is None:
            raise ValueError("either category_message or chat_id is required")
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    else:
        await category_message.edit_text(text=text)
        await category_message.edit_reply_markup(reply_markup=keyboard)


async def handle_category(current_category_id, chat_id: int | str | None, category_message, state: FSMContext):
    """
    what if user clicked on a category button?

    move in it, or send category.description, etc

    calls ``move_in_category``, ``send_category``
    :param chat_id: send to chat id (not needed if category_message is not None)
    :param category_message: ``None`` or existing Message to edit (if already surfing)
    :param current_category_id: new category id (``int|None``)
    :param state: aiogram state to update
    :return: None
    """
    category = await category_service.get_object(current_category_id)

    await send_category(category_message, chat_id, category)
