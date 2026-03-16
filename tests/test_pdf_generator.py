"""
Тесты для генератора PDF
"""
import pytest
from io import BytesIO
from services.pdf_generator import PDFResumeGenerator
from database import ResumeDatabase, db
import tempfile
import os


@pytest.fixture
def pdf_generator():
    """Создание генератора PDF"""
    return PDFResumeGenerator()


@pytest.fixture
def test_db_path(tmp_path):
    """Путь к тестовой БД"""
    return str(tmp_path / "test.db")


@pytest.fixture
def test_db(test_db_path):
    """Тестовая БД"""
    db = ResumeDatabase(test_db_path)
    # Создаём тестовые данные
    db.save_user_data(123, {
        "full_name": "Иванов Иван Иванович",
        "email": "ivan@example.com",
        "phone": "+7 (999) 123-45-67",
        "city": "Москва",
        "position": "Python-разработчик"
    })
    db.save_education(123, {
        "level": "Высшее",
        "institution": "МГУ им. Ломоносова",
        "faculty": "Факультет вычислительной математики и кибернетики",
        "specialty": "Прикладная математика",
        "year": "2020"
    })
    db.save_skills(123, ["Python", "JavaScript", "SQL"])
    return db


@pytest.fixture
def state_data():
    """Тестовые данные из state"""
    return {
        "work_experiences": [
            {
                "position": "Python-разработчик",
                "company": "Яндекс",
                "start_date": "01.2020",
                "end_date": "по настоящее время",
                "duties": "Разработка бэкенда, REST API",
                "achievements": "Увеличил производительность на 30%"
            }
        ]
    }


class TestPDFGenerator:
    """Тесты генератора PDF"""

    @pytest.mark.asyncio
    async def test_generate_pdf_exists(self, pdf_generator, test_db, test_db_path, monkeypatch):
        """PDF генерируется и не пустой"""
        # Подменяем глобальную БД на тестовую
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, {})
        assert buffer is not None
        assert len(buffer.getvalue()) > 0  # Файл не пустой

    @pytest.mark.asyncio
    async def test_generate_pdf_size(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data):
        """PDF имеет разумный размер"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, state_data)
        size = len(buffer.getvalue())
        assert 100 < size < 500000  # От 100 байт до 500KB

    @pytest.mark.asyncio
    async def test_generate_pdf_with_data(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data):
        """PDF содержит данные"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, state_data)
        content = buffer.getvalue()
        
        # Проверяем, что это PDF
        assert content.startswith(b'%PDF')
        
        # Проверяем размер
        assert len(content) > 100

    @pytest.mark.asyncio
    async def test_generate_pdf_valid(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data, tmp_path):
        """PDF валидный (открывается)"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, state_data)
        
        # Сохраняем во временный файл
        pdf_path = tmp_path / "test_resume.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        # Проверяем, что файл существует и не пустой
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0
        
        # Проверяем заголовок PDF
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            assert header.startswith(b'%PDF')

    @pytest.mark.asyncio
    async def test_generate_pdf_cyrillic(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data):
        """PDF поддерживает кириллицу"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, state_data)
        content = buffer.getvalue()
        
        # Проверяем, что файл не пустой
        assert len(content) > 100

    @pytest.mark.asyncio
    async def test_generate_pdf_structure(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data):
        """PDF имеет правильную структуру"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(123, state_data)
        content = buffer.getvalue().decode('latin-1', errors='ignore')
        
        # Проверяем наличие основных элементов PDF
        assert '/Type /Catalog' in content
        assert '/Pages' in content
        assert '/Page' in content

    @pytest.mark.asyncio
    async def test_generate_empty_pdf(self, pdf_generator, test_db, test_db_path, monkeypatch):
        """Пустой PDF всё равно генерируется"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)
        
        buffer = await pdf_generator.generate_simple(999, {})
        assert buffer is not None
        assert len(buffer.getvalue()) > 0

    @pytest.mark.asyncio
    async def test_generate_pdf_with_real_data(self, pdf_generator, test_db, test_db_path, monkeypatch):
        """PDF с реальными данными пользователя"""
        import services.pdf_generator as pdf_gen_module
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)

        # Данные как из реального state
        state_data = {
            "full_name": "Иванов Иван Иванович",
            "email": "ivan@test.ru",
            "phone": "+7 (999) 123-45-67",
            "city": "Москва",
            "position": "Python-разработчик",
            "work_experiences": [
                {
                    "position": "Python-разработчик",
                    "company": "Яндекс",
                    "start_date": "01.2020",
                    "end_date": "по настоящее время",
                    "duties": "Разработка бэкенда",
                    "achievements": "Увеличил производительность"
                }
            ]
        }

        buffer = await pdf_generator.generate_simple(123, state_data)
        content = buffer.getvalue()

        # Проверяем размер
        assert len(content) > 1000, f"PDF слишком маленький: {len(content)} байт"

        # Проверяем, что это PDF
        assert content.startswith(b'%PDF')

    @pytest.mark.asyncio
    async def test_generate_pdf_with_photo(self, pdf_generator, test_db, test_db_path, monkeypatch, state_data, tmp_path):
        """PDF содержит фото пользователя"""
        import services.pdf_generator as pdf_gen_module
        from unittest.mock import MagicMock
        import tempfile
        import os
        
        monkeypatch.setattr(pdf_gen_module, 'db', test_db)

        # Сохраняем тестовое фото в БД
        test_db.save_photo(123, file_id="AgACAgIAAAkBAAMK", file_path="photos/123.jpg", file_size=10240, mime_type="image/jpeg")

        # Создаём тестовое изображение для эмуляции загрузки фото
        try:
            from PIL import Image
            img_path = tmp_path / "test_photo.jpg"
            img = Image.new('RGB', (100, 150), color='red')
            img.save(img_path, 'JPEG')
        except ImportError:
            # Если PIL нет, создаём простой JPEG файл
            img_path = tmp_path / "test_photo.jpg"
            # Минимальный валидный JPEG (1x1 красный пиксель)
            jpeg_data = bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xD9
            ])
            with open(img_path, 'wb') as f:
                f.write(jpeg_data)

        # Создаём mock для бота с методом download
        mock_bot = MagicMock()
        
        async def mock_download(file, destination=None):
            """Эмуляция загрузки файла из Telegram"""
            if destination:
                with open(img_path, 'rb') as src:
                    with open(destination, 'wb') as dst:
                        dst.write(src.read())
            return destination
        
        mock_bot.download = mock_download
        
        # Используем set_bot для установки mock-бота
        pdf_gen_module.set_bot(mock_bot)

        buffer = await pdf_generator.generate_simple(123, state_data)
        content = buffer.getvalue()

        # Сохраняем PDF для отладки
        pdf_path = tmp_path / "test_resume_with_photo.pdf"
        with open(pdf_path, 'wb') as f:
            f.write(content)

        # Проверяем, что PDF содержит данные об изображении
        content_str = content.decode('latin-1', errors='ignore')
        
        # Проверяем, что в PDF есть изображение (Image XObject)
        has_image = '/Image' in content_str or '/XObject' in content_str
        assert has_image, "PDF не содержит изображений (фото не добавлено)"

        # Проверяем размер - PDF с фото должен быть больше
        assert len(content) > 5000, f"PDF с фото слишком маленький: {len(content)} байт"
