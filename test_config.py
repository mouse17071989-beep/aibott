#!/usr/bin/env python3
"""
Quick test script to verify bot configuration and connectivity
"""

import os
import sys
from dotenv import load_dotenv
import requests
import openai

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

print("=" * 60)
print("Telegram Code Bot - Configuration Test")
print("=" * 60)
print()

# Check environment variables
print("📋 Checking configuration...")
all_ok = True

if TELEGRAM_BOT_TOKEN:
    token_masked = TELEGRAM_BOT_TOKEN[:10] + "..." + TELEGRAM_BOT_TOKEN[-5:]
    print(f"✅ TELEGRAM_BOT_TOKEN: {token_masked}")
else:
    print("❌ TELEGRAM_BOT_TOKEN: NOT SET")
    all_ok = False

if OPENAI_API_KEY:
    key_masked = OPENAI_API_KEY[:5] + "..." + OPENAI_API_KEY[-5:]
    print(f"✅ OPENAI_API_KEY: {key_masked}")
else:
    print("❌ OPENAI_API_KEY: NOT SET")
    all_ok = False

if OPENAI_MODEL:
    print(f"✅ OPENAI_MODEL: {OPENAI_MODEL}")
else:
    print("❌ OPENAI_MODEL: NOT SET")
    all_ok = False

print()

# Test Telegram connection
print("🔗 Testing Telegram API connection...")
try:
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe",
        timeout=5,
    )
    if response.status_code == 200:
        data = response.json()
        bot_name = data.get("result", {}).get("username", "Unknown")
        print(f"✅ Telegram connection OK - Bot: @{bot_name}")
    else:
        print(f"❌ Telegram connection failed: {response.status_code}")
        all_ok = False
except Exception as e:
    print(f"❌ Telegram connection error: {e}")
    all_ok = False

print()

# Test OpenAI connection
print("🔗 Testing OpenAI API connection...")
try:
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, World!' and nothing else."}
        ],
        max_tokens=20,
    )

    if response.choices and len(response.choices) > 0:
        print(f"✅ OpenAI API connection OK")
        print(f"   Response: {response.choices[0].message.content}")
    else:
        print(f"❌ OpenAI API error: Unexpected response")
        all_ok = False
        
except Exception as e:
    error_str = str(e)
    if "insufficient_quota" in error_str or "quota" in error_str:
        print(f"⚠️  OpenAI API quota exceeded")
        print(f"   Info: Your free credits may have expired or been used up")
        print(f"   Solution: Go to https://platform.openai.com/account/billing/overview")
    elif "invalid_api_key" in error_str or "401" in error_str or "Incorrect API key" in error_str:
        print(f"❌ OpenAI authentication failed")
        print(f"   Check OPENAI_API_KEY in .env")
        all_ok = False
    else:
        print(f"❌ OpenAI API error: {error_str[:100]}")
        all_ok = False

print()
print("=" * 60)

if all_ok:
    print("✅ All checks passed! Bot is ready to run.")
    print()
    print("To start the bot, run:")
    print("  python main.py")
    sys.exit(0)
else:
    print("❌ Some checks failed. Please fix the issues above.")
    print()
    print("Common issues:")
    print("  - OpenAI quota: You've used up your free credits")
    print("  - Invalid API key: Check https://platform.openai.com/api-keys")
    print("  - Wrong model: Verify model exists in your OpenAI account")
    sys.exit(1)
