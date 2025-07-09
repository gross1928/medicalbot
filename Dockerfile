# Этап 1: Сборка с зависимостями
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем переменные окружения для Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы проекта и устанавливаем зависимости
# Это кэшируется, если файлы не менялись
COPY pyproject.toml poetry.lock* ./
# Добавляем . для поддержки старых версий poetry.lock
RUN poetry install --no-dev --no-root

# Этап 2: Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем переменные окружения для запуска
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8080

# Копируем виртуальное окружение со всеми зависимостями из сборщика
COPY --from=builder /app/.venv ./.venv

# Копируем исходный код приложения
COPY . .

# Открываем порт, который Railway будет использовать
EXPOSE 8080

# Команда для запуска приложения
# Uvicorn автоматически будет слушать на $PORT, если он установлен Railway
CMD ["uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "8080", "--factory"] 