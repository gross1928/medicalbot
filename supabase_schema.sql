-- ============================================
-- СХЕМА БАЗЫ ДАННЫХ ДЛЯ МЕДИЦИНСКОГО ИИ-АНАЛИЗАТОРА
-- Выполните этот скрипт в Supabase SQL Editor
-- ============================================

-- 1. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER CHECK (age > 0 AND age <= 150),
    gender VARCHAR(10) CHECK (gender IN ('M', 'F')),
    weight FLOAT CHECK (weight > 0 AND weight <= 500),
    height FLOAT CHECK (height > 50 AND height <= 250),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Индексы для пользователей
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- 2. ТАБЛИЦА АНАЛИЗОВ
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(1000) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'jpg', 'jpeg', 'png')),
    file_size INTEGER NOT NULL CHECK (file_size > 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'uploading', 'processing', 'analyzing', 'completed', 'failed', 'error')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    extracted_text TEXT,
    ocr_confidence FLOAT CHECK (ocr_confidence >= 0 AND ocr_confidence <= 1),
    processing_result JSONB,
    analysis_summary TEXT,
    processing_time_seconds FLOAT CHECK (processing_time_seconds >= 0),
    ai_tokens_used INTEGER CHECK (ai_tokens_used >= 0),
    error_message TEXT
);

-- Индексы для анализов
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_uploaded_at ON analyses(uploaded_at);

-- 3. ТАБЛИЦА РЕЗУЛЬТАТОВ БИОМАРКЕРОВ
CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    unit VARCHAR(50),
    reference_range VARCHAR(255),
    status VARCHAR(20) DEFAULT 'unknown' CHECK (status IN ('normal', 'low', 'high', 'critical_low', 'critical_high', 'unknown')),
    interpretation TEXT,
    numeric_value FLOAT,
    normal_min FLOAT,
    normal_max FLOAT,
    clinical_significance TEXT,
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для результатов
CREATE INDEX IF NOT EXISTS idx_results_analysis_id ON results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_results_name ON results(name);
CREATE INDEX IF NOT EXISTS idx_results_status ON results(status);

-- 4. ТАБЛИЦА РЕКОМЕНДАЦИЙ
CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('nutrition', 'exercise', 'lifestyle', 'supplements', 'medical', 'monitoring', 'general')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    biomarker_name VARCHAR(255),
    target_value VARCHAR(255),
    timeline VARCHAR(255),
    action_items JSONB,
    resources JSONB,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    scientific_basis TEXT,
    contraindications TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_personalized BOOLEAN DEFAULT TRUE
);

-- Индексы для рекомендаций
CREATE INDEX IF NOT EXISTS idx_recommendations_analysis_id ON recommendations(analysis_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_category ON recommendations(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_priority ON recommendations(priority);

-- 5. ТАБЛИЦА МЕДИЦИНСКИХ НОРМ
CREATE TABLE IF NOT EXISTS medical_norms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    biomarker_name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    min_value FLOAT,
    max_value FLOAT,
    gender VARCHAR(10) DEFAULT 'BOTH' CHECK (gender IN ('M', 'F', 'BOTH')),
    age_min INTEGER CHECK (age_min >= 0 AND age_min <= 150),
    age_max INTEGER CHECK (age_max >= 0 AND age_max <= 150),
    source VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1 CHECK (version > 0)
);

-- Индексы для медицинских норм
CREATE INDEX IF NOT EXISTS idx_medical_norms_biomarker ON medical_norms(biomarker_name);
CREATE INDEX IF NOT EXISTS idx_medical_norms_active ON medical_norms(is_active);
CREATE INDEX IF NOT EXISTS idx_medical_norms_gender_age ON medical_norms(gender, age_min, age_max);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Включаем RLS для всех таблиц
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE results ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_norms ENABLE ROW LEVEL SECURITY;

-- Политики безопасности (базовые - можно настроить под свои нужды)

-- Пользователи: доступ только к своим данным
CREATE POLICY IF NOT EXISTS "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY IF NOT EXISTS "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Анализы: доступ только к своим анализам
CREATE POLICY IF NOT EXISTS "Users can view own analyses" ON analyses
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY IF NOT EXISTS "Users can insert own analyses" ON analyses
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

-- Результаты: доступ через анализы
CREATE POLICY IF NOT EXISTS "Users can view own results" ON results
    FOR SELECT USING (
        analysis_id IN (
            SELECT id FROM analyses WHERE user_id::text = auth.uid()::text
        )
    );

-- Рекомендации: доступ через анализы
CREATE POLICY IF NOT EXISTS "Users can view own recommendations" ON recommendations
    FOR SELECT USING (
        analysis_id IN (
            SELECT id FROM analyses WHERE user_id::text = auth.uid()::text
        )
    );

-- Медицинские нормы: доступ всем для чтения
CREATE POLICY IF NOT EXISTS "Medical norms are readable by all" ON medical_norms
    FOR SELECT USING (is_active = true);

-- ============================================
-- БАЗОВЫЕ ДАННЫЕ (МЕДИЦИНСКИЕ НОРМЫ)
-- ============================================

INSERT INTO medical_norms (biomarker_name, unit, min_value, max_value, gender, age_min, age_max, source, notes) VALUES
-- Общий анализ крови
('Гемоглобин', 'г/л', 120, 140, 'F', 18, 150, 'ВОЗ', 'Норма для женщин'),
('Гемоглобин', 'г/л', 130, 160, 'M', 18, 150, 'ВОЗ', 'Норма для мужчин'),
('Эритроциты', '×10¹²/л', 3.8, 4.5, 'F', 18, 150, 'ВОЗ', 'Норма для женщин'),
('Эритроциты', '×10¹²/л', 4.0, 5.1, 'M', 18, 150, 'ВОЗ', 'Норма для мужчин'),
('Лейкоциты', '×10⁹/л', 4.0, 9.0, 'BOTH', 18, 150, 'ВОЗ', 'Общая норма'),
('Тромбоциты', '×10⁹/л', 150, 400, 'BOTH', 18, 150, 'ВОЗ', 'Общая норма'),

-- Биохимический анализ
('Глюкоза', 'ммоль/л', 3.3, 5.5, 'BOTH', 18, 150, 'АДА', 'Норма натощак'),
('Холестерин общий', 'ммоль/л', 3.0, 5.2, 'BOTH', 18, 150, 'ESC/EAS', 'Желательный уровень'),
('Билирубин общий', 'мкмоль/л', 5.0, 21.0, 'BOTH', 18, 150, 'ВОЗ', 'Общая норма'),
('АЛТ', 'Ед/л', 0, 40, 'BOTH', 18, 150, 'ВОЗ', 'Аланинаминотрансфераза'),
('АСТ', 'Ед/л', 0, 40, 'BOTH', 18, 150, 'ВОЗ', 'Аспартатаминотрансфераза'),
('Креатинин', 'мкмоль/л', 62, 106, 'F', 18, 150, 'KDIGO', 'Норма для женщин'),
('Креатинин', 'мкмоль/л', 80, 115, 'M', 18, 150, 'KDIGO', 'Норма для мужчин'),
('Мочевина', 'ммоль/л', 2.5, 8.3, 'BOTH', 18, 150, 'ВОЗ', 'Общая норма'),

-- Гормоны щитовидной железы
('ТТГ', 'мЕд/л', 0.4, 4.0, 'BOTH', 18, 150, 'ATA', 'Тиреотропный гормон'),
('Т4 свободный', 'пмоль/л', 9.0, 22.0, 'BOTH', 18, 150, 'ATA', 'Свободный тироксин'),
('Т3 свободный', 'пмоль/л', 2.6, 5.7, 'BOTH', 18, 150, 'ATA', 'Свободный трийодтиронин'),

-- Витамины и микроэлементы
('Витамин D', 'нг/мл', 30, 100, 'BOTH', 18, 150, 'IOM', 'Оптимальный уровень'),
('Витамин B12', 'пг/мл', 200, 900, 'BOTH', 18, 150, 'ВОЗ', 'Общая норма'),
('Ферритин', 'нг/мл', 15, 150, 'F', 18, 50, 'ВОЗ', 'Норма для женщин репродуктивного возраста'),
('Ферритин', 'нг/мл', 15, 400, 'M', 18, 150, 'ВОЗ', 'Норма для мужчин'),

-- Липидный профиль
('ЛПНП', 'ммоль/л', 0, 3.0, 'BOTH', 18, 150, 'ESC/EAS', 'Желательный уровень'),
('ЛПВП', 'ммоль/л', 1.2, 9999, 'F', 18, 150, 'ESC/EAS', 'Минимальный уровень для женщин'),
('ЛПВП', 'ммоль/л', 1.0, 9999, 'M', 18, 150, 'ESC/EAS', 'Минимальный уровень для мужчин'),
('Триглицериды', 'ммоль/л', 0, 1.7, 'BOTH', 18, 150, 'ESC/EAS', 'Желательный уровень')

ON CONFLICT (biomarker_name, gender, age_min, age_max) DO NOTHING;

-- ============================================
-- ФУНКЦИИ И ТРИГГЕРЫ
-- ============================================

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_medical_norms_updated_at BEFORE UPDATE ON medical_norms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ГОТОВО!
-- ============================================

-- Проверяем созданные таблицы
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'analyses', 'results', 'recommendations', 'medical_norms')
ORDER BY table_name, ordinal_position; 