# Базовый образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости для Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории для логов
RUN mkdir -p /app/logs

# Экспонируем порт для webhook
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"] 