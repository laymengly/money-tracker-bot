"""
Telegram Bot Core Engine for Money Tracker & Financial Assistant.
Built using python-telegram-bot v20+ with async handlers, Telegram Stars billing,
multi-step conversation flows, fast regex logging, and calendar navigation.
"""

import re
import calendar
from datetime import datetime, timezone, timedelta
from typing import Optional

from telegram import (
    Update,
    LabeledPrice,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters,
)

from config import (
    logger,
    TELEGRAM_BOT_TOKEN,
    WEBAPP_URL,
    PRO_PRICE_STARS,
    PRO_DURATION_DAYS,
    format_amount,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    get_category_emoji,
)
from database import db
from charts import generate_expense_donut_chart, generate_report_pie_chart
from keyboards import (
    get_main_reply_keyboard,
    get_category_keyboard,
    get_wallet_keyboard,
    get_receipt_keyboard,
    get_summary_keyboard,
    get_report_keyboard,
    get_net_balance_keyboard,
    get_calendar_keyboard,
    get_day_detail_keyboard,
    get_date_selection_keyboard,
    get_time_picker_keyboard,
    get_language_keyboard,
)
from locales import t, get_display_category, get_display_month

# Conversation States for Multi-Step Flow
(
    SELECT_CATEGORY,
    SELECT_WALLET,
    ENTER_AMOUNT_NOTE,
    SELECT_DATE,
    SELECT_TIME,
    ENTER_NEW_CATEGORY,
) = range(6)

# Regex pattern for fast-logging with optional date prefix:
# e.g., "-15 Food Team lunch" or "2026-10-18 -15 Food Team lunch" or "+3000 Salary Monthly payroll"
FAST_LOG_REGEX = re.compile(
    r"^(?:(\d{4}-\d{2}-\d{2})\s+)?([+-])(\d+(?:\.\d{1,2})?)\s+([A-Za-z0-9&_]+)(?:\s+(.*))?$"
)


# =====================================================================
# COMMAND HANDLERS
# =====================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command: initialize user profile and present main keyboard."""
    user = update.effective_user
    if not user:
        return

    profile = await db.get_or_create_user(user.id)
    lang = profile.get("language", "en")
    pro_badge = t("pro_badge", lang) if profile.get("is_pro") else t("free_badge", lang)

    if lang == "km":
        welcome_text = (
            f"👋 សូមស្វាគមន៍មកកាន់ <b>Money Tracker & Financial Assistant</b>, {user.first_name}!\n\n"
            f"ស្ថានភាព៖ {pro_badge}\n"
            f"រូបិយប័ណ្ណលំនាំដើម៖ <code>{profile.get('default_currency', 'USD')}</code>\n"
            f"កាបូបលំនាំដើម៖ <code>{profile.get('default_wallet', 'Bank')}</code>\n\n"
            "⚡ <b>ការកត់ត្រារហ័ស៖</b>\n"
            "ផ្ញើសារក្នុងប្រអប់ជជែកគ្រប់ពេល៖\n"
            "• <code>-15 Food ញ៉ាំបាយថ្ងៃត្រង់</code> (កត់ត្រាការចំណាយ)\n"
            "• <code>+2500 Salary ប្រាក់ខែប្រចាំខែ</code> (កត់ត្រាចំណូល)\n\n"
            "ឬចុចប៊ូតុងខាងក្រោមដើម្បីកត់ត្រាតាមជំហាន មើលតារាង និងប្រតិទិន!"
        )
    else:
        welcome_text = (
            f"👋 Welcome to <b>Money Tracker & Financial Assistant</b>, {user.first_name}!\n\n"
            f"Status: {pro_badge}\n"
            f"Default Currency: <code>{profile.get('default_currency', 'USD')}</code>\n"
            f"Default Wallet: <code>{profile.get('default_wallet', 'Bank')}</code>\n\n"
            "⚡ <b>Fast-Log Commands:</b>\n"
            "Simply send a quick message in chat anytime:\n"
            "• <code>-15 Food Team lunch</code> (Logs an expense)\n"
            "• <code>+2500 Salary Monthly bonus</code> (Logs an income)\n\n"
            "Or use the buttons below to log interactively, view charts, and explore the calendar!"
        )

    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_reply_keyboard(WEBAPP_URL, lang=lang),
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user with language selection keyboard."""
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    prompt = t("lang_switch_prompt", lang)
    if update.message:
        await update.message.reply_html(prompt, reply_markup=get_language_keyboard())
    elif update.callback_query:
        await update.callback_query.message.reply_html(prompt, reply_markup=get_language_keyboard())


async def set_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle set_lang_en and set_lang_km callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data  # "set_lang_en" or "set_lang_km"
    new_lang = "km" if "km" in data else "en"
    user = update.effective_user

    await db.set_user_language(user.id, new_lang)
    confirm_text = t("lang_changed", new_lang)

    await query.edit_message_text(confirm_text, parse_mode=ParseMode.HTML)
    await query.message.reply_html(
        "✨ " + t("btn_language", new_lang) + " ✓",
        reply_markup=get_main_reply_keyboard(WEBAPP_URL, lang=new_lang),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed help message."""
    help_text = (
        "💡 <b>Money Tracker Help & Commands</b>\n\n"
        "<b>Fast-Logging Syntax:</b>\n"
        "<code>[+/-][amount] [category] [optional note]</code>\n"
        "Examples:\n"
        "• <code>-12.50 Food Lunch with Alex</code>\n"
        "• <code>-45 Transport Weekly petrol</code>\n"
        "• <code>+1200 Freelance Web design project</code>\n\n"
        "<b>Bot Features:</b>\n"
        "• ➕ <b>Add Expense / 💰 Add Income</b>: Guided multi-step logger\n"
        "• 📊 <b>Summary</b>: Monthly financial overview & flow\n"
        "• 📅 <b>Calendar</b>: Interactive day-by-day markers (🔴 Expense, 🟢 Income, 🔶 Both)\n"
        "• 📈 <b>Chart</b>: High-res donut breakdown\n"
        "• ⭐ <b>Upgrade to Pro</b>: 30-day Pro membership via Telegram Stars (XTR)\n"
        "• 📱 <b>Mini App</b>: Offline-first WebApp with local sync"
    )
    await update.message.reply_html(help_text)


# =====================================================================
# FAST-LOGGING TEXT HANDLER
# =====================================================================

async def fast_log_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    r"""
    Regex fast-logger handler:
    Matches: ^(?:(\d{4}-\d{2}-\d{2})\s+)?([+-])(\d+(?:\.\d{1,2})?)\s+([A-Za-z0-9&_]+)(?:\s+(.*))?$
    """
    user = update.effective_user
    text = update.message.text.strip()
    match = FAST_LOG_REGEX.match(text)
    if not match or not user:
        return

    date_str, sign, amount_str, category_raw, note_raw = match.groups()
    amount = float(amount_str)
    tx_type = "expense" if sign == "-" else "income"
    note = note_raw.strip() if note_raw else ""

    # Parse optional date
    if date_str:
        try:
            tx_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            tx_date = datetime.now(timezone.utc)
    else:
        tx_date = datetime.now(timezone.utc)

    # Match or normalize category
    categories_dict = EXPENSE_CATEGORIES if tx_type == "expense" else INCOME_CATEGORIES
    matched_cat = next(
        (c for c in categories_dict if c.lower() == category_raw.lower()),
        category_raw.capitalize(),
    )
    emoji = get_category_emoji(matched_cat, tx_type)

    # Fetch user preferences
    profile = await db.get_or_create_user(user.id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")
    wallet = profile.get("default_wallet", "Bank")

    # Save to Firestore
    tx = await db.add_transaction(
        user_id=user.id,
        tx_type=tx_type,
        category=matched_cat,
        amount=amount,
        currency=currency,
        wallet=wallet,
        note=note,
        date=tx_date,
    )

    type_label = t("expense_logged", lang) if tx_type == "expense" else t("income_logged", lang)
    formatted = format_amount(amount, currency)
    disp_cat = get_display_category(matched_cat, lang)

    receipt_text = (
        f"<b>{type_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{t('lbl_amount', lang)}:</b> <code>{formatted}</code>\n"
        f"<b>{t('lbl_category', lang)}:</b> {emoji} {disp_cat}\n"
        f"<b>{t('lbl_wallet', lang)}:</b> 💳 {wallet}\n"
    )
    if note:
        receipt_text += f"<b>{t('lbl_note', lang)}:</b> <i>{note}</i>\n"
    receipt_text += (
        f"<b>{t('lbl_date', lang)}:</b> {tx_date.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{t('receipt_undo', lang)}"
    )

    await update.message.reply_html(
        receipt_text,
        reply_markup=get_receipt_keyboard(tx["id"], lang=lang),
    )


# =====================================================================
# MULTI-STEP CONVERSATION HANDLER
# =====================================================================

async def start_add_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 1: User clicked Add Expense or Add Income -> Prompt for category."""
    user = update.effective_user
    text = update.message.text or ""
    is_income = "income" in text.lower() or "ចំណូល" in text or "add_income" in text.lower()
    tx_type = "income" if is_income else "expense"
    context.user_data["flow_type"] = tx_type

    lang = await db.get_user_language(user.id)
    context.user_data["lang"] = lang

    user_categories = await db.get_user_categories(user.id, tx_type)
    title = t("select_income_cat", lang) if tx_type == "income" else t("select_expense_cat", lang)
    await update.message.reply_html(
        title,
        reply_markup=get_category_keyboard(user_categories, tx_type, lang=lang),
    )
    return SELECT_CATEGORY


async def add_new_category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User clicked Add New Category button."""
    query = update.callback_query
    await query.answer()

    data = query.data  # e.g. "addcat_expense" or "addcat_income"
    tx_type = data.split("_")[1]
    context.user_data["flow_type"] = tx_type

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    context.user_data["lang"] = lang

    await query.edit_message_text(
        t("enter_new_cat", lang),
        parse_mode=ParseMode.HTML,
    )
    return ENTER_NEW_CATEGORY


async def new_category_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new category name, save to Firestore, and proceed to wallet selection."""
    user = update.effective_user
    cat_name = update.message.text.strip()
    lang = context.user_data.get("lang") or await db.get_user_language(user.id)

    if not cat_name or len(cat_name) > 30:
        await update.message.reply_html(t("invalid_cat_name", lang))
        return ENTER_NEW_CATEGORY

    tx_type = context.user_data.get("flow_type", "expense")
    await db.add_user_category(user.id, tx_type, cat_name)
    context.user_data["flow_category"] = cat_name

    profile = await db.get_or_create_user(user.id)
    wallets = profile.get("wallets", ["Cash", "Bank"])
    emoji = get_category_emoji(cat_name, tx_type)

    added_text = t("cat_added", lang).format(emoji=emoji, category=cat_name)
    await update.message.reply_html(
        added_text,
        reply_markup=get_wallet_keyboard(wallets, tx_type, cat_name, lang=lang),
    )
    return SELECT_WALLET


async def category_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 2: Category chosen -> Prompt for wallet selection."""
    query = update.callback_query
    await query.answer()

    data = query.data  # e.g. "cat_expense_Food"
    parts = data.split("_", 2)
    tx_type = parts[1]
    category = parts[2]

    context.user_data["flow_type"] = tx_type
    context.user_data["flow_category"] = category

    user = update.effective_user
    profile = await db.get_or_create_user(user.id)
    wallets = profile.get("wallets", ["Cash", "Bank"])
    lang = profile.get("language", "en")
    context.user_data["lang"] = lang

    emoji = get_category_emoji(category, tx_type)
    disp_cat = get_display_category(category, lang)

    await query.edit_message_text(
        f"{t('lbl_category', lang)}: <b>{emoji} {disp_cat}</b>\n\n"
        f"{t('select_wallet', lang)}",
        parse_mode=ParseMode.HTML,
        reply_markup=get_wallet_keyboard(wallets, tx_type, category, lang=lang),
    )
    return SELECT_WALLET


async def wallet_selected_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 3: Wallet chosen -> Prompt for amount and note."""
    query = update.callback_query
    await query.answer()

    data = query.data  # e.g. "wal_expense_Food_Bank"
    parts = data.split("_", 3)
    wallet = parts[3]
    context.user_data["flow_wallet"] = wallet

    tx_type = context.user_data.get("flow_type", "expense")
    category = context.user_data.get("flow_category", "Other")
    lang = context.user_data.get("lang", "en")

    emoji = get_category_emoji(category, tx_type)
    disp_cat = get_display_category(category, lang)

    chosen_label = f"Selected: <b>{emoji} {disp_cat}</b> via <b>{wallet}</b>" if lang == "en" else f"បានជ្រើសរើស៖ <b>{emoji} {disp_cat}</b> តាម <b>{wallet}</b>"

    await query.edit_message_text(
        f"{chosen_label}\n\n{t('enter_amount_note', lang)}",
        parse_mode=ParseMode.HTML,
    )
    return ENTER_AMOUNT_NOTE


async def amount_note_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Step 4: Receive amount and optional note, then prompt for date selection."""
    user = update.effective_user
    text = update.message.text.strip()
    lang = context.user_data.get("lang") or await db.get_user_language(user.id)

    # Split amount and optional note
    parts = text.split(maxsplit=1)
    raw_amount = parts[0]
    note = parts[1] if len(parts) > 1 else ""

    try:
        amount = float(raw_amount)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await update.message.reply_html(t("invalid_amount", lang))
        return ENTER_AMOUNT_NOTE

    context.user_data["flow_amount"] = amount
    context.user_data["flow_note"] = note

    tx_type = context.user_data.get("flow_type", "expense")
    category = context.user_data.get("flow_category", "Other")
    wallet = context.user_data.get("flow_wallet", "Bank")
    emoji = get_category_emoji(category, tx_type)
    disp_cat = get_display_category(category, lang)

    profile = await db.get_or_create_user(user.id)
    currency = profile.get("default_currency", "USD")

    now = datetime.now(timezone.utc)
    rec_label = "Recorded" if lang == "en" else "បានកត់ត្រា"
    await update.message.reply_html(
        f"{rec_label}: <b>{format_amount(amount, currency)}</b> ({emoji} {disp_cat} • {wallet})\n\n"
        f"{t('select_date', lang)}",
        reply_markup=get_date_selection_keyboard(now.year, now.month, lang=lang),
    )
    return SELECT_DATE


async def date_picker_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle month navigation in the interactive date picker."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[1])
    month = int(parts[2])

    user = update.effective_user
    lang = context.user_data.get("lang") or await db.get_user_language(user.id)

    await query.edit_message_reply_markup(
        reply_markup=get_date_selection_keyboard(year, month, lang=lang)
    )
    return SELECT_DATE


async def date_picker_day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User tapped a specific day on the calendar grid -> Open time picker."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[1])
    month = int(parts[2])
    day = int(parts[3])

    context.user_data["flow_year"] = year
    context.user_data["flow_month"] = month
    context.user_data["flow_day"] = day

    user = update.effective_user
    lang = context.user_data.get("lang") or await db.get_user_language(user.id)

    date_display = f"{year}-{month:02d}-{day:02d}"
    await query.edit_message_text(
        f"📅 {t('lbl_date', lang)}: <b>{date_display}</b>\n\n"
        f"{t('choose_time', lang)}",
        parse_mode=ParseMode.HTML,
        reply_markup=get_time_picker_keyboard(year, month, day, lang=lang),
    )
    return SELECT_TIME


async def date_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User tapped quick Today or Yesterday shortcuts."""
    query = update.callback_query
    await query.answer()

    data = query.data
    now_utc = datetime.now(timezone.utc)

    if data == "datesel_today":
        return await finalize_and_save_transaction(update, context, now_utc)
    elif data == "datesel_yesterday":
        yesterday = now_utc - timedelta(days=1)
        return await finalize_and_save_transaction(update, context, yesterday)

    return SELECT_DATE


async def time_picker_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User tapped time preset or current time -> Save transaction."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[1])
    month = int(parts[2])
    day = int(parts[3])
    hour = int(parts[4])
    minute = int(parts[5])

    tx_datetime = datetime(year, month, day, hour, minute, 0, tzinfo=timezone.utc)
    return await finalize_and_save_transaction(update, context, tx_datetime)


async def finalize_and_save_transaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE, tx_date: datetime
) -> int:
    """Write validated record to Firestore and present confirmation receipt."""
    user = update.effective_user
    tx_type = context.user_data.get("flow_type", "expense")
    category = context.user_data.get("flow_category", "Other")
    wallet = context.user_data.get("flow_wallet", "Bank")
    amount = context.user_data.get("flow_amount", 0.0)
    note = context.user_data.get("flow_note", "")

    profile = await db.get_or_create_user(user.id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    # Save to Firestore
    tx = await db.add_transaction(
        user_id=user.id,
        tx_type=tx_type,
        category=category,
        amount=amount,
        currency=currency,
        wallet=wallet,
        note=note,
        date=tx_date,
    )

    emoji = get_category_emoji(category, tx_type)
    type_label = t("expense_logged", lang) if tx_type == "expense" else t("income_logged", lang)
    formatted = format_amount(amount, currency)
    disp_cat = get_display_category(category, lang)

    receipt_text = (
        f"<b>{type_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"<b>{t('lbl_amount', lang)}:</b> <code>{formatted}</code>\n"
        f"<b>{t('lbl_category', lang)}:</b> {emoji} {disp_cat}\n"
        f"<b>{t('lbl_wallet', lang)}:</b> 💳 {wallet}\n"
    )
    if note:
        receipt_text += f"<b>{t('lbl_note', lang)}:</b> <i>{note}</i>\n"
    receipt_text += (
        f"<b>{t('lbl_date', lang)}:</b> {tx_date.strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{t('receipt_saved', lang)}"
    )

    context.user_data.clear()
    if update.callback_query:
        await update.callback_query.edit_message_text(
            receipt_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_receipt_keyboard(tx["id"], lang=lang),
        )
    else:
        await update.message.reply_html(
            receipt_text,
            reply_markup=get_receipt_keyboard(tx["id"], lang=lang),
        )

    return ConversationHandler.END


async def cancel_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel interactive flow."""
    user = update.effective_user
    lang = await db.get_user_language(user.id) if user else "en"
    context.user_data.clear()
    msg = t("cancelled", lang)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg)
    elif update.message:
        await update.message.reply_html(msg)
    return ConversationHandler.END


# =====================================================================
# DELETE TRANSACTION CALLBACK
# =====================================================================

async def delete_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle receipt delete button callback."""
    query = update.callback_query
    await query.answer()

    tx_id = query.data.replace("del_tx_", "")
    user = update.effective_user
    lang = await db.get_user_language(user.id) if user else "en"
    success = await db.delete_transaction(user.id, tx_id)

    if success:
        await query.edit_message_text(t("deleted_success", lang), parse_mode=ParseMode.HTML)
    else:
        await query.edit_message_text(t("deleted_not_found", lang), parse_mode=ParseMode.HTML)


# =====================================================================
# SUMMARY DASHBOARD (/summary & Navigation)
# =====================================================================

def compute_month_range(year: int, month: int):
    """Compute start and end UTC datetime for given month."""
    start_dt = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
    if month == 12:
        end_dt = datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1)
    else:
        end_dt = datetime(year, month + 1, 1, 0, 0, 0, tzinfo=timezone.utc) - timedelta(microseconds=1)
    return start_dt, end_dt


async def render_summary_text(user_id: int, year: int, month: int) -> str:
    """Aggregate financial totals and build formatted summary dashboard string."""
    start_dt, end_dt = compute_month_range(year, month)
    txs = await db.get_transactions_in_range(user_id, start_dt, end_dt)
    profile = await db.get_or_create_user(user_id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    total_income = 0.0
    total_expenses = 0.0
    category_expenses = {}

    for tx in txs:
        amt = float(tx.get("amount", 0.0))
        t_type = tx.get("type", "expense").lower()
        if t_type == "income":
            total_income += amt
        else:
            total_expenses += amt
            cat = tx.get("category", "Other")
            category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

    net_flow = total_income - total_expenses
    month_name = get_display_month(month, lang)

    title_str = t("summary_title", lang).format(month=month_name, year=year)
    lines = [
        title_str,
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"💰 <b>{t('total_income', lang)}:</b>   <code>{format_amount(total_income, currency)}</code>",
        f"💸 <b>{t('total_expense', lang)}:</b> <code>{format_amount(total_expenses, currency)}</code>",
    ]

    if net_flow >= 0:
        lines.append(f"📈 <b>{t('net_flow', lang)}:</b>        <code>+{format_amount(net_flow, currency)}</code> 🟢")
    else:
        lines.append(f"📉 <b>{t('net_flow', lang)}:</b>        <code>-{format_amount(abs(net_flow), currency)}</code> 🔴")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🏷️ <b>{t('breakdown', lang)}:</b>")

    if category_expenses:
        sorted_cats = sorted(category_expenses.items(), key=lambda x: x[1], reverse=True)
        for cat, amt in sorted_cats:
            icon = EXPENSE_CATEGORIES.get(cat, "📦")
            disp_cat = get_display_category(cat, lang)
            pct = (amt / total_expenses * 100) if total_expenses > 0 else 0
            lines.append(f"{icon} <b>{disp_cat}:</b> {format_amount(amt, currency)} (<code>{pct:.1f}%</code>)")
    else:
        lines.append(f"<i>{t('no_records', lang)}</i>")

    return "\n".join(lines)


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /summary or '📊 Summary' button."""
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    now = datetime.now(timezone.utc)
    text = await render_summary_text(user.id, now.year, now.month)
    await update.message.reply_html(
        text,
        reply_markup=get_summary_keyboard(now.year, now.month, lang=lang),
    )


async def summary_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle month navigation inside summary callback."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    text = await render_summary_text(user.id, year, month)
    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_summary_keyboard(year, month, lang=lang),
    )


# =====================================================================
# VISUAL DONUT CHART ENGINE
# =====================================================================

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send high-resolution donut chart for the current month."""
    user = update.effective_user
    now = datetime.now(timezone.utc)
    await send_chart_for_period(update, user.id, now.year, now.month)


async def summary_chart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle '📈 View Chart' callback from summary keyboard."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    await send_chart_for_period(update, update.effective_user.id, year, month)


async def send_chart_for_period(update: Update, user_id: int, year: int, month: int) -> None:
    """Fetch expenses, render donut chart in-memory, and send via send_photo."""
    start_dt, end_dt = compute_month_range(year, month)
    txs = await db.get_transactions_in_range(user_id, start_dt, end_dt)
    profile = await db.get_or_create_user(user_id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    total_income = 0.0
    total_expenses = 0.0
    category_expenses = {}

    for tx in txs:
        amt = float(tx.get("amount", 0.0))
        if tx.get("type", "expense").lower() == "income":
            total_income += amt
        else:
            total_expenses += amt
            cat = tx.get("category", "Other")
            category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

    month_name = get_display_month(month, lang)

    if not category_expenses:
        msg = t("no_expenses_chart", lang).format(month=month_name, year=year)
        if update.callback_query:
            await update.callback_query.message.reply_html(msg)
        else:
            await update.message.reply_html(msg)
        return

    net_balance = total_income - total_expenses
    net_sign = "+" if net_balance >= 0 else "-"
    net_badge = "🟢" if net_balance >= 0 else "🔴"

    # Generate in-memory chart with Net Balance embedded directly in center
    chart_buf = generate_expense_donut_chart(
        category_totals=category_expenses,
        month_name=month_name,
        year=year,
        currency=currency,
        total_income=total_income,
        net_balance=net_balance,
    )
    if not chart_buf:
        return

    chart_header = "📈 <b>Expense & Balance Breakdown</b>" if lang == "en" else "📈 <b>ស្ថិតិចំណាយ និងសមតុល្យសុទ្ធ</b>"
    net_lbl = t("net_flow", lang)
    inc_lbl = t("total_income", lang)
    exp_lbl = t("total_expense", lang)

    caption = (
        f"{chart_header} • {month_name} {year}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 <b>{net_lbl}:</b> <code>{net_sign}{format_amount(abs(net_balance), currency)}</code> {net_badge}\n"
        f"🟢 <b>{inc_lbl}:</b> <code>+{format_amount(total_income, currency)}</code>\n"
        f"🔴 <b>{exp_lbl}:</b> <code>-{format_amount(total_expenses, currency)}</code>"
    )

    chat_id = update.effective_chat.id
    if update.callback_query:
        await update.callback_query.message.reply_photo(
            photo=chart_buf,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_report_keyboard(year, month, lang=lang),
        )
    else:
        await update.get_bot().send_photo(
            chat_id=chat_id,
            photo=chart_buf,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_report_keyboard(year, month, lang=lang),
        )


# =====================================================================
# FINANCIAL REPORT & PIE CHART ENGINE
# =====================================================================

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and send detailed monthly financial report with Pie Chart."""
    user = update.effective_user
    now = datetime.now(timezone.utc)
    await send_pie_report_for_period(update, user.id, now.year, now.month)


async def summary_pie_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle '🥧 Pie Report' callback from summary keyboard."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    await send_pie_report_for_period(update, update.effective_user.id, year, month)


async def report_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle month navigation on the Pie Report view."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    await send_pie_report_for_period(update, update.effective_user.id, year, month)


async def send_pie_report_for_period(update: Update, user_id: int, year: int, month: int) -> None:
    """Fetch month totals, render publication-grade Pie Chart, and send with financial health caption."""
    start_dt, end_dt = compute_month_range(year, month)
    txs = await db.get_transactions_in_range(user_id, start_dt, end_dt)
    profile = await db.get_or_create_user(user_id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    total_income = 0.0
    total_expenses = 0.0
    category_expenses = {}

    for tx in txs:
        amt = float(tx.get("amount", 0.0))
        t_type = tx.get("type", "expense").lower()
        if t_type == "income":
            total_income += amt
        else:
            total_expenses += amt
            cat = tx.get("category", "Other")
            category_expenses[cat] = category_expenses.get(cat, 0.0) + amt

    month_name = get_display_month(month, lang)

    if not category_expenses:
        msg = t("no_expenses_chart", lang).format(month=month_name, year=year)
        if update.callback_query:
            await update.callback_query.message.reply_html(msg)
        else:
            await update.message.reply_html(msg)
        return

    # Generate in-memory pie chart
    pie_buf = generate_report_pie_chart(
        category_totals=category_expenses,
        month_name=month_name,
        year=year,
        currency=currency,
        total_income=total_income,
        total_expense=total_expenses,
    )
    if not pie_buf:
        return

    # Determine top expense
    top_cat, top_amt = max(category_expenses.items(), key=lambda x: x[1])
    top_disp = get_display_category(top_cat, lang)
    top_emoji = get_category_emoji(top_cat, "expense")
    top_pct = (top_amt / total_expenses * 100) if total_expenses > 0 else 0

    net_flow = total_income - total_expenses
    health_badge = t("report_health_good", lang) if net_flow >= 0 else t("report_health_warn", lang)

    title_str = t("report_title", lang).format(month=month_name, year=year)
    lines = [
        title_str,
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"💰 <b>{t('total_income', lang)}:</b>   <code>{format_amount(total_income, currency)}</code>",
        f"💸 <b>{t('total_expense', lang)}:</b> <code>{format_amount(total_expenses, currency)}</code>",
    ]

    if net_flow >= 0:
        lines.append(f"📈 <b>{t('net_flow', lang)}:</b>        <code>+{format_amount(net_flow, currency)}</code> 🟢")
    else:
        lines.append(f"📉 <b>{t('net_flow', lang)}:</b>        <code>-{format_amount(abs(net_flow), currency)}</code> 🔴")

    if total_income > 0:
        savings_rate = max(0.0, (net_flow / total_income * 100))
        lines.append(f"🏦 <b>{t('report_savings_rate', lang)}:</b> <code>{savings_rate:.1f}%</code>")

    lines.append(f"🏆 <b>{t('report_top_cat', lang)}:</b> {top_emoji} {top_disp} (<code>{top_pct:.1f}%</code>)")
    status_label = "Status" if lang == "en" else "ស្ថានភាព"
    lines.append(f"🩺 <b>{status_label}:</b> {health_badge}")

    caption = "\n".join(lines)
    chat_id = update.effective_chat.id

    if update.callback_query:
        await update.callback_query.message.reply_photo(
            photo=pie_buf,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_report_keyboard(year, month, lang=lang),
        )
    else:
        await update.get_bot().send_photo(
            chat_id=chat_id,
            photo=pie_buf,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_report_keyboard(year, month, lang=lang),
        )


async def netbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance or /netbalance: render dedicated Net Balance Card with flashback button."""
    user = update.effective_user
    now = datetime.now(timezone.utc)
    await send_net_balance_card(update, user.id, now.year, now.month)


async def report_net_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle '⚡ Net Balance Card' callback: flash back to the Net Balance overview card."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    user = update.effective_user
    await send_net_balance_card(update, user.id, year, month)


async def send_net_balance_card(update: Update, user_id: int, year: int, month: int) -> None:
    """Render a dedicated, high-impact Net Balance Card with flashback button to report."""
    start_dt, end_dt = compute_month_range(year, month)
    txs = await db.get_transactions_in_range(user_id, start_dt, end_dt)
    profile = await db.get_or_create_user(user_id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    total_income = 0.0
    total_expenses = 0.0
    wallet_balances: Dict[str, float] = {}

    for tx in txs:
        amt = float(tx.get("amount", 0.0))
        t_type = tx.get("type", "expense").lower()
        wal = tx.get("wallet", "Cash")
        if t_type == "income":
            total_income += amt
            wallet_balances[wal] = wallet_balances.get(wal, 0.0) + amt
        else:
            total_expenses += amt
            wallet_balances[wal] = wallet_balances.get(wal, 0.0) - amt

    month_name = get_display_month(month, lang)
    net_flow = total_income - total_expenses
    savings_rate = (net_flow / total_income * 100) if total_income > 0 else 0.0

    flow_sign = "+" if net_flow >= 0 else "-"
    status_icon = "🟢" if net_flow >= 0 else "🔴"
    status_text = t("lbl_surplus", lang) if net_flow >= 0 else t("lbl_deficit", lang)

    title_str = t("net_balance_title", lang).format(month=month_name, year=year)

    lines = [
        title_str,
        "━━━━━━━━━━━━━━━━━━━━━━",
        f"💵 <b>{t('net_flow', lang)}:</b>  <code>{flow_sign}{format_amount(abs(net_flow), currency)}</code> {status_icon}",
        f"🏷️ <b>Status:</b>        {status_text}",
        "──────────────────────",
        f"🟢 <b>{t('total_income', lang)}:</b>   <code>+{format_amount(total_income, currency)}</code>",
        f"🔴 <b>{t('total_expense', lang)}:</b> <code>-{format_amount(total_expenses, currency)}</code>",
    ]

    if total_income > 0:
        lines.append(f"🏦 <b>{t('report_savings_rate', lang)}:</b> <code>{max(0.0, savings_rate):.1f}%</code>")

    if wallet_balances:
        lines.append("──────────────────────")
        lines.append(f"💼 <b>{t('wallet_breakdown', lang)}:</b>")
        for wal, bal in sorted(wallet_balances.items(), key=lambda x: x[1], reverse=True):
            w_icon = "🏦" if "bank" in wal.lower() else "💵" if "cash" in wal.lower() else "💳"
            w_sign = "+" if bal >= 0 else "-"
            lines.append(f"  {w_icon} {wal}: <code>{w_sign}{format_amount(abs(bal), currency)}</code>")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(t("flashback_hint", lang))

    text = "\n".join(lines)
    kb = get_net_balance_keyboard(year, month, lang=lang)

    if update.callback_query:
        try:
            await update.callback_query.message.reply_html(text, reply_markup=kb)
        except Exception:
            await update.callback_query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_html(text, reply_markup=kb)


# =====================================================================
# INTERACTIVE INLINE CALENDAR
# =====================================================================

async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /calendar or '📅 Calendar' button: render native month calendar."""
    user = update.effective_user
    lang = await db.get_user_language(user.id)
    now = datetime.now(timezone.utc)
    markers = await db.get_month_day_markers(user.id, now.year, now.month)

    month_name = get_display_month(now.month, lang)
    if lang == "km":
        text = (
            f"📅 <b>ប្រតិទិនហិរញ្ញវត្ថុ • {month_name} {now.year}</b>\n\n"
            "<b>កំណត់សម្គាល់៖</b>\n"
            "🔴 = មានការចំណាយ\n"
            "🟢 = មានចំណូល\n"
            "🔶 = មានទាំងចំណូល និងចំណាយ\n\n"
            "<i>ចុចលើថ្ងៃដែលមានសម្គាល់ ដើម្បីមើលប្រតិបត្តិការលម្អិត។</i>"
        )
    else:
        text = (
            f"📅 <b>Financial Calendar • {month_name} {now.year}</b>\n\n"
            "<b>Legend:</b>\n"
            "🔴 = Expense logged\n"
            "🟢 = Income logged\n"
            "🔶 = Both logged on that day\n\n"
            "<i>Tap any marked day to view its transactions.</i>"
        )

    await update.message.reply_html(
        text,
        reply_markup=get_calendar_keyboard(now.year, now.month, markers, lang=lang),
    )


async def calendar_nav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle navigation (prev/next month) on the inline calendar."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])

    user = update.effective_user
    lang = await db.get_user_language(user.id)
    markers = await db.get_month_day_markers(user.id, year, month)
    month_name = get_display_month(month, lang)

    if lang == "km":
        text = (
            f"📅 <b>ប្រតិទិនហិរញ្ញវត្ថុ • {month_name} {year}</b>\n\n"
            "<b>កំណត់សម្គាល់៖</b>\n"
            "🔴 = មានការចំណាយ\n"
            "🟢 = មានចំណូល\n"
            "🔶 = មានទាំងចំណូល និងចំណាយ\n\n"
            "<i>ចុចលើថ្ងៃដែលមានសម្គាល់ ដើម្បីមើលប្រតិបត្តិការលម្អិត។</i>"
        )
    else:
        text = (
            f"📅 <b>Financial Calendar • {month_name} {year}</b>\n\n"
            "<b>Legend:</b>\n"
            "🔴 = Expense logged\n"
            "🟢 = Income logged\n"
            "🔶 = Both logged on that day\n\n"
            "<i>Tap any marked day to view its transactions.</i>"
        )

    await query.edit_message_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=get_calendar_keyboard(year, month, markers, lang=lang),
    )


async def calendar_day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle tapping on a specific day in the calendar grid."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    year = int(parts[2])
    month = int(parts[3])
    day = int(parts[4])

    user = update.effective_user
    txs = await db.get_transactions_for_day(user.id, year, month, day)
    profile = await db.get_or_create_user(user.id)
    lang = profile.get("language", "en")
    currency = profile.get("default_currency", "USD")

    date_str = f"{year}-{month:02d}-{day:02d}"
    title = f"📅 <b>Transactions on {date_str}</b>" if lang == "en" else f"📅 <b>ប្រតិបត្តិការនៅថ្ងៃ {date_str}</b>"
    lines = [
        title,
        "━━━━━━━━━━━━━━━━━━━━━━",
    ]

    if not txs:
        empty_msg = "<i>No transactions recorded on this day.</i>" if lang == "en" else "<i>មិនមានប្រតិបត្តិការត្រូវបានកត់ត្រាក្នុងថ្ងៃនេះទេ។</i>"
        lines.append(empty_msg)
    else:
        day_income = 0.0
        day_expense = 0.0

        for tx in txs:
            amt = float(tx.get("amount", 0.0))
            t_type = tx.get("type", "expense").lower()
            cat = tx.get("category", "Other")
            note = tx.get("note", "")
            disp_cat = get_display_category(cat, lang)

            if t_type == "income":
                day_income += amt
                emoji = INCOME_CATEGORIES.get(cat, "💵")
                tag = "🟢 +"
            else:
                day_expense += amt
                emoji = EXPENSE_CATEGORIES.get(cat, "📦")
                tag = "🔴 -"

            note_str = f" • <i>{note}</i>" if note else ""
            lines.append(f"{tag}<code>{format_amount(amt, currency)}</code> ({emoji} {disp_cat}){note_str}")

        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        net_label = "Day Net:" if lang == "en" else "លំហូរសុទ្ធប្រចាំថ្ងៃ៖"
        lines.append(f"<b>{net_label}</b> <code>{format_amount(day_income - day_expense, currency)}</code>")

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=get_day_detail_keyboard(year, month, lang=lang),
    )


# =====================================================================
# TELEGRAM STARS IN-APP BILLING (XTR)
# =====================================================================

async def upgrade_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Telegram Stars (XTR) invoice for Pro Tier subscription."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    timestamp = int(datetime.now(timezone.utc).timestamp())
    payload = f"pro_sub_{user.id}_{timestamp}"
    lang = await db.get_user_language(user.id)

    # Telegram Stars billing invoice
    prices = [LabeledPrice("Pro Access", PRO_PRICE_STARS)]

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=t("pro_title", lang),
        description=t("pro_desc", lang),
        payload=payload,
        currency="XTR",
        prices=prices,
        provider_token="",  # Telegram Stars requires empty provider_token
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pre-checkout validation query: confirm payment eligibility immediately."""
    query = update.pre_checkout_query
    if query.currency != "XTR":
        await query.answer(ok=False, error_message="Only Telegram Stars (XTR) payments are accepted.")
        return

    # Payment confirmed
    await query.answer(ok=True)


async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle successful Telegram Stars payment: activate Pro subscription in Firestore."""
    payment = update.message.successful_payment
    user = update.effective_user
    lang = await db.get_user_language(user.id)

    logger.info(
        "Received successful Stars payment: user=%s, amount=%s XTR, charge_id=%s",
        user.id,
        payment.total_amount,
        payment.telegram_payment_charge_id,
    )

    # Upgrade in database
    new_expiry = await db.upgrade_to_pro(user.id, duration_days=PRO_DURATION_DAYS)
    expiry_str = new_expiry.strftime("%Y-%m-%d %H:%M UTC")

    if lang == "km":
        congrats_message = (
            "🎉 <b>សូមអបអរសាទរ! អ្នកគឺជាសមាជិក PRO!</b> ⭐\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>កញ្ចប់៖</b> Money Tracker Pro ({PRO_DURATION_DAYS} ថ្ងៃ)\n"
            f"<b>បានទូទាត់៖</b> <code>{payment.total_amount} ⭐️ XTR</code>\n"
            f"<b>មានសុពលភាពរហូតដល់៖</b> <code>{expiry_str}</code>\n\n"
            "✨ <b>មុខងារពិសេសដែលបានបើក៖</b>\n"
            "• កាបូបផ្ទាល់ខ្លួនមិនកំណត់\n"
            "• ការទាញយកឯកសារ CSV ប្រចាំខែដោយស្វ័យប្រវត្តិ\n"
            "• ការព្យាករណ៍ និងវិភាគហិរញ្ញវត្ថុកម្រិតខ្ពស់\n"
            "• ការធ្វើសមកាលកម្មលើ Cloud លឿនរហ័ស\n\n"
            "សូមអរគុណសម្រាប់ការគាំទ្រការអភិវឌ្ឍន៍របស់យើង!"
        )
    else:
        congrats_message = (
            "🎉 <b>CONGRATULATIONS! YOU'RE PRO!</b> ⭐\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Plan:</b> Money Tracker Pro ({PRO_DURATION_DAYS} Days)\n"
            f"<b>Paid:</b> <code>{payment.total_amount} ⭐️ XTR</code>\n"
            f"<b>Valid Until:</b> <code>{expiry_str}</code>\n\n"
            "✨ <b>Pro Features Unlocked:</b>\n"
            "• Unlimited Custom Wallets\n"
            "• Automated Monthly CSV Exports\n"
            "• Advanced Financial Forecasts\n"
            "• Priority Cloud Synchronization\n\n"
            "Thank you for supporting our development!"
        )

    await update.message.reply_html(congrats_message)


# =====================================================================
# NOOP CALLBACK HANDLER (FOR PADDING & HEADERS)
# =====================================================================

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Acknowledge non-interactive calendar buttons silently."""
    await update.callback_query.answer()


# =====================================================================
# APPLICATION FACTORY & MAIN RUNNER
# =====================================================================

def build_application() -> Application:
    """Build and configure the Telegram Bot Application."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning(
            "TELEGRAM_BOT_TOKEN is not set! Set it in your .env file or environment variables."
        )

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN or "DUMMY_TOKEN_FOR_BUILD").build()

    # 1. Conversation Handler for Multi-step Add Expense / Income
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^(➕ Add Expense|💰 Add Income|➕ បន្ថែមការចំណាយ|💰 បន្ថែមចំណូល)$"),
                start_add_flow,
            ),
            CommandHandler("add_expense", start_add_flow),
            CommandHandler("add_income", start_add_flow),
        ],
        states={
            SELECT_CATEGORY: [
                CallbackQueryHandler(category_selected_callback, pattern=r"^cat_"),
                CallbackQueryHandler(add_new_category_callback, pattern=r"^addcat_"),
            ],
            ENTER_NEW_CATEGORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, new_category_entered),
            ],
            SELECT_WALLET: [
                CallbackQueryHandler(wallet_selected_callback, pattern=r"^wal_"),
            ],
            ENTER_AMOUNT_NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_note_entered),
            ],
            SELECT_DATE: [
                CallbackQueryHandler(date_picker_nav_callback, pattern=r"^dtnav_"),
                CallbackQueryHandler(date_picker_day_callback, pattern=r"^dtday_"),
                CallbackQueryHandler(date_selection_callback, pattern=r"^datesel_"),
            ],
            SELECT_TIME: [
                CallbackQueryHandler(time_picker_callback, pattern=r"^dttime_"),
                CallbackQueryHandler(date_picker_nav_callback, pattern=r"^dtnav_"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_flow),
            CallbackQueryHandler(cancel_flow, pattern="^cancel_flow$"),
        ],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)

    # 2. Command Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("language", language_command))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("calendar", calendar_command))
    app.add_handler(CommandHandler("chart", chart_command))
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("balance", netbalance_command))
    app.add_handler(CommandHandler("netbalance", netbalance_command))
    app.add_handler(CommandHandler("upgrade", upgrade_command))

    # 3. Persistent Reply Button Messages (English & Khmer)
    app.add_handler(MessageHandler(filters.Regex(r"^(📊 Summary|📊 សង្ខេបហិរញ្ញវត្ថុ)$"), summary_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(📅 Calendar|📅 ប្រតិទិន)$"), calendar_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(📈 Chart|📈 គំនូសតារាង)$"), chart_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(🥧 Pie Report|🥧 របាយការណ៍គំនូសរង្វង់|📊 Report|📊 របាយការណ៍)$"), report_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(⚡ Net Balance Card|⚡ កាតសមតុល្យសុទ្ធ|⚡ Net Balance|⚡ សមតុល្យសុទ្ធ)$"), netbalance_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(⭐ Upgrade to Pro|⭐ ដំឡើងទៅ Pro)$"), upgrade_command))
    app.add_handler(MessageHandler(filters.Regex(r"^(🌐 Language / ភាសា|🌐 Language|🌐 ភាសា)$"), language_command))

    # 4. Fast-log Regex Handler
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(?:(\d{4}-\d{2}-\d{2})\s+)?([+-])(\d+(?:\.\d{1,2})?)\s+([A-Za-z0-9&_]+)"),
            fast_log_handler,
        )
    )

    # 5. Language Switcher Callback
    app.add_handler(CallbackQueryHandler(set_language_callback, pattern=r"^set_lang_"))

    # 6. Receipt Delete Callback
    app.add_handler(CallbackQueryHandler(delete_transaction_callback, pattern=r"^del_tx_"))

    # 7. Summary Navigation, Chart & Pie Report Callbacks
    app.add_handler(CallbackQueryHandler(summary_nav_callback, pattern=r"^sum_nav_"))
    app.add_handler(CallbackQueryHandler(summary_chart_callback, pattern=r"^sum_chart_"))
    app.add_handler(CallbackQueryHandler(summary_pie_callback, pattern=r"^sum_pie_"))
    app.add_handler(CallbackQueryHandler(report_nav_callback, pattern=r"^rep_nav_"))
    app.add_handler(CallbackQueryHandler(report_net_callback, pattern=r"^rep_net_"))

    # 8. Calendar Callbacks
    app.add_handler(CallbackQueryHandler(calendar_nav_callback, pattern=r"^cal_nav_"))
    app.add_handler(CallbackQueryHandler(calendar_day_callback, pattern=r"^cal_day_"))

    # 9. Telegram Stars Payment Handlers
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler))

    # 10. No-op Header/Padding buttons
    app.add_handler(CallbackQueryHandler(noop_callback, pattern="^noop$"))

    return app


def main():
    """Start polling loop."""
    logger.info("Starting Money Tracker Telegram Bot...")
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Please configure TELEGRAM_BOT_TOKEN in .env before running.")
        return

    app = build_application()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

