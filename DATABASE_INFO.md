# 🗄️ НАСТРОЙКА БАЗЫ ДАННЫХ SUPABASE

## 🚨 ИСПРАВЛЕНИЕ ОШИБКИ СИНТАКСИСА

**Проблема:** Ошибка `IF NOT EXISTS` для политик RLS не поддерживается в некоторых версиях PostgreSQL.

**Решение:** Используйте упрощенные SQL скрипты в правильном порядке:

## 📋 ПОШАГОВАЯ НАСТРОЙКА

### Шаг 1: Создание таблиц
```sql
-- Выполните в SQL Editor Supabase
-- Файл: supabase_simple.sql
```

### Шаг 2: Создание индексов
```sql
-- Выполните ПОСЛЕ создания таблиц
-- Файл: supabase_indexes.sql
```

### Шаг 3: Загрузка данных
```sql
-- Выполните ПОСЛЕ создания таблиц и индексов
-- Файл: supabase_data.sql
```

## 🛠️ ИНСТРУКЦИЯ ПО ВЫПОЛНЕНИЮ

1. **Откройте Supabase Dashboard**
   - Перейдите в ваш проект
   - Выберите "SQL Editor"

2. **Выполните скрипты по порядку:**
   
   **a) Создание таблиц:**
   - Скопируйте содержимое `supabase_simple.sql`
   - Вставьте в SQL Editor
   - Нажмите "Run"

   **b) Создание индексов:**
   - Скопируйте содержимое `supabase_indexes.sql`
   - Вставьте в SQL Editor
   - Нажмите "Run"

   **c) Загрузка данных:**
   - Скопируйте содержимое `supabase_data.sql`
   - Вставьте в SQL Editor
   - Нажмите "Run"

## 📊 СТРУКТУРА БАЗЫ ДАННЫХ

### Таблицы:
- **users** - пользователи Telegram бота
- **analyses** - загруженные анализы
- **results** - результаты биомаркеров
- **recommendations** - рекомендации ИИ
- **medical_norms** - медицинские нормы

### Особенности:
- ✅ UUID для всех ID
- ✅ Внешние ключи с CASCADE
- ✅ Валидация данных через CHECK
- ✅ Индексы для оптимизации
- ✅ 40+ медицинских норм
- ✅ Поддержка гендерных и возрастных различий

## 🔧 КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ

Обновите `.env` файл:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 🧪 ПРОВЕРКА НАСТРОЙКИ

После выполнения всех скриптов проверьте:

```sql
-- Проверка таблиц
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Проверка медицинских норм
SELECT COUNT(*) FROM medical_norms;
-- Должно быть ~40 записей

-- Проверка индексов
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public';
```

## 🆘 ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Ошибка "relation already exists"
```sql
-- Удалите таблицы если нужно пересоздать
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS analyses CASCADE;
DROP TABLE IF EXISTS medical_norms CASCADE;
DROP TABLE IF EXISTS users CASCADE;
```

### Ошибка кодировки
- Убедитесь, что используете UTF-8
- В Supabase SQL Editor по умолчанию правильная кодировка

## ✅ УСПЕШНАЯ НАСТРОЙКА

После успешной настройки у вас будет:
- 5 таблиц с правильной структурой
- Оптимизированные индексы
- 40+ медицинских норм
- Готовая база для ИИ-анализатора 