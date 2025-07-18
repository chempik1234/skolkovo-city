from aiogram import Router, F
from aiogram.enums import ReactionTypeType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReactionTypeEmoji

from config import NewsForm, States
from init import news_service, users_service

router = Router()


@router.message(NewsForm.waiting_for_content)
async def process_news_content(message: Message, state: FSMContext):
    if message.media_group_id is not None:
        await message.answer("Медиагруппы не разрешены из-за сурового API телеграм")
        await message.react([ReactionTypeEmoji(type=ReactionTypeType.EMOJI, emoji="👎")])
        return

    await message.answer("Подождите немного, сейчас начнётся...")
    await news_service.send(message, await users_service.get_objects_field("telegram_id"))

    await message.answer("✅ Контент принят. Рассылка начата в фоновом режиме.")
    await state.set_state(States.default)