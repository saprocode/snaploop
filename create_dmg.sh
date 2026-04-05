#!/bin/bash
# SnapLoop — macOS DMG Oluşturucu
# Gereksinim: create-dmg  →  brew install create-dmg

APP_NAME="SnapLoop"
VERSION="2.0.0"
APP_PATH="dist/SnapLoop.app"
DMG_NAME="SnapLoop_${VERSION}.dmg"

echo "🍎 macOS DMG oluşturuluyor..."

# create-dmg yüklü değilse kur
if ! command -v create-dmg &> /dev/null; then
    echo "📦 create-dmg kuruluyor..."
    brew install create-dmg
fi

# DMG oluştur
create-dmg \
  --volname "${APP_NAME}" \
  --volicon "icon.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "${APP_NAME}.app" 175 190 \
  --hide-extension "${APP_NAME}.app" \
  --app-drop-link 425 190 \
  --no-internet-enable \
  "${DMG_NAME}" \
  "${APP_PATH}"

echo "✅ Hazır: ${DMG_NAME}"
