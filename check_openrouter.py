#!/usr/bin/env python3
"""
OpenRouter API Connectivity Check Script

This script verifies that your OpenRouter API connection is working properly.
It checks:
1. API key validity
2. Network connectivity to OpenRouter
3. Available models
4. Basic inference capability

Usage:
    python check_openrouter.py
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "arcee-ai/trinity-large-preview:free")


def check_api_key_format() -> bool:
    """Check if API key has correct format"""
    logger.info("Checking API key format...")
    
    if not OPENROUTER_API_KEY:
        logger.error("❌ OPENROUTER_API_KEY is not set in .env file")
        return False
    
    if OPENROUTER_API_KEY.startswith("sk-or-v1-"):
        logger.info(f"✓ API key format looks valid (starts with 'sk-or-v1-')")
        return True
    else:
        logger.warning("⚠️  API key doesn't start with 'sk-or-v1-' - might be invalid")
        return False


def test_api_connectivity() -> bool:
    """Test basic connectivity to OpenRouter API"""
    logger.info(f"\nTesting connectivity to {OPENROUTER_API_URL}...")
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/user/telegram-code-bot",
            "X-Title": "Telegram Code Bot",
        }
        
        # Simple test - get models list
        response = requests.get(
            f"{OPENROUTER_API_URL}/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✓ Successfully connected to OpenRouter API")
            return True
        elif response.status_code == 401:
            logger.error("❌ Authentication failed - Invalid API key")
            logger.error(f"Response: {response.text}")
            return False
        else:
            logger.error(f"❌ API returned error {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection failed - Cannot reach OpenRouter API")
        logger.error("Make sure you have internet connection and the URL is correct")
        return False
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out - OpenRouter API is not responding")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False


def list_available_models() -> Optional[Dict[str, Any]]:
    """List available models from OpenRouter"""
    logger.info("\nFetching available models...")
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        response = requests.get(
            f"{OPENROUTER_API_URL}/models",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            models = response.json()
            logger.info(f"✓ Retrieved {len(models.get('data', []))} available models")
            
            # Show some free models
            free_models = [
                m for m in models.get('data', [])
                if m.get('pricing', {}).get('prompt') == '0' or 'free' in m.get('id', '').lower()
            ]
            
            if free_models:
                logger.info(f"\nFound {len(free_models)} free models:")
                for model in free_models[:5]:  # Show first 5
                    logger.info(f"  - {model.get('id')}")
                if len(free_models) > 5:
                    logger.info(f"  ... and {len(free_models) - 5} more")
            
            return models
        else:
            logger.error(f"Failed to fetch models: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return None


def test_inference() -> bool:
    """Test basic inference capability"""
    logger.info(f"\nTesting inference with model: {OPENROUTER_MODEL}...")
    logger.info("(This tests if your API key can make actual requests)")
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/user/telegram-code-bot",
            "X-Title": "Telegram Code Bot",
        }
        
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
        }
        
        response = requests.post(
            f"{OPENROUTER_API_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            logger.info("✓ Inference test successful!")
            logger.info(f"Response: {reply[:100]}...")
            return True
        elif response.status_code == 401:
            logger.error("❌ Invalid API key - authentication failed")
            return False
        elif response.status_code == 429:
            logger.warning("⚠️  Rate limit exceeded - too many requests")
            return False
        else:
            logger.error(f"❌ Inference failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Inference test error: {e}")
        return False


def print_summary(results: Dict[str, bool]) -> None:
    """Print summary of all checks"""
    logger.info("\n" + "="*50)
    logger.info("SUMMARY")
    logger.info("="*50)
    
    checks = [
        ("API Key Format", results.get("format")),
        ("API Connectivity", results.get("connectivity")),
        ("Inference Test", results.get("inference")),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for check_name, result in checks:
        status = "✓" if result else "❌"
        logger.info(f"{status} {check_name}")
    
    logger.info("="*50)
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("\n✓ All checks passed! Your bot should work with OpenRouter.")
    elif passed >= 2:
        logger.info("\n⚠️  Most checks passed. There might be minor issues.")
    else:
        logger.info("\n❌ Multiple checks failed. Please fix the issues above.")


def main():
    """Run all diagnostic checks"""
    logger.info("Starting OpenRouter Diagnostic Check\n")
    logger.info(f"API URL: {OPENROUTER_API_URL}")
    logger.info(f"Model: {OPENROUTER_MODEL}\n")
    
    results = {
        "format": check_api_key_format(),
        "connectivity": test_api_connectivity(),
    }
    
    # Only test inference if connectivity is working
    if results["connectivity"]:
        results["inference"] = test_inference()
    else:
        logger.warning("⚠️  Skipping inference test due to connectivity issues")
        results["inference"] = False
    
    # Try to list models even if inference failed
    try:
        list_available_models()
    except Exception as e:
        logger.warning(f"Could not fetch model list: {e}")
    
    print_summary(results)
    
    # Return appropriate exit code
    if results["format"] and results["connectivity"]:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
