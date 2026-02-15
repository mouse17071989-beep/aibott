#!/usr/bin/env python3
"""
Test script to verify Ollama connection and bot configuration
"""

import os
import sys
from dotenv import load_dotenv
import requests
from tabulate import tabulate

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

print("=" * 70)
print("🤖 Telegram Code Bot - Ollama Configuration Test")
print("=" * 70)
print()

# Check environment variables
print("📋 Checking configuration...")
config_data = []

if TELEGRAM_BOT_TOKEN:
    token_masked = TELEGRAM_BOT_TOKEN[:10] + "..." + TELEGRAM_BOT_TOKEN[-5:]
    config_data.append(["✅", "TELEGRAM_BOT_TOKEN", token_masked])
else:
    print("❌ TELEGRAM_BOT_TOKEN: NOT SET")
    config_data.append(["❌", "TELEGRAM_BOT_TOKEN", "NOT SET"])

config_data.append(["ℹ️", "OLLAMA_API_URL", OLLAMA_API_URL])
config_data.append(["ℹ️", "OLLAMA_MODEL", OLLAMA_MODEL])

print(tabulate(config_data, headers=["Status", "Variable", "Value"], tablefmt="grid"))
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
except Exception as e:
    print(f"❌ Telegram connection error: {e}")

print()

# Test Ollama connection
print("🔗 Testing Ollama API connection...")
try:
    # First check if Ollama server is running
    ollama_base_url = OLLAMA_API_URL.replace("/api/chat", "")
    
    response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        
        if models:
            print(f"✅ Ollama server is running at {ollama_base_url}")
            print(f"   Available models:")
            for model in models:
                model_name = model.get("name", "Unknown")
                is_requested = "🎯" if model_name.split(":")[0] == OLLAMA_MODEL.split(":")[0] else "  "
                print(f"     {is_requested} {model_name}")
            
            # Check if requested model is available
            available_model_names = [m.get("name", "").split(":")[0] for m in models]
            if OLLAMA_MODEL.split(":")[0] in available_model_names:
                print(f"\n✅ Requested model '{OLLAMA_MODEL}' is available")
            else:
                print(f"\n⚠️  Requested model '{OLLAMA_MODEL}' is NOT available")
                print(f"   Pull it with: ollama pull {OLLAMA_MODEL}")
        else:
            print(f"⚠️  Ollama server is running but no models are installed")
            print(f"   Pull a model: ollama pull {OLLAMA_MODEL}")
    else:
        print(f"❌ Ollama server not responding: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print(f"❌ Cannot connect to Ollama at {ollama_base_url}")
    print(f"   Make sure Ollama is installed and running:")
    print(f"   1. Download from https://ollama.ai")
    print(f"   2. Run: ollama serve")
    print(f"   3. In another terminal: ollama pull {OLLAMA_MODEL}")
except Exception as e:
    print(f"❌ Ollama connection error: {e}")

print()
print("=" * 70)
print("✅ Setup Instructions:")
print("=" * 70)
print("""
1. Install Ollama from https://ollama.ai
2. Start Ollama server:
   ollama serve

3. In another terminal, pull a model:
   ollama pull mistral      # Fast and good quality
   ollama pull neural-chat  # Faster, smaller
   ollama pull orca-mini    # Even lighter

4. Start the bot:
   python main.py

5. In Telegram, find your bot and send a message!
""")
print("=" * 70)
