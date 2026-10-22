import tkinter as tk
import math
import random


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#ffffff"
PANEL = "#ffffff"
BORDER = "#e0e0e0"
TEXT = "#1c1c1e"
MUTED = "#888888"

DARK_CASE = "#2a2a2a"
DARK_CASE_IN = "#3a3a3a"
NEEDLE_RED = "#e53935"

BTN_DARK = "#1e1e2e"
BTN_LIGHT = "#f5f5f0"
BTN_BLUE = "#1e3a5f"
BTN_PURPLE = "#4a3a6e"

ARROW_DARK = "#4a4a5a"
ARROW_LIGHT = "#8a8a80"    # ← темнее для контраста
ARROW_BLUE = "#4dabf7"
ARROW_PURPLE = "#8b7fd4"

RING_GREEN = "#2ecc71"
RING_ORANGE = "#e8a04a"
RING_BLUE = "#4a90d9"
RING_PURPLE = "#a890d9"


def polar(cx, cy, r, angle_deg):
    """
    Координаты точки на окружности.
    0° — вверх (12 часов), углы идут ПО ЧАСОВОЙ.
    """
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# СПИДОМЕТР
# ═══════════════════════════════════════════════════════════════════
class DialGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 65.0

        # Углы шкалы: 0% → 210° (слева-внизу), 100% → -30° (справа-внизу)
        # Идут через ВЕРХ по часовой.
        self.start_angle = 210
        self.end_angle = -30

        c = canvas
        r = size

        # ─── Корпус ─────────────────────────────────────────
        c.create_oval(cx - r - 4, cy - r - 4,
                      cx + r + 4, cy + r + 4,
                      fill="#1a1a1a", outline="")
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=DARK_CASE, outline=DARK_CASE_IN, width=2)

        # ─── Цветные полосы — по значению ────────────────────
        # 0…40 — зелёная
        self._draw_zone_arc(0, 40, RING_GREEN)
        # 40…60 — жёлто-зелёная
        self._draw_zone_arc(40, 60, "#9ed44a")
        # 60…80 — жёлтая
        self._draw_zone_arc(60, 80, "#f4d03f")
        # 80…95 — оранжевая
        self._draw_zone_arc(80, 95, "#f0803a")
        # 95…100 — красная
        self._draw_zone_arc(95, 100, "#e53935")

        # ─── Деления и подписи ──────────────────────────────
        for i in range(11):
            v = i * 10
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 14, a)
            x2, y2 = polar(cx, cy, r - 24, a)
            c.create_line(x1, y1, x2, y2, fill="#ffffff", width=1)

            x, y = polar(cx, cy, r - 40, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 8), fill="#e8e8e8")

        # Мелкие деления
        for v in range(0, 101, 5):
            if v % 10 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 14, a)
            x2, y2 = polar(cx, cy, r - 20, a)
            c.create_line(x1, y1, x2, y2, fill="#888888", width=1)

        # ─── Крупное число внизу ───────────────────────────
        self.value_text = c.create_text(
            cx, cy + r * 0.55,
            text="0",
            font=("Segoe UI", 20, "bold"),
            fill="#ffffff",
        )

        # ─── Стрелка ────────────────────────────────────────
        self.needle_id = c.create_line(
            cx, cy, cx, cy - r + 30,
            fill=NEEDLE_RED, width=4, capstyle="round",
        )
        # Центральная шайба
        c.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                      fill="#e53935", outline="#ffffff", width=2)

        # Первичная отрисовка
        self._redraw()

    def _draw_zone_arc(self, v_start, v_end, color):
        """Рисует дугу между двумя значениями."""
        c = self.canvas
        r = self.size - 6
        a1 = self._value_to_angle(v_start)
        a2 = self._value_to_angle(v_end)

        # В Tkinter create_arc: start — начало, extent — протяжённость (по часовой, если +)
        # У нас a1 > a2 (например 210° → 0°), идём по часовой: extent = a2 - a1 < 0
        extent = a2 - a1
        c.create_arc(
            self.cx - r, self.cy - r,
            self.cx + r, self.cy + r,
            start=a1, extent=extent,
            style="arc", outline=color, width=6,
        )

    def _value_to_angle(self, value):
        """0% → start_angle, 100% → end_angle."""
        pct = value / 100.0
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    def set_value(self, v):
        self.target = max(0.0, min(100.0, float(v)))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) < 0.3:
            self.value = self.target
        else:
            self.value += diff * 0.15
        self._redraw()

    def _redraw(self):
        a = self._value_to_angle(self.value)
        x, y = polar(self.cx, self.cy, self.size - 34, a)
        self.canvas.coords(self.needle_id, self.cx, self.cy, x, y)
        self.canvas.itemconfig(self.value_text,
                               text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# ИНДИКАТОР НАПРАВЛЕНИЯ
# ═══════════════════════════════════════════════════════════════════
class DirectionPad:
    def __init__(self, canvas, cx, cy, size,
                 bg_color, arrow_color, ring_color, center_icon_color,
                 show_ring=False):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.spin_speed = 0.0
        self.rotation = 0.0

        c = canvas
        r = size

        # ─── Фоновая плашка ────────────────────────────────
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=bg_color, outline="")

        # ─── Цветное кольцо ────────────────────────────────
        if show_ring:
            c.create_oval(cx - r + 4, cy - r + 4,
                          cx + r - 4, cy + r - 4,
                          fill="", outline=ring_color, width=3)

        # ─── Внутренний круг ───────────────────────────────
        inner_r = r * 0.65
        c.create_oval(cx - inner_r, cy - inner_r,
                      cx + inner_r, cy + inner_r,
                      fill="", outline=arrow_color, width=2)

        # ─── Четыре стрелки ────────────────────────────────
        # Больше по размеру и ближе к краю
        arrow_size = r * 0.15
        arrow_dist = r * 0.72

        self._draw_arrow(cx, cy - arrow_dist, "up", arrow_size, arrow_color)
        self._draw_arrow(cx + arrow_dist, cy, "right", arrow_size, arrow_color)
        self._draw_arrow(cx, cy + arrow_dist, "down", arrow_size, arrow_color)
        self._draw_arrow(cx - arrow_dist, cy, "left", arrow_size, arrow_color)

        # ─── Центральный круг ──────────────────────────────
        center_r = r * 0.32
        c.create_oval(cx - center_r, cy - center_r,
                      cx + center_r, cy + center_r,
                      fill=bg_color, outline=arrow_color, width=2)

        # ─── Иконка «обновить» ────────────────────────────
        self._draw_refresh_icon(cx, cy, center_r * 0.55, center_icon_color)

    def _draw_arrow(self, x, y, direction, size, color):
        """Рисует большой треугольник-стрелку."""
        c = self.canvas

        if direction == "up":
            pts = [x, y - size * 1.3,
                   x - size, y + size * 0.8,
                   x + size, y + size * 0.8]
        elif direction == "down":
            pts = [x, y + size * 1.3,
                   x - size, y - size * 0.8,
                   x + size, y - size * 0.8]
        elif direction == "left":
            pts = [x - size * 1.3, y,
                   x + size * 0.8, y - size,
                   x + size * 0.8, y + size]
        else:  # right
            pts = [x + size * 1.3, y,
                   x - size * 0.8, y - size,
                   x - size * 0.8, y + size]

        c.create_polygon(*pts, fill=color, outline="")

    def _draw_refresh_icon(self, cx, cy, r, color):
        """Иконка «обновить» — дуга 270° + 2 стрелки по краям."""
        c = self.canvas

        # Дуга (270°, начиная с 45°)
        c.create_arc(cx - r, cy - r, cx + r, cy + r,
                     start=45, extent=270,
                     style="arc", outline=color, width=3)

        # Стрелка сверху дуги — треугольник покрупнее
        x1, y1 = polar(cx, cy, r, -45)
        c.create_polygon(
            x1 - 6, y1 + 3,
            x1 + 6, y1 + 3,
            x1, y1 - 6,
            fill=color, outline="",
        )

        # Стрелка снизу дуги
        x2, y2 = polar(cx, cy, r, 135)
        c.create_polygon(
            x2 - 6, y2 - 3,
            x2 + 6, y2 - 3,
            x2, y2 + 6,
            fill=color, outline="",
        )

    def start_spin(self):
        self.spin_speed = 5.0

    def tick(self):
        if abs(self.spin_speed) > 0.01:
            self.rotation += self.spin_speed
            self.spin_speed *= 0.92
        else:
            self.rotation = 0.0
            self.spin_speed = 0.0


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class DirectionApp:
    def __init__(self, root):
        self.root = root
        root.title("Индикаторы направления")
        root.geometry("1200x420")
        root.minsize(1100, 400)
        root.configure(bg=BG)
        root.resizable(False, False)

        tk.Label(root, text="Индикаторы направления",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 4))

        tk.Label(root,
                 text="Ползунок меняет спидометр · кнопки управляют джойстиками",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 12))

        panel = tk.Frame(root, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        panel.pack(padx=20, pady=(0, 12))

        self.canvas = tk.Canvas(panel, width=1140, height=240,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ─── 5 приборов ─────────────────────────────────────
        self.dial = DialGauge(self.canvas, cx=120, cy=140, size=90)

        self.pad_dark = DirectionPad(
            self.canvas, cx=340, cy=140, size=90,
            bg_color=BTN_DARK, arrow_color=ARROW_DARK,
            ring_color=RING_GREEN, center_icon_color="#4ad0a0",
        )

        self.pad_light = DirectionPad(
            self.canvas, cx=560, cy=140, size=90,
            bg_color=BTN_LIGHT, arrow_color=ARROW_LIGHT,
            ring_color=RING_ORANGE, center_icon_color="#a89880",
            show_ring=True,
        )

        self.pad_blue = DirectionPad(
            self.canvas, cx=780, cy=140, size=90,
            bg_color=BTN_BLUE, arrow_color=ARROW_BLUE,
            ring_color=RING_BLUE, center_icon_color=ARROW_BLUE,
            show_ring=True,
        )

        self.pad_purple = DirectionPad(
            self.canvas, cx=1000, cy=140, size=90,
            bg_color=BTN_PURPLE, arrow_color=ARROW_PURPLE,
            ring_color=RING_PURPLE, center_icon_color=ARROW_PURPLE,
            show_ring=True,
        )

        # ─── Управление ─────────────────────────────────────
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(padx=20, pady=(0, 16))

        slider_frame = tk.Frame(ctrl, bg=BG)
        slider_frame.pack(side="left", padx=(0, 20))

        tk.Label(slider_frame, text="Спидометр",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack()

        self.value_label = tk.Label(slider_frame, text="65",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=BG, fg=TEXT)
        self.value_label.pack()

        self.scale = tk.Scale(slider_frame, from_=0, to=100,
                              orient="horizontal", length=200,
                              showvalue=False,
                              bg=BG, fg=TEXT, troughcolor="#d8d8d8",
                              activebackground=NEEDLE_RED,
                              highlightthickness=0, bd=0,
                              sliderlength=18, width=8,
                              command=self.on_slider)
        self.scale.set(65)
        self.scale.pack()

        self.btn_refresh = tk.Button(
            ctrl, text="🔄  Обновить всё",
            font=("Segoe UI", 11, "bold"),
            bg="#4a90d9", fg="#ffffff",
            activebackground="#3a7bc0", activeforeground="#ffffff",
            bd=0, padx=20, pady=12, cursor="hand2",
            command=self.refresh_all,
        )
        self.btn_refresh.pack(side="left", padx=(10, 0))

        self.btn_auto = tk.Button(
            ctrl, text="▶  Авто",
            font=("Segoe UI", 11, "bold"),
            bg="#2ecc71", fg="#ffffff",
            activebackground="#20a544", activeforeground="#ffffff",
            bd=0, padx=20, pady=12, cursor="hand2",
            command=self.toggle_auto,
        )
        self.btn_auto.pack(side="left", padx=(10, 0))

        self.auto_mode = False
        self.auto_phase = 0.0

        self._tick()

    def on_slider(self, v):
        if self.auto_mode:
            return
        val = float(v)
        self.dial.set_value(val)
        self.value_label.config(text=str(int(val)))

    def refresh_all(self):
        for pad in (self.pad_dark, self.pad_light,
                    self.pad_blue, self.pad_purple):
            pad.start_spin()

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_auto.config(text="⏹  Стоп", bg="#e53935",
                                 activebackground="#a82419")
            self.auto_phase = 0.0
        else:
            self.btn_auto.config(text="▶  Авто", bg="#2ecc71",
                                 activebackground="#20a544")

    def _tick(self):
        if self.auto_mode:
            self.auto_phase += 0.05
            val = 50 + 45 * math.sin(self.auto_phase)
            self.dial.set_value(val)
            self.scale.set(val)
            self.value_label.config(text=str(int(val)))
            if random.random() < 0.02:
                self.refresh_all()

        self.dial.tick()
        self.pad_dark.tick()
        self.pad_light.tick()
        self.pad_blue.tick()
        self.pad_purple.tick()

        self.root.after(33, self._tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = DirectionApp(root)
    root.mainloop()
