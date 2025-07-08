-- ============================================
-- УПРОЩЕННАЯ СХЕМА БД ДЛЯ МЕДИЦИНСКОГО ИИ-АНАЛИЗАТОРА
-- Версия без сложных политик RLS
-- ============================================

-- 1. ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ
CREATE TABLE users (
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

-- 2. ТАБЛИЦА АНАЛИЗОВ
CREATE TABLE analyses (
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

-- 3. ТАБЛИЦА РЕЗУЛЬТАТОВ БИОМАРКЕРОВ
CREATE TABLE results (
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

-- 4. ТАБЛИЦА РЕКОМЕНДАЦИЙ
CREATE TABLE recommendations (
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

-- 5. ТАБЛИЦА МЕДИЦИНСКИХ НОРМ
CREATE TABLE medical_norms (
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