import React, { useState, useEffect } from 'react';
import { CustomCategories, Language, Transaction, TransactionType } from '../types';
import { CATEGORIES, I18N } from '../constants';
import { formatLocalDateTime, getDisplayCategory, triggerHaptic } from '../utils';
import { APP_CONFIG } from '../config';

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (tx: Omit<Transaction, 'id' | 'synced'>) => void;
  customCategories: CustomCategories;
  onOpenCategoryModal: (type: TransactionType) => void;
  lang: Language;
  currency: string;
  selectedNewCategory?: string | null;
}

export const TransactionModal: React.FC<TransactionModalProps> = ({
  isOpen,
  onClose,
  onSave,
  customCategories,
  onOpenCategoryModal,
  lang,
  currency,
  selectedNewCategory,
}) => {
  const t = I18N[lang] || I18N.en;

  const [type, setType] = useState<TransactionType>('expense');
  const [dateTime, setDateTime] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [note, setNote] = useState('');

  // Whenever modal opens, reset fields
  useEffect(() => {
    if (isOpen) {
      setDateTime(formatLocalDateTime(new Date()));
      setAmount('');
      setNote('');
      const standardCats = Object.keys(CATEGORIES[type]);
      setCategory(standardCats[0] || 'Food');
    }
  }, [isOpen, type]);

  // When a new custom category is created, automatically switch to it
  useEffect(() => {
    if (selectedNewCategory) {
      setCategory(selectedNewCategory);
    }
  }, [selectedNewCategory]);

  if (!isOpen) return null;

  const standardMap = CATEGORIES[type] || CATEGORIES.expense;
  const customList = customCategories[type] || [];

  const handleTypeChange = (newType: TransactionType) => {
    triggerHaptic('light');
    setType(newType);
    const standardCats = Object.keys(CATEGORIES[newType]);
    setCategory(standardCats[0] || '');
  };

  const handlePresetDate = (mode: 'now' | 'today' | 'yesterday') => {
    triggerHaptic('light');
    const now = new Date();
    if (mode === 'now') {
      setDateTime(formatLocalDateTime(now));
    } else if (mode === 'today') {
      now.setHours(12, 0, 0, 0);
      setDateTime(formatLocalDateTime(now));
    } else if (mode === 'yesterday') {
      now.setDate(now.getDate() - 1);
      now.setHours(12, 0, 0, 0);
      setDateTime(formatLocalDateTime(now));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    triggerHaptic('medium');

    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      return;
    }

    const txDate = dateTime ? new Date(dateTime).toISOString() : new Date().toISOString();

    onSave({
      type,
      category,
      amount: parsedAmount,
      currency,
      wallet: APP_CONFIG.defaultWallet,
      note: note.trim(),
      date: txDate,
    });
  };

  return (
    <div
      className={`modal-overlay ${isOpen ? 'active' : ''}`}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="modal-title">{t.new_record}</h3>
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

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Type Segmented Switch */}
          <div className="form-group">
            <label className="form-label">{t.type}</label>
            <div className="type-segmented">
              <button
                type="button"
                className={`segment-btn ${type === 'expense' ? 'active expense' : ''}`}
                onClick={() => handleTypeChange('expense')}
              >
                {t.expense}
              </button>
              <button
                type="button"
                className={`segment-btn ${type === 'income' ? 'active income' : ''}`}
                onClick={() => handleTypeChange('income')}
              >
                {t.income}
              </button>
            </div>
          </div>

          {/* Date & Time */}
          <div className="form-group">
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2px',
              }}
            >
              <label className="form-label">{t.datetime}</label>
              <div className="quick-date-chips">
                <button
                  type="button"
                  className="date-chip"
                  onClick={() => handlePresetDate('now')}
                >
                  {t.chip_now}
                </button>
                <button
                  type="button"
                  className="date-chip"
                  onClick={() => handlePresetDate('today')}
                >
                  {t.chip_today}
                </button>
                <button
                  type="button"
                  className="date-chip"
                  onClick={() => handlePresetDate('yesterday')}
                >
                  {t.chip_yesterday}
                </button>
              </div>
            </div>
            <input
              className="input-field"
              type="datetime-local"
              required
              value={dateTime}
              onChange={(e) => setDateTime(e.target.value)}
            />
          </div>

          {/* Amount */}
          <div className="form-group">
            <label className="form-label">{t.amount}</label>
            <input
              className="input-field"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              autoFocus
            />
          </div>

          {/* Category */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="form-label">{t.category}</label>
              <button
                type="button"
                className="btn-subtle"
                onClick={() => {
                  triggerHaptic('light');
                  onOpenCategoryModal(type);
                }}
              >
                + New
              </button>
            </div>
            <select
              className="select-field"
              required
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {Object.entries(standardMap).map(([name, emoji]) => (
                <option key={name} value={name}>
                  {`${emoji} ${getDisplayCategory(name, lang)}`}
                </option>
              ))}
              {customList.map((name) => (
                <option key={`custom_${name}`} value={name}>
                  🏷️ {name}
                </option>
              ))}
            </select>
          </div>

          {/* Note */}
          <div className="form-group">
            <label className="form-label">{t.note}</label>
            <input
              className="input-field"
              type="text"
              placeholder={t.note_placeholder}
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </div>

          {/* Submit */}
          <div style={{ marginTop: '8px' }}>
            <button className="btn-primary" type="submit" style={{ width: '100%' }}>
              {t.save_record}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
