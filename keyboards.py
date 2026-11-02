"""
Keyboards module for Telegram Bot with bilingual English & Khmer support.
"""

import calendar
from datetime import datetime, timezone
from typing import Dict, List, Optional
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from config import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    WEBAPP_URL,
    get_category_emoji,
)
from locales import t, get_display_category, get_display_month


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard for switching user language."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en"),
            InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ", callback_data="set_lang_km"),
        ]
    ])


def get_main_reply_keyboard(
    webapp_url: Optional[str] = None, lang: str = "en"
) -> ReplyKeyboardMarkup:
    """
    Persistent main menu keyboard docked at chat bottom.
    Supports English & Khmer.
    """
    keyboard = [
        [
            KeyboardButton(t("btn_add_expense", lang)),
            KeyboardButton(t("btn_add_income", lang)),
        ],
        [
            KeyboardButton(t("btn_summary", lang)),
            KeyboardButton(t("btn_calendar", lang)),
        ],
        [
            KeyboardButton(t("btn_chart", lang)),
            KeyboardButton(t("btn_pie_report", lang)),
        ],
        [
            KeyboardButton(t("btn_upgrade", lang)),
            KeyboardButton(t("btn_language", lang)),
        ],
    ]

    target_url = webapp_url or WEBAPP_URL
    if target_url and target_url.startswith("http"):
        keyboard.append([
            KeyboardButton(t("btn_mini_app", lang), web_app=WebAppInfo(url=target_url))
        ])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def get_category_keyboard(
    categories: Optional[List[str]] = None,
    tx_type: str = "expense",
    lang: str = "en",
) -> InlineKeyboardMarkup:
    """Generate 3-column inline grid of categories with emojis and Add Category button."""
    if categories is None:
        categories = list(EXPENSE_CATEGORIES.keys() if tx_type == "expense" else INCOME_CATEGORIES.keys())

    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    for name in categories:
        emoji = get_category_emoji(name, tx_type)
        display_name = get_display_category(name, lang)
        row.append(
            InlineKeyboardButton(
                text=f"{emoji} {display_name}",
                callback_data=f"cat_{tx_type}_{name}",
            )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Add custom category & cancel buttons
    buttons.append([InlineKeyboardButton(t("btn_add_category", lang), callback_data=f"addcat_{tx_type}")])
    buttons.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_flow")])
    return InlineKeyboardMarkup(buttons)


def get_date_selection_keyboard(
    year: Optional[int] = None, month: Optional[int] = None, lang: str = "en"
) -> InlineKeyboardMarkup:
    """Interactive phone-like calendar date picker with month navigation."""
    now = datetime.now(timezone.utc)
    target_year = year or now.year
    target_month = month or now.month

    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_days = cal.monthdayscalendar(target_year, target_month)
    month_name = get_display_month(target_month, lang)

    prev_month = 12 if target_month == 1 else target_month - 1
    prev_year = target_year - 1 if target_month == 1 else target_year
    next_month = 1 if target_month == 12 else target_month + 1
    next_year = target_year + 1 if target_month == 12 else target_year

    keyboard: List[List[InlineKeyboardButton]] = []

    # Navigation header
    keyboard.append([
        InlineKeyboardButton("◀", callback_data=f"dtnav_{prev_year}_{prev_month}"),
        InlineKeyboardButton(f"🗓️ {month_name} {target_year}", callback_data="noop"),
        InlineKeyboardButton("▶", callback_data=f"dtnav_{next_year}_{next_month}"),
    ])

    # Weekday row
    weekdays = ["ច", "អ", "ព", "ព្រ", "សុ", "ស", "អា"] if lang == "km" else ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    keyboard.append([InlineKeyboardButton(w, callback_data="noop") for w in weekdays])

    # Day buttons grid
    for week in month_days:
        row: List[InlineKeyboardButton] = []
        for d in week:
            if d == 0:
                row.append(InlineKeyboardButton(" ", callback_data="noop"))
            else:
                is_today = (target_year == now.year and target_month == now.month and d == now.day)
                label = f"•{d}•" if is_today else f"{d}"
                row.append(
                    InlineKeyboardButton(
                        label,
                        callback_data=f"dtday_{target_year}_{target_month}_{d}",
                    )
                )
        keyboard.append(row)

    # Quick action shortcuts
    keyboard.append([
        InlineKeyboardButton(t("btn_today", lang), callback_data="datesel_today"),
        InlineKeyboardButton(t("btn_yesterday", lang), callback_data="datesel_yesterday"),
    ])

    # Cancel
    keyboard.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_flow")])
    return InlineKeyboardMarkup(keyboard)


def get_time_picker_keyboard(
    year: int, month: int, day: int, lang: str = "en"
) -> InlineKeyboardMarkup:
    """Selectable time picker keyboard for the chosen date."""
    now = datetime.now(timezone.utc)
    current_time_str = now.strftime("%H:%M")

    curr_label = f"⚡ ម៉ោងឥឡូវ ({current_time_str} UTC)" if lang == "km" else f"⚡ Current Time ({current_time_str} UTC)"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(curr_label, callback_data=f"dttime_{year}_{month}_{day}_{now.hour}_{now.minute}"),
        ],
        [
            InlineKeyboardButton("🌅 09:00", callback_data=f"dttime_{year}_{month}_{day}_9_0"),
            InlineKeyboardButton("☀️ 12:00", callback_data=f"dttime_{year}_{month}_{day}_12_0"),
            InlineKeyboardButton("☕ 15:00", callback_data=f"dttime_{year}_{month}_{day}_15_0"),
        ],
        [
            InlineKeyboardButton("🌆 18:00", callback_data=f"dttime_{year}_{month}_{day}_18_0"),
            InlineKeyboardButton("🍽️ 20:00", callback_data=f"dttime_{year}_{month}_{day}_20_0"),
            InlineKeyboardButton("🌙 22:00", callback_data=f"dttime_{year}_{month}_{day}_22_0"),
        ],
        [
            InlineKeyboardButton(t("btn_back_date", lang), callback_data=f"dtnav_{year}_{month}"),
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_flow"),
        ],
    ])


def get_wallet_keyboard(
    wallets: List[str], tx_type: str, category: str, lang: str = "en"
) -> InlineKeyboardMarkup:
    """Render registered wallet options as inline buttons."""
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []

    for w in wallets:
        icon = "🏦" if "bank" in w.lower() else "💵" if "cash" in w.lower() else "💳"
        row.append(
            InlineKeyboardButton(
                text=f"{icon} {w}",
                callback_data=f"wal_{tx_type}_{category}_{w}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(t("btn_cancel", lang), callback_data="cancel_flow")])
    return InlineKeyboardMarkup(buttons)


def get_receipt_keyboard(tx_id: str, lang: str = "en") -> InlineKeyboardMarkup:
    """Receipt confirmation inline keyboard with a quick delete button."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_delete", lang), callback_data=f"del_tx_{tx_id}")]
    ])


def get_summary_keyboard(year: int, month: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Navigation, chart, and net balance card trigger buttons for monthly summary."""
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_prev_month", lang), callback_data=f"sum_nav_{prev_year}_{prev_month}"),
            InlineKeyboardButton(t("btn_next_month", lang), callback_data=f"sum_nav_{next_year}_{next_month}"),
        ],
        [
            InlineKeyboardButton(t("btn_view_chart", lang), callback_data=f"sum_chart_{year}_{month}"),
            InlineKeyboardButton(t("btn_pie_report", lang), callback_data=f"sum_pie_{year}_{month}"),
        ],
        [
            InlineKeyboardButton(t("btn_net_balance", lang), callback_data=f"rep_net_{year}_{month}"),
        ],
    ])


def get_report_keyboard(year: int, month: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Navigation and view options for monthly financial pie report with Net Balance flashback."""
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    lbl_sum = "📊 សង្ខេបប្រចាំខែ" if lang == "km" else "📊 Summary View"
    lbl_donut = "🍩 គំនូសតារាង Donut" if lang == "km" else "🍩 Donut View"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("btn_prev_month", lang), callback_data=f"rep_nav_{prev_year}_{prev_month}"),
            InlineKeyboardButton(t("btn_next_month", lang), callback_data=f"rep_nav_{next_year}_{next_month}"),
        ],
        [
            InlineKeyboardButton(t("btn_net_balance", lang), callback_data=f"rep_net_{year}_{month}"),
            InlineKeyboardButton(lbl_donut, callback_data=f"sum_chart_{year}_{month}"),
        ],
        [
            InlineKeyboardButton(lbl_sum, callback_data=f"sum_nav_{year}_{month}"),
        ],
    ])


def get_net_balance_keyboard(year: int, month: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Navigation keyboard for the Net Balance Card view with flashback button to report."""
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year

    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    lbl_back_rep = t("btn_back_to_report", lang)
    lbl_donut = "🍩 គំនូសតារាង Donut" if lang == "km" else "🍩 Donut View"
    lbl_sum = "📊 សង្ខេបប្រចាំខែ" if lang == "km" else "📊 Summary View"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(lbl_back_rep, callback_data=f"rep_nav_{year}_{month}"),
            InlineKeyboardButton(lbl_donut, callback_data=f"sum_chart_{year}_{month}"),
        ],
        [
            InlineKeyboardButton(t("btn_prev_month", lang), callback_data=f"rep_net_{prev_year}_{prev_month}"),
            InlineKeyboardButton(t("btn_next_month", lang), callback_data=f"rep_net_{next_year}_{next_month}"),
        ],
        [
            InlineKeyboardButton(lbl_sum, callback_data=f"sum_nav_{year}_{month}"),
        ],
    ])


def get_calendar_keyboard(
    year: int,
    month: int,
    day_markers: Optional[Dict[int, str]] = None,
    lang: str = "en",
) -> InlineKeyboardMarkup:
    """Generate an inline keyboard representing the month grid with bilingual weekday headers."""
    markers = day_markers or {}
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_days = cal.monthdayscalendar(year, month)
    month_name = get_display_month(month, lang)

    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    next_month = 1 if month == 12 else month + 1
    next_year = year + 1 if month == 12 else year

    keyboard: List[List[InlineKeyboardButton]] = []

    # Row 1: Header with Month, Year and Nav buttons
    header_row = [
        InlineKeyboardButton("◀", callback_data=f"cal_nav_{prev_year}_{prev_month}"),
        InlineKeyboardButton(f"{month_name} {year}", callback_data="noop"),
        InlineKeyboardButton("▶", callback_data=f"cal_nav_{next_year}_{next_month}"),
    ]
    keyboard.append(header_row)

    # Row 2: Weekday names
    weekdays = ["ច", "អ", "ព", "ព្រ", "សុ", "ស", "អា"] if lang == "km" else ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    keyboard.append([InlineKeyboardButton(w, callback_data="noop") for w in weekdays])

    # Day rows
    for week in month_days:
        week_row: List[InlineKeyboardButton] = []
        for day in week:
            if day == 0:
                week_row.append(InlineKeyboardButton(" ", callback_data="noop"))
            else:
                marker = markers.get(day)
                if marker == "both":
                    label = f"{day}🔶"
                elif marker == "income":
                    label = f"{day}🟢"
                elif marker == "expense":
                    label = f"{day}🔴"
                else:
                    label = f"{day}"

                week_row.append(
                    InlineKeyboardButton(
                        label,
                        callback_data=f"cal_day_{year}_{month}_{day}",
                    )
                )
        keyboard.append(week_row)

    # Quick Jump to Today
    now = datetime.now(timezone.utc)
    lbl_today = "📅 ថ្ងៃនេះ" if lang == "km" else "📅 Jump to Today"
    lbl_sum = "📊 សង្ខេបប្រចាំខែ" if lang == "km" else "📊 Monthly Summary"
    keyboard.append([
        InlineKeyboardButton(lbl_today, callback_data=f"cal_nav_{now.year}_{now.month}"),
        InlineKeyboardButton(lbl_sum, callback_data=f"sum_nav_{year}_{month}"),
    ])

    return InlineKeyboardMarkup(keyboard)


def get_day_detail_keyboard(year: int, month: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Button to return back to calendar view from day breakdown."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back_cal", lang), callback_data=f"cal_nav_{year}_{month}")]
    ])
