"""
Репозитории для работы с данными
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from src.models import (
    User, UserCreate, UserUpdate,
    Analysis, AnalysisCreate, AnalysisUpdate,
    BiomarkerResult, BiomarkerCreate,
    Recommendation, RecommendationCreate,
    MedicalNorm, MedicalNormCreate
)
from .client import get_supabase_client

logger = logging.getLogger(__name__)


class BaseRepository:
    """Базовый репозиторий"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.client = get_supabase_client()
    
    def _handle_error(self, operation: str, error: Exception):
        """Обработка ошибок"""
        logger.error(f"Error in {operation} for table {self.table_name}: {error}")
        raise error


class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    def __init__(self):
        super().__init__("users")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Создать пользователя"""
        try:
            result = self.client.get_table(self.table_name).insert(
                user_data.model_dump()
            ).execute()
            
            if result.data:
                return User(**result.data[0])
            raise Exception("Failed to create user")
            
        except Exception as e:
            self._handle_error("create_user", e)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        try:
            result = self.client.get_table(self.table_name).select("*").eq(
                "telegram_id", telegram_id
            ).execute()
            
            if result.data:
                return User(**result.data[0])
            return None
            
        except Exception as e:
            self._handle_error("get_user_by_telegram_id", e)
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Обновить пользователя"""
        try:
            update_data = user_data.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = self.client.get_table(self.table_name).update(
                update_data
            ).eq("id", str(user_id)).execute()
            
            if result.data:
                return User(**result.data[0])
            raise Exception("Failed to update user")
            
        except Exception as e:
            self._handle_error("update_user", e)


class AnalysisRepository(BaseRepository):
    """Репозиторий для работы с анализами"""
    
    def __init__(self):
        super().__init__("analyses")
    
    async def create_analysis(self, analysis_data: AnalysisCreate) -> Analysis:
        """Создать анализ"""
        try:
            result = self.client.get_table(self.table_name).insert(
                analysis_data.model_dump()
            ).execute()
            
            if result.data:
                return Analysis(**result.data[0])
            raise Exception("Failed to create analysis")
            
        except Exception as e:
            self._handle_error("create_analysis", e)
    
    async def get_analysis(self, analysis_id: UUID) -> Optional[Analysis]:
        """Получить анализ по ID"""
        try:
            result = self.client.get_table(self.table_name).select("*").eq(
                "id", str(analysis_id)
            ).execute()
            
            if result.data:
                return Analysis(**result.data[0])
            return None
            
        except Exception as e:
            self._handle_error("get_analysis", e)
    
    async def get_user_analyses(self, user_id: UUID, limit: int = 10) -> List[Analysis]:
        """Получить анализы пользователя"""
        try:
            result = self.client.get_table(self.table_name).select("*").eq(
                "user_id", str(user_id)
            ).order("uploaded_at", desc=True).limit(limit).execute()
            
            return [Analysis(**item) for item in result.data]
            
        except Exception as e:
            self._handle_error("get_user_analyses", e)
    
    async def update_analysis(self, analysis_id: UUID, update_data: AnalysisUpdate) -> Analysis:
        """Обновить анализ"""
        try:
            update_dict = update_data.model_dump(exclude_unset=True)
            
            result = self.client.get_table(self.table_name).update(
                update_dict
            ).eq("id", str(analysis_id)).execute()
            
            if result.data:
                return Analysis(**result.data[0])
            raise Exception("Failed to update analysis")
            
        except Exception as e:
            self._handle_error("update_analysis", e)


class BiomarkerRepository(BaseRepository):
    """Репозиторий для работы с биомаркерами"""
    
    def __init__(self):
        super().__init__("results")
    
    async def create_biomarker(self, biomarker_data: BiomarkerCreate) -> BiomarkerResult:
        """Создать биомаркер"""
        try:
            result = self.client.get_table(self.table_name).insert(
                biomarker_data.model_dump()
            ).execute()
            
            if result.data:
                return BiomarkerResult(**result.data[0])
            raise Exception("Failed to create biomarker")
            
        except Exception as e:
            self._handle_error("create_biomarker", e)
    
    async def get_analysis_biomarkers(self, analysis_id: UUID) -> List[BiomarkerResult]:
        """Получить биомаркеры анализа"""
        try:
            result = self.client.get_table(self.table_name).select("*").eq(
                "analysis_id", str(analysis_id)
            ).execute()
            
            return [BiomarkerResult(**item) for item in result.data]
            
        except Exception as e:
            self._handle_error("get_analysis_biomarkers", e)


class RecommendationRepository(BaseRepository):
    """Репозиторий для работы с рекомендациями"""
    
    def __init__(self):
        super().__init__("recommendations")
    
    async def create_recommendation(self, recommendation_data: RecommendationCreate) -> Recommendation:
        """Создать рекомендацию"""
        try:
            result = self.client.get_table(self.table_name).insert(
                recommendation_data.model_dump()
            ).execute()
            
            if result.data:
                return Recommendation(**result.data[0])
            raise Exception("Failed to create recommendation")
            
        except Exception as e:
            self._handle_error("create_recommendation", e)
    
    async def get_analysis_recommendations(self, analysis_id: UUID) -> List[Recommendation]:
        """Получить рекомендации для анализа"""
        try:
            result = self.client.get_table(self.table_name).select("*").eq(
                "analysis_id", str(analysis_id)
            ).order("priority", desc=True).execute()
            
            return [Recommendation(**item) for item in result.data]
            
        except Exception as e:
            self._handle_error("get_analysis_recommendations", e)


class MedicalNormRepository(BaseRepository):
    """Репозиторий для работы с медицинскими нормами"""
    
    def __init__(self):
        super().__init__("medical_norms")
    
    async def get_norm_for_biomarker(
        self, 
        biomarker_name: str, 
        gender: str = "BOTH", 
        age: Optional[int] = None
    ) -> Optional[MedicalNorm]:
        """Получить норму для биомаркера"""
        try:
            query = self.client.get_table(self.table_name).select("*").eq(
                "biomarker_name", biomarker_name
            ).eq("is_active", True)
            
            # Добавляем фильтры по полу и возрасту
            if gender != "BOTH":
                query = query.in_("gender", [gender, "BOTH"])
            
            if age is not None:
                query = query.or_(
                    f"age_min.is.null,age_min.lte.{age}"
                ).or_(
                    f"age_max.is.null,age_max.gte.{age}"
                )
            
            result = query.execute()
            
            if result.data:
                # Возвращаем наиболее специфичную норму
                return MedicalNorm(**result.data[0])
            return None
            
        except Exception as e:
            self._handle_error("get_norm_for_biomarker", e) 