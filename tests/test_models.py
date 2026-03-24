"""
tests/test_models.py — тесты моделей данных

Проверяем дефолтные значения и создание объектов.
"""
from models import AIRefinedData, Education, ResumeData, WorkExperience


def test_resume_data_defaults():
    r = ResumeData()
    assert r.user_id == 0
    assert r.full_name == ""
    assert r.work_experiences == []
    assert r.skills == []
    assert r.education is None
    assert r.photo_file_id is None


def test_work_experience_defaults():
    exp = WorkExperience()
    assert exp.position == ""
    assert exp.company == ""
    assert exp.id is None


def test_education_defaults():
    edu = Education()
    assert edu.level == ""
    assert edu.year == ""


def test_ai_refined_data_defaults():
    refined = AIRefinedData()
    assert refined.position == ""
    assert refined.work_experiences == []
    assert refined.skills == []


def test_resume_data_with_values():
    r = ResumeData(user_id=42, full_name="Иван", position="Developer")
    assert r.user_id == 42
    assert r.full_name == "Иван"


def test_work_experience_with_values():
    exp = WorkExperience(company="Яндекс", position="Senior Dev", start_date="01.2020")
    assert exp.company == "Яндекс"
    assert exp.start_date == "01.2020"
