"""
Модель анализа медицинских показателей
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Статусы обработки анализа"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"


class AnalysisBase(BaseModel):
    """Базовая модель анализа"""
    user_id: UUID = Field(..., description="ID пользователя")
    file_path: str = Field(..., description="Путь к файлу в Supabase Storage")
    original_filename: str = Field(..., description="Оригинальное имя файла")
    file_type: str = Field(..., description="Тип файла (pdf, jpg, png)")
    file_size: int = Field(..., description="Размер файла в байтах")


class AnalysisCreate(AnalysisBase):
    """Модель для создания анализа"""
    pass


class AnalysisUpdate(BaseModel):
    """Модель для обновления анализа"""
    status: Optional[AnalysisStatus] = None
    error_message: Optional[str] = None
    processing_result: Optional[Dict[str, Any]] = None
    analysis_summary: Optional[str] = None


class Analysis(AnalysisBase):
    """Полная модель анализа из БД"""
    id: UUID = Field(..., description="UUID анализа")
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING, description="Статус обработки")
    uploaded_at: datetime = Field(..., description="Дата загрузки")
    processed_at: Optional[datetime] = Field(None, description="Дата завершения обработки")
    
    # Результаты обработки
    extracted_text: Optional[str] = Field(None, description="Извлеченный текст из файла")
    ocr_confidence: Optional[float] = Field(None, description="Уверенность OCR (0-1)")
    processing_result: Optional[Dict[str, Any]] = Field(None, description="Результат обработки")
    analysis_summary: Optional[str] = Field(None, description="Краткое резюме анализа")
    
    # Метаданные обработки
    processing_time_seconds: Optional[float] = Field(None, description="Время обработки в секундах")
    ai_tokens_used: Optional[int] = Field(None, description="Количество токенов ИИ")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 