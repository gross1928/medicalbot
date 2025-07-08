"""
AI анализатор медицинских данных
"""
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.settings import settings
from src.models import (
    BiomarkerResult, BiomarkerStatus, 
    Recommendation, RecommendationType, RecommendationPriority,
    User
)
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class MedicalAnalyzer:
    """Анализатор медицинских данных с помощью ИИ"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.prompt_manager = PromptManager()
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
    
    async def extract_biomarkers(self, extracted_text: str) -> List[Dict[str, Any]]:
        """Извлечь биомаркеры из текста анализа"""
        try:
            prompt = self.prompt_manager.get_extraction_prompt(extracted_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt_manager.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"Tokens used for extraction: {response.usage.total_tokens}")
            
            # Парсим JSON ответ
            try:
                biomarkers_data = json.loads(result_text)
                return biomarkers_data.get("biomarkers", [])
            except json.JSONDecodeError:
                logger.error("Failed to parse biomarkers JSON response")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting biomarkers: {e}")
            return []
    
    async def interpret_biomarkers(
        self, 
        biomarkers: List[Dict[str, Any]], 
        user: Optional[User] = None
    ) -> List[BiomarkerResult]:
        """Интерпретировать биомаркеры"""
        interpreted_biomarkers = []
        
        for biomarker_data in biomarkers:
            try:
                # Определяем статус относительно нормы
                status = await self._determine_biomarker_status(biomarker_data, user)
                
                # Создаем интерпретацию
                interpretation = await self._generate_biomarker_interpretation(
                    biomarker_data, status, user
                )
                
                biomarker = BiomarkerResult(
                    id=None,  # Будет установлен при сохранении в БД
                    analysis_id=None,  # Будет установлен позже
                    name=biomarker_data.get("name", ""),
                    value=biomarker_data.get("value", ""),
                    unit=biomarker_data.get("unit"),
                    reference_range=biomarker_data.get("reference_range"),
                    status=status,
                    interpretation=interpretation,
                    numeric_value=self._extract_numeric_value(biomarker_data.get("value", "")),
                    created_at=None  # Будет установлено при сохранении
                )
                
                interpreted_biomarkers.append(biomarker)
                
            except Exception as e:
                logger.error(f"Error interpreting biomarker {biomarker_data}: {e}")
                continue
        
        return interpreted_biomarkers
    
    async def generate_recommendations(
        self, 
        biomarkers: List[BiomarkerResult], 
        user: Optional[User] = None
    ) -> List[Recommendation]:
        """Генерировать персонализированные рекомендации"""
        try:
            prompt = self.prompt_manager.get_recommendations_prompt(biomarkers, user)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt_manager.get_recommendations_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            logger.info(f"Tokens used for recommendations: {response.usage.total_tokens}")
            
            # Парсим рекомендации
            try:
                recommendations_data = json.loads(result_text)
                return self._parse_recommendations(recommendations_data.get("recommendations", []))
            except json.JSONDecodeError:
                logger.error("Failed to parse recommendations JSON response")
                return []
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def analyze_results(self, analysis) -> List[Recommendation]:
        """Полный анализ результатов"""
        try:
            # 1. Извлекаем биомаркеры из текста
            biomarkers_data = await self.extract_biomarkers(analysis.extracted_text)
            
            if not biomarkers_data:
                logger.warning("No biomarkers extracted from text")
                return []
            
            # 2. Интерпретируем биомаркеры
            user = await self._get_user_by_analysis_id(analysis.id)
            biomarkers = await self.interpret_biomarkers(biomarkers_data, user)
            
            # 3. Сохраняем биомаркеры в БД
            await self._save_biomarkers(analysis.id, biomarkers)
            
            # 4. Генерируем рекомендации
            recommendations = await self.generate_recommendations(biomarkers, user)
            
            # 5. Сохраняем рекомендации в БД
            await self._save_recommendations(analysis.id, recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in analyze_results: {e}")
            return []
    
    async def _determine_biomarker_status(
        self, 
        biomarker_data: Dict[str, Any], 
        user: Optional[User]
    ) -> BiomarkerStatus:
        """Определить статус биомаркера относительно нормы"""
        try:
            # Здесь можно добавить логику сравнения с медицинскими нормами из БД
            # Пока используем простую ИИ-интерпретацию
            
            value = biomarker_data.get("value", "")
            reference_range = biomarker_data.get("reference_range", "")
            
            if not value or not reference_range:
                return BiomarkerStatus.UNKNOWN
            
            # Простая логика определения статуса
            numeric_value = self._extract_numeric_value(value)
            if numeric_value is None:
                return BiomarkerStatus.UNKNOWN
            
            # Парсим референсный диапазон
            normal_range = self._parse_reference_range(reference_range)
            if not normal_range:
                return BiomarkerStatus.UNKNOWN
            
            min_val, max_val = normal_range
            
            if numeric_value < min_val:
                # Проверяем критически низкий уровень (< 70% от минимума)
                if numeric_value < min_val * 0.7:
                    return BiomarkerStatus.CRITICAL_LOW
                return BiomarkerStatus.LOW
            elif numeric_value > max_val:
                # Проверяем критически высокий уровень (> 130% от максимума)
                if numeric_value > max_val * 1.3:
                    return BiomarkerStatus.CRITICAL_HIGH
                return BiomarkerStatus.HIGH
            else:
                return BiomarkerStatus.NORMAL
                
        except Exception as e:
            logger.error(f"Error determining biomarker status: {e}")
            return BiomarkerStatus.UNKNOWN
    
    async def _generate_biomarker_interpretation(
        self, 
        biomarker_data: Dict[str, Any], 
        status: BiomarkerStatus, 
        user: Optional[User]
    ) -> str:
        """Генерировать интерпретацию биомаркера"""
        try:
            prompt = self.prompt_manager.get_interpretation_prompt(biomarker_data, status, user)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты медицинский консультант. Дай краткую интерпретацию показателя."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating interpretation: {e}")
            return "Интерпретация недоступна"
    
    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """Извлечь числовое значение из строки"""
        try:
            # Убираем все нечисловые символы кроме точки и запятой
            import re
            numeric_str = re.sub(r'[^\d.,]', '', value.replace(',', '.'))
            return float(numeric_str) if numeric_str else None
        except:
            return None
    
    def _parse_reference_range(self, range_str: str) -> Optional[tuple]:
        """Парсить референсный диапазон"""
        try:
            import re
            # Ищем паттерны типа "3.5-5.0", "10 - 20", "<10", ">5"
            range_pattern = r'(\d+\.?\d*)\s*[-–—]\s*(\d+\.?\d*)'
            match = re.search(range_pattern, range_str)
            
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                return (min_val, max_val)
            
            return None
        except:
            return None
    
    def _parse_recommendations(self, recommendations_data: List[Dict]) -> List[Recommendation]:
        """Парсить рекомендации из JSON"""
        recommendations = []
        
        for rec_data in recommendations_data:
            try:
                recommendation = Recommendation(
                    id=None,  # Будет установлен при сохранении
                    analysis_id=None,  # Будет установлен позже
                    recommendation_text=rec_data.get("text", ""),
                    category=RecommendationType(rec_data.get("category", "general")),
                    priority=RecommendationPriority(rec_data.get("priority", "medium")),
                    biomarker_name=rec_data.get("biomarker_name"),
                    target_value=rec_data.get("target_value"),
                    timeline=rec_data.get("timeline"),
                    confidence_score=rec_data.get("confidence", 0.8),
                    created_at=None  # Будет установлено при сохранении
                )
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Error parsing recommendation {rec_data}: {e}")
                continue
        
        return recommendations
    
    async def _get_user_by_analysis_id(self, analysis_id) -> Optional[User]:
        """Получить пользователя по ID анализа"""
        # TODO: Реализовать получение пользователя из БД
        return None
    
    async def _save_biomarkers(self, analysis_id, biomarkers: List[BiomarkerResult]):
        """Сохранить биомаркеры в БД"""
        # TODO: Реализовать сохранение в БД
        pass
    
    async def _save_recommendations(self, analysis_id, recommendations: List[Recommendation]):
        """Сохранить рекомендации в БД"""
        # TODO: Реализовать сохранение в БД
        pass 