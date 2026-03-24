"""
database.py — работа с базой данных SQLite

Один класс ResumeDB со всеми операциями.
Методы названы по действию: save_*, get_*, delete_*

При добавлении нового поля в резюме:
1. Добавить колонку в _create_tables()
2. Добавить поле в save_resume() и get_resume()
"""
import json
import logging
import re
import sqlite3
from datetime import datetime
from typing import List, Optional

from models import Education, ResumeData, WorkExperience

logger = logging.getLogger(__name__)


class ResumeDB:
    """База данных резюме. Один экземпляр на всё приложение."""

    def __init__(self, db_path: str = "resumes.db"):
        self.db_path = db_path
        self._create_tables()

    # ── Инициализация ─────────────────────────────────────────────────────────

    def _create_tables(self):
        """Создать таблицы если не существуют"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS resumes (
                    user_id   INTEGER PRIMARY KEY,
                    full_name TEXT DEFAULT '',
                    email     TEXT DEFAULT '',
                    phone     TEXT DEFAULT '',
                    city      TEXT DEFAULT '',
                    position  TEXT DEFAULT '',
                    summary   TEXT DEFAULT '',
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS work_experience (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id      INTEGER NOT NULL,
                    position     TEXT DEFAULT '',
                    company      TEXT DEFAULT '',
                    start_date   TEXT DEFAULT '',
                    end_date     TEXT DEFAULT '',
                    duties       TEXT DEFAULT '',
                    achievements TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS education (
                    user_id     INTEGER PRIMARY KEY,
                    level       TEXT DEFAULT '',
                    institution TEXT DEFAULT '',
                    faculty     TEXT DEFAULT '',
                    specialty   TEXT DEFAULT '',
                    year        TEXT DEFAULT '',
                    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS skills (
                    user_id    INTEGER PRIMARY KEY,
                    skills_json TEXT DEFAULT '[]',
                    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS photos (
                    user_id   INTEGER PRIMARY KEY,
                    file_id   TEXT DEFAULT '',
                    file_size INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)

    # ── Резюме (основные данные) ──────────────────────────────────────────────

    def save_resume(self, user_id: int, data: dict):
        """Сохранить или обновить основные данные резюме"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO resumes (user_id, full_name, email, phone, city, position, summary, updated_at)
                VALUES (:uid, :full_name, :email, :phone, :city, :position, :summary, :now)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name  = excluded.full_name,
                    email      = excluded.email,
                    phone      = excluded.phone,
                    city       = excluded.city,
                    position   = excluded.position,
                    summary    = excluded.summary,
                    updated_at = excluded.updated_at
            """, {
                "uid": user_id,
                "full_name": data.get("full_name", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "city": data.get("city", ""),
                "position": data.get("position", ""),
                "summary": data.get("summary", ""),
                "now": datetime.now().isoformat(),
            })

    def get_resume(self, user_id: int) -> Optional[dict]:
        """Получить основные данные резюме"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM resumes WHERE user_id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def delete_resume(self, user_id: int):
        """Удалить все данные пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            for table in ("resumes", "work_experience", "education", "skills", "photos"):
                conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))

    # ── Опыт работы ───────────────────────────────────────────────────────────

    def add_work_experience(self, user_id: int, exp: WorkExperience):
        """Добавить запись об опыте работы"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO work_experience
                    (user_id, position, company, start_date, end_date, duties, achievements)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, exp.position, exp.company, exp.start_date,
                  exp.end_date, exp.duties, exp.achievements))

    def get_work_experiences(self, user_id: int) -> List[WorkExperience]:
        """Получить все записи опыта работы"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM work_experience WHERE user_id = ? ORDER BY id", (user_id,)
            ).fetchall()
            return [WorkExperience(
                position=row["position"],
                company=row["company"],
                start_date=row["start_date"],
                end_date=row["end_date"],
                duties=row["duties"],
                achievements=row["achievements"],
                id=row["id"],
            ) for row in rows]

    # ── Образование ───────────────────────────────────────────────────────────

    def save_education(self, user_id: int, edu: Education):
        """Сохранить образование"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO education (user_id, level, institution, faculty, specialty, year, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    level = excluded.level, institution = excluded.institution,
                    faculty = excluded.faculty, specialty = excluded.specialty,
                    year = excluded.year, updated_at = excluded.updated_at
            """, (user_id, edu.level, edu.institution, edu.faculty,
                  edu.specialty, edu.year, datetime.now().isoformat()))

    def get_education(self, user_id: int) -> Optional[Education]:
        """Получить образование"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM education WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return None
            return Education(
                level=row["level"], institution=row["institution"],
                faculty=row["faculty"], specialty=row["specialty"], year=row["year"]
            )

    # ── Навыки ────────────────────────────────────────────────────────────────

    def save_skills(self, user_id: int, skills: List[str]):
        """Сохранить список навыков"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO skills (user_id, skills_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    skills_json = excluded.skills_json,
                    updated_at = excluded.updated_at
            """, (user_id, json.dumps(skills, ensure_ascii=False), datetime.now().isoformat()))

    def get_skills(self, user_id: int) -> List[str]:
        """Получить список навыков"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT skills_json FROM skills WHERE user_id = ?", (user_id,)
            ).fetchone()
            if not row:
                return []
            try:
                return json.loads(row[0])
            except (json.JSONDecodeError, TypeError):
                return []

    @staticmethod
    def parse_skills_text(text: str) -> List[str]:
        """Разобрать строку навыков (разделители: запятая, точка с запятой, перенос строки)"""
        parts = re.split(r'[,;\n]+', text)
        return [s.strip() for s in parts if s.strip()]

    # ── Фото ──────────────────────────────────────────────────────────────────

    def save_photo(self, user_id: int, file_id: str, file_size: int = 0):
        """Сохранить file_id фото из Telegram"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO photos (user_id, file_id, file_size, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    file_id = excluded.file_id,
                    file_size = excluded.file_size,
                    updated_at = excluded.updated_at
            """, (user_id, file_id, file_size, datetime.now().isoformat()))

    def get_photo_file_id(self, user_id: int) -> Optional[str]:
        """Получить file_id фото или None"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT file_id FROM photos WHERE user_id = ?", (user_id,)
            ).fetchone()
            return row[0] if row else None

    def delete_photo(self, user_id: int):
        """Удалить фото"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM photos WHERE user_id = ?", (user_id,))

    # ── Загрузка полных данных резюме ─────────────────────────────────────────

    def load_full_resume(self, user_id: int) -> ResumeData:
        """Загрузить все данные пользователя из БД"""
        base = self.get_resume(user_id) or {}
        return ResumeData(
            user_id=user_id,
            full_name=base.get("full_name", ""),
            email=base.get("email", ""),
            phone=base.get("phone", ""),
            city=base.get("city", ""),
            position=base.get("position", ""),
            summary=base.get("summary", ""),
            work_experiences=self.get_work_experiences(user_id),
            education=self.get_education(user_id),
            skills=self.get_skills(user_id),
            photo_file_id=self.get_photo_file_id(user_id),
        )


# Глобальный экземпляр — используется во всём проекте
db = ResumeDB()
