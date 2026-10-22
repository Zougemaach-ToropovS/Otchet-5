
import tkinter as tk
import math
import random
from datetime import datetime


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#ffffff"
PANEL = "#ffffff"
BORDER = "#e0e0e0"
TEXT = "#1c1c1e"
MUTED = "#888888"

BLUE = "#4dabf7"
GREEN = "#2ecc71"
RED = "#e53935"
DARK = "#1a1a1a"
LIGHT = "#e0e0e0"
TICK = "#333333"


def polar(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# 1. КРУГОВОЙ ПРОГРЕСС
# ═══════════════════════════════════════════════════════════════════
class CircleProgress:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 0.0

        c = canvas
        r = size
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=DARK, outline="")
        c.create_oval(cx - r - 3, cy - r - 3,
                      cx + r + 3, cy + r + 3,
                      outline=LIGHT, width=1)

        # Дуга: extent не может быть ровно -360 — поэтому -359.9
        # Начинаем с 90° (сверху) и идём по часовой (минус extent)
        self.arc_id = c.create_arc(
            cx - r + 8, cy - r + 8,
            cx + r - 8, cy + r - 8,
            start=90, extent=-0.1,
            style="arc", outline=BLUE, width=8,
        )
        self.dot_id = c.create_oval(0, 0, 0, 0, fill=BLUE, outline="")

        self._redraw()

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
        c = self.canvas
        r = self.size - 8
        # Ограничиваем -359.9, чтобы Tkinter не схлопнул дугу
        extent = -359.9 * (self.value / 100.0)
        c.itemconfig(self.arc_id, extent=max(-359.9, extent))

        end_angle = 90 + extent
        x, y = polar(self.cx, self.cy, r, end_angle)
        c.coords(self.dot_id, x - 9, y - 9, x + 9, y + 9)


# ═══════════════════════════════════════════════════════════════════
# 2. КОЛЬЦЕВОЙ ИНДИКАТОР
# ═══════════════════════════════════════════════════════════════════
class RingGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 0.0

        c = canvas
        r = size
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill="#f5f5f5", outline=LIGHT, width=1)
        c.create_oval(cx - r + 10, cy - r + 10,
                      cx + r - 10, cy + r - 10,
                      fill="#ffffff", outline="")

        for i in range(40):
            a = 360 * i / 40
            x1, y1 = polar(cx, cy, r - 6, a)
            x2, y2 = polar(cx, cy, r - 16, a)
            c.create_line(x1, y1, x2, y2, fill="#cccccc", width=1)

        # Кольцо: extent не может быть -360, ограничиваем
        self.ring_id = c.create_arc(
            cx - r + 18, cy - r + 18,
            cx + r - 18, cy + r - 18,
            start=90, extent=-0.1,
            style="arc", outline=GREEN, width=14,
        )

        self.value_text = c.create_text(
            cx, cy, text="0",
            font=("Segoe UI", 28, "bold"),
            fill=GREEN,
        )

    def set_value(self, v):
        self.target = max(0.0, min(100.0, float(v)))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) < 0.3:
            self.value = self.target
        else:
            self.value += diff * 0.15
        c = self.canvas
        extent = -359.9 * self.value / 100.0
        c.itemconfig(self.ring_id, extent=max(-359.9, extent))
        c.itemconfig(self.value_text, text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# 3. ДУГОВОЙ ИНДИКАТОР — 0 слева, 100 справа, через ВЕРХ
# ═══════════════════════════════════════════════════════════════════
class ArcRuler:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 0.0

        c = canvas
        r = size

        # 0 — слева, 100 — справа. Углы:
        # 0% → 270° (слева), 100% → 90° (справа) — но мы хотим через ВЕРХ
        # т.е. 0% → 180+90 = 270° слева, 100% → 90° справа. Но угол идёт по часовой.
        # Проще: 0% → -90° (это справа-снизу), 100% → -90+180 = 90° (слева-снизу)? Нет.
        # Правильно: 0% → 270° (слева), 100% → 270+180 = 450° = 90° (справа).
        # Но тогда дуга идёт ЧЕРЕЗ НИЗ. Нам надо через ВЕРХ.
        # Значит: 0% → 270° (слева), 100% → 270-180 = 90° (справа) — но идём через верх.

        for v in range(0, 101, 20):
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 5, a)
            x2, y2 = polar(cx, cy, r - 25, a)
            c.create_line(x1, y1, x2, y2, fill=TICK, width=2)
            x, y = polar(cx, cy, r - 42, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 9, "bold"), fill=TEXT)

        for v in range(0, 101, 5):
            if v % 20 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 5, a)
            x2, y2 = polar(cx, cy, r - 15, a)
            c.create_line(x1, y1, x2, y2, fill="#666", width=1)

        for v in range(0, 101):
            if v % 5 == 0:
                continue
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 5, a)
            x2, y2 = polar(cx, cy, r - 10, a)
            c.create_line(x1, y1, x2, y2, fill="#999", width=1)

        self.value_text = c.create_text(
            cx, cy, text="0",
            font=("Segoe UI", 36, "bold"),
            fill="#333",
        )

    def _value_to_angle(self, value):
        # 0% → 270° (слева), 100% → 90° (справа), через верх
        # В Tkinter углы идут по часовой от 12 часов.
        # 270° = 9 часов (слева), 90° = 3 часа (справа).
        # Чтобы попасть из 270 в 90 через верх (12 часов) — надо идти в сторону
        # уменьшения угла: 270 → 180 (6 часов) → 90. Это НЕ через верх.
        # Правильный путь через верх: 270 → 315 → 360=0 → 45 → 90. То есть увеличивать.
        # Значит формула: angle = 270 + 180 * (value/100) — но 450 = 90.
        # Это верно: 270 + 180*1 = 450 = 90 (mod 360) — справа.
        return 270 + 180 * (value / 100.0)

    def set_value(self, v):
        self.target = max(0.0, min(100.0, float(v)))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) < 0.3:
            self.value = self.target
        else:
            self.value += diff * 0.15
        self.canvas.itemconfig(self.value_text,
                               text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# 4. СПИДОМЕТР
# ═══════════════════════════════════════════════════════════════════
class ArcSpeedometer:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 0.0

        c = canvas
        r = size

        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill="#f8f8f8", outline=LIGHT, width=1)

        # Фон — серая дуга 180° (от 180° до 360°): слева-снизу → через верх → справа-снизу
        # Tkinter: start=180 — это 6 часов снизу. Идём extent=-180 против часовой до 0° (12 часов)?
        # Нам надо: start на 9 часах (270°), extent=180 (по часовой к 3 часам — но через низ).
        # Точнее: 9 часов (270°) + 180° по часовой = 90° (3 часа) через НИЗ.
        # Через ВЕРХ: 9 часов (270°) - 180° = 90°. То есть extent=-180.
        c.create_arc(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                     start=180, extent=180,
                     style="arc", outline=LIGHT, width=8)

        # Красная зона 70…100% — правая часть дуги
        # 70% → 180 + 180*0.7 = 306° = -54° (правая-нижняя)
        # 100% → 180 + 180 = 360° = 0° (верх)
        # То есть красная зона от 306° до 0° (через правую-верхнюю четверть).
        # Значит start=306, extent=54 (по часовой к 0°).
        c.create_arc(cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
                     start=-54, extent=54,
                     style="arc", outline=RED, width=8)

        # Голубая дуга — динамическая, start=180, extent растёт от 0 до 180
        self.arc_id = c.create_arc(
            cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6,
            start=180, extent=0.1,
            style="arc", outline=BLUE, width=8,
        )

        # Деления
        for i in range(11):
            v = i * 10
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 14, a)
            x2, y2 = polar(cx, cy, r - 24, a)
            c.create_line(x1, y1, x2, y2, fill=TICK, width=1)
            x, y = polar(cx, cy, r - 40, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 8), fill=MUTED)

        # Центр
        c.create_oval(cx - 22, cy - 22, cx + 22, cy + 22,
                      fill="#ffffff", outline=LIGHT)

        self.value_text = c.create_text(
            cx, cy, text="0",
            font=("Segoe UI", 14, "bold"),
            fill=RED,
        )

        self.needle_id = c.create_line(
            cx, cy, cx, cy - r + 34,
            fill=RED, width=3, capstyle="round",
        )

    def _value_to_angle(self, value):
        # 0% → 180° (слева внизу), 100% → 360°=0° (справа внизу), через ВЕРХ
        # Но Tkinter: 0° — сверху. 180° — снизу. Нам надо: 0% на 9 часах (270°),
        # 100% на 3 часах (90°), через верх.
        # Это 270° - 180°*(value/100) — идём в сторону уменьшения.
        # 0% → 270°, 100% → 90°. Идём через 180° (низ)? Нет, 270 → 90 через 180 = через низ.
        # Через верх: 270 → 360 → 90 = увеличение: 270 + 180 * (value/100).
        return 270 + 180 * (value / 100.0)

    def set_value(self, v):
        self.target = max(0.0, min(100.0, float(v)))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) < 0.2:
            self.value = self.target
        else:
            self.value += diff * 0.15

        c = self.canvas
        # extent от 0.1 до 179.9 (полный 180 в Tkinter тоже работает)
        extent = 180 * self.value / 100.0
        c.itemconfig(self.arc_id, extent=max(0.1, extent))

        a = self._value_to_angle(self.value)
        x, y = polar(self.cx, self.cy, self.size - 34, a)
        c.coords(self.needle_id, self.cx, self.cy, x, y)
        c.itemconfig(self.value_text, text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# 5. РАДИО-ШКАЛА
# ═══════════════════════════════════════════════════════════════════
class RadioGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 0.0

        # Углы: 0% → -160° (лево-низ), 100% → -20° (право-низ), через верх
        self.start_angle = -160
        self.end_angle = -20

        c = canvas
        r = size

        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill="#f8f8f8", outline=LIGHT, width=1)

        for i in range(41):
            v = i * (100 / 40)
            a = self._value_to_angle(v)
            x1, y1 = polar(cx, cy, r - 6, a)
            x2, y2 = polar(cx, cy, r - 14, a)
            c.create_line(x1, y1, x2, y2, fill="#c8c8c8", width=1)

        self.arc_id = c.create_arc(
            cx - r + 10, cy - r + 10,
            cx + r - 10, cy + r - 10,
            start=self.start_angle, extent=0.1,
            style="arc", outline=BLUE, width=6,
        )

        # Синие метки скорости
        for text, v in [("0M", 0), ("25M", 25), ("50M", 50),
                        ("75M", 75), ("100M", 100)]:
            a = self._value_to_angle(v)
            x, y = polar(cx, cy, r - 26, a)
            c.create_text(x, y, text=text,
                          font=("Segoe UI", 8, "bold"), fill=BLUE)

        # Серые метки Mbps
        for text, v in [("13M", 13), ("38M", 38), ("63M", 63), ("88M", 88)]:
            a = self._value_to_angle(v)
            x, y = polar(cx, cy, r - 48, a)
            c.create_text(x, y, text=text,
                          font=("Segoe UI", 7), fill=MUTED)

        # Стрелка-игла (тонкая, не треугольник)
        self.needle_id = c.create_line(
            cx, cy, cx, cy - r + 34,
            fill=BLUE, width=3, capstyle="round",
        )
        c.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                      fill=BLUE, outline="")

        # Подписи Mbps и индикатор
        c.create_text(cx, cy + 22, text="Mbps",
                      font=("Segoe UI", 8), fill=MUTED)

        for i, h in enumerate([6, 12, 18]):
            c.create_rectangle(cx - 12 + i * 10, cy + 32 - h,
                               cx - 6 + i * 10, cy + 32,
                               fill="#c8c8c8", outline="")

        self.value_text = c.create_text(
            cx - 34, cy + 32, text="0",
            font=("Segoe UI", 9, "bold"), fill=TEXT,
        )

    def _value_to_angle(self, value):
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

        c = self.canvas
        extent = (self.end_angle - self.start_angle) * self.value / 100.0
        c.itemconfig(self.arc_id, extent=max(0.1, extent))

        a = self._value_to_angle(self.value)
        x, y = polar(self.cx, self.cy, self.size - 34, a)
        c.coords(self.needle_id, self.cx, self.cy, x, y)

        c.itemconfig(self.value_text, text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class FiveGaugesApp:
    def __init__(self, root):
        self.root = root
        root.title("Пять живых индикаторов")
        root.geometry("1200x640")
        root.minsize(1100, 620)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.auto_mode = False
        self.auto_phase = 0.0

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Пять живых индикаторов",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 4))

        tk.Label(root, text="Ползунки меняют приборы · кнопка «Авто» оживляет всё",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 12))

        # ═══ Панель с приборами ══════════════════════════════════
        panel = tk.Frame(root, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        panel.pack(padx=20, pady=(0, 16))

        self.canvas = tk.Canvas(panel, width=1140, height=240,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ── Приборы ──────────────────────────────────────────
        self.circle_progress = CircleProgress(self.canvas, cx=120, cy=140, size=90)
        self.ring_gauge = RingGauge(self.canvas, cx=340, cy=140, size=90)
        self.arc_ruler = ArcRuler(self.canvas, cx=560, cy=140, size=90)
        self.arc_speedo = ArcSpeedometer(self.canvas, cx=780, cy=140, size=90)
        self.radio_gauge = RadioGauge(self.canvas, cx=1000, cy=140, size=90)

        # ═══ Управление ══════════════════════════════════════════
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(padx=20, pady=(0, 16))

        self.sliders = []
        self._slider(ctrl, "Прогресс", self.circle_progress, 0)
        self._slider(ctrl, "Кольцо", self.ring_gauge, 1)
        self._slider(ctrl, "Шкала", self.arc_ruler, 2)
        self._slider(ctrl, "Спидо", self.arc_speedo, 3)
        self._slider(ctrl, "Радио", self.radio_gauge, 4)

        # ── Кнопка «Авто» ─────────────────────────────────────
        self.btn_auto = tk.Button(
            ctrl, text="▶  Авто",
            font=("Segoe UI", 12, "bold"),
            bg=GREEN, fg="#ffffff",
            activebackground="#20a544", activeforeground="#ffffff",
            bd=0, padx=24, pady=14, cursor="hand2",
            command=self.toggle_auto,
        )
        self.btn_auto.grid(row=0, column=5, padx=(24, 4))

        # ═══ Тик-цикл ════════════════════════════════════════════
        self._tick()

    def _slider(self, parent, label, gauge, col):
        frame = tk.Frame(parent, bg=BG)
        frame.grid(row=0, column=col, padx=8, pady=4)

        tk.Label(frame, text=label, font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(anchor="w")

        value_label = tk.Label(frame, text="0",
                               font=("Segoe UI", 10, "bold"),
                               bg=BG, fg=TEXT)
        value_label.pack()

        scale = tk.Scale(frame, from_=0, to=100,
                         orient="horizontal", length=160,
                         showvalue=False,
                         bg=BG, fg=TEXT,
                         troughcolor="#d8d8d8",
                         activebackground=BLUE,
                         highlightthickness=0, bd=0,
                         sliderlength=18, width=8,
                         command=lambda v, g=gauge, vl=value_label:
                             self._on_slider(v, g, vl))
        scale.set(0)
        scale.pack()

        self.sliders.append({"scale": scale, "label": value_label})

    def _on_slider(self, v, gauge, value_label):
        # Если в авто-режиме — игнорируем движение ползунка
        if self.auto_mode:
            return
        val = float(v)
        gauge.set_value(val)
        value_label.config(text=str(int(val)))

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_auto.config(text="⏹  Стоп", bg=RED,
                                 activebackground="#a82419")
            self.auto_phase = 0.0
        else:
            self.btn_auto.config(text="▶  Авто", bg=GREEN,
                                 activebackground="#20a544")

    def _tick(self):
        # Авто-режим — волновые движения всех приборов
        if self.auto_mode:
            self.auto_phase += 0.05
            for i, gauge in enumerate([self.circle_progress,
                                       self.ring_gauge,
                                       self.arc_ruler,
                                       self.arc_speedo,
                                       self.radio_gauge]):
                val = 50 + 45 * math.sin(self.auto_phase + i * 0.7)
                gauge.set_value(val)

            # Синхронизируем ползунки
            for i, sl in enumerate(self.sliders):
                v = 50 + 45 * math.sin(self.auto_phase + i * 0.7)
                sl["scale"].set(v)
                sl["label"].config(text=str(int(v)))

        # Тики всех приборов
        self.circle_progress.tick()
        self.ring_gauge.tick()
        self.arc_ruler.tick()
        self.arc_speedo.tick()
        self.radio_gauge.tick()

        self.root.after(33, self._tick)   # 30 FPS


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FiveGaugesApp(root)
    root.mainloop()
