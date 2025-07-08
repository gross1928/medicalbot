"""
FastAPI веб-приложение для webhook режима Telegram бота
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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
                logger.info(f"🔗 Настраиваем webhook: {webhook_url}")
                
                # Добавляем задержку для готовности Railway proxy
                import asyncio
                logger.info("⏳ Ждем готовности Railway proxy (5 сек)...")
                await asyncio.sleep(5)
                
                # Retry логика для webhook установки
                max_retries = 3
                retry_delay = 10  # секунд
                
                for attempt in range(max_retries):
                    try:
                        logger.info(f"🔄 Попытка установки webhook {attempt + 1}/{max_retries}")
                        
                        await bot_application.bot.set_webhook(
                            url=webhook_url,
                            allowed_updates=["message", "callback_query"],
                            drop_pending_updates=True
                        )
                        
                        # Проверяем что webhook действительно установлен
                        await asyncio.sleep(2)  # Небольшая задержка перед проверкой
                        webhook_info = await bot_application.bot.get_webhook_info()
                        
                        if webhook_info.url == webhook_url:
                            logger.info(f"✅ Webhook set successfully to: {webhook_url}")
                            logger.info(f"📊 Webhook info: URL={webhook_info.url}, pending={webhook_info.pending_update_count}")
                            break
                        else:
                            logger.warning(f"⚠️ Webhook URL mismatch: expected={webhook_url}, got={webhook_info.url}")
                            if attempt < max_retries - 1:
                                logger.info(f"⏳ Retry через {retry_delay} секунд...")
                                await asyncio.sleep(retry_delay)
                            else:
                                logger.error("❌ Failed to set webhook after all retries")
                                
                    except Exception as e:
                        logger.error(f"❌ Webhook attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries - 1:
                            logger.info(f"⏳ Retry через {retry_delay} секунд...")
                            await asyncio.sleep(retry_delay)
                        else:
                            logger.error("❌ Failed to set webhook after all retries")
                            # Не прерываем startup - приложение может работать без webhook
            else:
                logger.info("⚠️ No webhook URL configured, running in polling mode")
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
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
    openapi_url="/openapi.json"
)

# Добавляем CORS middleware для Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логируем все входящие запросы для диагностики Railway"""
    import time
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(f"🌐 Incoming request: {request.method} {request.url}")
    logger.info(f"🔍 Headers: {dict(request.headers)}")
    logger.info(f"📍 Client: {request.client}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"✅ Response: {response.status_code} in {process_time:.4f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Request failed: {e} in {process_time:.4f}s")
        raise


@app.get("/")
async def root():
    """Корневой endpoint"""
    import time
    import os
    
    logger.info("🏠 Root endpoint запрос получен!")
    
    response = {
        "message": "Medical AI Bot API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": time.time(),
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
        "port": os.environ.get('PORT', 'unknown'),
        "uptime": "healthy"
    }
    
    logger.info(f"🏠 Root endpoint ответ: {response}")
    return response

@app.get("/ping") 
async def ping():
    """Простейший ping endpoint для тестирования"""
    import time
    logger.info("🏓 Ping запрос получен!")
    return {"ping": "pong", "timestamp": time.time()}


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
    
    logger.info(f"📨 WEBHOOK запрос получен! Token: {token[:10]}...")
    logger.info(f"🔍 Request headers: {dict(request.headers)}")
    logger.info(f"📍 Client IP: {request.client}")
    
    # Проверяем токен
    if token != settings.telegram_bot_token:
        logger.warning(f"❌ Invalid webhook token received: {token}")
        logger.warning(f"📝 Expected: {settings.telegram_bot_token[:10]}...")
        raise HTTPException(status_code=403, detail="Invalid token")
    
    logger.info("✅ Webhook token valid")
    
    # Проверяем что бот инициализирован
    if not bot_application:
        logger.error("❌ Bot application not initialized")
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    logger.info("✅ Bot application ready")
    
    try:
        # Получаем данные от Telegram
        logger.info("📥 Получаем JSON данные от Telegram...")
        update_data = await request.json()
        logger.info(f"📊 Update data received: {str(update_data)[:200]}...")
        
        # Создаем объект Update
        logger.info("🔄 Создаём Telegram Update объект...")
        update = Update.de_json(update_data, bot_application.bot)
        
        if update:
            logger.info(f"✅ Update создан успешно! ID: {update.update_id}")
            
            # Логируем детали update
            if update.effective_user:
                logger.info(f"👤 User: {update.effective_user.first_name} (ID: {update.effective_user.id})")
            
            if update.effective_message:
                message_text = update.effective_message.text or "no text"
                logger.info(f"💬 Message: {message_text[:100]}...")
            
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
            logger.info("🚀 Добавляем update в фоновую обработку...")
            background_tasks.add_task(process_update, update)
            
            logger.info("✅ Webhook обработан успешно!")
            return {"status": "ok"}
        else:
            logger.warning("❌ Invalid update received - не удалось создать Update объект")
            return {"status": "error", "message": "Invalid update"}
            
    except Exception as e:
        logger.error(f"💥 ОШИБКА обработки webhook: {e}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        logger.error(f"📍 Error details: {str(e)}")
        import traceback
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        
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


@app.get("/debug")
async def debug_info():
    """Debug endpoint для Railway диагностики"""
    import os
    import socket
    import sys
    import time
    
    logger.info("🔧 Debug endpoint запрос получен!")
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        debug_data = {
            "environment": {
                "PORT": os.environ.get('PORT', 'not set'),
                "HOST": os.environ.get('HOST', 'not set'),
                "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT', 'not set'),
                "RAILWAY_PUBLIC_DOMAIN": os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'not set'),
                "RAILWAY_PROJECT_ID": os.environ.get('RAILWAY_PROJECT_ID', 'not set'),
                "RAILWAY_SERVICE_ID": os.environ.get('RAILWAY_SERVICE_ID', 'not set')
            },
            "system": {
                "hostname": hostname,
                "local_ip": local_ip,
                "python_version": sys.version,
                "platform": sys.platform
            },
            "application": {
                "settings_app_port": settings.app_port,
                "settings_app_host": settings.app_host,
                "webhook_url": settings.telegram_webhook_url,
                "bot_token_set": bool(settings.telegram_bot_token != "DEMO_TOKEN")
            },
            "status": "debug_ok",
            "timestamp": time.time()
        }
        
        logger.info(f"🔧 Debug info: {debug_data}")
        return debug_data
        
    except Exception as e:
        error_data = {
            "error": str(e),
            "status": "debug_error",
            "timestamp": time.time()
        }
        logger.error(f"❌ Debug endpoint error: {error_data}")
        return error_data


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