-- ============================================
-- ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ БАЗЫ ДАННЫХ
-- Выполните ПОСЛЕ создания таблиц
-- ============================================

-- Индексы для пользователей
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_active ON users(is_active);

-- Индексы для анализов
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_uploaded_at ON analyses(uploaded_at);

-- Индексы для результатов
CREATE INDEX idx_results_analysis_id ON results(analysis_id);
CREATE INDEX idx_results_name ON results(name);
CREATE INDEX idx_results_status ON results(status);

-- Индексы для рекомендаций
CREATE INDEX idx_recommendations_analysis_id ON recommendations(analysis_id);
CREATE INDEX idx_recommendations_category ON recommendations(category);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);

-- Индексы для медицинских норм
CREATE INDEX idx_medical_norms_biomarker ON medical_norms(biomarker_name);
CREATE INDEX idx_medical_norms_active ON medical_norms(is_active);
CREATE INDEX idx_medical_norms_gender_age ON medical_norms(gender, age_min, age_max); 