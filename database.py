"""
Database access layer for Money Tracker Bot.
Strict tenant isolation under users/{userId} in Firebase Firestore.
Includes asynchronous wrappers and a thread-safe in-memory fallback for local development.
"""

import os
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

from config import (
    logger,
    FIREBASE_CREDENTIALS_PATH,
    FIREBASE_PROJECT_ID,
    DEFAULT_CURRENCY,
    DEFAULT_WALLET,
    DEFAULT_WALLETS,
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_CATEGORIES,
)

# Optional Firebase import with fallback for local testing
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1 import SERVER_TIMESTAMP
    FIREBASE_AVAILABLE = True
except ImportError:
    firebase_admin = None
    firestore = None
    SERVER_TIMESTAMP = None
    FIREBASE_AVAILABLE = False


class FirestoreDB:
    """Production-grade Firestore client with tenant isolation."""

    def __init__(self):
        self._db = None
        self._is_mock = False
        self._mock_data: Dict[str, Dict[str, Any]] = {}  # {user_id: {profile: {}, transactions: {}}}
        self._init_client()

    def _init_client(self):
        """Initialize Firebase Admin SDK or initialize fallback store."""
        if not FIREBASE_AVAILABLE:
            logger.warning("firebase-admin is not installed. Falling back to in-memory store.")
            self._is_mock = True
            return

        try:
            if not firebase_admin._apps:
                if os.path.exists(FIREBASE_CREDENTIALS_PATH):
                    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred, {"projectId": FIREBASE_PROJECT_ID} if FIREBASE_PROJECT_ID else None)
                    logger.info("Firebase initialized with service account key: %s", FIREBASE_CREDENTIALS_PATH)
                else:
                    # Attempt application default credentials or mock fallback
                    try:
                        firebase_admin.initialize_app()
                        logger.info("Firebase initialized with Application Default Credentials.")
                    except Exception as default_e:
                        logger.warning(
                            "Firebase credentials not found (%s). Running with in-memory database fallback for development/demo. Details: %s",
                            FIREBASE_CREDENTIALS_PATH,
                            default_e,
                        )
                        self._is_mock = True
                        return

            self._db = firestore.client()
            logger.info("Firestore client connected successfully.")
        except Exception as e:
            logger.warning("Failed to initialize Firestore (%s). Using in-memory fallback store.", e)
            self._is_mock = True

    # ---------------------------------------------------------
    # USER OPERATIONS
    # ---------------------------------------------------------

    async def get_or_create_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch user document or create default profile under users/{userId}."""
        return await asyncio.to_thread(self._get_or_create_user_sync, str(user_id))

    def _get_or_create_user_sync(self, user_id_str: str) -> Dict[str, Any]:
        if self._is_mock:
            if user_id_str not in self._mock_data:
                now = datetime.now(timezone.utc)
                self._mock_data[user_id_str] = {
                    "profile": {
                        "user_id": user_id_str,
                        "created_at": now,
                        "is_pro": False,
                        "pro_expires_at": None,
                        "language": "en",
                        "default_currency": DEFAULT_CURRENCY,
                        "default_wallet": DEFAULT_WALLET,
                        "wallets": list(DEFAULT_WALLETS),
                        "expense_categories": list(DEFAULT_EXPENSE_CATEGORIES),
                        "income_categories": list(DEFAULT_INCOME_CATEGORIES),
                    },
                    "transactions": {},
                }
            profile = self._mock_data[user_id_str]["profile"]
            if "language" not in profile:
                profile["language"] = "en"
            if "expense_categories" not in profile:
                profile["expense_categories"] = list(DEFAULT_EXPENSE_CATEGORIES)
            if "income_categories" not in profile:
                profile["income_categories"] = list(DEFAULT_INCOME_CATEGORIES)
            return profile

        user_ref = self._db.collection("users").document(user_id_str)
        doc = user_ref.get()
        if doc.exists:
            data = doc.to_dict()
            # Ensure fields exist
            updated = False
            if "language" not in data:
                data["language"] = "en"
                updated = True
            if "expense_categories" not in data:
                data["expense_categories"] = list(DEFAULT_EXPENSE_CATEGORIES)
                updated = True
            if "income_categories" not in data:
                data["income_categories"] = list(DEFAULT_INCOME_CATEGORIES)
                updated = True
            if updated:
                user_ref.update({
                    "language": data["language"],
                    "expense_categories": data["expense_categories"],
                    "income_categories": data["income_categories"],
                })
            return data

        # Create new user document
        now = datetime.now(timezone.utc)
        default_data = {
            "created_at": now,
            "is_pro": False,
            "pro_expires_at": None,
            "language": "en",
            "default_currency": DEFAULT_CURRENCY,
            "default_wallet": DEFAULT_WALLET,
            "wallets": list(DEFAULT_WALLETS),
            "expense_categories": list(DEFAULT_EXPENSE_CATEGORIES),
            "income_categories": list(DEFAULT_INCOME_CATEGORIES),
        }
        user_ref.set(default_data)
        return default_data

    async def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language ('en' or 'km')."""
        user = await self.get_or_create_user(user_id)
        return user.get("language", "en")

    async def set_user_language(self, user_id: int, language: str) -> str:
        """Update user's preferred language."""
        lang = "km" if language.lower() in ("km", "khmer") else "en"
        await self.update_user(user_id, {"language": lang})
        return lang

    async def get_user_categories(self, user_id: int, tx_type: str = "expense") -> List[str]:
        """Get user's customized categories for expense or income."""
        user = await self.get_or_create_user(user_id)
        key = "expense_categories" if tx_type.lower() == "expense" else "income_categories"
        default = DEFAULT_EXPENSE_CATEGORIES if tx_type.lower() == "expense" else DEFAULT_INCOME_CATEGORIES
        return user.get(key, list(default))

    async def add_user_category(self, user_id: int, tx_type: str, category_name: str) -> List[str]:
        """Add a custom category to the user's category list."""
        return await asyncio.to_thread(self._add_user_category_sync, str(user_id), tx_type, category_name)

    def _add_user_category_sync(self, user_id_str: str, tx_type: str, category_name: str) -> List[str]:
        cleaned_cat = category_name.strip()
        if not cleaned_cat:
            raise ValueError("Category name cannot be empty.")

        key = "expense_categories" if tx_type.lower() == "expense" else "income_categories"
        default_list = DEFAULT_EXPENSE_CATEGORIES if tx_type.lower() == "expense" else DEFAULT_INCOME_CATEGORIES

        if self._is_mock:
            user = self._get_or_create_user_sync(user_id_str)
            cats = user.get(key, list(default_list))
            if cleaned_cat not in cats:
                cats.append(cleaned_cat)
            user[key] = cats
            return cats

        user_ref = self._db.collection("users").document(user_id_str)
        doc = user_ref.get()
        current_data = doc.to_dict() if doc.exists else {}
        cats = current_data.get(key, list(default_list))
        if cleaned_cat not in cats:
            cats.append(cleaned_cat)
            user_ref.update({key: cats})
        return cats

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user profile."""
        return await asyncio.to_thread(self._get_user_sync, str(user_id))

    def _get_user_sync(self, user_id_str: str) -> Optional[Dict[str, Any]]:
        if self._is_mock:
            if user_id_str in self._mock_data:
                return self._mock_data[user_id_str]["profile"]
            return None

        doc = self._db.collection("users").document(user_id_str).get()
        return doc.to_dict() if doc.exists else None

    async def update_user(self, user_id: int, updates: Dict[str, Any]) -> None:
        """Update fields in users/{userId}."""
        await asyncio.to_thread(self._update_user_sync, str(user_id), updates)

    def _update_user_sync(self, user_id_str: str, updates: Dict[str, Any]) -> None:
        if self._is_mock:
            if user_id_str in self._mock_data:
                self._mock_data[user_id_str]["profile"].update(updates)
            return

        self._db.collection("users").document(user_id_str).update(updates)

    async def upgrade_to_pro(self, user_id: int, duration_days: int = 30) -> datetime:
        """Activate or extend Pro status for user."""
        return await asyncio.to_thread(self._upgrade_to_pro_sync, str(user_id), duration_days)

    def _upgrade_to_pro_sync(self, user_id_str: str, duration_days: int) -> datetime:
        user = self._get_or_create_user_sync(user_id_str)
        now = datetime.now(timezone.utc)

        current_expiry = user.get("pro_expires_at")
        if current_expiry and isinstance(current_expiry, datetime) and current_expiry > now:
            new_expiry = current_expiry + timedelta(days=duration_days)
        else:
            new_expiry = now + timedelta(days=duration_days)

        updates = {
            "is_pro": True,
            "pro_expires_at": new_expiry,
        }
        self._update_user_sync(user_id_str, updates)
        return new_expiry

    # ---------------------------------------------------------
    # TRANSACTION OPERATIONS (users/{userId}/transactions/{txId})
    # ---------------------------------------------------------

    async def add_transaction(
        self,
        user_id: int,
        tx_type: str,
        category: str,
        amount: float,
        currency: Optional[str] = None,
        wallet: Optional[str] = None,
        note: Optional[str] = "",
        date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Add a new transaction under users/{userId}/transactions/{transactionId}.
        Amount is strictly normalized to positive float.
        """
        user_data = await self.get_or_create_user(user_id)
        curr = currency or user_data.get("default_currency", DEFAULT_CURRENCY)
        wal = wallet or user_data.get("default_wallet", DEFAULT_WALLET)
        dt = date or datetime.now(timezone.utc)
        normalized_amount = abs(float(amount))

        tx_payload = {
            "date": dt,
            "type": tx_type.lower(),  # "expense" | "income"
            "category": category.strip(),
            "amount": normalized_amount,
            "currency": curr.upper(),
            "wallet": wal,
            "note": note.strip() if note else "",
        }

        return await asyncio.to_thread(self._add_transaction_sync, str(user_id), tx_payload)

    def _add_transaction_sync(self, user_id_str: str, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        if self._is_mock:
            tx_id = f"tx_{uuid.uuid4().hex[:12]}"
            payload = dict(tx_payload)
            payload["id"] = tx_id
            self._mock_data[user_id_str]["transactions"][tx_id] = payload
            return payload

        tx_ref = self._db.collection("users").document(user_id_str).collection("transactions").document()
        payload = dict(tx_payload)
        payload["id"] = tx_ref.id
        tx_ref.set(payload)
        return payload

    async def delete_transaction(self, user_id: int, transaction_id: str) -> bool:
        """Delete transaction by ID."""
        return await asyncio.to_thread(self._delete_transaction_sync, str(user_id), transaction_id)

    def _delete_transaction_sync(self, user_id_str: str, transaction_id: str) -> bool:
        if self._is_mock:
            if user_id_str in self._mock_data:
                tx_dict = self._mock_data[user_id_str]["transactions"]
                if transaction_id in tx_dict:
                    del tx_dict[transaction_id]
                    return True
            return False

        tx_ref = (
            self._db.collection("users")
            .document(user_id_str)
            .collection("transactions")
            .document(transaction_id)
        )
        doc = tx_ref.get()
        if doc.exists:
            tx_ref.delete()
            return True
        return False

    async def get_transaction(self, user_id: int, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific transaction."""
        return await asyncio.to_thread(self._get_transaction_sync, str(user_id), transaction_id)

    def _get_transaction_sync(self, user_id_str: str, transaction_id: str) -> Optional[Dict[str, Any]]:
        if self._is_mock:
            if user_id_str in self._mock_data:
                return self._mock_data[user_id_str]["transactions"].get(transaction_id)
            return None

        doc = (
            self._db.collection("users")
            .document(user_id_str)
            .collection("transactions")
            .document(transaction_id)
            .get()
        )
        return doc.to_dict() if doc.exists else None

    async def get_transactions_in_range(
        self, user_id: int, start_dt: datetime, end_dt: datetime
    ) -> List[Dict[str, Any]]:
        """Retrieve all transactions between start_dt and end_dt (inclusive)."""
        return await asyncio.to_thread(
            self._get_transactions_in_range_sync, str(user_id), start_dt, end_dt
        )

    def _get_transactions_in_range_sync(
        self, user_id_str: str, start_dt: datetime, end_dt: datetime
    ) -> List[Dict[str, Any]]:
        if self._is_mock:
            if user_id_str not in self._mock_data:
                return []
            res = []
            for tx in self._mock_data[user_id_str]["transactions"].values():
                d = tx["date"]
                if isinstance(d, datetime):
                    if d.tzinfo is None:
                        d = d.replace(tzinfo=timezone.utc)
                    if start_dt <= d <= end_dt:
                        res.append(tx)
            res.sort(key=lambda x: x["date"], reverse=True)
            return res

        col = (
            self._db.collection("users")
            .document(user_id_str)
            .collection("transactions")
            .where("date", ">=", start_dt)
            .where("date", "<=", end_dt)
            .order_by("date", direction=firestore.Query.DESCENDING)
        )
        docs = col.stream()
        return [d.to_dict() for d in docs]

    async def get_transactions_for_day(
        self, user_id: int, year: int, month: int, day: int
    ) -> List[Dict[str, Any]]:
        """Get transactions for a specific day (UTC)."""
        start_dt = datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc)
        end_dt = datetime(year, month, day, 23, 59, 59, 999999, tzinfo=timezone.utc)
        return await self.get_transactions_in_range(user_id, start_dt, end_dt)

    async def get_month_day_markers(
        self, user_id: int, year: int, month: int
    ) -> Dict[int, str]:
        """
        Analyze month's transactions and return day marker dict:
        day_number -> 'expense' | 'income' | 'both'
        """
        # Determine range for whole month
        start_dt = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
        if month == 12:
            end_dt = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1)
        else:
            end_dt = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1)

        txs = await self.get_transactions_in_range(user_id, start_dt, end_dt)
        day_activity: Dict[int, Dict[str, bool]] = {}

        for tx in txs:
            dt = tx["date"]
            if hasattr(dt, "day"):
                day = dt.day
            else:
                continue

            if day not in day_activity:
                day_activity[day] = {"income": False, "expense": False}

            tx_type = tx.get("type", "expense").lower()
            if tx_type == "income":
                day_activity[day]["income"] = True
            else:
                day_activity[day]["expense"] = True

        markers: Dict[int, str] = {}
        for day, act in day_activity.items():
            if act["income"] and act["expense"]:
                markers[day] = "both"
            elif act["income"]:
                markers[day] = "income"
            elif act["expense"]:
                markers[day] = "expense"

        return markers

    async def get_all_transactions(self, user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get latest transactions for user (used by Mini App sync)."""
        return await asyncio.to_thread(self._get_all_transactions_sync, str(user_id), limit)

    def _get_all_transactions_sync(self, user_id_str: str, limit: int) -> List[Dict[str, Any]]:
        if self._is_mock:
            if user_id_str not in self._mock_data:
                return []
            txs = list(self._mock_data[user_id_str]["transactions"].values())
            txs.sort(key=lambda x: x["date"], reverse=True)
            return txs[:limit]

        col = (
            self._db.collection("users")
            .document(user_id_str)
            .collection("transactions")
            .order_by("date", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        return [d.to_dict() for d in col.stream()]


# Singleton database instance
db = FirestoreDB()
