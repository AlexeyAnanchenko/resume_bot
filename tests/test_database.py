"""
tests/test_database.py — тесты базы данных

Тестируем CRUD для всех таблиц.
"""
import pytest

from models import Education, WorkExperience


class TestResumeBasicData:
    def test_save_and_get_resume(self, db):
        db.save_resume(1, {"full_name": "Иван", "email": "ivan@test.ru", "phone": "+79991234567", "city": "Москва", "position": "Python Dev"})
        result = db.get_resume(1)
        assert result["full_name"] == "Иван"
        assert result["email"] == "ivan@test.ru"

    def test_update_resume(self, db):
        db.save_resume(1, {"full_name": "Старое имя"})
        db.save_resume(1, {"full_name": "Новое имя"})
        assert db.get_resume(1)["full_name"] == "Новое имя"

    def test_get_nonexistent_resume(self, db):
        assert db.get_resume(999) is None

    def test_delete_resume(self, db):
        db.save_resume(1, {"full_name": "Иван"})
        db.delete_resume(1)
        assert db.get_resume(1) is None


class TestWorkExperience:
    def test_add_and_get_work(self, db):
        exp = WorkExperience(position="Developer", company="Яндекс", start_date="01.2020", end_date="01.2023")
        db.add_work_experience(1, exp)
        results = db.get_work_experiences(1)
        assert len(results) == 1
        assert results[0].company == "Яндекс"

    def test_multiple_work_experiences(self, db):
        db.add_work_experience(1, WorkExperience(position="Junior", company="Компания А"))
        db.add_work_experience(1, WorkExperience(position="Senior", company="Компания Б"))
        results = db.get_work_experiences(1)
        assert len(results) == 2

    def test_empty_work_experiences(self, db):
        assert db.get_work_experiences(999) == []


class TestEducation:
    def test_save_and_get_education(self, db):
        edu = Education(level="Высшее", institution="МГУ", faculty="ВМК", specialty="Прикладная математика", year="2020")
        db.save_education(1, edu)
        result = db.get_education(1)
        assert result.institution == "МГУ"
        assert result.year == "2020"

    def test_update_education(self, db):
        db.save_education(1, Education(institution="МГУ"))
        db.save_education(1, Education(institution="СПбГУ"))
        assert db.get_education(1).institution == "СПбГУ"

    def test_no_education(self, db):
        assert db.get_education(999) is None


class TestSkills:
    def test_save_and_get_skills(self, db):
        db.save_skills(1, ["Python", "Django", "Git"])
        result = db.get_skills(1)
        assert result == ["Python", "Django", "Git"]

    def test_empty_skills(self, db):
        assert db.get_skills(999) == []

    def test_parse_comma_separated(self, db):
        skills = db.parse_skills_text("Python, Django, Git")
        assert skills == ["Python", "Django", "Git"]

    def test_parse_newline_separated(self, db):
        skills = db.parse_skills_text("Python\nDjango\nGit")
        assert skills == ["Python", "Django", "Git"]

    def test_parse_mixed_separators(self, db):
        skills = db.parse_skills_text("Python; Django\nGit, Docker")
        assert "Python" in skills
        assert "Docker" in skills

    def test_parse_strips_whitespace(self, db):
        skills = db.parse_skills_text("  Python  ,  Django  ")
        assert skills == ["Python", "Django"]


class TestPhotos:
    def test_save_and_get_photo(self, db):
        db.save_photo(1, file_id="AgACB123", file_size=5120)
        assert db.get_photo_file_id(1) == "AgACB123"

    def test_update_photo(self, db):
        db.save_photo(1, file_id="old_id")
        db.save_photo(1, file_id="new_id")
        assert db.get_photo_file_id(1) == "new_id"

    def test_delete_photo(self, db):
        db.save_photo(1, file_id="AgACB123")
        db.delete_photo(1)
        assert db.get_photo_file_id(1) is None

    def test_no_photo(self, db):
        assert db.get_photo_file_id(999) is None


class TestLoadFullResume:
    def test_load_full_resume(self, db, sample_resume):
        # Сохраняем все данные
        db.save_resume(sample_resume.user_id, {
            "full_name": sample_resume.full_name,
            "email": sample_resume.email,
            "phone": sample_resume.phone,
            "city": sample_resume.city,
            "position": sample_resume.position,
        })
        for exp in sample_resume.work_experiences:
            db.add_work_experience(sample_resume.user_id, exp)
        db.save_education(sample_resume.user_id, sample_resume.education)
        db.save_skills(sample_resume.user_id, sample_resume.skills)

        # Загружаем и проверяем
        loaded = db.load_full_resume(sample_resume.user_id)
        assert loaded.full_name == sample_resume.full_name
        assert len(loaded.work_experiences) == 1
        assert loaded.education.institution == sample_resume.education.institution
        assert loaded.skills == sample_resume.skills
