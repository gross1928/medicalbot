"""
Модель рекомендаций
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class RecommendationType(str, Enum):
    """Типы рекомендаций"""
    NUTRITION = "nutrition"
    EXERCISE = "exercise"
    LIFESTYLE = "lifestyle"
    SUPPLEMENTS = "supplements"
    MEDICAL = "medical"
    MONITORING = "monitoring"
    GENERAL = "general"


class RecommendationPriority(str, Enum):
    """Приоритет рекомендации"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationBase(BaseModel):
    """Базовая модель рекомендации"""
    analysis_id: UUID = Field(..., description="ID анализа")
    recommendation_text: str = Field(..., description="Текст рекомендации")
    category: RecommendationType = Field(..., description="Категория рекомендации")
    priority: RecommendationPriority = Field(default=RecommendationPriority.MEDIUM, description="Приоритет")


class RecommendationCreate(RecommendationBase):
    """Модель для создания рекомендации"""
    # Дополнительные поля для создания
    biomarker_name: Optional[str] = Field(None, description="Связанный биомаркер")
    target_value: Optional[str] = Field(None, description="Целевое значение")
    timeline: Optional[str] = Field(None, description="Временные рамки")


class Recommendation(RecommendationBase):
    """Полная модель рекомендации из БД"""
    id: UUID = Field(..., description="UUID рекомендации")
    
    # Дополнительная информация
    biomarker_name: Optional[str] = Field(None, description="Связанный биомаркер")
    target_value: Optional[str] = Field(None, description="Целевое значение")
    timeline: Optional[str] = Field(None, description="Временные рамки")
    
    # Структурированные данные
    action_items: Optional[Dict[str, Any]] = Field(None, description="Конкретные действия")
    resources: Optional[Dict[str, Any]] = Field(None, description="Полезные ресурсы")
    
    # Метаданные
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Уверенность в рекомендации")
    scientific_basis: Optional[str] = Field(None, description="Научное обоснование")
    contraindications: Optional[str] = Field(None, description="Противопоказания")
    
    # Системные поля
    created_at: datetime = Field(..., description="Дата создания")
    is_personalized: bool = Field(default=True, description="Персонализированная ли рекомендация")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 