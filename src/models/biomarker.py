"""
Модель биомаркера (показателя анализа)
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class BiomarkerStatus(str, Enum):
    """Статус биомаркера относительно нормы"""
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    CRITICAL_LOW = "critical_low"
    CRITICAL_HIGH = "critical_high"
    UNKNOWN = "unknown"


class BiomarkerBase(BaseModel):
    """Базовая модель биомаркера"""
    analysis_id: UUID = Field(..., description="ID анализа")
    name: str = Field(..., description="Название показателя")
    value: str = Field(..., description="Значение показателя")
    unit: Optional[str] = Field(None, description="Единица измерения")
    reference_range: Optional[str] = Field(None, description="Референсный диапазон")


class BiomarkerCreate(BiomarkerBase):
    """Модель для создания биомаркера"""
    pass


class BiomarkerResult(BiomarkerBase):
    """Результат биомаркера с интерпретацией"""
    id: UUID = Field(..., description="UUID биомаркера")
    status: BiomarkerStatus = Field(default=BiomarkerStatus.UNKNOWN, description="Статус относительно нормы")
    interpretation: Optional[str] = Field(None, description="Интерпретация показателя")
    
    # Нормализованные значения для анализа
    numeric_value: Optional[float] = Field(None, description="Числовое значение (если применимо)")
    normal_min: Optional[float] = Field(None, description="Минимальная норма")
    normal_max: Optional[float] = Field(None, description="Максимальная норма")
    
    # Дополнительная информация
    clinical_significance: Optional[str] = Field(None, description="Клиническое значение")
    recommendations: Optional[str] = Field(None, description="Первичные рекомендации")
    
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class Biomarker(BiomarkerResult):
    """Полная модель биомаркера (алиас для совместимости)"""
    pass 