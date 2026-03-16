"""
Тесты для базы данных резюме
"""
import pytest
import sqlite3
import os
from database import ResumeDatabase


@pytest.fixture
def test_db(tmp_path):
    """Создание тестовой БД"""
    db_path = str(tmp_path / "test_resumes.db")
    db = ResumeDatabase(db_path)
    yield db
    # Очистка после теста — закрываем соединение явно
    import gc
    gc.collect()
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        pass  # Windows может блокировать файл


class TestResumeDatabase:
    """Тесты для ResumeDatabase"""

    def test_create_table(self, test_db):
        """Проверка создания таблицы"""
        with sqlite3.connect(test_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='resumes'"
            )
            assert cursor.fetchone() is not None

    def test_save_user_data(self, test_db):
        """Сохранение данных пользователя"""
        data = {
            "full_name": "Иванов Иван",
            "email": "test@example.com",
            "phone": "+7 (999) 123-45-67",
            "city": "Москва",
            "position": "Разработчик"
        }
        test_db.save_user_data(123, data)

        result = test_db.get_resume(123)
        assert result is not None
        assert result["full_name"] == "Иванов Иван"
        assert result["email"] == "test@example.com"

    def test_update_user_data(self, test_db):
        """Обновление данных пользователя"""
        # Первое сохранение
        test_db.save_user_data(123, {"full_name": "Иванов Иван", "email": "old@test.com",
                                      "phone": "", "city": "", "position": ""})
        # Обновление
        test_db.save_user_data(123, {"full_name": "Иванов Иван Иванович", "email": "new@test.com",
                                      "phone": "", "city": "", "position": "Senior"})

        result = test_db.get_resume(123)
        assert result["full_name"] == "Иванов Иван Иванович"
        assert result["email"] == "new@test.com"
        assert result["position"] == "Senior"

    def test_get_nonexistent_resume(self, test_db):
        """Получение несуществующего резюме"""
        result = test_db.get_resume(999)
        assert result is None

    def test_delete_resume(self, test_db):
        """Удаление резюме"""
        test_db.save_user_data(123, {"full_name": "Тест", "email": "test@test.com",
                                      "phone": "", "city": "", "position": ""})
        test_db.delete_resume(123)

        result = test_db.get_resume(123)
        assert result is None
