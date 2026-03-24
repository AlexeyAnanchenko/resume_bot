"""
handlers/start.py — команды /start и /help

Точка входа пользователя в бота.
"""
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import kb_main_menu

logger = logging.getLogger(__name__)
router = Router()

WELCOME_TEXT = (
    "👋 <b>Привет!</b>\n\n"
    "Я помогу тебе создать профессиональное резюме в формате PDF.\n\n"
    "<b>Что я умею:</b>\n"
    "• Собрать данные через удобный диалог\n"
    "• Улучшить текст с помощью AI\n"
    "• Сгенерировать красивый PDF с кириллицей\n\n"
    "Нажми <b>Создать резюме</b> чтобы начать."
)

HELP_TEXT = (
    "❓ <b>Справка</b>\n\n"
    "<b>Команды:</b>\n"
    "/start — главное меню\n"
    "/resume — начать создание резюме\n"
    "/generate — сгенерировать PDF\n"
    "/help — эта справка\n\n"
    "<b>Как это работает:</b>\n"
    "1. Вводишь данные шаг за шагом\n"
    "2. Выбираешь PDF с AI или без\n"
    "3. Получаешь готовый файл\n\n"
    "<b>PDF с AI</b> — DeepSeek улучшит формулировки в профессиональном стиле.\n"
    "<b>PDF без AI</b> — твой текст как есть."
)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer(WELCOME_TEXT, reply_markup=kb_main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT)


@router.callback_query(lambda c: c.data == "help")
async def cb_help(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(HELP_TEXT)


@router.callback_query(lambda c: c.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(WELCOME_TEXT, reply_markup=kb_main_menu())
