"""
Обработчики загрузки и обработки фото
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import ResumeState
from database import db

logger = logging.getLogger(__name__)

# Максимальный размер фото: 10MB
MAX_PHOTO_SIZE = 10 * 1024 * 1024

# Разрешённые MIME-типы
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]


def get_photo_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура меню фото"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Отправить фото", callback_data="photo_send")
    builder.button(text="⏭️ Пропустить", callback_data="photo_skip")
    builder.adjust(2)
    return builder


def get_photo_result_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура результата после фото"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 PDF с AI", callback_data="generate_pdf_ai")
    builder.button(text="📄 PDF без AI", callback_data="generate_pdf_simple")
    builder.adjust(2)
    return builder


def get_photo_action_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура действий с фото"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оставить это фото", callback_data="photo_confirm")
    builder.button(text="🔄 Загрузить другое", callback_data="photo_retry")
    builder.button(text="⏭️ Пропустить", callback_data="photo_skip")
    builder.adjust(1)
    return builder


async def validate_photo_size(file_size: int) -> bool:
    """Проверка размера фото"""
    return file_size <= MAX_PHOTO_SIZE


async def is_valid_photo_format(mime_type: str) -> bool:
    """Проверка формата фото"""
    return mime_type in ALLOWED_MIME_TYPES


# Создаём роутер для обработчиков
router = Router()


@router.callback_query(F.data == "photo_send")
async def photo_send_callback(callback: CallbackQuery, state: FSMContext):
    """Запрос фото"""
    logger.info(f"Пользователь {callback.from_user.id} запросил загрузку фото")
    try:
        await state.set_state(ResumeState.PHOTO_ADD)
        await callback.message.edit_text(
            "📸 <b>Загрузка фотографии</b>\n\n"
            "Отправьте вашу фотографию.\n\n"
            "<b>Требования:</b>\n"
            "• Формат: JPEG, PNG, WebP\n"
            "• Размер: до 10MB\n"
            "• Рекомендуемый размер: 3x4 или 4x6\n\n"
            "Или нажмите <b>Пропустить</b>.",
            reply_markup=get_photo_action_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в photo_send_callback: {e}")


@router.message(ResumeState.PHOTO_ADD, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Обработка загруженного фото"""
    logger.info(f"Пользователь {message.from_user.id} отправил фото")
    try:
        # Получаем фото наилучшего качества
        photo = message.photo[-1]

        # Проверяем размер
        if not await validate_photo_size(photo.file_size):
            await message.answer(
                "❌ Фото слишком большое! Максимум 10MB.\n\n"
                "Отправьте фото меньшего размера или нажмите <b>Пропустить</b>.",
                reply_markup=get_photo_action_keyboard().as_markup()
            )
            return

        # Фото в Telegram всегда в формате JPEG, mime_type недоступен для PhotoSize
        # Пропускаем проверку формата

        # Сохраняем информацию о фото
        db.save_photo(
            user_id=message.from_user.id,
            file_id=photo.file_id,
            file_size=photo.file_size,
            mime_type="image/jpeg"  # Telegram отправляет фото в JPEG
        )

        # Показываем превью
        await message.answer_photo(
            photo=photo.file_id,
            caption=(
                "✅ Фото сохранено!\n\n"
                f"Размер: {photo.file_size / 1024:.1f} KB\n\n"
                "Оставить это фото или загрузить другое?"
            ),
            reply_markup=get_photo_action_keyboard().as_markup()
        )

        logger.info(f"Фото сохранено для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_photo: {e}")
        await message.answer("❌ Произошла ошибка при обработке фото. Попробуйте ещё раз.")


@router.callback_query(F.data == "photo_confirm")
async def photo_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Подтверждение фото"""
    logger.info(f"Пользователь {callback.from_user.id} подтвердил фото")
    try:
        await state.set_state(ResumeState.IDLE)
        
        keyboard = get_photo_result_keyboard()
        
        await callback.message.answer(
            "🎉 <b>Резюме готово к генерации!</b>\n\n"
            "Все данные сохранены.\n\n"
            "📄 <b>Выберите формат PDF:</b>\n"
            "• <b>PDF с AI</b> — переформулирует текст в профессиональном стиле\n"
            "• <b>PDF без AI</b> — использует ваши исходные данные",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в photo_confirm_callback: {e}")


@router.callback_query(F.data == "photo_retry")
async def photo_retry_callback(callback: CallbackQuery, state: FSMContext):
    """Повторная загрузка фото"""
    logger.info(f"Пользователь {callback.from_user.id} хочет загрузить другое фото")
    try:
        await state.set_state(ResumeState.PHOTO_ADD)
        await callback.message.edit_text(
            "📸 <b>Загрузка фотографии</b>\n\n"
            "Отправьте новую фотографию.",
            reply_markup=get_photo_action_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в photo_retry_callback: {e}")


@router.callback_query(F.data == "photo_skip")
async def photo_skip_callback(callback: CallbackQuery, state: FSMContext):
    """Пропуск фото"""
    logger.info(f"Пользователь {callback.from_user.id} пропустил загрузку фото")
    try:
        await state.set_state(ResumeState.IDLE)
        await callback.message.answer(
            "✅ Фото пропущено.\n\n"
            "🎉 <b>Резюме готово!</b>\n\n"
            "Все данные сохранены. Теперь вы можете:\n"
            "• Сгенерировать PDF (в разработке)\n"
            "• Редактировать разделы\n"
            "• Начать новое резюме\n\n"
            "Используйте меню для управления.",
            reply_markup=get_photo_menu_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в photo_skip_callback: {e}")
