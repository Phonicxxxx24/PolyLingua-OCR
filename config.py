import os

# ── Runtime environment detection ─────────────────────────────────────────────
IS_WINDOWS = os.name == "nt"

# ── Tesseract binary path ─────────────────────────────────────────────────────
# Priority:
# 1) TESSERACT_CMD environment variable
# 2) Windows default path
# 3) Linux container/system default path
TESSERACT_CMD = os.getenv("TESSERACT_CMD") or (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe" if IS_WINDOWS else "/usr/bin/tesseract"
)

# ── Tesseract language pack string ───────────────────────────────────────────
# Covers: English, Arabic, Chinese Simplified, Japanese, Korean, Hindi (Devanagari), Russian (Cyrillic)
# NOTE: Hindi/Devanagari = 'hin'  (NOT 'san' which is Sanskrit)
TESS_LANGS = "eng+ara+chi_sim+jpn+kor+hin+rus"

# ── Poppler path (required for PDF-to-image conversion) ──────────────────────
# Priority:
# 1) POPPLER_PATH environment variable (set empty to disable explicit path)
# 2) Windows local extraction path
# 3) None on Linux/container so pdf2image uses PATH
_poppler_env = os.getenv("POPPLER_PATH")
if _poppler_env is not None:
    POPPLER_PATH = _poppler_env.strip() or None
elif IS_WINDOWS:
    POPPLER_PATH = r"C:\Fusion Fest\Release-25.12.0-0\poppler-25.12.0\Library\bin"
else:
    POPPLER_PATH = None

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
    print(f"\nWARNING: Tesseract not found at: {TESSERACT_CMD}")
    print("   Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
    print("   or update TESSERACT_CMD in config.py\n")

if POPPLER_PATH and not os.path.isdir(POPPLER_PATH):
    print(f"\nWARNING: Poppler not found at: {POPPLER_PATH}")
    print("   PDF uploads will fail until Poppler is installed.")
    print("   Download from https://github.com/oschwartz10612/poppler-windows/releases")
    print("   Then update POPPLER_PATH in config.py to point to the 'Library\\bin' folder.\n")
