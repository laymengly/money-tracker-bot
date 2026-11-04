import React, { useState } from 'react';
import { ChartViewMode, Language, Transaction } from '../types';
import { CATEGORIES, CHART_COLORS, I18N } from '../constants';
import { formatCurrency, getDisplayCategory } from '../utils';

interface PieChartProps {
  transactions: Transaction[];
  chartViewMode: ChartViewMode;
  lang: Language;
  currency: string;
  netBalance: number;
  showLegend?: boolean;
}

export const PieChart: React.FC<PieChartProps> = ({
  transactions,
  chartViewMode,
  lang,
  currency,
  netBalance,
  showLegend = true,
}) => {
  const t = I18N[lang] || I18N.en;
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  // Aggregate expenses
  const expenses: Record<string, number> = {};
  let totalExpense = 0;

  transactions.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'expense' && amt > 0) {
      expenses[tx.category] = (expenses[tx.category] || 0) + amt;
      totalExpense += amt;
    }
  });

  const sortedCats = Object.entries(expenses).sort((a, b) => b[1] - a[1]);

  const netSign = netBalance >= 0 ? '+' : '-';
  const defaultCenterLabel = t.net_balance;
  const defaultCenterValue = `${netSign}${formatCurrency(Math.abs(netBalance), currency)}`;

  // Find active item if hovered/selected
  const activeItem = activeCategory ? sortedCats.find(([cat]) => cat === activeCategory) : null;
  const activeAmount = activeItem ? activeItem[1] : 0;
  const activeFraction = totalExpense > 0 && activeItem ? activeAmount / totalExpense : 0;
  const activePct = (activeFraction * 100).toFixed(1);

  const emoji = activeItem
    ? (CATEGORIES.expense && CATEGORIES.expense[activeItem[0]]) || '📦'
    : '';
  const dispName = activeItem ? getDisplayCategory(activeItem[0], lang) : '';

  const centerLabel = activeItem ? `${emoji} ${dispName}` : defaultCenterLabel;
  const centerValue = activeItem
    ? `${formatCurrency(activeAmount, currency)} (${activePct}%)`
    : defaultCenterValue;

  const cx = 110;
  const cy = 110;
  const rOuter = 85;
  const rInner = chartViewMode === 'donut' ? 52 : 0;

  let currentAngle = -90; // Start at top 12 o'clock

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', width: '100%', alignItems: 'center' }}>
      <div className="chart-wrapper">
        <svg
          className="pie-chart-svg"
          viewBox="0 0 220 220"
          width="165"
          height="165"
          onMouseLeave={() => setActiveCategory(null)}
        >
          {sortedCats.length === 0 || totalExpense === 0 ? (
            <circle
              cx="110"
              cy="110"
              r={chartViewMode === 'donut' ? '70' : '85'}
              fill="none"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth={chartViewMode === 'donut' ? '28' : '4'}
            />
          ) : sortedCats.length === 1 || sortedCats[0][1] / totalExpense >= 0.999 ? (
            chartViewMode === 'donut' ? (
              <circle
                cx={cx}
                cy={cy}
                r={(rOuter + rInner) / 2}
                fill="none"
                stroke={CHART_COLORS[0]}
                strokeWidth={rOuter - rInner}
                className={`pie-slice ${activeCategory === sortedCats[0][0] ? 'active' : ''}`}
                onMouseEnter={() => setActiveCategory(sortedCats[0][0])}
                onClick={() =>
                  setActiveCategory(activeCategory === sortedCats[0][0] ? null : sortedCats[0][0])
                }
              />
            ) : (
              <circle
                cx={cx}
                cy={cy}
                r={rOuter}
                fill={CHART_COLORS[0]}
                className={`pie-slice ${activeCategory === sortedCats[0][0] ? 'active' : ''}`}
                onMouseEnter={() => setActiveCategory(sortedCats[0][0])}
                onClick={() =>
                  setActiveCategory(activeCategory === sortedCats[0][0] ? null : sortedCats[0][0])
                }
              />
            )
          ) : (
            sortedCats.map(([cat, amt], idx) => {
              const sliceFraction = amt / totalExpense;
              const sliceAngle = sliceFraction * 360;
              const startAngle = currentAngle;
              const endAngle = currentAngle + sliceAngle;
              currentAngle = endAngle;

              const color = CHART_COLORS[idx % CHART_COLORS.length];
              const isActive = activeCategory === cat;

              const startRad = (startAngle * Math.PI) / 180;
              const endRad = (endAngle * Math.PI) / 180;

              const x1 = cx + rOuter * Math.cos(startRad);
              const y1 = cy + rOuter * Math.sin(startRad);
              const x2 = cx + rOuter * Math.cos(endRad);
              const y2 = cy + rOuter * Math.sin(endRad);

              const largeArcFlag = sliceAngle > 180 ? 1 : 0;

              let d = '';
              if (chartViewMode === 'donut') {
                const x3 = cx + rInner * Math.cos(endRad);
                const y3 = cy + rInner * Math.sin(endRad);
                const x4 = cx + rInner * Math.cos(startRad);
                const y4 = cy + rInner * Math.sin(startRad);

                d = `
                  M ${x1} ${y1}
                  A ${rOuter} ${rOuter} 0 ${largeArcFlag} 1 ${x2} ${y2}
                  L ${x3} ${y3}
                  A ${rInner} ${rInner} 0 ${largeArcFlag} 0 ${x4} ${y4}
                  Z
                `;
              } else {
                d = `
                  M ${cx} ${cy}
                  L ${x1} ${y1}
                  A ${rOuter} ${rOuter} 0 ${largeArcFlag} 1 ${x2} ${y2}
                  Z
                `;
              }

              return (
                <path
                  key={cat}
                  d={d}
                  fill={color}
                  className={`pie-slice ${isActive ? 'active' : ''}`}
                  onMouseEnter={() => setActiveCategory(cat)}
                  onClick={() => setActiveCategory(isActive ? null : cat)}
                />
              );
            })
          )}
        </svg>

        <div className="chart-center-info">
          <div className="center-label">{centerLabel}</div>
          <div className="center-value">{centerValue}</div>
        </div>
      </div>

      {/* Legend list (if showLegend is enabled) */}
      {showLegend && (
        <div className="chart-legend-grid">
          {sortedCats.length === 0 || totalExpense === 0 ? (
            <div
              className="report-sub"
              style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '8px 0' }}
            >
              {t.no_expense_chart}
            </div>
          ) : (
            sortedCats.map(([cat, amt], idx) => {
              const fraction = amt / totalExpense;
              const pctStr = (fraction * 100).toFixed(1);
              const color = CHART_COLORS[idx % CHART_COLORS.length];
              const catEmoji = (CATEGORIES.expense && CATEGORIES.expense[cat]) || '📦';
              const catDisp = getDisplayCategory(cat, lang);
              const isActive = activeCategory === cat;

              return (
                <div
                  key={cat}
                  className={`legend-item ${isActive ? 'active' : ''}`}
                  onMouseEnter={() => setActiveCategory(cat)}
                  onMouseLeave={() => setActiveCategory(null)}
                  onClick={() => setActiveCategory(isActive ? null : cat)}
                >
                  <div className="legend-left">
                    <span className="legend-dot" style={{ backgroundColor: color }} />
                    <span className="legend-name">{`${catEmoji} ${catDisp}`}</span>
                  </div>
                  <span className="legend-pct">{pctStr}%</span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};

export const CategoryLegendGrid: React.FC<{
  transactions: Transaction[];
  lang: Language;
}> = ({ transactions, lang }) => {
  const t = I18N[lang] || I18N.en;
  const expenses: Record<string, number> = {};
  let totalExpense = 0;

  transactions.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'expense' && amt > 0) {
      expenses[tx.category] = (expenses[tx.category] || 0) + amt;
      totalExpense += amt;
    }
  });

  const sortedCats = Object.entries(expenses).sort((a, b) => b[1] - a[1]);

  if (sortedCats.length === 0 || totalExpense === 0) {
    return (
      <div className="report-sub" style={{ textAlign: 'center', padding: '8px 0', width: '100%' }}>
        {t.no_expense_chart}
      </div>
    );
  }

  return (
    <div className="chart-legend-grid full-width-legend">
      {sortedCats.map(([cat, amt], idx) => {
        const fraction = amt / totalExpense;
        const pctStr = (fraction * 100).toFixed(1);
        const color = CHART_COLORS[idx % CHART_COLORS.length];
        const catEmoji = (CATEGORIES.expense && CATEGORIES.expense[cat]) || '📦';
        const catDisp = getDisplayCategory(cat, lang);

        return (
          <div key={cat} className="legend-item">
            <div className="legend-left">
              <span className="legend-dot" style={{ backgroundColor: color }} />
              <span className="legend-name">{`${catEmoji} ${catDisp}`}</span>
            </div>
            <span className="legend-pct">{pctStr}%</span>
          </div>
        );
      })}
    </div>
  );
};
