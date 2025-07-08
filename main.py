"""
Главный файл для запуска медицинского ИИ-анализатора
"""
import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from src.bot.bot import MedicalBot
from src.database.client import get_supabase_client

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('medical_bot.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("Starting Medical AI Analyzer Bot...")
        
        # Проверяем соединение с Supabase (необязательно для демо-режима)
        if not settings.supabase_url.startswith("https://demo"):
            supabase_client = get_supabase_client()
            if not await supabase_client.test_connection():
                logger.warning("Failed to connect to Supabase - continuing in demo mode")
        else:
            logger.info("Running in demo mode - skipping database connection")
        
        # Создаем и запускаем бота
        bot = MedicalBot()
        
        # Проверяем демо-режим
        if bot.demo_mode:
            logger.info("Application started in demo mode. Waiting...")
            # В демо-режиме просто ждем бесконечно
            while True:
                await asyncio.sleep(60)
                logger.info("Demo mode: Still running...")
        elif settings.telegram_webhook_url:
            # Запускаем FastAPI сервер для webhook режима
            logger.info("Starting FastAPI webhook server")
            import uvicorn
            from src.api.webapp import app
            
            # Запускаем сервер
            config = uvicorn.Config(
                app,
                host=settings.app_host,
                port=settings.app_port,
                log_level=settings.log_level.lower()
            )
            server = uvicorn.Server(config)
            await server.serve()
        else:
            # Запускаем в режиме polling (для разработки)
            logger.info("Starting bot in polling mode")
            await bot.start_polling()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 