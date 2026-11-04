import config from '../firebase-applet-config.json';
import { Language } from './types';

/**
 * Money Tracker & Financial Assistant - Application Configuration
 * Configure app settings directly in code here.
 */
export const APP_CONFIG = {
  // Default currency code (e.g., 'USD', 'KHR', 'EUR', 'GBP', 'THB', 'JPY')
  defaultCurrency: (import.meta.env.VITE_DEFAULT_CURRENCY as string) || 'USD',

  // Default wallet for transactions (e.g., 'Bank', 'Cash', 'Card')
  defaultWallet: (import.meta.env.VITE_DEFAULT_WALLET as string) || 'Bank',

  // Default language ('en' | 'km')
  defaultLanguage: ((import.meta.env.VITE_DEFAULT_LANGUAGE as string) as Language) || 'en',

  // Firebase project and database IDs (loaded from firebase-applet-config.json or env)
  firebase: {
    projectId: (import.meta.env.VITE_FIREBASE_PROJECT_ID as string) || config.projectId,
    firestoreDatabaseId:
      (import.meta.env.VITE_FIREBASE_DATABASE_ID as string) || config.firestoreDatabaseId,
  },
};

