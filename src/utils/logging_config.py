"""
Конфигурация логирования для медицинского бота
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from config.settings import settings


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Настройка системы логирования
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (если None, используется только консоль)
        max_bytes: Максимальный размер файла лога
        backup_count: Количество backup файлов
    """
    
    # Определяем уровень логирования
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Создаем форматтер
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Детальный форматтер для файла
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Очищаем существующие handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Настраиваем консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Настраиваем файловый handler если указан файл
    if log_file:
        try:
            # Создаем директорию для логов если не существует
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Создаем rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
            
            logging.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            logging.error(f"Failed to setup file logging: {e}")
    
    # Настраиваем специальные логгеры
    _setup_special_loggers(numeric_level)
    
    logging.info(f"Logging configured with level: {log_level}")


def _setup_special_loggers(level: int) -> None:
    """Настройка специальных логгеров для библиотек"""
    
    # Логгер для HTTP запросов
    http_logger = logging.getLogger('httpx')
    http_logger.setLevel(logging.WARNING)  # Уменьшаем verbosity HTTP запросов
    
    # Логгер для Telegram бота
    bot_logger = logging.getLogger('telegram')
    bot_logger.setLevel(level)
    
    # Логгер для Supabase
    supabase_logger = logging.getLogger('supabase')
    supabase_logger.setLevel(level)
    
    # Логгер для OpenAI
    openai_logger = logging.getLogger('openai')
    openai_logger.setLevel(logging.WARNING)  # Уменьшаем verbosity OpenAI
    
    # Логгер для OCR
    ocr_logger = logging.getLogger('pytesseract')
    ocr_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер с указанным именем
    
    Args:
        name: Имя логгера (обычно __name__)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(name)


def log_function_call(func):
    """
    Декоратор для логирования вызовов функций
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Логируем вызов функции
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({all_args})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper


def log_async_function_call(func):
    """
    Декоратор для логирования вызовов async функций
    """
    import asyncio
    
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Логируем вызов функции
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling async {func.__name__}({all_args})")
        
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Async {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async {func.__name__} failed with error: {e}")
            raise
    
    return wrapper


class StructuredLogger:
    """Структурированный логгер для важных событий"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_user_action(self, user_id: int, action: str, details: dict = None):
        """Логирование действий пользователя"""
        details = details or {}
        self.logger.info(
            f"User action - User: {user_id}, Action: {action}, Details: {details}"
        )
    
    def log_analysis_request(self, user_id: int, analysis_type: str, file_size: int = None):
        """Логирование запросов на анализ"""
        self.logger.info(
            f"Analysis request - User: {user_id}, Type: {analysis_type}, "
            f"File size: {file_size or 'N/A'} bytes"
        )
    
    def log_analysis_completion(self, user_id: int, analysis_id: str, duration: float):
        """Логирование завершения анализа"""
        self.logger.info(
            f"Analysis completed - User: {user_id}, Analysis: {analysis_id}, "
            f"Duration: {duration:.2f}s"
        )
    
    def log_error_event(self, user_id: int, error_type: str, error_details: str):
        """Логирование ошибок"""
        self.logger.error(
            f"Error event - User: {user_id}, Type: {error_type}, "
            f"Details: {error_details}"
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Логирование метрик производительности"""
        self.logger.info(
            f"Performance metric - {metric_name}: {value}{unit}"
        )


# Глобальный структурированный логгер
structured_logger = StructuredLogger("medical_bot")


def log_performance(operation_name: str):
    """
    Декоратор для измерения времени выполнения операций
    
    Usage:
        @log_performance("file_processing")
        def process_file(file_path):
            # processing logic
            pass
    """
    import time
    
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    structured_logger.log_performance_metric(
                        f"{operation_name}_duration", duration, "s"
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    structured_logger.log_performance_metric(
                        f"{operation_name}_failed_duration", duration, "s"
                    )
                    raise
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    structured_logger.log_performance_metric(
                        f"{operation_name}_duration", duration, "s"
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    structured_logger.log_performance_metric(
                        f"{operation_name}_failed_duration", duration, "s"
                    )
                    raise
            return sync_wrapper
    
    return decorator 