import tkinter as tk

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f4f1ec"
PANEL = "#ffffff"
BORDER = "#d8d4cd"

TUBE_BG = "#f8f8f8"
TUBE_EDGE = "#b8b5b0"
TUBE_GLASS = "#eae7e2"

LIQUID_COLD = "#2e6fdb"
LIQUID_OK = "#2ecc71"
LIQUID_HOT = "#e53935"

TEXT = "#1c1c1e"
MUTED = "#888888"
ACCENT = "#0a84ff"


# ─── Утилиты ─────────────────────────────────────────────────────
def to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def lerp_color(c1, c2, t):
    r1, g1, b1 = to_rgb(c1)
    r2, g2, b2 = to_rgb(c2)
    return to_hex((
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    ))


def lighten(color, amount):
    r, g, b = to_rgb(color)
    return to_hex((
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
    ))


def darken(color, amount):
    r, g, b = to_rgb(color)
    return to_hex((
        int(r * (1 - amount)),
        int(g * (1 - amount)),
        int(b * (1 - amount)),
    ))


# ─── Приложение ──────────────────────────────────────────────────
class ThermometerApp:
    def __init__(self, root):
        self.root = root
        root.title("Термометр")
        root.geometry("560x780")
        root.minsize(480, 720)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.vmin = 0
        self.vmax = 100
        self.value = 29.0
        self.target_value = 29.0
        self.heating = False
        self._alarm_played = False
        self._animating = False

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Термометр",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Двигайте ползунок или используйте кнопки",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 12))

        # ═══ Карточка с прибором ═════════════════════════════════
        card = tk.Frame(root, bg=PANEL,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=40, pady=(0, 12))

        self.canvas = tk.Canvas(card, width=280, height=520,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ═══ Цифровое значение ═══════════════════════════════════
        self.value_label = tk.Label(root, text="",
                                    font=("Consolas", 36, "bold"),
                                    bg=BG, fg=LIQUID_OK)
        self.value_label.pack(pady=(0, 6))

        self.status_label = tk.Label(root, text="",
                                     font=("Segoe UI", 11),
                                     bg=BG, fg=MUTED)
        self.status_label.pack(pady=(0, 12))

        # ═══ Ползунок ════════════════════════════════════════════
        self.scale = tk.Scale(
            root,
            from_=self.vmin, to=self.vmax,
            orient="horizontal",
            length=420,
            showvalue=True,
            font=("Segoe UI", 9),
            bg=BG, fg=TEXT,
            troughcolor="#d8d4cd",
            activebackground=ACCENT,
            highlightthickness=0, bd=0,
            sliderlength=24, width=12,
            command=self.on_scale_change,
        )
        self.scale.set(self.value)
        self.scale.pack(pady=(0, 14))

        # ═══ Кнопки ══════════════════════════════════════════════
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 20))

        self.btn_minus = self._make_button(btns, "➖  1°",
                                           lambda: self.step(-1))
        self.btn_minus.pack(side="left", padx=4)

        self.btn_plus = self._make_button(btns, "➕  1°",
                                          lambda: self.step(+1))
        self.btn_plus.pack(side="left", padx=4)

        self.btn_heat = self._make_button(btns, "🔥  Нагреть",
                                          self.toggle_heat,
                                          color=LIQUID_HOT)
        self.btn_heat.pack(side="left", padx=(20, 4))

        # ═══ Клавиатура ══════════════════════════════════════════
        root.bind("<Up>",    lambda e: self.step(+1))
        root.bind("<Down>",  lambda e: self.step(-1))
        root.bind("<Left>",  lambda e: self.step(-1))
        root.bind("<Right>", lambda e: self.step(+1))
        root.bind("<space>", lambda e: self.toggle_heat())

        # Первая отрисовка
        self.redraw()
        self.update_label()

    # ════════════════════════════════════════════════════════════
    # КНОПКИ
    # ════════════════════════════════════════════════════════════
    def _make_button(self, parent, text, command, color=ACCENT):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 11, "bold"),
                        bg=color, fg="#ffffff",
                        activebackground=color, activeforeground="#ffffff",
                        bd=0, relief="flat",
                        padx=16, pady=10,
                        cursor="hand2",
                        command=command)

        hover = lighten(color, 0.15)
        press = darken(color, 0.15)

        def on_enter(e):
            if btn["state"] != "disabled":
                btn.config(bg=hover)

        def on_leave(e):
            if btn["state"] != "disabled":
                btn.config(bg=color)

        def on_press(e):
            if btn["state"] != "disabled":
                btn.config(bg=press)

        def on_release(e):
            if btn["state"] != "disabled":
                btn.config(bg=hover)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        return btn

    # ════════════════════════════════════════════════════════════
    # ЦВЕТ ЖИДКОСТИ (плавный переход)
    # ════════════════════════════════════════════════════════════
    def _liquid_color(self):
        v = self.value
        if v <= 20:
            t = v / 20
            return lerp_color(LIQUID_COLD, LIQUID_OK, t)
        elif v <= 70:
            return LIQUID_OK
        else:
            t = min(1.0, (v - 70) / 30)
            return lerp_color(LIQUID_OK, LIQUID_HOT, t)

    # ════════════════════════════════════════════════════════════
    # ОТРИСОВКА
    # ════════════════════════════════════════════════════════════
    def redraw(self):
        c = self.canvas
        c.delete("all")

        cx = 140
        tube_w = 24
        tube_top = 30
        tube_bottom = 430
        bulb_r = 28
        liquid = self._liquid_color()

        # ─── Тень шарика ──────────────────────────────────────
        c.create_oval(cx - bulb_r - 2, tube_bottom - bulb_r + 4,
                      cx + bulb_r + 2, tube_bottom + bulb_r + 4,
                      fill="#d8d4cd", outline="")

        # ─── Шарик ────────────────────────────────────────────
        c.create_oval(cx - bulb_r, tube_bottom - bulb_r,
                      cx + bulb_r, tube_bottom + bulb_r,
                      fill=liquid, outline=TUBE_EDGE, width=2)
        # Блик на шарике
        c.create_oval(cx - bulb_r + 8, tube_bottom - bulb_r + 6,
                      cx - bulb_r + 18, tube_bottom - bulb_r + 16,
                      fill="#ffffff", outline="")

        # ─── Трубка ───────────────────────────────────────────
        c.create_rectangle(cx - tube_w / 2 - 2, tube_top - 2,
                           cx + tube_w / 2 + 2, tube_bottom + 2,
                           fill=TUBE_GLASS, outline=TUBE_EDGE, width=1)
        c.create_rectangle(cx - tube_w / 2, tube_top,
                           cx + tube_w / 2, tube_bottom,
                           fill=TUBE_BG, outline="")

        # ─── Столбик ──────────────────────────────────────────
        fill_pct = (self.value - self.vmin) / (self.vmax - self.vmin)
        fill_top = tube_bottom - (tube_bottom - tube_top) * fill_pct

        c.create_rectangle(cx - tube_w / 2 + 1, fill_top,
                           cx + tube_w / 2 - 1, tube_bottom,
                           fill=liquid, outline="")
        c.create_oval(cx - tube_w / 2 + 1, fill_top - 4,
                      cx + tube_w / 2 - 1, fill_top + 4,
                      fill=liquid, outline="")

        # ─── Блики на стекле ──────────────────────────────────
        c.create_line(cx - tube_w / 2 + 3, tube_top + 10,
                      cx - tube_w / 2 + 3, tube_bottom - 40,
                      fill="#ffffff", width=3)
        c.create_line(cx + tube_w / 2 - 4, tube_top + 10,
                      cx + tube_w / 2 - 4, tube_bottom - 40,
                      fill="#e0e0e0", width=1)

        # ─── Деления и подписи ────────────────────────────────
        tick_x_start = cx + tube_w / 2 + 6

        for v in range(self.vmin, self.vmax + 1):
            y = tube_bottom - (tube_bottom - tube_top) * \
                (v - self.vmin) / (self.vmax - self.vmin)

            if v % 25 == 0:
                c.create_line(tick_x_start, y,
                              tick_x_start + 18, y,
                              fill="#222222", width=2)
                c.create_text(tick_x_start + 26, y,
                              text=str(v),
                              font=("Segoe UI", 10, "bold"),
                              fill="#333333", anchor="w")
            elif v % 5 == 0:
                c.create_line(tick_x_start, y,
                              tick_x_start + 12, y,
                              fill="#555555", width=1)
            else:
                c.create_line(tick_x_start, y,
                              tick_x_start + 6, y,
                              fill="#aaaaaa", width=1)

        # ─── Красная зона 70…100 ─────────────────────────────
        y_hot = tube_bottom - (tube_bottom - tube_top) * \
                (70 - self.vmin) / (self.vmax - self.vmin)
        c.create_rectangle(tick_x_start + 34, tube_top,
                           tick_x_start + 44, y_hot,
                           fill="#ffcccc", outline="#e53935", width=1)

        # ─── Метка °C ─────────────────────────────────────────
        c.create_text(cx + bulb_r + 22, tube_bottom + 10,
                      text="°C",
                      font=("Segoe UI", 12, "bold"),
                      fill="#333333", anchor="w")

        # ─── Указатель текущего уровня ────────────────────────
        y_current = tube_bottom - (tube_bottom - tube_top) * fill_pct
        c.create_line(tick_x_start - 4, y_current,
                      tick_x_start + 22, y_current,
                      fill=liquid, width=2)
        c.create_polygon(tick_x_start - 4, y_current - 5,
                         tick_x_start - 4, y_current + 5,
                         tick_x_start - 12, y_current,
                         fill=liquid, outline="")

    # ════════════════════════════════════════════════════════════
    # ОБНОВЛЕНИЕ ЗНАЧЕНИЙ
    # ════════════════════════════════════════════════════════════
    def on_scale_change(self, value):
        self.target_value = float(value)
        if not self._animating:
            self._animating = True
            self._animate_tick()

    def _animate_tick(self):
        diff = self.target_value - self.value
        if abs(diff) < 0.2:
            self.value = self.target_value
            self.redraw()
            self.update_label()
            self._animating = False
            return
        self.value += diff * 0.25
        self.redraw()
        self.update_label()
        self.root.after(16, self._animate_tick)

    def step(self, delta):
        new_value = max(self.vmin, min(self.vmax, self.value + delta))
        self.scale.set(new_value)

    def update_label(self):
        color = self._liquid_color()
        self.value_label.config(text=f"{int(round(self.value))} °C", fg=color)

        if self.value < 20:
            status = "Холодно"
        elif self.value <= 70:
            status = "Норма"
        else:
            status = "Жарко"

        self.status_label.config(text=status, fg=color)

        # Звуковой сигнал при перегреве
        if self.value > 70 and not self._alarm_played:
            if HAS_SOUND:
                try:
                    winsound.Beep(880, 200)
                except Exception:
                    pass
            self._alarm_played = True
        elif self.value <= 70:
            self._alarm_played = False

    # ════════════════════════════════════════════════════════════
    # АВТОНАГРЕВ
    # ════════════════════════════════════════════════════════════
    def toggle_heat(self):
        self.heating = not self.heating
        if self.heating:
            self.btn_heat.config(text="⏹  Остановить")
            self._heat_tick()
        else:
            self.btn_heat.config(text="🔥  Нагреть")

    def _heat_tick(self):
        if not self.heating:
            return
        if self.value >= self.vmax:
            self.heating = False
            self.btn_heat.config(text="🔥  Нагреть")
            return
        self.scale.set(min(self.vmax, self.value + 1))
        self.root.after(300, self._heat_tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ThermometerApp(root)
    root.mainloop()
