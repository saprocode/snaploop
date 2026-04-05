; SnapLoop Windows Installer
; NSIS ile kurulum paketi oluşturur
; Gereksinim: https://nsis.sourceforge.io

!define APP_NAME     "SnapLoop"
!define APP_VERSION  "2.1.0"
!define APP_EXE      "SnapLoop.exe"
!define INSTALL_DIR  "$PROGRAMFILES64\SnapLoop"

Name "${APP_NAME} ${APP_VERSION}"
OutFile "SnapLoop_Setup_${APP_VERSION}.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\SnapLoop" "Install_Dir"
RequestExecutionLevel admin
SetCompressor lzma

Icon "assets\icon.ico"
UninstallIcon "assets\icon.ico"

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING

; Sayfalar
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Turkish"

; ── Kurulum ───────────────────────────────────────────────────────────────────
Section "SnapLoop (zorunlu)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; Dosyaları kopyala
  File "dist\SnapLoop.exe"
  File "README.md"

  ; Kayıt defteri
  WriteRegStr HKLM "Software\SnapLoop" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop" \
              "DisplayName" "SnapLoop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop" \
              "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop" \
              "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop" \
              "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop" \
              "NoRepair" 1

  ; Kaldırıcı yaz
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Başlat menüsü
  CreateDirectory "$SMPROGRAMS\SnapLoop"
  CreateShortcut  "$SMPROGRAMS\SnapLoop\SnapLoop.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut  "$SMPROGRAMS\SnapLoop\Kaldır.lnk"   "$INSTDIR\Uninstall.exe"

  ; Masaüstü kısayolu
  CreateShortcut "$DESKTOP\SnapLoop.lnk" "$INSTDIR\${APP_EXE}"
SectionEnd

; ── Kaldırma ──────────────────────────────────────────────────────────────────
Section "Uninstall"
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir  "$INSTDIR"

  Delete "$SMPROGRAMS\SnapLoop\SnapLoop.lnk"
  Delete "$SMPROGRAMS\SnapLoop\Kaldır.lnk"
  RMDir  "$SMPROGRAMS\SnapLoop"
  Delete "$DESKTOP\SnapLoop.lnk"

  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SnapLoop"
  DeleteRegKey HKLM "Software\SnapLoop"
SectionEnd
