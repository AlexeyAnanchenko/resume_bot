"""
tests/conftest.py — общие pytest-фикстуры

Все тесты используют временную in-memory БД, не трогая production.
"""
import pytest

from database import ResumeDB
from models import Education, ResumeData, WorkExperience


@pytest.fixture
def db(tmp_path):
    """Временная тестовая БД"""
    return ResumeDB(str(tmp_path / "test.db"))


@pytest.fixture
def sample_resume() -> ResumeData:
    """Полные тестовые данные резюме"""
    return ResumeData(
        user_id=42,
        full_name="Иванов Иван Иванович",
        email="ivan@test.ru",
        phone="+7 (999) 123-45-67",
        city="Москва",
        position="Python-разработчик",
        work_experiences=[
            WorkExperience(
                position="Senior Python Developer",
                company="Яндекс",
                start_date="01.2020",
                end_date="по настоящее время",
                duties="Разработка бэкенда на Python/Django",
                achievements="Ускорил CI/CD пайплайн на 40%",
            )
        ],
        education=Education(
            level="Высшее",
            institution="МГУ им. Ломоносова",
            faculty="ВМК",
            specialty="Прикладная математика",
            year="2019",
        ),
        skills=["Python", "Django", "PostgreSQL", "Docker", "Git"],
    )
