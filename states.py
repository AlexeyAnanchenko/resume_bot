from aiogram.fsm.state import State, StatesGroup


class ResumeState(StatesGroup):
    """Состояния диалога создания резюме"""
    # Базовые данные
    FULL_NAME = State()
    EMAIL = State()
    PHONE = State()
    CITY = State()
    POSITION = State()

    # Опыт работы
    WORK_MENU = State()  # Меню выбора действия
    WORK_ADD_POSITION = State()  # Ввод должности
    WORK_ADD_COMPANY = State()  # Ввод компании
    WORK_ADD_START_DATE = State()  # Дата начала
    WORK_ADD_END_DATE = State()  # Дата окончания (или "по настоящее время")
    WORK_ADD_DUTIES = State()  # Обязанности
    WORK_ADD_ACHIEVEMENTS = State()  # Достижения

    # Образование
    EDUCATION_MENU = State()
    EDUCATION_LEVEL = State()  # Уровень образования
    EDUCATION_INSTITUTION = State()  # Учебное заведение
    EDUCATION_FACULTY = State()  # Факультет
    EDUCATION_SPECIALTY = State()  # Специальность
    EDUCATION_YEAR = State()  # Год окончания

    # Навыки
    SKILLS_MENU = State()
    SKILLS_ADD = State()  # Добавление навыков

    # Фото
    PHOTO_MENU = State()
    PHOTO_ADD = State()  # Загрузка фото
    
    # Завершение
    IDLE = State()  # Без активного диалога
