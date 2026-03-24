"""
handlers/skills.py — раздел навыков

Пользователь вводит навыки через запятую, точку с запятой или с новой строки.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import db
from keyboards import kb_photo_menu, kb_skills_menu
from states import ResumeStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "skills_add")
async def cb_skills_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeStates.SKILLS_INPUT)
    await callback.answer()
    await callback.message.edit_text(
        "💻 <b>Навыки</b>\n\n"
        "Введите навыки через запятую, точку с запятой или с новой строки:\n\n"
        "Пример:\n"
        "Python, Django, PostgreSQL\n"
        "Git, Docker, Linux"
    )


@router.message(ResumeStates.SKILLS_INPUT)
async def process_skills(message: Message, state: FSMContext):
    text = message.text.strip()
    skills = db.parse_skills_text(text)

    if not skills:
        await message.answer("❌ Не удалось распознать навыки. Введите хотя бы один:")
        return

    db.save_skills(message.from_user.id, skills)
    await state.set_state(ResumeStates.SKILLS_MENU)

    preview = " • ".join(skills[:8])
    suffix = f" (и ещё {len(skills) - 8})" if len(skills) > 8 else ""
    logger.info(f"Навыки сохранены для user_id={message.from_user.id}: {len(skills)} шт.")

    await message.answer(
        f"✅ <b>Навыки сохранены!</b> ({len(skills)} шт.)\n\n"
        f"{preview}{suffix}",
        reply_markup=kb_skills_menu()
    )


@router.callback_query(F.data == "skills_done")
async def cb_skills_done(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ResumeStates.PHOTO_MENU)
    await callback.answer()
    await callback.message.edit_text(
        "✅ Раздел <b>Навыки</b> завершён.\n\n"
        "📸 <b>Фото</b>\n\n"
        "Добавьте фотографию в резюме (необязательно).",
        reply_markup=kb_photo_menu()
    )
