"""
SnapLoop — Otomatik Güncelleme Modülü
GitHub Releases API üzerinden güncelleme kontrolü yapar.
"""

import threading
import sys
import os
import json
import tempfile
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


# ── Sabitler ──────────────────────────────────────────────────────────────────
CURRENT_VERSION   = "2.0.0"
GITHUB_OWNER      = "KULLANICI_ADIN"   # ← GitHub kullanıcı adını yaz
GITHUB_REPO       = "snaploop"         # ← Repo adını yaz
RELEASES_API_URL  = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
UPDATE_CHECK_URL  = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/main/version.json"

# Renk paleti (ana uygulamayla aynı)
C = {
    "bg":       "#0d0d14",
    "surface":  "#14141f",
    "surface2": "#1c1c2e",
    "border":   "#2a2a45",
    "accent":   "#00e5ff",
    "accent2":  "#7c3aed",
    "accent3":  "#f59e0b",
    "danger":   "#ef4444",
    "success":  "#10b981",
    "text":     "#e2e8f0",
    "muted":    "#64748b",
    "white":    "#ffffff",
}


def version_tuple(v: str):
    """'2.1.0' → (2, 1, 0)"""
    try:
        return tuple(int(x) for x in v.lstrip("v").split("."))
    except Exception:
        return (0, 0, 0)


def check_for_update() -> dict | None:
    """
    GitHub Releases API'den son sürümü kontrol et.
    Yeni sürüm varsa bilgi dict'i döner, yoksa None.
    """
    try:
        req = urllib.request.Request(
            RELEASES_API_URL,
            headers={
                "Accept":     "application/vnd.github+json",
                "User-Agent": f"SnapLoop/{CURRENT_VERSION}",
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        latest_version = data.get("tag_name", "").lstrip("v")
        if not latest_version:
            return None

        if version_tuple(latest_version) <= version_tuple(CURRENT_VERSION):
            return None  # Güncel

        # Platform için doğru asset'i bul
        platform_asset = _find_asset(data.get("assets", []))

        return {
            "version":      latest_version,
            "release_name": data.get("name", f"v{latest_version}"),
            "notes":        data.get("body", "").strip()[:500],
            "html_url":     data.get("html_url", ""),
            "asset":        platform_asset,
        }

    except Exception as e:
        print(f"[Güncelleme kontrolü] {e}")
        return None


def _find_asset(assets: list) -> dict | None:
    """Platform için uygun kurulum dosyasını bul."""
    platform = sys.platform

    if platform == "win32":
        keywords = ["Setup", ".exe"]
    elif platform == "darwin":
        keywords = [".dmg"]
    else:
        keywords = [".deb", "linux", "Linux"]

    for keyword in keywords:
        for asset in assets:
            name = asset.get("name", "")
            if keyword.lower() in name.lower():
                return {
                    "name":         name,
                    "download_url": asset.get("browser_download_url", ""),
                    "size_mb":      round(asset.get("size", 0) / 1024 / 1024, 1),
                }

    # Hiç bulunamazsa ilk asset'i ver
    if assets:
        a = assets[0]
        return {
            "name":         a.get("name", ""),
            "download_url": a.get("browser_download_url", ""),
            "size_mb":      round(a.get("size", 0) / 1024 / 1024, 1),
        }
    return None


# ─────────────────────────────────────────────────────────────────────────────
class UpdateDialog(tk.Toplevel):
    """Güncelleme bildirimi penceresi."""

    def __init__(self, parent, update_info: dict):
        super().__init__(parent)
        self.update_info = update_info
        self.parent      = parent
        self._download_thread = None
        self._cancelled  = False

        self.title("Güncelleme Mevcut")
        self.geometry("520x420")
        self.resizable(False, False)
        self.configure(bg=C["bg"])
        self.transient(parent)
        self.grab_set()

        # Ortala
        self.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width()  // 2 - 260
        py = parent.winfo_y() + parent.winfo_height() // 2 - 210
        self.geometry(f"+{px}+{py}")

        self._build()

    def _build(self):
        info = self.update_info

        # Başlık
        header = tk.Frame(self, bg=C["surface2"], pady=16)
        header.pack(fill="x")

        tk.Label(header, text="⬆  Yeni Sürüm Mevcut!",
                 bg=C["surface2"], fg=C["accent"],
                 font=("Courier New", 14, "bold")).pack()

        ver_f = tk.Frame(header, bg=C["surface2"])
        ver_f.pack(pady=(6,0))
        tk.Label(ver_f, text=f"v{CURRENT_VERSION}",
                 bg=C["surface2"], fg=C["muted"],
                 font=("Courier New", 11)).pack(side="left")
        tk.Label(ver_f, text="  →  ",
                 bg=C["surface2"], fg=C["muted"],
                 font=("Courier New", 11)).pack(side="left")
        tk.Label(ver_f, text=f"v{info['version']}",
                 bg=C["surface2"], fg=C["success"],
                 font=("Courier New", 13, "bold")).pack(side="left")

        # Release notları
        body = tk.Frame(self, bg=C["bg"], padx=20, pady=14)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Sürüm Notları:", bg=C["bg"], fg=C["muted"],
                 font=("Courier New", 9, "bold")).pack(anchor="w")

        notes_frame = tk.Frame(body, bg=C["surface"], padx=10, pady=8)
        notes_frame.pack(fill="both", expand=True, pady=(4,0))

        notes_text = tk.Text(notes_frame, bg=C["surface"], fg=C["text"],
                             font=("Courier New", 9),
                             wrap="word", borderwidth=0, highlightthickness=0,
                             height=6)
        notes_text.pack(fill="both", expand=True)
        notes = info.get("notes") or "Hata düzeltmeleri ve iyileştirmeler."
        notes_text.insert("1.0", notes)
        notes_text.config(state="disabled")

        # Asset bilgisi
        asset = info.get("asset")
        if asset:
            tk.Label(body,
                     text=f"📦  {asset['name']}  —  {asset['size_mb']} MB",
                     bg=C["bg"], fg=C["muted"],
                     font=("Courier New", 9)).pack(anchor="w", pady=(8,0))

        # Progress bar (gizli başlar)
        self.progress_frame = tk.Frame(body, bg=C["bg"])
        self.progress_frame.pack(fill="x", pady=(6,0))

        self.progress_lbl = tk.Label(self.progress_frame, text="",
                                     bg=C["bg"], fg=C["accent"],
                                     font=("Courier New", 9))
        self.progress_lbl.pack(anchor="w")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Update.Horizontal.TProgressbar",
                        troughcolor=C["surface2"],
                        background=C["accent"],
                        borderwidth=0)
        self.progressbar = ttk.Progressbar(
            self.progress_frame,
            style="Update.Horizontal.TProgressbar",
            mode="determinate", maximum=100, value=0,
        )

        # Butonlar
        btn_f = tk.Frame(self, bg=C["bg"], padx=20, pady=14)
        btn_f.pack(fill="x")

        self.btn_update = tk.Button(
            btn_f, text="⬇  Güncelle ve Kur",
            command=self._start_download,
            bg=C["success"], fg=C["white"],
            activebackground=C["success"], activeforeground=C["white"],
            font=("Courier New", 10, "bold"),
            relief="flat", cursor="hand2", height=2,
        )
        self.btn_update.pack(side="left", fill="x", expand=True, padx=(0,8))

        # Asset yoksa tarayıcıda aç
        if not asset or not asset.get("download_url"):
            self.btn_update.config(text="🌐  Releases Sayfasını Aç",
                                   command=self._open_browser)

        self.btn_skip = tk.Button(
            btn_f, text="Şimdi Değil",
            command=self.destroy,
            bg=C["surface2"], fg=C["muted"],
            activebackground=C["surface2"], activeforeground=C["text"],
            font=("Courier New", 10),
            relief="flat", cursor="hand2", height=2,
        )
        self.btn_skip.pack(side="left", padx=(0,8))

        self.btn_skip_ver = tk.Button(
            btn_f, text="Bu Sürümü Atla",
            command=self._skip_version,
            bg=C["surface2"], fg=C["muted"],
            activebackground=C["surface2"], activeforeground=C["danger"],
            font=("Courier New", 10),
            relief="flat", cursor="hand2", height=2,
        )
        self.btn_skip_ver.pack(side="left")

    # ── İndirme ───────────────────────────────────────────────────────────────
    def _start_download(self):
        asset = self.update_info.get("asset")
        if not asset or not asset.get("download_url"):
            self._open_browser()
            return

        self.btn_update.config(state="disabled", text="İndiriliyor…")
        self.btn_skip.config(state="disabled")
        self.btn_skip_ver.config(state="disabled")

        self.progressbar.pack(fill="x", pady=(4,0))
        self.progress_lbl.config(text="Bağlanılıyor…")

        self._download_thread = threading.Thread(
            target=self._download_and_install,
            args=(asset,),
            daemon=True,
        )
        self._download_thread.start()

    def _download_and_install(self, asset: dict):
        url      = asset["download_url"]
        filename = asset["name"]
        tmp_dir  = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, filename)

        try:
            def reporthook(block_num, block_size, total_size):
                if self._cancelled or total_size <= 0:
                    return
                downloaded = block_num * block_size
                pct = min(int(downloaded / total_size * 100), 100)
                dl_mb  = downloaded / 1024 / 1024
                tot_mb = total_size  / 1024 / 1024
                self.after(0, self._update_progress, pct,
                           f"İndiriliyor… {dl_mb:.1f} / {tot_mb:.1f} MB")

            urllib.request.urlretrieve(url, tmp_path, reporthook)

            if self._cancelled:
                return

            self.after(0, self._update_progress, 100, "İndirme tamamlandı. Kuruluyor…")
            self.after(500, self._install, tmp_path)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "İndirme Hatası", f"İndirme başarısız:\n{e}", parent=self
            ))
            self.after(0, self._reset_buttons)

    def _update_progress(self, pct: int, label: str):
        self.progressbar["value"] = pct
        self.progress_lbl.config(text=label)

    def _install(self, filepath: str):
        try:
            platform = sys.platform
            if platform == "win32":
                os.startfile(filepath)
            elif platform == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                # .deb
                if filepath.endswith(".deb"):
                    subprocess.Popen(["pkexec", "dpkg", "-i", filepath])
                else:
                    os.chmod(filepath, 0o755)
                    subprocess.Popen([filepath])

            messagebox.showinfo(
                "Kurulum Başlatıldı",
                "Kurulum dosyası açıldı.\n"
                "Kurulum tamamlanınca SnapLoop'u yeniden başlatın.",
                parent=self,
            )
            self.parent.after(1500, self.parent.destroy)

        except Exception as e:
            messagebox.showerror("Kurulum Hatası", str(e), parent=self)
            self._reset_buttons()

    def _reset_buttons(self):
        self.btn_update.config(state="normal", text="⬇  Güncelle ve Kur")
        self.btn_skip.config(state="normal")
        self.btn_skip_ver.config(state="normal")
        self.progressbar.pack_forget()
        self.progress_lbl.config(text="")

    def _open_browser(self):
        import webbrowser
        webbrowser.open(self.update_info.get("html_url", ""))
        self.destroy()

    def _skip_version(self):
        """Bu sürümü atlamak için kaydet."""
        cfg_path = Path.home() / "SnapLoop_Recordings" / "skipped_version.txt"
        try:
            cfg_path.parent.mkdir(exist_ok=True)
            cfg_path.write_text(self.update_info["version"])
        except Exception:
            pass
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
def get_skipped_version() -> str:
    cfg_path = Path.home() / "SnapLoop_Recordings" / "skipped_version.txt"
    try:
        return cfg_path.read_text().strip()
    except Exception:
        return ""


def run_update_check(parent_window, silent: bool = True):
    """
    Arka planda güncelleme kontrolü yap.
    Yeni sürüm varsa UpdateDialog göster.
    silent=True → hata/bilgi mesajı gösterme (startup kontrolü için)
    """
    def _check():
        update_info = check_for_update()
        if not update_info:
            if not silent:
                parent_window.after(0, lambda: messagebox.showinfo(
                    "Güncelleme", "✓  Uygulama güncel!\nMevcut sürüm: v" + CURRENT_VERSION,
                    parent=parent_window,
                ))
            return

        # Kullanıcı bu sürümü atladıysa gösterme
        if update_info["version"] == get_skipped_version():
            return

        parent_window.after(0, lambda: UpdateDialog(parent_window, update_info))

    t = threading.Thread(target=_check, daemon=True)
    t.start()
