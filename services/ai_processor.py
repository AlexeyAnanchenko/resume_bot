"""
AI-процессор для переформулирования текста в профессиональный стиль
Использует DeepSeek API (совместим с OpenAI SDK)
"""
import logging
from typing import Optional
from openai import AsyncOpenAI
from config import DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)

# DeepSeek API совместим с OpenAI SDK
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Системный промпт для профессионального переформулирования
SYSTEM_PROMPT = """Ты — профессиональный карьерный консультант и эксперт по составлению резюме.
Твоя задача — переформулировать предоставленный текст в профессиональном деловом стиле,
используя общепринятые формулировки для резюме.

Требования к результату:
1. Используй активные глаголы действия (разработал, внедрил, увеличил, оптимизировал)
2. Избегай местоимения "я" — пиши в безличной форме или от третьего лица
3. Добавляй конкретные метрики и результаты где возможно
4. Используй профессиональную терминологию
5. Делай текст лаконичным и информативным
6. Сохраняй исходный смысл, но улучшай формулировки

Примеры преобразований:
- "Делал сайт на питоне" → "Разработка веб-приложений на Python"
- "Руководил командой из 5 человек" → "Управление командой разработчиков (5 человек)"
- "Увеличил продажи" → "Увеличение объёма продаж на 30% за счёт внедрения новой CRM-системы"
"""


class AIProcessor:
    """Процессор для AI-переформулирования текста"""

    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        """
        Инициализация AI-процессора

        Args:
            api_key: API-ключ для DeepSeek
        """
        self.api_key = api_key
        self.client: Optional[AsyncOpenAI] = None

        if api_key:
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=DEEPSEEK_BASE_URL
            )
            logger.info("AI-процессор инициализирован с DeepSeek API")
        else:
            logger.warning("AI-процессор инициализирован без API-ключа (режим заглушки)")

    async def refine_text(self, text: str, context: str = "") -> str:
        """
        Переформулирование текста в профессиональный стиль

        Args:
            text: Исходный текст для переформулирования
            context: Контекст (например, "должность", "обязанности", "достижения")

        Returns:
            Переформулированный текст
        """
        if not self.client:
            # Режим заглушки — возвращаем исходный текст
            logger.warning(f"AI недоступен, возвращаем исходный текст: {text[:50]}...")
            return text

        try:
            # Формируем промпт с учётом контекста
            user_prompt = self._build_user_prompt(text, context)

            # Запрашиваем переформулирование
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            refined_text = response.choices[0].message.content.strip()
            logger.info(f"Текст переформулирован: {text[:30]}... → {refined_text[:30]}...")
            return refined_text

        except Exception as e:
            logger.error(f"Ошибка AI-переформулирования: {e}")
            # Возвращаем исходный текст при ошибке
            return text

    def _build_user_prompt(self, text: str, context: str) -> str:
        """
        Построение пользовательского промпта

        Args:
            text: Исходный текст
            context: Контекст

        Returns:
            Промпт для AI
        """
        context_instruction = ""

        if context == "position":
            context_instruction = "Переформулируй название должности в профессиональном стиле."
        elif context == "duties":
            context_instruction = "Переформулируй обязанности в виде маркированного списка, используя глаголы действия."
        elif context == "achievements":
            context_instruction = "Переформулируй достижения, добавив конкретные метрики и результаты."
        elif context == "skills":
            context_instruction = "Перечисли навыки через запятую. Формат: Навык1, Навык2, Навык3. НЕ используй заголовки, категории, подзаголовки, звёздочки, маркеры списка или любое markdown-форматирование. Просто перечисли названия навыков через запятую."
        elif context == "about":
            context_instruction = "Напиши краткий профессиональный раздел 'О себе' на основе этой информации."
        else:
            context_instruction = "Переформулируй текст в профессиональном деловом стиле для резюме."

        return f"""
{context_instruction}

Исходный текст:
{text}

Переформулированный вариант:"""

    async def refine_work_experience(self, position: str, duties: str, achievements: str) -> dict:
        """
        Комплексное переформулирование опыта работы

        Args:
            position: Должность
            duties: Обязанности
            achievements: Достижения

        Returns:
            Словарь с переформулированными данными
        """
        tasks = []

        # Переформулируем каждый компонент
        if position:
            tasks.append(self.refine_text(position, "position"))
        else:
            tasks.append(self._dummy_task(position))

        if duties:
            tasks.append(self.refine_text(duties, "duties"))
        else:
            tasks.append(self._dummy_task(duties))

        if achievements:
            tasks.append(self.refine_text(achievements, "achievements"))
        else:
            tasks.append(self._dummy_task(achievements))

        # Выполняем все запросы параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "position": results[0] if not isinstance(results[0], Exception) else position,
            "duties": results[1] if not isinstance(results[1], Exception) else duties,
            "achievements": results[2] if not isinstance(results[2], Exception) else achievements
        }

    async def _dummy_task(self, value: str):
        """Заглушка для asyncio.gather"""
        return value


# Глобальный экземпляр
ai_processor = AIProcessor()


# Импортируем asyncio для gather
import asyncio