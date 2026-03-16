# Telegram Resume Bot — Бот для создания резюме

Telegram-бот для сбора информации о пользователе через диалог и генерации профессионального резюме в PDF с AI-переформулированием.

## Быстрый старт

1. **Установи зависимости:**
```bash
pip install -r requirements.txt
```

2. **Настрой .env:**
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
DEEPSEEK_API_KEY=your_api_key
```

3. **Запусти бота:**
```bash
python bot.py
```

4. **Или используй скрипты:**
- `restart_bot.bat` — перезапуск бота
- `check_bot.bat` — проверка статуса
- `stop_bot.bat` — остановка бота

## Структура проекта

```
resume_bot/
├── .env                    # Переменные окружения
├── requirements.txt        # Зависимости
├── config.py               # Конфигурация
├── bot.py                  # Точка входа
├── database.py             # SQLite БД
├── states.py               # FSM состояния
├── ARCHITECTURE.md         # Архитектура
├── TODO.md                 # Задачи
├── SCRIPTS.md              # Скрипты управления
├── handlers/
│   ├── __init__.py
│   ├── resume.py           # Обработчики резюме
│   ├── photo.py            # Обработчики фото
│   └── ai_handlers.py      # AI обработчики
├── services/
│   ├── __init__.py
│   ├── ai_processor.py     # AI переформулирование
│   └── pdf_generator.py    # Генерация PDF
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_ai_processor.py
│   ├── test_education_skills.py
│   ├── test_photo.py
│   ├── test_pdf_generator.py
│   └── manual_test.py
├── restart_bot.bat
├── check_bot.bat
└── stop_bot.bat
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Запустить бота, показать меню |
| `/resume` | Начать создание резюме |
| `/generate` | Сгенерировать PDF-резюме |
| `/help` | Показать справку |

## Возможности

- ✅ Пошаговый сбор данных (ФИО, контакты, должность)
- ✅ Опыт работы с деталями (компания, период, обязанности, достижения)
- ✅ Образование (уровень, ВУЗ, факультет, специальность, год)
- ✅ Навыки (парсинг через запятую/;/\n)
- ✅ Загрузка фото
- ✅ AI-переформулирование текста (DeepSeek API)
- ✅ Генерация PDF с кириллицей

## Тесты

```bash
# Запустить все тесты
python -m pytest tests/ -v

# Запустить с покрытием
python -m pytest tests/ -v --cov=.

# Запустить конкретный тест
python -m pytest tests/test_pdf_generator.py -v
```

**Статистика тестов:** 48 тестов проходят ✅

## Технологии

- **aiogram 3.x** — Telegram бот
- **SQLite** — база данных
- **reportlab** — генерация PDF
- **DeepSeek API** — AI переформулирование
- **pytest** — тестирование

## Лицензия

MIT
