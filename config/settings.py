"""
Конфигурация приложения для медицинского ИИ-анализатора
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
import secrets


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = Field("DEMO_TOKEN", env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: str = Field("", env="TELEGRAM_WEBHOOK_URL")
    
    # OpenAI Configuration
    openai_api_key: str = Field("sk-demo", env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(2000, env="OPENAI_MAX_TOKENS")
    
    # Supabase Configuration
    supabase_url: str = Field("https://demo.supabase.co", env="SUPABASE_URL")
    supabase_anon_key: str = Field("demo_anon_key", env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field("demo_service_key", env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Application Configuration
    app_env: str = Field("development", env="APP_ENV")
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(8000, env="APP_PORT")
    debug: bool = Field(True, env="DEBUG")
    
    # Security
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    encryption_key: str = Field("", env="ENCRYPTION_KEY")
    
    # File Processing
    max_file_size_mb: int = Field(20, env="MAX_FILE_SIZE_MB")
    allowed_file_types: List[str] = Field(default=["pdf", "jpg", "jpeg", "png"])
    ocr_language: str = Field("rus+eng", env="OCR_LANGUAGE")
    
    # Monitoring
    sentry_dsn: str = Field("", env="SENTRY_DSN")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(10, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(100, env="RATE_LIMIT_PER_HOUR")
    
    # AI Analysis Configuration
    ai_analysis_timeout: int = Field(120, env="AI_ANALYSIS_TIMEOUT")
    max_biomarkers_per_analysis: int = Field(50, env="MAX_BIOMARKERS_PER_ANALYSIS")
    cache_analysis_hours: int = Field(24, env="CACHE_ANALYSIS_HOURS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings() 