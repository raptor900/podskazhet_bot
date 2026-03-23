import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from bot.config import Config
from bot.knowledge_base import KnowledgeBaseManager
from bot.utils import save_user_query, format_structured_response

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize knowledge base manager
kb_manager = KnowledgeBaseManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    await update.message.reply_text(
        "👋 Привет! Я бот технической поддержки.\n\n"
        "Я могу отвечать на вопросы, используя базу знаний.\n"
        "Просто задайте свой вопрос, и я постараюсь найти ответ в документации.\n\n"
        "Доступные команды:\n"
        "/start - Показать это сообщение\n"
        "/rebuild - Перестроить индекс базы знаний (только для администратора)"
    )


async def rebuild_index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rebuild the knowledge base index (admin only)"""
    user_id = update.effective_user.id

    # Check if user is admin (you can modify this list)
    admin_ids = [192510379]  # Yuriy's Telegram ID

    if admin_ids and user_id not in admin_ids:
        await update.message.reply_text("⛔ У вас нет прав для выполнения этой команды.")
        return

    await update.message.reply_text("🔄 Перестраиваю индекс базы знаний...")

    try:
        kb_manager.rebuild_index()
        await update.message.reply_text("✅ Индекс успешно перестроен!")
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        await update.message.reply_text(f"❌ Ошибка при перестроении индекса: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user = update.effective_user
    question = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Get answer from knowledge base
        answer, sources = kb_manager.answer_question(question)

        # Format response
        response = format_structured_response(answer, sources)

        # Save query to file
        save_user_query(
            user_id=user.id,
            username=user.username or user.first_name,
            question=question,
            answer=answer,
            context_used=sources
        )

        # Send response
        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rebuild", rebuild_index))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
