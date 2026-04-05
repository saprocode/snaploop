#!/usr/bin/env python3
"""
SnapLoop — Otomatik Build Script
Kullanım: python build.py
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

APP_NAME    = "SnapLoop"
MAIN_SCRIPT = "snaploop.py"
VERSION     = "2.0.0"

def run(cmd):
    print(f"\n▶  {cmd}\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Hata! Komut başarısız: {cmd}")
        sys.exit(1)

def install_pyinstaller():
    print("📦 PyInstaller kuruluyor...")
    run(f"{sys.executable} -m pip install pyinstaller mss Pillow psutil --upgrade")

def build():
    platform = sys.platform
    print(f"\n🔨 Platform: {platform}")
    print(f"🐍 Python:   {sys.version}")

    # Önceki build'i temizle
    for d in ["build", "dist"]:
        if Path(d).exists():
            shutil.rmtree(d)
            print(f"🗑  {d}/ temizlendi")

    # Ortak PyInstaller argümanları
    args = [
        f"--name={APP_NAME}",
        "--onefile",          # Tek dosya
        "--windowed",         # Terminal penceresi çıkmasın (GUI app)
        "--clean",
        f"--add-data=README.md{os.pathsep}.",
    ]

    # İkon (varsa)
    icon_path = Path("icon.ico") if platform == "win32" else Path("icon.icns")
    if icon_path.exists():
        args.append(f"--icon={icon_path}")

    # Platform özel ayarlar
    if platform == "win32":
        args += [
            "--version-file=version_info.txt",  # Windows sürüm bilgisi
        ]
    elif platform == "darwin":
        args += [
            "--osx-bundle-identifier=com.snaploop.app",
        ]

    cmd = f"{sys.executable} -m PyInstaller {' '.join(args)} {MAIN_SCRIPT}"
    run(cmd)

    # Çıktıyı göster
    dist = Path("dist")
    if platform == "win32":
        exe = dist / f"{APP_NAME}.exe"
        if exe.exists():
            size = exe.stat().st_size / 1024 / 1024
            print(f"\n✅ Başarılı! → dist/{APP_NAME}.exe  ({size:.1f} MB)")
    elif platform == "darwin":
        app = dist / f"{APP_NAME}.app"
        exe = dist / APP_NAME
        target = app if app.exists() else exe
        print(f"\n✅ Başarılı! → dist/{target.name}")
    else:
        exe = dist / APP_NAME
        if exe.exists():
            size = exe.stat().st_size / 1024 / 1024
            print(f"\n✅ Başarılı! → dist/{APP_NAME}  ({size:.1f} MB)")

    print(f"\n📁 Çıktı klasörü: {dist.absolute()}")


def create_version_info():
    """Windows için sürüm bilgisi dosyası oluştur"""
    if sys.platform != "win32":
        return
    major, minor, patch = VERSION.split(".")
    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f, flags=0x0, OS=0x40004,
    fileType=0x1, subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(u'040904B0', [
        StringValue(u'CompanyName',      u'SnapLoop'),
        StringValue(u'FileDescription',  u'SnapLoop Ekran Kaydedici'),
        StringValue(u'FileVersion',      u'{VERSION}'),
        StringValue(u'InternalName',     u'SnapLoop'),
        StringValue(u'ProductName',      u'SnapLoop'),
        StringValue(u'ProductVersion',   u'{VERSION}'),
      ])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open("version_info.txt", "w") as f:
        f.write(content)
    print("📄 version_info.txt oluşturuldu")


if __name__ == "__main__":
    install_pyinstaller()
    create_version_info()
    build()
