import asyncio

from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMedia, URLInputFile

from init import bot, category_service, weather_service
from init.init_0 import bot_config
from keyboards import category_keyboard
from middlewares.prometheus import track_category_click_async
from models.category import CategoryModel
from translation import (translate_string as _,
                         get_language_for_telegram_id as _l,
                         get_title_description_for_language as _tdl)
from utils import remove_newline_escapes


async def delete_media_messages_from_state(state: FSMContext, chat_id: int | str):
    existing_media_messages_ids = await state.get_value("media_messages")
    if existing_media_messages_ids and isinstance(existing_media_messages_ids, list):
        await bot.delete_messages(chat_id=chat_id, message_ids=existing_media_messages_ids)


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
    asyncio.create_task(delete_media_messages_from_state(state, send_to))

    # append weather to text
    if isinstance(category, CategoryModel) and str(category.id) == bot_config.BOT_ROOT_CATEGORY_STR or category is None:
        weather_text = await weather_service.get_weather_text(language)
        if weather_text:
            if "{{weather}}" in text:
                text = text.replace("{{weather}}", weather_text)
            else:
                text = "\n\n".join([weather_text, text])

    await state.update_data({"media_messages": []})

    if category is None:
        send_media = False
    else:
        send_media = isinstance(category, CategoryModel) and \
                     (isinstance(category.images_urls, list) and all(category.images_urls) and category.images_urls) or \
                     (isinstance(category.videos_urls, list) and all(category.videos_urls) and category.videos_urls)

    if send_media:
        media_messages: list[Message] = []

        media_group: list[InputMedia] = []
        photo_urls = category.images_urls if category else None
        video_urls = category.videos_urls if category else None
        if photo_urls:
            media_group.extend([
                InputMediaPhoto(media=url)
                for url in photo_urls[:10]
            ])
        if video_urls:
            for url in video_urls:
                try:
                    video_message = await bot.send_video(send_to, URLInputFile(url, timeout=60))
                    media_messages.append(video_message)
                except TelegramNetworkError:
                    message = await bot.send_message(send_to, f"Не удалось отправить видео, откройте по (ссылке)[{url}]",
                                                     parse_mode="Markdown")
                    media_messages.append(message)

        if media_group:
            media_group[0].parse_mode = "Markdown"
            media_messages.extend(await bot.send_media_group(chat_id=send_to, media=media_group))

        # store messages ID so we can erase them later
        messages_ids = [i.message_id for i in media_messages]
        await state.update_data({"media_messages": messages_ids})


    if send_media or category_message is None:
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

    if bot_config.USE_PROMETHEUS():
        if category is None:
            parent_title = "None"
            category_title = "None"
        else:
            parent_category = await category_service.get_object(category.parent_id)
            parent_title = parent_category.title_ru if parent_category is not None else "None"
            category_title = category.title_ru
        asyncio.create_task(track_category_click_async(f"{category_title} ({parent_title})"))

    await send_category(category_message, chat_id, category, state)
