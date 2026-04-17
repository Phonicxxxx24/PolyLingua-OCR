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
    Build a translated PDF from the annotated paragraph list.
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

    # ── Title ─────────────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=ACCENT,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    story.append(Paragraph("PolyLingua OCR", title_style))
    story.append(Paragraph(f"Multilingual Extraction &amp; Translation Report", sub_style))
    if source_filename:
        story.append(Paragraph(f"Source: <b>{source_filename}</b>", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_LIGHT, spaceAfter=20))

    # ── Summary stats ─────────────────────────────────────────────────────────
    langs_found = list({p.get("lang", {}).get("name", "Unknown") for p in paragraphs})
    langs_found = [l for l in langs_found if l != "Unknown"]

    stat_style = ParagraphStyle(
        "Stat",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
    )
    story.append(Paragraph(f"<b>Total Blocks Detected:</b> {len(paragraphs)}", stat_style))
    story.append(Paragraph(f"<b>Languages Found:</b> {', '.join(langs_found) or 'N/A'}", stat_style))
    story.append(Spacer(1, 20))

    # ── Per-paragraph cards ───────────────────────────────────────────────────
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=ACCENT,
        spaceBefore=14,
        spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#9ca3af"),
        spaceAfter=2,
    )
    orig_style = ParagraphStyle(
        "Original",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6,
        backColor=colors.HexColor("#f9fafb"),
        leftIndent=8,
        rightIndent=8,
        borderPad=4,
    )
    trans_style = ParagraphStyle(
        "Translation",
        parent=styles["Normal"],
        fontSize=11,
        textColor=TEXT_DARK,
        spaceAfter=6,
        backColor=CARD_BG,
        leftIndent=8,
        rightIndent=8,
        borderPad=4,
    )

    for idx, para in enumerate(paragraphs, 1):
        lang_name  = para.get("lang", {}).get("name", "Unknown")
        orig_text  = para.get("text", "")
        trans_text = para.get("translation", "")

        block_elements = [
            Paragraph(f"Block #{idx} — {lang_name}", section_style),
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=6),
            Paragraph("ORIGINAL TEXT:", label_style),
            Paragraph(_safe(orig_text), orig_style),
            Paragraph("ENGLISH TRANSLATION:", label_style),
            Paragraph(_safe(trans_text), trans_style),
            Spacer(1, 8),
        ]
        story.append(KeepTogether(block_elements))

    doc.build(story)
    return output_path


def _safe(text: str) -> str:
    """Escape HTML entities for ReportLab."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))
