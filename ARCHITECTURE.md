# Архитектура проекта

## Что делает проект

Telegram-бот для создания профессиональных резюме:
1. Собирает данные через диалог
2. Переформулирует AI (DeepSeek)
3. Генерирует PDF с кириллицей

## Модули

| Модуль | Что делает | Зависит от |
|--------|-----------|------------|
| `bot.py` | Точка входа, команды | config, handlers |
| `config.py` | Конфигурация | .env |
| `database.py` | SQLite хранилище | - |
| `states.py` | FSM состояния | aiogram |
| `handlers/resume.py` | Сбор данных | states, database |
| `handlers/photo.py` | Загрузка фото | states, database |
| `handlers/ai_handlers.py` | AI команды | ai_processor |
| `services/ai_processor.py` | DeepSeek API | openai |
| `services/pdf_generator.py` | Генерация PDF | reportlab |
| `tests/` | Тесты | pytest |

## Поток данных

```
Пользователь → Telegram → Bot → FSM State
                              ↓
                        Database (SQLite)
                              ↓
                        AI Processor
                              ↓
                        PDF Generator
                              ↓
                        PDF файл → Пользователю
```

## База данных

### Таблица `resumes`
- user_id (PK)
- full_name, email, phone, city, position
- created_at, updated_at

### Таблица `education`
- user_id (PK)
- level, institution, faculty, specialty, year
- updated_at

### Таблица `skills`
- user_id (PK)
- skills_json (JSON массив)
- updated_at

### Таблица `photos`
- user_id (PK)
- file_id, file_path, file_size, mime_type
- updated_at

## FSM состояния

| Группа | Состояния |
|--------|-----------|
| Базовые | FULL_NAME, EMAIL, PHONE, CITY, POSITION |
| Опыт работы | WORK_MENU, WORK_ADD_*, WORK_FINISH |
| Образование | EDUCATION_MENU, EDUCATION_LEVEL, ..., EDUCATION_YEAR |
| Навыки | SKILLS_MENU, SKILLS_ADD |
| Фото | PHOTO_MENU, PHOTO_ADD, PHOTO_SKIP |
| Завершение | IDLE |

**Всего:** 23 состояния

## Inline-кнопки

### Главное меню
- 📝 Создать резюме
- ❓ Помощь

### Меню опыта работы
- ➕ Добавить место работы
- ✅ Завершить и продолжить
- 🏠 В главное меню

### Меню образования
- 🎓 Добавить образование
- ✅ Завершить и перейти к навыкам
- 🏠 В главное меню

### Меню навыков
- 💻 Добавить навыки
- ✅ Завершить создание резюме
- 🏠 В главное меню

### Меню фото
- 📸 Отправить фото
- ⏭️ Пропустить
- 🏠 В главное меню

### Результат фото
- 📄 PDF с AI
- 📄 PDF без AI

## Тесты

| Файл | Тестов | Описание |
|------|--------|----------|
| test_database.py | 5 | CRUD резюме |
| test_education_skills.py | 5 | Образование, навыки |
| test_photo.py | 6 | Фото, валидация |
| test_ai_processor.py | 14 | AI переформулирование |
| test_pdf_generator.py | 8 | Генерация PDF |
| manual_test.py | 1 | Integration тест |

**Итого:** 48 тестов проходят ✅

## Статистика

- **Файлов:** 17
- **Строк кода:** ~1500
- **Состояний FSM:** 23
- **Таблиц БД:** 4
- **Тестов:** 48
