import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import TELEGRAM_BOT_TOKEN

# Настройка логирования - вывод в файл и консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
# Используем HTML вместо Markdown — меньше проблем с экранированием
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Подключение обработчиков
from handlers.resume import router as resume_router
from handlers.photo import router as photo_router
dp.include_router(resume_router)
dp.include_router(photo_router)

# Регистрируем бот в pdf_generator для загрузки фото
from services.pdf_generator import set_bot
set_bot(bot)


@dp.message(Command("generate"))
async def cmd_generate(message: Message, state: FSMContext):
    """Генерация PDF-резюме с AI"""
    logger.info(f"Запрос на генерацию PDF с AI от пользователя {message.from_user.id}")
    await generate_pdf(message, state, use_ai=True)


@dp.callback_query(F.data == "generate_pdf_ai")
async def cb_generate_pdf_ai(callback: CallbackQuery, state: FSMContext):
    """Генерация PDF с AI (callback)"""
    logger.info(f"Запрос на генерацию PDF с AI от пользователя {callback.from_user.id}")
    await callback.answer()
    await generate_pdf(callback.message, state, use_ai=True)


@dp.callback_query(F.data == "generate_pdf_simple")
async def cb_generate_pdf_simple(callback: CallbackQuery, state: FSMContext):
    """Генерация PDF без AI (callback)"""
    logger.info(f"Запрос на генерацию PDF без AI от пользователя {callback.from_user.id}")
    await callback.answer()
    await generate_pdf(callback.message, state, use_ai=False)


async def generate_pdf(message: Message, state: FSMContext, use_ai: bool = True):
    """Общая функция генерации PDF"""
    from services.pdf_generator import pdf_generator
    from aiogram.types import FSInputFile
    import tempfile
    import os

    try:
        # Отправляем сообщение о начале генерации
        ai_text = " с AI-переформулированием" if use_ai else ""
        progress_msg = await message.answer(
            f"⏳ <b>Генерация резюме{ai_text}...</b>\n\n"
            "Это займёт 10-30 секунд."
        )

        # Получаем данные
        state_data = await state.get_data()
        # Используем chat.id как user_id (он одинаковый для пользователя и бота)
        user_id = message.chat.id
        logger.info(f"state_data для PDF: {state_data}")
        logger.info(f"user_id: {user_id}")

        # Проверяем данные в БД
        from database import db
        user_data = db.get_resume(user_id)
        logger.info(f"user_data из БД: {user_data}")

        # Генерируем PDF
        if use_ai:
            pdf_buffer = await pdf_generator.generate(user_id, state_data)
        else:
            pdf_buffer = await pdf_generator.generate_simple(user_id, state_data)

        logger.info(f"PDF размер: {len(pdf_buffer.getvalue())} байт")

        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(pdf_buffer.getvalue())
            temp_path = f.name

        # Отправляем файл
        ai_caption = "\n\nAI переформулировал:\n• Должность\n• Обязанности\n• Достижения\n• Навыки" if use_ai else ""
        await message.answer_document(
            document=FSInputFile(temp_path),
            caption=f"🎉 <b>Ваше резюме готово!</b>{ai_caption}"
        )

        # Удаляем временный файл
        os.unlink(temp_path)
        
        # Удаляем сообщение о прогрессе
        await progress_msg.delete()
        
        logger.info(f"PDF отправлен пользователю {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка генерации PDF: {e}")
        await message.answer(
            "❌ Произошла ошибка при генерации PDF.\n\n"
            f"Техническая информация: {e}"
        )


async def main():
    """Запуск бота"""
    logger.info("Бот запущен...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
