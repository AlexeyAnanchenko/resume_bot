"""
Скрипт для ручного тестирования бота
Запускает сценарий создания резюме
"""
import asyncio
import logging
import pytest
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat, Update
from handlers.resume import router
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)


@pytest.mark.asyncio
async def test_resume_flow():
    """Тестирование потока создания резюме"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    # Тестовый пользователь
    user = User(id=999, is_bot=False, first_name="Тест", username="test")
    chat = Chat(id=999, type="private")
    
    update_id = 0
    
    print("=" * 50)
    print("ТЕСТ: Запуск бота (/start)")
    print("=" * 50)
    
    # Команда /start
    update_id += 1
    msg = Message(message_id=1, date=1, chat=chat, from_user=user, text="/start")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Начало резюме (/resume)")
    print("=" * 50)
    
    # Команда /resume
    update_id += 1
    msg = Message(message_id=2, date=2, chat=chat, from_user=user, text="/resume")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Ввод ФИО")
    print("=" * 50)
    
    # Ввод ФИО
    update_id += 1
    msg = Message(message_id=3, date=3, chat=chat, from_user=user, text="Иванов Иван")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Ввод email (валидный)")
    print("=" * 50)
    
    # Ввод email
    update_id += 1
    msg = Message(message_id=4, date=4, chat=chat, from_user=user, text="test@example.com")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Ввод телефона")
    print("=" * 50)
    
    # Ввод телефона
    update_id += 1
    msg = Message(message_id=5, date=5, chat=chat, from_user=user, text="+7 (999) 123-45-67")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Ввод города")
    print("=" * 50)
    
    # Ввод города
    update_id += 1
    msg = Message(message_id=6, date=6, chat=chat, from_user=user, text="Москва")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ: Ввод должности")
    print("=" * 50)
    
    # Ввод должности
    update_id += 1
    msg = Message(message_id=7, date=7, chat=chat, from_user=user, text="Разработчик")
    update = Update(update_id=update_id, message=msg)
    await dp.feed_update(bot, update)
    
    print("\n" + "=" * 50)
    print("ТЕСТ ЗАВЕРШЁН")
    print("=" * 50)
    
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(test_resume_flow())
