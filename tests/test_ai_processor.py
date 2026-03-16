"""
Тесты для AI-процессора
"""
import pytest
from unittest.mock import AsyncMock, patch
from services.ai_processor import AIProcessor, SYSTEM_PROMPT


class TestAIProcessorInit:
    """Тесты инициализации AI-процессора"""

    def test_init_with_api_key(self):
        """Инициализация с API-ключом"""
        processor = AIProcessor(api_key="test-key")
        assert processor.client is not None
        assert processor.api_key == "test-key"

    def test_init_without_api_key(self):
        """Инициализация без API-ключа (режим заглушки)"""
        processor = AIProcessor(api_key="")
        assert processor.client is None

    def test_init_with_default_key(self):
        """Инициализация с ключом по умолчанию"""
        # Используем ключ из конфига
        from config import DEEPSEEK_API_KEY
        processor = AIProcessor()
        if DEEPSEEK_API_KEY:
            assert processor.client is not None
        else:
            assert processor.client is None


class TestAIProcessorRefine:
    """Тесты переформулирования текста"""

    @pytest.mark.asyncio
    async def test_refine_text_without_api(self):
        """Переформулирование без API (режим заглушки)"""
        processor = AIProcessor(api_key="")
        text = "Делал сайт на питоне"
        result = await processor.refine_text(text)
        # В режиме заглушки возвращается исходный текст
        assert result == text

    @pytest.mark.asyncio
    async def test_refine_text_with_mock(self):
        """Переформулирование с mock API"""
        processor = AIProcessor(api_key="test-key")

        # Мок для ответа API
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Разработка веб-приложений на Python"

        with patch.object(processor.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            result = await processor.refine_text("Делал сайт на питоне")

        assert result == "Разработка веб-приложений на Python"
        mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_refine_text_with_context(self):
        """Переформулирование с контекстом"""
        processor = AIProcessor(api_key="test-key")

        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Senior Python Developer"

        with patch.object(processor.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response
            result = await processor.refine_text("Питон разработчик", context="position")

        assert result == "Senior Python Developer"

    @pytest.mark.asyncio
    async def test_refine_text_error_handling(self):
        """Обработка ошибок API"""
        processor = AIProcessor(api_key="test-key")
        original_text = "Тестовый текст"

        # Мок, который выбрасывает исключение
        with patch.object(processor.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API Error")
            result = await processor.refine_text(original_text)

        # При ошибке возвращается исходный текст
        assert result == original_text


class TestAIBuildPrompt:
    """Тесты построения промптов"""

    def test_build_user_prompt_default(self):
        """Промпт по умолчанию"""
        processor = AIProcessor(api_key="")
        prompt = processor._build_user_prompt("текст", "")
        assert "текст" in prompt
        assert "профессиональном деловом стиле" in prompt

    def test_build_user_prompt_position(self):
        """Промпт для должности"""
        processor = AIProcessor(api_key="")
        prompt = processor._build_user_prompt("разработчик", "position")
        assert "должности" in prompt
        assert "разработчик" in prompt

    def test_build_user_prompt_duties(self):
        """Промпт для обязанностей"""
        processor = AIProcessor(api_key="")
        prompt = processor._build_user_prompt("обязанности", "duties")
        assert "обязанности" in prompt
        assert "глаголы действия" in prompt

    def test_build_user_prompt_achievements(self):
        """Промпт для достижений"""
        processor = AIProcessor(api_key="")
        prompt = processor._build_user_prompt("достижения", "achievements")
        assert "достижения" in prompt
        assert "метрики" in prompt

    def test_build_user_prompt_skills(self):
        """Промпт для навыков"""
        processor = AIProcessor(api_key="")
        prompt = processor._build_user_prompt("навыки", "skills")
        assert "навыки" in prompt
        assert "категориям" in prompt


class TestSystemPrompt:
    """Тесты системного промпта"""

    def test_system_prompt_exists(self):
        """Системный промпт существует"""
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT) > 100

    def test_system_prompt_contains_requirements(self):
        """Системный промпт содержит требования"""
        assert "глаголов действия" in SYSTEM_PROMPT or "глаголы действия" in SYSTEM_PROMPT
        assert "профессиональную терминологию" in SYSTEM_PROMPT or "профессиональной терминологии" in SYSTEM_PROMPT
        assert "лаконичным" in SYSTEM_PROMPT
