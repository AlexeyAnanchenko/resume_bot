"""
Тесты для образования и навыков
"""
import pytest
from database import ResumeDatabase


class TestEducationDatabase:
    """Тесты для хранения образования"""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Тестовая БД"""
        db_path = str(tmp_path / "test.db")
        return ResumeDatabase(db_path)

    def test_save_education(self, test_db):
        """Сохранение образования"""
        education = {
            "level": "Высшее",
            "institution": "МГУ им. Ломоносова",
            "faculty": "Факультет вычислительной математики и кибернетики",
            "specialty": "Прикладная математика",
            "year": "2020"
        }
        test_db.save_education(123, education)
        
        result = test_db.get_education(123)
        assert result is not None
        assert result["institution"] == "МГУ им. Ломоносова"

    def test_update_education(self, test_db):
        """Обновление образования"""
        test_db.save_education(123, {
            "level": "Бакалавр",
            "institution": "Старый ВУЗ",
            "faculty": "", "specialty": "", "year": ""
        })
        
        test_db.save_education(123, {
            "level": "Магистр",
            "institution": "Новый ВУЗ",
            "faculty": "ФВМК",
            "specialty": "Прикладная математика",
            "year": "2022"
        })
        
        result = test_db.get_education(123)
        assert result["level"] == "Магистр"
        assert result["institution"] == "Новый ВУЗ"


class TestSkillsDatabase:
    """Тесты для хранения навыков"""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Тестовая БД"""
        db_path = str(tmp_path / "test.db")
        return ResumeDatabase(db_path)

    def test_save_skills(self, test_db):
        """Сохранение навыков"""
        skills = ["Python", "JavaScript", "SQL", "Git"]
        test_db.save_skills(123, skills)
        
        result = test_db.get_skills(123)
        assert result == skills

    def test_update_skills(self, test_db):
        """Обновление навыков"""
        test_db.save_skills(123, ["Python", "Java"])
        test_db.save_skills(123, ["Python", "JavaScript", "SQL"])
        
        result = test_db.get_skills(123)
        assert "Java" not in result
        assert "JavaScript" in result
        assert "SQL" in result

    def test_parse_skills_from_text(self, test_db):
        """Парсинг навыков из текста"""
        # Тест через запятую
        skills = test_db.parse_skills("Python, JavaScript, SQL")
        assert len(skills) == 3
        
        # Тест через точку с запятой
        skills = test_db.parse_skills("Python; JavaScript; SQL")
        assert len(skills) == 3
        
        # Тест через новую строку
        skills = test_db.parse_skills("Python\nJavaScript\nSQL")
        assert len(skills) == 3
