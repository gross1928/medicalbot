"""
Основной класс Telegram бота
"""
import logging
from telegram import Update
from telegram.ext import Application, ContextTypes
from config.settings import settings
from .handlers import setup_handlers

logger = logging.getLogger(__name__)


class MedicalBot:
    """Основной класс медицинского бота"""
    
    def __init__(self):
        self.token = settings.telegram_bot_token
        self.application = None
        self.demo_mode = self.token in ["DEMO_TOKEN", "sk-demo"] or self.token.startswith("demo_")
    
    def create_application(self) -> Application:
        """Создать приложение бота"""
        if self.application is None:
            if self.demo_mode:
                logger.warning("Running in demo mode - bot functionality will be limited")
                # В демо-режиме создаем заглушку
                return None
            
            self.application = (
                Application.builder()
                .token(self.token)
                .build()
            )
            
            # Настройка обработчиков
            setup_handlers(self.application)
            logger.info("Bot application created and handlers configured")
        
        return self.application
    
    async def start_polling(self):
        """Запустить бота в режиме polling"""
        if self.demo_mode:
            logger.info("Demo mode: Would start polling here")
            return
            
        app = self.create_application()
        logger.info("Starting bot in polling mode...")
        await app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_webhook(self, webhook_url: str, port: int = 8000):
        """Запустить бота в режиме webhook"""
        if self.demo_mode:
            logger.info(f"Demo mode: Would start webhook on {webhook_url}:{port}")
            return
            
        app = self.create_application()
        logger.info(f"Starting bot in webhook mode on {webhook_url}:{port}")
        
        await app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES
        )
    
    async def process_update(self, update_data: dict):
        """Обработать обновление от webhook"""
        if self.demo_mode:
            logger.info(f"Demo mode: Would process update {update_data}")
            return
            
        if self.application is None:
            raise RuntimeError("Application not initialized")
        
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update) 