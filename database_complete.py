"""
Полный код базы данных для медицинского ИИ-анализатора
Объединяет все модели данных, клиент Supabase и репозитории в одном файле
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from supabase import create_client, Client
import logging

# ========== КОНФИГУРАЦИЯ ==========

# Для использования необходимо задать настройки
# from config.settings import settings
# Или напрямую:
# SUPABASE_URL = "your_supabase_url"
# SUPABASE_SERVICE_ROLE_KEY = "your_service_role_key"

logger = logging.getLogger(__name__)

# ========== ENUMS ==========

class AnalysisStatus(str, Enum):
    """Статусы обработки анализа"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"

class BiomarkerStatus(str, Enum):
    """Статус биомаркера относительно нормы"""
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"
    CRITICAL_LOW = "critical_low"
    CRITICAL_HIGH = "critical_high"
    UNKNOWN = "unknown"

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

# ========== МОДЕЛИ ПОЛЬЗОВАТЕЛЯ ==========

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

# ========== МОДЕЛИ АНАЛИЗА ==========

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

# ========== МОДЕЛИ БИОМАРКЕРОВ ==========

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

# ========== МОДЕЛИ РЕКОМЕНДАЦИЙ ==========

class RecommendationBase(BaseModel):
    """Базовая модель рекомендации"""
    analysis_id: UUID = Field(..., description="ID анализа")
    recommendation_text: str = Field(..., description="Текст рекомендации")
    category: RecommendationType = Field(..., description="Категория рекомендации")
    priority: RecommendationPriority = Field(default=RecommendationPriority.MEDIUM, description="Приоритет")

class RecommendationCreate(RecommendationBase):
    """Модель для создания рекомендации"""
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

# ========== МОДЕЛИ МЕДИЦИНСКИХ НОРМ ==========

class MedicalNormBase(BaseModel):
    """Базовая модель медицинской нормы"""
    biomarker_name: str = Field(..., description="Название биомаркера")
    unit: str = Field(..., description="Единица измерения")
    min_value: Optional[float] = Field(None, description="Минимальное значение нормы")
    max_value: Optional[float] = Field(None, description="Максимальное значение нормы")
    gender: str = Field(default="BOTH", description="Пол (M/F/BOTH)")
    age_min: Optional[int] = Field(None, description="Минимальный возраст")
    age_max: Optional[int] = Field(None, description="Максимальный возраст")

class MedicalNormCreate(MedicalNormBase):
    """Модель для создания медицинской нормы"""
    source: Optional[str] = Field(None, description="Источник нормы")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")

class MedicalNorm(MedicalNormBase):
    """Полная модель медицинской нормы из БД"""
    id: UUID = Field(..., description="UUID нормы")
    
    # Дополнительная информация
    source: Optional[str] = Field(None, description="Источник нормы")
    notes: Optional[str] = Field(None, description="Дополнительные заметки")
    clinical_significance: Optional[str] = Field(None, description="Клиническое значение")
    
    # Системные поля
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: Optional[datetime] = Field(None, description="Дата обновления")
    is_active: bool = Field(default=True, description="Активна ли норма")
    version: int = Field(default=1, description="Версия нормы")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }

# ========== SUPABASE CLIENT ==========

class SupabaseClient:
    """Обертка над Supabase клиентом"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Получить клиент Supabase"""
        if self._client is None:
            self._client = create_client(
                supabase_url=self.supabase_url,
                supabase_key=self.supabase_key
            )
            logger.info("Supabase client initialized")
        return self._client
    
    async def test_connection(self) -> bool:
        """Проверить соединение с Supabase"""
        try:
            # Простой запрос для проверки соединения
            result = self.client.table("users").select("id").limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    def get_storage_client(self):
        """Получить клиент для работы с файлами"""
        return self.client.storage
    
    def get_table(self, table_name: str):
        """Получить таблицу для работы"""
        return self.client.table(table_name)

# ========== БАЗОВЫЙ РЕПОЗИТОРИЙ ==========

class BaseRepository:
    """Базовый репозиторий"""
    
    def __init__(self, table_name: str, supabase_client: SupabaseClient):
        self.table_name = table_name
        self.client = supabase_client
    
    def _handle_error(self, operation: str, error: Exception):
        """Обработка ошибок"""
        logger.error(f"Error in {operation} for table {self.table_name}: {error}")
        raise error

# ========== РЕПОЗИТОРИЙ ПОЛЬЗОВАТЕЛЕЙ ==========

class UserRepository(BaseRepository):
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, supabase_client: SupabaseClient):
        super().__init__("users", supabase_client)
    
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

# ========== РЕПОЗИТОРИЙ АНАЛИЗОВ ==========

class AnalysisRepository(BaseRepository):
    """Репозиторий для работы с анализами"""
    
    def __init__(self, supabase_client: SupabaseClient):
        super().__init__("analyses", supabase_client)
    
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

# ========== РЕПОЗИТОРИЙ БИОМАРКЕРОВ ==========

class BiomarkerRepository(BaseRepository):
    """Репозиторий для работы с биомаркерами"""
    
    def __init__(self, supabase_client: SupabaseClient):
        super().__init__("results", supabase_client)
    
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

# ========== РЕПОЗИТОРИЙ РЕКОМЕНДАЦИЙ ==========

class RecommendationRepository(BaseRepository):
    """Репозиторий для работы с рекомендациями"""
    
    def __init__(self, supabase_client: SupabaseClient):
        super().__init__("recommendations", supabase_client)
    
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

# ========== РЕПОЗИТОРИЙ МЕДИЦИНСКИХ НОРМ ==========

class MedicalNormRepository(BaseRepository):
    """Репозиторий для работы с медицинскими нормами"""
    
    def __init__(self, supabase_client: SupabaseClient):
        super().__init__("medical_norms", supabase_client)
    
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

# ========== ФАСАД ДЛЯ РАБОТЫ С БД ==========

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_client = SupabaseClient(supabase_url, supabase_key)
        
        # Инициализация репозиториев
        self.users = UserRepository(self.supabase_client)
        self.analyses = AnalysisRepository(self.supabase_client)
        self.biomarkers = BiomarkerRepository(self.supabase_client)
        self.recommendations = RecommendationRepository(self.supabase_client)
        self.medical_norms = MedicalNormRepository(self.supabase_client)
    
    async def test_connection(self) -> bool:
        """Проверить соединение с базой данных"""
        return await self.supabase_client.test_connection()

# ========== ПРИМЕР ИСПОЛЬЗОВАНИЯ ==========

"""
# Инициализация
db = DatabaseManager(
    supabase_url="your_supabase_url",
    supabase_key="your_supabase_service_role_key"
)

# Проверка соединения
if await db.test_connection():
    print("✅ База данных подключена")

# Создание пользователя
user_data = UserCreate(
    telegram_id=12345,
    username="testuser",
    first_name="Test",
    age=25,
    gender="M"
)
user = await db.users.create_user(user_data)

# Создание анализа
analysis_data = AnalysisCreate(
    user_id=user.id,
    file_path="analyses/test.pdf",
    original_filename="blood_test.pdf",
    file_type="pdf",
    file_size=1024
)
analysis = await db.analyses.create_analysis(analysis_data)

# Получение анализов пользователя
user_analyses = await db.analyses.get_user_analyses(user.id)
""" 