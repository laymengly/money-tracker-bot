import React, { useRef, useState } from 'react';
import { ChartViewMode, Language, PeriodType, Transaction } from '../types';
import { I18N } from '../constants';
import { formatCurrency, getPeriodDisplayText, triggerHaptic } from '../utils';
import { CategoryLegendGrid, PieChart } from './PieChart';

interface DashboardCardProps {
  transactions: Transaction[];
  chartViewMode: ChartViewMode;
  onToggleChartViewMode: () => void;
  currentPeriod: PeriodType;
  customStartDate: string | null;
  customEndDate: string | null;
  onOpenPeriodModal: () => void;
  lang: Language;
  currency: string;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({
  transactions,
  chartViewMode,
  onToggleChartViewMode,
  currentPeriod,
  customStartDate,
  customEndDate,
  onOpenPeriodModal,
  lang,
  currency,
}) => {
  const t = I18N[lang] || I18N.en;
  const cardRef = useRef<HTMLElement>(null);

  // Default: compact card showing only the header summary row (matches user screenshot)
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  // Compute metrics
  let totalIncome = 0;
  let totalExpense = 0;

  transactions.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'income') {
      totalIncome += amt;
    } else {
      totalExpense += amt;
    }
  });

  const netBalance = totalIncome - totalExpense;
  const totalFlow = totalIncome + totalExpense;
  const incomeRatio = totalFlow > 0 ? (totalIncome / totalFlow) * 100 : 50;
  const expenseRatio = totalFlow > 0 ? (totalExpense / totalFlow) * 100 : 50;
  const savingsPct = totalIncome > 0 ? Math.max(0, (netBalance / totalIncome) * 100) : 0;

  const handleToggleExpand = () => {
    triggerHaptic('medium');
    setIsExpanded((prev) => !prev);
  };

  const handlePeriodBadgeClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    triggerHaptic('light');
    if (cardRef.current) {
      cardRef.current.classList.remove('flash-pulse');
      void cardRef.current.offsetWidth;
      cardRef.current.classList.add('flash-pulse');
    }
    onOpenPeriodModal();
  };

  const periodDisplayText = getPeriodDisplayText(
    currentPeriod,
    customStartDate,
    customEndDate,
    lang
  );

  return (
    <section
      ref={cardRef}
      className={`balance-card unified-dashboard-card ${isExpanded ? 'expanded' : 'compact'}`}
      id="mainDashboardCard"
    >
      {/* Default Summary Row (Matches user screenshot: left and right symmetrically aligned) */}
      <div
        className="compact-card-row"
        role="button"
        tabIndex={0}
        onClick={handleToggleExpand}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggleExpand();
          }
        }}
        title={isExpanded ? 'Click to collapse report' : 'Click to toggle full report'}
      >
        <div className="compact-card-left">
          <div className="compact-card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <rect x="2" y="2" width="20" height="20" rx="5" fill="#E2E8F0" />
              <rect x="5" y="10" width="3" height="8" rx="1.5" fill="#4ADE80" />
              <rect x="10.5" y="6" width="3" height="12" rx="1.5" fill="#F43F5E" />
              <rect x="16" y="8" width="3" height="10" rx="1.5" fill="#38BDF8" />
            </svg>
          </div>
          <div className="compact-card-text">
            <h2 className="compact-card-title">{t.report_title}</h2>
            <span className="compact-card-sub">{t.report_sub}</span>
          </div>
        </div>

        <div className="compact-card-right">
          <span className="compact-card-amount">
            {formatCurrency(netBalance, currency)}
          </span>
          <span className={`status-pill ${netBalance >= 0 ? 'surplus' : 'deficit'}`}>
            <span className="status-pill-dot" />
            <span>{netBalance >= 0 ? t.surplus : t.deficit}</span>
          </span>
        </div>
      </div>

      {/* Subtle indicator divider at the bottom of the compact card */}
      <div className="compact-card-divider" />

      {/* Expanded Full Screen / Full Breakdown View */}
      {isExpanded && (
        <div className="expanded-report-content">
          {/* Controls Bar: Period selector (Left) & Controls (Right) */}
          <div className="expanded-controls-bar">
            <div
              className="period-badge-clickable"
              role="button"
              tabIndex={0}
              onClick={handlePeriodBadgeClick}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handlePeriodBadgeClick(e as unknown as React.MouseEvent);
                }
              }}
              title="Tap to change report period"
            >
              <span>{periodDisplayText}</span>
              <span style={{ fontSize: '10px' }}>▼</span>
            </div>

            <div className="expanded-actions-group">
              <button
                type="button"
                className="btn-chart-toggle"
                title="Toggle Donut or Pie view"
                onClick={(e) => {
                  e.stopPropagation();
                  triggerHaptic('light');
                  onToggleChartViewMode();
                }}
              >
                {chartViewMode === 'donut' ? t.toggle_pie : t.toggle_donut}
              </button>
              <button
                type="button"
                className="btn-collapse-toggle"
                title="Collapse to default summary"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleExpand();
                }}
              >
                ▲
              </button>
            </div>
          </div>

          {/* Symmetrical Split Layout: Left Chart (165px) and Right Flow/Stats (165px) */}
          <div className="dashboard-split-layout">
            <div className="dashboard-left-chart">
              <PieChart
                transactions={transactions}
                chartViewMode={chartViewMode}
                lang={lang}
                currency={currency}
                netBalance={netBalance}
                showLegend={false}
              />
            </div>

            <div className="dashboard-right-balance">
              {/* Income & Expense Flow Rows */}
              <div className="flow-vertical-stack">
                <div className="flow-mini-row">
                  <span className="flow-title">{t.total_income}</span>
                  <span className="flow-value income">
                    +{formatCurrency(totalIncome, currency)}
                  </span>
                </div>
                <div className="flow-mini-row">
                  <span className="flow-title">{t.total_expense}</span>
                  <span className="flow-value expense">
                    -{formatCurrency(totalExpense, currency)}
                  </span>
                </div>
              </div>

              {/* Dual Ratio Bar & Savings Rate */}
              <div className="cashflow-ratio-bar">
                <div className="ratio-fill income" style={{ width: `${incomeRatio}%` }} />
                <div className="ratio-fill expense" style={{ width: `${expenseRatio}%` }} />
              </div>

              <div className="savings-meter-row">
                <span className="savings-lbl">🏦 {t.savings_rate_lbl}</span>
                <span className="savings-val">{savingsPct.toFixed(1)}%</span>
              </div>
            </div>
          </div>

          {/* Category Legend Grid across full width below the split layout */}
          <div className="expanded-legend-container">
            <CategoryLegendGrid transactions={transactions} lang={lang} />
          </div>
        </div>
      )}
    </section>
  );
};
