"""
SnapLoop — Cross-Platform Ekran Kaydedici
Gereksinimler: pip install mss pillow screeninfo psutil
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import sys
import json
import zipfile
import smtplib
import shutil
import tempfile
import io
import subprocess
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
from pathlib import Path

try:
    from updater import run_update_check, CURRENT_VERSION as _UPD_VERSION
    HAS_UPDATER = True
except ImportError:
    HAS_UPDATER = False

try:
    import mss
    import mss.tools
    HAS_MSS = True
except ImportError:
    HAS_MSS = False

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# ─── Renk Paleti ──────────────────────────────────────────────────────────────
C = {
    "bg":        "#0d0d14",
    "surface":   "#14141f",
    "surface2":  "#1c1c2e",
    "border":    "#2a2a45",
    "accent":    "#00e5ff",
    "accent2":   "#7c3aed",
    "accent3":   "#f59e0b",
    "danger":    "#ef4444",
    "success":   "#10b981",
    "text":      "#e2e8f0",
    "muted":     "#64748b",
    "white":     "#ffffff",
}

FONT_MONO  = ("Courier New", 10)
FONT_MONO_S = ("Courier New", 9)
FONT_MAIN  = ("Segoe UI", 11) if sys.platform == "win32" else ("SF Pro Display", 11) if sys.platform == "darwin" else ("Ubuntu", 11)
FONT_BOLD  = ("Segoe UI", 11, "bold") if sys.platform == "win32" else ("SF Pro Display", 11, "bold") if sys.platform == "darwin" else ("Ubuntu", 11, "bold")
FONT_BIG   = ("Segoe UI", 18, "bold") if sys.platform == "win32" else ("SF Pro Display", 18, "bold") if sys.platform == "darwin" else ("Ubuntu", 18, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold") if sys.platform == "win32" else ("SF Pro Display", 14, "bold") if sys.platform == "darwin" else ("Ubuntu", 14, "bold")


def get_windows_list():
    """Tüm açık pencereleri listele (cross-platform)"""
    windows = []
    if sys.platform == "win32":
        try:
            import ctypes
            import ctypes.wintypes
            EnumWindows       = ctypes.windll.user32.EnumWindows
            EnumWindowsProc   = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            GetWindowText     = ctypes.windll.user32.GetWindowTextW
            GetWindowTextLen  = ctypes.windll.user32.GetWindowTextLengthW
            IsWindowVisible   = ctypes.windll.user32.IsWindowVisible
            GetWindowRect     = ctypes.windll.user32.GetWindowRect

            def enum_cb(hwnd, _):
                if IsWindowVisible(hwnd) and GetWindowTextLen(hwnd) > 0:
                    buf = ctypes.create_unicode_buffer(256)
                    GetWindowText(hwnd, buf, 256)
                    rect = ctypes.wintypes.RECT()
                    GetWindowRect(hwnd, ctypes.byref(rect))
                    w = rect.right  - rect.left
                    h = rect.bottom - rect.top
                    if w > 50 and h > 50:
                        windows.append({
                            "title": buf.value,
                            "hwnd":  hwnd,
                            "left":  rect.left, "top": rect.top,
                            "width": w, "height": h,
                        })
                return True
            EnumWindows(EnumWindowsProc(enum_cb), 0)
        except Exception:
            pass

    elif sys.platform == "darwin":
        try:
            script = 'tell application "System Events" to get name of every process whose background only is false'
            out = subprocess.check_output(["osascript", "-e", script], text=True).strip()
            for name in out.split(", "):
                if name:
                    windows.append({"title": name, "hwnd": name, "left":0,"top":0,"width":1920,"height":1080})
        except Exception:
            pass

    else:  # Linux
        try:
            out = subprocess.check_output(
                ["wmctrl", "-lG"], text=True, stderr=subprocess.DEVNULL
            ).strip()
            for line in out.splitlines():
                parts = line.split(None, 8)
                if len(parts) >= 9:
                    wid   = parts[0]
                    left  = int(parts[2])
                    top   = int(parts[3])
                    w     = int(parts[4])
                    h     = int(parts[5])
                    title = parts[8]
                    if w > 50 and h > 50 and title.strip():
                        windows.append({"title": title, "hwnd": wid,
                                        "left": left, "top": top,
                                        "width": w, "height": h})
        except Exception:
            pass

    return windows


def capture_window(win_info, quality=90, fmt="PNG"):
    """Belirli bir pencereyi yakala"""
    if not HAS_MSS or not HAS_PIL:
        return None
    try:
        with mss.mss() as sct:
            region = {
                "left":   win_info["left"],
                "top":    win_info["top"],
                "width":  win_info["width"],
                "height": win_info["height"],
            }
            shot = sct.grab(region)
            img  = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            buf  = io.BytesIO()
            if fmt.upper() == "JPEG":
                img.save(buf, format="JPEG", quality=quality, optimize=True)
            elif fmt.upper() == "WEBP":
                img.save(buf, format="WEBP", quality=quality)
            else:
                img.save(buf, format="PNG", compress_level=max(0, min(9, (100-quality)//11)))
            buf.seek(0)
            return buf.read()
    except Exception as e:
        print(f"[capture_window] {e}")
        return None


def capture_monitor(monitor_info, quality=90, fmt="PNG"):
    """Belirli bir monitörü yakala"""
    if not HAS_MSS or not HAS_PIL:
        return None
    try:
        with mss.mss() as sct:
            shot = sct.grab(monitor_info)
            img  = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            buf  = io.BytesIO()
            if fmt.upper() == "JPEG":
                img.save(buf, format="JPEG", quality=quality, optimize=True)
            elif fmt.upper() == "WEBP":
                img.save(buf, format="WEBP", quality=quality)
            else:
                img.save(buf, format="PNG", compress_level=max(0, min(9, (100-quality)//11)))
            buf.seek(0)
            return buf.read()
    except Exception as e:
        print(f"[capture_monitor] {e}")
        return None


# ─── Stil Yardımcıları ────────────────────────────────────────────────────────
def styled_btn(parent, text, cmd, color=None, width=None, height=32, font=None):
    c = color or C["accent2"]
    kw = dict(
        text=text, command=cmd,
        bg=c, fg=C["white"],
        activebackground=c, activeforeground=C["white"],
        relief="flat", cursor="hand2",
        font=font or FONT_BOLD,
        bd=0, highlightthickness=0,
    )
    if width:  kw["width"]  = width
    if height: kw["height"] = height
    b = tk.Button(parent, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(c)))
    b.bind("<Leave>", lambda e: b.config(bg=c))
    return b


def _lighten(hex_color):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = min(255, r + 30)
    g = min(255, g + 30)
    b = min(255, b + 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def styled_entry(parent, textvariable=None, width=None, placeholder=""):
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        bg=C["surface2"], fg=C["text"],
        insertbackground=C["accent"],
        relief="flat", bd=0,
        font=FONT_MONO,
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["accent"],
    )
    if width: e.config(width=width)
    return e


def styled_label(parent, text, size=11, color=None, bold=False):
    fw = "bold" if bold else "normal"
    font_name = "Courier New" if size <= 9 else ("Segoe UI" if sys.platform=="win32" else "Ubuntu")
    return tk.Label(
        parent, text=text,
        bg=C["surface"], fg=color or C["text"],
        font=(font_name, size, fw),
    )


def section_header(parent, text):
    f = tk.Frame(parent, bg=C["surface"])
    tk.Label(f, text=text.upper(), bg=C["surface"], fg=C["accent"],
             font=("Courier New", 9, "bold")).pack(side="left")
    tk.Frame(f, bg=C["border"], height=1).pack(side="left", fill="x", expand=True, padx=(8,0), pady=6)
    return f


# ═══════════════════════════════════════════════════════════════════════════════
class SnapLoop(tk.Tk):

    VERSION = "2.0.0"
    SAVE_DIR = Path.home() / "SnapLoop_Recordings"

    def __init__(self):
        super().__init__()
        self.title("SnapLoop — Ekran Kaydedici")
        self.geometry("900x760")
        self.minsize(860, 700)
        self.configure(bg=C["bg"])

        self.SAVE_DIR.mkdir(exist_ok=True)

        # ── State ──
        self.recording      = False
        self.paused         = False
        self.record_thread  = None
        self.frame_count    = 0
        self.total_bytes    = 0
        self.session_dir    = None
        self.session_frames = []
        self.elapsed_secs   = 0
        self._timer_job     = None

        # ── Settings vars ──
        self.var_interval    = tk.DoubleVar(value=2.0)
        self.var_duration    = tk.DoubleVar(value=0.0)
        self.var_quality     = tk.IntVar(value=85)
        self.var_format      = tk.StringVar(value="PNG")
        self.var_size_limit  = tk.DoubleVar(value=500.0)
        self.var_limit_en    = tk.BooleanVar(value=True)
        self.var_duration_en = tk.BooleanVar(value=False)
        self.var_target_type = tk.StringVar(value="monitor")  # monitor | window | all

        # mail
        self.var_mail_to     = tk.StringVar()
        self.var_mail_from   = tk.StringVar()
        self.var_mail_pass   = tk.StringVar()
        self.var_smtp_host   = tk.StringVar(value="smtp.gmail.com")
        self.var_smtp_port   = tk.IntVar(value=587)

        # monitor / window selections
        self.monitors      = []
        self.monitor_vars  = []
        self.windows_list  = []
        self.window_var    = tk.StringVar()

        self._build_ui()
        self._refresh_targets()
        self._load_recordings()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Uygulama açılınca 3 saniye sonra arka planda güncelleme kontrolü yap
        if HAS_UPDATER:
            self.after(3000, lambda: run_update_check(self, silent=True))

    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=C["bg"], pady=10)
        topbar.pack(fill="x", padx=20)

        # Logo
        logo_f = tk.Frame(topbar, bg=C["bg"])
        logo_f.pack(side="left")
        tk.Label(logo_f, text="⬡", bg=C["bg"], fg=C["accent"], font=("Courier New", 22)).pack(side="left")
        tk.Label(logo_f, text=" Snap", bg=C["bg"], fg=C["text"],  font=("Segoe UI" if sys.platform=="win32" else "Ubuntu", 18, "bold")).pack(side="left")
        tk.Label(logo_f, text="Loop", bg=C["bg"], fg=C["accent"], font=("Segoe UI" if sys.platform=="win32" else "Ubuntu", 18, "bold")).pack(side="left")
        tk.Label(logo_f, text=f" v{self.VERSION}", bg=C["bg"], fg=C["muted"], font=("Courier New", 9)).pack(side="left", pady=8)

        # Status
        self.status_frame = tk.Frame(topbar, bg=C["surface2"], padx=12, pady=5)
        self.status_frame.pack(side="right")
        self.status_dot = tk.Label(self.status_frame, text="●", bg=C["surface2"], fg=C["muted"], font=("Courier New", 10))
        self.status_dot.pack(side="left")
        self.status_lbl = tk.Label(self.status_frame, text="HAZIR", bg=C["surface2"], fg=C["muted"],
                                   font=("Courier New", 9, "bold"))
        self.status_lbl.pack(side="left", padx=(4,0))

        # Güncelleme kontrolü butonu
        if HAS_UPDATER:
            upd_btn = tk.Button(
                topbar, text="⟳ Güncelleme Kontrol Et",
                command=lambda: run_update_check(self, silent=False),
                bg=C["surface2"], fg=C["muted"],
                activebackground=C["surface2"], activeforeground=C["accent"],
                font=("Courier New", 8), relief="flat", cursor="hand2",
                bd=0, padx=8, pady=4,
            )
            upd_btn.pack(side="right", padx=(0, 10))

        sep = tk.Frame(self, bg=C["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(0,12))

        # Notebook (tabs)
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Custom.TNotebook", background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("Custom.TNotebook.Tab",
                        background=C["surface"], foreground=C["muted"],
                        padding=[16,8], borderwidth=0, font=("Courier New", 9, "bold"))
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", C["surface2"])],
                  foreground=[("selected", C["accent"])])
        style.configure("Custom.TFrame", background=C["bg"])

        self.nb = ttk.Notebook(self, style="Custom.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=20, pady=(0,20))

        self._tab_record   = tk.Frame(self.nb, bg=C["bg"])
        self._tab_sessions = tk.Frame(self.nb, bg=C["bg"])
        self._tab_mail     = tk.Frame(self.nb, bg=C["bg"])

        self.nb.add(self._tab_record,   text="  ◉  KAYIT  ")
        self.nb.add(self._tab_sessions, text="  ⊞  KAYITLAR  ")
        self.nb.add(self._tab_mail,     text="  ✉  MAİL  ")

        self._build_record_tab()
        self._build_sessions_tab()
        self._build_mail_tab()

    # ══════════════════════════════ KAYIT TABÜ ════════════════════════════════
    def _build_record_tab(self):
        p = self._tab_record
        # Two columns
        left  = tk.Frame(p, bg=C["bg"])
        right = tk.Frame(p, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0,8), pady=8)
        right.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        # ── LEFT: Hedef Seçimi ──────────────────────────────────────────────
        target_card = self._card(left, "HEDEF EKRAN / PENCERE")
        target_card.pack(fill="x", pady=(0,12))

        # Target type
        type_f = tk.Frame(target_card, bg=C["surface"])
        type_f.pack(fill="x", pady=(0,10))

        for val, lbl in [("all","Tüm Ekranlar"), ("monitor","Ekran Seç"), ("window","Pencere Seç")]:
            rb = tk.Radiobutton(type_f, text=lbl, variable=self.var_target_type, value=val,
                                bg=C["surface"], fg=C["text"],
                                selectcolor=C["surface2"], activebackground=C["surface"],
                                activeforeground=C["accent"], font=FONT_MAIN,
                                command=self._on_target_type_change)
            rb.pack(side="left", padx=(0,16))

        # Monitor listesi
        self.monitor_frame = tk.Frame(target_card, bg=C["surface"])
        self.monitor_frame.pack(fill="x")

        # Window listesi
        self.window_frame = tk.Frame(target_card, bg=C["surface"])

        refresh_btn = styled_btn(target_card, "↻  Hedefleri Yenile", self._refresh_targets,
                                 color=C["muted"], height=26)
        refresh_btn.pack(anchor="e", pady=(8,0))

        # ── LEFT: Zamanlama ─────────────────────────────────────────────────
        timing_card = self._card(left, "ZAMANLAMA")
        timing_card.pack(fill="x", pady=(0,12))

        row1 = tk.Frame(timing_card, bg=C["surface"])
        row1.pack(fill="x")

        tk.Label(row1, text="Aralık (saniye):", bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9)).grid(row=0,column=0,sticky="w",pady=3)
        iv = styled_entry(row1, textvariable=self.var_interval, width=8)
        iv.grid(row=0, column=1, sticky="w", padx=(8,0))

        # Duration toggle + entry
        dur_row = tk.Frame(timing_card, bg=C["surface"])
        dur_row.pack(fill="x", pady=(4,0))
        self._chk(dur_row, "Süre Limiti (sn):", self.var_duration_en).pack(side="left")
        de = styled_entry(dur_row, textvariable=self.var_duration, width=8)
        de.pack(side="left", padx=8)

        # ── RIGHT: Kalite & Format ──────────────────────────────────────────
        quality_card = self._card(right, "KALİTE & FORMAT")
        quality_card.pack(fill="x", pady=(0,12))

        # Format seçimi
        tk.Label(quality_card, text="Format:", bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9)).pack(anchor="w")
        fmt_f = tk.Frame(quality_card, bg=C["surface"])
        fmt_f.pack(fill="x", pady=(4,10))
        for fmt in ["PNG","JPEG","WEBP"]:
            rb = tk.Radiobutton(fmt_f, text=fmt, variable=self.var_format, value=fmt,
                                bg=C["surface"], fg=C["text"],
                                selectcolor=C["surface2"], activebackground=C["surface"],
                                activeforeground=C["accent"], font=FONT_MAIN)
            rb.pack(side="left", padx=(0,12))

        # Quality slider
        tk.Label(quality_card, text="Kalite:", bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9)).pack(anchor="w")
        q_row = tk.Frame(quality_card, bg=C["surface"])
        q_row.pack(fill="x", pady=(4,0))
        self.quality_val_lbl = tk.Label(q_row, text="85%", bg=C["surface"],
                                        fg=C["accent"], font=("Courier New",16,"bold"), width=5)
        self.quality_val_lbl.pack(side="left")
        slider_bg = tk.Frame(q_row, bg=C["surface2"], height=8, bd=0)
        slider_bg.pack(side="left", fill="x", expand=True, padx=(8,0), ipady=0)
        self.quality_slider = tk.Scale(
            q_row, variable=self.var_quality, from_=10, to=100,
            orient="horizontal", showvalue=False,
            bg=C["surface"], fg=C["accent"], troughcolor=C["surface2"],
            activebackground=C["accent"], highlightthickness=0, bd=0,
            command=self._on_quality_change, length=200,
        )
        self.quality_slider.pack(side="left", fill="x", expand=True)

        # Kalite ipucu
        self.quality_hint = tk.Label(quality_card, text="Denge: Hız/Boyut", bg=C["surface"],
                                     fg=C["muted"], font=("Courier New",8))
        self.quality_hint.pack(anchor="e")

        # ── RIGHT: Boyut Limiti ─────────────────────────────────────────────
        limit_card = self._card(right, "BOYUT LİMİTİ")
        limit_card.pack(fill="x", pady=(0,12))

        lim_row = tk.Frame(limit_card, bg=C["surface"])
        lim_row.pack(fill="x")
        self._chk(lim_row, "Limit Aktif:", self.var_limit_en).pack(side="left")
        le = styled_entry(lim_row, textvariable=self.var_size_limit, width=8)
        le.pack(side="left", padx=8)
        tk.Label(lim_row, text="MB", bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9)).pack(side="left")

        # Progress bar for size
        self.size_bar_frame = tk.Frame(limit_card, bg=C["surface"])
        self.size_bar_frame.pack(fill="x", pady=(8,0))
        tk.Label(self.size_bar_frame, text="Kullanılan:", bg=C["surface"],
                 fg=C["muted"], font=("Courier New",8)).pack(anchor="w")
        bar_bg = tk.Frame(self.size_bar_frame, bg=C["border"], height=6)
        bar_bg.pack(fill="x", pady=(2,2))
        self.size_bar = tk.Frame(bar_bg, bg=C["success"], height=6)
        self.size_bar.place(x=0, y=0, relheight=1, relwidth=0)
        self.size_lbl = tk.Label(self.size_bar_frame, text="0.0 / 500.0 MB",
                                 bg=C["surface"], fg=C["muted"], font=("Courier New",8))
        self.size_lbl.pack(anchor="e")

        # ── BOTTOM: Kontrol paneli ──────────────────────────────────────────
        ctrl = tk.Frame(p, bg=C["bg"])
        ctrl.pack(side="bottom", fill="x", padx=0, pady=(0,12))

        # Timer + frame counter
        info_f = tk.Frame(ctrl, bg=C["surface2"], padx=16, pady=10)
        info_f.pack(fill="x", padx=0, pady=(0,10))

        self.timer_lbl = tk.Label(info_f, text="00:00:00", bg=C["surface2"],
                                  fg=C["accent"], font=("Courier New",26,"bold"))
        self.timer_lbl.pack(side="left")

        stats_f = tk.Frame(info_f, bg=C["surface2"])
        stats_f.pack(side="left", padx=24)
        self.frame_lbl = tk.Label(stats_f, text="0 kare", bg=C["surface2"],
                                  fg=C["text"], font=("Courier New",10))
        self.frame_lbl.pack(anchor="w")
        self.fps_lbl = tk.Label(stats_f, text="—", bg=C["surface2"],
                                fg=C["muted"], font=("Courier New",9))
        self.fps_lbl.pack(anchor="w")

        # Buttons
        btn_f = tk.Frame(ctrl, bg=C["bg"])
        btn_f.pack(fill="x")

        self.btn_start = styled_btn(btn_f, "▶  KAYDI BAŞLAT",
                                    self._start_recording, color=C["success"], height=40)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0,6))

        self.btn_pause = styled_btn(btn_f, "⏸  DURAKLAT",
                                    self._pause_recording, color=C["accent3"], height=40)
        self.btn_pause.pack(side="left", fill="x", expand=True, padx=(0,6))
        self.btn_pause.config(state="disabled")

        self.btn_stop = styled_btn(btn_f, "⏹  DURDUR",
                                   self._stop_recording, color=C["danger"], height=40)
        self.btn_stop.pack(side="left", fill="x", expand=True)
        self.btn_stop.config(state="disabled")

    # ══════════════════════════ KAYITLAR TABÜ ═════════════════════════════════
    def _build_sessions_tab(self):
        p = self._tab_sessions

        top = tk.Frame(p, bg=C["bg"])
        top.pack(fill="x", pady=(12,8))
        tk.Label(top, text="Tamamlanan Kayıtlar", bg=C["bg"], fg=C["text"],
                 font=FONT_TITLE).pack(side="left")
        styled_btn(top, "↻ Yenile", self._load_recordings,
                   color=C["surface2"], height=28).pack(side="right")

        # Listbox ile çerçeveleme
        list_frame = tk.Frame(p, bg=C["surface"], bd=1, relief="flat")
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=C["surface2"], troughcolor=C["border"],
                                  activebackground=C["accent"])
        scrollbar.pack(side="right", fill="y")

        self.recordings_lb = tk.Listbox(
            list_frame,
            bg=C["surface"], fg=C["text"],
            selectbackground=C["accent2"], selectforeground=C["white"],
            font=("Courier New", 10),
            borderwidth=0, highlightthickness=0,
            yscrollcommand=scrollbar.set,
            activestyle="none",
        )
        self.recordings_lb.pack(fill="both", expand=True)
        scrollbar.config(command=self.recordings_lb.yview)
        self.recordings_lb.bind("<<ListboxSelect>>", self._on_recording_select)

        # Action buttons
        action_f = tk.Frame(p, bg=C["bg"])
        action_f.pack(fill="x", pady=(10,0))

        self.btn_download = styled_btn(action_f, "⬇  İNDİR (ZIP)",
                                       self._download_selected, color=C["accent2"], height=36)
        self.btn_download.pack(side="left", padx=(0,8))
        self.btn_download.config(state="disabled")

        self.btn_send_mail = styled_btn(action_f, "✉  MAİL GÖNDER",
                                        self._send_mail_selected, color=C["accent3"], height=36)
        self.btn_send_mail.pack(side="left", padx=(0,8))
        self.btn_send_mail.config(state="disabled")

        self.btn_delete_rec = styled_btn(action_f, "✕  SİL",
                                         self._delete_selected, color=C["danger"], height=36)
        self.btn_delete_rec.pack(side="left")
        self.btn_delete_rec.config(state="disabled")

        # Info label
        self.rec_info_lbl = tk.Label(p, text="", bg=C["bg"], fg=C["muted"],
                                     font=("Courier New",9))
        self.rec_info_lbl.pack(anchor="w", pady=(6,0))

    # ══════════════════════════ MAİL TABÜ ═════════════════════════════════════
    def _build_mail_tab(self):
        p = self._tab_mail

        card = self._card(p, "SMTP AYARLARI")
        card.pack(fill="x", padx=0, pady=(12,0))
        card.config(bg=C["surface"])

        def row(label, var, show=""):
            f = tk.Frame(card, bg=C["surface"])
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label, bg=C["surface"], fg=C["muted"],
                     font=("Courier New",9), width=14, anchor="w").pack(side="left")
            e = styled_entry(f, textvariable=var)
            e.pack(side="left", fill="x", expand=True)
            if show: e.config(show=show)

        row("Gönderen:",     self.var_mail_from)
        row("Şifre:",        self.var_mail_pass,  show="●")
        row("Alıcı:",        self.var_mail_to)
        row("SMTP Host:",    self.var_smtp_host)

        port_f = tk.Frame(card, bg=C["surface"])
        port_f.pack(fill="x", pady=3)
        tk.Label(port_f, text="SMTP Port:", bg=C["surface"], fg=C["muted"],
                 font=("Courier New",9), width=14, anchor="w").pack(side="left")
        styled_entry(port_f, textvariable=self.var_smtp_port, width=8).pack(side="left")

        hint = tk.Label(p, text="⚠  Gmail kullanıcıları için 'Uygulama Şifresi' gereklidir.",
                        bg=C["bg"], fg=C["accent3"], font=("Courier New",9))
        hint.pack(anchor="w", pady=(10,0))

        save_btn = styled_btn(p, "Ayarları Kaydet", self._save_mail_settings,
                              color=C["success"], height=32)
        save_btn.pack(anchor="w", pady=(10,0))

        # Ayarları yükle
        self._load_mail_settings()

    # ─────────────────────────────────────────────────────────────────────────
    def _card(self, parent, title=""):
        outer = tk.Frame(parent, bg=C["surface"], padx=14, pady=12,
                         highlightbackground=C["border"], highlightthickness=1)
        if title:
            tk.Label(outer, text=title, bg=C["surface"], fg=C["accent"],
                     font=("Courier New",8,"bold")).pack(anchor="w", pady=(0,8))
        return outer

    def _chk(self, parent, text, var):
        return tk.Checkbutton(
            parent, text=text, variable=var,
            bg=parent.cget("bg"), fg=C["text"],
            selectcolor=C["surface2"],
            activebackground=parent.cget("bg"),
            activeforeground=C["accent"],
            font=FONT_MAIN,
        )

    # ─────────────────────────────────────────────────────────────────────────
    def _on_target_type_change(self):
        t = self.var_target_type.get()
        if t == "monitor":
            self.monitor_frame.pack(fill="x")
            self.window_frame.pack_forget()
        elif t == "window":
            self.monitor_frame.pack_forget()
            self.window_frame.pack(fill="x")
        else:
            self.monitor_frame.pack_forget()
            self.window_frame.pack_forget()

    def _refresh_targets(self):
        # Monitörler
        for w in self.monitor_frame.winfo_children():
            w.destroy()
        self.monitor_vars = []

        if HAS_MSS:
            with mss.mss() as sct:
                self.monitors = list(sct.monitors)[1:]  # [0] = tüm ekran birleşimi
                for i, m in enumerate(self.monitors):
                    var = tk.BooleanVar(value=(i == 0))
                    self.monitor_vars.append(var)
                    label = f"Ekran {i+1}  ({m['width']}×{m['height']})  Pos: {m['left']},{m['top']}"
                    cb = tk.Checkbutton(
                        self.monitor_frame, text=label, variable=var,
                        bg=C["surface"], fg=C["text"],
                        selectcolor=C["surface2"],
                        activebackground=C["surface"],
                        activeforeground=C["accent"],
                        font=FONT_MAIN,
                    )
                    cb.pack(anchor="w", pady=2)
        else:
            tk.Label(self.monitor_frame, text="mss kütüphanesi bulunamadı!",
                     bg=C["surface"], fg=C["danger"], font=FONT_MAIN).pack()

        # Pencereler
        for w in self.window_frame.winfo_children():
            w.destroy()
        self.windows_list = get_windows_list()

        if self.windows_list:
            tk.Label(self.window_frame, text="Pencere Seç:", bg=C["surface"],
                     fg=C["muted"], font=("Courier New",9)).pack(anchor="w", pady=(0,4))
            win_titles = [w["title"][:70] for w in self.windows_list]
            combo = ttk.Combobox(self.window_frame, textvariable=self.window_var,
                                 values=win_titles, font=("Courier New",10),
                                 state="readonly", width=50)
            combo.pack(fill="x")
            if win_titles:
                combo.current(0)
                self.window_var.set(win_titles[0])
        else:
            tk.Label(self.window_frame,
                     text="Pencere listesi alınamadı.\n(wmctrl yüklü değil veya desteklenmiyor)",
                     bg=C["surface"], fg=C["danger"], font=FONT_MAIN).pack()

        self._on_target_type_change()

    # ─────────────────────────────────────────────────────────────────────────
    def _on_quality_change(self, val=None):
        q = self.var_quality.get()
        self.quality_val_lbl.config(text=f"{q}%")
        if q < 40:
            hint = "Küçük boyut, düşük kalite"
            c = C["danger"]
        elif q < 70:
            hint = "Denge: Hız/Boyut"
            c = C["accent3"]
        else:
            hint = "Yüksek kalite, büyük boyut"
            c = C["success"]
        self.quality_hint.config(text=hint, fg=c)

    # ─────────────────────────────────────────────────────────────────────────
    def _start_recording(self):
        if not HAS_MSS or not HAS_PIL:
            messagebox.showerror("Hata", "mss ve Pillow kütüphaneleri gereklidir!\npip install mss pillow")
            return

        interval = self.var_interval.get()
        if interval <= 0:
            messagebox.showerror("Hata", "Aralık 0'dan büyük olmalı!")
            return

        # Session dizini
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir    = self.SAVE_DIR / f"session_{ts}"
        self.session_dir.mkdir(exist_ok=True)
        self.session_frames = []
        self.frame_count    = 0
        self.total_bytes    = 0
        self.elapsed_secs   = 0
        self.recording      = True
        self.paused         = False

        # Meta
        self._session_meta = {
            "started":  ts,
            "interval": interval,
            "format":   self.var_format.get(),
            "quality":  self.var_quality.get(),
            "target":   self.var_target_type.get(),
        }

        self._update_status("KAYIT", C["success"])
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_stop.config(state="normal")

        self._update_timer()
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

    def _record_loop(self):
        interval = self.var_interval.get()
        duration = self.var_duration.get() if self.var_duration_en.get() else 0
        fmt      = self.var_format.get()
        quality  = self.var_quality.get()
        target   = self.var_target_type.get()

        start_time = time.time()

        while self.recording:
            if self.paused:
                time.sleep(0.2)
                continue

            # Süre limiti
            if duration > 0 and (time.time() - start_time) >= duration:
                self.after(0, self._auto_stop, "Süre Limiti Doldu")
                return

            # Boyut limiti
            if self.var_limit_en.get():
                limit_mb = self.var_size_limit.get()
                if (self.total_bytes / (1024*1024)) >= limit_mb:
                    self.after(0, self._auto_stop, "Boyut Limiti Aşıldı")
                    return

            # Ekran görüntüsü al
            images = []
            if target == "all":
                with mss.mss() as sct:
                    for m in sct.monitors[1:]:
                        data = capture_monitor(m, quality, fmt)
                        if data:
                            images.append((f"all_mon{sct.monitors[1:].index(m)+1}", data))
            elif target == "monitor":
                for i, (m, var) in enumerate(zip(self.monitors, self.monitor_vars)):
                    if var.get():
                        data = capture_monitor(m, quality, fmt)
                        if data:
                            images.append((f"mon{i+1}", data))
            elif target == "window":
                sel = self.window_var.get()
                win_info = next((w for w in self.windows_list if w["title"][:70] == sel), None)
                if win_info:
                    data = capture_window(win_info, quality, fmt)
                    if data:
                        images.append(("win", data))

            if images:
                self.frame_count += 1
                ext = fmt.lower() if fmt != "JPEG" else "jpg"
                ts2 = datetime.now().strftime("%H-%M-%S_%f")
                for suffix, data in images:
                    fname = f"frame_{self.frame_count:05d}_{ts2}_{suffix}.{ext}"
                    fpath = self.session_dir / fname
                    with open(fpath, "wb") as f:
                        f.write(data)
                    self.total_bytes += len(data)
                    self.session_frames.append(str(fpath))

                self.after(0, self._update_stats)

            time.sleep(interval)

    def _update_stats(self):
        self.frame_lbl.config(text=f"{self.frame_count} kare")
        mb = self.total_bytes / (1024*1024)
        limit_mb = self.var_size_limit.get() if self.var_limit_en.get() else max(mb*2, 100)
        ratio = min(mb / limit_mb, 1.0) if limit_mb > 0 else 0
        color = C["success"] if ratio < 0.7 else C["accent3"] if ratio < 0.9 else C["danger"]
        self.size_bar.config(bg=color)
        self.size_bar.place(relwidth=ratio)
        self.size_lbl.config(text=f"{mb:.1f} / {self.var_size_limit.get():.0f} MB")
        interval = self.var_interval.get()
        if interval > 0:
            self.fps_lbl.config(text=f"1 kare / {interval}s  |  {mb:.2f} MB")

    def _update_timer(self):
        if self.recording and not self.paused:
            self.elapsed_secs += 1
        h = self.elapsed_secs // 3600
        m = (self.elapsed_secs % 3600) // 60
        s = self.elapsed_secs % 60
        self.timer_lbl.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        if self.recording:
            self._timer_job = self.after(1000, self._update_timer)

    def _pause_recording(self):
        if not self.recording: return
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.config(text="▶  DEVAM ET")
            self._update_status("DURAKLATILDI", C["accent3"])
        else:
            self.btn_pause.config(text="⏸  DURAKLAT")
            self._update_status("KAYIT", C["success"])

    def _stop_recording(self):
        self.recording = False
        if self._timer_job:
            self.after_cancel(self._timer_job)
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸  DURAKLAT")
        self.btn_stop.config(state="disabled")
        self._update_status("HAZIR", C["muted"])

        if self.session_frames:
            threading.Thread(target=self._finalize_session, daemon=True).start()
        else:
            messagebox.showinfo("Bilgi", "Hiç kare kaydedilmedi.")

    def _auto_stop(self, reason):
        messagebox.showinfo("Kayıt Durdu", f"Kayıt otomatik durduruldu:\n{reason}")
        self._stop_recording()

    def _finalize_session(self):
        self._update_status("ZIP'LENİYOR…", C["accent"])
        zip_name = f"{self.session_dir.name}.zip"
        zip_path = self.SAVE_DIR / zip_name

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Meta
            meta_str = json.dumps(self._session_meta, indent=2, ensure_ascii=False)
            zf.writestr("meta.json", meta_str)
            # Kareler
            for fpath in self.session_frames:
                zf.write(fpath, Path(fpath).name)

        # Orijinal klasörü sil
        shutil.rmtree(self.session_dir, ignore_errors=True)

        self.after(0, self._update_status, "HAZIR", C["muted"])
        self.after(0, self._load_recordings)
        self.after(0, lambda: messagebox.showinfo(
            "Kayıt Tamamlandı",
            f"✓  {self.frame_count} kare kaydedildi\n"
            f"📁  {zip_name}\n"
            f"💾  {os.path.getsize(zip_path)/1024/1024:.2f} MB"
        ))

    # ─────────────────────────────────────────────────────────────────────────
    def _update_status(self, text, color):
        self.status_dot.config(fg=color)
        self.status_lbl.config(text=text, fg=color)

    # ─────────────────────────────────────────────────────────────────────────
    def _load_recordings(self):
        self.recordings_lb.delete(0, "end")
        zips = sorted(self.SAVE_DIR.glob("*.zip"), reverse=True)
        for z in zips:
            sz = z.stat().st_size / 1024 / 1024
            self.recordings_lb.insert("end", f"  {z.name}   —   {sz:.2f} MB")
        if not zips:
            self.recordings_lb.insert("end", "  Henüz kayıt yok.")

    def _on_recording_select(self, event=None):
        sel = self.recordings_lb.curselection()
        has = bool(sel)
        st = "normal" if has else "disabled"
        self.btn_download.config(state=st)
        self.btn_send_mail.config(state=st)
        self.btn_delete_rec.config(state=st)
        if has:
            idx = sel[0]
            zips = sorted(self.SAVE_DIR.glob("*.zip"), reverse=True)
            if idx < len(zips):
                z = zips[idx]
                sz = z.stat().st_size / 1024/1024
                try:
                    with zipfile.ZipFile(z) as zf:
                        names = zf.namelist()
                    frames = [n for n in names if n != "meta.json"]
                    self.rec_info_lbl.config(
                        text=f"  Dosya: {z.name}  |  {sz:.2f} MB  |  {len(frames)} kare"
                    )
                except Exception:
                    self.rec_info_lbl.config(text=f"  {z.name}  |  {sz:.2f} MB")

    def _get_selected_zip(self):
        sel = self.recordings_lb.curselection()
        if not sel: return None
        idx  = sel[0]
        zips = sorted(self.SAVE_DIR.glob("*.zip"), reverse=True)
        if idx < len(zips):
            return zips[idx]
        return None

    def _download_selected(self):
        z = self._get_selected_zip()
        if not z: return
        dest = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP Dosyaları","*.zip")],
            initialfile=z.name,
        )
        if dest:
            shutil.copy2(z, dest)
            messagebox.showinfo("Başarılı", f"Kaydedildi:\n{dest}")

    def _delete_selected(self):
        z = self._get_selected_zip()
        if not z: return
        if messagebox.askyesno("Sil", f"'{z.name}' silinsin mi?"):
            z.unlink()
            self._load_recordings()
            self.rec_info_lbl.config(text="")
            for btn in [self.btn_download, self.btn_send_mail, self.btn_delete_rec]:
                btn.config(state="disabled")

    def _send_mail_selected(self):
        z = self._get_selected_zip()
        if not z: return

        to   = self.var_mail_to.get().strip()
        frm  = self.var_mail_from.get().strip()
        pwd  = self.var_mail_pass.get()
        host = self.var_smtp_host.get().strip()
        port = self.var_smtp_port.get()

        if not all([to, frm, pwd, host]):
            messagebox.showerror("Hata", "Lütfen Mail sekmesinden SMTP ayarlarını doldurun!")
            self.nb.select(2)
            return

        def send():
            try:
                msg = MIMEMultipart()
                msg["From"]    = frm
                msg["To"]      = to
                msg["Subject"] = f"SnapLoop Kayıt: {z.name}"
                msg.attach(MIMEText(
                    f"SnapLoop ekran kaydı ekte gönderilmiştir.\n\nDosya: {z.name}\n"
                    f"Boyut: {z.stat().st_size/1024/1024:.2f} MB",
                    "plain", "utf-8"
                ))
                with open(z, "rb") as f:
                    part = MIMEBase("application", "zip")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=z.name)
                    msg.attach(part)

                with smtplib.SMTP(host, port) as srv:
                    srv.ehlo()
                    srv.starttls()
                    srv.login(frm, pwd)
                    srv.send_message(msg)

                self.after(0, lambda: messagebox.showinfo("Gönderildi", f"Mail başarıyla gönderildi!\nAlıcı: {to}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Mail Hatası", str(e)))

        self._update_status("GÖNDERILIYOR…", C["accent3"])
        threading.Thread(target=send, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    def _save_mail_settings(self):
        cfg = {
            "mail_from":  self.var_mail_from.get(),
            "mail_to":    self.var_mail_to.get(),
            "smtp_host":  self.var_smtp_host.get(),
            "smtp_port":  self.var_smtp_port.get(),
        }
        cfg_path = self.SAVE_DIR / "mail_config.json"
        with open(cfg_path, "w") as f:
            json.dump(cfg, f, indent=2)
        messagebox.showinfo("Kaydedildi", "Mail ayarları kaydedildi.\n(Şifre güvenlik nedeniyle saklanmaz.)")

    def _load_mail_settings(self):
        cfg_path = self.SAVE_DIR / "mail_config.json"
        if cfg_path.exists():
            try:
                with open(cfg_path) as f:
                    cfg = json.load(f)
                self.var_mail_from.set(cfg.get("mail_from",""))
                self.var_mail_to.set(cfg.get("mail_to",""))
                self.var_smtp_host.set(cfg.get("smtp_host","smtp.gmail.com"))
                self.var_smtp_port.set(cfg.get("smtp_port",587))
            except Exception:
                pass

    # ─────────────────────────────────────────────────────────────────────────
    def _on_close(self):
        if self.recording:
            if not messagebox.askyesno("Çıkış", "Kayıt devam ediyor. Durdurup çıkılsın mı?"):
                return
            self._stop_recording()
            time.sleep(0.5)
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if not HAS_MSS:
        print("HATA: 'mss' kütüphanesi bulunamadı. Lütfen: pip install mss")
    if not HAS_PIL:
        print("HATA: 'Pillow' kütüphanesi bulunamadı. Lütfen: pip install pillow")

    app = SnapLoop()
    app.mainloop()
