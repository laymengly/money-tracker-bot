# Money Tracker & Financial Assistant

An offline-first personal finance tracker and Telegram Mini App (TMA) rewritten in React and TypeScript with Vite.

## Features

- **Side-by-Side Unified Dashboard**:
  - Interactive SVG Donut / Pie chart with dynamic slice calculation and responsive hover/touch details.
  - Net Balance Hero card with period badge and surplus/deficit health status.
  - Inflow & outflow stack with cashflow progress ratio and savings rate meter.
  - Category breakdown legend with interactive focus.
- **Bilingual Support (English 🇺🇸 & Khmer 🇰🇭)**:
  - Instant one-tap language switching with complete translations for all categories, buttons, prompts, and statistics.
- **Multi-Period Filtering**:
  - Filter reports and transaction history by:
    - This Week
    - This Month
    - This Year
    - All Time
    - Custom Date Range (interactive Start/End calendar pickers)
- **Transaction Management**:
  - Quick transaction logging with quick date chips (`⚡ Now`, `Today`, `Yesterday`).
  - Categorization with emojis for expense and income streams.
  - Custom category creator (`+ New`) with validation and instant availability.
  - Optional memo/note support.
- **Offline-First & Telegram Native**:
  - Full offline functionality with persistent local storage.
  - Visual sync dots (green = synced, gray = local).
  - Online/offline network indicator pill and status banner.
  - Telegram WebApp SDK support with haptic feedback and user profile synchronization.

## Technology Stack

- **Framework**: React 19 + TypeScript
- **Bundler / Dev Server**: Vite
- **Styling**: Modern dark mode UI tokens with CSS variables and glassmorphism

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```
