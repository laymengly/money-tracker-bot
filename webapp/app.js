/**
 * Telegram Mini App (TMA) - Money Tracker & Financial Assistant
 * Offline-first architecture with IndexedDB, Service Worker, and Background Sync.
 * Implements strict DOM safety (no innerHTML) and Telegram native theme & haptics.
 */

// Category Maps & Emojis
const CATEGORIES = {
  expense: {
    Food: '🍔',
    Transport: '🚗',
    Bills: '🧾',
    Shopping: '🛍️',
    Entertainment: '🎬',
    Health: '💊',
    Groceries: '🛒',
    Education: '📚',
    Other: '📦'
  },
  income: {
    Salary: '💼',
    Freelance: '💻',
    Investment: '📈',
    Bonus: '🎁',
    Refund: '🔄',
    Other: '💵'
  }
};

// Khmer translations for standard categories
const CATEGORY_NAMES_KM = {
  Food: 'អាហារ',
  Transport: 'ធ្វើដំណើរ',
  Bills: 'វិក្កយបត្រ',
  Shopping: 'ទិញទំនិញ',
  Entertainment: 'កម្សាន្ត',
  Health: 'សុខភាព',
  Groceries: 'គ្រឿងទេស',
  Education: 'ការសិក្សា',
  Other: 'ផ្សេងៗ',
  Salary: 'ប្រាក់ខែ',
  Freelance: 'ការងារក្រៅម៉ោង',
  Investment: 'ការវិនិយោគ',
  Bonus: 'ប្រាក់លើកទឹកចិត្ត',
  Refund: 'ប្រាក់ត្រឡប់មកវិញ'
};

// Bilingual Strings
const I18N = {
  en: {
    lang_btn: '🇰🇭 ខ្មែរ',
    online: 'Online',
    offline: 'Offline',
    offline_banner: 'Saved offline. Will sync when reconnected.',
    net_balance: 'Net Balance',
    total_income: '🟢 Total Income',
    total_expense: '🔴 Total Expenses',
    log_transaction: 'Log Transaction',
    tab_all: 'All',
    tab_expense: 'Expenses',
    tab_income: 'Income',
    recent_activity: 'Recent Activity',
    items: 'items',
    item: 'item',
    no_records: 'No records found',
    no_records_hint: 'Tap "Log Transaction" above to add your first expense or income.',
    new_record: 'New Record',
    type: 'Type',
    expense: 'Expense',
    income: 'Income',
    datetime: 'Date & Time',
    chip_now: '⚡ Now',
    chip_today: 'Today',
    chip_yesterday: 'Yesterday',
    amount: 'Amount',
    category: 'Category',
    wallet: 'Wallet',
    note: 'Note (Optional)',
    note_placeholder: 'e.g. Lunch with team',
    save_record: '💾 Save Record',
    new_cat_title: 'New Category',
    cat_name: 'Category Name',
    cat_placeholder: 'e.g. Gym, Coffee, Crypto',
    create_cat: '➕ Create Category',
    bank: '🏦 Bank',
    cash: '💵 Cash',
    card: '💳 Card',
    local_tag: '⚡ Local',
    synced_tag: '✓ Synced',
    toast_added: '✓ Category added!',
    toast_record_saved: '✓ Record saved & synced!',
    toast_offline_saved: '⚡ Saved offline. Will sync when reconnected.',
    toast_invalid_amt: '⚠️ Please enter a valid positive amount.',
    report_title: 'Expense Report',
    report_sub: 'Category Breakdown',
    toggle_donut: '🍩 Donut',
    toggle_pie: '🥧 Pie',
    total_spent: 'Total Spent',
    no_expense_chart: 'No expense records to visualize yet.',
    btn_flashback: '⚡ Net Balance',
    btn_back_to_chart: 'Back to Chart',
    flash_net_label: 'Net Balance',
    surplus: 'Surplus',
    deficit: 'Deficit',
    savings_rate_lbl: 'Savings Rate:',
    period_badge_week: '🗓️ This Week',
    period_badge_month: '📅 This Month',
    period_badge_year: '📆 This Year',
    period_badge_all: '♾️ All Time',
    period_badge_custom: '🔍 Custom',
    period_modal_title: 'Select Report Period',
    opt_week: 'This Week',
    opt_month: 'This Month',
    opt_year: 'This Year',
    opt_all: 'All Time',
    opt_custom: 'Custom Range',
    lbl_range_start: 'Start Date',
    lbl_range_end: 'End Date',
    btn_apply_range: '✓ Apply Range',
    tap_hint: '👆 Tap to switch: Week, Month, Year, Range'
  },
  km: {
    lang_btn: '🇺🇸 English',
    online: 'អនឡាញ',
    offline: 'គ្មានអ៊ីនធឺណិត',
    offline_banner: 'បានរក្សាទុកក្នុងឧបករណ៍។ នឹងធ្វើសមកាលកម្មពេលមានអ៊ីនធឺណិត។',
    net_balance: 'សមតុល្យសុទ្ធ',
    total_income: '🟢 ចំណូលសរុប',
    total_expense: '🔴 ចំណាយសរុប',
    log_transaction: 'កត់ត្រាប្រតិបត្តិការ',
    tab_all: 'ទាំងអស់',
    tab_expense: 'ចំណាយ',
    tab_income: 'ចំណូល',
    recent_activity: 'សកម្មភាពថ្មីៗ',
    items: 'កំណត់ត្រា',
    item: 'កំណត់ត្រា',
    no_records: 'មិនមានកំណត់ត្រាទេ',
    no_records_hint: 'ចុចលើ "កត់ត្រាប្រតិបត្តិការ" ខាងលើដើម្បីចាប់ផ្តើមកត់ត្រាដំបូង។',
    new_record: 'កំណត់ត្រាថ្មី',
    type: 'ប្រភេទប្រតិបត្តិការ',
    expense: 'ចំណាយ',
    income: 'ចំណូល',
    datetime: 'កាលបរិច្ឆេទ និងម៉ោង',
    chip_now: '⚡ ឥឡូវនេះ',
    chip_today: 'ថ្ងៃនេះ',
    chip_yesterday: 'ម្សិលមិញ',
    amount: 'ចំនួនទឹកប្រាក់',
    category: 'ប្រភេទ',
    wallet: 'កាបូប',
    note: 'ចំណាំ (ស្រេចចិត្ត)',
    note_placeholder: 'ឧ. ញ៉ាំបាយជាមួយក្រុមការងារ',
    save_record: '💾 រក្សាទុកកំណត់ត្រា',
    new_cat_title: 'ប្រភេទថ្មី',
    cat_name: 'ឈ្មោះប្រភេទ',
    cat_placeholder: 'ឧ. កាយវប្បកម្ម, កាហ្វេ, គ្រីបតូ',
    create_cat: '➕ បង្កើតប្រភេទថ្មី',
    bank: '🏦 ធនាគារ',
    cash: '💵 សាច់ប្រាក់',
    card: '💳 កាត',
    local_tag: '⚡ ក្នុងម៉ាស៊ីន',
    synced_tag: '✓ សមកាលកម្ម',
    toast_added: '✓ បានបន្ថែមប្រភេទថ្មី!',
    toast_record_saved: '✓ បានរក្សាទុក និង sync ដោយជោគជ័យ!',
    toast_offline_saved: '⚡ បានរក្សាទុកក្នុងឧបករណ៍។ នឹង sync ពេលមានអ៊ីនធឺណិត។',
    toast_invalid_amt: '⚠️ សូមបញ្ចូលចំនួនទឹកប្រាក់វិជ្ជមានត្រឹមត្រូវ។',
    report_title: 'របាយការណ៍ចំណាយ',
    report_sub: 'ការបែងចែកតាមប្រភេទ',
    toggle_donut: '🍩 Donut',
    toggle_pie: '🥧 គំនូសរង្វង់',
    total_spent: 'ចំណាយសរុប',
    no_expense_chart: 'មិនទាន់មានទិន្នន័យចំណាយសម្រាប់បង្ហាញគំនូសតារាងនៅឡើយទេ។',
    btn_flashback: '⚡ សមតុល្យសុទ្ធ',
    btn_back_to_chart: 'ត្រឡប់ទៅតារាង',
    flash_net_label: 'សមតុល្យសុទ្ធ',
    surplus: 'លើសសាច់ប្រាក់',
    deficit: 'ឱនភាព',
    savings_rate_lbl: 'អត្រាសន្សំប្រាក់៖',
    period_badge_week: '🗓️ ប្រចាំសប្តាហ៍',
    period_badge_month: '📅 ប្រចាំខែ',
    period_badge_year: '📆 ប្រចាំឆ្នាំ',
    period_badge_all: '♾️ ទាំងអស់',
    period_badge_custom: '🔍 ចន្លោះកាលបរិច្ឆេទ',
    period_modal_title: 'ជ្រើសរើសរយៈពេលរបាយការណ៍',
    opt_week: 'ប្រចាំសប្តាហ៍',
    opt_month: 'ប្រចាំខែ',
    opt_year: 'ប្រចាំឆ្នាំ',
    opt_all: 'ទាំងអស់',
    opt_custom: 'ចន្លោះកាលបរិច្ឆេទ',
    lbl_range_start: 'ចាប់ពីថ្ងៃ',
    lbl_range_end: 'ដល់ថ្ងៃ',
    btn_apply_range: '✓ អនុវត្តចន្លោះកាលបរិច្ឆេទ',
    tap_hint: '👆 ចុចដើម្បីប្តូរ៖ សប្តាហ៍ ខែ ឆ្នាំ ឬ Range'
  }
};

// State
let dbInstance = null;
let currentFilter = 'all'; // 'all' | 'expense' | 'income'
let selectedType = 'expense'; // 'expense' | 'income'
let chartViewMode = 'donut'; // 'donut' | 'pie'
let currentPeriod = 'month'; // 'week' | 'month' | 'year' | 'all' | 'custom'
let customStartDate = null;
let customEndDate = null;
let userId = 'demo_user';
let userCurrency = 'USD';
let userCustomCategories = { expense: [], income: [] };
let currentLang = localStorage.getItem('app_lang') || 'en';

const CHART_COLORS = [
  '#6366F1', '#EC4899', '#10B981', '#F59E0B', '#3B82F6',
  '#8B5CF6', '#14B8A6', '#EF4444', '#84CC16', '#F97316', '#06B6D4'
];

// DOM Elements
const offlineBanner = document.getElementById('offlineBanner');
const bannerText = document.getElementById('bannerText');
const networkPill = document.getElementById('networkPill');
const networkText = document.getElementById('networkText');
const langToggleBtn = document.getElementById('langToggleBtn');
const userNameEl = document.getElementById('userName');
const userAvatarEl = document.getElementById('userAvatar');
const userCurrencyTagEl = document.getElementById('userCurrencyTag');
const balanceLabelEl = document.getElementById('balanceLabel');
const totalBalanceEl = document.getElementById('totalBalance');
const periodBadge = document.getElementById('periodBadge');
const tapHintText = document.getElementById('tapHintText');
const balanceCardTrigger = document.getElementById('balanceCardTrigger');
const flowTitleIncomeEl = document.getElementById('flowTitleIncome');
const totalIncomeEl = document.getElementById('totalIncome');
const flowTitleExpenseEl = document.getElementById('flowTitleExpense');
const totalExpenseEl = document.getElementById('totalExpense');
const reportCardTitleEl = document.getElementById('reportCardTitle');
const reportSubTitleEl = document.getElementById('reportSubTitle');
const toggleChartTypeBtn = document.getElementById('toggleChartTypeBtn');
const pieChartSvg = document.getElementById('pieChartSvg');
const chartCenterLabel = document.getElementById('chartCenterLabel');
const chartCenterValue = document.getElementById('chartCenterValue');
const chartLegendList = document.getElementById('chartLegendList');
const reportCardEl = document.getElementById('reportCard');
const reportCardIcon = document.getElementById('reportCardIcon');
const flashbackNetBalanceBtn = document.getElementById('flashbackNetBalanceBtn');
const flashbackToChartBtn = document.getElementById('flashbackToChartBtn');
const reportChartView = document.getElementById('reportChartView');
const reportNetBalanceView = document.getElementById('reportNetBalanceView');
const flashNetLabel = document.getElementById('flashNetLabel');
const flashNetVal = document.getElementById('flashNetVal');
const flashNetBadge = document.getElementById('flashNetBadge');
const cashflowIncomeBar = document.getElementById('cashflowIncomeBar');
const cashflowExpenseBar = document.getElementById('cashflowExpenseBar');
const flashIncomeLabel = document.getElementById('flashIncomeLabel');
const flashIncomeVal = document.getElementById('flashIncomeVal');
const flashExpenseLabel = document.getElementById('flashExpenseLabel');
const flashExpenseVal = document.getElementById('flashExpenseVal');
const flashSavingsLabel = document.getElementById('flashSavingsLabel');
const flashSavingsVal = document.getElementById('flashSavingsVal');
const flashbackToChartText = document.getElementById('flashbackToChartText');
const logTxBtnTextEl = document.getElementById('logTxBtnText');
const tabAllEl = document.getElementById('tabAll');
const tabExpenseEl = document.getElementById('tabExpense');
const tabIncomeEl = document.getElementById('tabIncome');
const recentActivityTitleEl = document.getElementById('recentActivityTitle');
const txCountEl = document.getElementById('txCount');
const transactionListEl = document.getElementById('transactionList');
const openModalBtn = document.getElementById('openModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const txModal = document.getElementById('txModal');
const modalTitleEl = document.getElementById('modalTitle');
const txForm = document.getElementById('txForm');
const typeLabelEl = document.getElementById('typeLabel');
const typeExpenseBtn = document.getElementById('typeExpenseBtn');
const typeIncomeBtn = document.getElementById('typeIncomeBtn');
const dateTimeLabelEl = document.getElementById('dateTimeLabel');
const txDateTimeInput = document.getElementById('txDateTime');
const chipNow = document.getElementById('chipNow');
const chipToday = document.getElementById('chipToday');
const chipYesterday = document.getElementById('chipYesterday');
const amountLabelEl = document.getElementById('amountLabel');
const txAmountInput = document.getElementById('txAmount');
const categoryLabelEl = document.getElementById('categoryLabel');
const txCategorySelect = document.getElementById('txCategory');
const noteLabelEl = document.getElementById('noteLabel');
const txNoteInput = document.getElementById('txNote');
const saveTxBtnEl = document.getElementById('saveTxBtn');
const addCatBtn = document.getElementById('addCatBtn');
const catModal = document.getElementById('catModal');
const catModalTitleEl = document.getElementById('catModalTitle');
const closeCatModalBtn = document.getElementById('closeCatModalBtn');
const catForm = document.getElementById('catForm');
const catNameLabelEl = document.getElementById('catNameLabel');
const newCatNameInput = document.getElementById('newCatName');
const saveCatBtnEl = document.getElementById('saveCatBtn');
const toastEl = document.getElementById('toast');

// Period Modal Selectors
const periodModal = document.getElementById('periodModal');
const periodModalTitle = document.getElementById('periodModalTitle');
const closePeriodModalBtn = document.getElementById('closePeriodModalBtn');
const customRangeSection = document.getElementById('customRangeSection');
const rangeStartDate = document.getElementById('rangeStartDate');
const rangeEndDate = document.getElementById('rangeEndDate');
const applyRangeBtn = document.getElementById('applyRangeBtn');
const optWeekText = document.getElementById('optWeekText');
const optMonthText = document.getElementById('optMonthText');
const optYearText = document.getElementById('optYearText');
const optAllText = document.getElementById('optAllText');
const optCustomText = document.getElementById('optCustomText');
const lblRangeStart = document.getElementById('lblRangeStart');
const lblRangeEnd = document.getElementById('lblRangeEnd');

// -------------------------------------------------------------
// TELEGRAM WEBAPP INITIALIZATION
// -------------------------------------------------------------
function initTelegram() {
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();

    // Check user data from initDataUnsafe
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
      const tgUser = tg.initDataUnsafe.user;
      userId = String(tgUser.id);
      userNameEl.textContent = tgUser.first_name || 'My Finances';
      if (tgUser.first_name) {
        userAvatarEl.textContent = tgUser.first_name.charAt(0).toUpperCase();
      }
      if (!localStorage.getItem('app_lang') && tgUser.language_code === 'km') {
        currentLang = 'km';
      }
    }
  }
}

function triggerHaptic(type = 'light') {
  try {
    window.Telegram?.WebApp?.HapticFeedback?.impactOccurred(type);
  } catch (e) {
    // Graceful fallback for non-Telegram environments
  }
}

// -------------------------------------------------------------
// INDEXEDDB DATABASE LAYER (MoneyTrackerDB)
// -------------------------------------------------------------
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('MoneyTrackerDB', 1);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('transactions')) {
        const txStore = db.createObjectStore('transactions', { keyPath: 'id' });
        txStore.createIndex('date', 'date', { unique: false });
        txStore.createIndex('synced', 'synced', { unique: false });
      }
      if (!db.objectStoreNames.contains('sync_queue')) {
        db.createObjectStore('sync_queue', { keyPath: 'id' });
      }
    };

    request.onsuccess = (event) => {
      dbInstance = event.target.result;
      resolve(dbInstance);
    };

    request.onerror = (event) => {
      reject(event.target.error);
    };
  });
}

function idbGetAll(storeName) {
  return new Promise((resolve, reject) => {
    const tx = dbInstance.transaction(storeName, 'readonly');
    const store = tx.objectStore(storeName);
    const request = store.getAll();
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

function idbPut(storeName, item) {
  return new Promise((resolve, reject) => {
    const tx = dbInstance.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    const request = store.put(item);
    request.onsuccess = () => resolve(item);
    request.onerror = () => reject(request.error);
  });
}

function idbDelete(storeName, id) {
  return new Promise((resolve, reject) => {
    const tx = dbInstance.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    const request = store.delete(id);
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// -------------------------------------------------------------
// UI RENDERING (SAFE DOM MANIPULATION - NO INNERHTML)
// -------------------------------------------------------------
function formatCurrency(amount, currency = 'USD') {
  const sym = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency + ' ';
  return `${sym}${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.add('show');
  setTimeout(() => {
    toastEl.classList.remove('show');
  }, 2800);
}

function getDisplayCategory(name) {
  if (currentLang === 'km' && CATEGORY_NAMES_KM[name]) {
    return CATEGORY_NAMES_KM[name];
  }
  return name;
}

function getPeriodDisplayText(period, startStr, endStr) {
  const t = I18N[currentLang] || I18N.en;
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

function filterTransactionsByPeriod(transactions, period, startDateStr, endDateStr) {
  if (!transactions || transactions.length === 0) return [];
  if (period === 'all') return transactions;

  const now = new Date();

  if (period === 'week') {
    // Current week starting from Monday 00:00:00
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
      return !isNaN(d) && d >= startOfWeek && d <= endOfWeek;
    });
  }

  if (period === 'month') {
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0, 0);
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d) && d >= startOfMonth && d <= endOfMonth;
    });
  }

  if (period === 'year') {
    const startOfYear = new Date(now.getFullYear(), 0, 1, 0, 0, 0, 0);
    const endOfYear = new Date(now.getFullYear(), 11, 31, 23, 59, 59, 999);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d) && d >= startOfYear && d <= endOfYear;
    });
  }

  if (period === 'custom') {
    if (!startDateStr && !endDateStr) return transactions;
    const start = startDateStr ? new Date(`${startDateStr}T00:00:00`) : new Date(0);
    const end = endDateStr ? new Date(`${endDateStr}T23:59:59.999`) : new Date(8640000000000000);
    return transactions.filter((tx) => {
      const d = new Date(tx.date);
      return !isNaN(d) && d >= start && d <= end;
    });
  }

  return transactions;
}

function applyLanguage(lang) {
  currentLang = lang;
  const t = I18N[lang] || I18N.en;

  if (langToggleBtn) langToggleBtn.textContent = t.lang_btn;
  if (balanceLabelEl) balanceLabelEl.textContent = t.net_balance;
  if (flowTitleIncomeEl) flowTitleIncomeEl.textContent = t.total_income;
  if (flowTitleExpenseEl) flowTitleExpenseEl.textContent = t.total_expense;
  if (logTxBtnTextEl) logTxBtnTextEl.textContent = t.log_transaction;
  if (tabAllEl) tabAllEl.textContent = t.tab_all;
  if (tabExpenseEl) tabExpenseEl.textContent = t.tab_expense;
  if (tabIncomeEl) tabIncomeEl.textContent = t.tab_income;
  if (recentActivityTitleEl) recentActivityTitleEl.textContent = t.recent_activity;
  if (modalTitleEl) modalTitleEl.textContent = t.new_record;
  if (typeLabelEl) typeLabelEl.textContent = t.type;
  if (typeExpenseBtn) typeExpenseBtn.textContent = t.expense;
  if (typeIncomeBtn) typeIncomeBtn.textContent = t.income;
  if (dateTimeLabelEl) dateTimeLabelEl.textContent = t.datetime;
  if (chipNow) chipNow.textContent = t.chip_now;
  if (chipToday) chipToday.textContent = t.chip_today;
  if (chipYesterday) chipYesterday.textContent = t.chip_yesterday;
  if (amountLabelEl) amountLabelEl.textContent = t.amount;
  if (categoryLabelEl) categoryLabelEl.textContent = t.category;
  if (noteLabelEl) noteLabelEl.textContent = t.note;
  if (txNoteInput) txNoteInput.placeholder = t.note_placeholder;
  if (saveTxBtnEl) saveTxBtnEl.textContent = t.save_record;
  if (catModalTitleEl) catModalTitleEl.textContent = t.new_cat_title;
  if (catNameLabelEl) catNameLabelEl.textContent = t.cat_name;
  if (newCatNameInput) newCatNameInput.placeholder = t.cat_placeholder;
  if (saveCatBtnEl) saveCatBtnEl.textContent = t.create_cat;

  if (reportCardTitleEl) reportCardTitleEl.textContent = t.report_title;
  if (reportSubTitleEl) reportSubTitleEl.textContent = t.report_sub;
  if (toggleChartTypeBtn) {
    toggleChartTypeBtn.textContent = chartViewMode === 'donut' ? t.toggle_pie : t.toggle_donut;
  }
  if (flashbackNetBalanceBtn) flashbackNetBalanceBtn.textContent = t.btn_flashback;
  if (flashbackToChartText) flashbackToChartText.textContent = t.btn_back_to_chart;
  if (flashNetLabel) flashNetLabel.textContent = t.flash_net_label;
  if (flashIncomeLabel) flashIncomeLabel.textContent = t.total_income;
  if (flashExpenseLabel) flashExpenseLabel.textContent = t.total_expense;
  if (flashSavingsLabel) flashSavingsLabel.textContent = `🏦 ${t.savings_rate_lbl}`;

  if (periodBadge) periodBadge.textContent = getPeriodDisplayText(currentPeriod, customStartDate, customEndDate);
  if (tapHintText) tapHintText.textContent = t.tap_hint;
  if (periodModalTitle) periodModalTitle.textContent = t.period_modal_title;
  if (optWeekText) optWeekText.textContent = t.opt_week;
  if (optMonthText) optMonthText.textContent = t.opt_month;
  if (optYearText) optYearText.textContent = t.opt_year;
  if (optAllText) optAllText.textContent = t.opt_all;
  if (optCustomText) optCustomText.textContent = t.opt_custom;
  if (lblRangeStart) lblRangeStart.textContent = t.lbl_range_start;
  if (lblRangeEnd) lblRangeEnd.textContent = t.lbl_range_end;
  if (applyRangeBtn) applyRangeBtn.textContent = t.btn_apply_range;

  populateCategoryOptions(selectedType);
}

function populateCategoryOptions(type) {
  txCategorySelect.replaceChildren();
  const standardMap = CATEGORIES[type] || CATEGORIES.expense;
  const customList = userCustomCategories[type] || [];

  // 1. Standard categories
  Object.entries(standardMap).forEach(([name, emoji]) => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = `${emoji} ${getDisplayCategory(name)}`;
    txCategorySelect.appendChild(opt);
  });

  // 2. User custom categories
  customList.forEach((name) => {
    if (!standardMap[name]) {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = `🏷️ ${name}`;
      txCategorySelect.appendChild(opt);
    }
  });
}

async function fetchUserCategories() {
  if (!navigator.onLine) return;
  try {
    const res = await fetch(`/api/categories?userId=${encodeURIComponent(userId)}`);
    if (res.ok) {
      const data = await res.json();
      if (data.expense && Array.isArray(data.expense)) {
        userCustomCategories.expense = data.expense;
      }
      if (data.income && Array.isArray(data.income)) {
        userCustomCategories.income = data.income;
      }
      populateCategoryOptions(selectedType);
    }
  } catch (e) {
    // Graceful offline fallback
  }
}

function renderTransactions(transactions) {
  const t = I18N[currentLang] || I18N.en;

  // Sort descending by date
  const sorted = [...transactions].sort((a, b) => new Date(b.date) - new Date(a.date));

  // Compute metrics
  let totalIncome = 0;
  let totalExpense = 0;

  sorted.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'income') {
      totalIncome += amt;
    } else {
      totalExpense += amt;
    }
  });

  const netBalance = totalIncome - totalExpense;
  totalBalanceEl.textContent = formatCurrency(netBalance, userCurrency);
  totalIncomeEl.textContent = `+${formatCurrency(totalIncome, userCurrency)}`;
  totalExpenseEl.textContent = `-${formatCurrency(totalExpense, userCurrency)}`;

  // Update Net Balance Flashback Card metrics
  if (flashNetVal) {
    const netSign = netBalance >= 0 ? '+' : '-';
    flashNetVal.textContent = `${netSign}${formatCurrency(Math.abs(netBalance), userCurrency)}`;
  }
  if (flashNetBadge) {
    if (netBalance >= 0) {
      flashNetBadge.className = 'status-pill surplus';
      flashNetBadge.textContent = t.surplus;
    } else {
      flashNetBadge.className = 'status-pill deficit';
      flashNetBadge.textContent = t.deficit;
    }
  }

  const balanceStatusBadge = document.getElementById('balanceStatusBadge');
  if (balanceStatusBadge) {
    if (netBalance >= 0) {
      balanceStatusBadge.className = 'status-pill surplus';
      balanceStatusBadge.textContent = `🟢 ${t.surplus}`;
    } else {
      balanceStatusBadge.className = 'status-pill deficit';
      balanceStatusBadge.textContent = `🔴 ${t.deficit}`;
    }
  }
  const totalFlow = totalIncome + totalExpense;
  const incomeRatio = totalFlow > 0 ? (totalIncome / totalFlow) * 100 : 50;
  const expenseRatio = totalFlow > 0 ? (totalExpense / totalFlow) * 100 : 50;
  if (cashflowIncomeBar) cashflowIncomeBar.style.width = `${incomeRatio}%`;
  if (cashflowExpenseBar) cashflowExpenseBar.style.width = `${expenseRatio}%`;
  if (flashIncomeVal) flashIncomeVal.textContent = `+${formatCurrency(totalIncome, userCurrency)}`;
  if (flashExpenseVal) flashExpenseVal.textContent = `-${formatCurrency(totalExpense, userCurrency)}`;
  const savingsPct = totalIncome > 0 ? Math.max(0, (netBalance / totalIncome) * 100) : 0;
  if (flashSavingsVal) flashSavingsVal.textContent = `${savingsPct.toFixed(1)}%`;

  // Filter for display
  const filtered = sorted.filter((tx) => {
    if (currentFilter === 'all') return true;
    return tx.type === currentFilter;
  });

  txCountEl.textContent = `${filtered.length} ${filtered.length === 1 ? t.item : t.items}`;
  transactionListEl.replaceChildren();

  if (filtered.length === 0) {
    const emptyContainer = document.createElement('div');
    emptyContainer.className = 'empty-state';

    const iconSpan = document.createElement('div');
    iconSpan.className = 'empty-icon';
    iconSpan.textContent = '📊';

    const titleDiv = document.createElement('div');
    titleDiv.className = 'empty-title';
    titleDiv.textContent = t.no_records;

    const hintDiv = document.createElement('div');
    hintDiv.textContent = t.no_records_hint;

    emptyContainer.appendChild(iconSpan);
    emptyContainer.appendChild(titleDiv);
    emptyContainer.appendChild(hintDiv);
    transactionListEl.appendChild(emptyContainer);
    return;
  }

  filtered.forEach((tx) => {
    const itemCard = document.createElement('div');
    itemCard.className = 'tx-item';

    // Left block
    const leftDiv = document.createElement('div');
    leftDiv.className = 'tx-left';

    const iconDiv = document.createElement('div');
    iconDiv.className = `tx-icon ${tx.type}`;
    const emoji = (CATEGORIES[tx.type] && CATEGORIES[tx.type][tx.category]) || (tx.type === 'income' ? '💵' : '📦');
    iconDiv.textContent = emoji;

    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'tx-details';

    const categoryTitle = document.createElement('div');
    categoryTitle.className = 'tx-category';
    categoryTitle.textContent = getDisplayCategory(tx.category);

    const metaDiv = document.createElement('div');
    metaDiv.className = 'tx-meta';

    const dateSpan = document.createElement('span');
    const d = new Date(tx.date);
    dateSpan.textContent = isNaN(d) ? 'Recent' : d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

    metaDiv.appendChild(dateSpan);

    if (tx.note) {
      const noteSpan = document.createElement('span');
      noteSpan.textContent = `• ${tx.note}`;
      metaDiv.appendChild(noteSpan);
    }

    detailsDiv.appendChild(categoryTitle);
    detailsDiv.appendChild(metaDiv);

    leftDiv.appendChild(iconDiv);
    leftDiv.appendChild(detailsDiv);

    // Right block - amount with sync status dot at the end (gray = local, green = synced)
    const rightDiv = document.createElement('div');
    rightDiv.className = 'tx-right';

    const amountSpan = document.createElement('span');
    amountSpan.className = `tx-amount ${tx.type}`;
    const prefix = tx.type === 'income' ? '+' : '-';
    amountSpan.textContent = `${prefix}${formatCurrency(tx.amount, tx.currency || userCurrency)}`;

    const syncDot = document.createElement('span');
    syncDot.className = `sync-dot ${tx.synced ? 'synced' : 'local'}`;
    syncDot.title = tx.synced ? (t.synced_tag || 'Synced') : (t.local_tag || 'Local');
    amountSpan.appendChild(syncDot);

    rightDiv.appendChild(amountSpan);

    itemCard.appendChild(leftDiv);
    itemCard.appendChild(rightDiv);

    transactionListEl.appendChild(itemCard);
  });
}

function renderPieChart(transactions) {
  if (!pieChartSvg) return;
  const t = I18N[currentLang] || I18N.en;

  // Aggregate expenses and income
  const expenses = {};
  let totalExpense = 0;
  let totalIncome = 0;

  transactions.forEach((tx) => {
    const amt = Number(tx.amount) || 0;
    if (tx.type === 'expense') {
      if (amt > 0) {
        expenses[tx.category] = (expenses[tx.category] || 0) + amt;
        totalExpense += amt;
      }
    } else if (tx.type === 'income') {
      if (amt > 0) {
        totalIncome += amt;
      }
    }
  });

  const netBalance = totalIncome - totalExpense;
  const netSign = netBalance >= 0 ? '+' : '-';

  pieChartSvg.replaceChildren();
  if (chartLegendList) chartLegendList.replaceChildren();

  const resetCenter = () => {
    if (chartCenterLabel) chartCenterLabel.textContent = t.net_balance;
    if (chartCenterValue) chartCenterValue.textContent = `${netSign}${formatCurrency(Math.abs(netBalance), userCurrency)}`;
  };
  resetCenter();

  const sortedCats = Object.entries(expenses).sort((a, b) => b[1] - a[1]);

  if (sortedCats.length === 0 || totalExpense === 0) {
    // Render placeholder subtle circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', '110');
    circle.setAttribute('cy', '110');
    circle.setAttribute('r', chartViewMode === 'donut' ? '70' : '85');
    circle.setAttribute('fill', 'none');
    circle.setAttribute('stroke', 'rgba(255, 255, 255, 0.08)');
    circle.setAttribute('stroke-width', chartViewMode === 'donut' ? '28' : '4');
    pieChartSvg.appendChild(circle);

    if (chartLegendList) {
      const emptyMsg = document.createElement('div');
      emptyMsg.className = 'report-sub';
      emptyMsg.style.gridColumn = '1 / -1';
      emptyMsg.style.textAlign = 'center';
      emptyMsg.textContent = t.no_expense_chart;
      chartLegendList.appendChild(emptyMsg);
    }
    return;
  }

  const cx = 110;
  const cy = 110;
  const rOuter = 85;
  const rInner = chartViewMode === 'donut' ? 52 : 0;

  let startAngle = -90; // Start at top (12 o'clock)

  sortedCats.forEach(([cat, amt], idx) => {
    const fraction = amt / totalExpense;
    const sweepAngle = fraction * 360;
    const endAngle = startAngle + sweepAngle;
    const color = CHART_COLORS[idx % CHART_COLORS.length];
    const emoji = (CATEGORIES.expense && CATEGORIES.expense[cat]) || '📦';
    const dispName = getDisplayCategory(cat);
    const pctStr = (fraction * 100).toFixed(1);

    // Build SVG path
    let pathEl;
    if (sortedCats.length === 1 || fraction >= 0.999) {
      // Single category 100% full circle
      if (chartViewMode === 'donut') {
        pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        pathEl.setAttribute('cx', String(cx));
        pathEl.setAttribute('cy', String(cy));
        pathEl.setAttribute('r', String((rOuter + rInner) / 2));
        pathEl.setAttribute('fill', 'none');
        pathEl.setAttribute('stroke', color);
        pathEl.setAttribute('stroke-width', String(rOuter - rInner));
      } else {
        pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        pathEl.setAttribute('cx', String(cx));
        pathEl.setAttribute('cy', String(cy));
        pathEl.setAttribute('r', String(rOuter));
        pathEl.setAttribute('fill', color);
      }
    } else {
      const rad = (deg) => (deg * Math.PI) / 180;
      const x1 = cx + rOuter * Math.cos(rad(startAngle));
      const y1 = cy + rOuter * Math.sin(rad(startAngle));
      const x2 = cx + rOuter * Math.cos(rad(endAngle));
      const y2 = cy + rOuter * Math.sin(rad(endAngle));
      const largeArc = sweepAngle > 180 ? 1 : 0;

      let d;
      if (chartViewMode === 'donut') {
        const ix1 = cx + rInner * Math.cos(rad(startAngle));
        const iy1 = cy + rInner * Math.sin(rad(startAngle));
        const ix2 = cx + rInner * Math.cos(rad(endAngle));
        const iy2 = cy + rInner * Math.sin(rad(endAngle));
        d = `M ${x1} ${y1} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2} ${y2} L ${ix2} ${iy2} A ${rInner} ${rInner} 0 ${largeArc} 0 ${ix1} ${iy1} Z`;
      } else {
        d = `M ${cx} ${cy} L ${x1} ${y1} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2} ${y2} Z`;
      }

      pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathEl.setAttribute('d', d);
      pathEl.setAttribute('fill', color);
    }

    pathEl.setAttribute('class', 'pie-slice');

    // Hover & Touch interaction
    const onActivate = () => {
      document.querySelectorAll('.pie-slice').forEach(s => s.classList.remove('active'));
      document.querySelectorAll('.legend-item').forEach(l => l.classList.remove('active'));
      pathEl.classList.add('active');
      const legEl = document.getElementById(`leg_${idx}`);
      if (legEl) legEl.classList.add('active');
      if (chartCenterLabel) chartCenterLabel.textContent = `${emoji} ${dispName}`;
      if (chartCenterValue) chartCenterValue.textContent = `${formatCurrency(amt, userCurrency)} (${pctStr}%)`;
    };

    pathEl.addEventListener('mouseenter', onActivate);
    pathEl.addEventListener('click', onActivate);

    pieChartSvg.appendChild(pathEl);

    // Build Legend item
    if (chartLegendList) {
      const legItem = document.createElement('div');
      legItem.className = 'legend-item';
      legItem.id = `leg_${idx}`;

      const left = document.createElement('div');
      left.className = 'legend-left';

      const dot = document.createElement('span');
      dot.className = 'legend-dot';
      dot.style.backgroundColor = color;

      const nameSpan = document.createElement('span');
      nameSpan.className = 'legend-name';
      nameSpan.textContent = `${emoji} ${dispName}`;

      left.appendChild(dot);
      left.appendChild(nameSpan);

      const pctSpan = document.createElement('span');
      pctSpan.className = 'legend-pct';
      pctSpan.textContent = `${pctStr}%`;

      legItem.appendChild(left);
      legItem.appendChild(pctSpan);

      legItem.addEventListener('click', onActivate);
      legItem.addEventListener('mouseenter', onActivate);
      legItem.addEventListener('mouseleave', resetCenter);

      chartLegendList.appendChild(legItem);
    }

    startAngle = endAngle;
  });

  pieChartSvg.addEventListener('mouseleave', resetCenter);
}

// -------------------------------------------------------------
// SYNC & DATA FETCHING ENGINE
// -------------------------------------------------------------
async function refreshLocalUI() {
  const allTxs = await idbGetAll('transactions');
  const periodTxs = filterTransactionsByPeriod(allTxs, currentPeriod, customStartDate, customEndDate);

  if (periodBadge) {
    periodBadge.textContent = getPeriodDisplayText(currentPeriod, customStartDate, customEndDate);
  }

  renderTransactions(periodTxs);
  renderPieChart(periodTxs);
  checkQueueStatus();
}

async function checkQueueStatus() {
  const queue = await idbGetAll('sync_queue');
  const t = I18N[currentLang] || I18N.en;
  if (queue.length > 0) {
    bannerText.textContent = `⚡ ${queue.length} ${t.items} queued. ${t.offline_banner}`;
    offlineBanner.className = 'status-banner';
  } else if (!navigator.onLine) {
    bannerText.textContent = `⚡ ${t.offline_banner}`;
    offlineBanner.className = 'status-banner';
  } else {
    offlineBanner.className = 'status-banner hidden';
  }
}

async function fetchServerTransactions() {
  if (!navigator.onLine) return;

  try {
    const res = await fetch(`/api/transactions?userId=${encodeURIComponent(userId)}`);
    if (!res.ok) return;

    const data = await res.json();
    if (data.transactions && Array.isArray(data.transactions)) {
      for (const serverTx of data.transactions) {
        serverTx.synced = true;
        await idbPut('transactions', serverTx);
      }
      refreshLocalUI();
    }
  } catch (err) {
    // Network or server unreachable; offline-first continues seamlessly
  }
}

async function processSyncQueue() {
  if (!navigator.onLine) return;

  const queue = await idbGetAll('sync_queue');
  if (queue.length === 0) return;

  const t = I18N[currentLang] || I18N.en;
  bannerText.textContent = `🔄 Syncing ${queue.length} offline record(s)...`;
  offlineBanner.className = 'status-banner';

  for (const item of queue) {
    try {
      const res = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId,
          transaction: item
        })
      });

      if (res.ok) {
        const responseData = await res.json();
        // Remove from queue
        await idbDelete('sync_queue', item.id);

        // Update local transaction store with confirmed synced record
        item.synced = true;
        if (responseData.server_id) {
          // Replace temporary ID with server ID
          await idbDelete('transactions', item.id);
          item.id = responseData.server_id;
        }
        await idbPut('transactions', item);
      }
    } catch (err) {
      // Interrupted network, queue remains for subsequent retry
      break;
    }
  }

  const remaining = await idbGetAll('sync_queue');
  if (remaining.length === 0) {
    bannerText.textContent = '✓ All records synchronized successfully!';
    offlineBanner.className = 'status-banner synced';
    setTimeout(() => {
      offlineBanner.className = 'status-banner hidden';
    }, 2500);
  } else {
    checkQueueStatus();
  }

  refreshLocalUI();
}

// -------------------------------------------------------------
// EVENT HANDLERS
// -------------------------------------------------------------
function setNetworkState(isOnline) {
  const t = I18N[currentLang] || I18N.en;
  if (isOnline) {
    networkPill.className = 'network-pill online';
    networkText.textContent = t.online;
    processSyncQueue();
    fetchServerTransactions();
  } else {
    networkPill.className = 'network-pill offline';
    networkText.textContent = t.offline;
    checkQueueStatus();
  }
}

window.addEventListener('online', () => setNetworkState(true));
window.addEventListener('offline', () => setNetworkState(false));

// Language Switcher Toggle
if (langToggleBtn) {
  langToggleBtn.addEventListener('click', () => {
    triggerHaptic('light');
    currentLang = currentLang === 'en' ? 'km' : 'en';
    localStorage.setItem('app_lang', currentLang);
    applyLanguage(currentLang);
    setNetworkState(navigator.onLine);
    refreshLocalUI();
  });
}

// Chart Mode Toggle (Pie <-> Donut)
if (toggleChartTypeBtn) {
  toggleChartTypeBtn.addEventListener('click', () => {
    triggerHaptic('light');
    chartViewMode = chartViewMode === 'donut' ? 'pie' : 'donut';
    const t = I18N[currentLang] || I18N.en;
    toggleChartTypeBtn.textContent = chartViewMode === 'donut' ? t.toggle_pie : t.toggle_donut;
    refreshLocalUI();
  });
}

// Flash Back to Net Balance Card
if (flashbackNetBalanceBtn) {
  flashbackNetBalanceBtn.addEventListener('click', () => {
    triggerHaptic('medium');
    const isShowingNet = reportNetBalanceView && !reportNetBalanceView.classList.contains('hidden');

    if (isShowingNet) {
      // Toggle back to Chart view
      if (reportNetBalanceView) reportNetBalanceView.classList.add('hidden');
      if (reportChartView) reportChartView.classList.remove('hidden');
      if (reportCardIcon) reportCardIcon.textContent = '🥧';
      if (reportCardTitleEl) reportCardTitleEl.textContent = (I18N[currentLang] || I18N.en).report_title;
    } else {
      // Flash to Net Balance view
      if (reportChartView) reportChartView.classList.add('hidden');
      if (reportNetBalanceView) reportNetBalanceView.classList.remove('hidden');
      if (reportCardIcon) reportCardIcon.textContent = '⚡';
      if (reportCardTitleEl) reportCardTitleEl.textContent = (I18N[currentLang] || I18N.en).flash_net_label;

      // Trigger flashy neon pulse on the hero balance card
      const heroBalance = document.querySelector('.balance-card');
      if (heroBalance) {
        heroBalance.classList.remove('flash-pulse');
        void heroBalance.offsetWidth;
        heroBalance.classList.add('flash-pulse');
        heroBalance.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  });
}

// Return to Chart button inside Flash view
if (flashbackToChartBtn) {
  flashbackToChartBtn.addEventListener('click', () => {
    triggerHaptic('light');
    if (reportNetBalanceView) reportNetBalanceView.classList.add('hidden');
    if (reportChartView) reportChartView.classList.remove('hidden');
    if (reportCardIcon) reportCardIcon.textContent = '🥧';
    if (reportCardTitleEl) reportCardTitleEl.textContent = (I18N[currentLang] || I18N.en).report_title;
  });
}

function formatLocalDateTime(date) {
  const d = date || new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const year = d.getFullYear();
  const month = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Modal Controls
openModalBtn.addEventListener('click', () => {
  triggerHaptic('light');
  txModal.classList.add('active');
  txDateTimeInput.value = formatLocalDateTime(new Date());
  txAmountInput.value = '';
  txNoteInput.value = '';
  populateCategoryOptions(selectedType);
  txAmountInput.focus();
});

// Quick Date Chips
chipNow.addEventListener('click', () => {
  triggerHaptic('light');
  txDateTimeInput.value = formatLocalDateTime(new Date());
});

chipToday.addEventListener('click', () => {
  triggerHaptic('light');
  const d = new Date();
  d.setHours(12, 0, 0, 0);
  txDateTimeInput.value = formatLocalDateTime(d);
});

chipYesterday.addEventListener('click', () => {
  triggerHaptic('light');
  const d = new Date();
  d.setDate(d.getDate() - 1);
  d.setHours(12, 0, 0, 0);
  txDateTimeInput.value = formatLocalDateTime(d);
});

closeModalBtn.addEventListener('click', () => {
  txModal.classList.remove('active');
});

txModal.addEventListener('click', (e) => {
  if (e.target === txModal) {
    txModal.classList.remove('active');
  }
});

// Category Modal Event Listeners
addCatBtn.addEventListener('click', () => {
  triggerHaptic('light');
  catModal.classList.add('active');
  newCatNameInput.value = '';
  newCatNameInput.focus();
});

closeCatModalBtn.addEventListener('click', () => {
  catModal.classList.remove('active');
});

catModal.addEventListener('click', (e) => {
  if (e.target === catModal) {
    catModal.classList.remove('active');
  }
});

catForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  triggerHaptic('medium');
  const catName = newCatNameInput.value.trim();
  if (!catName) return;

  if (!userCustomCategories[selectedType].includes(catName)) {
    userCustomCategories[selectedType].push(catName);
  }

  populateCategoryOptions(selectedType);
  txCategorySelect.value = catName;
  catModal.classList.remove('active');
  const t = I18N[currentLang] || I18N.en;
  showToast(t.toast_added);

  // Sync category to server if online
  if (navigator.onLine) {
    try {
      await fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId,
          type: selectedType,
          name: catName,
        })
      });
    } catch (err) {
      // Offline fallback
    }
  }
});

// Type toggle in form
typeExpenseBtn.addEventListener('click', () => {
  triggerHaptic('light');
  selectedType = 'expense';
  typeExpenseBtn.className = 'segment-btn active expense';
  typeIncomeBtn.className = 'segment-btn income';
  populateCategoryOptions('expense');
});

typeIncomeBtn.addEventListener('click', () => {
  triggerHaptic('light');
  selectedType = 'income';
  typeIncomeBtn.className = 'segment-btn active income';
  typeExpenseBtn.className = 'segment-btn expense';
  populateCategoryOptions('income');
});

// Filter Tabs
document.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    triggerHaptic('light');
    document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    refreshLocalUI();
  });
});

// Submit Form (Add Record)
txForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  triggerHaptic('medium');
  const t = I18N[currentLang] || I18N.en;

  const amount = parseFloat(txAmountInput.value);
  if (isNaN(amount) || amount <= 0) {
    showToast(t.toast_invalid_amt);
    return;
  }

  const category = txCategorySelect.value;
  const note = txNoteInput.value.trim();
  const chosenDateTime = txDateTimeInput.value;

  let txDateIso;
  if (chosenDateTime) {
    txDateIso = new Date(chosenDateTime).toISOString();
  } else {
    txDateIso = new Date().toISOString();
  }

  // Temporary unique ID
  const tempId = `local_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const newTx = {
    id: tempId,
    type: selectedType,
    category: category,
    amount: amount,
    currency: userCurrency,
    wallet: 'Bank',
    note: note,
    date: txDateIso,
    synced: false
  };

  // 1. Write immediately to local IndexedDB transactions store
  await idbPut('transactions', newTx);
  txModal.classList.remove('active');
  refreshLocalUI();

  // 2. Network Check
  if (navigator.onLine) {
    showToast('Saving to cloud...');
    try {
      const res = await fetch('/api/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userId,
          transaction: newTx
        })
      });

      if (res.ok) {
        const result = await res.json();
        // Server accepted
        newTx.synced = true;
        if (result.server_id) {
          await idbDelete('transactions', tempId);
          newTx.id = result.server_id;
        }
        await idbPut('transactions', newTx);
        showToast(t.toast_record_saved);
        refreshLocalUI();
      } else {
        throw new Error('Sync failed');
      }
    } catch (err) {
      // Request failed: Queue for later background sync
      await idbPut('sync_queue', newTx);
      showToast(t.toast_offline_saved);
      checkQueueStatus();
    }
  } else {
    // 3. Offline Mode: Add to sync queue
    await idbPut('sync_queue', newTx);
    showToast(t.toast_offline_saved);
    checkQueueStatus();
  }
});

// -------------------------------------------------------------
// REPORT PERIOD SELECTION CONTROLS (TAP HERO BALANCE CARD)
// -------------------------------------------------------------
if (balanceCardTrigger) {
  const openPeriodModal = () => {
    triggerHaptic('light');
    // Pre-fill date inputs if empty
    if (rangeStartDate && !rangeStartDate.value) {
      const now = new Date();
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
      const pad = (n) => String(n).padStart(2, '0');
      rangeStartDate.value = `${firstDay.getFullYear()}-${pad(firstDay.getMonth() + 1)}-${pad(firstDay.getDate())}`;
    }
    if (rangeEndDate && !rangeEndDate.value) {
      const now = new Date();
      const pad = (n) => String(n).padStart(2, '0');
      rangeEndDate.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
    }
    // Update active class on period buttons
    document.querySelectorAll('.period-btn').forEach((b) => {
      if (b.dataset.period === currentPeriod) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
    if (customRangeSection) {
      if (currentPeriod === 'custom') {
        customRangeSection.classList.remove('hidden');
      } else {
        customRangeSection.classList.add('hidden');
      }
    }
    if (periodModal) {
      periodModal.classList.add('active');
    }
  };

  balanceCardTrigger.addEventListener('click', openPeriodModal);
  balanceCardTrigger.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openPeriodModal();
    }
  });
}

// Close Period Modal
if (closePeriodModalBtn) {
  closePeriodModalBtn.addEventListener('click', () => {
    if (periodModal) periodModal.classList.remove('active');
  });
}

if (periodModal) {
  periodModal.addEventListener('click', (e) => {
    if (e.target === periodModal) {
      periodModal.classList.remove('active');
    }
  });
}

// Period Quick Selection Buttons
document.querySelectorAll('.period-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    triggerHaptic('medium');
    const period = btn.dataset.period;
    document.querySelectorAll('.period-btn').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');

    if (period === 'custom') {
      if (customRangeSection) customRangeSection.classList.remove('hidden');
      return;
    }

    if (customRangeSection) customRangeSection.classList.add('hidden');
    currentPeriod = period;
    if (periodModal) periodModal.classList.remove('active');

    // Visual pulse on dashboard card
    const dashCard = document.getElementById('mainDashboardCard');
    if (dashCard) {
      dashCard.classList.remove('flash-pulse');
      void dashCard.offsetWidth;
      dashCard.classList.add('flash-pulse');
    }

    refreshLocalUI();
  });
});

// Apply Custom Date Range Button
if (applyRangeBtn) {
  applyRangeBtn.addEventListener('click', () => {
    triggerHaptic('medium');
    const start = rangeStartDate ? rangeStartDate.value : null;
    const end = rangeEndDate ? rangeEndDate.value : null;

    if (start && end && start > end) {
      showToast(currentLang === 'km' ? '⚠️ កាលបរិច្ឆេទចាប់ផ្តើមត្រូវតែមុនកាលបរិច្ឆេទបញ្ចប់' : '⚠️ Start date must be before end date.');
      return;
    }

    currentPeriod = 'custom';
    customStartDate = start || null;
    customEndDate = end || null;
    if (periodModal) periodModal.classList.remove('active');

    const dashCard = document.getElementById('mainDashboardCard');
    if (dashCard) {
      dashCard.classList.remove('flash-pulse');
      void dashCard.offsetWidth;
      dashCard.classList.add('flash-pulse');
    }

    refreshLocalUI();
  });
}

// -------------------------------------------------------------
// APP BOOTSTRAP
// -------------------------------------------------------------
async function bootstrap() {
  initTelegram();
  applyLanguage(currentLang);

  // Register Service Worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // Ignore Service Worker registration errors in restricted environments
    });
  }

  // Open IndexedDB
  await openDatabase();

  // Immediate local UI render
  await refreshLocalUI();

  // Initial network check & category fetch
  setNetworkState(navigator.onLine);
  fetchUserCategories();
}

document.addEventListener('DOMContentLoaded', bootstrap);
