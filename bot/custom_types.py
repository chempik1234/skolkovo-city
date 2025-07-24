from enum import Enum
from typing import Literal

Language = Literal['ru', 'en']


class LanguageEnum(Enum):
    en = 'en'
    ru = 'ru'
