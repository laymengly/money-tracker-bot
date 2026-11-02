# Deploy script for Money Tracker & Mini App on Firebase (PowerShell)
param (
    [string]$Target = "all",
    [string]$Project = ""
)

Write-Host "🔥 Starting Firebase Deployment..." -ForegroundColor Cyan

# Check Firebase CLI
if (-not (Get-Command "firebase" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ firebase-tools is not installed. Run: npm install -g firebase-tools" -ForegroundColor Red
    exit 1
}

$deployArgs = @()

if ($Project -ne "") {
    $deployArgs += @("--project", $Project)
}

switch ($Target.ToLower()) {
    "hosting" {
        Write-Host "📦 Deploying Firebase Hosting (Telegram Mini App)..." -ForegroundColor Yellow
        firebase deploy --only hosting @deployArgs
    }
    "firestore" {
        Write-Host "🛡️ Deploying Cloud Firestore Rules & Indexes..." -ForegroundColor Yellow
        firebase deploy --only firestore @deployArgs
    }
    "functions" {
        Write-Host "⚡ Deploying Cloud Functions (FastAPI Backend)..." -ForegroundColor Yellow
        firebase deploy --only functions @deployArgs
    }
    "all" {
        Write-Host "🚀 Deploying Full Stack (Hosting + Firestore + Functions)..." -ForegroundColor Yellow
        firebase deploy @deployArgs
    }
    default {
        Write-Host "Unknown target '$Target'. Use: all, hosting, firestore, or functions." -ForegroundColor Red
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "👉 To configure Telegram Webhook with your deployed URL, run:" -ForegroundColor Cyan
    Write-Host "   python set_webhook.py --url https://<your-project-id>.web.app`n" -ForegroundColor White
} else {
    Write-Host "`n❌ Deployment failed. If your login token expired, run: firebase login --reauth" -ForegroundColor Yellow
}

