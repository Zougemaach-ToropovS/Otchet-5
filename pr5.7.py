
import tkinter as tk
import math
import random
from datetime import datetime


# ─── Единая палитра ──────────────────────────────────────────────
BG = "#f4f4f4"
PANEL = "#ffffff"
BORDER = "#d8d8d8"
TEXT = "#1c1c1e"
MUTED = "#888888"

ACCENT = "#2ec4b6"       # циан — прогресс
NEEDLE = "#e53935"       # стрелка
CLOCK_HAND = "#4dabf7"   # стрелки часов
SKY = "#4a90d9"          # авиагоризонт: небо
GROUND = "#8b6f47"       # авиагоризонт: земля
FORK = "#ffcc00"         # вилка авиагоризонта


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# 1. ПРОГРЕСС-ДУГА
# ═══════════════════════════════════════════════════════════════════
class ProgressArc:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 0.0
        self.target = 88.0

        self._draw_static()
        self._draw_dynamic()

    def _draw_static(self):
        c = self.canvas
        r = self.size - 10

        # Фоновая дуга
        c.create_arc(self.cx - r, self.cy - r,
                     self.cx + r, self.cy + r,
                     start=-90, extent=180,
                     style="arc", outline="#e0e0e0", width=6)

        # Метки 0…100
        for v in range(0, 101, 10):
            a = 90 - 180 * v / 100
            x, y = polar(self.cx, self.cy, r + 16, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 8, "bold"),
                          fill=MUTED)

        # Тексты в центре
        self.value_text = c.create_text(
            self.cx, self.cy + 4,
            text="0%",
            font=("Segoe UI", 26, "bold"),
            fill=ACCENT,
        )
        c.create_text(self.cx, self.cy + 36,
                      text="Процент выполнения",
                      font=("Segoe UI", 9),
                      fill=MUTED)

    def _draw_dynamic(self):
        c = self.canvas
        r = self.size - 10
        self.arc_id = c.create_arc(
            self.cx - r, self.cy - r,
            self.cx + r, self.cy + r,
            start=90, extent=0,
            style="arc", outline=ACCENT, width=8,
        )
        self.dot_id = c.create_oval(0, 0, 0, 0,
                                    fill=ACCENT, outline="#ffffff", width=2)

    def set_value(self, v):
        self.target = max(0, min(100, v))

    def _redraw(self):
        c = self.canvas
        r = self.size - 10
        extent = -180 * (self.value / 100)

        c.itemconfig(self.arc_id, extent=extent)
        c.itemconfig(self.value_text, text=f"{int(round(self.value))}%")

        # Точка в конце дуги
        end_angle = 90 + extent
        x, y = polar(self.cx, self.cy, r, end_angle)
        c.coords(self.dot_id, x - 7, y - 7, x + 7, y + 7)

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.3:
            self.value += diff * 0.15
        else:
            self.value = self.target
        self._redraw()


# ═══════════════════════════════════════════════════════════════════
# 2. СПИДОМЕТР
# ═══════════════════════════════════════════════════════════════════
class RoundDial:
    def __init__(self, canvas, cx, cy, size, vmin=0, vmax=120):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.vmin = vmin
        self.vmax = vmax
        self.value = 0.0
        self.target = 65.0
        self.start_angle = -135
        self.end_angle = 135

        self._draw_case()
        self._draw_zones()
        self._draw_ticks()
        self._draw_labels()
        self._draw_center_value()
        self._draw_needle()

    def _draw_case(self):
        c = self.canvas
        s = self.size
        c.create_oval(self.cx - s - 4, self.cy - s - 4,
                      self.cx + s + 4, self.cy + s + 4,
                      fill="#2c2c2c", outline="#1a1a1a", width=1)
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill="#4a4a4a", outline="#5a5a5a", width=1)
        c.create_oval(self.cx - s + 14, self.cy - s + 14,
                      self.cx + s - 14, self.cy + s - 14,
                      fill="#3a3a3a", outline="")

    def _draw_zones(self):
        c = self.canvas
        r = self.size - 18
        # Зелёная 0…40
        c.create_arc(self.cx - r, self.cy - r,
                     self.cx + r, self.cy + r,
                     start=45, extent=-108,
                     style="arc", outline="#2ecc71", width=8)
        # Жёлтая 40…70
        c.create_arc(self.cx - r, self.cy - r,
                     self.cx + r, self.cy + r,
                     start=-63, extent=-81,
                     style="arc", outline="#f4b400", width=8)
        # Красная 70…100
        c.create_arc(self.cx - r, self.cy - r,
                     self.cx + r, self.cy + r,
                     start=-144, extent=-81,
                     style="arc", outline="#e53935", width=8)

    def _draw_ticks(self):
        c = self.canvas
        for v in range(self.vmin, self.vmax + 1, 10):
            a = self._value_to_angle(v)
            x1, y1 = polar(self.cx, self.cy, self.size - 28, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 20, a)
            c.create_line(x1, y1, x2, y2, fill="#e8e8e8", width=2)

    def _draw_labels(self):
        c = self.canvas
        for v in range(self.vmin, self.vmax + 1, 20):
            a = self._value_to_angle(v)
            x, y = polar(self.cx, self.cy, self.size - 42, a)
            c.create_text(x, y, text=str(v),
                          font=("Segoe UI", 8),
                          fill="#e8e8e8")

    def _draw_center_value(self):
        c = self.canvas
        c.create_oval(self.cx - 22, self.cy - 22,
                      self.cx + 22, self.cy + 22,
                      fill="#ffffff", outline="#d0d0d0", width=1)
        self.value_text = c.create_text(
            self.cx, self.cy,
            text="0",
            font=("Segoe UI", 18, "bold"),
            fill="#1a1a1a",
        )

    def _draw_needle(self):
        c = self.canvas
        self.needle_id = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size + 32,
            fill=NEEDLE, width=3, capstyle="round",
        )
        c.create_oval(self.cx - 5, self.cy - 5,
                      self.cx + 5, self.cy + 5,
                      fill="#1a1a1a", outline="")

    def _value_to_angle(self, value):
        pct = (value - self.vmin) / (self.vmax - self.vmin)
        return self.start_angle + (self.end_angle - self.start_angle) * pct

    def set_value(self, v):
        self.target = max(self.vmin, min(self.vmax, v))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) > 0.2:
            self.value += diff * 0.2
        else:
            self.value = self.target

        a = self._value_to_angle(self.value)
        x, y = polar(self.cx, self.cy, self.size - 32, a)
        tail_x, tail_y = polar(self.cx, self.cy, -6, a)

        self.canvas.coords(self.needle_id,
                           tail_x, tail_y, x, y)
        self.canvas.itemconfig(self.value_text,
                               text=str(int(round(self.value))))


# ═══════════════════════════════════════════════════════════════════
# 3. ЧАСЫ (реальное время)
# ═══════════════════════════════════════════════════════════════════
class SimpleClock:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        self._draw_case()
        self._draw_ticks()
        self._draw_hands()
        self._update_time()

    def _draw_case(self):
        c = self.canvas
        s = self.size
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill="#1a1a1a", outline="#000000", width=2)

    def _draw_ticks(self):
        c = self.canvas
        for i in range(12):
            a = i * 30
            x1, y1 = polar(self.cx, self.cy, self.size - 6, a)
            x2, y2 = polar(self.cx, self.cy, self.size - 18, a)
            c.create_line(x1, y1, x2, y2, fill="#ffffff", width=3)

    def _draw_hands(self):
        c = self.canvas
        # Часовая (толстая, короткая)
        self.hour_hand = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.4,
            fill=CLOCK_HAND, width=6, capstyle="round",
        )
        # Минутная (средняя)
        self.minute_hand = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.65,
            fill=CLOCK_HAND, width=4, capstyle="round",
        )
        # Секундная (тонкая, красная)
        self.second_hand = c.create_line(
            self.cx, self.cy, self.cx, self.cy - self.size * 0.75,
            fill="#e53935", width=2, capstyle="round",
        )
        # Центр
        c.create_oval(self.cx - 6, self.cy - 6,
                      self.cx + 6, self.cy + 6,
                      fill=CLOCK_HAND, outline="")

    def _update_time(self):
        now = datetime.now()
        h = now.hour % 12
        m = now.minute
        s = now.second

        # Часовая
        a = (h + m / 60) * 30
        x, y = polar(self.cx, self.cy, self.size * 0.4, a)
        self.canvas.coords(self.hour_hand, self.cx, self.cy, x, y)

        # Минутная
        a = (m + s / 60) * 6
        x, y = polar(self.cx, self.cy, self.size * 0.65, a)
        self.canvas.coords(self.minute_hand, self.cx, self.cy, x, y)

        # Секундная
        a = s * 6
        x, y = polar(self.cx, self.cy, self.size * 0.75, a)
        self.canvas.coords(self.second_hand, self.cx, self.cy, x, y)

        self.canvas.after(1000, self._update_time)


# ═══════════════════════════════════════════════════════════════════
# 4. АВИАГОРИЗОНТ
# ═══════════════════════════════════════════════════════════════════
class AttitudeDial:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        self.pitch = 0.0        # тангаж
        self.roll = 0.0         # крен
        self.target_pitch = 10.0
        self.target_roll = 0.0

        self._draw_case()
        self._draw_inner()
        self._draw_fork_and_marks()

    def _draw_case(self):
        c = self.canvas
        s = self.size
        c.create_oval(self.cx - s - 2, self.cy - s - 2,
                      self.cx + s + 2, self.cy + s + 2,
                      fill="#3a3a3a", outline="#1a1a1a", width=2)
        c.create_oval(self.cx - s, self.cy - s,
                      self.cx + s, self.cy + s,
                      fill="#e8e8e8", outline="#a0a0a0", width=1)

    def _draw_inner(self):
        c = self.canvas
        s = self.size - 8

        # Контейнер для подвижной части
        self.sky_id = c.create_oval(self.cx - s, self.cy - s,
                                    self.cx + s, self.cy + s,
                                    fill=SKY, outline="")
        self.ground_id = c.create_arc(
            self.cx - s, self.cy - s,
            self.cx + s, self.cy + s,
            start=0, extent=180,
            fill=GROUND, outline="", style="chord",
        )

        # Линия горизонта
        self.horizon_id = c.create_line(
            self.cx - s, self.cy, self.cx + s, self.cy,
            fill="#ffffff", width=2,
        )

        # Метки тангажа
        self.pitch_marks = []
        for p in (-30, -20, -10, 10, 20, 30):
            y = self.cy - (p / 30) * s * 0.55
            w = 30 if abs(p) % 20 == 0 else 20
            line_id = c.create_line(self.cx - w, y, self.cx + w, y,
                                    fill="#ffffff", width=1)
            text_l = c.create_text(self.cx - w - 6, y, text=str(p),
                                   font=("Segoe UI", 6, "bold"),
                                   fill="#ffffff", anchor="e")
            text_r = c.create_text(self.cx + w + 6, y, text=str(p),
                                   font=("Segoe UI", 6, "bold"),
                                   fill="#ffffff", anchor="w")
            self.pitch_marks.append((line_id, text_l, text_r, p))

    def _draw_fork_and_marks(self):
        c = self.canvas
        s = self.size - 18

        # Неподвижная жёлтая вилка
        c.create_line(self.cx - 16, self.cy - s + 8,
                      self.cx - 16, self.cy - 4, fill=FORK, width=3)
        c.create_line(self.cx + 16, self.cy - s + 8,
                      self.cx + 16, self.cy - 4, fill=FORK, width=3)
        c.create_line(self.cx - 8, self.cy - 8,
                      self.cx, self.cy - s + 8, fill=FORK, width=2)
        c.create_line(self.cx + 8, self.cy - 8,
                      self.cx, self.cy - s + 8, fill=FORK, width=2)

        # Неподвижные центральные метки
        c.create_line(self.cx - 30, self.cy,
                      self.cx - 10, self.cy, fill="#ffffff", width=2)
        c.create_line(self.cx + 10, self.cy,
                      self.cx + 30, self.cy, fill="#ffffff", width=2)
        c.create_oval(self.cx - 3, self.cy - 3,
                      self.cx + 3, self.cy + 3,
                      fill="#ffffff", outline="")

    def set_pitch(self, p):
        self.target_pitch = max(-45, min(45, p))

    def set_roll(self, r):
        self.target_roll = max(-45, min(45, r))

    def tick(self):
        diff_p = self.target_pitch - self.pitch
        diff_r = self.target_roll - self.roll
        if abs(diff_p) > 0.2:
            self.pitch += diff_p * 0.15
        else:
            self.pitch = self.target_pitch
        if abs(diff_r) > 0.2:
            self.roll += diff_r * 0.15
        else:
            self.roll = self.target_roll

        self._redraw_inner()

    def _redraw_inner(self):
        c = self.canvas
        s = self.size - 8

        # Сдвиг горизонта по тангажу
        dy = (self.pitch / 30) * s * 0.55

        # Синяя область — круг, но сдвигаем внутренние элементы
        c.coords(self.horizon_id,
                 self.cx - s, self.cy + dy,
                 self.cx + s, self.cy + dy)

        # Подвижные метки тангажа
        for line_id, text_l, text_r, p in self.pitch_marks:
            y = self.cy - (p / 30) * s * 0.55 + dy
            w = 30 if abs(p) % 20 == 0 else 20
            c.coords(line_id, self.cx - w, y, self.cx + w, y)
            c.coords(text_l, self.cx - w - 6, y)
            c.coords(text_r, self.cx + w + 6, y)


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class FourGaugesApp:
    def __init__(self, root):
        self.root = root
        root.title("Четыре живых индикатора")
        root.geometry("1200x560")
        root.minsize(1100, 540)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.demo_running = False
        self.demo_dir = 1

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="Четыре живых индикатора",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 4))

        tk.Label(root, text="Часы идут · ползунки меняют приборы · «Демо» оживляет всё",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 10))

        # ═══ Панель с приборами ══════════════════════════════════
        panel = tk.Frame(root, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        panel.pack(padx=20, pady=(0, 12))

        self.canvas = tk.Canvas(panel, width=1140, height=240,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # ── Создаём приборы ──────────────────────────────────
        self.progress = ProgressArc(self.canvas, cx=140, cy=140, size=90)
        self.dial = RoundDial(self.canvas, cx=400, cy=130, size=85)
        self.clock = SimpleClock(self.canvas, cx=660, cy=130, size=80)
        self.attitude = AttitudeDial(self.canvas, cx=920, cy=130, size=90)

        # ═══ Управление ══════════════════════════════════════════
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(padx=20, pady=(0, 16))

        # Прогресс
        self._slider(ctrl, "Прогресс, %", 0, 100, 88,
                     lambda v: self.progress.set_value(v))

        # Скорость
        self._slider(ctrl, "Скорость", 0, 120, 65,
                     lambda v: self.dial.set_value(v))

        # Тангаж
        self._slider(ctrl, "Тангаж", -45, 45, 10,
                     lambda v: self.attitude.set_pitch(v))

        # Крен
        self._slider(ctrl, "Крен", -45, 45, 0,
                     lambda v: self.attitude.set_roll(v))

        # Кнопка Демо
        self.btn_demo = tk.Button(ctrl, text="▶  Демо",
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#2ecc71", fg="#ffffff",
                                  activebackground="#20a544",
                                  activeforeground="#ffffff",
                                  bd=0, padx=20, pady=10,
                                  cursor="hand2",
                                  command=self.toggle_demo)
        self.btn_demo.grid(row=0, column=4, padx=(16, 4))

        # ═══ Общий тик ═══════════════════════════════════════════
        self._tick()

    def _slider(self, parent, label, vmin, vmax, init, callback):
        frame = tk.Frame(parent, bg=BG)
        frame.grid(row=0, column=len(parent.grid_slaves()), padx=8, pady=4)

        tk.Label(frame, text=label, font=("Segoe UI", 9),
                 bg=BG, fg=MUTED).pack(anchor="w")

        scale = tk.Scale(frame, from_=vmin, to=vmax,
                         orient="horizontal", length=180,
                         showvalue=True,
                         font=("Segoe UI", 8),
                         bg=BG, fg=TEXT,
                         troughcolor="#d8d8d8",
                         activebackground=ACCENT,
                         highlightthickness=0, bd=0,
                         sliderlength=18, width=8,
                         command=callback)
        scale.set(init)
        scale.pack()

    def toggle_demo(self):
        self.demo_running = not self.demo_running
        if self.demo_running:
            self.btn_demo.config(text="⏹  Стоп", bg="#e53935")
        else:
            self.btn_demo.config(text="▶  Демо", bg="#2ecc71")

    def _tick(self):
        # Обычные тики приборов
        self.progress.tick()
        self.dial.tick()
        self.attitude.tick()

        # Демо — меняем все значения сразу
        if self.demo_running:
            self.demo_dir *= -1 if random.random() < 0.05 else 1
            self.progress.set_value(random.uniform(20, 100))
            self.dial.set_value(random.uniform(0, 120))
            self.attitude.set_pitch(random.uniform(-30, 30))
            self.attitude.set_roll(random.uniform(-30, 30))

        self.root.after(60, self._tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FourGaugesApp(root)
    root.mainloop()
