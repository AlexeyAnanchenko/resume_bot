"""
tests/test_ai_service.py — тесты AI-сервиса

Тестируем поведение при отключённом AI (без ключа) и parse_skills_text.
"""
import pytest

from models import ResumeData, WorkExperience
from services.ai_service import AIService


@pytest.fixture
def ai_svc_disabled(monkeypatch):
    """AI-сервис с отключённым ключом"""
    import services.ai_service as module
    monkeypatch.setattr(module, "AI_ENABLED", False)
    svc = AIService()
    svc._client = None
    return svc


@pytest.mark.asyncio
async def test_refine_returns_original_when_disabled(ai_svc_disabled, sample_resume):
    """Без AI возвращаем оригинальные данные"""
    refined = await ai_svc_disabled.refine_resume(sample_resume)
    assert refined.position == sample_resume.position
    assert refined.skills == sample_resume.skills


@pytest.mark.asyncio
async def test_refine_empty_resume_no_crash(ai_svc_disabled):
    """Пустое резюме не должно падать"""
    resume = ResumeData(user_id=1)
    refined = await ai_svc_disabled.refine_resume(resume)
    assert refined is not None


@pytest.mark.asyncio
async def test_refine_preserves_work_experiences(ai_svc_disabled, sample_resume):
    """Опыт работы сохраняется при отключённом AI"""
    refined = await ai_svc_disabled.refine_resume(sample_resume)
    assert len(refined.work_experiences) == len(sample_resume.work_experiences)
    assert refined.work_experiences[0].company == sample_resume.work_experiences[0].company


def test_to_refined_converts_correctly():
    """_to_refined корректно конвертирует ResumeData → AIRefinedData"""
    resume = ResumeData(
        user_id=1,
        position="Developer",
        skills=["Python", "Git"],
        work_experiences=[WorkExperience(company="Яндекс")],
    )
    refined = AIService._to_refined(resume)
    assert refined.position == "Developer"
    assert refined.skills == ["Python", "Git"]
    assert len(refined.work_experiences) == 1
