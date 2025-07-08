"""
Модель медицинских норм
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class GenderType(str, Enum):
    """Тип пола"""
    MALE = "M"
    FEMALE = "F"
    BOTH = "BOTH"


class AgeGroup(str, Enum):
    """Возрастные группы"""
    CHILD = "child"  # 0-17
    ADULT = "adult"  # 18-64
    ELDERLY = "elderly"  # 65+
    ALL = "all"


class MedicalNormBase(BaseModel):
    """Базовая модель медицинской нормы"""
    biomarker_name: str = Field(..., description="Название биомаркера")
    unit: str = Field(..., description="Единица измерения")
    min_value: Optional[float] = Field(None, description="Минимальное нормальное значение")
    max_value: Optional[float] = Field(None, description="Максимальное нормальное значение")
    optimal_min: Optional[float] = Field(None, description="Минимальное оптимальное значение")
    optimal_max: Optional[float] = Field(None, description="Максимальное оптимальное значение")
    
    # Демографические параметры
    gender: GenderType = Field(default=GenderType.BOTH, description="Пол")
    age_group: AgeGroup = Field(default=AgeGroup.ALL, description="Возрастная группа")
    age_min: Optional[int] = Field(None, ge=0, le=150, description="Минимальный возраст")
    age_max: Optional[int] = Field(None, ge=0, le=150, description="Максимальный возраст")


class MedicalNormCreate(MedicalNormBase):
    """Модель для создания медицинской нормы"""
    # Дополнительные поля для создания
    source: Optional[str] = Field(None, description="Источник данных")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")


class MedicalNorm(MedicalNormBase):
    """Полная модель медицинской нормы из БД"""
    id: UUID = Field(..., description="UUID нормы")
    
    # Дополнительная информация
    source: Optional[str] = Field(None, description="Источник данных")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")
    
    # Критические значения
    critical_low: Optional[float] = Field(None, description="Критически низкое значение")
    critical_high: Optional[float] = Field(None, description="Критически высокое значение")
    
    # Метаданные
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Качество данных")
    last_updated: Optional[datetime] = Field(None, description="Последнее обновление")
    is_active: bool = Field(default=True, description="Активна ли норма")
    
    # Системные поля
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 