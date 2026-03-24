"""
services/ai_service.py — улучшение текста через DeepSeek AI

Единственный публичный метод: refine_resume(resume_data) → AIRefinedData
Все промпты в методе _get_prompt(context).

Если DEEPSEEK_API_KEY не задан — возвращает оригинальные данные без изменений.
"""
import asyncio
import logging
from copy import deepcopy
from typing import List

from openai import AsyncOpenAI

from config import AI_ENABLED, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from models import AIRefinedData, ResumeData, WorkExperience

logger = logging.getLogger(__name__)


class AIService:
    """Сервис для улучшения текста резюме через DeepSeek API"""

    SYSTEM_PROMPT = (
        "Ты помощник по написанию профессиональных резюме на русском языке. "
        "Отвечай только улучшенным текстом, без пояснений и вводных фраз."
    )

    # ── Промпты для каждого контекста ─────────────────────────────────────────
    # Чтобы изменить промпт — найди нужный ключ и измени текст
    PROMPTS = {
        "position": (
            "Переформулируй название должности профессионально и коротко. "
            "Верни только название должности, без лишних слов.\n\nДолжность: {text}"
        ),
        "duties": (
            "Переформулируй обязанности в виде маркированного списка (• пункт). "
            "Используй глаголы действия. Каждый пункт с новой строки.\n\nОбязанности: {text}"
        ),
        "achievements": (
            "Переформулируй достижения профессионально, добавь конкретику и цифры где возможно. "
            "Используй маркированный список.\n\nДостижения: {text}"
        ),
        "skills": (
            "Перечисли навыки через запятую в профессиональном виде. "
            "Только навыки, никаких заголовков и форматирования.\n\nНавыки: {text}"
        ),
    }

    def __init__(self):
        self._client: AsyncOpenAI | None = None
        if AI_ENABLED:
            self._client = AsyncOpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url=DEEPSEEK_BASE_URL,
            )

    async def refine_resume(self, resume: ResumeData) -> AIRefinedData:
        """
        Улучшить все текстовые поля резюме через AI.
        Если AI недоступен — вернуть данные как есть.
        """
        if not AI_ENABLED or self._client is None:
            logger.info("AI отключён (нет DEEPSEEK_API_KEY), используем оригинальный текст")
            return self._to_refined(resume)

        logger.info(f"Начало AI-улучшения для user_id={resume.user_id}")

        try:
            refined = AIRefinedData()

            # Должность
            if resume.position:
                refined.position = await self._call(resume.position, "position")
            else:
                refined.position = resume.position

            # Опыт работы — параллельно
            refined.work_experiences = await self._refine_work_experiences(resume.work_experiences)

            # Навыки
            if resume.skills:
                skills_text = ", ".join(resume.skills)
                raw = await self._call(skills_text, "skills")
                refined.skills = [s.strip() for s in raw.split(",") if s.strip()]
            else:
                refined.skills = resume.skills

            logger.info(f"AI-улучшение завершено для user_id={resume.user_id}")
            return refined

        except Exception as e:
            logger.error(f"Ошибка AI: {e}, используем оригинальный текст")
            return self._to_refined(resume)

    async def _refine_work_experiences(self, experiences: list) -> List[WorkExperience]:
        """Параллельно улучшить все записи опыта работы"""
        if not experiences:
            return []

        async def refine_one(exp: WorkExperience) -> WorkExperience:
            result = deepcopy(exp)
            tasks = {
                "position": self._call(exp.position, "position") if exp.position else asyncio.sleep(0),
                "duties": self._call(exp.duties, "duties") if exp.duties else asyncio.sleep(0),
                "achievements": self._call(exp.achievements, "achievements") if exp.achievements else asyncio.sleep(0),
            }
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            keys = list(tasks.keys())
            for i, key in enumerate(keys):
                if not isinstance(results[i], Exception) and isinstance(results[i], str):
                    setattr(result, key, results[i])
            return result

        return list(await asyncio.gather(*[refine_one(exp) for exp in experiences]))

    async def _call(self, text: str, context: str) -> str:
        """Один запрос к DeepSeek API"""
        prompt = self.PROMPTS.get(context, "Улучши текст профессионально:\n\n{text}").format(text=text)
        response = await self._client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _to_refined(resume: ResumeData) -> AIRefinedData:
        """Конвертировать ResumeData в AIRefinedData без изменений"""
        return AIRefinedData(
            position=resume.position,
            work_experiences=resume.work_experiences,
            skills=resume.skills,
        )


# Глобальный экземпляр
ai_service = AIService()
