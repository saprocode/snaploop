import re

with open("snaploop.py", "r", encoding="utf-8") as f:
    code = f.read()

new_tab = """    def _build_record_tab(self):
        p = self._tab_record

        # ── 1. KONTROL PANELİ (Daha Düzenli Bir Bottom Bar) ─────────────────────
        ctrl = tk.Frame(p, bg=C["surface2"], bd=1, relief="flat", highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(side="bottom", fill="x", pady=(15, 0))
        
        ctrl_inner = tk.Frame(ctrl, bg=C["surface2"], padx=25, pady=16)
        ctrl_inner.pack(fill="both")

        info_f = tk.Frame(ctrl_inner, bg=C["surface2"])
        info_f.pack(side="left", fill="y")
        self.timer_lbl = tk.Label(info_f, text="00:00:00", bg=C["surface2"],
                                  fg=C["accent"], font=("Courier New", 28, "bold"))
        self.timer_lbl.pack(anchor="w")
        
        stats_f = tk.Frame(info_f, bg=C["surface2"])
        stats_f.pack(anchor="w")
        self.frame_lbl = tk.Label(stats_f, text="0 kare", bg=C["surface2"],
                                  fg=C["text"], font=FONT_MONO)
        self.frame_lbl.pack(side="left")
        self.fps_lbl = tk.Label(stats_f, text="—", bg=C["surface2"],
                                fg=C["muted"], font=FONT_MONO)
        self.fps_lbl.pack(side="left", padx=(8,0))

        btn_f = tk.Frame(ctrl_inner, bg=C["surface2"])
        btn_f.pack(side="right", fill="y", pady=(2,0))
        
        self.btn_start = styled_btn(btn_f, "▶  BAŞLAT",
                                    self._start_recording, color=C["success"], width=130, height=44, font=("Courier New", 12, "bold"))
        self.btn_start.pack(side="left", padx=(0,10))

        self.btn_pause = styled_btn(btn_f, "⏸  DURAKLAT",
                                    self._pause_recording, color=C["accent3"], width=130, height=44, font=("Courier New", 12, "bold"))
        self.btn_pause.pack(side="left", padx=(0,10))
        self.btn_pause.config(state="disabled")

        self.btn_stop = styled_btn(btn_f, "⏹  DURDUR",
                                   self._stop_recording, color=C["danger"], width=130, height=44, font=("Courier New", 12, "bold"))
        self.btn_stop.pack(side="left")
        self.btn_stop.config(state="disabled")

        # ── 2. ANA İÇERİK KARTLARI ───────────────────────────────────────────
        content = tk.Frame(p, bg=C["bg"])
        content.pack(side="top", fill="both", expand=True)
        
        left = tk.Frame(content, bg=C["bg"])
        right = tk.Frame(content, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0,8), pady=(8,0))
        right.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(8,0))

        # -- SOL: HEDEF SEÇİMİ --
        target_card = self._card(left, "HEDEF EKRAN / PENCERE")
        target_card.pack(fill="both", expand=True, pady=(0,12))

        type_f = tk.Frame(target_card, bg=C["surface"])
        type_f.pack(fill="x", pady=(0,10))
        for val, lbl in [("all","Tüm Ekranlar"), ("monitor","Ekran Seç"), ("window","Pencere Seç")]:
            rb = tk.Radiobutton(type_f, text=lbl, variable=self.var_target_type, value=val,
                                bg=C["surface"], fg=C["accent"], selectcolor=C["surface2"],
                                activebackground=C["surface"], activeforeground=C["white"], font=FONT_MONO,
                                command=self._on_target_type_change, cursor="hand2")
            rb.pack(side="left", padx=(0,16))

        self.monitor_frame = tk.Frame(target_card, bg=C["surface"])
        self.monitor_frame.pack(fill="x")
        self.window_frame = tk.Frame(target_card, bg=C["surface"])
        
        refresh_btn = styled_btn(target_card, "↻  Hedefleri Yenile", self._refresh_targets,
                                 color=C["muted"], width=180, height=30, font=FONT_MONO)
        refresh_btn.pack(side="bottom", anchor="e", pady=(8,0))

        # -- SAĞ: KALİTE & FORMAT --
        quality_card = self._card(right, "KAYIT BİÇİMİ VE KALİTE")
        quality_card.pack(fill="x", pady=(0,12))

        fmt_f = tk.Frame(quality_card, bg=C["surface"])
        fmt_f.pack(fill="x", pady=(4,10))
        tk.Label(fmt_f, text="Format:", bg=C["surface"], fg=C["muted"], font=FONT_MONO).pack(side="left", padx=(0,8))
        for fmt in ["PNG","JPEG","WEBP"]:
            rb = tk.Radiobutton(fmt_f, text=fmt, variable=self.var_format, value=fmt,
                                bg=C["surface"], fg=C["accent"], selectcolor=C["surface2"],
                                activebackground=C["surface"], activeforeground=C["white"], font=FONT_MONO, cursor="hand2")
            rb.pack(side="left", padx=(0,12))

        q_row = tk.Frame(quality_card, bg=C["surface"])
        q_row.pack(fill="x", pady=(4,0))
        tk.Label(q_row, text="Kalite:", bg=C["surface"], fg=C["muted"], font=FONT_MONO).pack(side="left", padx=(0,8))
        self.quality_slider = tk.Scale(
            q_row, variable=self.var_quality, from_=10, to=100,
            orient="horizontal", showvalue=False,
            bg=C["surface"], fg=C["accent"], troughcolor=C["surface2"],
            activebackground=C["accent"], highlightthickness=0, bd=0,
            command=self._on_quality_change, length=120,
        )
        self.quality_slider.pack(side="left", fill="x", expand=True)
        self.quality_val_lbl = tk.Label(q_row, text="85%", bg=C["surface"],
                                        fg=C["text"], font=("Courier New",12,"bold"), width=5)
        self.quality_val_lbl.pack(side="left", padx=(8,0))

        # -- SAĞ: ZAMANLAMA --
        timing_card = self._card(right, "ZAMANLAMA LİMİTLERİ")
        timing_card.pack(fill="x", pady=(0,12))
        
        row1 = tk.Frame(timing_card, bg=C["surface"])
        row1.pack(fill="x")
        tk.Label(row1, text="Kare Aralığı (sn):", bg=C["surface"], fg=C["muted"], font=FONT_MONO).grid(row=0,column=0,sticky="w",pady=3)
        styled_entry(row1, textvariable=self.var_interval, width=8).grid(row=0, column=1, sticky="w", padx=(8,0))

        dur_row = tk.Frame(timing_card, bg=C["surface"])
        dur_row.pack(fill="x", pady=(4,0))
        self._chk(dur_row, "Otomatik Durdur (sn):", self.var_duration_en).pack(side="left")
        styled_entry(dur_row, textvariable=self.var_duration, width=8).pack(side="left", padx=(8,0))

        # -- SAĞ: KOTA --
        limit_card = self._card(right, "BOYUT LİMİTİ (KOTA)")
        limit_card.pack(fill="x", pady=(0,12))
        
        lim_row = tk.Frame(limit_card, bg=C["surface"])
        lim_row.pack(fill="x")
        self._chk(lim_row, "Kotayı Aktif Et (MB):", self.var_limit_en).pack(side="left")
        styled_entry(lim_row, textvariable=self.var_size_limit, width=8).pack(side="left", padx=(8,0))

        self.size_bar_frame = tk.Frame(limit_card, bg=C["surface"])
        self.size_bar_frame.pack(fill="x", pady=(12,0))
        tk.Label(self.size_bar_frame, text="Kullanılan Alan:", bg=C["surface"],
                 fg=C["muted"], font=("Courier New",8)).pack(anchor="w")
        bar_bg = tk.Frame(self.size_bar_frame, bg=C["border"], height=6)
        bar_bg.pack(fill="x", pady=(4,2))
        self.size_bar = tk.Frame(bar_bg, bg=C["accent"], height=6)
        self.size_bar.place(x=0, y=0, relheight=1, relwidth=0)
        self.size_lbl = tk.Label(self.size_bar_frame, text="0.0 / 500.0 MB",
                                 bg=C["surface"], fg=C["muted"], font=("Courier New",8))
        self.size_lbl.pack(anchor="e")
"""

start_idx = code.find("    def _build_record_tab(self):")
end_idx = code.find("    # ══════════════════════════ KAYITLAR TABÜ", start_idx)

if start_idx != -1 and end_idx != -1:
    new_code = code[:start_idx] + new_tab + "\n" + code[end_idx:]
    with open("snaploop.py", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Replaced successfully.")
else:
    print("Could not find blocks.")
