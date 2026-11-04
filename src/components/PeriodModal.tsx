import React, { useState, useEffect } from 'react';
import { Language, PeriodType } from '../types';
import { I18N } from '../constants';
import { triggerHaptic } from '../utils';

interface PeriodModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPeriod: PeriodType;
  onSelectPeriod: (period: PeriodType) => void;
  onApplyCustomRange: (start: string, end: string) => void;
  initialStartDate: string | null;
  initialEndDate: string | null;
  lang: Language;
  onShowDateError: () => void;
}

export const PeriodModal: React.FC<PeriodModalProps> = ({
  isOpen,
  onClose,
  currentPeriod,
  onSelectPeriod,
  onApplyCustomRange,
  initialStartDate,
  initialEndDate,
  lang,
  onShowDateError,
}) => {
  const t = I18N[lang] || I18N.en;

  const [selectedPeriod, setSelectedPeriod] = useState<PeriodType>(currentPeriod);
  const [startDate, setStartDate] = useState(initialStartDate || '');
  const [endDate, setEndDate] = useState(initialEndDate || '');

  useEffect(() => {
    if (isOpen) {
      setSelectedPeriod(currentPeriod);
      if (!startDate) {
        const now = new Date();
        const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
        const pad = (n: number) => String(n).padStart(2, '0');
        setStartDate(
          `${firstDay.getFullYear()}-${pad(firstDay.getMonth() + 1)}-${pad(firstDay.getDate())}`
        );
      }
      if (!endDate) {
        const now = new Date();
        const pad = (n: number) => String(n).padStart(2, '0');
        setEndDate(`${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`);
      }
    }
  }, [isOpen, currentPeriod]);

  if (!isOpen) return null;

  const handlePeriodClick = (p: PeriodType) => {
    triggerHaptic('medium');
    setSelectedPeriod(p);
    if (p !== 'custom') {
      onSelectPeriod(p);
      onClose();
    }
  };

  const handleApplyRange = () => {
    triggerHaptic('medium');
    if (startDate && endDate && startDate > endDate) {
      onShowDateError();
      return;
    }
    onApplyCustomRange(startDate, endDate);
    onClose();
  };

  return (
    <div
      className={`modal-overlay ${isOpen ? 'active' : ''}`}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-content" style={{ maxWidth: '440px' }}>
        <div className="modal-header">
          <h3 className="modal-title">{t.period_modal_title}</h3>
          <button
            type="button"
            className="modal-close-btn"
            onClick={() => {
              triggerHaptic('light');
              onClose();
            }}
          >
            ✕
          </button>
        </div>

        {/* Quick Period Options Grid */}
        <div className="period-options-grid">
          <button
            type="button"
            className={`period-btn ${selectedPeriod === 'week' ? 'active' : ''}`}
            onClick={() => handlePeriodClick('week')}
          >
            <span className="period-icon">🗓️</span>
            <span className="period-name">{t.opt_week}</span>
          </button>
          <button
            type="button"
            className={`period-btn ${selectedPeriod === 'month' ? 'active' : ''}`}
            onClick={() => handlePeriodClick('month')}
          >
            <span className="period-icon">📅</span>
            <span className="period-name">{t.opt_month}</span>
          </button>
          <button
            type="button"
            className={`period-btn ${selectedPeriod === 'year' ? 'active' : ''}`}
            onClick={() => handlePeriodClick('year')}
          >
            <span className="period-icon">📆</span>
            <span className="period-name">{t.opt_year}</span>
          </button>
          <button
            type="button"
            className={`period-btn ${selectedPeriod === 'all' ? 'active' : ''}`}
            onClick={() => handlePeriodClick('all')}
          >
            <span className="period-icon">♾️</span>
            <span className="period-name">{t.opt_all}</span>
          </button>
          <button
            type="button"
            className={`period-btn ${selectedPeriod === 'custom' ? 'active' : ''}`}
            style={{ gridColumn: 'span 2' }}
            onClick={() => handlePeriodClick('custom')}
          >
            <span className="period-icon">🔍</span>
            <span className="period-name">{t.opt_custom}</span>
          </button>
        </div>

        {/* Custom Date Range Section */}
        {selectedPeriod === 'custom' && (
          <div className="custom-range-box">
            <div className="range-inputs-row">
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">{t.lbl_range_start}</label>
                <input
                  className="input-field"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">{t.lbl_range_end}</label>
                <input
                  className="input-field"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
            <button
              className="btn-primary"
              type="button"
              style={{ width: '100%', marginTop: '10px' }}
              onClick={handleApplyRange}
            >
              {t.btn_apply_range}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
