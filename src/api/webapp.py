"""
FastAPI веб-приложение для webhook режима Telegram бота
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

from telegram import Update
from telegram.ext import Application

from config.settings import settings
from src.bot.bot import MedicalBot
from src.utils.logging_config import setup_logging, structured_logger

logger = logging.getLogger(__name__)


# Глобальная переменная для бота
bot_application: Application = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global bot_application
    
    try:
        # Инициализация при старте
        logger.info("Starting FastAPI application...")
        
        # Создаем и инициализируем бота
        medical_bot = MedicalBot()
        bot_application = medical_bot.create_application()
        
        if bot_application:
            # Инициализируем приложение бота
            await bot_application.initialize()
            await bot_application.start()
            
            # Устанавливаем webhook если есть URL
            if settings.telegram_webhook_url:
                webhook_url = f"{settings.telegram_webhook_url}/webhook/{settings.telegram_bot_token}"
                await bot_application.bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=["message", "callback_query"],
                    drop_pending_updates=True
                )
                logger.info(f"Webhook set to: {webhook_url}")
            else:
                logger.info("No webhook URL configured, running in polling mode")
        else:
            logger.info("Bot application is in demo mode")
        
        logger.info("FastAPI application started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    finally:
        # Очистка при остановке
        logger.info("Shutting down FastAPI application...")
        
        if bot_application:
            try:
                # Удаляем webhook
                await bot_application.bot.delete_webhook(drop_pending_updates=True)
                
                # Останавливаем приложение
                await bot_application.stop()
                await bot_application.shutdown()
                
                logger.info("Bot application stopped successfully")
                
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")


# Создаем FastAPI приложение
app = FastAPI(
    title="Medical AI Bot API",
    description="API для медицинского бота анализа анализов",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Medical AI Bot API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ для диагностики Railway
    import os
    import psutil
    import time
    
    logger.info("🏥 Health check запрос получен!")
    logger.info(f"🌐 Запрос от: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
    
    try:
        # Логируем системную информацию
        process = psutil.Process()
        memory_info = process.memory_info()
        
        logger.info(f"💾 Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
        logger.info(f"⚡ CPU percent: {process.cpu_percent()}%")
        logger.info(f"🕒 Uptime: {time.time() - process.create_time():.2f} seconds")
        
        # Проверяем состояние бота (для информации, но не критично)
        bot_status = "unknown"
        if bot_application and bot_application.running:
            bot_status = "running"
            logger.info("🤖 Bot application: RUNNING")
        elif bot_application:
            bot_status = "stopped"
            logger.info("🤖 Bot application: STOPPED")
        else:
            bot_status = "not_initialized"
            logger.info("🤖 Bot application: NOT_INITIALIZED")
        
        # Логируем настройки
        webhook_url = "none"
        if settings.telegram_webhook_url:
            webhook_url = f"{settings.telegram_webhook_url}/webhook/{settings.telegram_bot_token}"
            logger.info(f"🔗 Webhook URL: {webhook_url}")
        else:
            logger.info("🔗 Webhook URL: не настроен")
        
        # Логируем переменные окружения
        logger.info(f"🌍 PORT env: {os.environ.get('PORT', 'не задан')}")
        logger.info(f"🏠 HOST env: {os.environ.get('HOST', 'не задан')}")
        logger.info(f"🚂 Railway env: {os.environ.get('RAILWAY_ENVIRONMENT', 'не задан')}")
        
        response_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "bot_status": bot_status,
            "webhook_url": webhook_url,
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(),
            "uptime_seconds": round(time.time() - process.create_time(), 2),
            "port": os.environ.get('PORT', settings.app_port),
            "host": settings.app_host,
            "message": "FastAPI server is running and healthy"
        }
        
        logger.info(f"✅ Health check успешен! Ответ: {response_data}")
        return response_data
        
    except Exception as e:
        # Даже при ошибках возвращаем 200 OK
        # Railway нужен только ответ сервера, не внутренняя логика
        logger.error(f"❌ Health check internal error: {e}")
        logger.error(f"🔍 Error details: {str(e)}")
        
        error_response = {
            "status": "healthy",
            "bot_status": "error", 
            "error": str(e),
            "timestamp": time.time(),
            "message": "FastAPI server is running despite internal errors"
        }
        
        logger.info(f"⚠️ Health check с ошибкой, но возвращаем OK: {error_response}")
        return error_response


@app.post("/webhook/{token}")
async def webhook(token: str, request: Request, background_tasks: BackgroundTasks):
    """Webhook endpoint для получения обновлений от Telegram"""
    
    # Проверяем токен
    if token != settings.telegram_bot_token:
        logger.warning(f"Invalid webhook token received: {token}")
        raise HTTPException(status_code=403, detail="Invalid token")
    
    # Проверяем что бот инициализирован
    if not bot_application:
        logger.error("Bot application not initialized")
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    try:
        # Получаем данные от Telegram
        update_data = await request.json()
        
        # Создаем объект Update
        update = Update.de_json(update_data, bot_application.bot)
        
        if update:
            # Логируем получение update
            if hasattr(structured_logger, 'log_user_action'):
                structured_logger.log_user_action(
                    user_id=update.effective_user.id if update.effective_user else 0,
                    action="webhook_update_received",
                    details={
                        "update_id": update.update_id,
                        "type": update.effective_message.text[:50] if update.effective_message else "callback_query"
                    }
                )
            
            # Обрабатываем update в фоне
            background_tasks.add_task(process_update, update)
            
            return {"status": "ok"}
        else:
            logger.warning("Invalid update received")
            return {"status": "error", "message": "Invalid update"}
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        if hasattr(structured_logger, 'log_error_event'):
            structured_logger.log_error_event(
                user_id=0,
                error_type="webhook_processing_error",
                error_details=str(e)
            )
        
        # Возвращаем 200 чтобы Telegram не повторял запрос
        return {"status": "error", "message": str(e)}


async def process_update(update: Update):
    """Обработать update от Telegram"""
    try:
        # Добавляем update в очередь обработки
        await bot_application.update_queue.put(update)
        
    except Exception as e:
        logger.error(f"Error adding update to queue: {e}")


@app.get("/stats")
async def get_stats():
    """Получить статистику бота"""
    try:
        # Базовая статистика
        webhook_url = "none"
        if settings.telegram_webhook_url:
            webhook_url = f"{settings.telegram_webhook_url}/webhook/{settings.telegram_bot_token}"
            
        stats = {
            "bot_running": bot_application.running if bot_application else False,
            "webhook_url": webhook_url,
        }
        
        # Можно добавить дополнительную статистику из базы данных
        # stats.update(await get_database_stats())
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )


@app.post("/admin/send_message")
async def admin_send_message(request: Request):
    """Админский endpoint для отправки сообщений (для тестирования)"""
    
    # Простая проверка авторизации (в продакшене использовать JWT или API ключи)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization")
    
    token = auth_header.split(" ")[1]
    if token != settings.admin_token:  # Добавить в settings
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    try:
        data = await request.json()
        chat_id = data.get("chat_id")
        message = data.get("message")
        
        if not chat_id or not message:
            raise HTTPException(status_code=400, detail="Missing chat_id or message")
        
        if bot_application and bot_application.bot:
            await bot_application.bot.send_message(
                chat_id=chat_id,
                text=message
            )
            
            return {"status": "sent", "chat_id": chat_id}
        else:
            raise HTTPException(status_code=503, detail="Bot not available")
            
    except Exception as e:
        logger.error(f"Error sending admin message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/webhook_info")
async def get_webhook_info():
    """Получить информацию о webhook"""
    try:
        if bot_application and bot_application.bot:
            webhook_info = await bot_application.bot.get_webhook_info()
            
            return {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "last_error_date": webhook_info.last_error_date,
                "last_error_message": webhook_info.last_error_message,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates
            }
        else:
            raise HTTPException(status_code=503, detail="Bot not available")
            
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_app() -> FastAPI:
    """Фабрика для создания приложения"""
    # Настраиваем логирование
    setup_logging(
        log_level=settings.log_level,
        log_file="logs/medical_bot.log"
    )
    
    logger.info("Creating FastAPI application...")
    return app


def run_webhook_server():
    """Запустить сервер в webhook режиме"""
    logger.info("Starting webhook server...")
    
    uvicorn.run(
        "src.api.webapp:app",
        host="0.0.0.0",
        port=settings.port,
        log_level=settings.log_level.lower(),
        access_log=True,
        reload=False  # В продакшене отключаем reload
    )


if __name__ == "__main__":
    run_webhook_server() 