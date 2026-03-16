import sqlite3
import re
import json
from datetime import datetime
from typing import Optional, Dict, Any, List


class ResumeDatabase:
    """SQLite база данных для хранения резюме"""

    def __init__(self, db_path: str = "resumes.db"):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        """Создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            # Основная таблица резюме
            conn.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    city TEXT,
                    position TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица образования
            conn.execute("""
                CREATE TABLE IF NOT EXISTS education (
                    user_id INTEGER PRIMARY KEY,
                    level TEXT,
                    institution TEXT,
                    faculty TEXT,
                    specialty TEXT,
                    year TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица навыков
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    user_id INTEGER PRIMARY KEY,
                    skills_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица фото
            conn.execute("""
                CREATE TABLE IF NOT EXISTS photos (
                    user_id INTEGER PRIMARY KEY,
                    file_id TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    mime_type TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def save_user_data(self, user_id: int, data: Dict[str, Any]):
        """Сохранение данных пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            # Получаем только нужные поля
            full_name = data.get("full_name", "")
            email = data.get("email", "")
            phone = data.get("phone", "")
            city = data.get("city", "")
            position = data.get("position", "")

            conn.execute("""
                INSERT INTO resumes (user_id, full_name, email, phone, city, position)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = ?,
                    email = ?,
                    phone = ?,
                    city = ?,
                    position = ?,
                    updated_at = ?
            """, (user_id, full_name, email, phone, city, position,
                  full_name, email, phone, city, position, datetime.now().isoformat()))
            conn.commit()

    def get_resume(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение резюме пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM resumes WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def delete_resume(self, user_id: int):
        """Удаление резюме пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
            conn.commit()

    def save_education(self, user_id: int, education: Dict[str, str]):
        """Сохранение образования"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO education (user_id, level, institution, faculty, specialty, year)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    level = ?,
                    institution = ?,
                    faculty = ?,
                    specialty = ?,
                    year = ?,
                    updated_at = ?
            """, (user_id, education.get("level", ""), education.get("institution", ""),
                  education.get("faculty", ""), education.get("specialty", ""),
                  education.get("year", ""), education.get("level", ""),
                  education.get("institution", ""), education.get("faculty", ""),
                  education.get("specialty", ""), education.get("year", ""),
                  datetime.now().isoformat()))
            conn.commit()

    def get_education(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение образования"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM education WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def save_skills(self, user_id: int, skills: List[str]):
        """Сохранение навыков"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO skills (user_id, skills_json)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    skills_json = ?,
                    updated_at = ?
            """, (user_id, json.dumps(skills, ensure_ascii=False),
                  json.dumps(skills, ensure_ascii=False), datetime.now().isoformat()))
            conn.commit()

    def get_skills(self, user_id: int) -> Optional[List[str]]:
        """Получение навыков"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT skills_json FROM skills WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def parse_skills(self, text: str) -> List[str]:
        """Парсинг навыков из текста (через запятую, точку с запятой или новую строку)"""
        # Разделяем по разным разделителям
        separators = [',', ';', '\n']
        result = text

        for sep in separators:
            result = result.replace(sep, '|')

        # Разбиваем и очищаем
        skills = [skill.strip() for skill in result.split('|')]
        return [skill for skill in skills if skill]  # Убираем пустые

    def save_photo(self, user_id: int, file_id: str, file_path: str = None, 
                   file_size: int = None, mime_type: str = None):
        """Сохранение информации о фото"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO photos (user_id, file_id, file_path, file_size, mime_type)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    file_id = ?,
                    file_path = ?,
                    file_size = ?,
                    mime_type = ?,
                    updated_at = ?
            """, (user_id, file_id, file_path, file_size, mime_type,
                  file_id, file_path, file_size, mime_type, datetime.now().isoformat()))
            conn.commit()

    def get_photo(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о фото"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM photos WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def delete_photo(self, user_id: int):
        """Удаление фото"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM photos WHERE user_id = ?", (user_id,))
            conn.commit()


# Глобальный экземпляр БД
db = ResumeDatabase()
