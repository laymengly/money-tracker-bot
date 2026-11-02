"""
Bilingual localization strings (English & Khmer) for Money Tracker Ecosystem.
"""

from typing import Dict, Any

LOCALES: Dict[str, Dict[str, str]] = {
    "en": {
        # Buttons
        "btn_add_expense": "➕ Add Expense",
        "btn_add_income": "💰 Add Income",
        "btn_summary": "📊 Summary",
        "btn_calendar": "📅 Calendar",
        "btn_chart": "📈 Chart",
        "btn_upgrade": "⭐ Upgrade to Pro",
        "btn_mini_app": "📱 Open Mini App",
        "btn_language": "🌐 Language / ភាសា",
        "btn_today": "⚡ Today",
        "btn_yesterday": "⏪ Yesterday",
        "btn_cancel": "❌ Cancel",
        "btn_add_category": "➕ Add New Category",
        "btn_delete": "🗑️ Delete",
        "btn_back_cal": "🔙 Back to Calendar",
        "btn_back_date": "🔙 Pick Another Date",
        "btn_view_chart": "📈 View Chart",
        "btn_pie_report": "🥧 Pie Report",
        "btn_net_balance": "⚡ Net Balance Card",
        "btn_back_to_report": "🥧 Back to Report",
        "btn_prev_month": "◀ Prev Month",
        "btn_next_month": "Next Month ▶",

        # Titles & Prompts
        "select_expense_cat": "➕ <b>Select Expense Category:</b>",
        "select_income_cat": "💰 <b>Select Income Category:</b>",
        "select_wallet": "💳 <b>Select Wallet/Account:</b>",
        "enter_amount_note": "✍️ <b>Enter amount and optional note:</b>\nExamples:\n• <code>25</code>\n• <code>45.50 Dinner with family</code>\n\n<i>Send your text now or /cancel:</i>",
        "select_date": "📅 <b>Select Date (Interactive Calendar):</b>\n<i>Tap a date like a mobile phone calendar picker:</i>",
        "choose_time": "⏰ <b>Choose Time:</b>\nTap current time or a quick preset below:",
        "invalid_amount": "⚠️ <b>Invalid Amount!</b>\nPlease enter a valid positive number, e.g. <code>18.50 Groceries</code>\nTry again or send /cancel.",
        "invalid_cat_name": "⚠️ <b>Invalid Category Name:</b>\nPlease keep it between 1 and 30 characters. Try again or send /cancel:",
        "enter_new_cat": "✨ <b>Enter New Category Name:</b>\n\nSend the name for your custom category (e.g. <i>Coffee</i>, <i>Gym</i>, <i>Freelance</i>):\n\n<i>Or send /cancel to abort.</i>",
        "cat_added": "✅ Added category: <b>{emoji} {category}</b>\n\n💳 <b>Select Wallet/Account:</b>",
        "cancelled": "❌ Action cancelled.",
        "deleted_success": "🗑️ <i>Transaction deleted successfully.</i>",
        "deleted_not_found": "⚠️ <i>Transaction already deleted or not found.</i>",
        "lang_switch_prompt": "🌐 <b>Select Language / ជ្រើសរើសភាសា:</b>",
        "lang_changed": "✓ Language set to <b>English 🇺🇸</b>.",

        # Receipts
        "expense_logged": "🔴 Expense Logged",
        "income_logged": "🟢 Income Logged",
        "lbl_amount": "Amount",
        "lbl_category": "Category",
        "lbl_wallet": "Wallet",
        "lbl_note": "Note",
        "lbl_date": "Date",
        "receipt_saved": "<i>Transaction saved successfully!</i>",
        "receipt_undo": "<i>Tap below to undo if made in error.</i>",

        # Summary & Chart
        "summary_title": "📊 <b>Financial Summary • {month} {year}</b>",
        "report_title": "🥧 <b>Financial Report • {month} {year}</b>",
        "report_top_cat": "Top Spending",
        "report_savings_rate": "Savings Rate",
        "report_health_good": "🟢 Healthy Cash Flow",
        "report_health_warn": "🔴 Deficit Warning (Expenses > Income)",
        "total_income": "Total Income",
        "total_expense": "Total Expenses",
        "net_flow": "Net Flow",
        "breakdown": "Category Breakdown",
        "no_records": "No expense records found for this period.",
        "no_expenses_chart": "ℹ️ <b>No expenses found</b> for {month} {year}. Add expenses first to generate charts!",
        "net_balance_title": "💳 <b>NET BALANCE CARD • {month} {year}</b>",
        "wallet_breakdown": "Wallets Breakdown",
        "flashback_hint": "⚡ <i>Tap '🥧 Back to Report' to flashback to Pie Chart.</i>",
        "lbl_surplus": "🟢 Surplus",
        "lbl_deficit": "🔴 Deficit",

        # Pro & Billing
        "pro_badge": "⭐ <b>PRO MEMBER</b>",
        "free_badge": "🆓 Free Tier",
        "pro_title": "Money Tracker Pro (30 Days)",
        "pro_desc": "Unlock unlimited wallets, CSV exports, and AI analytics",
    },
    "km": {
        # Buttons
        "btn_add_expense": "➕ បន្ថែមការចំណាយ",
        "btn_add_income": "💰 បន្ថែមចំណូល",
        "btn_summary": "📊 សង្ខេបហិរញ្ញវត្ថុ",
        "btn_calendar": "📅 ប្រតិទិន",
        "btn_chart": "📈 គំនូសតារាង",
        "btn_upgrade": "⭐ ដំឡើងទៅ Pro",
        "btn_mini_app": "📱 បើក Mini App",
        "btn_language": "🌐 Language / ភាសា",
        "btn_today": "⚡ ថ្ងៃនេះ",
        "btn_yesterday": "⏪ ម្សិលមិញ",
        "btn_cancel": "❌ បោះបង់",
        "btn_add_category": "➕ បន្ថែមប្រភេទថ្មី",
        "btn_delete": "🗑️ លុបចោល",
        "btn_back_cal": "🔙 ត្រឡប់ទៅប្រតិទិន",
        "btn_back_date": "🔙 ជ្រើសរើសកាលបរិច្ឆេទផ្សេង",
        "btn_view_chart": "📈 មើលតារាង",
        "btn_pie_report": "🥧 របាយការណ៍គំនូសរង្វង់",
        "btn_net_balance": "⚡ កាតសមតុល្យសុទ្ធ",
        "btn_back_to_report": "🥧 ត្រឡប់ទៅរបាយការណ៍",
        "btn_prev_month": "◀ ខែមុន",
        "btn_next_month": "ខែបន្ទាប់ ▶",

        # Titles & Prompts
        "select_expense_cat": "➕ <b>ជ្រើសរើសប្រភេទចំណាយ៖</b>",
        "select_income_cat": "💰 <b>ជ្រើសរើសប្រភេទចំណូល៖</b>",
        "select_wallet": "💳 <b>ជ្រើសរើសកាបូប/គណនី៖</b>",
        "enter_amount_note": "✍️ <b>បញ្ចូលចំនួនទឹកប្រាក់ និងកំណត់ចំណាំ៖</b>\nឧទាហរណ៍៖\n• <code>25</code>\n• <code>45.50 ញ៉ាំបាយជាមួយគ្រួសារ</code>\n\n<i>ផ្ញើសារឥឡូវនេះ ឬផ្ញើ /cancel៖</i>",
        "select_date": "📅 <b>ជ្រើសរើសកាលបរិច្ឆេទ (ប្រតិទិន)៖</b>\n<i>ចុចលើថ្ងៃដូចនៅលើទូរស័ព្ទដៃ៖</i>",
        "choose_time": "⏰ <b>ជ្រើសរើសពេលវេលា៖</b>\nចុចលើម៉ោងបច្ចុប្បន្ន ឬម៉ោងកំណត់រហ័សខាងក្រោម៖",
        "invalid_amount": "⚠️ <b>ចំនួនទឹកប្រាក់មិនត្រឹមត្រូវ!</b>\nសូមបញ្ចូលលេខវិជ្ជមាន ឧ. <code>18.50 ទិញម្ហូប</code>\nព្យាយាមម្តងទៀត ឬផ្ញើ /cancel។",
        "invalid_cat_name": "⚠️ <b>ឈ្មោះប្រភេទមិនត្រឹមត្រូវ!</b>\nសូមដាក់ឈ្មោះចន្លោះពី 1 ទៅ 30 តួអក្សរ។ ព្យាយាមម្តងទៀត ឬផ្ញើ /cancel៖",
        "enter_new_cat": "✨ <b>បញ្ចូលឈ្មោះប្រភេទថ្មី៖</b>\n\nផ្ញើឈ្មោះប្រភេទផ្ទាល់ខ្លួនរបស់អ្នក (ឧ. <i>កាហ្វេ</i>, <i>កីឡា</i>, <i>ការងារក្រៅម៉ោង</i>)៖\n\n<i>ឬផ្ញើ /cancel ដើម្បីបោះបង់។</i>",
        "cat_added": "✅ បានបន្ថែមប្រភេទ៖ <b>{emoji} {category}</b>\n\n💳 <b>ជ្រើសរើសកាបូប/គណនី៖</b>",
        "cancelled": "❌ បានបោះបង់សកម្មភាព។",
        "deleted_success": "🗑️ <i>ប្រតិបត្តិការត្រូវបានលុបដោយជោគជ័យ។</i>",
        "deleted_not_found": "⚠️ <i>ប្រតិបត្តិការត្រូវបានលុប ឬរកមិនឃើញ។</i>",
        "lang_switch_prompt": "🌐 <b>ជ្រើសរើសភាសា / Select Language:</b>",
        "lang_changed": "✓ ភាសាត្រូវបានប្តូរទៅជា <b>ភាសាខ្មែរ 🇰🇭</b>។",

        # Receipts
        "expense_logged": "🔴 បានកត់ត្រាការចំណាយ",
        "income_logged": "🟢 បានកត់ត្រាចំណូល",
        "lbl_amount": "ចំនួនទឹកប្រាក់",
        "lbl_category": "ប្រភេទ",
        "lbl_wallet": "កាបូប",
        "lbl_note": "ចំណាំ",
        "lbl_date": "កាលបរិច្ឆេទ",
        "receipt_saved": "<i>បានរក្សាទុកប្រតិបត្តិការដោយជោគជ័យ!</i>",
        "receipt_undo": "<i>ចុចប៊ូតុងខាងក្រោមដើម្បីលុបវិញ ប្រសិនបើកត់ត្រាខុស។</i>",

        # Summary & Chart
        "summary_title": "📊 <b>សង្ខេបហិរញ្ញវត្ថុ • {month} {year}</b>",
        "report_title": "🥧 <b>របាយការណ៍ហិរញ្ញវត្ថុ • {month} {year}</b>",
        "report_top_cat": "ចំណាយច្រើនជាងគេ",
        "report_savings_rate": "អត្រាសន្សំប្រាក់",
        "report_health_good": "🟢 លំហូរសាច់ប្រាក់ល្អប្រសើរ",
        "report_health_warn": "🔴 ការព្រមានឱនភាព (ចំណាយលើសចំណូល)",
        "total_income": "ចំណូលសរុប",
        "total_expense": "ចំណាយសរុប",
        "net_flow": "លំហូរសុទ្ធ",
        "breakdown": "ការបែងចែកតាមប្រភេទ",
        "no_records": "មិនមានកំណត់ត្រាចំណាយក្នុងកាលបរិច្ឆេទនេះទេ។",
        "no_expenses_chart": "ℹ️ <b>មិនមានទិន្នន័យចំណាយ</b> សម្រាប់ខែ {month} {year} ទេ។ សូមកត់ត្រាចំណាយជាមុនសិន ដើម្បីបង្កើតគំនូសតារាង!",
        "net_balance_title": "💳 <b>កាតសមតុល្យសុទ្ធ • {month} {year}</b>",
        "wallet_breakdown": "សមតុល្យតាមកាបូប",
        "flashback_hint": "⚡ <i>ចុច '🥧 ត្រឡប់ទៅរបាយការណ៍' ដើម្បីផ្លាស់ប្តូរទៅកាន់គំនូសរង្វង់ភ្លាមៗ។</i>",
        "lbl_surplus": "🟢 លើសសាច់ប្រាក់",
        "lbl_deficit": "🔴 ឱនភាព",

        # Pro & Billing
        "pro_badge": "⭐ <b>សមាជិក PRO</b>",
        "free_badge": "🆓 កម្រិតឥតគិតថ្លៃ",
        "pro_title": "Money Tracker Pro (30 ថ្ងៃ)",
        "pro_desc": "ដោះសោកាបូបប្រាក់មិនកំណត់ ទាញយក CSV និងការវិភាគ AI",
    }
}

# Category labels in Khmer
CATEGORY_TRANSLATIONS_KM: Dict[str, str] = {
    "Food": "អាហារ",
    "Transport": "ធ្វើដំណើរ",
    "Bills": "វិក្កយបត្រ",
    "Shopping": "ទិញទំនិញ",
    "Entertainment": "កម្សាន្ត",
    "Health": "សុខភាព",
    "Groceries": "គ្រឿងទេស",
    "Education": "ការសិក្សា",
    "Other": "ផ្សេងៗ",
    "Salary": "ប្រាក់ខែ",
    "Freelance": "ការងារក្រៅម៉ោង",
    "Investment": "វិនិយោគ",
    "Bonus": "ប្រាក់រង្វាន់",
    "Refund": "ប្រាក់បង្វិល",
}

# Khmer Month Names
KHMER_MONTHS = [
    "",
    "មករា",
    "កុម្ភៈ",
    "មីនា",
    "មេសា",
    "ឧសភា",
    "មិថុនា",
    "កក្កដា",
    "សីហា",
    "កញ្ញា",
    "តុលា",
    "វិច្ឆិកា",
    "ធ្នូ",
]


def t(key: str, lang: str = "en", **kwargs) -> str:
    """Retrieve localized string with optional format kwargs."""
    target_lang = lang if lang in LOCALES else "en"
    text = LOCALES[target_lang].get(key, LOCALES["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def get_display_category(category: str, lang: str = "en") -> str:
    """Translate standard category name to Khmer if requested."""
    if lang == "km" and category in CATEGORY_TRANSLATIONS_KM:
        return CATEGORY_TRANSLATIONS_KM[category]
    return category


def get_display_month(month_num: int, lang: str = "en") -> str:
    """Get month name in English or Khmer."""
    if lang == "km" and 1 <= month_num <= 12:
        return KHMER_MONTHS[month_num]
    import calendar
    return calendar.month_name[month_num]
