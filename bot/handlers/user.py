from email_validator import validate_email, EmailNotValidError
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from email_validator import validate_email

from bot_functions.user import check_user_data
from config import RegistrationStates, States
from init import users_service
from translation import translate_string as _, get_language_for_telegram_id

router = Router()


@router.message(RegistrationStates.full_name)
async def full_name_input_handler(message: Message, state: FSMContext):
    full_name = message.text
    user_id = message.from_user.id
    language = await get_language_for_telegram_id(user_id)
    if not full_name:
        await message.answer(_(f"Полное имя должно быть непустым", language),
                             show_alert=True)
        return
    await users_service.update_data(user_id, {"full_name": full_name}, create_if_absent=True)
    await check_user_data(user_id, state)


@router.message(RegistrationStates.email)
async def email_input_handler(message: Message, state: FSMContext):
    email = message.text
    user_id = message.from_user.id
    language = await get_language_for_telegram_id(user_id)
    if not email:
        await message.answer(_("Email должен быть непустым", language),
                             show_alert=True, send_success_message=True)
        return

    # validate
    try:
        email = validate_email(email).normalized
    except EmailNotValidError:
        await message.answer(_("Некорректный формат email", language),
                             show_alert=True)
        return

    await users_service.update_data(user_id, {"email": email}, create_if_absent=True)
    await check_user_data(user_id, state, send_success_message=True)


@router.callback_query(RegistrationStates.agreement)
async def agreement_input_handler(callback: CallbackQuery, state: FSMContext):
    answer_yes_no = callback.data
    user_id = callback.from_user.id
    if answer_yes_no != "yes":
        language = await get_language_for_telegram_id(user_id)
        await callback.answer(_("Что ж, можете дать согласие позже.", language))
        return

    await users_service.update_data(user_id, {"personal_data_agreement": True}, create_if_absent=True)
    await check_user_data(user_id, state, send_success_message=True)


@router.callback_query(States.choose_language)
async def choose_language_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = callback.data
    await users_service.update_data(user_id, {"language": language})
    await state.set_state(States.default)
    await callback.answer(_("Язык изменён", language))
