export type TransactionType = 'expense' | 'income';
export type PeriodType = 'week' | 'month' | 'year' | 'all' | 'custom';
export type FilterType = 'all' | 'expense' | 'income';
export type ChartViewMode = 'donut' | 'pie';
export type Language = 'en' | 'km';

export interface Transaction {
  id: string;
  type: TransactionType;
  category: string;
  amount: number;
  currency: string;
  wallet: string;
  note?: string;
  date: string; // ISO string
  synced: boolean;
}

export interface CustomCategories {
  expense: string[];
  income: string[];
}
