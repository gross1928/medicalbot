# Базовый образ Python
FROM python:3.11-slim

# Метаданные
LABEL maintainer="Medical AI Bot"
LABEL version="1.0"

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Обновляем систему и устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    # Основные утилиты
    curl \
    gcc \
    g++ \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libtesseract-dev \
    # PDF обработка
    poppler-utils \
    # Очистка
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip setuptools wheel

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости с подробным выводом
RUN pip install --no-cache-dir -r requirements.txt --verbose

# Копируем исходный код
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/logs /app/uploads /app/temp

# Устанавливаем права доступа
RUN chmod +x /app

# Экспонируем порт для webhook
EXPOSE 8000

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Команда запуска
CMD ["python", "main.py"] 