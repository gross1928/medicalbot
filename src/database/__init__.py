"""
Модуль работы с базой данных (Supabase)
"""

from .client import get_supabase_client, SupabaseClient
from .repositories import (
    UserRepository,
    AnalysisRepository,
    BiomarkerRepository, 
    RecommendationRepository,
    MedicalNormRepository
)

__all__ = [
    "get_supabase_client",
    "SupabaseClient",
    "UserRepository",
    "AnalysisRepository",
    "BiomarkerRepository",
    "RecommendationRepository", 
    "MedicalNormRepository",
] 