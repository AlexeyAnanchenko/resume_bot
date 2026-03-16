"""
Генератор PDF-резюме с AI-переформулированием
"""
import logging
import re
from io import BytesIO
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
# Шрифты с поддержкой кириллицы
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from services.ai_processor import ai_processor
from database import db
import tempfile
import os

logger = logging.getLogger(__name__)

# Глобальная переменная для bot (устанавливается извне при необходимости)
_bot = None


def set_bot(bot):
    """Установка экземпляра бота для загрузки фото"""
    global _bot
    _bot = bot


def get_bot():
    """Получение экземпляра бота"""
    if _bot is None:
        # Пытаемся импортировать из bot.py
        try:
            from bot import bot
            return bot
        except Exception:
            return None
    return _bot

# Регистрируем шрифт с поддержкой кириллицы
# На Windows используем Arial, на Linux/Mac — другие системные шрифты
import platform
import os

system = platform.system()
FONT_REGISTERED = False

if system == 'Windows':
    # Windows шрифты
    arial_path = 'C:\\Windows\\Fonts\\arial.ttf'
    arial_bold_path = 'C:\\Windows\\Fonts\\arialbd.ttf'
    
    if os.path.exists(arial_path) and os.path.exists(arial_bold_path):
        try:
            pdfmetrics.registerFont(TTFont('Arial', arial_path))
            pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
            CYRILLIC_FONT = 'Arial'
            CYRILLIC_BOLD = 'Arial-Bold'
            FONT_REGISTERED = True
            logger.info("Шрифт Arial зарегистрирован")
        except Exception as e:
            logger.warning(f"Не удалось зарегистрировать Arial: {e}")
            CYRILLIC_FONT = 'Helvetica'
            CYRILLIC_BOLD = 'Helvetica-Bold'
    else:
        logger.warning(f"Шрифты Arial не найдены: {arial_path}")
        CYRILLIC_FONT = 'Helvetica'
        CYRILLIC_BOLD = 'Helvetica-Bold'
else:
    CYRILLIC_FONT = 'Helvetica'
    CYRILLIC_BOLD = 'Helvetica-Bold'

if not FONT_REGISTERED:
    logger.warning(f"Используется шрифт без кириллицы: {CYRILLIC_FONT}")


class PDFResumeGenerator:
    """Генератор PDF-резюме"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Настройка стилей"""
        # Заголовок (ФИО)
        self.title_style = ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=10,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            fontName=CYRILLIC_BOLD
        )

        # Подзаголовок (должность)
        self.subtitle_style = ParagraphStyle(
            name='ResumeSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER,
            fontName=CYRILLIC_BOLD
        )

        # Заголовок раздела
        self.section_style = ParagraphStyle(
            name='ResumeSection',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#34495e'),
            borderWidth=0,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=5,
            fontName=CYRILLIC_BOLD
        )

        # Обычный текст
        self.body_style = ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leading=14,
            fontName=CYRILLIC_FONT
        )

    async def _add_photo(self, photo_data: Dict[str, Any]):
        """
        Добавление фото в PDF

        Args:
            photo_data: Данные фото из БД (file_id, file_path и т.д.)

        Returns:
            Image элемент для PDF или None
        """
        file_id = photo_data.get("file_id")
        if not file_id:
            logger.warning("Нет file_id для фото")
            return None

        try:
            # Создаём временный файл для загрузки фото
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_path = temp_file.name

            # Загружаем фото из Telegram
            bot = get_bot()
            if not bot:
                logger.warning("Бот не инициализирован, не могу загрузить фото")
                os.unlink(temp_path)
                return None

            await bot.download(file_id, destination=temp_path)

            # Проверяем, что файл загружен
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                logger.warning(f"Фото не загруено: {temp_path}")
                os.unlink(temp_path)
                return None

            # Создаём Image элемент
            # Размер фото: 5x6 см (достаточно крупно для резюме)
            photo_width = 6 * cm
            photo_height = 7 * cm

            img = Image(temp_path, width=photo_width, height=photo_height)

            # Сохраняем путь к файлу в объекте Image для последующего удаления
            img._temp_path = temp_path

            logger.info(f"Фото добавлено: {temp_path}, размер: {os.path.getsize(temp_path)} байт")
            return img

        except Exception as e:
            logger.error(f"Ошибка загрузки фото: {e}")
            # Удаляем временный файл если он создан
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            return None

    async def generate(self, user_id: int, state_data: Dict[str, Any]) -> BytesIO:
        """
        Генерация PDF-резюме с AI-переформулированием

        Args:
            user_id: ID пользователя
            state_data: Данные из state

        Returns:
            BytesIO с PDF-файлом
        """
        logger.info(f"Генерация PDF с AI для пользователя {user_id}")

        # Получаем и переформулируем данные
        refined_data = await self._get_refined_data(user_id, state_data)
        return await self._build_pdf(refined_data)

    async def generate_simple(self, user_id: int, state_data: Dict[str, Any]) -> BytesIO:
        """
        Генерация PDF-резюме без AI (исходные данные)

        Args:
            user_id: ID пользователя
            state_data: Данные из state

        Returns:
            BytesIO с PDF-файлом
        """
        logger.info(f"Генерация PDF без AI для пользователя {user_id}")
        logger.info(f"state_data: {state_data}")

        # Получаем данные без переформулирования
        user_data = db.get_resume(user_id)
        logger.info(f"user_data из БД: {user_data}")
        
        if not user_data:
            # Пустой PDF
            user_data = {}

        simple_data = {
            "user_data": user_data,
            "work_experiences": state_data.get("work_experiences", []),
            "education": db.get_education(user_id),
            "skills": db.get_skills(user_id),
            "photo": db.get_photo(user_id),
            "position_refined": user_data.get("position", "")  # Используем оригинал
        }
        logger.info(f"simple_data: {simple_data}")

        return await self._build_pdf(simple_data)

    async def _build_pdf(self, refined_data: Dict[str, Any]) -> BytesIO:
        """
        Построение PDF документа

        Args:
            refined_data: Данные для PDF

        Returns:
            BytesIO с PDF-файлом
        """
        logger.info(f"_build_pdf вызван с данными: {refined_data}")
        
        buffer = BytesIO()
        logger.info(f"Создан buffer, initial tell: {buffer.tell()}")
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        elements = []
        logger.info(f"Начало построения элементов PDF")

        # Заголовок (ФИО)
        user_data = refined_data.get("user_data", {})
        logger.info(f"user_data: {user_data}")
        
        full_name = user_data.get("full_name", "")
        logger.info(f"full_name: '{full_name}'")
        if full_name:
            try:
                p = Paragraph(full_name, self.title_style)
                elements.append(p)
                logger.info(f"Добавлен заголовок с ФИО: {full_name}")
            except Exception as e:
                logger.error(f"Ошибка добавления ФИО: {e}")

        # Должность
        position = refined_data.get("position_refined") or user_data.get("position", "")
        logger.info(f"position: '{position}'")
        if position:
            try:
                p = Paragraph(position, self.subtitle_style)
                elements.append(p)
                logger.info(f"Добавлена должность: {position}")
            except Exception as e:
                logger.error(f"Ошибка добавления должности: {e}")

        # Фото (если есть)
        photo_data = refined_data.get("photo")
        logger.info(f"photo_data: {photo_data}")
        if photo_data and photo_data.get("file_id"):
            try:
                photo_element = await self._add_photo(photo_data)
                if photo_element:
                    elements.append(photo_element)
                    elements.append(Spacer(1, 0.3*cm))
                    logger.info("Добавлено фото в PDF")
            except Exception as e:
                logger.error(f"Ошибка добавления фото: {e}")

        # Контакты
        contact_info = self._format_contacts(user_data)
        logger.info(f"contact_info: '{contact_info}'")
        if contact_info:
            try:
                p = Paragraph(contact_info, self.body_style)
                elements.append(p)
                elements.append(Spacer(1, 0.3*cm))
                logger.info("Добавлены контакты")
            except Exception as e:
                logger.error(f"Ошибка добавления контактов: {e}")

        # Опыт работы
        work_experiences = refined_data.get("work_experiences", [])
        logger.info(f"work_experiences: {work_experiences}")
        if work_experiences:
            try:
                elements.append(Paragraph("ОПЫТ РАБОТЫ", self.section_style))
                for exp in work_experiences:
                    elements.extend(self._format_work_experience(exp))
                logger.info(f"Добавлен опыт работы: {len(work_experiences)} записей")
            except Exception as e:
                logger.error(f"Ошибка добавления опыта работы: {e}")

        # Образование
        education = refined_data.get("education")
        logger.info(f"education: {education}")
        if education and education.get("institution"):
            try:
                elements.append(Paragraph("ОБРАЗОВАНИЕ", self.section_style))
                elements.extend(self._format_education(education))
                logger.info("Добавлено образование")
            except Exception as e:
                logger.error(f"Ошибка добавления образования: {e}")

        # Навыки
        skills = refined_data.get("skills_refined") or refined_data.get("skills", [])
        logger.info(f"skills: {skills}")
        if skills:
            try:
                elements.append(Paragraph("НАВЫКИ", self.section_style))
                
                # Преобразуем в список если это строка
                if isinstance(skills, str):
                    # Очищаем от markdown-форматирования
                    skills = skills.replace('**', '').replace('*', '').replace('`', '')
                    
                    # Разбиваем текст на отдельные навыки
                    skills_list = []
                    
                    # Сначала разбиваем по заголовкам типа "Технические навыки:"
                    parts = re.split(r'(?i)\s*(технические навыки|навыки|skills|technical skills)\s*:\s*', skills)
                    
                    for part in parts:
                        if not part.strip():
                            continue
                        # Пропускаем сами заголовки
                        if part.strip().lower() in ['технические навыки', 'навыки', 'skills', 'technical skills']:
                            continue
                            
                        # Разбиваем часть по маркерам списка (-, •, *) или новой строке
                        sub_parts = re.split(r'[\n•]|\s*-\s*|\s*\*\s*', part)
                        for sub in sub_parts:
                            sub = sub.strip()
                            # Дополнительно разбиваем по запятой
                            if ',' in sub:
                                for item in sub.split(','):
                                    item = item.strip()
                                    if item and item.lower() not in ['технические навыки', 'навыки', 'skills', 'technical skills']:
                                        skills_list.append(item)
                            elif sub and sub.lower() not in ['технические навыки', 'навыки', 'skills', 'technical skills']:
                                skills_list.append(sub)
                else:
                    skills_list = skills
                
                # Добавляем каждый навык с новой строки
                for skill in skills_list:
                    # Убираем лишние маркеры
                    skill_clean = skill.lstrip('•-*').strip()
                    # Пропускаем заголовки и пустые
                    skip_phrases = ['технические навыки', 'навыки', 'skills', 'technical skills', '']
                    if skill_clean and skill_clean.lower() not in skip_phrases:
                        elements.append(Paragraph(f"• {skill_clean}", self.body_style))
                
                logger.info("Добавлены навыки")
            except Exception as e:
                logger.error(f"Ошибка добавления навыков: {e}")

        logger.info(f"Всего элементов в PDF: {len(elements)}")
        
        if not elements:
            # Добавляем хотя бы один элемент чтобы PDF не был пустым
            logger.warning("Нет элементов, добавляем placeholder")
            try:
                logger.info(f"Попытка добавить placeholder с title_style={self.title_style}, fontName={self.title_style.fontName}")
                elements.append(Paragraph("Resume", self.title_style))
                elements.append(Spacer(1, 2*cm))
                elements.append(Paragraph("No data found", self.body_style))
                logger.info("Placeholder добавлен успешно")
            except Exception as e:
                logger.error(f"Ошибка добавления placeholder: {e}", exc_info=True)
                # Используем стандартные стили без кириллицы
                from reportlab.lib.styles import getSampleStyleSheet
                styles = getSampleStyleSheet()
                elements.append(Paragraph("Resume", styles['Heading1']))
                elements.append(Spacer(1, 2*cm))
                elements.append(Paragraph("No data found", styles['Normal']))
                logger.info("Placeholder добавлен со стандартными стилями")

        # Build PDF
        logger.info(f"Начало doc.build(), элементов: {len(elements)}")
        try:
            doc.build(elements)
            logger.info(f"doc.build() завершён, buffer.tell(): {buffer.tell()}")
        except Exception as e:
            logger.error(f"Ошибка doc.build(): {e}", exc_info=True)
            # Создаём минимальный PDF вручную
            from reportlab.pdfgen import canvas
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.drawString(100, 750, "Resume")
            can.save()
            packet.seek(0)
            # Копируем в оригинальный буфер
            buffer.write(packet.getvalue())

        # Очищаем временные файлы от фото
        for elem in elements:
            if hasattr(elem, '_temp_path'):
                try:
                    if os.path.exists(elem._temp_path):
                        os.unlink(elem._temp_path)
                        logger.info(f"Временный файл фото удалён: {elem._temp_path}")
                except Exception as e:
                    logger.warning(f"Не удалось удалить временный файл {elem._temp_path}: {e}")

        buffer.seek(0)
        logger.info(f"PDF сгенерирован, размер: {buffer.tell()} байт")
        return buffer

    async def _get_refined_data(self, user_id: int, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Получение данных с AI-переформулированием"""
        user_data = db.get_resume(user_id)
        
        # Если данных в БД нет, берём из state_data
        if not user_data:
            logger.warning(f"Данные не найдены в БД для user_id={user_id}, используем state_data")
            user_data = {
                "full_name": state_data.get("full_name", ""),
                "email": state_data.get("email", ""),
                "phone": state_data.get("phone", ""),
                "city": state_data.get("city", ""),
                "position": state_data.get("position", "")
            }

        refined = {
            "user_data": user_data,
            "work_experiences": [],
            "education": db.get_education(user_id),
            "skills": db.get_skills(user_id),
            "photo": db.get_photo(user_id)
        }

        # Если образования нет в БД, берём из state_data
        if not refined["education"]:
            refined["education"] = {
                "level": state_data.get("education_level", ""),
                "institution": state_data.get("education_institution", ""),
                "faculty": state_data.get("education_faculty", ""),
                "specialty": state_data.get("education_specialty", ""),
                "year": state_data.get("education_year", "")
            }

        # Если навыков нет в БД, берём из state_data
        if not refined["skills"]:
            skills_text = state_data.get("skills", "")
            if skills_text:
                refined["skills"] = db.parse_skills(skills_text)
            else:
                refined["skills"] = []

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

        return refined

    def _format_contacts(self, user_data: Dict[str, Any]) -> str:
        """Форматирование контактов"""
        parts = []

        if user_data.get("email"):
            parts.append(f"Email: {user_data['email']}")
        if user_data.get("phone"):
            parts.append(f"Тел: {user_data['phone']}")
        if user_data.get("city"):
            parts.append(f"Город: {user_data['city']}")

        return " | ".join(parts)

    def _format_work_experience(self, exp: Dict[str, Any]) -> List:
        """Форматирование опыта работы"""
        elements = []

        # Должность и компания
        position = exp.get("position", "")
        company = exp.get("company", "")
        period = f"{exp.get('start_date', '')} — {exp.get('end_date', '')}"

        if position or company:
            header = f"<b>{position}</b> в {company}" if company else f"<b>{position}</b>"
            if period:
                header += f" ({period})"
            elements.append(Paragraph(header, self.body_style))

        # Обязанности - разбиваем по строкам
        duties = exp.get("duties", "")
        if duties:
            # Разбиваем по новой строке или точке с запятой
            duties_lines = [d.strip() for d in duties.replace(';', '\n').split('\n') if d.strip()]
            for duty in duties_lines:
                # Убираем лишние маркеры списка
                duty_clean = duty.lstrip('•-').strip()
                if duty_clean:
                    elements.append(Paragraph(f"• {duty_clean}", self.body_style))

        # Достижения
        achievements = exp.get("achievements", "")
        if achievements:
            elements.append(Paragraph(f"<i>Достижения: {achievements}</i>", self.body_style))

        elements.append(Spacer(1, 0.2*cm))
        return elements

    def _format_education(self, education: Dict[str, Any]) -> List:
        """Форматирование образования"""
        elements = []

        level = education.get("level", "")
        institution = education.get("institution", "")
        faculty = education.get("faculty", "")
        specialty = education.get("specialty", "")
        year = education.get("year", "")

        text = f"<b>{level}</b>: {institution}"
        if faculty or specialty:
            text += f", {faculty}, {specialty}"
        if year:
            text += f" ({year})"

        elements.append(Paragraph(text, self.body_style))
        elements.append(Spacer(1, 0.2*cm))
        return elements


# Глобальный экземпляр
pdf_generator = PDFResumeGenerator()
