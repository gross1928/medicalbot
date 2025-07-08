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
    import os
    import time
    
    try:
        start_time = time.time()
        logger.info("🚀 Starting Medical AI Analyzer Bot...")
        
        # Логируем системную информацию
        logger.info(f"🐍 Python version: {sys.version}")
        logger.info(f"💻 Platform: {sys.platform}")
        logger.info(f"🚂 Railway environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
        logger.info(f"📂 Working directory: {os.getcwd()}")
        
        # Логируем настройки
        logger.info(f"⚙️ App host: {settings.app_host}")
        logger.info(f"⚙️ App port: {settings.app_port}")
        logger.info(f"⚙️ Log level: {settings.log_level}")
        logger.info(f"⚙️ Webhook URL: {settings.telegram_webhook_url or 'не задан'}")
        
        # Проверяем соединение с Supabase (необязательно для демо-режима)
        logger.info("🗄️ Проверяем соединение с базой данных...")
        if not settings.supabase_url.startswith("https://demo"):
            supabase_client = get_supabase_client()
            if not await supabase_client.test_connection():
                logger.warning("⚠️ Failed to connect to Supabase - continuing in demo mode")
            else:
                logger.info("✅ Supabase connection successful")
        else:
            logger.info("🎭 Running in demo mode - skipping database connection")
        
        # Создаем и запускаем бота
        logger.info("🤖 Создаём MedicalBot...")
        bot = MedicalBot()
        logger.info(f"🎭 Demo mode: {bot.demo_mode}")
        
        # Проверяем демо-режим
        if bot.demo_mode:
            logger.info("🎭 Application started in demo mode. Waiting...")
            # В демо-режиме просто ждем бесконечно
            while True:
                await asyncio.sleep(60)
                logger.info("🎭 Demo mode: Still running...")
        elif settings.telegram_webhook_url:
            # Запускаем FastAPI сервер для webhook режима
            import os
            import uvicorn
            from src.api.webapp import app
            
            # КРИТИЧНО: Railway ожидает приложение на $PORT
            railway_port = os.environ.get('PORT', settings.app_port)
            actual_host = settings.app_host
            actual_port = int(railway_port)
            
            logger.info("🚀 Starting FastAPI webhook server")
            logger.info(f"🌍 Host: {actual_host}")
            logger.info(f"🔌 Port: {actual_port} (Railway PORT env: {os.environ.get('PORT', 'не задан')})")
            logger.info(f"📝 Log level: {settings.log_level.lower()}")
            logger.info(f"🚂 Railway environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'не задан')}")
            logger.info(f"🔗 Webhook URL: {settings.telegram_webhook_url}")
            
            # Запускаем сервер с Railway-оптимизированными настройками
            config = uvicorn.Config(
                app,
                host="0.0.0.0",        # Explicit binding для Railway
                port=actual_port,      # $PORT от Railway
                log_level=settings.log_level.lower(),
                access_log=True,       # Включаем access логи
                use_colors=False,      # Отключаем цвета для Railway логов
                server_header=False,   # Убираем server header
                timeout_keep_alive=30, # Keep-alive timeout
                timeout_graceful_shutdown=30,  # Graceful shutdown
                workers=1,             # Single worker для Railway
                loop="asyncio",        # Explicit event loop
                interface="asgi3",     # ASGI3 interface
                reload=False,          # Disable reload in production
                limit_concurrency=100, # Connection limit
                limit_max_requests=1000,  # Request limit per worker
                backlog=2048           # Socket backlog
            )
            server = uvicorn.Server(config)
            
            logger.info(f"🎯 Сервер будет слушать на {actual_host}:{actual_port}")
            
            # Railway диагностика
            logger.info(f"🚂 Railway PORT env var: {os.environ.get('PORT', 'не задан')}")
            logger.info(f"🌐 Railway URL env var: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'не задан')}")
            logger.info(f"🔗 Full Railway URL: https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'unknown')}")
            logger.info(f"⚙️ Uvicorn config: workers=1, interface=asgi3, backlog=2048")
            
            # Проверяем что порт свободен
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((actual_host, actual_port))
                sock.close()
                logger.info(f"✅ Port {actual_port} is available for binding")
            except OSError as e:
                logger.warning(f"⚠️ Port {actual_port} binding check failed: {e}")
            
            await server.serve()
        else:
            # Запускаем в режиме polling (для разработки)
            logger.info("🔄 Starting bot in polling mode")
            await bot.start_polling()
            
        # Если дошли сюда, всё прошло успешно
        elapsed = time.time() - start_time
        logger.info(f"🎉 Application started successfully in {elapsed:.2f} seconds")
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR starting bot: {e}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📍 Error details: {str(e)}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        raise  # Перебрасываем ошибку чтобы Railway видел failure


if __name__ == "__main__":
    asyncio.run(main()) 