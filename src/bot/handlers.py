"""
Обработчики команд и сообщений Telegram бота
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

from src.database import UserRepository, AnalysisRepository
from src.models import UserCreate
from src.ai.analyzer import MedicalAnalyzer
from src.file_processing.processor import FileProcessor

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Регистрируем пользователя в базе данных
    user_repo = UserRepository()
    
    try:
        existing_user = await user_repo.get_user_by_telegram_id(user.id)
        if not existing_user:
            # Создаем нового пользователя
            user_data = UserCreate(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            await user_repo.create_user(user_data)
            logger.info(f"New user registered: {user.id}")
    
    except Exception as e:
        logger.error(f"Error registering user: {e}")
    
    welcome_message = """
🏥 **Добро пожаловать в Медицинский ИИ-Анализатор!**

Я помогу вам анализировать медицинские показатели и давать персонализированные рекомендации по улучшению здоровья.

**Что я умею:**
📊 Анализировать результаты анализов крови, мочи и других показателей
🤖 Интерпретировать ваши медицинские данные с помощью ИИ
💡 Давать рекомендации по питанию, спорту и образу жизни
📈 Отслеживать динамику ваших показателей

**Как пользоваться:**
1. Отправьте файл с анализами
2. Я извлеку и проанализирую ваши показатели
3. Получите персонализированные рекомендации

**⚠️ Важно:** Рекомендации носят информационный характер и не заменяют консультацию врача!

Готовы начать? Отправьте файл с вашими анализами! 📋
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Загрузить анализ", callback_data="upload_guide")],
        [InlineKeyboardButton("📚 Инструкция", callback_data="help")],
        [InlineKeyboardButton("👤 Мой профиль", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = """
📚 **Инструкция по использованию**

**Поддерживаемые форматы:**
• PDF файлы (результаты лабораторий)  
• Изображения анализов (JPG, PNG, JPEG)
• Максимальный размер: 20 МБ

**Поддерживаемые анализы:**
• Общий анализ крови
• Биохимический анализ крови
• Гормональные исследования
• Анализы мочи
• Витамины и микроэлементы

**Команды:**
/start - Главное меню
/help - Эта инструкция
/history - История анализов
/profile - Настройки профиля

**Как получить лучшие результаты:**
1. Загружайте четкие фото/сканы
2. Убедитесь, что текст читаем
3. Укажите ваш возраст и пол в профиле

**Безопасность:** Все данные шифруются и доступны только вам.
"""
    
    await update.message.reply_text(help_message, parse_mode='Markdown')


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /profile"""
    user_id = update.effective_user.id
    user_repo = UserRepository()
    
    try:
        user = await user_repo.get_user_by_telegram_id(user_id)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден. Используйте /start для регистрации.")
            return
        
        profile_text = f"""
👤 **Ваш профиль**

**Основная информация:**
• Имя: {user.first_name or 'Не указано'}
• Username: @{user.username or 'Не указан'}
• Возраст: {user.age or 'Не указан'}
• Пол: {user.gender or 'Не указан'}
• Рост: {user.height or 'Не указан'} см
• Вес: {user.weight or 'Не указан'} кг

**Статистика:**
• Дата регистрации: {user.created_at.strftime('%d.%m.%Y')}
• Статус: {'Активен' if user.is_active else 'Неактивен'}

Для более точных рекомендаций заполните данные о возрасте, поле и физических параметрах.
"""
        
        keyboard = [
            [InlineKeyboardButton("✏️ Редактировать профиль", callback_data="edit_profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        await update.message.reply_text("❌ Ошибка получения профиля.")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /history"""
    user_id = update.effective_user.id
    user_repo = UserRepository()
    analysis_repo = AnalysisRepository()
    
    try:
        user = await user_repo.get_user_by_telegram_id(user_id)
        if not user:
            await update.message.reply_text("❌ Пользователь не найден.")
            return
        
        analyses = await analysis_repo.get_user_analyses(user.id, limit=10)
        
        if not analyses:
            await update.message.reply_text("📋 У вас пока нет загруженных анализов.")
            return
        
        history_text = "📊 **История ваших анализов:**\n\n"
        
        for i, analysis in enumerate(analyses, 1):
            status_emoji = {
                "completed": "✅",
                "processing": "⏳",
                "failed": "❌",
                "pending": "🕐"
            }.get(analysis.status, "❓")
            
            history_text += f"{i}. {status_emoji} **{analysis.original_filename}**\n"
            history_text += f"   📅 {analysis.uploaded_at.strftime('%d.%m.%Y %H:%M')}\n"
            history_text += f"   📋 Статус: {analysis.status}\n\n"
        
        await update.message.reply_text(history_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        await update.message.reply_text("❌ Ошибка получения истории.")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженных файлов"""
    user_id = update.effective_user.id
    document = update.message.document
    
    # Проверяем размер файла
    max_size_mb = 20
    if document.file_size > max_size_mb * 1024 * 1024:
        await update.message.reply_text(
            f"❌ Файл слишком большой! Максимальный размер: {max_size_mb} МБ"
        )
        return
    
    # Проверяем тип файла
    from config.settings import settings
    allowed_types = settings.supported_file_types
    file_extension = document.file_name.split('.')[-1].lower()
    
    if file_extension not in allowed_types:
        await update.message.reply_text(
            f"❌ Неподдерживаемый формат файла!\n"
            f"Поддерживаемые форматы: {', '.join(allowed_types).upper()}"
        )
        return
    
    # Отправляем сообщение о начале обработки
    processing_message = await update.message.reply_text(
        "⏳ Загружаю и обрабатываю ваш файл... Это может занять несколько минут."
    )
    
    try:
        # Загружаем файл
        file_processor = FileProcessor()
        analysis_result = await file_processor.process_file(
            document, user_id, update.effective_chat.id
        )
        
        if analysis_result:
            await processing_message.edit_text("✅ Анализ завершен! Формирую отчет...")
            
            # Здесь будет вызов ИИ-анализатора
            analyzer = MedicalAnalyzer()
            recommendations = await analyzer.analyze_results(analysis_result)
            
            # Отправляем результаты пользователю
            await send_analysis_results(update, analysis_result, recommendations)
        else:
            await processing_message.edit_text(
                "❌ Не удалось обработать файл. Убедитесь, что файл содержит медицинские данные."
            )
    
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        await processing_message.edit_text(
            "❌ Произошла ошибка при обработке файла. Попробуйте еще раз."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик загруженных фотографий"""
    user_id = update.effective_user.id
    photo = update.message.photo[-1]  # Берем фото наибольшего размера
    
    processing_message = await update.message.reply_text(
        "⏳ Обрабатываю фотографию анализа..."
    )
    
    try:
        file_processor = FileProcessor()
        analysis_result = await file_processor.process_photo(
            photo, user_id, update.effective_chat.id
        )
        
        if analysis_result:
            await processing_message.edit_text("✅ Анализ завершен!")
            
            analyzer = MedicalAnalyzer()
            recommendations = await analyzer.analyze_results(analysis_result)
            
            await send_analysis_results(update, analysis_result, recommendations)
        else:
            await processing_message.edit_text(
                "❌ Не удалось извлечь данные из фотографии. "
                "Убедитесь, что текст четкий и читаемый."
            )
    
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await processing_message.edit_text("❌ Ошибка обработки фотографии.")


async def send_analysis_results(update: Update, analysis, recommendations):
    """Отправить результаты анализа пользователю"""
    try:
        # Формируем отчет
        report = f"📊 **Результаты анализа**\n\n"
        
        if analysis.biomarkers:
            report += "**Ваши показатели:**\n"
            for biomarker in analysis.biomarkers[:10]:  # Показываем первые 10
                status_emoji = {
                    "normal": "✅",
                    "low": "🔽",
                    "high": "🔼",
                    "critical_low": "⚠️",
                    "critical_high": "⚠️"
                }.get(biomarker.status, "❓")
                
                report += f"{status_emoji} **{biomarker.name}**: {biomarker.value}"
                if biomarker.unit:
                    report += f" {biomarker.unit}"
                report += "\n"
        
        report += "\n💡 **Персонализированные рекомендации:**\n"
        
        if recommendations:
            for rec in recommendations[:5]:  # Показываем топ-5 рекомендаций
                category_emoji = {
                    "nutrition": "🥗",
                    "exercise": "💪",
                    "supplements": "💊",
                    "lifestyle": "🏃‍♂️",
                    "medical": "👨‍⚕️"
                }.get(rec.category, "💡")
                
                report += f"\n{category_emoji} **{rec.category.title()}:**\n"
                report += f"{rec.recommendation_text}\n"
        
        report += "\n⚠️ **Важно:** Это информационные рекомендации. Обязательно проконсультируйтесь с врачом!"
        
        await update.message.reply_text(report, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error sending analysis results: {e}")
        await update.message.reply_text("❌ Ошибка формирования отчета.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "upload_guide":
        guide_text = """
📋 **Как загрузить анализ:**

1. **Нажмите 📎 (скрепка)** в поле ввода сообщения
2. **Выберите файл** или **сделайте фото**
3. **Отправьте файл** боту
4. **Дождитесь результата** (1-3 минуты)

**Поддерживаемые форматы:**
• PDF файлы лабораторий
• Фото анализов (JPG, PNG, JPEG)
• Максимальный размер: 20 МБ

**Для лучшего результата:**
📸 Делайте четкие фото
💡 Хорошее освещение
📏 Полностью видимый текст
"""
        await query.edit_message_text(guide_text, parse_mode='Markdown')
    
    elif query.data == "help":
        await help_command(update, context)
    
    elif query.data == "profile":
        await profile_command(update, context)


def setup_handlers(application: Application):
    """Настройка всех обработчиков бота"""
    
    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("history", history_command))
    
    # Файлы и фото
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Inline кнопки
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("All handlers configured successfully") 