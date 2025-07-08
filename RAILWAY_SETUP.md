# 🚀 Настройка Railway для Медицинского ИИ-Анализатора

## Переменные окружения для Railway

Для деплоя на Railway необходимо настроить следующие переменные окружения:

### 🔐 Обязательные переменные

#### Telegram Bot
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```
- Получите токен от [@BotFather](https://t.me/BotFather) в Telegram
- Команда: `/newbot` → выберите имя → скопируйте токен

#### OpenAI API
```
OPENAI_API_KEY=your_openai_api_key_here
```
- Получите на [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Убедитесь, что у вас есть кредиты на аккаунте

#### Supabase Database
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```
- Создайте проект на [supabase.com](https://supabase.com)
- Перейдите в Settings → API
- Скопируйте URL, anon key и service_role key

#### Security
```
SECRET_KEY=your_random_secret_key_minimum_32_characters
```
- Генерируйте случайный ключ длиной минимум 32 символа
- Можно использовать: `openssl rand -hex 32`

### ⚙️ Конфигурационные переменные

#### Application Settings
```
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
```

#### Webhook URL
```
TELEGRAM_WEBHOOK_URL=https://your-railway-app.railway.app
```
- Railway автоматически предоставит URL после деплоя
- Формат: `https://medicalbot-production-xxxx.up.railway.app`

### 📊 Опциональные переменные

#### OpenAI Configuration
```
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
```

#### File Processing
```
MAX_FILE_SIZE_MB=20
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png
OCR_LANGUAGE=rus+eng
```

#### Monitoring
```
LOG_LEVEL=INFO
SENTRY_DSN=your_sentry_dsn_if_needed
```

#### Rate Limiting
```
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100
```

#### AI Analysis
```
AI_ANALYSIS_TIMEOUT=120
MAX_BIOMARKERS_PER_ANALYSIS=50
CACHE_ANALYSIS_HOURS=24
```

## 🔧 Пошаговая настройка Railway

### 1. Создание проекта Railway
1. Войдите на [railway.app](https://railway.app)
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Подключите репозиторий `https://github.com/gross1928/medicalbot.git`

### 2. Настройка переменных окружения
1. В панели Railway откройте ваш проект
2. Перейдите на вкладку "Variables"
3. Добавьте все обязательные переменные из списка выше

### 3. Настройка Supabase
1. Создайте проект на [supabase.com](https://supabase.com)
2. Выполните SQL для создания таблиц:

```sql
-- Пользователи
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER CHECK (age > 0 AND age <= 150),
    gender VARCHAR(10),
    weight FLOAT CHECK (weight > 0),
    height FLOAT CHECK (height > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Анализы
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    extracted_text TEXT,
    ocr_confidence FLOAT,
    processing_result JSONB,
    analysis_summary TEXT,
    processing_time_seconds FLOAT,
    ai_tokens_used INTEGER,
    error_message TEXT
);

-- Результаты биомаркеров
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    unit VARCHAR(50),
    reference_range VARCHAR(255),
    status VARCHAR(20) DEFAULT 'unknown',
    interpretation TEXT,
    numeric_value FLOAT,
    normal_min FLOAT,
    normal_max FLOAT,
    clinical_significance TEXT,
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Рекомендации
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    biomarker_name VARCHAR(255),
    target_value VARCHAR(255),
    timeline VARCHAR(255),
    action_items JSONB,
    resources JSONB,
    confidence_score FLOAT,
    scientific_basis TEXT,
    contraindications TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_personalized BOOLEAN DEFAULT TRUE
);

-- Медицинские нормы
CREATE TABLE medical_norms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    biomarker_name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    min_value FLOAT,
    max_value FLOAT,
    gender VARCHAR(10) DEFAULT 'BOTH',
    age_min INTEGER,
    age_max INTEGER,
    source VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

3. Создайте bucket "medical-files" в Storage:
   - Перейдите в Storage
   - Нажмите "Create bucket"
   - Имя: `medical-files`
   - Public: `false`

### 4. Настройка Telegram Webhook
После деплоя на Railway получите URL приложения и настройте webhook:
```
TELEGRAM_WEBHOOK_URL=https://your-app-name.up.railway.app
```

### 5. Проверка деплоя
1. Railway автоматически запустит билд из Dockerfile
2. Проверьте логи в Railway консоли
3. Убедитесь, что приложение запустилось без ошибок
4. Протестируйте бота в Telegram

## 🚨 Важные моменты

### Безопасность
- ⚠️ Никогда не коммитьте `.env` файлы в Git
- ⚠️ Используйте сильные секретные ключи
- ⚠️ Service Role Key держите в секрете

### Мониторинг
- Следите за использованием OpenAI API
- Контролируйте размер файлов в Supabase Storage
- Настройте уведомления об ошибках

### Лимиты
- OpenAI: зависит от вашего плана
- Supabase: 500MB базы данных на бесплатном плане
- Railway: зависит от выбранного плана

## 📞 Поддержка
Если возникли проблемы при настройке:
1. Проверьте логи в Railway консоли
2. Убедитесь, что все переменные окружения заданы правильно
3. Проверьте подключение к Supabase
4. Протестируйте OpenAI API ключ 