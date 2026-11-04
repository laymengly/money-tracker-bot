import React, { useState } from 'react';
import { AVAILABLE_CURRENCIES, AVAILABLE_WALLETS } from '../constants';
import { Language } from '../types';
import { triggerHaptic } from '../utils';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  onSelectLang: (lang: Language) => void;
  currency: string;
  onSelectCurrency: (currency: string) => void;
  defaultWallet: string;
  onSelectWallet: (wallet: string) => void;
  firebaseProjectId: string;
  firestoreDatabaseId: string;
  userId: string | null;
  isOnline: boolean;
  onForceSync: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  lang,
  onSelectLang,
  currency,
  onSelectCurrency,
  defaultWallet,
  onSelectWallet,
  firebaseProjectId,
  firestoreDatabaseId,
  userId,
  isOnline,
  onForceSync,
}) => {
  const [copied, setCopied] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleCopy = (text: string, label: string) => {
    triggerHaptic('light');
    navigator.clipboard?.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-card"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="settingsModalTitle"
      >
        <div className="modal-header">
          <h2 id="settingsModalTitle" className="modal-title">
            ⚙️ {lang === 'km' ? 'ការកំណត់ & កំណត់រចនាសម្ព័ន្ធ' : 'Configuration & Settings'}
          </h2>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close settings"
          >
            ✕
          </button>
        </div>

        <div className="modal-body settings-modal-body">
          {/* Currency Configuration */}
          <div className="settings-section">
            <label className="settings-label">
              💱 {lang === 'km' ? 'រូបិយប័ណ្ណលំនាំដើម (Currency)' : 'Default Currency'}
            </label>
            <div className="settings-chips-grid">
              {AVAILABLE_CURRENCIES.map((c) => (
                <button
                  key={c.code}
                  type="button"
                  className={`settings-chip ${currency === c.code ? 'active' : ''}`}
                  onClick={() => {
                    triggerHaptic('light');
                    onSelectCurrency(c.code);
                  }}
                >
                  <span className="currency-symbol">{c.symbol}</span>
                  <span className="currency-code">{c.code}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Default Wallet Configuration */}
          <div className="settings-section">
            <label className="settings-label">
              💳 {lang === 'km' ? 'កាបូបលំនាំដើម (Default Wallet)' : 'Default Wallet'}
            </label>
            <div className="settings-chips-grid">
              {AVAILABLE_WALLETS.map((w) => (
                <button
                  key={w.id}
                  type="button"
                  className={`settings-chip ${defaultWallet === w.id ? 'active' : ''}`}
                  onClick={() => {
                    triggerHaptic('light');
                    onSelectWallet(w.id);
                  }}
                >
                  <span>{w.icon}</span>
                  <span>{w.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Language Configuration */}
          <div className="settings-section">
            <label className="settings-label">
              🌐 {lang === 'km' ? 'ភាសា (Language)' : 'Language'}
            </label>
            <div className="settings-chips-grid">
              <button
                type="button"
                className={`settings-chip ${lang === 'en' ? 'active' : ''}`}
                onClick={() => {
                  triggerHaptic('light');
                  onSelectLang('en');
                }}
              >
                <span>🇺🇸</span>
                <span>English</span>
              </button>
              <button
                type="button"
                className={`settings-chip ${lang === 'km' ? 'active' : ''}`}
                onClick={() => {
                  triggerHaptic('light');
                  onSelectLang('km');
                }}
              >
                <span>🇰🇭</span>
                <span>ភាសាខ្មែរ (Khmer)</span>
              </button>
            </div>
          </div>

          {/* Firebase Configuration Info & Cloud Sync */}
          <div className="settings-section firebase-info-card">
            <div className="firebase-info-header">
              <div className="firebase-info-title">
                <span>🔥</span>
                <span>{lang === 'km' ? 'ការកំណត់រចនាសម្ព័ន្ធ Firebase' : 'Firebase Configuration'}</span>
              </div>
              <span className={`network-pill mini ${isOnline ? 'online' : 'offline'}`}>
                <span className="dot" />
                <span>{isOnline ? 'Connected' : 'Offline'}</span>
              </span>
            </div>

            <div className="config-var-row">
              <div className="config-var-label">Project ID</div>
              <div
                className="config-var-value"
                title="Click to copy"
                onClick={() => handleCopy(firebaseProjectId, 'project')}
              >
                <code>{firebaseProjectId}</code>
                <span className="copy-icon">{copied === 'project' ? '✓' : '📋'}</span>
              </div>
            </div>

            <div className="config-var-row">
              <div className="config-var-label">Firestore Database</div>
              <div
                className="config-var-value"
                title="Click to copy"
                onClick={() => handleCopy(firestoreDatabaseId, 'db')}
              >
                <code className="truncate-var">{firestoreDatabaseId}</code>
                <span className="copy-icon">{copied === 'db' ? '✓' : '📋'}</span>
              </div>
            </div>

            <div className="config-var-row">
              <div className="config-var-label">Cloud Sync State</div>
              <div className="config-var-value">
                <span style={{ color: userId ? '#34D399' : '#F59E0B' }}>
                  {userId ? '✓ Synchronized' : '⚡ Local Auth Initializing...'}
                </span>
              </div>
            </div>

            <button
              type="button"
              className="btn-sync-now"
              onClick={() => {
                triggerHaptic('medium');
                onForceSync();
              }}
            >
              🔄 {lang === 'km' ? 'ធ្វើសមកាលកម្មឥឡូវនេះ (Sync Now)' : 'Sync Now to Firestore'}
            </button>
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-modal-submit" onClick={onClose}>
            ✓ {lang === 'km' ? 'យល់ព្រម' : 'Done'}
          </button>
        </div>
      </div>
    </div>
  );
};
