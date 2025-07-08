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
        
        # Проверяем соединение с Supabase
        supabase_client = get_supabase_client()
        if not await supabase_client.test_connection():
            logger.error("Failed to connect to Supabase")
            return
        
        # Создаем и запускаем бота
        bot = MedicalBot()
        
        if settings.telegram_webhook_url:
            # Запускаем в режиме webhook (для продакшна)
            logger.info("Starting bot in webhook mode")
            await bot.start_webhook(
                webhook_url=settings.telegram_webhook_url,
                port=settings.app_port
            )
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