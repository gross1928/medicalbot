"""
Основной процессор файлов - интеграция всех компонентов обработки
"""
import logging
import tempfile
import os
from typing import Optional, Dict, Any
from pathlib import Path
import asyncio

from .ocr import OCRProcessor
from .storage import StorageManager
from src.database.client import get_supabase_client

logger = logging.getLogger(__name__)


class FileProcessor:
    """Основной процессор файлов"""
    
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.storage_manager = StorageManager(get_supabase_client())
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.jpg': self._process_image,
            '.jpeg': self._process_image,
            '.png': self._process_image,
            '.gif': self._process_image,
            '.bmp': self._process_image,
            '.tiff': self._process_image,
        }
    
    async def process_file(
        self, 
        file_data: bytes, 
        filename: str, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Обработать файл полностью
        
        Args:
            file_data: Данные файла
            filename: Имя файла
            user_id: ID пользователя
        
        Returns:
            Dict с результатами обработки:
            {
                "success": bool,
                "file_path": str,           # Путь в хранилище
                "extracted_text": str,     # Извлеченный текст
                "file_info": dict,         # Информация о файле
                "error": str               # Ошибка если есть
            }
        """
        try:
            logger.info(f"Processing file: {filename} for user {user_id}")
            
            # Получаем расширение файла
            file_extension = Path(filename).suffix.lower()
            
            if file_extension not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Неподдерживаемый формат файла: {file_extension}"
                }
            
            # Загружаем файл в хранилище
            file_path = await self.storage_manager.upload_file(
                file_data, filename, user_id
            )
            
            if not file_path:
                return {
                    "success": False,
                    "error": "Ошибка загрузки файла в хранилище"
                }
            
            # Скачиваем файл во временную директорию для обработки
            temp_file_path = await self.storage_manager.download_file_to_temp(file_path)
            
            if not temp_file_path:
                return {
                    "success": False,
                    "error": "Ошибка скачивания файла для обработки"
                }
            
            try:
                # Обрабатываем файл в зависимости от типа
                processor_func = self.supported_formats[file_extension]
                extracted_text = await processor_func(temp_file_path)
                
                # Информация о файле
                file_info = {
                    "filename": filename,
                    "size": len(file_data),
                    "type": file_extension,
                    "storage_path": file_path
                }
                
                result = {
                    "success": True,
                    "file_path": file_path,
                    "extracted_text": extracted_text,
                    "file_info": file_info
                }
                
                logger.info(f"Successfully processed file: {filename}")
                return result
                
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {temp_file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return {
                "success": False,
                "error": f"Ошибка обработки файла: {str(e)}"
            }
    
    async def _process_pdf(self, file_path: str) -> Optional[str]:
        """Обработать PDF файл"""
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Сначала пытаемся извлечь текст напрямую
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # Если текст найден и он достаточной длины
                    if len(text.strip()) > 50:
                        logger.info("Successfully extracted text from PDF directly")
                        return text.strip()
            except Exception as e:
                logger.warning(f"Direct PDF text extraction failed: {e}")
            
            # Если прямое извлечение не удалось, используем OCR
            logger.info("Using OCR for PDF processing")
            extracted_text = await self.ocr_processor.extract_text_from_pdf(file_path)
            
            if extracted_text:
                logger.info("Successfully extracted text from PDF using OCR")
                return extracted_text
            else:
                logger.warning("No text extracted from PDF")
                return None
                
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None
    
    async def _process_image(self, file_path: str) -> Optional[str]:
        """Обработать изображение"""
        try:
            logger.info(f"Processing image: {file_path}")
            
            extracted_text = await self.ocr_processor.extract_text_from_image(file_path)
            
            if extracted_text:
                logger.info("Successfully extracted text from image")
                return extracted_text
            else:
                logger.warning("No text extracted from image")
                return None
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    async def get_file_text(self, file_path: str) -> Optional[str]:
        """Получить текст из уже обработанного файла"""
        try:
            # Скачиваем файл во временную директорию
            temp_file_path = await self.storage_manager.download_file_to_temp(file_path)
            
            if not temp_file_path:
                return None
            
            try:
                # Определяем тип файла и обрабатываем
                file_extension = Path(file_path).suffix.lower()
                
                if file_extension in self.supported_formats:
                    processor_func = self.supported_formats[file_extension]
                    return await processor_func(temp_file_path)
                else:
                    logger.error(f"Unsupported file format: {file_extension}")
                    return None
                    
            finally:
                # Удаляем временный файл
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
                    
        except Exception as e:
            logger.error(f"Error getting file text: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Удалить файл из хранилища"""
        try:
            return await self.storage_manager.delete_file(file_path)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Получить временную ссылку на файл"""
        try:
            return await self.storage_manager.get_file_url(file_path, expires_in)
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            return None
    
    def validate_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Валидировать файл перед обработкой"""
        try:
            file_size = len(file_data)
            file_extension = Path(filename).suffix.lower()
            
            # Проверки
            checks = {
                "size_ok": file_size <= 20 * 1024 * 1024,  # 20MB
                "format_ok": file_extension in self.supported_formats,
                "not_empty": file_size > 0,
                "filename_ok": len(filename) > 0 and len(filename) <= 255
            }
            
            # Сообщения об ошибках
            errors = []
            if not checks["size_ok"]:
                errors.append(f"Файл слишком большой: {file_size / 1024 / 1024:.1f}MB (максимум 20MB)")
            
            if not checks["format_ok"]:
                errors.append(f"Неподдерживаемый формат: {file_extension}")
                errors.append(f"Поддерживаемые форматы: {', '.join(self.supported_formats.keys())}")
            
            if not checks["not_empty"]:
                errors.append("Файл пустой")
            
            if not checks["filename_ok"]:
                errors.append("Некорректное имя файла")
            
            return {
                "valid": all(checks.values()),
                "checks": checks,
                "errors": errors,
                "file_info": {
                    "size": file_size,
                    "size_mb": round(file_size / 1024 / 1024, 2),
                    "extension": file_extension,
                    "filename": filename
                }
            }
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return {
                "valid": False,
                "checks": {},
                "errors": [f"Ошибка валидации: {str(e)}"],
                "file_info": {}
            }
    
    async def process_multiple_files(
        self, 
        files_data: list, 
        user_id: int
    ) -> Dict[str, Any]:
        """
        Обработать несколько файлов одновременно
        
        Args:
            files_data: Список с данными файлов [(file_data, filename), ...]
            user_id: ID пользователя
        
        Returns:
            Dict с результатами обработки всех файлов
        """
        try:
            logger.info(f"Processing {len(files_data)} files for user {user_id}")
            
            # Обрабатываем файлы параллельно
            tasks = [
                self.process_file(file_data, filename, user_id)
                for file_data, filename in files_data
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Анализируем результаты
            successful = []
            failed = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed.append({
                        "filename": files_data[i][1],
                        "error": str(result)
                    })
                elif result.get("success"):
                    successful.append(result)
                else:
                    failed.append({
                        "filename": files_data[i][1],
                        "error": result.get("error", "Unknown error")
                    })
            
            return {
                "total_files": len(files_data),
                "successful_count": len(successful),
                "failed_count": len(failed),
                "successful": successful,
                "failed": failed,
                "combined_text": "\n\n".join([
                    r["extracted_text"] for r in successful 
                    if r.get("extracted_text")
                ])
            }
            
        except Exception as e:
            logger.error(f"Error processing multiple files: {e}")
            return {
                "total_files": len(files_data),
                "successful_count": 0,
                "failed_count": len(files_data),
                "successful": [],
                "failed": [{"error": f"Общая ошибка обработки: {str(e)}"}],
                "combined_text": ""
            }
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Получить статистику обработки файлов"""
        try:
            storage_stats = await self.storage_manager.get_storage_stats()
            
            return {
                "storage": storage_stats,
                "supported_formats": list(self.supported_formats.keys()),
                "max_file_size_mb": 20,
                "ocr_language": self.ocr_processor.language
            }
            
        except Exception as e:
            logger.error(f"Error getting processing stats: {e}")
            return {
                "error": str(e)
            } 