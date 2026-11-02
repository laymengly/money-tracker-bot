# 💰 Money Tracker & Financial Assistant Ecosystem

An end-to-end, production-ready Telegram Personal Finance Ecosystem consisting of:
1. **Asynchronous Python Telegram Bot** (`python-telegram-bot` v20+) integrated with Firebase Firestore.
2. **In-Memory Donut Chart Engine** (`matplotlib`) for high-resolution visual financial breakdowns.
3. **Interactive Native Inline Calendar** with day-by-day activity markers (🔴 Expense, 🟢 Income, 🔶 Both).
4. **Telegram Stars (XTR) In-App Monetization** for Pro tier subscription.
5. **Offline-First Telegram Mini App (TMA)** built with vanilla HTML5/JS, Service Worker (PWA cache), and IndexedDB for transparent offline logging and background sync.

---

## 🏗️ Architecture & Firestore Data Schema

The database follows strict tenant isolation under `users/{userId}`:

```
users/{userId}
 ├── created_at: Firestore Timestamp
 ├── is_pro: Boolean (default: False)
 ├── pro_expires_at: Firestore Timestamp or null
 ├── default_currency: String ("USD")
 ├── default_wallet: String ("Bank")
 ├── wallets: Array of strings (default: ["Cash", "Bank"])
 └── transactions/{transactionId} (Subcollection)
      ├── id: String (UUID or Firestore auto-ID)
      ├── date: Firestore Timestamp (UTC)
      ├── type: String ("expense" | "income")
      ├── category: String ("Food", "Bills", "Transport", "Shopping", "Salary", etc.)
      ├── amount: Float (strictly positive number)
      ├── currency: String (ISO 4217, e.g. "USD", "EUR")
      ├── wallet: String ("Cash", "Bank", "Card")
      └── note: String (optional note)
```

---

## ⚡ Key Bot Capabilities

### 1. Main Navigation & Fast-Logging
- **Persistent Bottom Reply Keyboard**:
  ```
  [ ➕ Add Expense ] [ 💰 Add Income ]
  [ 📊 Summary ]      [ 📅 Calendar ]
  [ 📈 Chart ]        [ ⭐ Upgrade to Pro ]
  ```
- **Regex Fast-Logging**:
  Send message directly in chat:
  - `-15 Food Team lunch` ➔ Logs $15.00 expense under Food today.
  - `2026-10-18 -25 Food Dinner` ➔ Logs $25.00 expense under Food on October 18, 2026.
  - `+3000 Salary Monthly payroll` ➔ Logs $3,000.00 income under Salary.
  - Includes instant receipt card and inline `[ 🗑️ Delete ]` button.

### 2. Multi-Step Interactive Flow (`ConversationHandler`)
- Click **➕ Add Expense** or **💰 Add Income**:
  1. **Category Selection**: 3-column inline grid with emoji icons plus **➕ Add New Category** button (allowing users to add custom categories on the fly).
  2. **Wallet Selection**: Dynamically fetched from user's registered wallets.
  3. **Amount & Note**: Prompts user for input with strict numeric validation.
  4. **Date Selection**: Pick `[ 📅 Today ]`, `[ 📅 Yesterday ]`, or `[ 🗓️ Custom Date (YYYY-MM-DD) ]`.
  5. **Receipt Card**: Formatted receipt with chosen date and quick undo action.

### 3. Summary Dashboard (`/summary`)
- Aggregates income, expenses, and net flow for any selected month.
- Shows percentage breakdown by category.
- Interactive inline navigation: `[ ◀ Prev Month ]`, `[ Next Month ▶ ]`, `[ 📈 View Chart ]`.

### 4. Visual Donut Chart Engine (`charts.py`)
- Renders high-resolution donut charts using `matplotlib`.
- Custom transparent background, center total badge, percentage slices, and formatted legend.
- **Strictly in-memory**: Saved into `io.BytesIO` buffer without disk writes.

### 5. Interactive Inline Calendar (`/calendar`)
- Full month grid with weekday headers (`Mo Tu We Th Fr Sa Su`).
- Day markers:
  - `[ {day}🔴 ]`: Expenses logged
  - `[ {day}🟢 ]`: Income logged
  - `[ {day}🔶 ]`: Both logged
  - `[ {day} ]`: No activity
- Tapping any day opens a drill-down breakdown with individual transactions and a `[ 🔙 Back to Calendar ]` button.

### 6. Telegram Stars (XTR) In-App Billing
- Upgrade via `/upgrade` or **⭐ Upgrade to Pro**.
- Sends invoice with currency `XTR` (Telegram Stars, 150 Stars).
- Automatically handles `PreCheckoutQuery` and `SUCCESSFUL_PAYMENT`.
- Updates user document with `is_pro=True` and extends `pro_expires_at` by 30 days.

---

## 📱 Offline-First Telegram Mini App (TMA)

Located in `webapp/`:
- **PWA Service Worker (`sw.js`)**: Cache-First strategy for application shell and assets.
- **IndexedDB (`MoneyTrackerDB`)**:
  - `transactions`: Local offline cache for instantaneous UI rendering.
  - `sync_queue`: Queues records created while offline.
- **Auto-Sync**: Automatically listens for `online` events, sends background POST requests to `/api/sync`, updates IDs, and clears the queue.
- **Telegram Native Theme & Haptics**: Uses `--tg-theme-*` variables and triggers `Telegram.WebApp.HapticFeedback`.

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set your `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather).
If using Firebase Firestore, place your `serviceAccountKey.json` in the root directory. (If omitted, the app will run with an in-memory database store for testing and demo).

### 3. Start the Mini App & Sync Server
```bash
python server.py
```
Open `http://127.0.0.1:8000` in your browser to test the Mini App, or expose it via ngrok/HTTPS for Telegram.

### 4. Run the Telegram Bot
```bash
python bot.py
```

---

## 🔥 Firebase Deployment Guide

This project is fully configured for deployment on Firebase:
- **Firebase Hosting**: Serves the Telegram Mini App (TMA PWA) from `webapp/` via high-speed global CDN with HTTPS and offline service worker caching.
- **Firebase Cloud Functions (2nd Gen Python)**: Serves the FastAPI REST API (`/api/sync`, `/api/categories`, `/api/transactions`, `/api/health`) and the Telegram webhook endpoint (`/api/telegram-webhook`).
- **Cloud Firestore**: Persistent multi-tenant storage with security rules defined in `firestore.rules`.

### 1. Authenticate with Firebase CLI
If your session has expired, re-authenticate:
```bash
firebase login --reauth
```

### 2. Connect Your Firebase Project
Select or add your Firebase project:
```bash
firebase use --add
```

### 3. Deploy to Firebase
Deploy all components (Hosting, Firestore rules/indexes, and Cloud Functions):
```bash
firebase deploy
```
Or deploy individual services:
- **Deploy only the Mini App (Hosting)**:
  ```bash
  firebase deploy --only hosting
  ```
- **Deploy Firestore security rules & indexes**:
  ```bash
  firebase deploy --only firestore
  ```
- **Deploy Backend Cloud Functions**:
  ```bash
  firebase deploy --only functions
  ```

### 4. Configure Telegram Webhook for Serverless Bot
Once deployed, link your Telegram bot to Firebase to receive updates serverlessly:
```bash
python set_webhook.py --url https://<your-project-id>.web.app
```
To inspect the webhook status:
```bash
python set_webhook.py --info
```
To revert back to local polling mode:
```bash
python set_webhook.py --delete
python bot.py
```

