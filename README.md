# PolyLingua OCR

PolyLingua OCR is a Flask web application for multilingual OCR, language detection, translation to English, optional back translation, annotated image output, JSON export, and translated PDF export.

## What It Does

- Accepts image and PDF uploads
- Converts PDF first page to image using Poppler
- Runs OCR with Tesseract using multilingual language packs
- Detects language per extracted block
- Translates extracted text to English
- Supports back translation from English to selected language
- Draws language colored annotations on the image
- Exports processing results as JSON
- Exports translated text as a clean PDF (translated text only)

## Tech Stack

- Backend: Flask
- OCR: Tesseract OCR via pytesseract
- PDF to image: pdf2image + Poppler
- Language detection: langdetect
- Translation: deep-translator and googletrans
- Image processing: Pillow
- PDF generation: ReportLab
- Frontend: HTML, CSS, JavaScript

## Architecture

```mermaid
flowchart TD
    A[Client Browser] --> B[/upload]
    B --> C[Save Uploaded File]
    C --> D{Is PDF?}
    D -- Yes --> E[Convert First Page with pdf2image and Poppler]
    D -- No --> F[Use Uploaded Image]
    E --> G[OCR Engine]
    F --> G[OCR Engine]
    G --> H[Language Detector]
    H --> I[Translator to English]
    I --> J[Annotate Image]
    I --> K[Build JSON Output]
    I --> L[Build Translated PDF]
    K --> M[/download/json/<job_id>]
    L --> N[/download/pdf/<job_id>]
    A --> O[/back_translate]
    O --> P[googletrans EN to Target]
    P --> A
```

## Runtime Flow

1. User uploads an image or PDF from the browser.
2. Backend saves the file under static/uploads.
3. If file is PDF, first page is converted to PNG with Poppler.
4. OCR extracts words and line grouped text blocks.
5. Noisy OCR blocks are filtered using confidence and quality rules.
6. Language is detected per block.
7. Each block is translated to English.
8. Annotated image, JSON, and translated PDF are generated.
9. Frontend renders extracted blocks, confidence, and translations.
10. Optional back translation can be requested per displayed block.

## Project Structure

```text
app.py
config.py
requirements.txt
modules/
  __init__.py
  image_processor.py
  language_detector.py
  ocr_engine.py
  pdf_exporter.py
  translator.py
outputs/
static/
  css/styles.css
  js/app.js
  uploads/
templates/
  index.html
```

## Prerequisites

- Python 3.10+ recommended
- Tesseract OCR installed on Windows
- Poppler for Windows installed for PDF support

### Windows local installs

Install the following once on your machine:

1. Python 3.11 or newer
2. Tesseract OCR (with language packs for ara, chi_sim, jpn, kor, hin, rus)
3. Poppler for Windows (for PDF input)

Then confirm your paths in [config.py](config.py).

## Configuration

Edit config.py:

- TESSERACT_CMD should point to tesseract.exe
- POPPLER_PATH should point to Poppler Library/bin
- TESS_LANGS should include installed Tesseract language packs

Example values:

- TESSERACT_CMD = C:\Program Files\Tesseract-OCR\tesseract.exe
- POPPLER_PATH = C:\Fusion Fest\Release-25.12.0-0\poppler-25.12.0\Library\bin
- TESS_LANGS = eng+ara+chi_sim+jpn+kor+hin+rus

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open:

- http://127.0.0.1:5000
