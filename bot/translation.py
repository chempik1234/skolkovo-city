import csv
import os
from collections import defaultdict

from init.init_1 import users_service
from init.init_0 import bot_config
from models.category import CategoryModel
from custom_types import Language


def load_translations(filepath) -> dict:
    """
    get all possible translation combinations

    ru,en,sp
    word1,word2,word3

    word1: {en: word2, sp: word3}
    word2: {ru: word1, sp: word3}
    word3: {ru: word1, en: word2}
    """
    result = defaultdict(lambda: defaultdict(lambda: "???", {}), {})
    with open(filepath, "r") as file:
        csvreader = csv.reader(file.readlines(), delimiter=",")

        languages = []
        for row in csvreader:
            if not languages:
                languages = row.copy()
                continue
            for ind, word in enumerate(row):
                result[word] = defaultdict(lambda: "???", {lang: word for lang, word in zip(languages, row)})
    return result


async def get_description_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return get_description_for_language(category, language)


async def get_title_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return get_title_for_language(category, language)


async def get_description_for_language(category: CategoryModel, language: Language):
    return category.description_en if language == "en" else category.description_ru


async def get_title_for_language(category: CategoryModel, language: Language):
    return category.title_en if language == "en" else category.title_ru


async def get_title_description_for_chat_id(category: CategoryModel, telegram_id: int | str):
    language = await get_language_for_telegram_id(telegram_id)
    return await get_title_description_for_language(category, language)


async def get_title_description_for_language(category: CategoryModel, language: Language):
    if language == "en":
        return category.title_en, category.description_en
    return category.title_ru, category.description_ru


async def get_language_for_telegram_id(telegram_id: int | str):
    language: Language | None = await users_service.get_language(telegram_id=telegram_id)
    language = "ru" if language is None else language
    return language


def translate_string(string: str, language: Language):
    return TRANSLATIONS[string][language]


TRANSLATIONS = load_translations(os.path.join(bot_config.CONFIG_MOUNT_DIR, "translation.csv"))
