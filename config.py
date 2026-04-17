import os

# ── Tesseract binary path ─────────────────────────────────────────────────────
# Default Windows install path. Update if you installed to a different location.
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── Tesseract language pack string ───────────────────────────────────────────
# Covers: English, Arabic, Chinese Simplified, Japanese, Korean, Hindi (Devanagari), Russian (Cyrillic)
# NOTE: Hindi/Devanagari = 'hin'  (NOT 'san' which is Sanskrit)
TESS_LANGS = "eng+ara+chi_sim+jpn+kor+hin+rus"

# ── Poppler path (required for PDF-to-image conversion) ──────────────────────
# Update this path to match WHERE you extracted Poppler on your machine.
# Common locations after extraction:
#   C:\poppler\Library\bin          ← if you extracted to C:\poppler\
#   C:\poppler-24.x.x\Library\bin  ← version-specific folder name
# Set to None to let pdf2image search your system PATH instead.
POPPLER_PATH = r"C:\Fusion Fest\Release-25.12.0-0\poppler-25.12.0\Library\bin"

# ── File handling ─────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
ALLOWED_EXTS  = {"png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff", "pdf"}

# ── Max upload size (16 MB) ──────────────────────────────────────────────────
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# ── Create directories if they don't exist ────────────────────────────────────
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ── Startup checks ────────────────────────────────────────────────────────────
if not os.path.isfile(TESSERACT_CMD):
    print(f"\n⚠️  WARNING: Tesseract not found at: {TESSERACT_CMD}")
    print("   Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
    print("   or update TESSERACT_CMD in config.py\n")

if POPPLER_PATH and not os.path.isdir(POPPLER_PATH):
    print(f"\n⚠️  WARNING: Poppler not found at: {POPPLER_PATH}")
    print("   PDF uploads will fail until Poppler is installed.")
    print("   Download from https://github.com/oschwartz10612/poppler-windows/releases")
    print("   Then update POPPLER_PATH in config.py to point to the 'Library\\bin' folder.\n")
