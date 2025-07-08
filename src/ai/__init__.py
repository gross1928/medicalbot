"""
AI модуль для анализа медицинских данных
"""

from .analyzer import MedicalAnalyzer
from .prompts import PromptManager

__all__ = [
    "MedicalAnalyzer",
    "PromptManager",
] 