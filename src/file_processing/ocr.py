"""
OCR процессор для извлечения текста из изображений
"""
import logging
import tempfile
from typing import Optional
from PIL import Image
import pytesseract
from config.settings import settings

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Процессор для распознавания текста с изображений"""
    
    def __init__(self):
        self.language = settings.ocr_language
        self.confidence_threshold = 30  # Минимальная уверенность OCR
        
        # Настройки Tesseract
        self.config = r'--oem 3 --psm 6'
    
    async def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Извлечь текст из изображения"""
        try:
            # Открываем изображение
            image = Image.open(image_path)
            
            # Предобработка изображения для лучшего распознавания
            processed_image = self._preprocess_image(image)
            
            # Извлекаем текст
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=self.config
            )
            
            # Проверяем качество распознавания
            confidence = self._get_ocr_confidence(processed_image)
            
            if confidence < self.confidence_threshold:
                logger.warning(f"Low OCR confidence: {confidence}%")
            
            # Очищаем и нормализуем текст
            clean_text = self._clean_extracted_text(text)
            
            if len(clean_text.strip()) < 10:
                logger.warning("Extracted text is too short, might be poor quality")
                return None
            
            logger.info(f"Successfully extracted {len(clean_text)} characters from image")
            return clean_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return None
    
    async def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Извлечь текст из PDF с помощью OCR (для сканированных PDF)"""
        try:
            import pdf2image
            
            # Конвертируем PDF в изображения
            pages = pdf2image.convert_from_path(pdf_path)
            
            all_text = []
            
            for i, page in enumerate(pages):
                logger.info(f"Processing PDF page {i+1}/{len(pages)}")
                
                # Сохраняем страницу как временное изображение
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    page.save(temp_file.name, 'PNG')
                    
                    # Извлекаем текст со страницы
                    page_text = await self.extract_text_from_image(temp_file.name)
                    
                    if page_text:
                        all_text.append(page_text)
                    
                    # Удаляем временный файл
                    import os
                    os.unlink(temp_file.name)
            
            if not all_text:
                logger.warning("No text extracted from PDF pages")
                return None
            
            # Объединяем текст со всех страниц
            combined_text = "\n\n".join(all_text)
            logger.info(f"Successfully extracted text from {len(pages)} PDF pages")
            
            return combined_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Предобработка изображения для улучшения OCR"""
        try:
            # Конвертируем в оттенки серого
            if image.mode != 'L':
                image = image.convert('L')
            
            # Увеличиваем разрешение для лучшего распознавания мелкого текста
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Улучшаем контрастность
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Увеличиваем резкость
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image  # Возвращаем оригинал при ошибке
    
    def _get_ocr_confidence(self, image: Image.Image) -> float:
        """Получить уверенность OCR распознавания"""
        try:
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Вычисляем среднюю уверенность по всем словам
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if not confidences:
                return 0.0
            
            return sum(confidences) / len(confidences)
            
        except Exception as e:
            logger.error(f"Error calculating OCR confidence: {e}")
            return 50.0  # Средняя уверенность по умолчанию
    
    def _clean_extracted_text(self, text: str) -> str:
        """Очистить и нормализовать извлеченный текст"""
        try:
            # Удаляем лишние пробелы и переносы строк
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Убираем лишние пробелы
                line = ' '.join(line.split())
                
                # Пропускаем очень короткие строки (вероятно, мусор)
                if len(line) > 2:
                    cleaned_lines.append(line)
            
            # Объединяем строки
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Удаляем повторяющиеся символы (артефакты OCR)
            import re
            cleaned_text = re.sub(r'(.)\1{3,}', r'\1\1', cleaned_text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text  # Возвращаем оригинал при ошибке
    
    def extract_text_with_coordinates(self, image_path: str) -> Optional[dict]:
        """Извлечь текст с координатами (для продвинутого анализа)"""
        try:
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            # Получаем данные с координатами
            data = pytesseract.image_to_data(
                processed_image,
                lang=self.language,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Фильтруем и структурируем данные
            words = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > self.confidence_threshold:
                    word_data = {
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                    words.append(word_data)
            
            return {
                'words': words,
                'full_text': ' '.join([w['text'] for w in words]),
                'average_confidence': sum([w['confidence'] for w in words]) / len(words) if words else 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting text with coordinates: {e}")
            return None 