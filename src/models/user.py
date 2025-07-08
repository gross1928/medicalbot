"""
Модель пользователя
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    telegram_id: int = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Username в Telegram")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    age: Optional[int] = Field(None, ge=1, le=150, description="Возраст пользователя")
    gender: Optional[str] = Field(None, description="Пол пользователя (M/F)")
    weight: Optional[float] = Field(None, ge=1, le=500, description="Вес в кг")
    height: Optional[float] = Field(None, ge=50, le=250, description="Рост в см")


class UserCreate(UserBase):
    """Модель для создания пользователя"""
    pass


class UserUpdate(BaseModel):
    """Модель для обновления пользователя"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = None
    weight: Optional[float] = Field(None, ge=1, le=500)
    height: Optional[float] = Field(None, ge=50, le=250)


class User(UserBase):
    """Полная модель пользователя из БД"""
    id: UUID = Field(..., description="UUID пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата последнего обновления")
    is_active: bool = Field(True, description="Активен ли пользователь")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        } 