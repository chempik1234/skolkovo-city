from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from init import category_service
from models.category import CategoryModel


async def category_keyboard(category: CategoryModel | None) -> InlineKeyboardMarkup:
    if isinstance(category, CategoryModel):
        category_id, parent_id = category.id, category.parent_id
    else:
        category_id = parent_id = None

    category_children = await category_service.get_children_by_id(category_id)

    keyboard = []
    for category in category_children:
        text = category.title
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=f'category_{category.id}' if not category.link else None,
                    url=category.link,
                )
            ]
        )
    if category_id is not None:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=f'category_{parent_id}',
                ),
                InlineKeyboardButton(
                    text='Главное меню',
                    callback_data='category_None',
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
