"""
states.py — состояния FSM-диалога

Группы состояний соответствуют разделам резюме.
Каждая группа = один файл в handlers/.
"""
from aiogram.fsm.state import State, StatesGroup


class ResumeStates(StatesGroup):
    # ── Базовые данные (handlers/resume.py) ──────────────────────────
    FULL_NAME = State()
    EMAIL = State()
    PHONE = State()
    CITY = State()
    POSITION = State()

    # ── Опыт работы (handlers/work.py) ───────────────────────────────
    WORK_MENU = State()
    WORK_POSITION = State()
    WORK_COMPANY = State()
    WORK_START_DATE = State()
    WORK_END_DATE = State()
    WORK_DUTIES = State()
    WORK_ACHIEVEMENTS = State()

    # ── Образование (handlers/education.py) ──────────────────────────
    EDUCATION_MENU = State()
    EDUCATION_LEVEL = State()
    EDUCATION_INSTITUTION = State()
    EDUCATION_FACULTY = State()
    EDUCATION_SPECIALTY = State()
    EDUCATION_YEAR = State()

    # ── Навыки (handlers/skills.py) ───────────────────────────────────
    SKILLS_MENU = State()
    SKILLS_INPUT = State()

    # ── Фото (handlers/photo.py) ──────────────────────────────────────
    PHOTO_MENU = State()
    PHOTO_WAITING = State()

    # ── Завершение ────────────────────────────────────────────────────
    DONE = State()  # Данные собраны, ожидаем генерации
