import re
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from states import ResumeState
from database import db

logger = logging.getLogger(__name__)

# Валидация email
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


async def validate_email(text: str) -> bool:
    """Проверка корректности email"""
    return bool(EMAIL_PATTERN.match(text.strip()))


async def validate_phone(text: str) -> bool:
    """Проверка телефона (минимум 10 цифр)"""
    digits = re.sub(r'\D', '', text)
    return len(digits) >= 10


def get_start_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура для /start"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Создать резюме", callback_data="start_resume")
    builder.button(text="❓ Помощь", callback_data="start_help")
    builder.adjust(2)
    return builder


def get_education_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура меню образования"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Добавить образование", callback_data="education_add")
    builder.button(text="✅ Завершить и перейти к навыкам", callback_data="education_finish")
    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder


def get_skills_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура меню навыков"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💻 Добавить навыки", callback_data="skills_add")
    builder.button(text="✅ Завершить создание резюме", callback_data="skills_finish")
    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder


def get_work_menu_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура меню опыта работы"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить место работы", callback_data="work_add")
    builder.button(text="✅ Завершить и продолжить", callback_data="work_finish")
    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder


def get_work_action_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура действий при добавлении опыта"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="work_back")
    builder.button(text="❌ Отмена", callback_data="work_cancel")
    builder.adjust(2)
    return builder


def get_continue_keyboard() -> InlineKeyboardBuilder:
    """Клавиатура продолжения"""
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Продолжить", callback_data="continue_next")
    builder.button(text="❌ Отмена", callback_data="cancel_resume")
    builder.adjust(2)
    return builder


# Создаём роутер для обработчиков
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    logger.info(f"Команда /start от пользователя {message.from_user.id}")
    try:
        keyboard = get_start_keyboard()
        await message.answer(
            "👋 Привет! Я бот для создания профессиональных резюме.\n\n"
            "Я помогу тебе составить качественное резюме в формате PDF.\n\n"
            "Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
        logger.info(f"Показано меню /start пользователю {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")


@router.callback_query(F.data == "start_resume")
async def start_resume_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Создать резюме' из /start"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Создать резюме'")
    try:
        await state.set_state(ResumeState.FULL_NAME)
        await callback.message.edit_text(
            "📝 <b>Начинаем создание резюме</b>\n\n"
            "Шаг 1/5: Введите ваше <b>ФИО полностью</b>\n"
            "(например: Иванов Иван Иванович)"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в start_resume_callback: {e}")


@router.callback_query(F.data == "start_help")
async def start_help_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Помощь' из /start"""
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Помощь'")
    try:
        keyboard = get_start_keyboard()
        await callback.message.edit_text(
            "📚 <b>Справка</b>\n\n"
            "Я помогу вам создать профессиональное резюме.\n\n"
            "<b>Команды:</b>\n"
            "/start - Запустить бота\n"
            "/resume - Начать создание резюме\n"
            "/generate - Сгенерировать PDF-резюме\n"
            "/cancel - Отменить текущее действие\n"
            "/help - Эта справка\n\n"
            "<b>Как это работает:</b>\n"
            "1. Бот задаёт вопросы по очереди\n"
            "2. Вы отвечаете (ФИО, контакты, опыт, образование, навыки)\n"
            "3. Отправляете команду `/generate`\n"
            "4. AI переформулирует данные в профессиональный стиль\n"
            "5. Вы получаете готовое PDF-резюме",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в start_help_callback: {e}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    logger.info(f"Команда /help от пользователя {message.from_user.id}")
    try:
        keyboard = get_start_keyboard()
        await message.answer(
            "📚 <b>Справка</b>\n\n"
            "<b>Доступные команды:</b>\n\n"
            "/start - Запустить бота и показать меню\n"
            "/resume - Начать создание резюме\n"
            "/cancel - Отменить текущее действие\n"
            "/help - Показать эту справку\n\n"
            "<b>Как это работает:</b>\n"
            "1. Бот задаёт вопросы по очереди\n"
            "2. AI переформулирует ответы в профессиональный стиль\n"
            "3. Вы получаете готовое PDF-резюме",
            reply_markup=keyboard.as_markup()
        )
        logger.info(f"Показана справка пользователю {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в cmd_help: {e}")


@router.message(Command("resume"))
async def cmd_resume(message: Message, state: FSMContext):
    """Начало создания резюме"""
    logger.info(f"Команда /resume от пользователя {message.from_user.id}")
    try:
        await state.set_state(ResumeState.FULL_NAME)
        await message.answer(
            "📝 <b>Начинаем создание резюме</b>\n\n"
            "Шаг 1/5: Введите ваше <b>ФИО полностью</b>\n"
            "(например: Иванов Иван Иванович)"
        )
        logger.info(f"Запрошено ФИО от пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в cmd_resume: {e}")


@router.message(F.text, ResumeState.FULL_NAME)
async def process_full_name(message: Message, state: FSMContext):
    """Обработка ФИО"""
    logger.info(f"Получено ФИО от пользователя {message.from_user.id}: {message.text}")
    try:
        full_name = message.text.strip()
        if len(full_name) < 3:
            await message.answer("❌ ФИО слишком короткое. Введите полное ФИО:")
            return

        await state.update_data(full_name=full_name)
        await state.set_state(ResumeState.EMAIL)
        await message.answer(
            f"✅ Принято: {full_name}\n\n"
            "Шаг 2/5: Введите ваш <b>email</b>\n"
            "(например: example@mail.ru)"
        )
        logger.info(f"ФИО сохранено, запрошен email от пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_full_name: {e}")


@router.message(F.text, ResumeState.EMAIL)
async def process_email(message: Message, state: FSMContext):
    """Обработка email"""
    logger.info(f"Получен email от пользователя {message.from_user.id}: {message.text}")
    try:
        email = message.text.strip()
        if not await validate_email(email):
            await message.answer("❌ Неверный формат email. Попробуйте ещё раз:")
            return

        await state.update_data(email=email)
        await state.set_state(ResumeState.PHONE)
        await message.answer(
            f"✅ Email сохранён: {email}\n\n"
            "Шаг 3/5: Введите ваш <b>телефон</b>\n"
            "(например: +7 (999) 123-45-67)"
        )
        logger.info(f"Email сохранён, запрошен телефон от пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_email: {e}")


@router.message(F.text, ResumeState.PHONE)
async def process_phone(message: Message, state: FSMContext):
    """Обработка телефона"""
    logger.info(f"Получен телефон от пользователя {message.from_user.id}: {message.text}")
    try:
        phone = message.text.strip()
        if not await validate_phone(phone):
            await message.answer("❌ Телефон должен содержать минимум 10 цифр. Попробуйте ещё раз:")
            return

        await state.update_data(phone=phone)
        await state.set_state(ResumeState.CITY)
        await message.answer(
            f"✅ Телефон сохранён: {phone}\n\n"
            "Шаг 4/5: Введите ваш <b>город</b>\n"
            "(например: Москва, Санкт-Петербург, Екатеринбург)"
        )
        logger.info(f"Телефон сохранён, запрошен город от пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_phone: {e}")


@router.message(F.text, ResumeState.CITY)
async def process_city(message: Message, state: FSMContext):
    """Обработка города"""
    logger.info(f"Получен город от пользователя {message.from_user.id}: {message.text}")
    try:
        city = message.text.strip()
        if len(city) < 2:
            await message.answer("❌ Введите корректное название города:")
            return

        await state.update_data(city=city)
        await state.set_state(ResumeState.POSITION)
        await message.answer(
            f"✅ Город: {city}\n\n"
            "Шаг 5/5: Введите <b>желаемую должность</b>\n"
            "(например: Python-разработчик, Менеджер по продажам, Бухгалтер)"
        )
        logger.info(f"Город сохранён, запрошена должность от пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_city: {e}")


@router.message(F.text, ResumeState.POSITION)
async def process_position(message: Message, state: FSMContext):
    """Обработка должности и завершение базового сбора данных"""
    logger.info(f"Получена должность от пользователя {message.from_user.id}: {message.text}")
    try:
        position = message.text.strip()
        if len(position) < 2:
            await message.answer("❌ Введите корректное название должности:")
            return

        # Сохраняем все данные
        data = await state.get_data()
        data["position"] = position
        data["user_id"] = message.from_user.id
        db.save_user_data(message.from_user.id, data)

        await state.set_state(ResumeState.WORK_MENU)
        
        keyboard = get_work_menu_keyboard()
        await message.answer(
            f"✅ Должность: {position}\n\n"
            "🎉 <b>Базовые данные сохранены!</b>\n\n"
            "Теперь добавьте опыт работы — это повысит шансы на собеседование:\n\n"
            "• Укажите должность\n"
            "• Компанию\n"
            "• Период работы\n"
            "• Обязанности и достижения\n\n"
            "Можно добавить несколько мест работы.",
            reply_markup=keyboard.as_markup()
        )
        logger.info(f"Должность сохранена, показано меню опыта работы для пользователя {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка в process_position: {e}")


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся в главное меню")
    try:
        await state.clear()
        keyboard = get_start_keyboard()
        await callback.message.edit_text(
            "🏠 <b>Главное меню</b>\n\n"
            "Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в main_menu_callback: {e}")


@router.callback_query(F.data == "work_add")
async def work_add_callback(callback: CallbackQuery, state: FSMContext):
    """Начало добавления опыта работы"""
    logger.info(f"Пользователь {callback.from_user.id} начал добавление опыта работы")
    try:
        await state.set_state(ResumeState.WORK_ADD_POSITION)
        await callback.message.edit_text(
            "💼 <b>Добавление опыта работы</b>\n\n"
            "Шаг 1/5: Введите <b>должность</b>\n"
            "(например: Старший разработчик)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в work_add_callback: {e}")


@router.callback_query(F.data == "work_back")
async def work_back_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат в меню опыта работы"""
    logger.info(f"Пользователь {callback.from_user.id} вернулся в меню опыта работы")
    try:
        await state.set_state(ResumeState.WORK_MENU)
        await callback.message.edit_text(
            "📋 <b>Меню опыта работы</b>\n\n"
            "Добавьте информацию о местах работы.",
            reply_markup=get_work_menu_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в work_back_callback: {e}")


@router.callback_query(F.data == "work_cancel")
async def work_cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена добавления опыта работы"""
    logger.info(f"Пользователь {callback.from_user.id} отменил добавление опыта работы")
    try:
        await state.set_state(ResumeState.WORK_MENU)
        await callback.message.edit_text(
            "📋 <b>Меню опыта работы</b>\n\n"
            "Добавьте информацию о местах работы.",
            reply_markup=get_work_menu_keyboard().as_markup()
        )
        await callback.answer("Отменено")
    except Exception as e:
        logger.error(f"Ошибка в work_cancel_callback: {e}")


@router.callback_query(F.data == "work_finish")
async def work_finish_callback(callback: CallbackQuery, state: FSMContext):
    """Завершение раздела опыта работы"""
    logger.info(f"Пользователь {callback.from_user.id} завершил раздел опыта работы")
    try:
        await state.set_state(ResumeState.EDUCATION_MENU)
        keyboard = get_education_menu_keyboard()
        await callback.message.edit_text(
            "✅ Раздел <b>Опыт работы</b> завершён.\n\n"
            "🎓 <b>Образование</b>\n\n"
            "Добавьте информацию об образовании:\n"
            "• Уровень (бакалавр/магистр)\n"
            "• Учебное заведение\n"
            "• Факультет и специальность\n"
            "• Год окончания",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в work_finish_callback: {e}")


@router.callback_query(F.data == "education_add")
async def education_add_callback(callback: CallbackQuery, state: FSMContext):
    """Начало добавления образования"""
    logger.info(f"Пользователь {callback.from_user.id} начал добавление образования")
    try:
        await state.set_state(ResumeState.EDUCATION_LEVEL)
        await callback.message.edit_text(
            "🎓 <b>Добавление образования</b>\n\n"
            "Шаг 1/5: Введите <b>уровень образования</b>\n"
            "(например: Высшее, Бакалавр, Магистр, Среднее специальное)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в education_add_callback: {e}")


@router.message(ResumeState.EDUCATION_LEVEL)
async def process_education_level(message: Message, state: FSMContext):
    """Обработка уровня образования"""
    logger.info(f"Получен уровень образования: {message.text}")
    try:
        level = message.text.strip()
        if len(level) < 2:
            await message.answer("❌ Введите корректный уровень образования:")
            return

        await state.update_data(education_level=level)
        await state.set_state(ResumeState.EDUCATION_INSTITUTION)
        await message.answer(
            f"✅ Уровень: {level}\n\n"
            "Шаг 2/5: Введите <b>название учебного заведения</b>\n"
            "(например: МГУ им. Ломоносова, СПбГУ, МФТИ)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_education_level: {e}")


@router.message(ResumeState.EDUCATION_INSTITUTION)
async def process_education_institution(message: Message, state: FSMContext):
    """Обработка учебного заведения"""
    logger.info(f"Получено учебное заведение: {message.text}")
    try:
        institution = message.text.strip()
        if len(institution) < 2:
            await message.answer("❌ Введите корректное название учебного заведения:")
            return

        await state.update_data(education_institution=institution)
        await state.set_state(ResumeState.EDUCATION_FACULTY)
        await message.answer(
            f"✅ Учебное заведение: {institution}\n\n"
            "Шаг 3/5: Введите <b>факультет</b>\n"
            "(например: Факультет вычислительной математики и кибернетики)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_education_institution: {e}")


@router.message(ResumeState.EDUCATION_FACULTY)
async def process_education_faculty(message: Message, state: FSMContext):
    """Обработка факультета"""
    logger.info(f"Получен факультет: {message.text}")
    try:
        faculty = message.text.strip()
        if len(faculty) < 2:
            await message.answer("❌ Введите корректное название факультета:")
            return

        await state.update_data(education_faculty=faculty)
        await state.set_state(ResumeState.EDUCATION_SPECIALTY)
        await message.answer(
            f"✅ Факультет: {faculty}\n\n"
            "Шаг 4/5: Введите <b>специальность</b>\n"
            "(например: Прикладная математика, Программная инженерия)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_education_faculty: {e}")


@router.message(ResumeState.EDUCATION_SPECIALTY)
async def process_education_specialty(message: Message, state: FSMContext):
    """Обработка специальности"""
    logger.info(f"Получена специальность: {message.text}")
    try:
        specialty = message.text.strip()
        if len(specialty) < 2:
            await message.answer("❌ Введите корректное название специальности:")
            return

        await state.update_data(education_specialty=specialty)
        await state.set_state(ResumeState.EDUCATION_YEAR)
        await message.answer(
            f"✅ Специальность: {specialty}\n\n"
            "Шаг 5/5: Введите <b>год окончания</b>\n"
            "(например: 2020, 2021, 2022)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_education_specialty: {e}")


@router.message(ResumeState.EDUCATION_YEAR)
async def process_education_year(message: Message, state: FSMContext):
    """Обработка года окончания"""
    logger.info(f"Получен год окончания: {message.text}")
    try:
        year = message.text.strip()
        if len(year) != 4 or not year.isdigit():
            await message.answer("❌ Введите год в формате YYYY (например: 2020):")
            return

        # Сохраняем образование
        data = await state.get_data()
        education = {
            "level": data.get("education_level", ""),
            "institution": data.get("education_institution", ""),
            "faculty": data.get("education_faculty", ""),
            "specialty": data.get("education_specialty", ""),
            "year": year
        }
        db.save_education(message.from_user.id, education)

        # Очищаем временные данные
        await state.update_data(
            education_level=None, education_institution=None,
            education_faculty=None, education_specialty=None
        )

        await state.set_state(ResumeState.EDUCATION_MENU)
        keyboard = get_education_menu_keyboard()
        await message.answer(
            f"✅ Образование добавлено!\n\n"
            f"<b>{education['level']}</b>\n"
            f"{education['institution']}\n"
            f"Факультет: {education['faculty']}\n"
            f"Специальность: {education['specialty']}\n"
            f"Год окончания: {education['year']}\n\n"
            "Добавить ещё одно образование или продолжить?",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_education_year: {e}")


@router.callback_query(F.data == "education_finish")
async def education_finish_callback(callback: CallbackQuery, state: FSMContext):
    """Завершение раздела образования"""
    logger.info(f"Пользователь {callback.from_user.id} завершил раздел образования")
    try:
        await state.set_state(ResumeState.SKILLS_MENU)
        keyboard = get_skills_menu_keyboard()
        await callback.message.edit_text(
            "✅ Раздел <b>Образование</b> завершён.\n\n"
            "💻 <b>Навыки</b>\n\n"
            "Добавьте ваши профессиональные навыки:\n"
            "• Языки программирования (Python, Java...)\n"
            "• Фреймворки (Django, Spring...)\n"
            "• Инструменты (Git, Docker...)\n\n"
            "Можно вводить через запятую или каждый с новой строки.",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в education_finish_callback: {e}")


@router.callback_query(F.data == "skills_add")
async def skills_add_callback(callback: CallbackQuery, state: FSMContext):
    """Добавление навыков"""
    logger.info(f"Пользователь {callback.from_user.id} начал добавление навыков")
    try:
        await state.set_state(ResumeState.SKILLS_ADD)
        await callback.message.edit_text(
            "💻 <b>Добавление навыков</b>\n\n"
            "Введите навыки через запятую, точку с запятой или с новой строки:\n\n"
            "Пример:\n"
            "Python, JavaScript, SQL\n"
            "Git, Docker, Kubernetes\n"
            "PostgreSQL, MongoDB",
            reply_markup=get_work_action_keyboard().as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в skills_add_callback: {e}")


@router.message(ResumeState.SKILLS_ADD)
async def process_skills_add(message: Message, state: FSMContext):
    """Обработка добавления навыков"""
    logger.info(f"Получены навыки: {message.text}")
    try:
        text = message.text.strip()
        if len(text) < 2:
            await message.answer("❌ Введите хотя бы один навык:")
            return

        # Парсим навыки
        skills = db.parse_skills(text)
        if not skills:
            await message.answer("❌ Не удалось распознать навыки. Попробуйте ещё раз:")
            return

        # Сохраняем навыки
        db.save_skills(message.from_user.id, skills)

        await state.set_state(ResumeState.SKILLS_MENU)
        keyboard = get_skills_menu_keyboard()
        
        skills_list = "\n".join(f"• {skill}" for skill in skills[:10])
        if len(skills) > 10:
            skills_list += f"\n... и ещё {len(skills) - 10}"
        
        await message.answer(
            f"✅ Навыки сохранены!\n\n"
            f"Добавлено: {len(skills)}\n\n"
            f"{skills_list}\n\n"
            "Добавить ещё навыки или завершить создание резюме?",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_skills_add: {e}")


@router.callback_query(F.data == "skills_finish")
async def skills_finish_callback(callback: CallbackQuery, state: FSMContext):
    """Завершение раздела навыков и переход к фото"""
    logger.info(f"Пользователь {callback.from_user.id} завершил раздел навыков")
    try:
        await state.set_state(ResumeState.PHOTO_MENU)
        # Импортируем здесь, чтобы избежать циклического импорта
        from handlers.photo import get_photo_menu_keyboard
        keyboard = get_photo_menu_keyboard()
        await callback.message.edit_text(
            "✅ Навыки сохранены!\n\n"
            "📸 <b>Следующий шаг: Фото</b>\n\n"
            "Вы можете добавить фотографию в резюме.\n"
            "Это необязательно, но может повысить шансы.\n\n"
            "Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в skills_finish_callback: {e}")


@router.callback_query(F.data == "cancel_resume")
async def cancel_resume_callback(callback: CallbackQuery, state: FSMContext):
    """Отмена создания резюме"""
    logger.info(f"Пользователь {callback.from_user.id} отменил создание резюме")
    try:
        await state.clear()
        await callback.message.edit_text(
            "❌ Создание резюме отменено.\n\n"
            "Используйте /resume чтобы начать заново."
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в cancel_resume_callback: {e}")


@router.message(ResumeState.WORK_ADD_POSITION)
async def process_work_position(message: Message, state: FSMContext):
    """Обработка должности в опыте работы"""
    logger.info(f"Получена должность опыта работы: {message.text}")
    try:
        position = message.text.strip()
        if len(position) < 2:
            await message.answer("❌ Введите корректное название должности:")
            return

        await state.update_data(work_position=position)
        await state.set_state(ResumeState.WORK_ADD_COMPANY)
        await message.answer(
            f"✅ Должность: {position}\n\n"
            "Шаг 2/5: Введите <b>название компании</b>\n"
            "(например: Яндекс, Сбер, ИП Иванов)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_position: {e}")


@router.message(ResumeState.WORK_ADD_COMPANY)
async def process_work_company(message: Message, state: FSMContext):
    """Обработка компании"""
    logger.info(f"Получена компания: {message.text}")
    try:
        company = message.text.strip()
        if len(company) < 2:
            await message.answer("❌ Введите корректное название компании:")
            return

        await state.update_data(work_company=company)
        await state.set_state(ResumeState.WORK_ADD_START_DATE)
        await message.answer(
            f"✅ Компания: {company}\n\n"
            "Шаг 3/5: Введите <b>дату начала работы</b>\n"
            "(например: 01.2020 или Январь 2020)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_company: {e}")


@router.message(ResumeState.WORK_ADD_START_DATE)
async def process_work_start_date(message: Message, state: FSMContext):
    """Обработка даты начала работы"""
    logger.info(f"Получена дата начала: {message.text}")
    try:
        start_date = message.text.strip()
        if len(start_date) < 3:
            await message.answer("❌ Введите корректную дату:")
            return

        await state.update_data(work_start_date=start_date)
        await state.set_state(ResumeState.WORK_ADD_END_DATE)
        await message.answer(
            f"✅ Дата начала: {start_date}\n\n"
            "Шаг 4/5: Введите <b>дату окончания</b>\n"
            "или напишите <b>по настоящее время</b>",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_start_date: {e}")


@router.message(ResumeState.WORK_ADD_END_DATE)
async def process_work_end_date(message: Message, state: FSMContext):
    """Обработка даты окончания работы"""
    logger.info(f"Получена дата окончания: {message.text}")
    try:
        end_date = message.text.strip()
        if len(end_date) < 3:
            await message.answer("❌ Введите корректную дату:")
            return

        await state.update_data(work_end_date=end_date)
        await state.set_state(ResumeState.WORK_ADD_DUTIES)
        await message.answer(
            f"✅ Дата окончания: {end_date}\n\n"
            "Шаг 5/5: Введите <b>обязанности</b>\n"
            "(перечислите через запятую или с новой строки)",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_end_date: {e}")


@router.message(ResumeState.WORK_ADD_DUTIES)
async def process_work_duties(message: Message, state: FSMContext):
    """Обработка обязанностей"""
    logger.info(f"Получены обязанности: {message.text}")
    try:
        duties = message.text.strip()
        if len(duties) < 5:
            await message.answer("❌ Введите корректное описание обязанностей:")
            return

        await state.update_data(work_duties=duties)
        await state.set_state(ResumeState.WORK_ADD_ACHIEVEMENTS)
        await message.answer(
            f"✅ Обязанности сохранены.\n\n"
            "🏆 Введите <b>достижения</b> (необязательно)\n"
            "Например: увеличил продажи на 30%, внедрил новую систему...\n\n"
            "Или напишите <b>пропустить</b> если нет достижений.",
            reply_markup=get_work_action_keyboard().as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_duties: {e}")


@router.message(ResumeState.WORK_ADD_ACHIEVEMENTS)
async def process_work_achievements(message: Message, state: FSMContext):
    """Обработка достижений"""
    logger.info(f"Получены достижения: {message.text}")
    try:
        text = message.text.strip().lower()
        
        if text == "пропустить":
            achievements = ""
        else:
            achievements = message.text.strip()
            if len(achievements) < 3:
                await message.answer("❌ Введите корректное описание достижений или 'пропустить':")
                return

        # Сохраняем опыт работы в список
        data = await state.get_data()
        work_experiences = data.get("work_experiences", [])
        
        new_experience = {
            "position": data.get("work_position", ""),
            "company": data.get("work_company", ""),
            "start_date": data.get("work_start_date", ""),
            "end_date": data.get("work_end_date", ""),
            "duties": data.get("work_duties", ""),
            "achievements": achievements
        }
        work_experiences.append(new_experience)
        
        # Очищаем временные данные
        await state.update_data(work_experiences=work_experiences)
        await state.update_data(
            work_position=None, work_company=None,
            work_start_date=None, work_end_date=None,
            work_duties=None, work_achievements=None
        )
        
        await state.set_state(ResumeState.WORK_MENU)
        keyboard = get_work_menu_keyboard()
        await message.answer(
            f"✅ Опыт работы добавлен!\n\n"
            f"<b>{new_experience['position']}</b> в {new_experience['company']}\n"
            f"Период: {new_experience['start_date']} — {new_experience['end_date']}\n\n"
            "Добавить ещё одно место работы или продолжить?",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        logger.error(f"Ошибка в process_work_achievements: {e}")
