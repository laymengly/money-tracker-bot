#!/usr/bin/env bash
# Deploy script for Money Tracker & Mini App on Firebase (Bash)

set -e

TARGET=${1:-all}
PROJECT=${2:-""}

echo "🔥 Starting Firebase Deployment..."

if ! command -v firebase &> /dev/null; then
    echo "❌ firebase-tools is not installed. Run: npm install -g firebase-tools"
    exit 1
fi

PROJECT_ARGS=()
if [ -n "$PROJECT" ]; then
    PROJECT_ARGS=("--project" "$PROJECT")
fi

case "$TARGET" in
    hosting)
        echo "📦 Deploying Firebase Hosting (Telegram Mini App)..."
        firebase deploy --only hosting "${PROJECT_ARGS[@]}"
        ;;
    firestore)
        echo "🛡️ Deploying Cloud Firestore Rules & Indexes..."
        firebase deploy --only firestore "${PROJECT_ARGS[@]}"
        ;;
    functions)
        echo "⚡ Deploying Cloud Functions (FastAPI Backend)..."
        firebase deploy --only functions "${PROJECT_ARGS[@]}"
        ;;
    all)
        echo "🚀 Deploying Full Stack (Hosting + Firestore + Functions)..."
        firebase deploy "${PROJECT_ARGS[@]}"
        ;;
    *)
        echo "❌ Unknown target '$TARGET'. Use: all, hosting, firestore, or functions."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment completed successfully!"
echo "👉 To configure Telegram Webhook with your deployed URL, run:"
echo "   python set_webhook.py --url https://<your-project-id>.web.app"
echo ""

