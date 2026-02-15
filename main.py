#!/usr/bin/env python3
"""
Telegram Bot for AI-powered Code Generation using OpenRouter API
"""

import os
import logging
from typing import Optional, Dict, List
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import json
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL),
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "arcee-ai/trinity-large-preview:free")
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")

# Conversation states
CODE_REQUEST = 1
WAITING_FOR_CODE = 2

# Store user conversations for context
user_conversations: Dict[int, List[Dict]] = {}

MAX_CONTEXT_MESSAGES = 10
MAX_RESPONSE_LENGTH = 4000


class CodeGenerationBot:
    """Telegram bot for AI-powered code generation using OpenRouter"""

    def __init__(self):
        self.api_url = f"{OPENROUTER_API_URL}/chat/completions"
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        logger.info(f"Bot initialized with OpenRouter model: {self.model}")
        logger.info(f"OpenRouter API: {OPENROUTER_API_URL}")

    def _get_conversation_context(self, user_id: int) -> str:
        """Get conversation context for the user"""
        if user_id not in user_conversations:
            return ""

        messages = user_conversations[user_id][-MAX_CONTEXT_MESSAGES:]
        context = "\n".join([f"[{msg['role']}]: {msg['content'][:100]}" for msg in messages])
        return context

    def _add_to_conversation(self, user_id: int, role: str, content: str):
        """Add message to conversation history"""
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        user_conversations[user_id].append({"role": role, "content": content, "timestamp": datetime.now()})

        # Keep only recent messages
        if len(user_conversations[user_id]) > MAX_CONTEXT_MESSAGES * 2:
            user_conversations[user_id] = user_conversations[user_id][-MAX_CONTEXT_MESSAGES:]

    def call_openrouter_api(self, messages: List[Dict]) -> Optional[str]:
        """Call OpenRouter API for code generation"""
        try:
            logger.debug(f"Calling OpenRouter API with {len(messages)} messages...")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/user/telegram-code-bot",
                "X-Title": "Telegram Code Bot",
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000,
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    logger.debug(f"Got response from OpenRouter: {len(content)} chars")
                    return content
                else:
                    logger.error(f"Unexpected OpenRouter response: {data}")
                    return None
            else:
                error_msg = response.text
                logger.error(f"OpenRouter API error: {response.status_code} - {error_msg}")
                if "invalid_api_key" in error_msg.lower() or "401" in str(response.status_code):
                    logger.error("Invalid API key! Check OPENROUTER_API_KEY in .env")
                return None

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to OpenRouter. Check internet connection!")
            return None
        except Exception as e:
            logger.error(f"OpenRouter API call failed: {str(e)}")
            return None

    def _format_code_response(self, response: str) -> str:
        """Format AI response for better readability in Telegram"""
        if len(response) > MAX_RESPONSE_LENGTH:
            response = response[: MAX_RESPONSE_LENGTH - 100] + "\n\n[...response truncated...]"

        # Add code block formatting if response contains code
        if "```" not in response and any(keyword in response.lower() for keyword in ["def ", "class ", "import ", "function"]):
            response = f"```python\n{response}\n```"

        return response

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        logger.info(f"User {user.id} started the bot")

        welcome_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "🤖 Я твой AI-бот для написания кодов на OpenRouter (бесплатно!)\n\n"
            "📝 Отправь мне:\n"
            "• /code - начать писать код\n"
            "• /help - справка по командам\n"
            "• Любое сообщение с описанием кода\n\n"
            "⚡ Я быстро сгенерирую нужный код!"
        )

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = (
            "📚 Доступные команды:\n\n"
            "/start - Начать работу\n"
            "/code - Начать писать код\n"
            "/help - Эта справка\n"
            "/cancel - Отменить текущую операцию\n\n"
            "💡 Примеры запросов:\n"
            "• Напиши функцию для сортировки массива\n"
            "• Создай REST API на Python с FastAPI\n"
            "• Как сделать Authentication в Node.js?\n\n"
            "🔄 Я помню контекст переписки, можешь задавать уточняющие вопросы!"
        )

        await update.message.reply_text(help_text)

    async def code_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Code generation command handler"""
        await update.message.reply_text(
            "📝 Отлично! Описывай, какой код тебе нужен.\n"
            "Например: 'Напиши функцию для проверки палиндрома на Python'\n\n"
            "/cancel - отменить"
        )
        return WAITING_FOR_CODE

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel handler"""
        await update.message.reply_text("Отменено ✋\n\nИспользуй /help для справки по командам.")
        return ConversationHandler.END

    async def handle_code_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle code generation requests"""
        user_id = update.effective_user.id
        user_message = update.message.text

        logger.info(f"User {user_id} requested: {user_message[:50]}...")

        # Add user message to conversation
        self._add_to_conversation(user_id, "user", user_message)

        # Show typing indicator
        await update.message.chat.send_action("typing")

        # Prepare messages for API
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты - опытный программист и помощник по написанию кода. "
                    "Генерируй чистый, хорошо структурированный код с комментариями. "
                    "Всегда объясняй что ты делаешь. "
                    "Предпочитай полезные ответы с примерами использования."
                ),
            }
        ]

        # Add conversation history
        if user_id in user_conversations:
            for msg in user_conversations[user_id][-MAX_CONTEXT_MESSAGES :]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Get response from OpenRouter
        response = self.call_openrouter_api(messages)

        if response:
            # Add assistant response to conversation
            self._add_to_conversation(user_id, "assistant", response)

            # Format and send response
            formatted_response = self._format_code_response(response)

            await update.message.reply_text(formatted_response, parse_mode="Markdown")

            logger.info(f"Successfully generated code for user {user_id}")
        else:
            await update.message.reply_text(
                "❌ Ошибка при обращении к OpenRouter API.\n"
                "Проверь API ключ в .env и интернет соединение."
            )
            logger.error(f"Failed to get response for user {user_id}")

        return ConversationHandler.END

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        user_message = update.message.text

        logger.info(f"User {user_id} sent message: {user_message[:50]}...")

        # Add user message to conversation
        self._add_to_conversation(user_id, "user", user_message)

        # Show typing indicator
        await update.message.chat.send_action("typing")

        # Prepare messages for API
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты - опытный программист и помощник по написанию кода. "
                    "Генерируй чистый, хорошо структурированный код с комментариями. "
                    "Всегда объясняй что ты делаешь. "
                    "Предпочитай полезные ответы с примерами использования."
                ),
            }
        ]

        # Add conversation history
        if user_id in user_conversations:
            for msg in user_conversations[user_id][-MAX_CONTEXT_MESSAGES :]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Get response from OpenRouter
        response = self.call_openrouter_api(messages)

        if response:
            # Add assistant response to conversation
            self._add_to_conversation(user_id, "assistant", response)

            # Format and send response
            formatted_response = self._format_code_response(response)

            await update.message.reply_text(formatted_response, parse_mode="Markdown")

            logger.info(f"Successfully responded to user {user_id}")
        else:
            await update.message.reply_text(
                "❌ Ошибка при обращении к OpenRouter API.\n"
                "Проверь API ключ в .env и интернет соединение."
            )
            logger.error(f"Failed to get response for user {user_id}")


def main():
    """Main function to start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env")
        exit(1)
    
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set in .env")
        exit(1)

    logger.info("Starting Telegram Code Generation Bot with OpenRouter API...")

    # Create bot instance
    bot_instance = CodeGenerationBot()

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("code", bot_instance.code_command)],
        states={WAITING_FOR_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_code_request)]},
        fallbacks=[CommandHandler("cancel", bot_instance.cancel)],
    )

    # Define error handler
    async def error_handler(update, context):
        """Log errors and handle them gracefully"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)
        # Don't re-raise if it's a conflict error - just log it
        if "Conflict" not in str(context.error):
            raise context.error

    # Register error handler
    application.add_error_handler(error_handler)

    # Register handlers
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(CommandHandler("help", bot_instance.help_command))
    application.add_handler(CommandHandler("cancel", bot_instance.cancel))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_message))

    # Start the bot
    logger.info("Bot started. Waiting for messages...")

    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")


if __name__ == "__main__":
    main()
