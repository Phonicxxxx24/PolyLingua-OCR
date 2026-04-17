FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ara \
    tesseract-ocr-chi-sim \
    tesseract-ocr-jpn \
    tesseract-ocr-kor \
    tesseract-ocr-hin \
    tesseract-ocr-rus \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

ENV PORT=10000 \
    TESSERACT_CMD=/usr/bin/tesseract \
    POPPLER_PATH=

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "2", "app:app"]
