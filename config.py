"""
config.py — все настройки и константы проекта

Одно место для всех конфигурационных значений.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ─── AI ────────────────────────────────────────────────────────────────────────
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL: str = "deepseek-chat"
AI_ENABLED: bool = bool(DEEPSEEK_API_KEY)  # AI доступен только если есть ключ

# ─── База данных ───────────────────────────────────────────────────────────────
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "resumes.db")

# ─── Фото ──────────────────────────────────────────────────────────────────────
MAX_PHOTO_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

# ─── Логирование ───────────────────────────────────────────────────────────────
LOG_FILE: str = "bot.log"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
