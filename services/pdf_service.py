"""
services/pdf_service.py — генерация PDF-резюме

Публичный метод: generate_pdf(resume, bot) → BytesIO

Для изменения дизайна PDF — правь метод _build_styles() и методы _section_*
Шрифты: Arial (Windows) или DejaVu (Linux/Docker). Оба поддерживают кириллицу.
"""
import logging
import os
import platform
import tempfile
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

from models import ResumeData

logger = logging.getLogger(__name__)

# ─── Шрифты с кириллицей ──────────────────────────────────────────────────────
# Приоритет: DejaVu (кросс-платформенный) → Arial (Windows) → Helvetica (fallback)

def _register_fonts() -> tuple[str, str]:
    """Зарегистрировать шрифты и вернуть (обычный, жирный)"""
    # 1. DejaVu — работает на Linux/Docker (поставляется с reportlab или системный)
    dejavu_paths = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("fonts/DejaVuSans.ttf", "fonts/DejaVuSans-Bold.ttf"),
    ]
    for regular, bold in dejavu_paths:
        if os.path.exists(regular) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", regular))
                pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))
                logger.info(f"Шрифт DejaVu зарегистрирован из {regular}")
                return "DejaVu", "DejaVu-Bold"
            except Exception as e:
                logger.warning(f"Не удалось зарегистрировать DejaVu: {e}")

    # 2. Arial — Windows
    if platform.system() == "Windows":
        arial = "C:/Windows/Fonts/arial.ttf"
        arial_bold = "C:/Windows/Fonts/arialbd.ttf"
        if os.path.exists(arial) and os.path.exists(arial_bold):
            try:
                pdfmetrics.registerFont(TTFont("Arial", arial))
                pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold))
                logger.info("Шрифт Arial зарегистрирован")
                return "Arial", "Arial-Bold"
            except Exception as e:
                logger.warning(f"Не удалось зарегистрировать Arial: {e}")

    logger.warning("Кириллические шрифты не найдены, используется Helvetica (без кириллицы)")
    return "Helvetica", "Helvetica-Bold"


FONT_REGULAR, FONT_BOLD = _register_fonts()


class PDFService:
    """Генератор PDF-резюме"""

    # ── Цвета (меняй здесь для смены дизайна) ────────────────────────────────
    COLOR_HEADER_BG = colors.HexColor("#2c3e50")    # Тёмно-синий фон шапки
    COLOR_HEADER_TEXT = colors.white
    COLOR_SECTION_LINE = colors.HexColor("#3498db")  # Синяя линия под заголовком раздела
    COLOR_SECTION_TEXT = colors.HexColor("#2c3e50")
    COLOR_BODY_TEXT = colors.HexColor("#333333")
    COLOR_CONTACT_TEXT = colors.HexColor("#ecf0f1")

    def __init__(self):
        self.styles = self._build_styles()

    def _build_styles(self) -> dict:
        """Все стили ReportLab. Меняй font size, spaceAfter, textColor здесь."""
        return {
            "name": ParagraphStyle(
                "Name", fontName=FONT_BOLD, fontSize=26, alignment=TA_CENTER,
                textColor=self.COLOR_HEADER_TEXT, spaceAfter=4
            ),
            "contact": ParagraphStyle(
                "Contact", fontName=FONT_REGULAR, fontSize=10, alignment=TA_CENTER,
                textColor=self.COLOR_CONTACT_TEXT, spaceAfter=2
            ),
            "section_title": ParagraphStyle(
                "SectionTitle", fontName=FONT_BOLD, fontSize=14,
                textColor=self.COLOR_SECTION_TEXT, spaceBefore=16, spaceAfter=4
            ),
            "job_title": ParagraphStyle(
                "JobTitle", fontName=FONT_BOLD, fontSize=11,
                textColor=self.COLOR_BODY_TEXT, spaceAfter=2
            ),
            "company": ParagraphStyle(
                "Company", fontName=FONT_REGULAR, fontSize=10,
                textColor=colors.HexColor("#7f8c8d"), spaceAfter=4
            ),
            "body": ParagraphStyle(
                "Body", fontName=FONT_REGULAR, fontSize=10,
                textColor=self.COLOR_BODY_TEXT, spaceAfter=4, leading=14
            ),
            "skills": ParagraphStyle(
                "Skills", fontName=FONT_REGULAR, fontSize=10,
                textColor=self.COLOR_BODY_TEXT, spaceAfter=2
            ),
        }

    async def generate_pdf(self, resume: ResumeData, bot=None) -> BytesIO:
        """
        Сгенерировать PDF-резюме.
        bot нужен только для загрузки фото из Telegram.
        Возвращает BytesIO с PDF.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm
        )

        story = []

        # Шапка с именем и контактами
        story.extend(await self._build_header(resume, bot))

        # Должность
        if resume.position:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(resume.position, self.styles["company"]))

        # Опыт работы
        if resume.work_experiences:
            story.extend(self._build_section("Опыт работы"))
            for exp in resume.work_experiences:
                story.extend(self._build_work_item(exp))

        # Образование
        if resume.education:
            story.extend(self._build_section("Образование"))
            story.extend(self._build_education_item(resume.education))

        # Навыки
        if resume.skills:
            story.extend(self._build_section("Навыки"))
            story.append(Paragraph(" • ".join(resume.skills), self.styles["skills"]))

        doc.build(story)
        buffer.seek(0)
        return buffer

    async def _build_header(self, resume: ResumeData, bot) -> list:
        """Шапка: фото слева, имя и контакты справа"""
        elements = []

        # Контактная строка
        contacts = []
        if resume.phone:
            contacts.append(resume.phone)
        if resume.email:
            contacts.append(resume.email)
        if resume.city:
            contacts.append(f"📍 {resume.city}")

        name_para = Paragraph(resume.full_name or "Имя не указано", self.styles["name"])
        contact_para = Paragraph("  |  ".join(contacts), self.styles["contact"])

        # Загружаем фото если есть
        photo_image = None
        if resume.photo_file_id and bot:
            photo_image = await self._download_photo(resume.photo_file_id, bot)

        # Шапка как таблица: [фото | имя + контакты]
        if photo_image:
            header_data = [[photo_image, [name_para, Spacer(1, 0.2 * cm), contact_para]]]
            col_widths = [3 * cm, 14 * cm]
        else:
            header_data = [[[name_para, Spacer(1, 0.2 * cm), contact_para]]]
            col_widths = [17 * cm]

        header_table = Table(header_data, colWidths=col_widths)
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), self.COLOR_HEADER_BG),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 16),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.COLOR_HEADER_BG]),
        ]))
        elements.append(header_table)
        return elements

    def _build_section(self, title: str) -> list:
        """Заголовок раздела с горизонтальной линией"""
        return [
            Spacer(1, 0.4 * cm),
            Paragraph(title, self.styles["section_title"]),
            HRFlowable(width="100%", thickness=1, color=self.COLOR_SECTION_LINE, spaceAfter=6),
        ]

    def _build_work_item(self, exp) -> list:
        """Одна запись опыта работы"""
        elements = []
        period = f"{exp.start_date} — {exp.end_date}" if exp.start_date else ""

        # Таблица: [Должность | Период]
        if period:
            row = [[
                Paragraph(exp.position, self.styles["job_title"]),
                Paragraph(period, self.styles["company"])
            ]]
            t = Table(row, colWidths=[11 * cm, 6 * cm])
            t.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            elements.append(t)
        else:
            elements.append(Paragraph(exp.position, self.styles["job_title"]))

        if exp.company:
            elements.append(Paragraph(exp.company, self.styles["company"]))

        if exp.duties:
            elements.append(Paragraph(f"<b>Обязанности:</b> {exp.duties}", self.styles["body"]))

        if exp.achievements:
            elements.append(Paragraph(f"<b>Достижения:</b> {exp.achievements}", self.styles["body"]))

        elements.append(Spacer(1, 0.3 * cm))
        return elements

    def _build_education_item(self, edu) -> list:
        """Блок образования"""
        elements = []
        if edu.level and edu.institution:
            elements.append(Paragraph(f"{edu.level} — {edu.institution}", self.styles["job_title"]))
        elif edu.institution:
            elements.append(Paragraph(edu.institution, self.styles["job_title"]))

        details = []
        if edu.faculty:
            details.append(f"Факультет: {edu.faculty}")
        if edu.specialty:
            details.append(f"Специальность: {edu.specialty}")
        if edu.year:
            details.append(f"Год окончания: {edu.year}")
        if details:
            elements.append(Paragraph(", ".join(details), self.styles["body"]))

        return elements

    async def _download_photo(self, file_id: str, bot) -> Optional[Image]:
        """Скачать фото из Telegram и вернуть Image для ReportLab"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                await bot.download(file_id, destination=f.name)
                img = Image(f.name, width=2.5 * cm, height=3 * cm)
                img.keepInFrame = True
                return img
        except Exception as e:
            logger.warning(f"Не удалось загрузить фото {file_id}: {e}")
            return None


# Глобальный экземпляр
pdf_service = PDFService()
