import tkinter as tk
import math


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f0f0f0"
PANEL = "#ffffff"
BORDER = "#c0c0c0"

CASE_TOP = "#3a3a3a"        # верхняя (серая) часть корпуса
CASE_BOTTOM = "#1a1a1a"     # нижняя (чёрная) часть
CASE_EDGE = "#000000"       # чёрная рамка
DIAL = "#e8e8e8"            # циферблат
DIAL_SHADOW = "#cccccc"

TEXT = "#1a1a1a"
MUTED = "#666666"
GOOD_TEXT = "#555555"
BAD_TEXT = "#333333"

NEEDLE = "#e53935"          # красная стрелка

# 10 сегментов — плавный переход от зелёного к красному
SEGMENT_COLORS = [
    "#2ecc71", "#4cd964", "#7ed321", "#a8d84a", "#d4d840",
    "#f4d03f", "#f4b400", "#f59e0b", "#f97316", "#e53935",
]

ACCENT = "#0a84ff"


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    """Точка на окружности. 0° = вверх, по часовой."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ─── Индикатор ───────────────────────────────────────────────────
class GoodBadGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        self.value = 30             # 0…100
        self.segments = 10

        # Углы шкалы
        self.start_angle = -75
        self.end_angle = 75

        self._draw_case()
        self._draw_dial()
        self._draw_segments()
        self._draw_labels()
        self._draw_value_text()
        self._draw_needle()
        self._draw_mini_indicator()

    # ─── Корпус ─────────────────────────────────────────────────
    def _draw_case(self):
        c = self.canvas
        s = self.size

        # Внешняя рамка (чёрная)
        c.create_rectangle(
            self.cx - s - 10, self.cy - s * 0.75 - 10,
            self.cx + s + 10, self.cy + s * 0.75 + 10,
            fill=CASE_EDGE, outline=""
        )
        # Верхняя серая часть
        c.create_rectangle(
            self.cx - s - 4, self.cy - s * 0.75 - 4,
            self.cx + s + 4, self.cy + s * 0.2,
            fill=CASE_TOP, outline=""
        )
        # Нижняя чёрная часть
        c.create_rectangle(
            self.cx - s - 4, self.cy + s * 0.2,
            self.cx + s + 4, self.cy + s * 0.75 + 4,
            fill=CASE_BOTTOM, outline=""
        )
        # Лёгкий блик сверху
        c.create_rectangle(
            self.cx - s + 10, self.cy - s * 0.75 + 8,
            self.cx + s - 10, self.cy - s * 0.75 + 12,
            fill="#5a5a5a", outline=""
        )

    # ─── Циферблат ──────────────────────────────────────────────
    def _draw_dial(self):
        c = self.canvas
        s = self.size

        # Прямоугольник циферблата
        c.create_rectangle(
            self.cx - s + 6, self.cy - s * 0.55 + 4,
            self.cx + s - 6, self.cy + s * 0.45,
            fill=DIAL, outline=DIAL_SHADOW, width=1
        )

        # Лёгкий градиент-тень сверху
        c.create_line(
            self.cx - s + 8, self.cy - s * 0.55 + 6,
            self.cx + s - 8, self.cy - s * 0.55 + 6,
            fill="#d0d0d0", width=3
        )

    # ─── Сегменты шкалы ─────────────────────────────────────────
    def _draw_segments(self):
        c = self.canvas
        r_outer = self.size - 20
        r_inner = self.size - 55

        n = self.segments
        for i in range(n):
            a1 = self.start_angle + (self.end_angle - self.start_angle) * i / n
            a2 = self.start_angle + (self.end_angle - self.start_angle) * (i + 1) / n

            color = SEGMENT_COLORS[i]

            # Рисуем сегмент как заполненный полигон
            self._segment_arc(r_inner, r_outer, a1, a2, color)

    def _segment_arc(self, r_in, r_out, a1, a2, color, steps=20):
        c = self.canvas
        pts = []
        for i in range(steps + 1):
            a = a1 + (a2 - a1) * i / steps
            pts.append(polar(self.cx, self.cy, r_out, a))
        for i in range(steps, -1, -1):
            a = a1 + (a2 - a1) * i / steps
            pts.append(polar(self.cx, self.cy, r_in, a))
        flat = [v for pt in pts for v in pt]
        c.create_polygon(*flat, fill=color, outline="#ffffff", width=1)

    # ─── Подписи GOOD / BAD ────────────────────────────────────
    def _draw_labels(self):
        c = self.canvas
        r = self.size - 12

        x_good, y_good = polar(self.cx, self.cy, r, self.start_angle - 8)
        c.create_text(x_good, y_good, text="GOOD",
                      font=("Segoe UI", 12, "bold"),
                      fill=GOOD_TEXT)

        x_bad, y_bad = polar(self.cx, self.cy, r, self.end_angle + 8)
        c.create_text(x_bad, y_bad, text="BAD",
                      font=("Segoe UI", 12, "bold"),
                      fill=BAD_TEXT)

    # ─── Текст % по центру ──────────────────────────────────────
    def _draw_value_text(self):
        c = self.canvas
        self._percent_text = c.create_text(
            self.cx, self.cy + self.size * 0.1,
            text="30 %",
            font=("Segoe UI", 22, "bold"),
            fill=TEXT,
        )

    # ─── Стрелка ────────────────────────────────────────────────
    def _draw_needle(self):
        self._needle_items = []
        self._redraw_needle()

    def _redraw_needle(self):
        c = self.canvas
        for item in self._needle_items:
            c.delete(item)
        self._needle_items = []

        a = self._value_to_angle(self.value)
        r = self.size - 35

        tip_x, tip_y = polar(self.cx, self.cy, r, a)
        tail_x, tail_y = polar(self.cx, self.cy, -18, a)

        # Тень
        sh = c.create_line(tip_x + 1, tip_y + 2,
                           tail_x + 1, tail_y + 2,
                           fill="#aaa", width=3, capstyle="round")
        # Тело стрелки
        body = c.create_line(tail_x, tail_y, tip_x, tip_y,
                             fill=NEEDLE, width=4,
                             capstyle="round")
        # Шайба
        hub = c.create_oval(self.cx - 8, self.cy - 8,
                            self.cx + 8, self.cy + 8,
                            fill="#3a3a3a", outline="")

        self._needle_items = [sh, body, hub]

    # ─── Мини-индикатор в правом нижнем углу ────────────────────
    def _draw_mini_indicator(self):
        c = self.canvas
        s = self.size

        # Позиция блока
        base_x = self.cx + s - 90
        base_y = self.cy + s * 0.55

        # Фон
        c.create_rectangle(
            base_x - 6, base_y - 24,
            base_x + 10 * 10 + 6, base_y + 4,
            fill="#0a0a0a", outline="#3a3a3a", width=1
        )

        # 10 полосок
        self._mini_bars = []
        for i in range(10):
            x = base_x + i * 10
            bar = c.create_rectangle(
                x, base_y - 20,
                x + 7, base_y - 2,
                fill="#2a2a2a", outline="#555", width=1
            )
            self._mini_bars.append(bar)

        self._redraw_mini_indicator()

    def _redraw_mini_indicator(self):
        """Подсвечивает полоски пропорционально значению."""
        n = 10
        active = int(round(self.value / 100 * n))
        for i, bar in enumerate(self._mini_bars):
            if i < active:
                color = SEGMENT_COLORS[i]
            else:
                color = "#2a2a2a"
            self.canvas.itemconfig(bar, fill=color)

    # ─── Значение → угол ────────────────────────────────────────
    def _value_to_angle(self, value):
        pct = value / 100
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    # ─── Обновление ─────────────────────────────────────────────
    def set_value(self, value):
        self.value = max(0, min(100, value))

        # Стрелка
        self._redraw_needle()
        # Мини-индикатор
        self._redraw_mini_indicator()
        # Текст процента
        self.canvas.itemconfig(
            self._percent_text,
            text=f"{int(round(self.value))} %"
        )

    def get_color(self):
        """Цвет текущего сегмента (для подсветки фона)."""
        idx = min(9, int(self.value // 10))
        return SEGMENT_COLORS[idx]


# ─── Приложение ──────────────────────────────────────────────────
class GaugeApp:
    def __init__(self, root):
        self.root = root
        root.title("Good / Bad индикатор")
        root.geometry("640x780")
        root.minsize(560, 720)
        root.configure(bg=BG)
        root.resizable(False, False)

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Индикатор состояния",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Хорошо … Плохо — двигайте ползунок",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 14))

        # ═══ Карточка с прибором ═════════════════════════════════
        self.card = tk.Frame(root, bg=PANEL,
                             highlightthickness=1,
                             highlightbackground=BORDER)
        self.card.pack(padx=40, pady=(0, 14))

        self.canvas = tk.Canvas(self.card, width=480, height=340,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ═══ Индикатор ═══════════════════════════════════════════
        self.gauge = GoodBadGauge(self.canvas,
                                  cx=240, cy=180, size=190)

        # ═══ Подпись ═════════════════════════════════════════════
        self.status = tk.Label(root, text="",
                               font=("Segoe UI", 14, "bold"),
                               bg=BG, fg=TEXT)
        self.status.pack(pady=(0, 8))

        # ═══ Ползунок ════════════════════════════════════════════
        self.scale = tk.Scale(
            root, from_=0, to=100,
            orient="horizontal", length=460,
            showvalue=False,
            bg=BG, fg=TEXT,
            troughcolor="#d8d4cd",
            activebackground=ACCENT,
            highlightthickness=0, bd=0,
            sliderlength=24, width=12,
            command=self.on_change,
        )
        self.scale.set(30)
        self.scale.pack(pady=(0, 14))

        # ═══ Кнопки ══════════════════════════════════════════════
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 20))

        self._btn(btns, "− 5", lambda: self.step(-5)).pack(side="left", padx=4)
        self._btn(btns, "+ 5", lambda: self.step(+5)).pack(side="left", padx=4)
        self._btn(btns, "Плохо", lambda: self.scale.set(95),
                  color="#e53935").pack(side="left", padx=(16, 4))
        self._btn(btns, "Хорошо", lambda: self.scale.set(10),
                  color="#2ecc71").pack(side="left", padx=4)

        # Первичная отрисовка
        self.on_change(30)

    def _btn(self, parent, text, command, color=ACCENT):
        b = tk.Button(parent, text=text,
                      font=("Segoe UI", 11, "bold"),
                      bg=color, fg="#ffffff",
                      activebackground=color, activeforeground="#ffffff",
                      bd=0, relief="flat",
                      padx=16, pady=10,
                      cursor="hand2",
                      command=command)

        def on_enter(e):
            b.config(bg=self._darken(color))

        def on_leave(e):
            b.config(bg=color)

        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    def _darken(self, color):
        color = color.lstrip("#")
        r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4))
        return "#%02x%02x%02x" % (int(r * 0.8), int(g * 0.8), int(b * 0.8))

    # ─── Действия ───────────────────────────────────────────────
    def on_change(self, value):
        v = float(value)
        self.gauge.set_value(v)

        # Текст и цвет статуса
        if v < 30:
            text = "Отлично"
            color = "#2ecc71"
        elif v < 55:
            text = "Хорошо"
            color = "#7ed321"
        elif v < 75:
            text = "Внимание"
            color = "#f4b400"
        elif v < 90:
            text = "Плохо"
            color = "#f97316"
        else:
            text = "Опасно"
            color = "#e53935"

        self.status.config(text=text, fg=color)
        self.card.config(highlightbackground=color)

    def step(self, delta):
        v = max(0, min(100, self.gauge.value + delta))
        self.scale.set(v)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = GaugeApp(root)
    root.mainloop()
