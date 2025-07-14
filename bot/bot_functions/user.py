import asyncio

from aiogram.fsm.context import FSMContext

from config import RegistrationStates
from init import users_service, bot
from keyboards import yes_no_keyboard
from models.user import UserModel


def user_data_filled_text(full_name_filled: bool, email_filled: bool, personal_data_agreement_filled: bool):
    return (f"Заполните данные профиля\n"
            f"Полное имя: {'✅' if full_name_filled else '❌'}\n"
            f"Email: {'✅' if email_filled else '❌'}\n"
            f"Согласие на обработку персональных данных: {'✅' if personal_data_agreement_filled else '❌'}")


async def check_user_data(telegram_id: int, state: FSMContext, send_success_message: bool = False) -> bool:
    """
    returns ``True`` if user filled all his fields and now counts as authenticated, else sends him messages
    :param send_success_message: send a success message if ``True``
    :param state: state to update (set to RegistrationStates.<>)
    :param telegram_id: telegram id to check
    :return: ``True`` if user can use bot, else ``False``
    """
    user = await users_service.get_object(telegram_id=telegram_id)

    user_correctly_filled = email_filled = full_name_filled = personal_data_agreement_filled = user is not None
    if isinstance(user, UserModel):
        if not user.email:
            user_correctly_filled = email_filled = False
        if not user.full_name:
            user_correctly_filled = full_name_filled = False
        if not user.personal_data_agreement:
            user_correctly_filled = personal_data_agreement_filled = False
    if user_correctly_filled:
        if send_success_message:
            await bot.send_message(chat_id=telegram_id, text="Данные заполнены! Можете использовать /start")
        return True

    text_beginning = user_data_filled_text(full_name_filled, email_filled, personal_data_agreement_filled) + "\n\n"
    if not full_name_filled:
        await bot.send_message(chat_id=telegram_id, text=f"{text_beginning}Введите имя:")
        await state.set_state(RegistrationStates.full_name)
    elif not email_filled:
        await bot.send_message(chat_id=telegram_id, text=f"{text_beginning}Введите email:")
        await state.set_state(RegistrationStates.email)
    elif not personal_data_agreement_filled:
        await bot.send_message(chat_id=telegram_id,
                               text=f"{text_beginning}Даёте согласие на обработку персональных данных?",
                               reply_markup=yes_no_keyboard)
        await state.set_state(RegistrationStates.agreement)
