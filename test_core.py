"""
Automated unit verification for Money Tracker ecosystem.
"""

import sys
import asyncio
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from bot import FAST_LOG_REGEX
from database import db
from keyboards import (
    get_main_reply_keyboard,
    get_calendar_keyboard,
    get_summary_keyboard,
    get_category_keyboard,
    get_date_selection_keyboard,
    get_time_picker_keyboard,
    get_report_keyboard,
    get_net_balance_keyboard,
)
from charts import generate_expense_donut_chart, generate_report_pie_chart


async def run_tests():
    print("Testing Regex Fast-Log Parser (with optional date)...")
    test_cases = [
        ("-15 Food Team lunch", (None, "-", "15", "Food", "Team lunch")),
        ("2026-10-18 -25.50 Food Dinner", ("2026-10-18", "-", "25.50", "Food", "Dinner")),
        ("+3000 Salary Monthly payroll", (None, "+", "3000", "Salary", "Monthly payroll")),
        ("2026-10-01 +500 Freelance Web project", ("2026-10-01", "+", "500", "Freelance", "Web project")),
        ("-4.50 Coffee", (None, "-", "4.50", "Coffee", None)),
        ("+50 Freelance", (None, "+", "50", "Freelance", None)),
    ]
    for text, expected in test_cases:
        match = FAST_LOG_REGEX.match(text)
        assert match is not None, f"Failed to match: {text}"
        groups = match.groups()
        assert groups[0] == expected[0], f"Date mismatch: {groups[0]} vs {expected[0]}"
        assert groups[1] == expected[1], f"Sign mismatch: {groups[1]} vs {expected[1]}"
        assert groups[2] == expected[2], f"Amount mismatch: {groups[2]} vs {expected[2]}"
        assert groups[3] == expected[3], f"Category mismatch: {groups[3]} vs {expected[3]}"
        assert groups[4] == expected[4], f"Note mismatch: {groups[4]} vs {expected[4]}"
    print("✓ Fast-log regex matches standard and date-prefixed patterns.")

    print("\nTesting Database Tenant Isolation & Schema...")
    user_id = 999888777
    user = await db.get_or_create_user(user_id)
    assert user["is_pro"] is False
    assert user["default_currency"] == "USD"
    assert user["default_wallet"] == "Bank"
    assert "Cash" in user["wallets"]
    print("✓ User profile initialized with tenant isolation.")

    # Add expense
    tx_exp = await db.add_transaction(
        user_id=user_id,
        tx_type="expense",
        category="Food",
        amount=15.50,
        note="Lunch",
    )
    assert tx_exp["id"] is not None
    assert tx_exp["amount"] == 15.50
    assert tx_exp["type"] == "expense"

    # Add income
    tx_inc = await db.add_transaction(
        user_id=user_id,
        tx_type="income",
        category="Salary",
        amount=3000.0,
        note="Payday",
    )
    assert tx_inc["type"] == "income"
    print("✓ Transactions created successfully.")

    # Day markers
    now = datetime.now(timezone.utc)
    markers = await db.get_month_day_markers(user_id, now.year, now.month)
    assert markers.get(now.day) == "both", f"Expected day {now.day} to have marker 'both', got: {markers.get(now.day)}"
    print(f"✓ Calendar day markers computed correctly: day {now.day} marked as '{markers.get(now.day)}'.")

    # Pro upgrade
    expiry = await db.upgrade_to_pro(user_id, 30)
    user_updated = await db.get_user(user_id)
    assert user_updated["is_pro"] is True
    assert user_updated["pro_expires_at"] == expiry
    print("✓ Pro tier upgrade and expiration timestamp verified.")

    # Custom Category addition
    await db.add_user_category(user_id, "expense", "Gym")
    user_cats = await db.get_user_categories(user_id, "expense")
    assert "Gym" in user_cats, "Gym category should be in user expense categories!"
    print("✓ Custom user category ('Gym') added and queried successfully.")

    # Clean delete
    del_res = await db.delete_transaction(user_id, tx_exp["id"])
    assert del_res is True
    print("✓ Delete transaction confirmed.")

    print("\nTesting Keyboards...")
    main_kb = get_main_reply_keyboard("https://example.com/tma")
    assert len(main_kb.keyboard) >= 3
    cal_kb = get_calendar_keyboard(now.year, now.month, markers)
    assert len(cal_kb.inline_keyboard) > 3
    cat_kb = get_category_keyboard(user_cats, "expense")
    assert any("Gym" in btn.text for row in cat_kb.inline_keyboard for btn in row)
    assert any("Add New Category" in btn.text for row in cat_kb.inline_keyboard for btn in row)
    date_kb = get_date_selection_keyboard(2026, 10)
    assert len(date_kb.inline_keyboard) >= 6, "Interactive date picker should render header, weekdays, day rows, shortcuts and cancel!"
    assert any("Mo" in btn.text for btn in date_kb.inline_keyboard[1]), "Should contain weekday headers"
    time_kb = get_time_picker_keyboard(2026, 10, 19)
    assert len(time_kb.inline_keyboard) >= 4, "Time picker should provide current time, presets, and back button"
    print("✓ Reply, Calendar, Custom Category, Interactive Date Picker, and Time Picker keyboards verified.")

    print("\nTesting In-Memory Donut Chart Generation (with Net Balance)...")
    category_totals = {"Food": 150.0, "Bills": 80.0, "Transport": 45.0}
    chart_buf = generate_expense_donut_chart(
        category_totals, "October", 2026, "USD", total_income=3000.0, net_balance=2725.0
    )
    assert chart_buf is not None
    data = chart_buf.getvalue()
    assert len(data) > 1000
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Generated buffer is not a valid PNG!"
    print(f"✓ Donut chart generated in-memory with Net Balance embedded: {len(data)} bytes (valid PNG header).")

    print("\nTesting In-Memory Financial Report Pie Chart Generation...")
    pie_buf = generate_report_pie_chart(
        category_totals=category_totals,
        month_name="October",
        year=2026,
        currency="USD",
        total_income=3000.0,
        total_expense=275.0,
    )
    assert pie_buf is not None
    pie_data = pie_buf.getvalue()
    assert len(pie_data) > 1000
    assert pie_data[:8] == b"\x89PNG\r\n\x1a\n", "Generated pie report buffer is not a valid PNG!"
    print(f"✓ Financial Pie Chart generated in-memory with size: {len(pie_data)} bytes (valid PNG header).")

    print("\nTesting Report Navigation & Flashback Net Balance Keyboards...")
    rep_kb_en = get_report_keyboard(2026, 10, lang="en")
    assert any("Donut" in btn.text for row in rep_kb_en.inline_keyboard for btn in row)
    assert any("Net Balance" in btn.text for row in rep_kb_en.inline_keyboard for btn in row)

    rep_kb_km = get_report_keyboard(2026, 10, lang="km")
    assert any("Donut" in btn.text for row in rep_kb_km.inline_keyboard for btn in row)
    assert any("ខែមុន" in btn.text for row in rep_kb_km.inline_keyboard for btn in row)
    assert any("សង្ខេបប្រចាំខែ" in btn.text for row in rep_kb_km.inline_keyboard for btn in row)
    assert any("កាតសមតុល្យសុទ្ធ" in btn.text for row in rep_kb_km.inline_keyboard for btn in row)

    net_kb_en = get_net_balance_keyboard(2026, 10, lang="en")
    assert any("Back to Report" in btn.text for row in net_kb_en.inline_keyboard for btn in row)

    net_kb_km = get_net_balance_keyboard(2026, 10, lang="km")
    assert any("ត្រឡប់ទៅរបាយការណ៍" in btn.text for row in net_kb_km.inline_keyboard for btn in row)
    print("✓ Bilingual English and Khmer report and Net Balance flashback keyboards verified.")

    print("\nTesting Bilingual (English & Khmer) Localization & Language Switching...")
    from locales import t, get_display_category, get_display_month
    from keyboards import get_language_keyboard

    # Test locale string lookups
    assert t("btn_add_expense", "en") == "➕ Add Expense"
    assert t("btn_add_expense", "km") == "➕ បន្ថែមការចំណាយ"
    assert t("btn_summary", "km") == "📊 សង្ខេបហិរញ្ញវត្ថុ"
    assert get_display_category("Food", "km") == "អាហារ"
    assert get_display_category("Salary", "km") == "ប្រាក់ខែ"
    assert get_display_month(10, "km") == "តុលា"
    assert get_display_month(10, "en") == "October"

    # Test database language persistence
    default_lang = await db.get_user_language(user_id)
    assert default_lang == "en", f"Default language should be 'en', got: {default_lang}"
    await db.set_user_language(user_id, "km")
    km_lang = await db.get_user_language(user_id)
    assert km_lang == "km", f"Language should be updated to 'km', got: {km_lang}"
    await db.set_user_language(user_id, "en")
    en_lang = await db.get_user_language(user_id)
    assert en_lang == "en", f"Language should be switched back to 'en', got: {en_lang}"

    # Test Khmer Keyboards
    main_kb_km = get_main_reply_keyboard(lang="km")
    assert any("បន្ថែមការចំណាយ" in btn.text for row in main_kb_km.keyboard for btn in row)
    assert any("Language / ភាសា" in btn.text for row in main_kb_km.keyboard for btn in row)

    lang_kb = get_language_keyboard()
    assert any("English" in btn.text for row in lang_kb.inline_keyboard for btn in row)
    assert any("ភាសាខ្មែរ" in btn.text for row in lang_kb.inline_keyboard for btn in row)

    cat_kb_km = get_category_keyboard(user_cats, "expense", lang="km")
    assert any("អាហារ" in btn.text for row in cat_kb_km.inline_keyboard for btn in row)

    cal_kb_km = get_calendar_keyboard(2026, 10, markers, lang="km")
    assert any("តុលា" in btn.text for row in cal_kb_km.inline_keyboard for btn in row)

    date_kb_km = get_date_selection_keyboard(2026, 10, lang="km")
    assert any("ថ្ងៃនេះ" in btn.text for row in date_kb_km.inline_keyboard for btn in row)
    print("✓ Bilingual English and Khmer localization, database persistence, and keyboards verified.")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())

