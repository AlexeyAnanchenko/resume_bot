"""
AI-обработчики — упрощённая версия
AI применяется автоматически при генерации PDF
"""
import logging
from aiogram import Router
from services.ai_processor import ai_processor
from database import db

logger = logging.getLogger(__name__)

router = Router()


async def refine_resume_data(user_id: int, state_data: dict) -> dict:
    """
    Переформулирование всех данных резюме перед генерацией PDF
    
    Args:
        user_id: ID пользователя
        state_data: Данные из state (опыт работы, навыки)
    
    Returns:
        Словарь с переформулированными данными
    """
    logger.info(f"Начало AI-переформулирования для пользователя {user_id}")
    
    # Получаем базовые данные из БД
    user_data = db.get_resume(user_id)
    if not user_data:
        return {}
    
    refined = {
        "user_data": user_data,
        "work_experiences": [],
        "education": db.get_education(user_id),
        "skills": db.get_skills(user_id),
        "photo": db.get_photo(user_id)
    }
    
    # Переформулируем должность
    if user_data.get("position"):
        refined["position_refined"] = await ai_processor.refine_text(
            user_data["position"],
            context="position"
        )
    
    # Переформулируем опыт работы
    work_experiences = state_data.get("work_experiences", [])
    for exp in work_experiences:
        refined_exp = {}
        
        if exp.get("position"):
            refined_exp["position"] = await ai_processor.refine_text(
                exp["position"],
                context="position"
            )
        
        if exp.get("duties"):
            refined_exp["duties"] = await ai_processor.refine_text(
                exp["duties"],
                context="duties"
            )
        
        if exp.get("achievements"):
            refined_exp["achievements"] = await ai_processor.refine_text(
                exp["achievements"],
                context="achievements"
            )
        
        # Если AI не доступен, используем оригинал
        refined["work_experiences"].append({
            "position": refined_exp.get("position", exp.get("position", "")),
            "company": exp.get("company", ""),
            "start_date": exp.get("start_date", ""),
            "end_date": exp.get("end_date", ""),
            "duties": refined_exp.get("duties", exp.get("duties", "")),
            "achievements": refined_exp.get("achievements", exp.get("achievements", ""))
        })
    
    # Переформулируем навыки
    if refined["skills"]:
        skills_text = ", ".join(refined["skills"])
        refined["skills_refined"] = await ai_processor.refine_text(
            skills_text,
            context="skills"
        )
    
    logger.info(f"AI-переформулирование завершено для пользователя {user_id}")
    return refined
