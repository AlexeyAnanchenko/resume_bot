"""
handlers/work.py — раздел опыта работы

Последовательность: Должность → Компания → Дата начала → Дата окончания → Обязанности → Достижения
Можно добавить несколько мест работы.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards import kb_education_menu, kb_work_input, kb_work_menu
from models import WorkExperience
from states import ResumeStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "work_add")
async def cb_work_add(callback: CallbackQuery, state: FSMContext):
    """Начать ввод нового места работы"""
    await state.set_state(ResumeStates.WORK_POSITION)
    await callback.answer()
    await callback.message.edit_text(
        "📋 <b>Опыт работы</b> — Шаг 1/6\n\n"
        "Введите вашу <b>должность</b>\n"
        "Пример: Senior Python Developer",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_POSITION)
async def process_work_position(message: Message, state: FSMContext):
    pos = message.text.strip()
    if len(pos) < 2:
        await message.answer("❌ Введите название должности:")
        return
    await state.update_data(w_position=pos)
    await state.set_state(ResumeStates.WORK_COMPANY)
    await message.answer(
        f"✅ Должность: <b>{pos}</b>\n\n"
        "Шаг 2/6: Введите <b>название компании</b>\n"
        "Пример: Яндекс, Сбер, ООО «Ромашка»",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_COMPANY)
async def process_work_company(message: Message, state: FSMContext):
    company = message.text.strip()
    if len(company) < 2:
        await message.answer("❌ Введите название компании:")
        return
    await state.update_data(w_company=company)
    await state.set_state(ResumeStates.WORK_START_DATE)
    await message.answer(
        f"✅ Компания: <b>{company}</b>\n\n"
        "Шаг 3/6: Введите <b>дату начала работы</b>\n"
        "Пример: 01.2020 или Январь 2020",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_START_DATE)
async def process_work_start_date(message: Message, state: FSMContext):
    date = message.text.strip()
    if len(date) < 3:
        await message.answer("❌ Введите корректную дату:")
        return
    await state.update_data(w_start=date)
    await state.set_state(ResumeStates.WORK_END_DATE)
    await message.answer(
        f"✅ Начало: <b>{date}</b>\n\n"
        "Шаг 4/6: Введите <b>дату окончания</b>\n"
        "Или напишите: по настоящее время",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_END_DATE)
async def process_work_end_date(message: Message, state: FSMContext):
    date = message.text.strip()
    if len(date) < 3:
        await message.answer("❌ Введите корректную дату:")
        return
    await state.update_data(w_end=date)
    await state.set_state(ResumeStates.WORK_DUTIES)
    await message.answer(
        f"✅ Окончание: <b>{date}</b>\n\n"
        "Шаг 5/6: Опишите ваши <b>обязанности</b>\n"
        "Можно перечислить через запятую или с новой строки",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_DUTIES)
async def process_work_duties(message: Message, state: FSMContext):
    duties = message.text.strip()
    if len(duties) < 5:
        await message.answer("❌ Опишите обязанности подробнее:")
        return
    await state.update_data(w_duties=duties)
    await state.set_state(ResumeStates.WORK_ACHIEVEMENTS)
    await message.answer(
        "Шаг 6/6: Опишите ваши <b>достижения</b>\n"
        "Пример: Увеличил производительность на 30%\n\n"
        "Или напишите <b>нет</b> если нечего добавить",
        reply_markup=kb_work_input()
    )


@router.message(ResumeStates.WORK_ACHIEVEMENTS)
async def process_work_achievements(message: Message, state: FSMContext):
    achievements = message.text.strip()
    if achievements.lower() in ("нет", "—", "-", ""):
        achievements = ""

    data = await state.get_data()
    exp = WorkExperience(
        position=data.get("w_position", ""),
        company=data.get("w_company", ""),
        start_date=data.get("w_start", ""),
        end_date=data.get("w_end", ""),
        duties=data.get("w_duties", ""),
        achievements=achievements,
    )
    db.add_work_experience(message.from_user.id, exp)

    # Очистить временные данные об опыте работы из state
    await state.update_data(w_position=None, w_company=None, w_start=None,
                             w_end=None, w_duties=None)
    await state.set_state(ResumeStates.WORK_MENU)

    logger.info(f"Сохранён опыт работы для user_id={message.from_user.id}: {exp.company}")
    await message.answer(
        f"✅ <b>Место работы добавлено!</b>\n\n"
        f"<b>{exp.position}</b> в {exp.company}\n"
        f"{exp.start_date} — {exp.end_date}\n\n"
        "Добавить ещё одно место работы или продолжить?",
        reply_markup=kb_work_menu()
    )


@router.callback_query(F.data == "work_menu")
async def cb_work_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню опыта работы"""
    await state.set_state(ResumeStates.WORK_MENU)
    await callback.answer()
    await callback.message.edit_text(
        "📋 <b>Опыт работы</b>\n\nДобавьте места работы или переходите к образованию.",
        reply_markup=kb_work_menu()
    )


@router.callback_query(F.data == "work_done")
async def cb_work_done(callback: CallbackQuery, state: FSMContext):
    """Завершить раздел опыта работы"""
    await state.set_state(ResumeStates.EDUCATION_MENU)
    await callback.answer()
    await callback.message.edit_text(
        "✅ Раздел <b>Опыт работы</b> завершён.\n\n"
        "🎓 <b>Образование</b>\n\n"
        "Добавьте информацию об образовании или пропустите.",
        reply_markup=kb_education_menu()
    )
