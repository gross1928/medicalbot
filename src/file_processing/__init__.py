"""
Модуль обработки файлов
"""

from .processor import FileProcessor
from .ocr import OCRProcessor
from .storage import StorageManager

__all__ = [
    "FileProcessor",
    "OCRProcessor", 
    "StorageManager",
] 