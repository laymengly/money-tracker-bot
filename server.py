"""
FastAPI Backend Server for Money Tracker Telegram Mini App (TMA).
Serves static PWA assets (HTML, CSS, JS, Service Worker) and REST sync endpoints.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from config import logger, SERVER_HOST, SERVER_PORT, TELEGRAM_BOT_TOKEN
from database import db

# Telegram webhook secret token (optional security enhancement)
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

_bot_application = None

async def get_bot_application():
    """Retrieve or initialize the Telegram Bot Application for webhook handling."""
    global _bot_application
    if _bot_application is None and TELEGRAM_BOT_TOKEN and "ABCdef" not in TELEGRAM_BOT_TOKEN:
        try:
            from bot import build_application
            app_instance = build_application()
            await app_instance.initialize()
            await app_instance.start()
            _bot_application = app_instance
            logger.info("Telegram Bot Application initialized for webhook processing.")
        except Exception as e:
            logger.warning("Could not initialize Telegram Bot Application for webhook: %s", e)
            _bot_application = None
    return _bot_application


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager to handle bot lifecycle."""
    await get_bot_application()
    yield
    global _bot_application
    if _bot_application:
        try:
            await _bot_application.stop()
            await _bot_application.shutdown()
            logger.info("Telegram Bot Application stopped successfully.")
        except Exception as e:
            logger.warning("Error during Telegram Bot shutdown: %s", e)


app = FastAPI(
    title="Money Tracker Telegram Mini App API",
    description="Sync server for offline-first Telegram Mini App and Firestore database",
    version="1.0.0",
    lifespan=lifespan,
)

# Strict CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# PYDANTIC SCHEMAS
# -------------------------------------------------------------
class TransactionSyncItem(BaseModel):
    id: Optional[str] = None
    type: str = Field(..., pattern="^(expense|income)$")
    category: str
    amount: float = Field(..., gt=0)
    currency: Optional[str] = "USD"
    wallet: Optional[str] = "Bank"
    note: Optional[str] = ""
    date: Optional[str] = None


class AddCategoryPayload(BaseModel):
    userId: str
    type: str = Field(..., pattern="^(expense|income)$")
    name: str = Field(..., min_length=1, max_length=30)


class SyncPayload(BaseModel):
    userId: str
    transaction: TransactionSyncItem


# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/categories")
async def get_categories(userId: str = Query(..., min_length=1)):
    """Fetch user's expense and income categories."""
    try:
        user_id_int = int(userId) if userId.isdigit() else abs(hash(userId)) % 1000000000
    except Exception:
        user_id_int = 123456789

    expense_cats = await db.get_user_categories(user_id_int, "expense")
    income_cats = await db.get_user_categories(user_id_int, "income")
    return {
        "userId": userId,
        "expense": expense_cats,
        "income": income_cats,
    }


@app.post("/api/categories")
async def add_category(payload: AddCategoryPayload):
    """Add a new category for user."""
    try:
        user_id_int = int(payload.userId) if payload.userId.isdigit() else abs(hash(payload.userId)) % 1000000000
    except Exception:
        user_id_int = 123456789

    updated_cats = await db.add_user_category(user_id_int, payload.type, payload.name)
    return {
        "status": "success",
        "type": payload.type,
        "category": payload.name.strip(),
        "categories": updated_cats,
    }


@app.get("/api/transactions")
async def get_user_transactions(userId: str = Query(..., min_length=1)):
    """Fetch user's latest transactions from Firestore."""
    try:
        user_id_int = int(userId) if userId.isdigit() else abs(hash(userId)) % 1000000000
    except Exception:
        user_id_int = 123456789

    txs = await db.get_all_transactions(user_id_int, limit=100)

    # Format datetime objects for JSON serialization
    serialized = []
    for tx in txs:
        item = dict(tx)
        if isinstance(item.get("date"), datetime):
            item["date"] = item["date"].isoformat()
        serialized.append(item)

    return {"userId": userId, "transactions": serialized}


@app.post("/api/sync")
async def sync_transaction(payload: SyncPayload):
    """
    Sync an offline-created transaction into the Firebase Firestore database.
    """
    try:
        user_id_int = int(payload.userId) if payload.userId.isdigit() else abs(hash(payload.userId)) % 1000000000
    except Exception:
        user_id_int = 123456789

    item = payload.transaction

    # Parse date if provided
    dt = None
    if item.date:
        try:
            dt = datetime.fromisoformat(item.date.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.now(timezone.utc)

    # Save to database
    saved_tx = await db.add_transaction(
        user_id=user_id_int,
        tx_type=item.type,
        category=item.category,
        amount=item.amount,
        currency=item.currency or "USD",
        wallet=item.wallet or "Bank",
        note=item.note or "",
        date=dt,
    )

    return {
        "status": "success",
        "client_id": item.id,
        "server_id": saved_tx["id"],
    }


# -------------------------------------------------------------
# TELEGRAM WEBHOOK ENDPOINTS (FOR SERVERLESS DEPLOYMENT)
# -------------------------------------------------------------
@app.post("/api/telegram-webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: Optional[str] = Header(None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    """
    Handle incoming Telegram webhook updates.
    Ensures secure authentication via secret token when configured.
    """
    if TELEGRAM_WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Unauthorized webhook request: secret token mismatch.")
            raise HTTPException(status_code=403, detail="Forbidden: Invalid secret token")

    bot_app = await get_bot_application()
    if not bot_app:
        logger.warning("Telegram update received but bot application is not active.")
        return JSONResponse({"status": "bot_not_configured"}, status_code=200)

    try:
        from telegram import Update
        data = await request.json()
        update = Update.de_json(data=data, bot=bot_app.bot)
        await bot_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error("Error processing telegram webhook update: %s", e)
        return JSONResponse({"status": "error", "message": "Failed to process update"}, status_code=200)


@app.get("/api/telegram-info")
async def telegram_webhook_info():
    """Retrieve Telegram Bot webhook status and pending updates."""
    bot_app = await get_bot_application()
    if not bot_app:
        return {"configured": False, "message": "Telegram Bot is not initialized or configured"}
    try:
        info = await bot_app.bot.get_webhook_info()
        return {
            "configured": True,
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": info.last_error_date.isoformat() if info.last_error_date else None,
            "last_error_message": info.last_error_message,
        }
    except Exception as e:
        return {"configured": True, "error": str(e)}


# -------------------------------------------------------------
# STATIC FILES SERVING (TMA PWA)
# -------------------------------------------------------------
WEBAPP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")

# Mount sw.js and manifest.json at root level for proper Service Worker scope
@app.get("/sw.js")
async def serve_service_worker():
    return FileResponse(os.path.join(WEBAPP_DIR, "sw.js"), media_type="application/javascript")


@app.get("/manifest.json")
async def serve_manifest():
    return FileResponse(os.path.join(WEBAPP_DIR, "manifest.json"), media_type="application/manifest+json")


@app.get("/app.js")
async def serve_app_js():
    return FileResponse(os.path.join(WEBAPP_DIR, "app.js"), media_type="application/javascript")


@app.get("/style.css")
async def serve_style_css():
    return FileResponse(os.path.join(WEBAPP_DIR, "style.css"), media_type="text/css")


@app.get("/")
@app.get("/index.html")
async def serve_index():
    return FileResponse(os.path.join(WEBAPP_DIR, "index.html"))


# Mount the remaining static folder if needed
if os.path.exists(WEBAPP_DIR):
    app.mount("/static", StaticFiles(directory=WEBAPP_DIR), name="static")


def main():
    logger.info("Starting TMA sync server on %s:%d", SERVER_HOST, SERVER_PORT)
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)


if __name__ == "__main__":
    main()
