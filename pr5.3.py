import tkinter as tk
import math
from datetime import datetime


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f4f1ec"
PANEL = "#ffffff"
BORDER = "#d8d4cd"
TEXT = "#1c1c1e"
MUTED = "#888888"

# Манометр
GAUGE_CASE_OUTER = "#2c2c2c"
GAUGE_CASE_MID = "#4a4a4a"
GAUGE_CASE_INNER = "#e8e5e0"
GAUGE_DIAL = "#f8f6f2"
GAUGE_TICK = "#2c2c2c"
GAUGE_TEXT = "#1a1a1a"
GAUGE_NEEDLE = "#1a1a1a"
GAUGE_CENTER = "#2c2c2c"

ZONE_GREEN = "#2ecc71"
ZONE_YELLOW = "#f4b400"
ZONE_RED = "#e53935"

# Часы
CLOCK_CASE = "#d94141"
CLOCK_CASE_DARK = "#a02e2e"
CLOCK_DIAL = "#ffffff"
CLOCK_TEXT = "#1a1a1a"
CLOCK_NEEDLE_H = "#1a1a1a"
CLOCK_NEEDLE_M = "#1a1a1a"
CLOCK_NEEDLE_S = "#e53935"


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    """Точка на окружности. 0° = вверх, по часовой."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# МАНОМЕТР
# ═══════════════════════════════════════════════════════════════════
class Manometer:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        self.vmin = 0
        self.vmax = 120
        self.start_angle = -135
        self.end_angle = 135
        self.value = 29.0

        self.zones = [
            (60, ZONE_GREEN),
            (90, ZONE_YELLOW),
            (120, ZONE_RED),
        ]

        self._draw_case()
        self._draw_zones()
        self._draw_ticks()
        self._draw_labels()
        self._draw_value_label()
        self._draw_needle()

    def _draw_case(self):
        c = self.canvas
        s = self.size

        # Внешняя тень
        c.create_oval(self.cx - s + 5, self.cy - s + 7,
                      self.cx + s + 5, self.cy + s + 7,
                      fill="#b0aca8", outline="")

        # Чёрный внешний корпус
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill=GAUGE_CASE_OUTER, outline="#1a1a1a", width=2)

        # Светлый ободок
        c.create_oval(self.cx - s + 8, self.cy - s + 8,
                      self.cx + s - 8, self.cy + s - 8,
                      fill=GAUGE_CASE_MID, outline="")

        # Внутренний светлый
        c.create_oval(self.cx - s + 14, self.cy - s + 14,
                      self.cx + s - 14, self.cy + s - 14,
                      fill=GAUGE_CASE_INNER, outline="")

        # Циферблат
        c.create_oval(self.cx - s + 22, self.cy - s + 22,
                      self.cx + s - 22, self.cy + s - 22,
                      fill=GAUGE_DIAL, outline="#c0bdb8", width=1)

    def _draw_zones(self):
        """Цветные дуги по периметру циферблата."""
        c = self.canvas
        r_outer = self.size - 26
        r_inner = self.size - 42

        prev = self.vmin
        for to_val, color in self.zones:
            a1 = self._value_to_angle(prev)
            a2 = self._value_to_angle(to_val)
            self._ring_arc(r_inner, r_outer, a1, a2, color)
            prev = to_val

    def _ring_arc(self, r_in, r_out, a1, a2, color, steps=40):
        c = self.canvas
        points = []
        for i in range(steps + 1):
            a = a1 + (a2 - a1) * i / steps
            points.append(polar(self.cx, self.cy, r_out, a))
        for i in range(steps, -1, -1):
            a = a1 + (a2 - a1) * i / steps
            points.append(polar(self.cx, self.cy, r_in, a))
        flat = [v for pt in points for v in pt]
        c.create_polygon(*flat, fill=color, outline="")

    def _draw_ticks(self):
        c = self.canvas

        # Крупные деления каждые 15 bar
        for v in range(self.vmin, self.vmax + 1, 15):
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 50, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 24, a)
            c.create_line(x1, y1, x2, y2, fill=GAUGE_TICK, width=2)

        # Средние деления каждые 5 bar
        for v in range(self.vmin, self.vmax + 1, 5):
            if v % 15 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 36, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 24, a)
            c.create_line(x1, y1, x2, y2, fill=GAUGE_TICK, width=1)

    def _draw_labels(self):
        c = self.canvas
        r_label = self.size - 62

        for v in range(self.vmin, self.vmax + 1, 15):
            a = self._value_to_angle(v)
            x, y = polar(self.cx, self.cy, r_label, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 9, "bold"),
                          fill=GAUGE_TEXT)

    def _draw_value_label(self):
        """Метка значения под стрелкой (например, '29 [bar]')."""
        c = self.canvas
        self._value_text_id = c.create_text(
            self.cx, self.cy + self.size * 0.55,
            text="29 [bar]",
            font=("Segoe UI", 12, "bold"),
            fill=GAUGE_TEXT,
        )

    def _draw_needle(self):
        self._needle_items = []
        self._redraw_needle()

    def _redraw_needle(self):
        c = self.canvas

        for item in self._needle_items:
            c.delete(item)
        self._needle_items = []

        a = self._value_to_angle(self.value)
        r = self.size - 48

        tip_x, tip_y = polar(self.cx, self.cy, r, a)
        tail_x, tail_y = polar(self.cx, self.cy, -14, a)

        # Тень
        shadow = c.create_line(tip_x + 2, tip_y + 3,
                               tail_x + 2, tail_y + 3,
                               fill="#888", width=4, capstyle="round")

        # Тело
        body = c.create_line(tail_x, tail_y, tip_x, tip_y,
                             fill=GAUGE_NEEDLE, width=4,
                             capstyle="round")

        # Шайба
        hub1 = c.create_oval(self.cx - 12, self.cy - 12,
                             self.cx + 12, self.cy + 12,
                             fill="#4a4a4a", outline="")
        hub2 = c.create_oval(self.cx - 7, self.cy - 7,
                             self.cx + 7, self.cy + 7,
                             fill=GAUGE_CENTER, outline="")

        self._needle_items = [shadow, body, hub1, hub2]

    def _value_to_angle(self, value):
        pct = (value - self.vmin) / (self.vmax - self.vmin)
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    def set_value(self, value):
        self.value = max(self.vmin, min(self.vmax, value))
        self._redraw_needle()
        self.canvas.itemconfig(
            self._value_text_id,
            text=f"{int(round(self.value))} [bar]"
        )


# ═══════════════════════════════════════════════════════════════════
# ЧАСЫ
# ═══════════════════════════════════════════════════════════════════
class Clock:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        self._draw_case()
        self._draw_ticks()
        self._draw_numbers()

        # Стрелки
        self.hour_needle = None
        self.minute_needle = None
        self.second_needle = None
        self._draw_needles()
        self._update_time()

    def _draw_case(self):
        c = self.canvas
        s = self.size

        # Тень
        c.create_oval(self.cx - s + 5, self.cy - s + 7,
                      self.cx + s + 5, self.cy + s + 7,
                      fill="#b0aca8", outline="")

        # Красный корпус
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill=CLOCK_CASE, outline=CLOCK_CASE_DARK, width=2)

        # Внутренний тёмный ободок
        c.create_oval(self.cx - s + 6, self.cy - s + 6,
                      self.cx + s - 6, self.cy + s - 6,
                      fill=CLOCK_CASE_DARK, outline="")

        # Белый циферблат
        c.create_oval(self.cx - s + 12, self.cy - s + 12,
                      self.cx + s - 12, self.cy + s - 12,
                      fill=CLOCK_DIAL, outline="")

    def _draw_ticks(self):
        c = self.canvas

        # Минутные — 60 рисок
        for i in range(60):
            a = i * 6
            if i % 5 == 0:
                r1 = self.size - 26
                r2 = self.size - 16
                w = 3
            else:
                r1 = self.size - 22
                r2 = self.size - 16
                w = 1
            x1, y1 = polar(self.cx, self.cy, r1, a)
            x2, y2 = polar(self.cx, self.cy, r2, a)
            c.create_line(x1, y1, x2, y2, fill=CLOCK_TEXT, width=w)

    def _draw_numbers(self):
        c = self.canvas
        r_num = self.size - 44

        for i in range(1, 13):
            a = i * 30
            x, y = polar(self.cx, self.cy, r_num, a)
            c.create_text(x, y, text=str(i),
                          font=("Segoe UI", 16, "bold"),
                          fill=CLOCK_TEXT)

    def _draw_needles(self):
        c = self.canvas

        # Центральная шайба
        c.create_oval(self.cx - 6, self.cy - 6,
                      self.cx + 6, self.cy + 6,
                      fill=CLOCK_NEEDLE_H, outline="")

        # Часовая
        self.hour_needle = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.45,
            fill=CLOCK_NEEDLE_H, width=6, capstyle="round"
        )
        # Минутная
        self.minute_needle = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.65,
            fill=CLOCK_NEEDLE_M, width=4, capstyle="round"
        )
        # Секундная
        self.second_needle = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.72,
            fill=CLOCK_NEEDLE_S, width=2, capstyle="round"
        )

    def _update_time(self):
        now = datetime.now()

        # Часы
        h = now.hour % 12
        m = now.minute
        s = now.second

        # Часовая стрелка
        hour_angle = (h + m / 60) * 30
        self._rotate_needle(self.hour_needle, hour_angle, self.size * 0.45)

        # Минутная
        minute_angle = (m + s / 60) * 6
        self._rotate_needle(self.minute_needle, minute_angle, self.size * 0.65)

        # Секундная
        second_angle = s * 6
        self._rotate_needle(self.second_needle, second_angle, self.size * 0.72)

        self.canvas.after(1000, self._update_time)

    def _rotate_needle(self, needle_id, angle, length):
        x, y = polar(self.cx, self.cy, length, angle)
        self.canvas.coords(needle_id, self.cx, self.cy, x, y)


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class AnalogApp:
    def __init__(self, root):
        self.root = root
        root.title("Аналоговые приборы")
        root.geometry("1000x820")
        root.minsize(880, 760)
        root.configure(bg=BG)

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Аналоговые приборы",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Манометр и часы — стрелки в реальном времени",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 10))

        # ═══ Область с приборами ═════════════════════════════════
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=20)

        # ── Манометр ─────────────────────────────────────────
        left = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=10)

        self.gauge_canvas = tk.Canvas(left, width=420, height=420,
                                      bg=BG, highlightthickness=0)
        self.gauge_canvas.pack()

        self.gauge = Manometer(self.gauge_canvas,
                               cx=210, cy=210, size=190)

        self.gauge_value = tk.Label(left, text="29 [bar]",
                                    font=("Consolas", 18, "bold"),
                                    bg=BG, fg=TEXT)
        self.gauge_value.pack(pady=(6, 4))

        self.gauge_scale = tk.Scale(
            left, from_=0, to=120,
            orient="horizontal", length=380,
            showvalue=False,
            bg=BG, fg=TEXT,
            troughcolor="#c9c6c1",
            activebackground=GAUGE_NEEDLE,
            highlightthickness=0, bd=0,
            sliderlength=22, width=10,
            command=self.on_gauge_change,
        )
        self.gauge_scale.set(29)
        self.gauge_scale.pack(pady=(0, 10))

        # Кнопки манометра
        btns = tk.Frame(left, bg=BG)
        btns.pack(pady=(0, 10))

        self._make_button(btns, "−  5", lambda: self.gauge_step(-5)).pack(
            side="left", padx=4)
        self._make_button(btns, "+  5", lambda: self.gauge_step(+5)).pack(
            side="left", padx=4)
        self._make_button(btns, "Сейчас", self.set_now).pack(
            side="left", padx=(16, 4))

        # ── Часы ─────────────────────────────────────────────
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=10)

        self.clock_canvas = tk.Canvas(right, width=420, height=420,
                                      bg=BG, highlightthickness=0)
        self.clock_canvas.pack()

        self.clock = Clock(self.clock_canvas,
                           cx=210, cy=210, size=190)

        tk.Label(right, text="",
                 font=("Consolas", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(6, 4))

        tk.Label(right, text="текущее время",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 10))

    # ════════════════════════════════════════════════════════════
    # КНОПКИ
    # ════════════════════════════════════════════════════════════
    def _make_button(self, parent, text, command, color="#0a84ff"):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 11, "bold"),
                        bg=color, fg="#ffffff",
                        activebackground=color, activeforeground="#ffffff",
                        bd=0, relief="flat",
                        padx=16, pady=8,
                        cursor="hand2",
                        command=command)

        def on_enter(e):
            btn.config(bg="#0066cc")

        def on_leave(e):
            btn.config(bg=color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ════════════════════════════════════════════════════════════
    # ДЕЙСТВИЯ
    # ════════════════════════════════════════════════════════════
    def on_gauge_change(self, value):
        v = float(value)
        self.gauge.set_value(v)
        self.gauge_value.config(text=f"{int(round(v))} [bar]")

    def gauge_step(self, delta):
        v = max(0, min(120, self.gauge.value + delta))
        self.gauge_scale.set(v)

    def set_now(self):
        """Устанавливает давление по текущей минуте."""
        v = datetime.now().minute * 2  # 0…118
        self.gauge_scale.set(v)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = AnalogApp(root)
    root.mainloop()
