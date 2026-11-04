import { useState, useEffect } from 'react';
import {
  ChartViewMode,
  CustomCategories,
  FilterType,
  Language,
  PeriodType,
  Transaction,
  TransactionType,
} from './types';
import { I18N } from './constants';
import { filterTransactionsByPeriod, triggerHaptic } from './utils';
import {
  initAuthListener,
  syncTransactionToFirestore,
  deleteTransactionFromFirestore,
  subscribeToUserTransactions,
  syncCustomCategoriesToFirestore,
  subscribeToUserCategories,
  syncUnsyncedBatch,
  testFirestoreConnection,
} from './firebase';
import { DashboardCard } from './components/DashboardCard';
import { TransactionList } from './components/TransactionList';
import { TransactionModal } from './components/TransactionModal';
import { CategoryModal } from './components/CategoryModal';
import { PeriodModal } from './components/PeriodModal';
import { SettingsModal } from './components/SettingsModal';
import config from '../firebase-applet-config.json';

export function App() {
  // Localization
  const [lang, setLang] = useState<Language>(() => {
    const saved = localStorage.getItem('app_lang');
    return saved === 'km' ? 'km' : 'en';
  });

  // User & Configuration state
  const [userName, setUserName] = useState('Financial Assistant');
  const [userAvatar, setUserAvatar] = useState('👤');
  const [userCurrency, setUserCurrency] = useState<string>(() => {
    return (
      localStorage.getItem('app_currency') ||
      (import.meta.env.VITE_DEFAULT_CURRENCY as string) ||
      'USD'
    );
  });
  const [defaultWallet, setDefaultWallet] = useState<string>(() => {
    return (
      localStorage.getItem('app_default_wallet') ||
      (import.meta.env.VITE_DEFAULT_WALLET as string) ||
      'Bank'
    );
  });
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

  // Configuration variables
  const firebaseProjectId =
    (import.meta.env.VITE_FIREBASE_PROJECT_ID as string) || config.projectId;
  const firestoreDatabaseId =
    (import.meta.env.VITE_FIREBASE_DATABASE_ID as string) || config.firestoreDatabaseId;

  // Network state
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);

  // Transactions state (empty default for new users)
  const [transactions, setTransactions] = useState<Transaction[]>(() => {
    try {
      const saved = localStorage.getItem('money_tracker_txs');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          // If localStorage contains old seed mock data, clean it up for a fresh user experience
          const userOnly = parsed.filter(
            (t: Transaction) => t && t.id && !t.id.startsWith('tx_seed_')
          );
          if (userOnly.length !== parsed.length) {
            localStorage.setItem('money_tracker_txs', JSON.stringify(userOnly));
          }
          return userOnly;
        }
      }
    } catch {
      // Fallback
    }
    return [];
  });

  // Custom categories state
  const [customCategories, setCustomCategories] = useState<CustomCategories>(() => {
    try {
      const saved = localStorage.getItem('money_tracker_categories');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch {
      // Fallback
    }
    return { expense: [], income: [] };
  });

  // Filter & Chart modes
  const [currentFilter, setCurrentFilter] = useState<FilterType>('all');
  const [chartViewMode, setChartViewMode] = useState<ChartViewMode>('donut');
  const [currentPeriod, setCurrentPeriod] = useState<PeriodType>('month');
  const [customStartDate, setCustomStartDate] = useState<string | null>(null);
  const [customEndDate, setCustomEndDate] = useState<string | null>(null);

  // Modals state
  const [isTxModalOpen, setIsTxModalOpen] = useState(false);
  const [isCatModalOpen, setIsCatModalOpen] = useState(false);
  const [catModalType, setCatModalType] = useState<TransactionType>('expense');
  const [selectedNewCategory, setSelectedNewCategory] = useState<string | null>(null);
  const [isPeriodModalOpen, setIsPeriodModalOpen] = useState(false);

  // Toast state
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const t = I18N[lang] || I18N.en;

  const showToast = (msg: string) => {
    setToastMessage(msg);
  };

  useEffect(() => {
    if (!toastMessage) return;
    const timer = setTimeout(() => {
      setToastMessage(null);
    }, 2800);
    return () => clearTimeout(timer);
  }, [toastMessage]);

  // Persist transactions
  useEffect(() => {
    localStorage.setItem('money_tracker_txs', JSON.stringify(transactions));
  }, [transactions]);

  // Persist custom categories
  useEffect(() => {
    localStorage.setItem('money_tracker_categories', JSON.stringify(customCategories));
  }, [customCategories]);

  // Synchronize document language for Khmer font rendering
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  // Firebase Auth user
  const [userId, setUserId] = useState<string | null>(null);

  // Initialize Firebase Auth & test connection
  useEffect(() => {
    testFirestoreConnection().catch((err) => {
      console.warn('Firestore connection check notice:', err);
    });
    const unsubscribeAuth = initAuthListener((user) => {
      setUserId(user.uid);
    });
    return () => {
      unsubscribeAuth();
    };
  }, []);

  // Sync with Firestore when userId is available
  useEffect(() => {
    if (!userId) return;

    // 1. Bulk push any existing unsynced transactions to Firestore
    const unsynced = transactions.filter((tx) => !tx.synced);
    if (unsynced.length > 0 && isOnline) {
      syncUnsyncedBatch(userId, unsynced)
        .then(() => {
          setTransactions((prev) =>
            prev.map((tx) => ({ ...tx, synced: true }))
          );
        })
        .catch((err) => console.error('Error syncing unsynced records to Firestore:', err));
    }

    // 2. Real-time listener for Firestore transactions
    const unsubscribeTxs = subscribeToUserTransactions(
      userId,
      (serverTxs) => {
        if (serverTxs.length > 0) {
          setTransactions((prevLocal) => {
            const localUnsynced = prevLocal.filter((tx) => !tx.synced);
            const serverIds = new Set(serverTxs.map((t) => t.id));
            const pendingLocal = localUnsynced.filter((t) => !serverIds.has(t.id));
            return [...pendingLocal, ...serverTxs];
          });
        } else if (transactions.length > 0) {
          // If Firestore is empty but client has local items, upload them
          syncUnsyncedBatch(userId, transactions).catch((err) =>
            console.error('Initial data upload error:', err)
          );
        }
      },
      (err) => console.warn('Firestore subscription error:', err)
    );

    // 3. Real-time listener for custom categories
    const unsubscribeCats = subscribeToUserCategories(userId, (serverCats) => {
      if (serverCats && (serverCats.expense?.length || serverCats.income?.length)) {
        setCustomCategories(serverCats);
      }
    });

    return () => {
      unsubscribeTxs();
      unsubscribeCats();
    };
  }, [userId, isOnline]);

  // Network listener & Telegram integration
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      if (userId) {
        const unsynced = transactions.filter((t) => !t.synced);
        if (unsynced.length > 0) {
          syncUnsyncedBatch(userId, unsynced)
            .then(() => {
              setTransactions((prev) =>
                prev.map((item) => ({ ...item, synced: true }))
              );
              showToast('✓ Synchronized with Firestore');
            })
            .catch((err) => console.error('Reconnection sync error:', err));
          return;
        }
      }
      showToast('✓ Synchronized with cloud');
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Initialize Telegram WebApp
    try {
      const tg = (window as unknown as {
        Telegram?: {
          WebApp?: {
            ready: () => void;
            expand: () => void;
            initDataUnsafe?: { user?: { first_name?: string; language_code?: string } };
          };
        };
      }).Telegram?.WebApp;

      if (tg) {
        tg.ready();
        tg.expand();

        if (tg.initDataUnsafe?.user) {
          const user = tg.initDataUnsafe.user;
          if (user.first_name) {
            setUserName(user.first_name);
            setUserAvatar(user.first_name.charAt(0).toUpperCase());
          }
          if (!localStorage.getItem('app_lang') && user.language_code === 'km') {
            setLang('km');
          }
        }
      }
    } catch {
      // Ignored
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [userId, transactions]);

  // Language toggle
  const handleToggleLang = () => {
    triggerHaptic('light');
    const newLang = lang === 'en' ? 'km' : 'en';
    setLang(newLang);
    localStorage.setItem('app_lang', newLang);
  };

  // Add new transaction
  const handleSaveTransaction = (newTxData: Omit<Transaction, 'id' | 'synced'>) => {
    const newTx: Transaction = {
      ...newTxData,
      id: `tx_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      synced: false,
    };

    setTransactions((prev) => [newTx, ...prev]);
    setIsTxModalOpen(false);

    if (userId && isOnline) {
      syncTransactionToFirestore(userId, newTx)
        .then(() => {
          setTransactions((prev) =>
            prev.map((t) => (t.id === newTx.id ? { ...t, synced: true } : t))
          );
          showToast(t.toast_record_saved);
        })
        .catch((err) => {
          console.error('Failed to sync transaction to Firestore:', err);
          showToast(t.toast_offline_saved);
        });
    } else {
      showToast(t.toast_offline_saved);
    }
  };

  // Add custom category
  const handleSaveCategory = (type: TransactionType, name: string) => {
    if (!customCategories[type].includes(name)) {
      const updatedCats = {
        ...customCategories,
        [type]: [...customCategories[type], name],
      };
      setCustomCategories(updatedCats);
      if (userId && isOnline) {
        syncCustomCategoriesToFirestore(userId, updatedCats);
      }
    }
    setSelectedNewCategory(name);
    setIsCatModalOpen(false);
    showToast(t.toast_added);
  };

  // Delete transaction (e.g. from left slide gesture)
  const handleDeleteTransaction = (id: string) => {
    triggerHaptic('medium');
    setTransactions((prev) => prev.filter((tx) => tx.id !== id));
    if (userId && isOnline) {
      deleteTransactionFromFirestore(userId, id).catch((err) =>
        console.error('Failed to delete transaction from Firestore:', err)
      );
    }
    showToast(t.toast_deleted);
  };

  // Change currency configuration
  const handleSelectCurrency = (newCurr: string) => {
    setUserCurrency(newCurr);
    localStorage.setItem('app_currency', newCurr);
    showToast(`Currency changed to ${newCurr}`);
  };

  // Change default wallet configuration
  const handleSelectWallet = (newWallet: string) => {
    setDefaultWallet(newWallet);
    localStorage.setItem('app_default_wallet', newWallet);
    showToast(`Default wallet set to ${newWallet}`);
  };

  // Force full sync to Firestore
  const handleForceSync = () => {
    if (!userId) {
      showToast('⚡ Connecting to Firebase...');
      return;
    }
    syncUnsyncedBatch(userId, transactions)
      .then(() => {
        setTransactions((prev) => prev.map((tx) => ({ ...tx, synced: true })));
        showToast('✓ All records synchronized to Firestore');
      })
      .catch((err) => {
        console.error('Force sync error:', err);
        showToast('⚠️ Sync error. Please check connection.');
      });
  };

  // Filter transactions by selected period
  const periodTransactions = filterTransactionsByPeriod(
    transactions,
    currentPeriod,
    customStartDate,
    customEndDate
  );

  const unsyncedCount = transactions.filter((tx) => !tx.synced).length;

  return (
    <>
      {/* Offline / Sync Banner */}
      {(!isOnline || unsyncedCount > 0) && (
        <div className="status-banner">
          <span>⚡</span>
          <span>
            {unsyncedCount > 0
              ? `${unsyncedCount} ${t.items} queued. ${t.offline_banner}`
              : t.offline_banner}
          </span>
        </div>
      )}

      <div className="app-container" lang={lang}>
        {/* Header */}
        <header className="app-header">
          <div className="user-profile">
            <div className="user-avatar">{userAvatar}</div>
            <div className="user-meta">
              <h1>{userName}</h1>
              <div className="user-tier">
                <span className="tier-badge">{t.free_tier}</span>
                <span>• {userCurrency}</span>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <button
              className="btn-settings-icon"
              type="button"
              aria-label="Configuration & Settings"
              title="Configuration & Settings"
              onClick={() => {
                triggerHaptic('light');
                setIsSettingsModalOpen(true);
              }}
            >
              ⚙️
            </button>
            <button
              className="lang-switch-btn"
              type="button"
              aria-label="Switch Language"
              onClick={handleToggleLang}
            >
              {t.lang_btn}
            </button>
            <div className={`network-pill ${isOnline ? 'online' : 'offline'}`}>
              <span className="dot" />
              <span>{isOnline ? t.online : t.offline}</span>
            </div>
          </div>
        </header>

        {/* Unified Balance Hero & Statistics Graph Card (Side-by-Side) */}
        <DashboardCard
          transactions={periodTransactions}
          chartViewMode={chartViewMode}
          onToggleChartViewMode={() =>
            setChartViewMode((prev) => (prev === 'donut' ? 'pie' : 'donut'))
          }
          currentPeriod={currentPeriod}
          customStartDate={customStartDate}
          customEndDate={customEndDate}
          onOpenPeriodModal={() => setIsPeriodModalOpen(true)}
          lang={lang}
          currency={userCurrency}
        />

        {/* Action Bar */}
        <section className="action-bar">
          <button
            className="btn-primary"
            type="button"
            onClick={() => {
              triggerHaptic('light');
              setSelectedNewCategory(null);
              setIsTxModalOpen(true);
            }}
          >
            <span>➕</span>
            <span>{t.log_transaction}</span>
          </button>
        </section>

        {/* Filter Tabs */}
        <section className="filter-tabs">
          <button
            className={`tab-btn ${currentFilter === 'all' ? 'active' : ''}`}
            type="button"
            onClick={() => {
              triggerHaptic('light');
              setCurrentFilter('all');
            }}
          >
            {t.tab_all}
          </button>
          <button
            className={`tab-btn ${currentFilter === 'expense' ? 'active' : ''}`}
            type="button"
            onClick={() => {
              triggerHaptic('light');
              setCurrentFilter('expense');
            }}
          >
            {t.tab_expense}
          </button>
          <button
            className={`tab-btn ${currentFilter === 'income' ? 'active' : ''}`}
            type="button"
            onClick={() => {
              triggerHaptic('light');
              setCurrentFilter('income');
            }}
          >
            {t.tab_income}
          </button>
        </section>

        {/* Transactions List */}
        <TransactionList
          transactions={periodTransactions}
          currentFilter={currentFilter}
          lang={lang}
          currency={userCurrency}
          onDelete={handleDeleteTransaction}
        />
      </div>

      {/* Transaction Modal Drawer */}
      <TransactionModal
        isOpen={isTxModalOpen}
        onClose={() => setIsTxModalOpen(false)}
        onSave={handleSaveTransaction}
        customCategories={customCategories}
        onOpenCategoryModal={(type) => {
          setCatModalType(type);
          setIsCatModalOpen(true);
        }}
        lang={lang}
        currency={userCurrency}
        selectedNewCategory={selectedNewCategory}
      />

      {/* Category Creation Modal */}
      <CategoryModal
        isOpen={isCatModalOpen}
        onClose={() => setIsCatModalOpen(false)}
        onSave={handleSaveCategory}
        type={catModalType}
        lang={lang}
      />

      {/* Period Selection Modal */}
      <PeriodModal
        isOpen={isPeriodModalOpen}
        onClose={() => setIsPeriodModalOpen(false)}
        currentPeriod={currentPeriod}
        onSelectPeriod={(p) => setCurrentPeriod(p)}
        onApplyCustomRange={(start, end) => {
          setCurrentPeriod('custom');
          setCustomStartDate(start || null);
          setCustomEndDate(end || null);
        }}
        initialStartDate={customStartDate}
        initialEndDate={customEndDate}
        lang={lang}
        onShowDateError={() => showToast(t.toast_date_err)}
      />

      {/* Settings & Configuration Modal */}
      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
        lang={lang}
        onSelectLang={(newLang) => {
          setLang(newLang);
          localStorage.setItem('app_lang', newLang);
        }}
        currency={userCurrency}
        onSelectCurrency={handleSelectCurrency}
        defaultWallet={defaultWallet}
        onSelectWallet={handleSelectWallet}
        firebaseProjectId={firebaseProjectId}
        firestoreDatabaseId={firestoreDatabaseId}
        userId={userId}
        isOnline={isOnline}
        onForceSync={handleForceSync}
      />

      {/* Toast Notification Container */}
      <div className={`toast-container ${toastMessage ? 'show' : ''}`}>{toastMessage}</div>
    </>
  );
}

export default App;
