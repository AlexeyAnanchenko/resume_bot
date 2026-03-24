"""
keyboards.py — ВСЕ inline-клавиатуры проекта

Одно место для всех кнопок. Каждая функция возвращает готовую клавиатуру.
Названия функций: kb_<раздел>_<контекст>

Чтобы изменить текст кнопки — найди нужную функцию и измени text=".."
Чтобы добавить кнопку — добавь builder.button(...) в нужную функцию
"""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def kb_main_menu() -> InlineKeyboardMarkup:
    """Главное меню (/start)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Создать резюме", callback_data="resume_start")
    builder.button(text="❓ Помощь", callback_data="help")
    builder.adjust(2)
    return builder.as_markup()


def kb_cancel() -> InlineKeyboardMarkup:
    """Кнопка отмены (используется во время ввода данных)"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="resume_cancel")
    return builder.as_markup()


def kb_cancel_or_back(back_callback: str) -> InlineKeyboardMarkup:
    """Кнопки назад + отмена"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data=back_callback)
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


# ─── Опыт работы ───────────────────────────────────────────────────────────────

def kb_work_menu() -> InlineKeyboardMarkup:
    """Меню раздела опыта работы"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить место работы", callback_data="work_add")
    builder.button(text="✅ Перейти к образованию", callback_data="work_done")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def kb_work_input() -> InlineKeyboardMarkup:
    """Кнопки во время ввода данных об опыте работы"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад в меню", callback_data="work_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── Образование ───────────────────────────────────────────────────────────────

def kb_education_menu() -> InlineKeyboardMarkup:
    """Меню раздела образования"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Добавить образование", callback_data="education_add")
    builder.button(text="✅ Перейти к навыкам", callback_data="education_done")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def kb_education_input() -> InlineKeyboardMarkup:
    """Кнопки во время ввода данных об образовании"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад в меню", callback_data="education_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── Навыки ────────────────────────────────────────────────────────────────────

def kb_skills_menu() -> InlineKeyboardMarkup:
    """Меню раздела навыков"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💻 Добавить навыки", callback_data="skills_add")
    builder.button(text="✅ Перейти к фото", callback_data="skills_done")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── Фото ──────────────────────────────────────────────────────────────────────

def kb_photo_menu() -> InlineKeyboardMarkup:
    """Меню загрузки фото"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Загрузить фото", callback_data="photo_upload")
    builder.button(text="⏭️ Пропустить", callback_data="photo_skip")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()


def kb_photo_confirm() -> InlineKeyboardMarkup:
    """Подтверждение фото"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Оставить это фото", callback_data="photo_confirm")
    builder.button(text="🔄 Загрузить другое", callback_data="photo_upload")
    builder.button(text="⏭️ Пропустить фото", callback_data="photo_skip")
    builder.adjust(1)
    return builder.as_markup()


# ─── Генерация PDF ─────────────────────────────────────────────────────────────

def kb_generate() -> InlineKeyboardMarkup:
    """Выбор варианта генерации PDF"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 PDF с AI (улучшенный текст)", callback_data="pdf_with_ai")
    builder.button(text="📄 PDF без AI (как есть)", callback_data="pdf_simple")
    builder.adjust(1)
    return builder.as_markup()
