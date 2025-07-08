"""
Менеджер хранения файлов в Supabase Storage
"""
import logging
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
from supabase import Client
from config.settings import settings

logger = logging.getLogger(__name__)


class StorageManager:
    """Менеджер для работы с файлами в Supabase Storage"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.bucket_name = "medical-files"
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        
        # Создаем bucket если его нет
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Убедиться что bucket существует"""
        try:
            # Проверяем существование bucket
            buckets = self.supabase.storage.list_buckets()
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            if not bucket_exists:
                # Создаем bucket
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={
                        "public": False,  # Приватные файлы
                        "allowedMimeTypes": [
                            "application/pdf",
                            "image/jpeg", 
                            "image/jpg",
                            "image/png",
                            "image/gif",
                            "image/bmp",
                            "image/tiff"
                        ],
                        "fileSizeLimit": self.max_file_size
                    }
                )
                logger.info(f"Created storage bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
    
    async def upload_file(self, file_data: bytes, filename: str, user_id: int) -> Optional[str]:
        """
        Загрузить файл в хранилище
        
        Returns:
            str: Путь к файлу в хранилище или None при ошибке
        """
        try:
            # Валидация файла
            if not self._validate_file(file_data, filename):
                return None
            
            # Генерируем уникальное имя файла
            file_path = self._generate_file_path(filename, user_id)
            
            # Загружаем файл
            result = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_data,
                file_options={
                    "cache-control": "3600",
                    "upsert": "false"  # Не перезаписывать существующие файлы
                }
            )
            
            if result:
                logger.info(f"Successfully uploaded file: {file_path}")
                return file_path
            else:
                logger.error("Failed to upload file")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return None
    
    async def download_file(self, file_path: str) -> Optional[bytes]:
        """Скачать файл из хранилища"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).download(file_path)
            
            if result:
                logger.info(f"Successfully downloaded file: {file_path}")
                return result
            else:
                logger.error(f"Failed to download file: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def download_file_to_temp(self, file_path: str) -> Optional[str]:
        """
        Скачать файл во временную директорию
        
        Returns:
            str: Путь к временному файлу или None при ошибке
        """
        try:
            # Скачиваем файл
            file_data = await self.download_file(file_path)
            if not file_data:
                return None
            
            # Получаем расширение файла
            original_filename = Path(file_path).name
            extension = Path(original_filename).suffix
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(
                suffix=extension, 
                delete=False
            ) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            logger.info(f"Downloaded file to temp path: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error downloading file to temp: {e}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """Удалить файл из хранилища"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if result:
                logger.info(f"Successfully deleted file: {file_path}")
                return True
            else:
                logger.error(f"Failed to delete file: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    async def get_file_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Получить временную ссылку на файл
        
        Args:
            file_path: Путь к файлу в хранилище
            expires_in: Время жизни ссылки в секундах (по умолчанию 1 час)
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            if result and 'signedURL' in result:
                logger.info(f"Generated signed URL for file: {file_path}")
                return result['signedURL']
            else:
                logger.error(f"Failed to generate signed URL for file: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            return None
    
    async def cleanup_old_files(self, days: int = 30) -> int:
        """
        Очистить старые файлы (старше указанного количества дней)
        
        Returns:
            int: Количество удаленных файлов
        """
        try:
            # Получаем список всех файлов
            result = self.supabase.storage.from_(self.bucket_name).list()
            
            if not result:
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days)
            files_to_delete = []
            
            for file_info in result:
                # Проверяем дату создания файла
                created_at = datetime.fromisoformat(
                    file_info['created_at'].replace('Z', '+00:00')
                )
                
                if created_at < cutoff_date:
                    files_to_delete.append(file_info['name'])
            
            # Удаляем старые файлы
            if files_to_delete:
                delete_result = self.supabase.storage.from_(self.bucket_name).remove(
                    files_to_delete
                )
                
                if delete_result:
                    logger.info(f"Cleaned up {len(files_to_delete)} old files")
                    return len(files_to_delete)
            
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0
    
    def _validate_file(self, file_data: bytes, filename: str) -> bool:
        """Валидация файла"""
        try:
            # Проверяем размер файла
            if len(file_data) > self.max_file_size:
                logger.error(f"File too large: {len(file_data)} bytes")
                return False
            
            # Проверяем расширение файла
            extension = Path(filename).suffix.lower()
            if extension not in self.allowed_extensions:
                logger.error(f"Invalid file extension: {extension}")
                return False
            
            # Проверяем что файл не пустой
            if len(file_data) == 0:
                logger.error("Empty file")
                return False
            
            # Базовая проверка формата файла по magic bytes
            if not self._check_file_format(file_data, extension):
                logger.error(f"Invalid file format for extension: {extension}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False
    
    def _check_file_format(self, file_data: bytes, extension: str) -> bool:
        """Проверка формата файла по magic bytes"""
        try:
            magic_bytes = file_data[:16]
            
            # PDF
            if extension == '.pdf':
                return magic_bytes.startswith(b'%PDF-')
            
            # JPEG
            elif extension in ['.jpg', '.jpeg']:
                return magic_bytes.startswith(b'\xff\xd8\xff')
            
            # PNG
            elif extension == '.png':
                return magic_bytes.startswith(b'\x89PNG\r\n\x1a\n')
            
            # GIF
            elif extension == '.gif':
                return magic_bytes.startswith(b'GIF87a') or magic_bytes.startswith(b'GIF89a')
            
            # BMP
            elif extension == '.bmp':
                return magic_bytes.startswith(b'BM')
            
            # TIFF
            elif extension in ['.tiff', '.tif']:
                return (magic_bytes.startswith(b'II*\x00') or 
                       magic_bytes.startswith(b'MM\x00*'))
            
            # Если формат не поддерживается, считаем валидным
            return True
            
        except Exception as e:
            logger.error(f"Error checking file format: {e}")
            return True  # При ошибке считаем валидным
    
    def _generate_file_path(self, filename: str, user_id: int) -> str:
        """Генерировать уникальный путь к файлу"""
        try:
            # Получаем расширение файла
            extension = Path(filename).suffix.lower()
            
            # Генерируем уникальный ID
            file_id = str(uuid.uuid4())
            
            # Создаем структуру папок: user_id/year/month/file_id.extension
            now = datetime.now()
            
            file_path = f"{user_id}/{now.year}/{now.month:02d}/{file_id}{extension}"
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating file path: {e}")
            # Fallback - простой путь
            return f"{user_id}/{uuid.uuid4()}{Path(filename).suffix.lower()}"
    
    async def get_user_files(self, user_id: int, limit: int = 100) -> list:
        """Получить список файлов пользователя"""
        try:
            # Ищем файлы в папке пользователя
            result = self.supabase.storage.from_(self.bucket_name).list(
                path=str(user_id),
                limit=limit
            )
            
            if result:
                return result
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting user files: {e}")
            return []
    
    async def get_storage_stats(self) -> dict:
        """Получить статистику хранилища"""
        try:
            # Получаем список всех файлов
            result = self.supabase.storage.from_(self.bucket_name).list()
            
            if not result:
                return {
                    'total_files': 0,
                    'total_size': 0,
                    'avg_file_size': 0
                }
            
            total_files = len(result)
            total_size = sum(file_info.get('metadata', {}).get('size', 0) for file_info in result)
            avg_file_size = total_size / total_files if total_files > 0 else 0
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'avg_file_size': avg_file_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'avg_file_size': 0,
                'error': str(e)
            } 