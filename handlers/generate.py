"""
handlers/generate.py — генерация PDF-резюме

Два варианта:
- pdf_with_ai: сначала улучшаем текст через DeepSeek, потом генерируем PDF
- pdf_simple: сразу генерируем PDF из оригинальных данных

Оба варианта используют одни и те же сервисы, разница только в вызове ai_service.
"""
import logging
import os
import tempfile

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from database import db
from services.ai_service import ai_service
from services.pdf_service import pdf_service

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "pdf_with_ai")
async def cb_pdf_with_ai(callback: CallbackQuery, state: FSMContext):
    """Генерация PDF с AI-улучшением"""
    await callback.answer()
    await _generate(callback.message, callback.from_user.id, use_ai=True)


@router.callback_query(F.data == "pdf_simple")
async def cb_pdf_simple(callback: CallbackQuery, state: FSMContext):
    """Генерация PDF без AI"""
    await callback.answer()
    await _generate(callback.message, callback.from_user.id, use_ai=False)


@router.message(Command("generate"))
async def cmd_generate(message: Message):
    """Команда /generate — генерация PDF с AI"""
    await _generate(message, message.from_user.id, use_ai=True)


async def _generate(message: Message, user_id: int, use_ai: bool):
    """
    Основная функция генерации PDF.
    
    Шаги:
    1. Загрузить данные из БД
    2. (Опционально) Улучшить текст через AI
    3. Сгенерировать PDF
    4. Отправить пользователю
    """
    ai_label = " с AI-улучшением" if use_ai else ""
    progress = await message.answer(f"⏳ <b>Генерация резюме{ai_label}...</b>\n\nЭто займёт 10–30 секунд.")

    try:
        # 1. Загрузить данные
        resume = db.load_full_resume(user_id)

        if not resume.full_name and not resume.position:
            await progress.delete()
            await message.answer(
                "❌ Данные резюме не найдены.\n\n"
                "Используйте /resume чтобы начать создание."
            )
            return

        # 2. AI-улучшение (если выбрано)
        if use_ai:
            refined = await ai_service.refine_resume(resume)
            # Подставляем улучшенные данные в резюме
            resume.position = refined.position or resume.position
            resume.work_experiences = refined.work_experiences or resume.work_experiences
            resume.skills = refined.skills or resume.skills

        # 3. Генерация PDF — получаем bot из message
        bot = message.bot
        pdf_buffer = await pdf_service.generate_pdf(resume, bot)

        # 4. Отправка через временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(pdf_buffer.getvalue())
            tmp_path = f.name

        ai_note = "\n\n🤖 <i>Текст улучшен с помощью AI</i>" if use_ai else ""
        await message.answer_document(
            document=FSInputFile(tmp_path, filename=f"resume_{resume.full_name or user_id}.pdf"),
            caption=f"🎉 <b>Ваше резюме готово!</b>{ai_note}"
        )
        os.unlink(tmp_path)

        logger.info(f"PDF отправлен user_id={user_id}, use_ai={use_ai}")

    except Exception as e:
        logger.error(f"Ошибка генерации PDF для user_id={user_id}: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при генерации PDF.\n\n"
            "Попробуйте ещё раз или обратитесь в поддержку."
        )
    finally:
        await progress.delete()
