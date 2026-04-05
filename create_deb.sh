#!/bin/bash
# SnapLoop — Linux .deb Paketi Oluşturucu
# Ubuntu/Debian için

APP_NAME="snaploop"
VERSION="2.1.0"
ARCH="amd64"
PKG_DIR="pkg_${APP_NAME}_${VERSION}"

echo "🐧 Linux .deb paketi oluşturuluyor..."

# Klasör yapısı
mkdir -p "${PKG_DIR}/DEBIAN"
mkdir -p "${PKG_DIR}/usr/local/bin"
mkdir -p "${PKG_DIR}/usr/share/applications"
mkdir -p "${PKG_DIR}/usr/share/pixmaps"

# Binary kopyala
cp dist/SnapLoop "${PKG_DIR}/usr/local/bin/snaploop"
chmod +x "${PKG_DIR}/usr/local/bin/snaploop"

# DEBIAN/control
cat > "${PKG_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Architecture: ${ARCH}
Maintainer: SnapLoop <info@snaploop.app>
Description: Cross-platform ekran kaydedici
 Çoklu ekran ve pencere bazlı ekran görüntüsü kaydeder.
 Otomatik ZIP, mail gönderimi ve boyut limiti destekler.
Depends: wmctrl
EOF

# .desktop dosyası (uygulama menüsü)
cat > "${PKG_DIR}/usr/share/applications/snaploop.desktop" << EOF
[Desktop Entry]
Version=1.0
Name=SnapLoop
Comment=Ekran Kaydedici
Exec=/usr/local/bin/snaploop
Icon=snaploop
Terminal=false
Type=Application
Categories=Utility;
EOF

# .deb oluştur
dpkg-deb --build "${PKG_DIR}" "SnapLoop_${VERSION}_${ARCH}.deb"

# Temizle
rm -rf "${PKG_DIR}"

echo "✅ Hazır: SnapLoop_${VERSION}_${ARCH}.deb"
echo ""
echo "Kurmak için:"
echo "  sudo dpkg -i SnapLoop_${VERSION}_${ARCH}.deb"
