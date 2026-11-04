import { PeriodType, Language, Transaction } from './types';
import { CATEGORY_NAMES_KM, I18N } from './constants';

export function formatCurrency(amount: number, currency = 'USD'): string {
  const sym = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency + ' ';
  return `${sym}${Number(amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatLocalDateTime(date?: Date): string {
  const d = date || new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const year = d.getFullYear();
  const month = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export function triggerHaptic(type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'light') {
  try {
    const tg = (window as unknown as { Telegram?: { WebApp?: { HapticFeedback?: { impactOccurred: (t: string) => void } } } }).Telegram?.WebApp;
    tg?.HapticFeedback?.impactOccurred(type);
  } catch {
    // Non-telegram fallback
  }
}

export function getDisplayCategory(name: string, lang: Language): string {
  if (lang === 'km' && CATEGORY_NAMES_KM[name]) {
    return CATEGORY_NAMES_KM[name];
  }
  return name;
}

export function getPeriodDisplayText(
  period: PeriodType,
  startStr: string | null,
  endStr: string | null,
  lang: Language
): string {
  const t = I18N[lang] || I18N.en;
  if (period === 'week') return `${t.period_badge_week} ▼`;
  if (period === 'month') return `${t.period_badge_month} ▼`;
  if (period === 'year') return `${t.period_badge_year} ▼`;
  if (period === 'all') return `${t.period_badge_all} ▼`;
  if (period === 'custom') {
    if (startStr && endStr) {
      return `🔍 ${startStr} ~ ${endStr} ▼`;
    }
    return `${t.period_badge_custom} ▼`;
  }
  return `${t.period_badge_month} ▼`;
}

export function filterTransactionsByPeriod(
  transactions: Transaction[],
  period: PeriodType,
  startDateStr: string | null,
  endDateStr: string | null
): Transaction[] {
  if (!transactions || transactions.length === 0) return [];
  if (period === 'all') return transactions;

  const now = new Date();

  if (period === 'week') {
    const startOfWeek = new Date(now);
    const day = now.getDay();
    const diffToMonday = (day === 0 ? -6 : 1) - day;
    startOfWeek.setDate(now.getDate() + diffToMonday);
    startOfWeek.setHours(0, 0, 0, 0);

    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);
    endOfWeek.setHours(23, 59, 59, 999);

    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d.getTime()) && d >= startOfWeek && d <= endOfWeek;
    });
  }

  if (period === 'month') {
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0, 0);
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d.getTime()) && d >= startOfMonth && d <= endOfMonth;
    });
  }

  if (period === 'year') {
    const startOfYear = new Date(now.getFullYear(), 0, 1, 0, 0, 0, 0);
    const endOfYear = new Date(now.getFullYear(), 11, 31, 23, 59, 59, 999);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d.getTime()) && d >= startOfYear && d <= endOfYear;
    });
  }

  if (period === 'custom') {
    if (!startDateStr && !endDateStr) return transactions;
    const start = startDateStr ? new Date(`${startDateStr}T00:00:00`) : new Date(0);
    const end = endDateStr ? new Date(`${endDateStr}T23:59:59.999`) : new Date(8640000000000000);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d.getTime()) && d >= start && d <= end;
    });
  }

  return transactions;
}
