# 🏥 Медицинский ИИ Анализатор - Telegram Bot

> **Статус**: ✅ **ГОТОВ К ДЕПЛОЮ** | **Версия**: 1.0.0 | **Дата**: 14.12.2024

Полнофункциональный Telegram бот для анализа медицинских результатов с использованием искусственного интеллекта OpenAI GPT-4.

## 🎯 Основные возможности

- 📱 **Telegram интерфейс** - удобное взаимодействие через мессенджер
- 🤖 **ИИ анализ** - интерпретация медицинских показателей с помощью GPT-4
- 📄 **Обработка файлов** - поддержка PDF, JPG, PNG до 20MB с OCR
- 💾 **Надежное хранение** - Supabase PostgreSQL + Storage  
- 🔒 **Безопасность** - валидация данных, медицинские дисклеймеры
- 📊 **Мониторинг** - структурированное логирование
- 🚀 **Railway готовность** - Docker контейнер для быстрого деплоя

## 🛠 Технологический стек

- **Backend**: Python 3.11+ + FastAPI
- **Bot Framework**: python-telegram-bot v20+
- **AI/ML**: OpenAI GPT-4 API
- **Database**: Supabase (PostgreSQL + Storage)
- **OCR**: Tesseract (русский + английский)
- **Deployment**: Railway.app + Docker
- **Monitoring**: Structured logging

## 🚀 Быстрый старт (5 минут)

### 1. Настройка Supabase

1. Создайте проект на [supabase.com](https://supabase.com)
2. Перейдите в Settings > API и скопируйте:
   - `Project URL`
   - `anon public key`
   - `service_role key`
3. Создайте bucket "medical-files" в Storage:
   ```sql
   -- В SQL Editor выполните:
   INSERT INTO storage.buckets (id, name, public) VALUES ('medical-files', 'medical-files', false);
   ```

### 2. Получение API ключей

1. **Telegram Bot Token**:
   - Напишите [@BotFather](https://t.me/BotFather)
   - Выполните `/newbot`
   - Скопируйте токен

2. **OpenAI API Key**:
   - Регистрация на [platform.openai.com](https://platform.openai.com)
   - Create API Key
   - Пополните баланс ($5+ для начала)

### 3. Деплой на Railway

1. Форкните этот репозиторий в GitHub
2. Перейдите на [railway.app](https://railway.app)
3. "New Project" > "Deploy from GitHub repo"
4. Выберите ваш fork
5. Добавьте переменные окружения:

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
SECRET_KEY=your_random_secret_key_32_chars
WEBHOOK_URL=https://your-railway-app.up.railway.app
```

6. Деплой произойдет автоматически!

## 📱 Команды бота

- `/start` - Начать работу с ботом
- `/help` - Справка по использованию
- `/profile` - Личный профиль и настройки
- `/history` - История анализов
- **Отправка файла** - загрузите медицинский анализ для обработки

## 🔧 Локальная разработка

### Требования

- Python 3.11+
- Tesseract OCR
- Git

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/medical-ai-bot.git
cd medical-ai-bot

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cp .env.example .env
# Заполните переменные окружения
```

### Переменные окружения (.env)

```bash
# Обязательные
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
SECRET_KEY=your_random_secret_key

# Опциональные
WEBHOOK_URL=https://your-domain.com  # Для webhook режима
PORT=8000
LOG_LEVEL=INFO
OCR_LANGUAGE=rus+eng
DEBUG=True
```

### Запуск

```bash
# Режим polling (для разработки)
python main.py

# Режим webhook (для продакшна)
python -m src.api.webapp
```

## 📁 Структура проекта

```
medical-bot/
├── 📄 main.py                    # Точка входа (polling режим)
├── 📄 requirements.txt           # Python зависимости (27 пакетов)
├── 📄 Dockerfile                 # Railway контейнер
├── 📄 railway.json              # Railway конфигурация
├── 📄 README.md                 # Документация
├── 📄 tasks.md                  # Отчет о разработке
├── 📁 config/
│   └── 📄 settings.py           # Pydantic настройки
├── 📁 src/
│   ├── 📁 models/               # Pydantic модели данных
│   │   ├── user.py              # Пользователи
│   │   ├── analysis.py          # Анализы
│   │   ├── biomarker.py         # Биомаркеры
│   │   ├── recommendation.py    # Рекомендации
│   │   └── medical_norm.py      # Медицинские нормы
│   ├── 📁 database/             # Supabase интеграция
│   │   ├── client.py            # Клиент подключения
│   │   └── repositories.py      # CRUD операции
│   ├── 📁 bot/                  # Telegram бот
│   │   ├── bot.py               # Основной класс бота
│   │   └── handlers.py          # Обработчики команд
│   ├── 📁 ai/                   # OpenAI интеграция
│   │   ├── analyzer.py          # ИИ анализатор
│   │   └── prompts.py           # Промпты для GPT-4
│   ├── 📁 file_processing/      # Обработка файлов
│   │   ├── processor.py         # Основной процессор
│   │   ├── ocr.py               # OCR с Tesseract
│   │   └── storage.py           # Supabase Storage
│   ├── 📁 utils/                # Утилиты
│   │   ├── logging_config.py    # Настройка логирования
│   │   └── medical_data.py      # Медицинские справочники
│   └── 📁 api/                  # FastAPI webhook
│       └── webapp.py            # Веб-приложение
└── 📁 tests/                    # Тесты
    ├── __init__.py
    └── test_basic.py            # Базовые тесты
```

## 🧪 Тестирование

```bash
# Базовые тесты импортов
python tests/test_basic.py

# Проверка основных компонентов
python -c "
import os
os.environ.update({
    'TELEGRAM_BOT_TOKEN': 'test',
    'OPENAI_API_KEY': 'test',
    'SUPABASE_URL': 'https://test.co',
    'SUPABASE_ANON_KEY': 'test',
    'SUPABASE_SERVICE_ROLE_KEY': 'test',
    'SECRET_KEY': 'test'
})
from config.settings import settings
from src.utils.medical_data import MedicalDataHelper
print('✅ Все модули работают!')
"
```

## 📊 Медицинские возможности

### Поддерживаемые анализы

- **Общий анализ крови**: гемоглобин, эритроциты, лейкоциты, тромбоциты, СОЭ
- **Биохимия крови**: глюкоза, холестерин (общий, ЛПВП, ЛПНП), триглицериды, АЛТ, АСТ, креатинин, мочевина
- **Гормоны**: ТТГ, Т4, Т3, инсулин, кортизол
- **Общий анализ мочи**: белок, глюкоза

### База знаний

- 📊 **Референсные значения** по полу и возрасту
- 🔍 **Интерпретация отклонений** с объяснениями
- 💡 **Персонализированные рекомендации**
- ⚕️ **Медицинские дисклеймеры** для безопасности

## 🔒 Безопасность

- ✅ **Валидация входных данных** с Pydantic
- ✅ **Проверка файлов** по magic bytes
- ✅ **Ограничения размеров** файлов (20MB)
- ✅ **Приватное хранилище** в Supabase
- ✅ **Медицинские предупреждения** в каждом ответе
- ✅ **Логирование действий** для аудита

## 💰 Стоимость использования

### OpenAI API (примерно)
- **Анализ одного файла**: ~$0.01-0.05
- **100 анализов в месяц**: ~$1-5
- **1000 анализов в месяц**: ~$10-50

### Railway hosting
- **Hobby план**: $5/месяц (достаточно для старта)
- **Pro план**: $20/месяц (для активного использования)

### Supabase
- **Free tier**: до 500MB storage, 50MB database
- **Pro план**: $25/месяц (больше лимитов)

## 📈 Масштабирование

### Оптимизация расходов
- ✅ Кэширование результатов анализов
- ✅ Оптимизированные промпты для ИИ
- ✅ Batch обработка файлов
- ✅ Monitoring использования API

### Улучшения функциональности
- 🔄 Добавление новых типов анализов
- 📱 Веб-интерфейс на React
- 🤖 Чат-бот для вопросов о здоровье
- 📊 Дашборд для врачей
- 🔗 Интеграция с носимыми устройствами

## ⚠️ Медицинские дисклеймеры

> **ВАЖНО**: Этот бот предоставляет информационные материалы и не заменяет консультацию врача. Все рекомендации носят справочный характер. При любых отклонениях в анализах обратитесь к квалифицированному медицинскому специалисту.

- 🩺 **Не заменяет врача** - только информационная поддержка
- 📋 **Не ставит диагнозы** - только интерпретация показателей  
- 💊 **Не назначает лечение** - только общие рекомендации
- 🚨 **При критических значениях** - немедленно к врачу

## 🤝 Поддержка и развитие

### Сообщить о проблеме
- 🐛 **GitHub Issues**: [создать issue](https://github.com/your-username/medical-ai-bot/issues)
- 📧 **Email**: your-email@example.com
- 💬 **Telegram**: [@your_username](https://t.me/your_username)

### Внести вклад
1. Fork репозитория
2. Создайте feature branch
3. Сделайте изменения
4. Создайте Pull Request

## 📝 Лицензия

MIT License - смотрите [LICENSE](LICENSE) для деталей.

## 🎉 Готово!

Ваш медицинский ИИ анализатор готов к работе! 

**Следующие шаги:**
1. ✅ Настроить Supabase проект
2. ✅ Получить API ключи
3. ✅ Задеплоить на Railway
4. ✅ Протестировать бота
5. 🚀 Начать использование!

---

*Разработано с ❤️ для улучшения доступности медицинской информации* 