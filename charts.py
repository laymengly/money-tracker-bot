"""
In-memory chart generation engine for Money Tracker.
Uses matplotlib to generate clean, modern donut charts saved directly to io.BytesIO buffers.
"""

import io
from typing import Dict, Optional
import matplotlib

# Set non-interactive backend before importing pyplot
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import CURRENCY_SYMBOLS, EXPENSE_CATEGORIES

# Modern, harmonious color palette
MODERN_PALETTE = [
    "#6366F1",  # Indigo
    "#EC4899",  # Pink
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#3B82F6",  # Blue
    "#8B5CF6",  # Purple
    "#14B8A6",  # Teal
    "#EF4444",  # Red
    "#84CC16",  # Lime
    "#F97316",  # Orange
    "#06B6D4",  # Cyan
]


def generate_expense_donut_chart(
    category_totals: Dict[str, float],
    month_name: str,
    year: int,
    currency: str = "USD",
    total_income: Optional[float] = None,
    net_balance: Optional[float] = None,
) -> Optional[io.BytesIO]:
    """
    Generate an in-memory Donut Chart of monthly expenses with Net Balance.
    Returns an io.BytesIO buffer positioned at start, or None if no expenses.
    """
    # Filter out categories with zero or negative amounts
    filtered = {cat: amt for cat, amt in category_totals.items() if amt > 0}
    if not filtered:
        return None

    # Sort descending by amount
    sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    total_amount = sum(values)

    curr_sym = CURRENCY_SYMBOLS.get(currency.upper(), currency.upper() + " ")

    # Set up Matplotlib figure with transparent background and high DPI
    fig, ax = plt.subplots(figsize=(7, 6), subplot_kw=dict(aspect="equal"), dpi=300)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Color mapping
    colors = [MODERN_PALETTE[i % len(MODERN_PALETTE)] for i in range(len(labels))]

    # Generate Donut Chart (wedgeprops width=0.4 creates the donut hole)
    wedges, texts, autotexts = ax.pie(
        values,
        labels=None,  # We will use an elegant legend instead of crowded slice labels
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 4.0 else "",
        pctdistance=0.80,
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.38, edgecolor="#1E293B", linewidth=1.5, antialiased=True),
    )

    # Format percentage texts inside slices
    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_fontsize(9)
        autotext.set_fontweight("bold")

    # Compute net balance if income is provided
    calc_net = net_balance
    if calc_net is None and total_income is not None:
        calc_net = total_income - total_amount

    # Center label inside donut hole: display Net Balance directly if available!
    if calc_net is not None:
        net_sign = "+" if calc_net >= 0 else "-"
        center_text = f"NET BALANCE\n{net_sign}{curr_sym}{abs(calc_net):,.2f}"
    else:
        center_text = f"TOTAL\n{curr_sym}{total_amount:,.2f}"

    ax.text(
        0,
        0,
        center_text,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#F8FAFC",
        linespacing=1.3,
    )

    # Format labels with clean category names and percentages
    legend_labels = []
    for cat, amt in zip(labels, values):
        pct = (amt / total_amount) * 100
        legend_labels.append(f"{cat}: {curr_sym}{amt:,.2f} ({pct:.1f}%)")

    # Clean, modern legend positioned below or to the side
    if calc_net is not None:
        net_sign = "+" if calc_net >= 0 else "-"
        leg_title = f"{month_name} {year}\nNet: {net_sign}{curr_sym}{abs(calc_net):,.2f} | Spent: {curr_sym}{total_amount:,.2f}"
    else:
        leg_title = f"Expenses Breakdown • {month_name} {year}"

    ax.legend(
        wedges,
        legend_labels,
        title=leg_title,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
        facecolor="#0F172A",
        edgecolor="#334155",
        labelcolor="#E2E8F0",
        fontsize=9,
        title_fontsize=10,
    )

    # Set title styling
    plt.setp(ax.get_legend().get_title(), color="#F1F5F9", weight="bold")

    # Save strictly to in-memory BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=300)
    plt.close(fig)
    buf.seek(0)

    return buf


def generate_report_pie_chart(
    category_totals: Dict[str, float],
    month_name: str,
    year: int,
    currency: str = "USD",
    total_income: Optional[float] = None,
    total_expense: Optional[float] = None,
) -> Optional[io.BytesIO]:
    """
    Generate an in-memory classic Pie Chart for monthly financial reports.
    Features exploded top spending category, percentage badges, drop-shadow styling,
    and a comprehensive breakdown card.
    Returns io.BytesIO buffer positioned at start, or None if no data.
    """
    filtered = {cat: amt for cat, amt in category_totals.items() if amt > 0}
    if not filtered:
        return None

    # Sort descending
    sorted_items = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in sorted_items]
    values = [v for _, v in sorted_items]
    total_amount = sum(values)

    curr_sym = CURRENCY_SYMBOLS.get(currency.upper(), currency.upper() + " ")

    # Highlight top expense slice with explode offset
    explode = [0.06 if i == 0 else 0.0 for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(8, 6.2), subplot_kw=dict(aspect="equal"), dpi=300)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    colors = [MODERN_PALETTE[i % len(MODERN_PALETTE)] for i in range(len(labels))]

    # Classic solid Pie Chart with shadow and crisp slice borders
    wedges, texts, autotexts = ax.pie(
        values,
        explode=explode,
        labels=None,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 5.0 else "",
        pctdistance=0.70,
        startangle=140,
        colors=colors,
        shadow=True,
        wedgeprops=dict(edgecolor="#0F172A", linewidth=1.5, antialiased=True),
    )

    for autotext in autotexts:
        autotext.set_color("#FFFFFF")
        autotext.set_fontsize(10)
        autotext.set_fontweight("bold")

    # Build detailed report legend
    legend_labels = []
    for cat, amt in zip(labels, values):
        pct = (amt / total_amount) * 100
        legend_labels.append(f"{cat}: {curr_sym}{amt:,.2f} ({pct:.1f}%)")

    header_title = f"Report • {month_name} {year}"
    if total_income is not None:
        net_flow = total_income - total_amount
        net_sign = "+" if net_flow >= 0 else "-"
        status_word = "Surplus" if net_flow >= 0 else "Deficit"
        header_title += f"\nNet Balance: {net_sign}{curr_sym}{abs(net_flow):,.2f} ({status_word})"
        header_title += f"\nIncome: +{curr_sym}{total_income:,.2f}"
    header_title += f"\nSpent: -{curr_sym}{total_amount:,.2f}"
    if total_income is not None and total_income > 0:
        savings = total_income - total_amount
        savings_rate = max(0.0, (savings / total_income) * 100)
        header_title += f" (Savings: {savings_rate:.1f}%)"

    legend = ax.legend(
        wedges,
        legend_labels,
        title=header_title,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=True,
        facecolor="#0F172A",
        edgecolor="#334155",
        labelcolor="#E2E8F0",
        fontsize=9,
        title_fontsize=10,
    )
    plt.setp(legend.get_title(), color="#38BDF8", weight="bold")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=300)
    plt.close(fig)
    buf.seek(0)

    return buf

