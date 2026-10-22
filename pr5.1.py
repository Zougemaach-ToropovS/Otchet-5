import tkinter as tk
import math


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#e8e5e0"                # фон окна — светло-серый
CASE_OUTER = "#c9c6c1"        # внешний ободок корпуса
CASE_MID = "#b8b5b0"          # средний ободок
CASE_INNER = "#f4f1ec"        # внутренний (светлый) ободок
DIAL = "#ffffff"              # белый циферблат
DIAL_SHADOW = "#e8e5e0"       # лёгкая тень на циферблате
TICK_MAJOR = "#3a3a3a"        # крупные деления
TICK_MINOR = "#888888"        # мелкие деления
TEXT = "#1a1a1a"              # цифры
MUTED = "#666666"             # подписи
NEEDLE_RED = "#e53935"        # красная стрелка
NEEDLE_DARK = "#2c2c2c"       # тёмная стрелка
CENTER = "#2c2c2c"            # центр стрелки

# Цвета зон на тахометре
ZONE_GREEN = "#7bc043"
ZONE_YELLOW = "#f4b400"
ZONE_RED = "#e53935"


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    """Точка на окружности. Угол 0 = вверх, по часовой."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ─── Аналоговый прибор ───────────────────────────────────────────
class AnalogGauge:
    def __init__(self, canvas, cx, cy, size,
                 vmin, vmax,
                 start_angle, end_angle,
                 major_step, minor_step,
                 label="", unit="",
                 zones=None,
                 needle_color=NEEDLE_RED):
        """
        canvas       — Canvas, на котором рисуем
        cx, cy       — центр прибора
        size         — радиус внешнего обода
        vmin, vmax   — диапазон значений
        start_angle  — угол начала шкалы (0 = верх, по часовой)
        end_angle    — угол конца шкалы
        major_step   — шаг крупных делений
        minor_step   — шаг мелких делений
        label        — подпись под шкалой (например, °C)
        unit         — единица (для форматирования значения)
        zones        — [(до_значения, цвет), ...] цветные зоны
        """
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.vmin = vmin
        self.vmax = vmax
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.major_step = major_step
        self.minor_step = minor_step
        self.label = label
        self.unit = unit
        self.zones = zones or []
        self.needle_color = needle_color

        self.value = vmin

        self._draw_case()
        self._draw_zones()
        self._draw_ticks()
        self._draw_labels()
        self._draw_center_label()
        self._draw_needle()

    # ─── Корпус ─────────────────────────────────────────────────
    def _draw_case(self):
        c = self.canvas
        s = self.size

        # Внешняя тень
        c.create_oval(self.cx - s + 4, self.cy - s + 6,
                      self.cx + s + 4, self.cy + s + 6,
                      fill="#b0aca8", outline="")
        # Внешний ободок
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill=CASE_OUTER, outline="#a8a5a0", width=1)
        # Средний ободок
        c.create_oval(self.cx - s + 6, self.cy - s + 6,
                      self.cx + s - 6, self.cy + s - 6,
                      fill=CASE_MID, outline="")
        # Внутренний светлый ободок
        c.create_oval(self.cx - s + 12, self.cy - s + 12,
                      self.cx + s - 12, self.cy + s - 12,
                      fill=CASE_INNER, outline="")
        # Циферблат
        c.create_oval(self.cx - s + 22, self.cy - s + 22,
                      self.cx + s - 22, self.cy + s - 22,
                      fill=DIAL, outline="#c0bdb8", width=1)
        # Тонкая дуга-тень сверху на циферблате
        c.create_arc(self.cx - s + 30, self.cy - s + 30,
                     self.cx + s - 30, self.cy + s - 30,
                     start=60, extent=60,
                     style="arc", outline="#f0ede8", width=6)

    # ─── Цветные зоны ───────────────────────────────────────────
    def _draw_zones(self):
        if not self.zones:
            return
        c = self.canvas
        r_outer = self.size - 30
        r_inner = self.size - 48

        prev_value = self.vmin
        for to_value, color in self.zones:
            a1 = self._value_to_angle(prev_value)
            a2 = self._value_to_angle(to_value)
            self._draw_ring_arc(r_inner, r_outer, a1, a2, color)
            prev_value = to_value

        # Последняя зона до vmax
        if prev_value < self.vmax:
            a1 = self._value_to_angle(prev_value)
            a2 = self._value_to_angle(self.vmax)
            self._draw_ring_arc(r_inner, r_outer, a1, a2, ZONE_GREEN)

    def _draw_ring_arc(self, r_in, r_out, a1, a2, color, steps=40):
        c = self.canvas
        points = []
        for i in range(steps + 1):
            a = a1 + (a2 - a1) * i / steps
            points.append(polar(self.cx, self.cy, r_out, a))
        for i in range(steps, -1, -1):
            a = a1 + (a2 - a1) * i / steps
            points.append(polar(self.cx, self.cy, r_in, a))
        flat = [c for pt in points for c in pt]
        c.create_polygon(*flat, fill=color, outline="")

    # ─── Деления ────────────────────────────────────────────────
    def _draw_ticks(self):
        c = self.canvas
        r_tick_major = self.size - 34
        r_tick_minor = self.size - 40

        # Крупные деления
        v = self.vmin
        while v <= self.vmax + 1e-6:
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, r_tick_major, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 22, a)
            c.create_line(x1, y1, x2, y2, fill=TICK_MAJOR, width=2)
            v += self.major_step

        # Мелкие деления
        v = self.vmin
        while v <= self.vmax + 1e-6:
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, r_tick_minor, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 22, a)
            c.create_line(x1, y1, x2, y2, fill=TICK_MINOR, width=1)
            v += self.minor_step

    # ─── Подписи чисел ──────────────────────────────────────────
    def _draw_labels(self):
        c = self.canvas
        r_label = self.size - 58

        v = self.vmin
        while v <= self.vmax + 1e-6:
            a = self._value_to_angle(v)
            x, y = polar(self.cx, self.cy, r_label, a)
            text = f"{int(v)}" if v == int(v) else f"{v:.0f}"
            c.create_text(x, y, text=text,
                          font=("Segoe UI", 9, "bold"),
                          fill=TEXT)
            v += self.major_step

    def _draw_center_label(self):
        if not self.label:
            return
        self.canvas.create_text(
            self.cx, self.cy + self.size * 0.45,
            text=self.label,
            font=("Segoe UI", 14, "bold"),
            fill=TEXT,
        )

    # ─── Стрелка ────────────────────────────────────────────────
    def _draw_needle(self):
        c = self.canvas
        self._needle_id = None
        self._redraw_needle()

    def _redraw_needle(self):
        c = self.canvas

        # Удаляем старую
        if self._needle_id is not None:
            for item in self._needle_id:
                c.delete(item)

        angle = self._value_to_angle(self.value)
        r = self.size - 45

        # Основание стрелки (короткий хвост) и остриё
        tip_x, tip_y = polar(self.cx, self.cy, r, angle)
        tail_x, tail_y = polar(self.cx, self.cy, -12, angle)

        # Тень стрелки
        shadow = c.create_line(tip_x + 2, tip_y + 3,
                               tail_x + 2, tail_y + 3,
                               fill="#888", width=4,
                               capstyle="round")
        # Тело стрелки
        body = c.create_line(tail_x, tail_y, tip_x, tip_y,
                             fill=self.needle_color, width=5,
                             capstyle="round")
        # Остриё
        tip = c.create_oval(tip_x - 3, tip_y - 3,
                            tip_x + 3, tip_y + 3,
                            fill=self.needle_color, outline="")

        # Центральная шайба
        c.create_oval(self.cx - 12, self.cy - 12,
                      self.cx + 12, self.cy + 12,
                      fill="#e0dcd7", outline="#b0aca8", width=1)
        hub = c.create_oval(self.cx - 8, self.cy - 8,
                            self.cx + 8, self.cy + 8,
                            fill=CENTER, outline="")

        self._needle_id = [shadow, body, tip, hub]

    # ─── Преобразование значения в угол ─────────────────────────
    def _value_to_angle(self, value):
        pct = (value - self.vmin) / (self.vmax - self.vmin)
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    # ─── Установка значения ─────────────────────────────────────
    def set_value(self, value):
        self.value = max(self.vmin, min(self.vmax, value))
        self._redraw_needle()


# ─── Приложение ──────────────────────────────────────────────────
class GaugeApp:
    def __init__(self, root):
        self.root = root
        root.title("Аналоговые приборы")
        root.geometry("1000x680")
        root.minsize(900, 620)
        root.configure(bg=BG)

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Аналоговые измерительные приборы",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Двигайте ползунки — стрелки поворачиваются",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 10))

        # ═══ Основная область ════════════════════════════════════
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=20)

        # ── Термометр ─────────────────────────────────────────
        thermo_frame = tk.Frame(main, bg=BG)
        thermo_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.thermo_canvas = tk.Canvas(thermo_frame, width=420, height=420,
                                       bg=BG, highlightthickness=0)
        self.thermo_canvas.pack()

        self.thermo = AnalogGauge(
            self.thermo_canvas,
            cx=210, cy=210, size=190,
            vmin=-30, vmax=50,
            start_angle=-140, end_angle=140,
            major_step=10, minor_step=5,
            label="°C",
            needle_color=NEEDLE_RED,
        )

        self.thermo_value = tk.Label(thermo_frame, text="0 °C",
                                     font=("Consolas", 18, "bold"),
                                     bg=BG, fg=TEXT)
        self.thermo_value.pack(pady=(6, 4))

        self.thermo_scale = tk.Scale(
            thermo_frame, from_=-30, to=50,
            orient="horizontal", length=380,
            showvalue=False,
            bg=BG, fg=TEXT, troughcolor="#c9c6c1",
            activebackground=NEEDLE_RED,
            highlightthickness=0, bd=0,
            sliderlength=22, width=10,
            command=self.on_thermo_change,
        )
        self.thermo_scale.set(20)
        self.thermo_scale.pack(pady=(0, 20))

        # ── Тахометр ──────────────────────────────────────────
        tacho_frame = tk.Frame(main, bg=BG)
        tacho_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.tacho_canvas = tk.Canvas(tacho_frame, width=420, height=420,
                                      bg=BG, highlightthickness=0)
        self.tacho_canvas.pack()

        self.tacho = AnalogGauge(
            self.tacho_canvas,
            cx=210, cy=210, size=190,
            vmin=0, vmax=120,
            start_angle=-140, end_angle=140,
            major_step=10, minor_step=2,
            label="",
            zones=[
                (50, ZONE_GREEN),
                (80, ZONE_YELLOW),
                (120, ZONE_RED),
            ],
            needle_color=NEEDLE_RED,
        )

        self.tacho_value = tk.Label(tacho_frame, text="0",
                                    font=("Consolas", 18, "bold"),
                                    bg=BG, fg=TEXT)
        self.tacho_value.pack(pady=(6, 4))

        self.tacho_scale = tk.Scale(
            tacho_frame, from_=0, to=120,
            orient="horizontal", length=380,
            showvalue=False,
            bg=BG, fg=TEXT, troughcolor="#c9c6c1",
            activebackground=NEEDLE_RED,
            highlightthickness=0, bd=0,
            sliderlength=22, width=10,
            command=self.on_tacho_change,
        )
        self.tacho_scale.set(45)
        self.tacho_scale.pack(pady=(0, 20))

        # Первичная отрисовка
        self.on_thermo_change(self.thermo_scale.get())
        self.on_tacho_change(self.tacho_scale.get())

    def on_thermo_change(self, value):
        v = float(value)
        self.thermo.set_value(v)
        self.thermo_value.config(text=f"{v:+.1f} °C")

    def on_tacho_change(self, value):
        v = float(value)
        self.tacho.set_value(v)
        self.tacho_value.config(text=f"{int(v)}")


# ─── Запуск ──────────────────────────────────────────────────────
root = tk.Tk()
app = GaugeApp(root)
root.mainloop()
