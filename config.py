"""
Configuration module for Money Tracker & Financial Assistant Bot and Mini App.
"""

import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger("money_tracker_bot")

# Telegram Bot Settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# WebApp URL (For Telegram Mini App button)
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")

# API Server Settings
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Firebase Firestore Configuration
# Path to serviceAccountKey.json or leave empty for demo in-memory fallback
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", None)

# Default User Preferences
DEFAULT_CURRENCY: str = "USD"
DEFAULT_WALLET: str = "Bank"
DEFAULT_WALLETS: List[str] = ["Cash", "Bank"]

# Telegram Stars Monetization Configuration
PRO_PRICE_STARS: int = 150  # 150 Telegram Stars (XTR)
PRO_DURATION_DAYS: int = 30  # 30 Days Pro access

# Financial Categories & Visual Emojis
EXPENSE_CATEGORIES: Dict[str, str] = {
    "Food": "🍔",
    "Transport": "🚗",
    "Bills": "🧾",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Health": "💊",
    "Groceries": "🛒",
    "Education": "📚",
    "Other": "📦",
}

INCOME_CATEGORIES: Dict[str, str] = {
    "Salary": "💼",
    "Freelance": "💻",
    "Investment": "📈",
    "Bonus": "🎁",
    "Refund": "🔄",
    "Other": "💵",
}

DEFAULT_EXPENSE_CATEGORIES: List[str] = list(EXPENSE_CATEGORIES.keys())
DEFAULT_INCOME_CATEGORIES: List[str] = list(INCOME_CATEGORIES.keys())

def get_category_emoji(category: str, tx_type: str = "expense") -> str:
    """Retrieve emoji for standard or user-defined custom categories."""
    source_map = EXPENSE_CATEGORIES if tx_type.lower() == "expense" else INCOME_CATEGORIES
    if category in source_map:
        return source_map[category]
    return "🏷️"

# Currency formatting helpers
CURRENCY_SYMBOLS: Dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "KHR": "៛",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
    "SGD": "S$",
}

def format_amount(amount: float, currency: str = "USD") -> str:
    """Format amount with currency symbol or ISO code."""
    sym = CURRENCY_SYMBOLS.get(currency.upper(), currency.upper() + " ")
    return f"{sym}{amount:,.2f}"
