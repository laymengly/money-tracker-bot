import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  signInAnonymously,
  onAuthStateChanged,
  User,
} from 'firebase/auth';
import {
  getFirestore,
  collection,
  doc,
  setDoc,
  deleteDoc,
  onSnapshot,
  getDocFromServer,
  writeBatch,
  Firestore,
} from 'firebase/firestore';
import config from '../firebase-applet-config.json';
import { CustomCategories, Transaction } from './types';

// Initialize Firebase configuration with support for environment variable overrides
const firebaseConfig = {
  projectId: (import.meta.env.VITE_FIREBASE_PROJECT_ID as string) || config.projectId,
  appId: (import.meta.env.VITE_FIREBASE_APP_ID as string) || config.appId,
  apiKey: (import.meta.env.VITE_FIREBASE_API_KEY as string) || config.apiKey,
  authDomain: (import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string) || config.authDomain,
  firestoreDatabaseId:
    (import.meta.env.VITE_FIREBASE_DATABASE_ID as string) || config.firestoreDatabaseId,
  storageBucket: (import.meta.env.VITE_FIREBASE_STORAGE_BUCKET as string) || config.storageBucket,
  messagingSenderId:
    (import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string) || config.messagingSenderId,
};

// Initialize Firebase App
export const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);

// Initialize Auth
export const auth = getAuth(app);

// Initialize Firestore (support custom databaseId if configured)
export const db: Firestore =
  firebaseConfig.firestoreDatabaseId && firebaseConfig.firestoreDatabaseId !== '(default)'
    ? getFirestore(app, firebaseConfig.firestoreDatabaseId)
    : getFirestore(app);

// Connection test helper
export async function testFirestoreConnection(): Promise<boolean> {
  try {
    await getDocFromServer(doc(db, 'test', 'connection'));
    return true;
  } catch (error) {
    if (error instanceof Error && error.message.includes('the client is offline')) {
      console.warn('Firestore client is offline.');
      return false;
    }
    return true;
  }
}

// Auto sign in anonymously or listen to auth state
export function initAuthListener(onUserReady: (user: User) => void): () => void {
  const unsubscribe = onAuthStateChanged(auth, (user) => {
    if (user) {
      onUserReady(user);
    } else {
      signInAnonymously(auth).catch((err) => {
        console.error('Anonymous sign in error:', err);
      });
    }
  });
  return unsubscribe;
}

// Sync transaction to Firestore
export async function syncTransactionToFirestore(
  userId: string,
  tx: Transaction
): Promise<void> {
  try {
    const txRef = doc(db, 'users', userId, 'transactions', tx.id);
    const payload = {
      id: tx.id,
      userId,
      type: tx.type,
      category: tx.category,
      amount: tx.amount,
      currency: tx.currency,
      wallet: tx.wallet || 'Bank',
      note: tx.note || '',
      date: tx.date,
      createdAt: new Date().toISOString(),
    };
    await setDoc(txRef, payload, { merge: true });
  } catch (err) {
    console.error('Failed to sync transaction to Firestore:', err);
    throw err;
  }
}

// Delete transaction from Firestore
export async function deleteTransactionFromFirestore(
  userId: string,
  txId: string
): Promise<void> {
  try {
    const txRef = doc(db, 'users', userId, 'transactions', txId);
    await deleteDoc(txRef);
  } catch (err) {
    console.error('Failed to delete transaction from Firestore:', err);
    throw err;
  }
}

// Subscribe to real-time transactions from Firestore
export function subscribeToUserTransactions(
  userId: string,
  onUpdate: (transactions: Transaction[]) => void,
  onError?: (error: Error) => void
): () => void {
  const txColRef = collection(db, 'users', userId, 'transactions');
  return onSnapshot(
    txColRef,
    (snapshot) => {
      const serverTxs: Transaction[] = [];
      snapshot.forEach((docSnap) => {
        const data = docSnap.data();
        serverTxs.push({
          id: data.id || docSnap.id,
          type: data.type || 'expense',
          category: data.category || 'General',
          amount: Number(data.amount) || 0,
          currency: data.currency || 'USD',
          wallet: data.wallet || 'Bank',
          note: data.note || '',
          date: data.date || new Date().toISOString(),
          synced: true,
        });
      });
      onUpdate(serverTxs);
    },
    (err) => {
      console.error('Error listening to transactions:', err);
      onError?.(err);
    }
  );
}

// Sync custom categories to Firestore
export async function syncCustomCategoriesToFirestore(
  userId: string,
  categories: CustomCategories
): Promise<void> {
  try {
    const prefRef = doc(db, 'users', userId, 'settings', 'preferences');
    await setDoc(
      prefRef,
      {
        userId,
        customCategories: categories,
        updatedAt: new Date().toISOString(),
      },
      { merge: true }
    );
  } catch (err) {
    console.error('Failed to sync custom categories to Firestore:', err);
  }
}

// Subscribe to custom categories
export function subscribeToUserCategories(
  userId: string,
  onUpdate: (categories: CustomCategories) => void
): () => void {
  const prefRef = doc(db, 'users', userId, 'settings', 'preferences');
  return onSnapshot(
    prefRef,
    (docSnap) => {
      if (docSnap.exists()) {
        const data = docSnap.data();
        if (data.customCategories) {
          onUpdate(data.customCategories as CustomCategories);
        }
      }
    },
    (err) => {
      console.warn('Error reading custom categories from Firestore:', err);
    }
  );
}

// Bulk sync unsynced local transactions to Firestore
export async function syncUnsyncedBatch(
  userId: string,
  unsyncedTxs: Transaction[]
): Promise<void> {
  if (unsyncedTxs.length === 0) return;
  const batch = writeBatch(db);
  unsyncedTxs.forEach((tx) => {
    const txRef = doc(db, 'users', userId, 'transactions', tx.id);
    batch.set(
      txRef,
      {
        id: tx.id,
        userId,
        type: tx.type,
        category: tx.category,
        amount: tx.amount,
        currency: tx.currency,
        wallet: tx.wallet || 'Bank',
        note: tx.note || '',
        date: tx.date,
        createdAt: new Date().toISOString(),
      },
      { merge: true }
    );
  });
  await batch.commit();
}
