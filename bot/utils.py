from init import users_service
from models.category import CategoryModel
from models.user import UserModel


def remove_newline_escapes(text: str) -> str:
    return text.replace("\\n", "\n")


async def get_description_for_chat_id(category: CategoryModel, telegram_id: int | str):
    # TODO: create a method to receive only language, not the whole model
    user: UserModel | None = await users_service.get_object(telegram_id=telegram_id)
    language = "ru" if user is None else user.language
    print(telegram_id, user, language, category.description_ru)
    return category.description_en if language == "en" else category.description_ru
