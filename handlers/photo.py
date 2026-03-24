"""
handlers/photo.py — загрузка фото

Пользователь отправляет фото → сохраняем file_id в БД → предлагаем генерацию PDF.
Фото опционально — можно пропустить.
"""
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import MAX_PHOTO_SIZE_BYTES
from database import db
from keyboards import kb_generate, kb_photo_confirm, kb_photo_menu
from states import ResumeStates

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "photo_upload")
async def cb_photo_upload(callback: CallbackQuery, state: FSMContext):
    """Запросить фото у пользователя"""
    await state.set_state(ResumeStates.PHOTO_WAITING)
    await callback.answer()
    await callback.message.edit_text(
        "📸 <b>Загрузка фото</b>\n\n"
        "Отправьте вашу фотографию.\n\n"
        "<b>Требования:</b>\n"
        f"• Формат: JPEG, PNG\n"
        f"• Размер: до {MAX_PHOTO_SIZE_BYTES // 1024 // 1024} MB\n"
        "• Рекомендуется: портретное фото 3×4"
    )


@router.message(ResumeStates.PHOTO_WAITING, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработать загруженное фото"""
    photo = message.photo[-1]  # Лучшее качество

    if photo.file_size and photo.file_size > MAX_PHOTO_SIZE_BYTES:
        await message.answer(
            f"❌ Фото слишком большое! Максимум {MAX_PHOTO_SIZE_BYTES // 1024 // 1024} MB.\n"
            "Отправьте фото меньшего размера.",
            reply_markup=kb_photo_menu()
        )
        return

    db.save_photo(message.from_user.id, file_id=photo.file_id, file_size=photo.file_size or 0)
    await state.set_state(ResumeStates.PHOTO_MENU)

    size_kb = (photo.file_size or 0) / 1024
    logger.info(f"Фото сохранено для user_id={message.from_user.id}, size={size_kb:.0f}KB")

    await message.answer_photo(
        photo=photo.file_id,
        caption=(
            "✅ <b>Фото сохранено!</b>\n\n"
            f"Размер: {size_kb:.0f} KB\n\n"
            "Оставить это фото или загрузить другое?"
        ),
        reply_markup=kb_photo_confirm()
    )


@router.message(ResumeStates.PHOTO_WAITING)
async def process_photo_wrong_type(message: Message):
    """Пользователь прислал не фото"""
    await message.answer(
        "❌ Пожалуйста, отправьте фотографию (не файл и не документ)."
    )


@router.callback_query(F.data == "photo_confirm")
async def cb_photo_confirm(callback: CallbackQuery, state: FSMContext):
    """Фото подтверждено → предложить генерацию PDF"""
    await state.set_state(ResumeStates.DONE)
    await callback.answer()
    await callback.message.answer(
        "🎉 <b>Резюме готово к генерации!</b>\n\n"
        "Выберите вариант PDF:\n"
        "• <b>С AI</b> — DeepSeek улучшит формулировки\n"
        "• <b>Без AI</b> — ваш текст как есть",
        reply_markup=kb_generate()
    )


@router.callback_query(F.data == "photo_skip")
async def cb_photo_skip(callback: CallbackQuery, state: FSMContext):
    """Пропустить фото → предложить генерацию PDF"""
    await state.set_state(ResumeStates.DONE)
    await callback.answer()
    await callback.message.answer(
        "⏭️ Фото пропущено.\n\n"
        "🎉 <b>Резюме готово к генерации!</b>\n\n"
        "Выберите вариант PDF:\n"
        "• <b>С AI</b> — DeepSeek улучшит формулировки\n"
        "• <b>Без AI</b> — ваш текст как есть",
        reply_markup=kb_generate()
    )
