from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from config import States
from init import bot, category_service
from keyboards import category_keyboard
from models.category import CategoryModel
from translation import (translate_string as _,
                         get_language_for_telegram_id as _l,
                         get_title_description_for_language as _tdl)
from utils import remove_newline_escapes


async def send_category(category_message: Message | None, chat_id: int | str | None, category: CategoryModel | None,
                        state: FSMContext) -> None:
    """
    send | update message with category inline buttons
    :param chat_id: send to chat id (not needed if category_message is not None)
    :param category_message: ``None`` or existing Message to edit (if already surfing)
    :param category: ``CategoryModel|None`` parent category to search children for
    :param state: ``FSMContext`` state to use to find media messages to delete
    :return: None
    """
    telegram_id = chat_id if chat_id is not None else category_message.chat.id
    language = await _l(telegram_id)

    if isinstance(category, CategoryModel):
        # bad for us chat id might be group id, not user id

        title, description = await _tdl(category, language)
        if description:
            text = description
        elif title:
            text = title
        else:
            text = "???"
    else:
        text = _("Привет! Здесь вы можете найти все об ИЦ Сколково.\nВыберите то, что вас сейчас интересует", language)

    keyboard = await category_keyboard(category, language=language)

    text = remove_newline_escapes(text)

    if category_message is None and chat_id is None:
        raise ValueError("either category_message or chat_id is required")

    send_to = chat_id if chat_id else telegram_id

    # erase existing media messages
    existing_media_messages_ids = await state.get_value("media_messages")
    if existing_media_messages_ids and isinstance(existing_media_messages_ids, list):
        await bot.delete_messages(chat_id=send_to, message_ids=existing_media_messages_ids)
        await state.update_data({"media_messages": []})

    send_images = isinstance(category, CategoryModel) and \
                  isinstance(category.images_urls, list) and all(category.images_urls) and category.images_urls
    if send_images:
        photo_urls = category.images_urls
        media_group = [
            InputMediaPhoto(media=url)
            for url in photo_urls[:10]
        ]
        media_group[0].parse_mode = "Markdown"
        messages: list[Message] = await bot.send_media_group(chat_id=send_to, media=media_group)

        # store messages ID so we can erase them later
        messages_ids = [i.message_id for i in messages]
        await state.update_data({"media_messages": messages_ids})


    if send_images or category_message is None:
        await bot.send_message(chat_id=send_to, text=text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await category_message.edit_text(text=text, parse_mode="Markdown")
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

    await send_category(category_message, chat_id, category, state)
