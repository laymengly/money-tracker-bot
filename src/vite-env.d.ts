/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FIREBASE_PROJECT_ID?: string;
  readonly VITE_WEBAPP_URL?: string;
  readonly VITE_TELEGRAM_BOT_TOKEN?: string;
  readonly VITE_TELEGRAM_BOT_USERNAME?: string;
  readonly VITE_DEFAULT_CURRENCY?: string;
  readonly VITE_DEFAULT_WALLET?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
