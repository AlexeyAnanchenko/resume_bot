"""
bot.py — точка входа приложения

Регистрирует все роутеры и запускает polling.
Добавление нового модуля: import + dp.include_router()

Порядок роутеров важен: более специфичные фильтры — выше.
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import LOG_FILE, LOG_LEVEL, TELEGRAM_BOT_TOKEN

# ─── Логирование ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─── Импорт роутеров ──────────────────────────────────────────────────────────
# Порядок: start → resume → work → education → skills → photo → generate
from handlers.start import router as start_router
from handlers.resume import router as resume_router
from handlers.work import router as work_router
from handlers.education import router as education_router
from handlers.skills import router as skills_router
from handlers.photo import router as photo_router
from handlers.generate import router as generate_router


def create_dispatcher() -> Dispatcher:
    """Создать и настроить диспетчер"""
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
        start_router,
        resume_router,
        work_router,
        education_router,
        skills_router,
        photo_router,
        generate_router,
    )
    return dp


async def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN не задан! Проверьте .env файл.")
        return

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = create_dispatcher()

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
