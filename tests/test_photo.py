"""
Тесты для загрузки и обработки фото
"""
import pytest
import os
from database import ResumeDatabase


class TestPhotoDatabase:
    """Тесты для хранения фото"""

    @pytest.fixture
    def test_db(self, tmp_path):
        """Тестовая БД"""
        db_path = str(tmp_path / "test.db")
        return ResumeDatabase(db_path)

    def test_save_photo_path(self, test_db):
        """Сохранение пути к фото"""
        photo_path = "/path/to/photo.jpg"
        test_db.save_photo(123, photo_path)
        
        result = test_db.get_photo(123)
        assert result is not None
        assert result["file_id"] == photo_path

    def test_update_photo(self, test_db):
        """Обновление фото"""
        test_db.save_photo(123, "/old/path.jpg")
        test_db.save_photo(123, "/new/path.jpg")
        
        result = test_db.get_photo(123)
        assert result is not None
        assert result["file_id"] == "/new/path.jpg"

    def test_delete_photo(self, test_db):
        """Удаление фото"""
        test_db.save_photo(123, "/path/to/photo.jpg")
        test_db.delete_photo(123)
        
        result = test_db.get_photo(123)
        assert result is None

    def test_get_nonexistent_photo(self, test_db):
        """Получение несуществующего фото"""
        result = test_db.get_photo(999)
        assert result is None


class TestPhotoValidation:
    """Тесты для валидации фото"""

    @pytest.mark.asyncio
    async def test_validate_photo_size_valid(self):
        """Валидный размер фото (до 10MB)"""
        from handlers.photo import validate_photo_size
        
        # 5MB - валидно
        assert await validate_photo_size(5 * 1024 * 1024) is True
        # 10MB - граница
        assert await validate_photo_size(10 * 1024 * 1024) is True

    @pytest.mark.asyncio
    async def test_validate_photo_size_invalid(self):
        """Невалидный размер фото (более 10MB)"""
        from handlers.photo import validate_photo_size
        
        # 15MB - невалидно
        assert await validate_photo_size(15 * 1024 * 1024) is False

    @pytest.mark.asyncio
    async def test_validate_photo_format_valid(self):
        """Валидные форматы фото"""
        from handlers.photo import is_valid_photo_format
        
        assert await is_valid_photo_format("image/jpeg") is True
        assert await is_valid_photo_format("image/png") is True
        assert await is_valid_photo_format("image/webp") is True

    @pytest.mark.asyncio
    async def test_validate_photo_format_invalid(self):
        """Невалидные форматы фото"""
        from handlers.photo import is_valid_photo_format
        
        assert await is_valid_photo_format("image/gif") is False
        assert await is_valid_photo_format("video/mp4") is False
        assert await is_valid_photo_format("application/pdf") is False
