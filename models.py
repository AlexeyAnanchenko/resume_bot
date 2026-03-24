"""
models.py — структуры данных проекта

Все dataclasses здесь. Нет логики, только данные.
При добавлении нового поля: сначала сюда, потом в database.py
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class WorkExperience:
    """Одна запись опыта работы"""
    position: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    duties: str = ""
    achievements: str = ""
    id: Optional[int] = None  # ID записи в БД


@dataclass
class Education:
    """Образование пользователя"""
    level: str = ""        # Бакалавр / Магистр / Среднее специальное
    institution: str = ""  # Название ВУЗа
    faculty: str = ""
    specialty: str = ""
    year: str = ""


@dataclass
class ResumeData:
    """Полные данные резюме — всё что нужно для генерации PDF"""
    # Основные данные
    user_id: int = 0
    full_name: str = ""
    email: str = ""
    phone: str = ""
    city: str = ""
    position: str = ""
    summary: str = ""      # Краткое описание "О себе" (опционально)

    # Разделы
    work_experiences: List[WorkExperience] = field(default_factory=list)
    education: Optional[Education] = None
    skills: List[str] = field(default_factory=list)
    photo_file_id: Optional[str] = None  # Telegram file_id фото


@dataclass
class AIRefinedData:
    """Результат AI-переформулирования для генерации PDF"""
    position: str = ""
    work_experiences: List[WorkExperience] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    summary: str = ""
