# AI-GUIDE.md — Руководство для ИИ-агента

## Что делает этот проект

Telegram-бот создаёт PDF-резюме. Пользователь вводит данные через диалог, 
DeepSeek AI улучшает текст, ReportLab генерирует PDF с кириллицей.

## Как читать код — порядок файлов

```
1. config.py          — все настройки и константы
2. models.py          — структуры данных (dataclasses)
3. database.py        — работа с SQLite
4. states.py          — FSM состояния диалога
5. keyboards.py       — ВСЕ inline-клавиатуры в одном месте
6. handlers/
   ├── start.py       — /start, /help
   ├── resume.py      — сбор базовых данных (ФИО, email, телефон...)
   ├── work.py        — опыт работы
   ├── education.py   — образование
   ├── skills.py      — навыки
   ├── photo.py       — загрузка фото
   └── generate.py    — генерация PDF
7. services/
   ├── ai_service.py  — DeepSeek API
   └── pdf_service.py — генерация PDF
8. bot.py             — точка входа, регистрация роутеров
```

## Как добавить новое поле в резюме

1. Добавить поле в `models.py` → класс `ResumeData`
2. Добавить колонку в `database.py` → метод `_create_tables()`
3. Добавить состояние в `states.py`
4. Добавить хэндлер в нужный файл `handlers/`
5. Обновить `services/pdf_service.py` чтобы поле отобразилось в PDF

## Как изменить текст кнопок

Все кнопки в `keyboards.py`. Функция называется `kb_<назначение>`.

## Как изменить промпт для AI

В `services/ai_service.py`, метод `_get_prompt(context)` — словарь промптов.

## Как изменить дизайн PDF

В `services/pdf_service.py`, метод `_build_styles()` — все стили ReportLab.

## Схема базы данных

```sql
-- resumes: основные данные
user_id | full_name | email | phone | city | position | summary

-- work_experience: опыт работы (один пользователь — много записей)
id | user_id | position | company | start_date | end_date | duties | achievements

-- education: образование
user_id | level | institution | faculty | specialty | year

-- skills: навыки (JSON массив)
user_id | skills_json

-- photos: фото
user_id | file_id | file_size
```

## Переменные окружения (.env)

```
TELEGRAM_BOT_TOKEN=...   # обязательно
DEEPSEEK_API_KEY=...     # опционально, без него AI отключается
```

## Запуск

```bash
pip install -r requirements.txt
python bot.py
```

## Тесты

```bash
pytest tests/ -v
```

## Частые задачи

| Задача | Файл |
|--------|------|
| Изменить приветственное сообщение | handlers/start.py |
| Добавить новый раздел резюме | models.py → database.py → states.py → handlers/ |
| Изменить формат PDF | services/pdf_service.py |
| Изменить промпты AI | services/ai_service.py → _get_prompt() |
| Добавить кнопку | keyboards.py |
| Изменить валидацию | handlers/resume.py (email/phone) |
