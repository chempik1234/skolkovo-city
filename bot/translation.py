from init import users_service
from models.category import CategoryModel
from models.user import UserModel


async def get_description_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return get_description_for_language(category, language)


async def get_title_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return get_title_for_language(category, language)


async def get_description_for_language(category: CategoryModel, language: str):
    return category.description_en if language == "en" else category.description_ru


async def get_title_for_language(category: CategoryModel, language: str):
    return category.title_en if language == "en" else category.title_ru


async def get_title_description_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return await get_title_description_for_language(category, language)


async def get_title_description_for_language(category: CategoryModel, language: str):
    if language == "en":
        return category.title_en, category.description_en
    return category.title_ru, category.description_ru


async def get_language_for_telegram_id(telegram_id: int | str):
    # TODO: create a method to receive only language, not the whole model
    user: UserModel | None = await users_service.get_object(telegram_id=telegram_id)
    language = "ru" if user is None else user.language
    return language


async def translate_string(string: str, language: str):
    # TODO: make i18n from scratch
    return string
