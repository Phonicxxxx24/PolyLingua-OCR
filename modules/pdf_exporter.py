"""
pdf_exporter.py — Generates a styled translated PDF using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


# ── Color palette ─────────────────────────────────────────────────────────────
BG_COLOR      = colors.HexColor("#0d0f14")
ACCENT        = colors.HexColor("#7c3aed")
ACCENT_LIGHT  = colors.HexColor("#a78bfa")
TEXT_DARK     = colors.HexColor("#1e1b4b")
CARD_BG       = colors.HexColor("#f5f3ff")
HEADER_BG     = colors.HexColor("#4c1d95")


def export_pdf(paragraphs: list, output_path: str, source_filename: str = "") -> str:
    """
    Build a clean translated-only PDF from the paragraph list.
    Returns output_path.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Translated text only ──────────────────────────────────────────────────
    trans_style = ParagraphStyle(
        "Translation",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#111827"),
        leading=17,
        spaceAfter=10,
    )

    for para in paragraphs:
        trans_text = para.get("translation", "")
        if not trans_text or not trans_text.strip():
            continue
        story.append(Paragraph(_safe(trans_text.strip()), trans_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    return output_path


def _safe(text: str) -> str:
    """Escape HTML entities for ReportLab."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
