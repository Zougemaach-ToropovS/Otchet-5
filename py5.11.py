import tkinter as tk
import math
import random


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#ffffff"
PANEL = "#ffffff"
BORDER = "#e0e0e0"
TEXT = "#1c1c1e"
MUTED = "#888888"

RING_RED = "#c0202a"            # красная окантовка
CASE_DARK = "#2a3a52"           # тёмно-синий корпус
CASE_INNER = "#4a5f7a"          # светлее внутри
DIAL_BLUE = "#5a7290"           # синий циферблат
DIAL_LIGHT = "#7a92b0"          # светлый оттенок
DIAL_DARK = "#3a4a62"           # тёмный оттенок

NORTH_RED = "#e02a2a"           # северная половина стрелки
SOUTH_BLUE = "#3a8ed0"          # южная половина стрелки
CENTER_WHITE = "#f0f0f0"
CENTER_DOT = "#1a1a1a"

TICK_WHITE = "#ffffff"


# ─── Утилиты ─────────────────────────────────────────────────────
def polar(cx, cy, r, angle_deg):
    """0° = север (вверх), по часовой."""
    rad = math.radians(angle_deg - 90)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


# ═══════════════════════════════════════════════════════════════════
# КОМПАС
# ═══════════════════════════════════════════════════════════════════
class Compass:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size

        # Азимут (0 = север, по часовой)
        self.heading = 0.0
        self.target = 0.0

        c = canvas
        r = size

        # ─── Внешний красный ободок ─────────────────────────
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=RING_RED, outline="")

        # ─── Тёмно-синий корпус ─────────────────────────────
        c.create_oval(cx - r + 6, cy - r + 6,
                      cx + r - 6, cy + r - 6,
                      fill=CASE_DARK, outline="")

        # ─── Внутренний градиент — светлее к центру ─────────
        for i in range(6):
            ratio = i / 6
            radius = (r - 14) * (1 - ratio * 0.7)
            # Цвет от тёмного к синему
            color = self._lerp(CASE_INNER, DIAL_BLUE, ratio)
            c.create_oval(cx - radius, cy - radius,
                          cx + radius, cy + radius,
                          fill="", outline=color, width=8)

        # ─── Центральный синий круг ────────────────────────
        dial_r = r - 40
        c.create_oval(cx - dial_r, cy - dial_r,
                      cx + dial_r, cy + dial_r,
                      fill=DIAL_BLUE, outline="")

        # ─── Верхний светлый блик на циферблате ────────────
        c.create_arc(cx - dial_r + 4, cy - dial_r + 4,
                     cx + dial_r - 4, cy + dial_r - 4,
                     start=20, extent=140,
                     style="chord",
                     fill=DIAL_LIGHT, outline="")

        # ─── Буквы N S E W ─────────────────────────────────
        letter_r = dial_r - 26
        self._draw_letter(cx, cy, letter_r, 0, "N", NORTH_RED)
        self._draw_letter(cx, cy, letter_r, 90, "E", TICK_WHITE)
        self._draw_letter(cx, cy, letter_r, 180, "S", TICK_WHITE)
        self._draw_letter(cx, cy, letter_r, 270, "W", TICK_WHITE)

        # ─── 4 белые риски по диагоналям ───────────────────
        for a in (45, 135, 225, 315):
            x1, y1 = polar(cx, cy, dial_r - 12, a)
            x2, y2 = polar(cx, cy, dial_r - 4, a)
            c.create_line(x1, y1, x2, y2, fill=TICK_WHITE, width=4,
                          capstyle="round")

        # ─── Стрелка (динамическая) ────────────────────────
        # Северная половина (красная)
        self.north_poly = c.create_polygon(
            0, 0, 0, 0, 0, 0,
            fill=NORTH_RED, outline="",
        )
        # Южная половина (синяя)
        self.south_poly = c.create_polygon(
            0, 0, 0, 0, 0, 0,
            fill=SOUTH_BLUE, outline="",
        )

        # ─── Центральная шайба ─────────────────────────────
        c.create_oval(cx - 12, cy - 12,
                      cx + 12, cy + 12,
                      fill=CENTER_WHITE, outline="#888888", width=1)
        c.create_oval(cx - 5, cy - 5,
                      cx + 5, cy + 5,
                      fill=CENTER_DOT, outline="")

        # ─── Первая отрисовка ──────────────────────────────
        self._redraw_needle()

    def _lerp(self, c1, c2, t):
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = (int(c1[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = (int(c2[i:i+2], 16) for i in (0, 2, 4))
        return "#%02x%02x%02x" % (
            int(r1 + (r2 - r1) * t),
            int(g1 + (g2 - g1) * t),
            int(b1 + (b2 - b1) * t),
        )

    def _draw_letter(self, cx, cy, r, angle, letter, color):
        x, y = polar(cx, cy, r, angle)
        self.canvas.create_text(
            x, y, text=letter,
            font=("Segoe UI", 20, "bold"),
            fill=color,
        )

    def _redraw_needle(self):
        """Рисует красно-синюю стрелку по текущему курсу."""
        c = self.canvas
        cx, cy = self.cx, self.cy
        a = self.heading

        # Длина стрелки
        north_len = self.size - 75
        south_len = self.size - 75

        # Северный конец (остриё)
        nx, ny = polar(cx, cy, north_len, a)
        # Южный конец
        sx, sy = polar(cx, cy, south_len, a + 180)

        # Боковые смещения
        left_x, left_y = polar(cx, cy, 12, a - 90)
        right_x, right_y = polar(cx, cy, 12, a + 90)

        # Северный треугольник (красный)
        c.coords(self.north_poly,
                 nx, ny,
                 left_x, left_y,
                 cx, cy,
                 right_x, right_y)

        # Южный треугольник (синий)
        c.coords(self.south_poly,
                 sx, sy,
                 left_x, left_y,
                 cx, cy,
                 right_x, right_y)

    def set_heading(self, angle):
        """Угол в градусах: 0 = север, по часовой."""
        self.target = angle % 360

    def tick(self):
        # Плавное вращение с учётом перехода через 360°
        diff = self.target - self.heading
        # Нормализуем к [-180, 180]
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360

        if abs(diff) < 0.3:
            self.heading = self.target
        else:
            self.heading = (self.heading + diff * 0.12) % 360

        self._redraw_needle()


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class CompassApp:
    def __init__(self, root):
        self.root = root
        root.title("Компас")
        root.geometry("700x760")
        root.minsize(620, 720)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.auto_mode = False

        # ─── Заголовок ─────────────────────────────────────
        tk.Label(root, text="Компас",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Ползунок меняет курс · кнопки управляют вращением",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 14))

        # ─── Карточка с компасом ───────────────────────────
        panel = tk.Frame(root, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        panel.pack(padx=40, pady=(0, 16))

        self.canvas = tk.Canvas(panel, width=460, height=460,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        self.compass = Compass(self.canvas, cx=230, cy=230, size=200)

        # ─── Подпись курса ─────────────────────────────────
        self.heading_label = tk.Label(root, text="0°  С",
                                      font=("Consolas", 22, "bold"),
                                      bg=BG, fg=RING_RED)
        self.heading_label.pack(pady=(0, 12))

        # ─── Ползунок ──────────────────────────────────────
        self.scale = tk.Scale(root, from_=0, to=359,
                              orient="horizontal", length=460,
                              showvalue=False,
                              bg=BG, fg=TEXT,
                              troughcolor="#d8d8d8",
                              activebackground=RING_RED,
                              highlightthickness=0, bd=0,
                              sliderlength=24, width=12,
                              command=self.on_slider)
        self.scale.set(0)
        self.scale.pack(pady=(0, 14))

        # ─── Кнопки ────────────────────────────────────────
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 20))

        self.btn_north = self._btn(btns, "⬆  Север",
                                   self.go_north,
                                   color="#c0202a")
        self.btn_north.pack(side="left", padx=6)

        self.btn_rotate = self._btn(btns, "🔄  Случайно",
                                    self.random_heading,
                                    color="#3a8ed0")
        self.btn_rotate.pack(side="left", padx=6)

        self.btn_auto = self._btn(btns, "▶  Авто",
                                  self.toggle_auto,
                                  color="#2ea87a")
        self.btn_auto.pack(side="left", padx=6)

        # ─── Тик-цикл ──────────────────────────────────────
        self._tick()

    def _btn(self, parent, text, command, color):
        btn = tk.Button(parent, text=text,
                        font=("Segoe UI", 11, "bold"),
                        bg=color, fg="#ffffff",
                        activebackground=self._darken(color),
                        activeforeground="#ffffff",
                        bd=0, padx=20, pady=12, cursor="hand2",
                        command=command)
        return btn

    def _darken(self, color):
        color = color.lstrip("#")
        r, g, b = (int(color[i:i+2], 16) for i in (0, 2, 4))
        return "#%02x%02x%02x" % (int(r * 0.8), int(g * 0.8), int(b * 0.8))

    # ─── Действия ──────────────────────────────────────────
    def on_slider(self, v):
        if self.auto_mode:
            return
        val = float(v)
        self.compass.set_heading(val)
        self._update_label(val)

    def go_north(self):
        self.auto_mode = False
        self.btn_auto.config(text="▶  Авто", bg="#2ea87a")
        self.scale.set(0)
        self.compass.set_heading(0)
        self._update_label(0)

    def random_heading(self):
        self.auto_mode = False
        self.btn_auto.config(text="▶  Авто", bg="#2ea87a")
        val = random.randint(0, 359)
        self.scale.set(val)
        self.compass.set_heading(val)
        self._update_label(val)

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_auto.config(text="⏹  Стоп",
                                 bg=self._darken("#e53935"))
        else:
            self.btn_auto.config(text="▶  Авто",
                                 bg="#2ea87a")

    def _update_label(self, angle):
        angle = int(round(angle)) % 360
        names = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ", "С"]
        idx = int(round(angle / 45)) % 8
        self.heading_label.config(text=f"{angle}°  {names[idx]}")

    # ─── Тик-цикл ──────────────────────────────────────────
    def _tick(self):
        if self.auto_mode:
            new_target = (self.compass.target + random.uniform(1, 3)) % 360
            self.compass.set_heading(new_target)
            self.scale.set(int(new_target))
            self._update_label(new_target)

        self.compass.tick()

        # Обновляем подпись по текущему значению
        if not self.auto_mode:
            self._update_label(self.compass.heading)

        self.root.after(33, self._tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = CompassApp(root)
    root.mainloop()
