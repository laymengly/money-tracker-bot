import React, { useState } from 'react';
import { Language, TransactionType } from '../types';
import { I18N } from '../constants';
import { triggerHaptic } from '../utils';

interface CategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (type: TransactionType, name: string) => void;
  type: TransactionType;
  lang: Language;
}

export const CategoryModal: React.FC<CategoryModalProps> = ({
  isOpen,
  onClose,
  onSave,
  type,
  lang,
}) => {
  const t = I18N[lang] || I18N.en;
  const [catName, setCatName] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    triggerHaptic('medium');
    const trimmed = catName.trim();
    if (!trimmed) return;
    onSave(type, trimmed);
    setCatName('');
  };

  return (
    <div
      className={`modal-overlay ${isOpen ? 'active' : ''}`}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="modal-content" style={{ maxWidth: '420px' }}>
        <div className="modal-header">
          <h3 className="modal-title">{t.new_cat_title}</h3>
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
          <div className="form-group">
            <label className="form-label">{t.cat_name}</label>
            <input
              className="input-field"
              type="text"
              placeholder={t.cat_placeholder}
              required
              maxLength={30}
              value={catName}
              onChange={(e) => setCatName(e.target.value)}
              autoFocus
            />
          </div>
          <div style={{ marginTop: '10px' }}>
            <button className="btn-primary" type="submit" style={{ width: '100%' }}>
              {t.create_cat}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
