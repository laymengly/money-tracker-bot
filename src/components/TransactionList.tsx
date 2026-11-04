import React, { useState, useRef } from 'react';
import { FilterType, Language, Transaction } from '../types';
import { CATEGORIES, I18N } from '../constants';
import { formatCurrency, getDisplayCategory, triggerHaptic } from '../utils';

interface SwipeableItemProps {
  tx: Transaction;
  lang: Language;
  currency: string;
  onDelete: (id: string) => void;
}

const SwipeableTransactionItem: React.FC<SwipeableItemProps> = ({
  tx,
  lang,
  currency,
  onDelete,
}) => {
  const t = I18N[lang] || I18N.en;

  const [offsetX, setOffsetX] = useState(0);
  const [isSwiping, setIsSwiping] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const startXRef = useRef(0);
  const startYRef = useRef(0);
  const isHorizontalScrollRef = useRef<boolean | null>(null);

  const handleDelete = () => {
    triggerHaptic('medium');
    onDelete(tx.id);
  };

  // Touch handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    startXRef.current = e.touches[0].clientX;
    startYRef.current = e.touches[0].clientY;
    isHorizontalScrollRef.current = null;
    setIsSwiping(true);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentX = e.touches[0].clientX;
    const currentY = e.touches[0].clientY;
    const deltaX = currentX - startXRef.current;
    const deltaY = currentY - startYRef.current;

    // Detect gesture direction on first significant movement
    if (isHorizontalScrollRef.current === null) {
      if (Math.abs(deltaX) > 8 || Math.abs(deltaY) > 8) {
        isHorizontalScrollRef.current = Math.abs(deltaX) > Math.abs(deltaY);
      }
    }

    // If vertical scrolling, don't intercept horizontal drag
    if (isHorizontalScrollRef.current === false) {
      return;
    }

    // Calculate left slide
    const baseOffset = isOpen ? -80 : 0;
    const targetOffset = baseOffset + deltaX;

    // Constrain offset between -100px (max left) and 0px (closed)
    const clampedOffset = Math.max(-100, Math.min(0, targetOffset));
    setOffsetX(clampedOffset);
  };

  const handleTouchEnd = () => {
    setIsSwiping(false);
    isHorizontalScrollRef.current = null;

    // If swiped left past threshold of 40px
    if (offsetX < -40) {
      setOffsetX(-80);
      setIsOpen(true);
      triggerHaptic('light');
    } else {
      setOffsetX(0);
      setIsOpen(false);
    }
  };

  // Mouse handlers for desktop browser support
  const handleMouseDown = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const baseOffset = isOpen ? -80 : 0;
    setIsSwiping(true);

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const targetOffset = baseOffset + deltaX;
      const clampedOffset = Math.max(-100, Math.min(0, targetOffset));
      setOffsetX(clampedOffset);
    };

    const onMouseUp = () => {
      setIsSwiping(false);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);

      setOffsetX((prev) => {
        if (prev < -40) {
          setIsOpen(true);
          triggerHaptic('light');
          return -80;
        }
        setIsOpen(false);
        return 0;
      });
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

  const handleCardClick = () => {
    if (isOpen) {
      setOffsetX(0);
      setIsOpen(false);
    }
  };

  const emoji =
    (CATEGORIES[tx.type] && CATEGORIES[tx.type][tx.category]) ||
    (tx.type === 'income' ? '💵' : '📦');
  const dispCategory = getDisplayCategory(tx.category, lang);
  const d = new Date(tx.date);
  const dateStr = isNaN(d.getTime())
    ? 'Recent'
    : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  const prefix = tx.type === 'income' ? '+' : '-';

  return (
    <div className="tx-swipe-wrapper">
      {/* Background Red Delete Action */}
      <div
        className="tx-delete-action"
        role="button"
        tabIndex={0}
        aria-label="Delete transaction"
        onClick={handleDelete}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleDelete();
          }
        }}
      >
        <span className="tx-delete-icon">🗑️</span>
        <span className="tx-delete-text">{t.btn_delete}</span>
      </div>

      {/* Foreground Transaction Card */}
      <div
        className={`tx-item ${isSwiping ? 'swiping' : ''}`}
        style={{ transform: `translateX(${offsetX}px)` }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        onClick={handleCardClick}
      >
        <div className="tx-left">
          <div className={`tx-icon ${tx.type}`}>{emoji}</div>
          <div className="tx-details">
            <div className="tx-category">{dispCategory}</div>
            <div className="tx-meta">
              <span>{dateStr}</span>
              {tx.note && <span>• {tx.note}</span>}
            </div>
          </div>
        </div>

        <div className="tx-right">
          <span className={`tx-amount ${tx.type}`}>
            {prefix}
            {formatCurrency(tx.amount, tx.currency || currency)}
            <span
              className={`sync-dot ${tx.synced ? 'synced' : 'local'}`}
              title={tx.synced ? t.synced_tag : t.local_tag}
            />
          </span>
        </div>
      </div>
    </div>
  );
};

interface TransactionListProps {
  transactions: Transaction[];
  currentFilter: FilterType;
  lang: Language;
  currency: string;
  onDelete: (id: string) => void;
}

export const TransactionList: React.FC<TransactionListProps> = ({
  transactions,
  currentFilter,
  lang,
  currency,
  onDelete,
}) => {
  const t = I18N[lang] || I18N.en;
  const [searchQuery, setSearchQuery] = useState('');

  // 1. Filter transactions by type (all/expense/income)
  const typeFiltered = transactions.filter((tx) => {
    if (currentFilter === 'all') return true;
    return tx.type === currentFilter;
  });

  // 2. Filter transactions by search query (description/note or category)
  const normalizedQuery = searchQuery.trim().toLowerCase();
  const searchFiltered = typeFiltered.filter((tx) => {
    if (!normalizedQuery) return true;
    const noteMatch = tx.note ? tx.note.toLowerCase().includes(normalizedQuery) : false;
    const catMatch = tx.category.toLowerCase().includes(normalizedQuery);
    const localizedCatMatch = getDisplayCategory(tx.category, lang)
      .toLowerCase()
      .includes(normalizedQuery);
    return noteMatch || catMatch || localizedCatMatch;
  });

  // 3. Sort descending by date
  const sorted = [...searchFiltered].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  return (
    <>
      <section className="section-header">
        <h2 className="section-title">{t.recent_activity}</h2>
        <span className="tx-count">
          {sorted.length} {sorted.length === 1 ? t.item : t.items}
        </span>
      </section>

      {/* Search Bar */}
      <div className="tx-search-box">
        <span className="tx-search-icon">🔍</span>
        <input
          type="text"
          className="tx-search-input"
          placeholder={t.search_placeholder}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchQuery && (
          <button
            type="button"
            className="tx-search-clear"
            aria-label="Clear search"
            onClick={() => {
              triggerHaptic('light');
              setSearchQuery('');
            }}
          >
            ✕
          </button>
        )}
      </div>

      <div className="transaction-list">
        {sorted.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">{searchQuery ? '🔍' : '📊'}</div>
            <div className="empty-title">
              {searchQuery ? t.no_search_results : t.no_records}
            </div>
            <div>
              {searchQuery ? `"${searchQuery}"` : t.no_records_hint}
            </div>
            {searchQuery && (
              <button
                type="button"
                className="btn-clear-search"
                onClick={() => {
                  triggerHaptic('light');
                  setSearchQuery('');
                }}
              >
                {lang === 'km' ? 'សម្អាតការស្វែងរក' : 'Clear search'}
              </button>
            )}
          </div>
        ) : (
          sorted.map((tx) => (
            <SwipeableTransactionItem
              key={tx.id}
              tx={tx}
              lang={lang}
              currency={currency}
              onDelete={onDelete}
            />
          ))
        )}
      </div>
    </>
  );
};
