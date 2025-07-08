"""
Медицинские справочники и данные
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AnalysisCategory(Enum):
    """Категории медицинских анализов"""
    BLOOD_GENERAL = "blood_general"
    BLOOD_BIOCHEMISTRY = "blood_biochemistry"
    BLOOD_HORMONES = "blood_hormones"
    BLOOD_IMMUNOLOGY = "blood_immunology"
    URINE_GENERAL = "urine_general"
    URINE_BIOCHEMISTRY = "urine_biochemistry"
    STOOL = "stool"
    OTHER = "other"


class Gender(Enum):
    """Пол"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


@dataclass
class ReferenceRange:
    """Референсные значения показателя"""
    min_value: Optional[float]
    max_value: Optional[float]
    unit: str
    gender: Optional[Gender] = None
    age_min: Optional[int] = None  # Минимальный возраст в годах
    age_max: Optional[int] = None  # Максимальный возраст в годах
    notes: Optional[str] = None


@dataclass
class Biomarker:
    """Биомаркер с референсными значениями"""
    name: str
    synonyms: List[str]
    category: AnalysisCategory
    reference_ranges: List[ReferenceRange]
    description: Optional[str] = None
    clinical_significance: Optional[str] = None


class MedicalDataHelper:
    """Помощник для работы с медицинскими данными"""
    
    def __init__(self):
        self.biomarkers = self._load_biomarkers()
        self.interpretation_rules = self._load_interpretation_rules()
    
    def _load_biomarkers(self) -> Dict[str, Biomarker]:
        """Загрузить справочник биомаркеров"""
        biomarkers = {}
        
        # Общий анализ крови
        biomarkers.update(self._get_blood_general_biomarkers())
        
        # Биохимия крови
        biomarkers.update(self._get_blood_biochemistry_biomarkers())
        
        # Гормоны
        biomarkers.update(self._get_hormone_biomarkers())
        
        # Общий анализ мочи
        biomarkers.update(self._get_urine_general_biomarkers())
        
        return biomarkers
    
    def _get_blood_general_biomarkers(self) -> Dict[str, Biomarker]:
        """Биомаркеры общего анализа крови"""
        return {
            "hemoglobin": Biomarker(
                name="Гемоглобин",
                synonyms=["Hb", "HGB", "гемоглобин"],
                category=AnalysisCategory.BLOOD_GENERAL,
                reference_ranges=[
                    ReferenceRange(120, 140, "г/л", Gender.FEMALE, 18, 65),
                    ReferenceRange(130, 160, "г/л", Gender.MALE, 18, 65),
                    ReferenceRange(115, 135, "г/л", Gender.FEMALE, 65, 100),
                    ReferenceRange(125, 155, "г/л", Gender.MALE, 65, 100),
                ],
                description="Белок, переносящий кислород в крови",
                clinical_significance="Снижение указывает на анемию, повышение - на полицитемию"
            ),
            "erythrocytes": Biomarker(
                name="Эритроциты",
                synonyms=["RBC", "Red Blood Cells", "эритроциты"],
                category=AnalysisCategory.BLOOD_GENERAL,
                reference_ranges=[
                    ReferenceRange(3.8, 4.5, "×10¹²/л", Gender.FEMALE),
                    ReferenceRange(4.3, 5.0, "×10¹²/л", Gender.MALE),
                ],
                description="Красные кровяные клетки",
                clinical_significance="Отражает кислородную емкость крови"
            ),
            "leukocytes": Biomarker(
                name="Лейкоциты",
                synonyms=["WBC", "White Blood Cells", "лейкоциты"],
                category=AnalysisCategory.BLOOD_GENERAL,
                reference_ranges=[
                    ReferenceRange(4.0, 9.0, "×10⁹/л"),
                ],
                description="Белые кровяные клетки",
                clinical_significance="Повышение указывает на воспаление или инфекцию"
            ),
            "platelets": Biomarker(
                name="Тромбоциты",
                synonyms=["PLT", "Platelets", "тромбоциты"],
                category=AnalysisCategory.BLOOD_GENERAL,
                reference_ranges=[
                    ReferenceRange(150, 400, "×10⁹/л"),
                ],
                description="Клетки свертывания крови",
                clinical_significance="Снижение повышает риск кровотечений"
            ),
            "esr": Biomarker(
                name="СОЭ",
                synonyms=["ESR", "СОЭ", "скорость оседания эритроцитов"],
                category=AnalysisCategory.BLOOD_GENERAL,
                reference_ranges=[
                    ReferenceRange(2, 15, "мм/ч", Gender.MALE),
                    ReferenceRange(2, 20, "мм/ч", Gender.FEMALE),
                ],
                description="Скорость оседания эритроцитов",
                clinical_significance="Повышение указывает на воспалительный процесс"
            ),
        }
    
    def _get_blood_biochemistry_biomarkers(self) -> Dict[str, Biomarker]:
        """Биомаркеры биохимии крови"""
        return {
            "glucose": Biomarker(
                name="Глюкоза",
                synonyms=["Glucose", "глюкоза", "сахар"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(3.3, 5.5, "ммоль/л"),
                ],
                description="Уровень сахара в крови",
                clinical_significance="Повышение указывает на диабет или предиабет"
            ),
            "cholesterol_total": Biomarker(
                name="Холестерин общий",
                synonyms=["Total Cholesterol", "общий холестерин"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(3.0, 5.2, "ммоль/л"),
                ],
                description="Общий уровень холестерина",
                clinical_significance="Повышение увеличивает риск сердечно-сосудистых заболеваний"
            ),
            "hdl_cholesterol": Biomarker(
                name="Холестерин ЛПВП",
                synonyms=["HDL", "ЛПВП", "хороший холестерин"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(1.0, None, "ммоль/л", Gender.MALE),
                    ReferenceRange(1.2, None, "ммоль/л", Gender.FEMALE),
                ],
                description="Липопротеины высокой плотности",
                clinical_significance="Чем выше, тем лучше для сердца"
            ),
            "ldl_cholesterol": Biomarker(
                name="Холестерин ЛПНП",
                synonyms=["LDL", "ЛПНП", "плохой холестерин"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(None, 3.0, "ммоль/л"),
                ],
                description="Липопротеины низкой плотности",
                clinical_significance="Повышение увеличивает риск атеросклероза"
            ),
            "triglycerides": Biomarker(
                name="Триглицериды",
                synonyms=["TG", "триглицериды"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(None, 1.7, "ммоль/л"),
                ],
                description="Жиры в крови",
                clinical_significance="Повышение связано с риском панкреатита"
            ),
            "alt": Biomarker(
                name="АЛТ",
                synonyms=["ALT", "АЛТ", "аланинаминотрансфераза"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(None, 41, "Ед/л", Gender.MALE),
                    ReferenceRange(None, 31, "Ед/л", Gender.FEMALE),
                ],
                description="Фермент печени",
                clinical_significance="Повышение указывает на повреждение печени"
            ),
            "ast": Biomarker(
                name="АСТ",
                synonyms=["AST", "АСТ", "аспартатаминотрансфераза"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(None, 40, "Ед/л", Gender.MALE),
                    ReferenceRange(None, 32, "Ед/л", Gender.FEMALE),
                ],
                description="Фермент печени и сердца",
                clinical_significance="Повышение указывает на повреждение печени или сердца"
            ),
            "creatinine": Biomarker(
                name="Креатинин",
                synonyms=["Creatinine", "креатинин"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(62, 115, "мкмоль/л", Gender.MALE),
                    ReferenceRange(53, 97, "мкмоль/л", Gender.FEMALE),
                ],
                description="Продукт обмена креатина",
                clinical_significance="Повышение указывает на нарушение функции почек"
            ),
            "urea": Biomarker(
                name="Мочевина",
                synonyms=["Urea", "мочевина"],
                category=AnalysisCategory.BLOOD_BIOCHEMISTRY,
                reference_ranges=[
                    ReferenceRange(2.5, 6.4, "ммоль/л"),
                ],
                description="Продукт белкового обмена",
                clinical_significance="Повышение указывает на нарушение функции почек"
            ),
        }
    
    def _get_hormone_biomarkers(self) -> Dict[str, Biomarker]:
        """Биомаркеры гормонов"""
        return {
            "tsh": Biomarker(
                name="ТТГ",
                synonyms=["TSH", "ТТГ", "тиреотропный гормон"],
                category=AnalysisCategory.BLOOD_HORMONES,
                reference_ranges=[
                    ReferenceRange(0.4, 4.0, "мЕд/л"),
                ],
                description="Тиреотропный гормон",
                clinical_significance="Регулирует функцию щитовидной железы"
            ),
            "t4_free": Biomarker(
                name="Т4 свободный",
                synonyms=["Free T4", "свободный Т4"],
                category=AnalysisCategory.BLOOD_HORMONES,
                reference_ranges=[
                    ReferenceRange(9.0, 22.0, "пмоль/л"),
                ],
                description="Свободный тироксин",
                clinical_significance="Основной гормон щитовидной железы"
            ),
            "t3_free": Biomarker(
                name="Т3 свободный",
                synonyms=["Free T3", "свободный Т3"],
                category=AnalysisCategory.BLOOD_HORMONES,
                reference_ranges=[
                    ReferenceRange(2.6, 5.7, "пмоль/л"),
                ],
                description="Свободный трийодтиронин",
                clinical_significance="Активная форма гормона щитовидной железы"
            ),
            "insulin": Biomarker(
                name="Инсулин",
                synonyms=["Insulin", "инсулин"],
                category=AnalysisCategory.BLOOD_HORMONES,
                reference_ranges=[
                    ReferenceRange(2.6, 24.9, "мкЕд/мл"),
                ],
                description="Гормон поджелудочной железы",
                clinical_significance="Регулирует уровень глюкозы в крови"
            ),
            "cortisol": Biomarker(
                name="Кортизол",
                synonyms=["Cortisol", "кортизол"],
                category=AnalysisCategory.BLOOD_HORMONES,
                reference_ranges=[
                    ReferenceRange(171, 536, "нмоль/л"),
                ],
                description="Гормон стресса",
                clinical_significance="Повышение связано со стрессом и болезнями надпочечников"
            ),
        }
    
    def _get_urine_general_biomarkers(self) -> Dict[str, Biomarker]:
        """Биомаркеры общего анализа мочи"""
        return {
            "urine_protein": Biomarker(
                name="Белок в моче",
                synonyms=["Protein", "белок", "протеин"],
                category=AnalysisCategory.URINE_GENERAL,
                reference_ranges=[
                    ReferenceRange(None, 0.14, "г/л"),
                ],
                description="Белок в моче",
                clinical_significance="Повышение указывает на заболевание почек"
            ),
            "urine_glucose": Biomarker(
                name="Глюкоза в моче",
                synonyms=["Glucose", "глюкоза", "сахар в моче"],
                category=AnalysisCategory.URINE_GENERAL,
                reference_ranges=[
                    ReferenceRange(None, 0.8, "ммоль/л"),
                ],
                description="Глюкоза в моче",
                clinical_significance="Появление указывает на диабет"
            ),
        }
    
    def _load_interpretation_rules(self) -> Dict[str, Dict]:
        """Загрузить правила интерпретации результатов"""
        return {
            "hemoglobin": {
                "low": {
                    "description": "Анемия - снижение уровня гемоглобина",
                    "recommendations": [
                        "Обратиться к врачу для выяснения причины анемии",
                        "Увеличить потребление железосодержащих продуктов",
                        "Рассмотреть прием препаратов железа по назначению врача"
                    ],
                    "severity": {
                        "mild": (100, 120),
                        "moderate": (70, 100),
                        "severe": (0, 70)
                    }
                },
                "high": {
                    "description": "Полицитемия - повышение уровня гемоглобина",
                    "recommendations": [
                        "Обратиться к гематологу",
                        "Исключить обезвоживание",
                        "Проверить функцию почек и легких"
                    ]
                }
            },
            "glucose": {
                "high": {
                    "description": "Гипергликемия - повышение уровня глюкозы",
                    "recommendations": [
                        "Обратиться к эндокринологу",
                        "Соблюдать диету с ограничением углеводов",
                        "Увеличить физическую активность",
                        "Контролировать вес"
                    ],
                    "severity": {
                        "prediabetes": (5.6, 6.9),
                        "diabetes": (7.0, float('inf'))
                    }
                },
                "low": {
                    "description": "Гипогликемия - снижение уровня глюкозы",
                    "recommendations": [
                        "Регулярно питаться",
                        "Избегать длительных периодов голодания",
                        "Обратиться к врачу если эпизоды повторяются"
                    ]
                }
            },
            "cholesterol_total": {
                "high": {
                    "description": "Гиперхолестеринемия - повышение холестерина",
                    "recommendations": [
                        "Соблюдать диету с ограничением насыщенных жиров",
                        "Увеличить физическую активность",
                        "Снизить вес при необходимости",
                        "Рассмотреть прием статинов по назначению врача"
                    ]
                }
            }
        }
    
    def find_biomarker(self, name: str) -> Optional[Biomarker]:
        """Найти биомаркер по названию или синониму"""
        name_lower = name.lower().strip()
        
        # Прямой поиск по ключу
        if name_lower in self.biomarkers:
            return self.biomarkers[name_lower]
        
        # Поиск по синонимам
        for biomarker in self.biomarkers.values():
            if name_lower in [syn.lower() for syn in biomarker.synonyms]:
                return biomarker
            if name_lower in biomarker.name.lower():
                return biomarker
        
        return None
    
    def get_reference_range(
        self, 
        biomarker_name: str, 
        gender: Optional[Gender] = None, 
        age: Optional[int] = None
    ) -> Optional[ReferenceRange]:
        """Получить референсные значения для биомаркера"""
        biomarker = self.find_biomarker(biomarker_name)
        if not biomarker:
            return None
        
        # Фильтруем по полу и возрасту
        suitable_ranges = []
        for ref_range in biomarker.reference_ranges:
            # Проверяем пол
            if ref_range.gender and gender and ref_range.gender != gender:
                continue
            
            # Проверяем возраст
            if age is not None:
                if ref_range.age_min and age < ref_range.age_min:
                    continue
                if ref_range.age_max and age > ref_range.age_max:
                    continue
            
            suitable_ranges.append(ref_range)
        
        # Возвращаем наиболее специфичный диапазон
        if suitable_ranges:
            # Сортируем по специфичности (с полом и возрастом в приоритете)
            suitable_ranges.sort(key=lambda r: (
                r.gender is not None,
                r.age_min is not None or r.age_max is not None
            ), reverse=True)
            return suitable_ranges[0]
        
        # Если нет подходящих, возвращаем первый доступный
        return biomarker.reference_ranges[0] if biomarker.reference_ranges else None
    
    def interpret_value(
        self, 
        biomarker_name: str, 
        value: float,
        gender: Optional[Gender] = None,
        age: Optional[int] = None
    ) -> Dict:
        """Интерпретировать значение биомаркера"""
        ref_range = self.get_reference_range(biomarker_name, gender, age)
        if not ref_range:
            return {
                "status": "unknown",
                "message": "Референсные значения не найдены"
            }
        
        # Определяем статус
        status = "normal"
        message = "Значение в пределах нормы"
        recommendations = []
        
        if ref_range.min_value is not None and value < ref_range.min_value:
            status = "low"
            message = f"Значение ниже нормы (< {ref_range.min_value} {ref_range.unit})"
        elif ref_range.max_value is not None and value > ref_range.max_value:
            status = "high" 
            message = f"Значение выше нормы (> {ref_range.max_value} {ref_range.unit})"
        
        # Получаем рекомендации
        biomarker_key = biomarker_name.lower().replace(" ", "_")
        if biomarker_key in self.interpretation_rules:
            rules = self.interpretation_rules[biomarker_key]
            if status in rules:
                recommendations = rules[status].get("recommendations", [])
        
        return {
            "status": status,
            "message": message,
            "reference_range": f"{ref_range.min_value or ''}-{ref_range.max_value or ''} {ref_range.unit}",
            "recommendations": recommendations,
            "severity": self._assess_severity(biomarker_name, value, status, ref_range)
        }
    
    def _assess_severity(
        self, 
        biomarker_name: str, 
        value: float, 
        status: str,
        ref_range: ReferenceRange
    ) -> str:
        """Оценить степень отклонения"""
        if status == "normal":
            return "normal"
        
        # Простая оценка по степени отклонения от нормы
        if ref_range.min_value is not None and ref_range.max_value is not None:
            normal_range = ref_range.max_value - ref_range.min_value
            
            if status == "low":
                deviation = (ref_range.min_value - value) / normal_range
            else:  # high
                deviation = (value - ref_range.max_value) / normal_range
            
            if deviation < 0.1:
                return "borderline"
            elif deviation < 0.5:
                return "mild"
            elif deviation < 1.0:
                return "moderate"
            else:
                return "severe"
        
        return "mild"  # По умолчанию
    
    def get_biomarkers_by_category(self, category: AnalysisCategory) -> List[Biomarker]:
        """Получить биомаркеры по категории"""
        return [
            biomarker for biomarker in self.biomarkers.values()
            if biomarker.category == category
        ]
    
    def suggest_additional_tests(self, abnormal_biomarkers: List[str]) -> List[str]:
        """Предложить дополнительные анализы на основе отклонений"""
        suggestions = []
        
        # Правила для предложения дополнительных анализов
        for biomarker_name in abnormal_biomarkers:
            biomarker_key = biomarker_name.lower().replace(" ", "_")
            
            if "glucose" in biomarker_key:
                suggestions.extend(["HbA1c", "Инсулин", "С-пептид"])
            
            elif "cholesterol" in biomarker_key:
                suggestions.extend(["Аполипопротеин A1", "Аполипопротеин B", "Липопротеин(а)"])
            
            elif any(liver in biomarker_key for liver in ["alt", "ast"]):
                suggestions.extend(["Билирубин", "ГГТ", "Щелочная фосфатаза", "Альбумин"])
            
            elif any(kidney in biomarker_key for kidney in ["creatinine", "urea"]):
                suggestions.extend(["Клиренс креатинина", "Цистатин C", "Общий анализ мочи"])
            
            elif "hemoglobin" in biomarker_key:
                suggestions.extend(["Железо", "Ферритин", "Трансферрин", "B12", "Фолиевая кислота"])
        
        # Убираем дубликаты
        return list(set(suggestions))
    
    def get_biomarker_info(self, name: str) -> Optional[Dict]:
        """Получить полную информацию о биомаркере"""
        biomarker = self.find_biomarker(name)
        if not biomarker:
            return None
        
        return {
            "name": biomarker.name,
            "synonyms": biomarker.synonyms,
            "category": biomarker.category.value,
            "description": biomarker.description,
            "clinical_significance": biomarker.clinical_significance,
            "reference_ranges": [
                {
                    "min": r.min_value,
                    "max": r.max_value,
                    "unit": r.unit,
                    "gender": r.gender.value if r.gender else None,
                    "age_min": r.age_min,
                    "age_max": r.age_max,
                    "notes": r.notes
                }
                for r in biomarker.reference_ranges
            ]
        } 