"""
ocr_engine.py — Runs Tesseract OCR and returns structured word/paragraph blocks.
"""

import re
import pytesseract
from pytesseract import Output
from PIL import Image
import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD
TESSERACT_CONFIG = "--oem 3 --psm 6 -l eng+ara+chi_sim+jpn+kor+hin+rus"
LAYOUT_CONFIG = "--oem 3 --psm 3 -l eng+ara+chi_sim+jpn+kor+hin+rus"


def perform_ocr(img: Image.Image) -> dict:
    """Run Tesseract text extraction with fixed multilingual OCR config."""
    text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
    print(f"[OCR] Preview (first 200 chars): {text[:200]}")
    return {"text": text}


def run_ocr(image_path: str) -> dict:
    """
    Run Tesseract on the given image file.

    Returns:
        {
            "words": [ {text, x, y, w, h, conf, block_num, par_num, line_num} ],
            "paragraphs": [ {text, x, y, w, h, block_num} ]
        }
    """
    img = Image.open(image_path).convert("RGB")

    # Keep exact OCR extraction config for text preview and use layout mode for segmentation.
    perform_ocr(img)
    data = pytesseract.image_to_data(
        img,
        output_type=Output.DICT,
        config=LAYOUT_CONFIG,
    )

    words = []
    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        conf = int(float(data["conf"][i]))
        if text and conf > 20:                  # filter low-confidence noise
            words.append({
                "text":      text,
                "x":         data["left"][i],
                "y":         data["top"][i],
                "w":         data["width"][i],
                "h":         data["height"][i],
                "conf":      conf,
                "block_num": data["block_num"][i],
                "par_num":   data["par_num"][i],
                "line_num":  data["line_num"][i],
            })

    paragraphs = _group_into_paragraphs(words)
    paragraphs = _filter_paragraphs(paragraphs)

    return {"words": words, "paragraphs": paragraphs, "image_size": img.size}


def _group_into_paragraphs(words: list) -> list:
    """Group word-level data into line-aware paragraph blocks."""
    from collections import defaultdict

    groups = defaultdict(list)
    for w in words:
        key = (w["block_num"], w["par_num"], w["line_num"])
        groups[key].append(w)

    paragraphs = []
    for (block_num, par_num, line_num), wlist in groups.items():
        if not wlist:
            continue
        text = " ".join(w["text"] for w in wlist)
        avg_conf = int(round(sum(w["conf"] for w in wlist) / len(wlist)))
        x    = min(w["x"] for w in wlist)
        y    = min(w["y"] for w in wlist)
        x2   = max(w["x"] + w["w"] for w in wlist)
        y2   = max(w["y"] + w["h"] for w in wlist)
        paragraphs.append({
            "text":      text,
            "x":         x,
            "y":         y,
            "w":         x2 - x,
            "h":         y2 - y,
            "block_num": block_num,
            "par_num":   par_num,
            "line_num":  line_num,
            "conf":      avg_conf,
        })

    # Sort top-to-bottom, left-to-right
    paragraphs.sort(key=lambda p: (p["y"], p["x"]))
    return paragraphs


def _contains_cjk(text: str) -> bool:
    """Return True when text contains any CJK script character."""
    return bool(re.search(r"[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]", text))


def _is_only_numbers_or_punctuation(text: str) -> bool:
    """Return True when text has no alphabetic script characters."""
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    # \W + digits + underscore means no letters from any script.
    return bool(re.fullmatch(r"[\W\d_]+", compact, flags=re.UNICODE))


def _is_too_short(text: str) -> bool:
    """Filter short text unless it is a valid single CJK character block."""
    compact = re.sub(r"\s+", "", text)
    if len(compact) >= 3:
        return False
    if _contains_cjk(compact) and len(compact) >= 1:
        return False
    return True


def _filter_paragraphs(paragraphs: list) -> list:
    """Remove noisy OCR blocks using confidence/text-quality rules."""
    filtered = []
    for para in paragraphs:
        text = (para.get("text") or "").strip()
        conf = int(para.get("conf", 0))

        if conf < 40:
            continue
        if _is_too_short(text):
            continue
        if _is_only_numbers_or_punctuation(text):
            continue

        filtered.append(para)
    return filtered
