"""
Configuration module for Telegram Code Generation Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# NeuroAPI Configuration
NEURO_API_KEY = os.getenv("NEURO_API_KEY")
NEURO_API_ENDPOINT = os.getenv("NEURO_API_ENDPOINT", "https://neuroapi.host/v1")
NEURO_MODEL = os.getenv("NEURO_MODEL", "claude-opus-4-6")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Bot Settings
MAX_CONTEXT_MESSAGES = 10  # Maximum number of messages to keep in context
MAX_RESPONSE_LENGTH = 4000  # Maximum response length in characters
API_TIMEOUT = 30  # API request timeout in seconds
API_TEMPERATURE = 0.7  # Temperature for API (0-1, higher = more creative)
API_MAX_TOKENS = 2000  # Maximum tokens in response

# Conversation Settings
CLEAR_HISTORY_ON_START = False  # Clear user history when they use /start
ENABLE_USER_STATS = False  # Track user statistics

# Validation
def validate_config():
    """Validate that all required environment variables are set"""
    missing_vars = []

    if not TELEGRAM_BOT_TOKEN:
        missing_vars.append("TELEGRAM_BOT_TOKEN")

    if not NEURO_API_KEY:
        missing_vars.append("NEURO_API_KEY")

    if not NEURO_API_ENDPOINT:
        missing_vars.append("NEURO_API_ENDPOINT")

    if not NEURO_MODEL:
        missing_vars.append("NEURO_MODEL")

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return True
