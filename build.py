# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import shutil
from pathlib import Path

APP_NAME    = "SnapLoop"
MAIN_SCRIPT = "snaploop.py"
VERSION     = "2.1.0"

def run(cmd):
    print("\n> " + cmd + "\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("ERROR: " + cmd)
        sys.exit(1)

def create_version_info():
    major, minor, patch = VERSION.split(".")
    content = "\n".join([
        "VSVersionInfo(",
        "  ffi=FixedFileInfo(",
        "    filevers=(" + major + ", " + minor + ", " + patch + ", 0),",
        "    prodvers=(" + major + ", " + minor + ", " + patch + ", 0),",
        "    mask=0x3f,",
        "    flags=0x0,",
        "    OS=0x40004,",
        "    fileType=0x1,",
        "    subtype=0x0,",
        "    date=(0, 0)",
        "  ),",
        "  kids=[",
        "    StringFileInfo(",
        "      [",
        "      StringTable(",
        "        u'040904B0',",
        "        [StringStruct(u'CompanyName', u'SnapLoop'),",
        "        StringStruct(u'FileDescription', u'SnapLoop Screen Recorder'),",
        "        StringStruct(u'FileVersion', u'" + VERSION + "'),",
        "        StringStruct(u'InternalName', u'SnapLoop'),",
        "        StringStruct(u'LegalCopyright', u'Copyright 2024'),",
        "        StringStruct(u'OriginalFilename', u'SnapLoop.exe'),",
        "        StringStruct(u'ProductName', u'SnapLoop'),",
        "        StringStruct(u'ProductVersion', u'" + VERSION + "')])",
        "      ]",
        "    ),",
        "    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])",
        "  ]",
        ")",
    ])
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write(content + "\n")
    print("Created version_info.txt")

def build():
    platform = sys.platform
    print("Platform: " + platform)

    for d in ["build", "dist"]:
        if Path(d).exists():
            shutil.rmtree(d)

    args = [
        "--name=" + APP_NAME,
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
    ]

    if Path("updater.py").exists():
        args.append("--add-data=updater.py" + os.pathsep + ".")
        
    if Path("assets").exists():
        args.append("--add-data=assets" + os.pathsep + "assets")

    if platform == "win32":
        if Path("assets/icon.ico").exists():
            args.append("--icon=assets/icon.ico")
        create_version_info()
        args.append("--version-file=version_info.txt")
    elif platform == "darwin":
        if Path("assets/icon.icns").exists():
            args.append("--icon=assets/icon.icns")
        args.append("--osx-bundle-identifier=com.snaploop.app")

    cmd = sys.executable + " -m PyInstaller " + " ".join(args) + " " + MAIN_SCRIPT
    run(cmd)

    dist = Path("dist")
    if platform == "win32":
        exe = dist / (APP_NAME + ".exe")
        if exe.exists():
            size = round(exe.stat().st_size / 1024 / 1024, 1)
            print("Done: dist/" + APP_NAME + ".exe (" + str(size) + " MB)")
    elif platform == "darwin":
        app = dist / (APP_NAME + ".app")
        target = app if app.exists() else dist / APP_NAME
        print("Done: dist/" + target.name)
    else:
        exe = dist / APP_NAME
        if exe.exists():
            size = round(exe.stat().st_size / 1024 / 1024, 1)
            print("Done: dist/" + APP_NAME + " (" + str(size) + " MB)")

if __name__ == "__main__":
    run(sys.executable + " -m pip install pyinstaller mss Pillow psutil --upgrade -q")
    build()
