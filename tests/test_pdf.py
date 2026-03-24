"""
tests/test_pdf.py — тесты генерации PDF

Проверяем что PDF генерируется, не пустой и содержит корректную структуру.
"""
import pytest

from models import ResumeData
from services.pdf_service import PDFService


@pytest.fixture
def pdf_svc():
    return PDFService()


@pytest.mark.asyncio
async def test_generate_pdf_returns_bytes(pdf_svc, sample_resume):
    buf = await pdf_svc.generate_pdf(sample_resume, bot=None)
    assert buf is not None
    assert len(buf.getvalue()) > 1000


@pytest.mark.asyncio
async def test_generate_pdf_is_valid_pdf(pdf_svc, sample_resume):
    buf = await pdf_svc.generate_pdf(sample_resume, bot=None)
    assert buf.getvalue().startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_pdf_empty_resume(pdf_svc):
    """Пустое резюме не должно падать"""
    empty = ResumeData(user_id=1)
    buf = await pdf_svc.generate_pdf(empty, bot=None)
    assert len(buf.getvalue()) > 0


@pytest.mark.asyncio
async def test_generate_pdf_no_work_experience(pdf_svc):
    """Резюме без опыта работы"""
    resume = ResumeData(user_id=1, full_name="Тест", position="Разработчик")
    buf = await pdf_svc.generate_pdf(resume, bot=None)
    assert buf.getvalue().startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_pdf_no_skills(pdf_svc, sample_resume):
    """Резюме без навыков"""
    sample_resume.skills = []
    buf = await pdf_svc.generate_pdf(sample_resume, bot=None)
    assert buf.getvalue().startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_pdf_size_reasonable(pdf_svc, sample_resume):
    """PDF не должен быть слишком маленьким или огромным"""
    buf = await pdf_svc.generate_pdf(sample_resume, bot=None)
    size = len(buf.getvalue())
    assert 1_000 < size < 10_000_000  # от 1KB до 10MB
