import tkinter as tk
import math


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f4f4f4"
PANEL = "#ffffff"
BORDER = "#d0d0d0"
TEXT = "#1c1c1e"
MUTED = "#888888"

# Спидометр
DIAL = "#fafafa"
ARC_DARK = "#3a3a3a"       # дуга шкалы (тёмная)
ARC_LIGHT = "#8a8a8a"      # светлый край дуги
TICK_MAJOR = "#1a1a1a"
TICK_MINOR = "#666666"
NEEDLE = "#e53935"
NEEDLE_GLOW = "#ff6b6b"    # свечение вокруг шайбы
CENTER_HUB = "#e53935"

OK = "#2ecc71"
WARN = "#f4b400"
DANGER = "#e53935"
ACCENT = "#0a84ff"


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    """Точка на окружности. 0° = вверх, по часовой."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# СПИДОМЕТР
# ═══════════════════════════════════════════════════════════════════
class Speedometer:
    def __init__(self, canvas, cx, cy, size,
                 vmin=0, vmax=100, unit=""):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.vmin = vmin
        self.vmax = vmax
        self.unit = unit

        # Углы шкалы — от -135° до +135° (широкая дуга)
        self.start_angle = -135
        self.end_angle = 135

        self.value = 0.0

        self._draw_case()
        self._draw_arc()
        self._draw_ticks()
        self._draw_labels()
        self._draw_value_text()
        self._draw_needle()

    # ─── Корпус ─────────────────────────────────────────────────
    def _draw_case(self):
        c = self.canvas
        s = self.size

        # Внешняя тень
        c.create_oval(self.cx - s + 4, self.cy - s + 6,
                      self.cx + s + 4, self.cy + s + 6,
                      fill="#c8c8c8", outline="")

        # Внешний светлый ободок
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill="#e8e8e8", outline="#b8b8b8", width=1)

        # Внутренний циферблат
        c.create_oval(self.cx - s + 8, self.cy - s + 8,
                      self.cx + s - 8, self.cy + s - 8,
                      fill=DIAL, outline="#d0d0d0", width=1)

    # ─── Дуга шкалы (толстая серая сверху) ──────────────────────
    def _draw_arc(self):
        c = self.canvas
        r_outer = self.size - 18
        r_inner = self.size - 42

        # Задняя светлая дуга (весь диапазон)
        self._ring_arc(r_inner, r_outer,
                       self.start_angle, self.end_angle,
                       ARC_LIGHT)

        # Тёмная дуга (сужена до 0…100, но с небольшим отступом для стиля)
        self._ring_arc(r_inner + 2, r_outer - 2,
                       self.start_angle + 2, self.end_angle - 2,
                       ARC_DARK)

    def _ring_arc(self, r_in, r_out, a1, a2, color, steps=60):
        c = self.canvas
        pts = []
        for i in range(steps + 1):
            a = a1 + (a2 - a1) * i / steps
            pts.append(polar(self.cx, self.cy, r_out, a))
        for i in range(steps, -1, -1):
            a = a1 + (a2 - a1) * i / steps
            pts.append(polar(self.cx, self.cy, r_in, a))
        flat = [v for pt in pts for v in pt]
        c.create_polygon(*flat, fill=color, outline="")

    # ─── Деления ────────────────────────────────────────────────
    def _draw_ticks(self):
        c = self.canvas

        # Крупные деления каждые 10
        for v in range(self.vmin, self.vmax + 1, 10):
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 50, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 30, a)
            c.create_line(x1, y1, x2, y2,
                          fill=TICK_MAJOR, width=2)

        # Средние деления каждые 5 (только не кратные 10)
        for v in range(self.vmin, self.vmax + 1, 5):
            if v % 10 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 44, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 30, a)
            c.create_line(x1, y1, x2, y2,
                          fill=TICK_MINOR, width=1)

        # Мелкие деления каждые 2 (только не кратные 5)
        for v in range(self.vmin, self.vmax + 1, 2):
            if v % 5 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 38, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 30, a)
            c.create_line(x1, y1, x2, y2,
                          fill=TICK_MINOR, width=1)

    # ─── Подписи чисел ──────────────────────────────────────────
    def _draw_labels(self):
        c = self.canvas
        r_label = self.size - 62

        for v in range(self.vmin, self.vmax + 1, 10):
            a = self._value_to_angle(v)
            x, y = polar(self.cx, self.cy, r_label, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 10, "bold"),
                          fill=TEXT)

    # ─── Крупное число под шкалой ───────────────────────────────
    def _draw_value_text(self):
        c = self.canvas
        self._value_text = c.create_text(
            self.cx, self.cy + self.size * 0.30,
            text="0",
            font=("Segoe UI", 32, "bold"),
            fill="#4a90d9",
        )
        if self.unit:
            c.create_text(
                self.cx, self.cy + self.size * 0.55,
                text=self.unit,
                font=("Segoe UI", 12),
                fill=MUTED,
            )

    # ─── Стрелка со свечением ───────────────────────────────────
    def _draw_needle(self):
        self._needle_items = []
        self._redraw_needle()

    def _redraw_needle(self):
        c = self.canvas
        for item in self._needle_items:
            c.delete(item)
        self._needle_items = []

        a = self._value_to_angle(self.value)
        r = self.size - 55

        tip_x, tip_y = polar(self.cx, self.cy, r, a)
        tail_x, tail_y = polar(self.cx, self.cy, -12, a)

        # Тень стрелки
        shadow = c.create_line(tip_x + 2, tip_y + 3,
                               tail_x + 2, tail_y + 3,
                               fill="#cccccc", width=5,
                               capstyle="round")

        # Тело стрелки — красное, чуть шире к центру
        body = c.create_line(tail_x, tail_y, tip_x, tip_y,
                             fill=NEEDLE, width=4,
                             capstyle="round")

        # Остриё стрелки
        tip = c.create_oval(tip_x - 3, tip_y - 3,
                            tip_x + 3, tip_y + 3,
                            fill=NEEDLE, outline="")

        # Свечение вокруг центра — 3 круга разного размера с уменьшающейся прозрачностью
        glow_outer = c.create_oval(
            self.cx - 26, self.cy - 26,
            self.cx + 26, self.cy + 26,
            fill=NEEDLE_GLOW, outline="",
        )
        glow_mid = c.create_oval(
            self.cx - 20, self.cy - 20,
            self.cx + 20, self.cy + 20,
            fill=NEEDLE_GLOW, outline="",
        )
        # Основная шайба — красный круг
        hub_outer = c.create_oval(
            self.cx - 14, self.cy - 14,
            self.cx + 14, self.cy + 14,
            fill=CENTER_HUB, outline="",
        )
        # Блик
        hub_shine = c.create_oval(
            self.cx - 6, self.cy - 8,
            self.cx + 2, self.cy - 2,
            fill="#ff9090", outline="",
        )

        self._needle_items = [
            shadow, body, tip,
            glow_outer, glow_mid,
            hub_outer, hub_shine,
        ]

    # ─── Преобразования ─────────────────────────────────────────
    def _value_to_angle(self, value):
        pct = (value - self.vmin) / (self.vmax - self.vmin)
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    # ─── Установка значения ─────────────────────────────────────
    def set_value(self, value):
        self.value = max(self.vmin, min(self.vmax, value))
        self._redraw_needle()

        # Меняем цвет числа в зависимости от диапазона
        if self.value < 40:
            color = "#4a90d9"   # синий — спокойно
        elif self.value < 70:
            color = "#f4b400"   # жёлтый — внимание
        else:
            color = "#e53935"   # красный — быстро

        self.canvas.itemconfig(
            self._value_text,
            text=f"{int(round(self.value))}",
            fill=color,
        )


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class SpeedometerApp:
    def __init__(self, root):
        self.root = root
        root.title("Спидометр")
        root.geometry("640x760")
        root.minsize(560, 700)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.accelerating = False

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Спидометр",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Стрелка и число следуют за ползунком",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 14))

        # ═══ Карточка с прибором ═════════════════════════════════
        card = tk.Frame(root, bg=PANEL,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(padx=40, pady=(0, 14))

        self.canvas = tk.Canvas(card, width=440, height=440,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ═══ Прибор ══════════════════════════════════════════════
        self.speedo = Speedometer(self.canvas,
                                  cx=220, cy=220, size=190,
                                  vmin=0, vmax=100,
                                  unit="км/ч")

        # ═══ Ползунок ════════════════════════════════════════════
        self.scale = tk.Scale(
            root, from_=0, to=100,
            orient="horizontal", length=440,
            showvalue=False,
            bg=BG, fg=TEXT,
            troughcolor="#d8d4cd",
            activebackground=ACCENT,
            highlightthickness=0, bd=0,
            sliderlength=24, width=12,
            command=self.on_change,
        )
        self.scale.set(0)
        self.scale.pack(pady=(0, 12))

        # ═══ Кнопки ══════════════════════════════════════════════
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 20))

        self._btn(btns, "−  10", lambda: self.step(-10)).pack(
            side="left", padx=4)
        self._btn(btns, "+  10", lambda: self.step(+10)).pack(
            side="left", padx=4)
        self.btn_accel = self._btn(btns, "🔥  Разгон", self.toggle_accel,
                                   color="#e53935")
        self.btn_accel.pack(side="left", padx=(20, 4))

        # Клавиатура
        root.bind("<Left>",  lambda e: self.step(-5))
        root.bind("<Right>", lambda e: self.step(+5))
        root.bind("<Up>",    lambda e: self.step(+5))
        root.bind("<Down>",  lambda e: self.step(-5))
        root.bind("<space>", lambda e: self.toggle_accel())

    # ─── Кнопки ────────────────────────────────────────────────
    def _btn(self, parent, text, command, color=ACCENT):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 11, "bold"),
                        bg=color, fg="#ffffff",
                        activebackground=color, activeforeground="#ffffff",
                        bd=0, relief="flat",
                        padx=16, pady=10,
                        cursor="hand2",
                        command=command)

        def on_enter(e):
            btn.config(bg=self._darken(color))

        def on_leave(e):
            btn.config(bg=color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _darken(self, color):
        color = color.lstrip("#")
        r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4))
        return "#%02x%02x%02x" % (int(r * 0.8), int(g * 0.8), int(b * 0.8))

    # ─── Действия ──────────────────────────────────────────────
    def on_change(self, value):
        self.speedo.set_value(float(value))

    def step(self, delta):
        v = max(0, min(100, self.speedo.value + delta))
        self.scale.set(v)

    def toggle_accel(self):
        self.accelerating = not self.accelerating
        if self.accelerating:
            self.btn_accel.config(text="⏹  Стоп")
            self._accel_tick()
        else:
            self.btn_accel.config(text="🔥  Разгон")

    def _accel_tick(self):
        if not self.accelerating:
            return
        if self.speedo.value >= 100:
            self.accelerating = False
            self.btn_accel.config(text="🔥  Разгон")
            return
        self.scale.set(min(100, self.speedo.value + 2))
        self.root.after(80, self._accel_tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedometerApp(root)
    root.mainloop()
