"""
language_detector.py — Detect language of each paragraph block.
"""

import re
from langdetect import detect, LangDetectException

# Human-readable names + language badge colors
LANG_META = {
    "ar":    {"name": "Arabic",              "color": "#f59e0b"},
    "zh-cn": {"name": "Chinese (Simplified)","color": "#ef4444"},
    "zh-tw": {"name": "Chinese (Traditional)","color": "#f97316"},
    "ja":    {"name": "Japanese",            "color": "#a855f7"},
    "ko":    {"name": "Korean",              "color": "#3b82f6"},
    "hi":    {"name": "Hindi (Devanagari)",  "color": "#10b981"},
    "ru":    {"name": "Russian (Cyrillic)",  "color": "#06b6d4"},
    "en":    {"name": "English",             "color": "#6b7280"},
    "de":    {"name": "German",              "color": "#8b5cf6"},
    "fr":    {"name": "French",              "color": "#ec4899"},
    "es":    {"name": "Spanish",             "color": "#14b8a6"},
    "it":    {"name": "Italian",             "color": "#f472b6"},
    "pt":    {"name": "Portuguese",          "color": "#84cc16"},
    "unknown": {"name": "Unknown",           "color": "#374151"},
}


SCRIPT_PATTERNS = {
    "ar": re.compile(r"[\u0600-\u06FF]"),
    "zh-cn": re.compile(r"[\u4E00-\u9FFF]"),
    "ja": re.compile(r"[\u3040-\u30FF]"),
    "ko": re.compile(r"[\uAC00-\uD7AF]"),
    "hi": re.compile(r"[\u0900-\u097F]"),
    "ru": re.compile(r"[\u0400-\u04FF]"),
}


def _detect_by_script(text: str) -> str:
    """Return a language code based on strong Unicode script evidence."""
    script_hits = {}
    for code, pattern in SCRIPT_PATTERNS.items():
        script_hits[code] = len(pattern.findall(text))

    best_code = max(script_hits, key=script_hits.get)
    if script_hits[best_code] > 0:
        return best_code
    return "unknown"


def detect_language(text: str) -> dict:
    """
    Detect language of a text string.
    Returns: { code, name, color }
    """
    if not text or len(text.strip()) < 3:
        return {"code": "unknown", **LANG_META["unknown"]}

    # Prefer script detection when possible; it is more stable for short OCR blocks.
    script_code = _detect_by_script(text)
    if script_code != "unknown":
        return {"code": script_code, **LANG_META.get(script_code, LANG_META["unknown"])}

    try:
        code = detect(text)
        meta = LANG_META.get(code, {"name": code.upper(), "color": "#6366f1"})
        return {"code": code, **meta}
    except LangDetectException:
        return {"code": "unknown", **LANG_META["unknown"]}


def annotate_paragraphs(paragraphs: list) -> list:
    """
    Add language detection result to each paragraph block.
    Returns the same list with 'lang' field added.
    """
    for para in paragraphs:
        para["lang"] = detect_language(para["text"])
    return paragraphs
