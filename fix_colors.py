import re

with open("snaploop.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix Update Button
old_upd = """        # Güncelleme kontrolü butonu
        if HAS_UPDATER:
            upd_btn = tk.Button(
                topbar, text="⟳ Güncelleme Kontrol Et",
                command=lambda: run_update_check(self, silent=False),
                bg=C["surface2"], fg=C["muted"],
                activebackground=C["surface2"], activeforeground=C["accent"],
                font=("Courier New", 8), relief="flat", cursor="hand2",
                bd=0, padx=8, pady=4,
            )
            upd_btn.pack(side="right", padx=(0, 10))"""

new_upd = """        # Güncelleme kontrolü butonu
        if HAS_UPDATER:
            upd_btn = styled_btn(
                topbar, "⟳ Güncellemeleri Denetle",
                cmd=lambda: run_update_check(self, silent=False),
                color=C["surface2"], height=30, font=("Courier New", 9, "bold")
            )
            upd_btn.pack(side="right", padx=(0, 10))"""

# Fix Tabs visibility
old_tabs = """        style.configure("Custom.TNotebook.Tab",
                        background=C["surface"], foreground=C["muted"],
                        padding=[16,8], borderwidth=0, font=("Courier New", 9, "bold"))"""

new_tabs = """        style.configure("Custom.TNotebook.Tab",
                        background=C["surface"], foreground=C["text"],
                        padding=[16,8], borderwidth=0, font=("Courier New", 10, "bold"))"""

code = code.replace(old_upd, new_upd)
code = code.replace(old_tabs, new_tabs)

with open("snaploop.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Colors updated successfully.")
