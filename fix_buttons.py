import re

def insert_common_ui(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    button_code = """
def _lighten(hex_color):
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"#{min(255, r + 30):02x}{min(255, g + 30):02x}{min(255, b + 30):02x}"
    except:
        return hex_color

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, color, text_color, width, height, font_t):
        super().__init__(parent, borderwidth=0, relief="flat", highlightthickness=0, bg=parent.cget('bg'))
        self.command = command
        self.color = color
        self.hover_color = _lighten(color)
        self.text_color = text_color
        self.text_val = text
        self.font = font_t
        self.is_disabled = False

        self.width_val = width if width else 150
        self.height_val = height if height else 36
        super().config(width=self.width_val, height=self.height_val)
        
        self.rect = self.create_polygon([0,0,0,0], fill=self.color, smooth=True)
        self.text_item = self.create_text(0, 0, text=self.text_val, fill=self.text_color, font=self.font)

        self.bind("<Configure>", self.on_resize)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def config(self, **kwargs):
        if 'text' in kwargs:
            self.text_val = kwargs.pop('text')
            self.itemconfig(self.text_item, text=self.text_val)
        if 'command' in kwargs:
            self.command = kwargs.pop('command')
        if 'state' in kwargs:
            state = kwargs.pop('state')
            if state == 'disabled':
                self.is_disabled = True
                self.itemconfig(self.rect, fill=C["surface2"])
                self.itemconfig(self.text_item, fill=C["muted"])
            else:
                self.is_disabled = False
                self.itemconfig(self.rect, fill=self.color)
                self.itemconfig(self.text_item, fill=self.text_color)
        if kwargs:
            super().config(**kwargs)
            
    def on_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10: return
        r = min(h // 2, 8)
        points = [
            r, 0, w-r, 0, w, 0, w, r,
            w, h-r, w, h, w-r, h, r, h,
            0, h, 0, h-r, 0, r, 0, 0
        ]
        self.coords(self.rect, points)
        self.coords(self.text_item, w/2, h/2)
        
    def on_press(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.color)
    def on_release(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.hover_color)
            if self.command:
                self.command()
    def on_enter(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.hover_color)
            self.config(cursor="hand2")
    def on_leave(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.color)
            self.config(cursor="")

def styled_btn(parent, text, cmd, color=None, width=None, height=36, font=None):
    c = color or C["accent2"]
    text_c = C["bg"] if c in [C["accent"], C["accent3"], C["success"]] else C["white"]
    return RoundedButton(parent, text, cmd, c, text_c, width, height, font or ("Courier New", 11, "bold"))
"""

    if "class RoundedButton" not in code:
        # inject just before def check_for_update
        idx = code.find("def check_for_update()")
        code = code[:idx] + button_code + "\n\n" + code[idx:]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

insert_common_ui("updater.py")

with open("updater.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace updater's old buttons
old_buttons = """        self.btn_update = tk.Button(
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
        self.btn_skip_ver.pack(side="left")"""

new_buttons = """        self.btn_update = styled_btn(
            btn_f, "⬇  Güncelle ve Kur",
            cmd=self._start_download,
            color=C["success"], height=40, font=("Courier New", 10, "bold")
        )
        self.btn_update.pack(side="left", fill="x", expand=True, padx=(0,8))

        # Asset yoksa tarayıcıda aç
        if not asset or not asset.get("download_url"):
            self.btn_update.config(text="��  Releases Sayfasını Aç",
                                   command=self._open_browser)

        self.btn_skip = styled_btn(
            btn_f, "Şimdi Değil",
            cmd=self.destroy,
            color=C["surface2"], height=40, width=120, font=("Courier New", 10)
        )
        self.btn_skip.pack(side="left", padx=(0,8))

        self.btn_skip_ver = styled_btn(
            btn_f, "Bu Sürümü Atla",
            cmd=self._skip_version,
            color=C["surface2"], height=40, width=140, font=("Courier New", 10)
        )
        self.btn_skip_ver.pack(side="left")"""

if old_buttons in code:
    with open("updater.py", "w", encoding="utf-8") as f:
        f.write(code.replace(old_buttons, new_buttons))
        
