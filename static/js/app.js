/* ─────────────────────────────────────────────────────────────────────────────
   PolyLingua OCR — app.js
───────────────────────────────────────────────────────────────────────────── */

'use strict';

// ── DOM refs ─────────────────────────────────────────────────────────────────
const dropZone        = document.getElementById('drop-zone');
const fileInput       = document.getElementById('file-input');
const uploadSection   = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const progressStep    = document.getElementById('progress-step');
const progressBar     = document.getElementById('progress-bar');
const errorBanner     = document.getElementById('error-banner');
const errorMsg        = document.getElementById('error-msg');
const resultsSection  = document.getElementById('results-section');
const resultsMeta     = document.getElementById('results-meta');
const langSummary     = document.getElementById('lang-summary');
const blocksList      = document.getElementById('blocks-list');
const blocksCount     = document.getElementById('blocks-count');
const annotatedImg    = document.getElementById('annotated-img');
const btnJson         = document.getElementById('btn-json');
const btnPdf          = document.getElementById('btn-pdf');
const btnReset        = document.getElementById('btn-reset');

// ── State ─────────────────────────────────────────────────────────────────────
let currentJobId   = null;
let downloadJsonUrl = null;
let downloadPdfUrl  = null;

// ── Progress simulation steps ─────────────────────────────────────────────────
const STEPS = [
  { pct: 15,  label: 'Running Tesseract OCR engine…' },
  { pct: 35,  label: 'Detecting script & language…' },
  { pct: 60,  label: 'Translating text to English…' },
  { pct: 80,  label: 'Drawing bounding box overlay…' },
  { pct: 92,  label: 'Generating PDF report…' },
  { pct: 99,  label: 'Finalising output…' },
];

const LANG_CODE_TO_NAME = {
  ar: 'Arabic',
  'zh-cn': 'Chinese (Simplified)',
  'zh-tw': 'Chinese (Traditional)',
  zh: 'Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  hi: 'Hindi (Devanagari)',
  ru: 'Russian (Cyrillic)',
  en: 'English',
  de: 'German',
  fr: 'French',
  es: 'Spanish',
  it: 'Italian',
  pt: 'Portuguese',
  unknown: 'Unknown',
};

function readableLangName(code, fallbackName = 'Unknown') {
  const key = String(code || 'unknown').toLowerCase();
  return LANG_CODE_TO_NAME[key] || fallbackName || key.toUpperCase();
}

// ── Drag & Drop ───────────────────────────────────────────────────────────────
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

dropZone.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') fileInput.click();
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

// ── Download Buttons ──────────────────────────────────────────────────────────
btnJson.addEventListener('click', () => {
  if (downloadJsonUrl) window.location.href = downloadJsonUrl;
});

btnPdf.addEventListener('click', () => {
  if (downloadPdfUrl) window.location.href = downloadPdfUrl;
});

btnReset.addEventListener('click', resetUI);

// ── Main Upload Handler ───────────────────────────────────────────────────────
async function handleFile(file) {
  const allowed = ['image/png','image/jpeg','image/webp','image/bmp',
                   'image/tiff','application/pdf'];
  if (!allowed.includes(file.type) && !file.name.match(/\.(tif|tiff|pdf)$/i)) {
    showError('Unsupported file type. Please upload PNG, JPG, WEBP, BMP, TIFF or PDF.');
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    showError('File too large. Maximum size is 16 MB.');
    return;
  }

  // Reset state
  hideError();
  showProgress();

  // Simulate progress while waiting for server
  const stepTimer = simulateProgress();

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('/upload', { method: 'POST', body: formData });
    clearInterval(stepTimer);

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Server error: ${response.status}`);
    }

    const data = await response.json();
    setProgress(100, 'Done!');

    setTimeout(() => showResults(data, file.name), 350);

  } catch (err) {
    clearInterval(stepTimer);
    hideProgress();
    showError(err.message || 'An unexpected error occurred. Please try again.');
  }
}

// ── Progress ──────────────────────────────────────────────────────────────────
function simulateProgress() {
  let idx = 0;
  setProgress(5, STEPS[0].label);
  const timer = setInterval(() => {
    if (idx < STEPS.length) {
      const step = STEPS[idx++];
      setProgress(step.pct, step.label);
    }
  }, 1800);
  return timer;
}

function setProgress(pct, label) {
  progressBar.style.width = `${pct}%`;
  progressStep.textContent = label;
}

function showProgress() {
  uploadSection.classList.add('hidden');
  progressSection.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  setProgress(0, 'Uploading file…');
}

function hideProgress() {
  progressSection.classList.add('hidden');
  uploadSection.classList.remove('hidden');
}

// ── Results ───────────────────────────────────────────────────────────────────
function showResults(data, filename) {
  progressSection.classList.add('hidden');
  resultsSection.classList.remove('hidden');

  currentJobId = data.job_id;
  downloadJsonUrl = data.download_json;
  downloadPdfUrl  = data.download_pdf;

  // Meta line
  resultsMeta.textContent =
    `${data.total_blocks} blocks · ${data.languages.join(', ') || 'Unknown language'} · ${filename}`;

  // Language chips
  langSummary.innerHTML = '';
  if (data.languages && data.languages.length) {
    data.languages.forEach(lang => {
      const para = data.paragraphs.find(p => p.lang?.name === lang);
      const color = para?.lang?.color || '#6366f1';
      const name = readableLangName(para?.lang?.code, lang);
      const chip = document.createElement('span');
      chip.className = 'lang-chip';
      chip.style.setProperty('--c', color);
      chip.textContent = name;
      langSummary.appendChild(chip);
    });
  }

  // Annotated image
  annotatedImg.src = data.annotated_image + '?t=' + Date.now();
  annotatedImg.alt = `Annotated ${filename}`;

  // Blocks
  blocksCount.textContent = `${data.total_blocks} block${data.total_blocks !== 1 ? 's' : ''}`;
  blocksList.innerHTML = '';
  data.paragraphs.forEach((para, idx) => buildBlockCard(para, idx));

  // Download buttons
  btnJson.disabled = !downloadJsonUrl;
  btnPdf.disabled  = !downloadPdfUrl;
}

function buildBlockCard(para, idx) {
  const card = document.createElement('div');
  card.className = 'block-card';
  card.style.animationDelay = `${idx * 40}ms`;

  const langColor = para.lang?.color || '#6366f1';
  const langName  = readableLangName(para.lang?.code, para.lang?.name || 'Unknown');
  const origText  = para.text        || '';
  const transText = para.translation || origText;

  card.innerHTML = `
    <div class="block-header">
      <span class="block-num">#${idx + 1}</span>
      <span class="block-lang-badge" style="--c:${langColor}">${langName}</span>
      <span class="block-conf">conf: ${avgConf(para)}%</span>
    </div>
    <div class="block-label">Original Text</div>
    <div class="block-text" lang="und">${escHtml(origText)}</div>
    <div class="block-label">English Translation</div>
    <div class="block-translation">${escHtml(transText)}</div>
  `;

  blocksList.appendChild(card);
}

function avgConf(para) {
  return para.conf ?? '—';
}

// ── Error ─────────────────────────────────────────────────────────────────────
function showError(msg) {
  errorMsg.textContent = msg;
  errorBanner.classList.remove('hidden');
  uploadSection.classList.remove('hidden');
}

function hideError() {
  errorBanner.classList.add('hidden');
}

// ── Reset ─────────────────────────────────────────────────────────────────────
function resetUI() {
  resultsSection.classList.add('hidden');
  errorBanner.classList.add('hidden');
  uploadSection.classList.remove('hidden');
  blocksList.innerHTML = '';
  langSummary.innerHTML = '';
  fileInput.value = '';
  currentJobId = null;
  downloadJsonUrl = null;
  downloadPdfUrl = null;
}

// ── Utility ───────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
