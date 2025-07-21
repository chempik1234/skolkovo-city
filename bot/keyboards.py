from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import category_service
from init_configs import BOT_ROOT_CATEGORY
from models.category import CategoryModel
from utils import get_title_for_language as _t
from translation import translate_string as _


async def category_keyboard(category: CategoryModel | None, language: str = "ru") -> InlineKeyboardMarkup:
    if isinstance(category, CategoryModel):
        category_id, parent_id = category.id, category.parent_id
    else:
        category_id = parent_id = None

    category_children = await category_service.get_children_by_id(category_id)

    keyboard = []
    for category in category_children:
        text = await _t(category, language)
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text if text else "???",
                    callback_data=f'category_{category.id}' if not category.link else None,
                    url=category.link,
                )
            ]
        )
    if category_id != BOT_ROOT_CATEGORY:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=_('Назад', language),
                    callback_data=f'category_{parent_id}',
                ),
                InlineKeyboardButton(
                    text=_('Главное меню', language),
                    callback_data=f'category_{BOT_ROOT_CATEGORY}',
                ),
            ],
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


yes_no_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data='yes',
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data='no',
            ),
        ],
    ],
)

language_keyboards = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🇷🇺",
                callback_data="language_ru",
            ),
            InlineKeyboardButton(
                text="🇬🇧",
                callback_data="language_en",
            ),
        ],
    ],
)
