# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import shutil
from pathlib import Path

APP_NAME    = "SnapLoop"
MAIN_SCRIPT = "snaploop.py"
VERSION     = "2.0.0"

def run(cmd):
    print("\n> " + cmd + "\n")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("ERROR: Command failed: " + cmd)
        sys.exit(1)

def install_pyinstaller():
    print("Installing PyInstaller...")
    run(sys.executable + " -m pip install pyinstaller mss Pillow psutil --upgrade")

def build():
    platform = sys.platform
    print("Platform: " + platform)
    print("Python: " + sys.version)

    for d in ["build", "dist"]:
        if Path(d).exists():
            shutil.rmtree(d)
            print("Cleaned: " + d)

    args = [
        "--name=" + APP_NAME,
        "--onefile",
        "--windowed",
        "--clean",
        "--add-data=README.md" + os.pathsep + ".",
    ]

    if platform == "win32":
        icon_path = Path("icon.ico")
        if icon_path.exists():
            args.append("--icon=icon.ico")
        create_version_info()
        args.append("--version-file=version_info.txt")
    elif platform == "darwin":
        icon_path = Path("icon.icns")
        if icon_path.exists():
            args.append("--icon=icon.icns")
        args.append("--osx-bundle-identifier=com.snaploop.app")

    cmd = sys.executable + " -m PyInstaller " + " ".join(args) + " " + MAIN_SCRIPT
    run(cmd)

    dist = Path("dist")
    if platform == "win32":
        exe = dist / (APP_NAME + ".exe")
        if exe.exists():
            size = exe.stat().st_size / 1024 / 1024
            print("Done: dist/" + APP_NAME + ".exe  (" + str(round(size, 1)) + " MB)")
    elif platform == "darwin":
        app = dist / (APP_NAME + ".app")
        target = app if app.exists() else dist / APP_NAME
        print("Done: dist/" + target.name)
    else:
        exe = dist / APP_NAME
        if exe.exists():
            size = exe.stat().st_size / 1024 / 1024
            print("Done: dist/" + APP_NAME + "  (" + str(round(size, 1)) + " MB)")

    print("Output: " + str(dist.absolute()))


def create_version_info():
    major, minor, patch = VERSION.split(".")
    lines = [
        "VSVersionInfo(",
        "  ffi=FixedFileInfo(",
        "    filevers=(" + major + ", " + minor + ", " + patch + ", 0),",
        "    prodvers=(" + major + ", " + minor + ", " + patch + ", 0),",
        "    mask=0x3f, flags=0x0, OS=0x40004,",
        "    fileType=0x1, subtype=0x0,",
        "    date=(0, 0)",
        "  ),",
        "  kids=[",
        "    StringFileInfo([",
        "      StringTable(u'040904B0', [",
        "        StringValue(u'CompanyName',     u'SnapLoop'),",
        "        StringValue(u'FileDescription', u'SnapLoop Screen Recorder'),",
        "        StringValue(u'FileVersion',     u'" + VERSION + "'),",
        "        StringValue(u'InternalName',    u'SnapLoop'),",
        "        StringValue(u'ProductName',     u'SnapLoop'),",
        "        StringValue(u'ProductVersion',  u'" + VERSION + "'),",
        "      ])",
        "    ]),",
        "    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])",
        "  ]",
        ")",
    ]
    with open("version_info.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("Created: version_info.txt")


if __name__ == "__main__":
    install_pyinstaller()
    build()