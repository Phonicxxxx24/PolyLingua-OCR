"""
app.py — PolyLingua OCR Flask Application
"""

import os
import uuid
import json
import asyncio
import inspect
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from googletrans import Translator

import config
from modules.ocr_engine       import run_ocr
from modules.language_detector import annotate_paragraphs
from modules.translator        import translate_paragraphs
from modules.image_processor   import annotate_image
from modules.pdf_exporter      import export_pdf


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
app.config["UPLOAD_FOLDER"]      = config.UPLOAD_FOLDER

SUPPORTED_BACK_TRANSLATE_LANGS = {"ar", "zh-cn", "ja", "ko", "hi", "ru"}


# ── Helpers ────────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return ("." in filename and
            filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTS)


def pdf_to_image(pdf_path: str, upload_folder: str, job_id: str) -> str:
    """Convert first page of PDF to a PNG for OCR."""
    pages = convert_from_path(
        pdf_path,
        dpi=200,
        first_page=1,
        last_page=1,
        poppler_path=config.POPPLER_PATH,   # explicit path — avoids PATH lookup issues
    )
    img_path = os.path.join(upload_folder, f"{job_id}_page1.png")
    pages[0].save(img_path, "PNG")
    return img_path


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    # ── Save upload ────────────────────────────────────────────────────────────
    job_id   = str(uuid.uuid4())[:8]
    filename = secure_filename(file.filename)
    ext      = filename.rsplit(".", 1)[1].lower()
    saved_path = os.path.join(config.UPLOAD_FOLDER, f"{job_id}_{filename}")
    file.save(saved_path)

    # ── PDF → image conversion ─────────────────────────────────────────────────
    image_path = saved_path
    if ext == "pdf":
        try:
            image_path = pdf_to_image(saved_path, config.UPLOAD_FOLDER, job_id)
        except Exception as e:
            return jsonify({"error": f"PDF conversion failed: {e}. Is Poppler installed?"}), 500

    # ── OCR pipeline ──────────────────────────────────────────────────────────
    try:
        ocr_result = run_ocr(image_path)
    except Exception as e:
        return jsonify({"error": f"OCR failed: {e}. Is Tesseract installed?"}), 500

    paragraphs = ocr_result["paragraphs"]

    # Language detection
    paragraphs = annotate_paragraphs(paragraphs)

    # Translation
    paragraphs = translate_paragraphs(paragraphs)

    # Ensure confidence is always present in API/JSON output.
    for para in paragraphs:
        para.setdefault("conf", None)

    # Annotate image with bounding boxes
    annotated_filename = f"{job_id}_annotated.jpg"
    annotated_path     = os.path.join(config.UPLOAD_FOLDER, annotated_filename)
    annotate_image(image_path, paragraphs, annotated_path)

    # ── Save JSON output ───────────────────────────────────────────────────────
    output_data = {
        "job_id":        job_id,
        "source_file":   filename,
        "image_size":    ocr_result["image_size"],
        "total_blocks":  len(paragraphs),
        "languages":     list({p["lang"]["name"] for p in paragraphs if p["lang"]["code"] != "unknown"}),
        "paragraphs":    paragraphs,
    }
    json_path = os.path.join(config.OUTPUT_FOLDER, f"{job_id}_result.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # ── Build translated PDF ───────────────────────────────────────────────────
    pdf_path = os.path.join(config.OUTPUT_FOLDER, f"{job_id}_translated.pdf")
    try:
        export_pdf(paragraphs, pdf_path, filename)
    except Exception as e:
        pdf_path = None

    return jsonify({
        "job_id":           job_id,
        "annotated_image":  f"/static/uploads/{annotated_filename}",
        "paragraphs":       paragraphs,
        "languages":        output_data["languages"],
        "total_blocks":     len(paragraphs),
        "download_json":    f"/download/json/{job_id}",
        "download_pdf":     f"/download/pdf/{job_id}" if pdf_path else None,
    })


@app.route("/download/json/<job_id>")
def download_json(job_id: str):
    path = os.path.join(config.OUTPUT_FOLDER, f"{job_id}_result.json")
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    return send_file(path, as_attachment=True,
                     download_name=f"polylingua_{job_id}.json")


@app.route("/download/pdf/<job_id>")
def download_pdf(job_id: str):
    path = os.path.join(config.OUTPUT_FOLDER, f"{job_id}_translated.pdf")
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    return send_file(path, as_attachment=True,
                     download_name=f"polylingua_{job_id}_translated.pdf")


@app.route("/back_translate", methods=["POST"])
def back_translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    target_lang = str(data.get("target_lang", "")).lower().strip()

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Invalid text"}), 400

    if target_lang not in SUPPORTED_BACK_TRANSLATE_LANGS:
        return jsonify({"error": "Unsupported target language"}), 400

    try:
        translator = Translator()
        translated = translator.translate(text, src="en", dest=target_lang)
        if inspect.isawaitable(translated):
            translated = asyncio.run(translated)
        translated_text = getattr(translated, "text", None)
        if not translated_text:
            raise RuntimeError("Empty translation result")
        return jsonify({"translated_text": translated_text})
    except Exception:
        return jsonify({"error": "Translation failed"}), 500


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
