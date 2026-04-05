import tkinter as tk

C = {
    "bg":        "#0d0d14",
    "surface":   "#14141f",
    "surface2":  "#1c1c2e",
    "border":    "#2a2a45",
    "accent":    "#00e5ff",
    "success":   "#10b981",
    "text":      "#e2e8f0",
    "muted":     "#64748b",
}

def _lighten(hex_color):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = min(255, r + 40)
    g = min(255, g + 40)
    b = min(255, b + 40)
    return f"#{r:02x}{g:02x}{b:02x}"

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
        if 'state' in kwargs:
            if kwargs['state'] == 'disabled':
                self.is_disabled = True
                self.itemconfig(self.rect, fill=C["surface2"])
                self.itemconfig(self.text_item, fill=C["muted"])
            else:
                self.is_disabled = False
                self.itemconfig(self.rect, fill=self.color)
                self.itemconfig(self.text_item, fill=self.text_color)
            del kwargs['state']
        if kwargs:
            super().config(**kwargs)
            
    def on_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10: return
        r = min(h // 2, 8) # radius of 8
        points = [
            r, 0,
            w-r, 0,
            w, 0,
            w, r,
            w, h-r,
            w, h,
            w-r, h,
            r, h,
            0, h,
            0, h-r,
            0, r,
            0, 0
        ]
        self.coords(self.rect, points)
        self.coords(self.text_item, w/2, h/2)
        
    def on_press(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.hover_color)
    def on_release(self, event):
        if not self.is_disabled:
            self.itemconfig(self.rect, fill=self.color)
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
    return RoundedButton(parent, text, cmd, color or C["accent"], C["bg"], width, height, font or ("Courier New", 12, "bold"))

root = tk.Tk()
root.config(bg=C["bg"])
btn = styled_btn(root, "PLAY", lambda: print("play"), color=C["success"])
btn.pack(pady=20, padx=20, fill="x", expand=True)

# we won't run mainloop, just checking syntax
print("Syntax OK")
