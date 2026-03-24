"""
handlers/resume.py — сбор базовых данных резюме

Последовательность: ФИО → Email → Телефон → Город → Должность → Меню опыта работы

Валидация: email (regex), телефон (минимум 10 цифр).
"""
import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards import kb_cancel, kb_work_menu
from states import ResumeStates

logger = logging.getLogger(__name__)
router = Router()

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


def _phone_valid(text: str) -> bool:
    return len(re.sub(r'\D', '', text)) >= 10


@router.callback_query(F.data == "resume_start")
@router.message(Command("resume"))
async def start_resume(event, state: FSMContext):
    """Начать сбор данных резюме"""
    await state.clear()
    await state.set_state(ResumeStates.FULL_NAME)

    text = (
        "📝 <b>Создание резюме</b>\n\n"
        "Шаг 1/5: Введите ваше <b>полное имя</b>\n"
        "Пример: Иванов Иван Иванович"
    )
    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(text, reply_markup=kb_cancel())
    else:
        await event.answer(text, reply_markup=kb_cancel())


@router.message(ResumeStates.FULL_NAME)
async def process_full_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Введите корректное имя (минимум 2 символа):")
        return
    await state.update_data(full_name=name)
    await state.set_state(ResumeStates.EMAIL)
    await message.answer(
        f"✅ Имя: <b>{name}</b>\n\n"
        "Шаг 2/5: Введите ваш <b>email</b>\n"
        "Пример: ivan@example.com",
        reply_markup=kb_cancel()
    )


@router.message(ResumeStates.EMAIL)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not EMAIL_RE.match(email):
        await message.answer("❌ Некорректный email. Попробуйте ещё раз:")
        return
    await state.update_data(email=email)
    await state.set_state(ResumeStates.PHONE)
    await message.answer(
        f"✅ Email: <b>{email}</b>\n\n"
        "Шаг 3/5: Введите ваш <b>телефон</b>\n"
        "Пример: +7 (999) 123-45-67",
        reply_markup=kb_cancel()
    )


@router.message(ResumeStates.PHONE)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not _phone_valid(phone):
        await message.answer("❌ Некорректный телефон (минимум 10 цифр). Попробуйте ещё раз:")
        return
    await state.update_data(phone=phone)
    await state.set_state(ResumeStates.CITY)
    await message.answer(
        f"✅ Телефон: <b>{phone}</b>\n\n"
        "Шаг 4/5: Введите ваш <b>город</b>\n"
        "Пример: Москва",
        reply_markup=kb_cancel()
    )


@router.message(ResumeStates.CITY)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if len(city) < 2:
        await message.answer("❌ Введите название города:")
        return
    await state.update_data(city=city)
    await state.set_state(ResumeStates.POSITION)
    await message.answer(
        f"✅ Город: <b>{city}</b>\n\n"
        "Шаг 5/5: Введите вашу <b>желаемую должность</b>\n"
        "Пример: Python-разработчик",
        reply_markup=kb_cancel()
    )


@router.message(ResumeStates.POSITION)
async def process_position(message: Message, state: FSMContext):
    position = message.text.strip()
    if len(position) < 2:
        await message.answer("❌ Введите название должности:")
        return

    data = await state.get_data()
    data["position"] = position

    # Сохраняем базовые данные в БД
    db.save_resume(message.from_user.id, data)
    await state.update_data(position=position)
    await state.set_state(ResumeStates.WORK_MENU)

    await message.answer(
        f"✅ Должность: <b>{position}</b>\n\n"
        "🎉 Базовые данные сохранены!\n\n"
        "📋 <b>Следующий раздел: Опыт работы</b>\n"
        "Добавьте места работы или пропустите этот раздел.",
        reply_markup=kb_work_menu()
    )


@router.callback_query(F.data == "resume_cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    """Отменить создание резюме"""
    await state.clear()
    await callback.answer("Отменено")
    await callback.message.edit_text(
        "❌ Создание резюме отменено.\n\nИспользуйте /resume чтобы начать заново."
    )
