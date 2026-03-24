"""
handlers/education.py — раздел образования

Последовательность: Уровень → ВУЗ → Факультет → Специальность → Год
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards import kb_education_input, kb_education_menu, kb_skills_menu
from models import Education
from states import ResumeStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "education_add")
async def cb_education_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeStates.EDUCATION_LEVEL)
    await callback.answer()
    await callback.message.edit_text(
        "🎓 <b>Образование</b> — Шаг 1/5\n\n"
        "Введите <b>уровень образования</b>\n"
        "Пример: Высшее, Бакалавр, Магистр, Среднее специальное",
        reply_markup=kb_education_input()
    )


@router.message(ResumeStates.EDUCATION_LEVEL)
async def process_edu_level(message: Message, state: FSMContext):
    level = message.text.strip()
    if len(level) < 2:
        await message.answer("❌ Введите уровень образования:")
        return
    await state.update_data(edu_level=level)
    await state.set_state(ResumeStates.EDUCATION_INSTITUTION)
    await message.answer(
        f"✅ Уровень: <b>{level}</b>\n\n"
        "Шаг 2/5: Введите <b>название учебного заведения</b>\n"
        "Пример: МГУ им. Ломоносова",
        reply_markup=kb_education_input()
    )


@router.message(ResumeStates.EDUCATION_INSTITUTION)
async def process_edu_institution(message: Message, state: FSMContext):
    inst = message.text.strip()
    if len(inst) < 2:
        await message.answer("❌ Введите название учебного заведения:")
        return
    await state.update_data(edu_institution=inst)
    await state.set_state(ResumeStates.EDUCATION_FACULTY)
    await message.answer(
        f"✅ ВУЗ: <b>{inst}</b>\n\n"
        "Шаг 3/5: Введите <b>факультет</b>",
        reply_markup=kb_education_input()
    )


@router.message(ResumeStates.EDUCATION_FACULTY)
async def process_edu_faculty(message: Message, state: FSMContext):
    faculty = message.text.strip()
    if len(faculty) < 2:
        await message.answer("❌ Введите название факультета:")
        return
    await state.update_data(edu_faculty=faculty)
    await state.set_state(ResumeStates.EDUCATION_SPECIALTY)
    await message.answer(
        f"✅ Факультет: <b>{faculty}</b>\n\n"
        "Шаг 4/5: Введите <b>специальность</b>",
        reply_markup=kb_education_input()
    )


@router.message(ResumeStates.EDUCATION_SPECIALTY)
async def process_edu_specialty(message: Message, state: FSMContext):
    spec = message.text.strip()
    if len(spec) < 2:
        await message.answer("❌ Введите специальность:")
        return
    await state.update_data(edu_specialty=spec)
    await state.set_state(ResumeStates.EDUCATION_YEAR)
    await message.answer(
        f"✅ Специальность: <b>{spec}</b>\n\n"
        "Шаг 5/5: Введите <b>год окончания</b>\n"
        "Пример: 2020",
        reply_markup=kb_education_input()
    )


@router.message(ResumeStates.EDUCATION_YEAR)
async def process_edu_year(message: Message, state: FSMContext):
    year = message.text.strip()
    if len(year) != 4 or not year.isdigit():
        await message.answer("❌ Введите год в формате ГГГГ (например: 2020):")
        return

    data = await state.get_data()
    edu = Education(
        level=data.get("edu_level", ""),
        institution=data.get("edu_institution", ""),
        faculty=data.get("edu_faculty", ""),
        specialty=data.get("edu_specialty", ""),
        year=year,
    )
    db.save_education(message.from_user.id, edu)
    await state.update_data(edu_level=None, edu_institution=None, edu_faculty=None, edu_specialty=None)
    await state.set_state(ResumeStates.EDUCATION_MENU)

    logger.info(f"Образование сохранено для user_id={message.from_user.id}")
    await message.answer(
        f"✅ <b>Образование добавлено!</b>\n\n"
        f"<b>{edu.level}</b> — {edu.institution}\n"
        f"{edu.faculty}, {edu.specialty}, {edu.year}",
        reply_markup=kb_education_menu()
    )


@router.callback_query(F.data == "education_menu")
async def cb_education_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeStates.EDUCATION_MENU)
    await callback.answer()
    await callback.message.edit_text(
        "🎓 <b>Образование</b>\n\nДобавьте образование или переходите к навыкам.",
        reply_markup=kb_education_menu()
    )


@router.callback_query(F.data == "education_done")
async def cb_education_done(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeStates.SKILLS_MENU)
    await callback.answer()
    await callback.message.edit_text(
        "✅ Раздел <b>Образование</b> завершён.\n\n"
        "💻 <b>Навыки</b>\n\n"
        "Добавьте профессиональные навыки или пропустите.",
        reply_markup=kb_skills_menu()
    )
