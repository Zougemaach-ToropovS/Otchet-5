import tkinter as tk
import math
import random


BG = "#ffffff"
PANEL = "#ffffff"
BORDER = "#e0e0e0"
TEXT = "#1c1c1e"
MUTED = "#888888"

DARK_BG = "#2a2a2a"
BLUE = "#4dabf7"
GREEN = "#2ea87a"
GREEN_DARK = "#1e8a5c"
GREEN_LIGHT = "#4ade80"
CYAN = "#22d3ee"
CYAN_DARK = "#0891b2"
RED = "#e53935"
RED_LIGHT = "#ff8888"
RED_DEEP = "#b71c1c"
GREEN_BALL = "#2ea87a"
GREEN_BALL_LIGHT = "#66dba5"
GREEN_BALL_DEEP = "#1a6e4a"


# ═══════════════════════════════════════════════════════════════════
# 1. ТЁМНЫЙ КРУГ С ДУГОЙ
# ═══════════════════════════════════════════════════════════════════
class DarkArcGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 65.0
        self.target = 65.0

        c = canvas
        r = size

        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=DARK_BG, outline="")

        # Дуга идёт почти по внешнему краю — отступ 2 px
        self.arc_id = c.create_arc(
            cx - r + 4, cy - r + 4,
            cx + r - 4, cy + r - 4,
            start=180, extent=0,
            style="arc", outline=BLUE, width=8,
        )

        self.text_id = c.create_text(
            cx, cy, text="65%",
            font=("Segoe UI", 22, "bold"),
            fill="#ffffff",
        )
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
        # Дуга идёт от 180° по часовой на 270° максимум
        extent = 270 * (self.value / 100.0)
        self.canvas.itemconfig(self.arc_id, extent=extent)
        self.canvas.itemconfig(self.text_id,
                               text=f"{int(round(self.value))}%")


# ═══════════════════════════════════════════════════════════════════
# 2. ТЁМНЫЙ КРУГ С ЗАЛИВКОЙ — теперь через круг + маску
# ═══════════════════════════════════════════════════════════════════
class DarkFillGauge:
    """
    Заливка снизу — рисуется круг с цветом, сверху маска того же цвета,
    что фон. Маска — прямоугольник ВНУТРИ круга, обрезается сама за счёт
    того, что мы рисуем фон-круг поверх прямоугольника.
    """
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 65.0
        self.target = 65.0
        self.r = size

        c = canvas

        # 1. Тёмный корпус (внешний)
        c.create_oval(cx - size, cy - size, cx + size, cy + size,
                      fill=DARK_BG, outline="", tags="case_bg")

        # 2. Зелёная заливка — КРУГ (тот же размер, что корпус)
        self.fill_oval = c.create_oval(
            cx - size, cy - size, cx + size, cy + size,
            fill=GREEN, outline="", tags="fill"
        )

        # 3. Маска — тёмный круг того же размера, но рисуется поверх
        #    нижняя часть остаётся видимой, верх — закрашивается.
        #    Но так мы не сможем показать нижнюю часть.
        #    Правильнее: маска = прямоугольник сверху + круг сзади.
        #    Решение: используем create_arc — тёмная полусфера сверху.
        self.mask_arc = c.create_arc(
            cx - size, cy - size, cx + size, cy + size,
            start=0, extent=180,
            style="chord", fill=DARK_BG, outline="",
            tags="mask"
        )
        # Но арка сверху закрашивает всё, что выше центра. А нам надо
        # чтобы маска шла по уровню жидкости.
        # Значит: маска = create_polygon, закрашивающий область между
        # верхом круга и уровнем. Плюс круглая обводка.

        self.mask_poly = c.create_polygon(
            0, 0, 0, 0, 0, 0, 0, 0,
            fill=DARK_BG, outline="", tags="mask_poly"
        )

        # 4. Обводка корпуса поверх всего
        c.create_oval(cx - size, cy - size, cx + size, cy + size,
                      fill="", outline="#4a4a4a", width=2, tags="border")

        # 5. Текст
        self.text_id = c.create_text(
            cx, cy, text="65%",
            font=("Segoe UI", 22, "bold"),
            fill="#ffffff", tags="text"
        )

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
        r = self.r
        cx, cy = self.cx, self.cy

        # Уровень: сверху 0%, снизу 100%
        level_y = cy - r + 2 * r * (1 - self.value / 100)

        # Маска = многоугольник, покрывающий верхнюю часть круга.
        # Форма: сверху прямоугольник до level_y, но с закруглением
        # по краям круга. Приближаем: верхняя часть — прямоугольник от
        # верха круга до level_y, а по бокам оставляем только внутри круга.

        # Упрощение: маска рисуется как прямоугольник, но мы "прижимаем"
        # его к circle area — Tkinter это не делает, поэтому по бокам
        # маска не выйдет за круг, если мы закрасим прямоугольник
        # шириной = диаметр.

        # Точки маски — полукруг сверху + прямоугольник до уровня
        pts = []
        # Полукруг сверху (180° — от левого края до правого)
        steps = 30
        for i in range(steps + 1):
            a = 180 - 180 * i / steps  # от 180° до 0°
            rad = math.radians(a - 90)
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            if y <= level_y:
                pts.extend([x, y])
        # Правый нижний угол маски
        pts.extend([cx + r, level_y])
        # Левый нижний угол
        pts.extend([cx - r, level_y])

        if len(pts) >= 6:
            self.canvas.coords(self.mask_poly, *pts)

        self.canvas.itemconfig(self.text_id,
                               text=f"{int(round(self.value))}%")
        self.canvas.tag_raise(self.text_id)


# ═══════════════════════════════════════════════════════════════════
# 3. ВОЛНА + ПУЗЫРЬКИ — обрезаем по кругу
# ═══════════════════════════════════════════════════════════════════
class WaveLiquidGauge:
    def __init__(self, canvas, cx, cy, size):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.size = size
        self.value = 65.0
        self.target = 65.0
        self.r = size

        self.phase = 0.0
        self.bubbles = []

        c = canvas

        # Тёмный фон
        c.create_oval(cx - size, cy - size, cx + size, cy + size,
                      fill=DARK_BG, outline="", tags="case_bg")

        # Жидкость — рисуем как круг, обрезаем сверху маской
        self.fill_oval = c.create_oval(
            cx - size, cy - size, cx + size, cy + size,
            fill=CYAN, outline="", tags="fill"
        )

        # Маска (как во 2-м приборе)
        self.mask_poly = c.create_polygon(
            0, 0, 0, 0, 0, 0, 0, 0,
            fill=DARK_BG, outline="", tags="mask_poly"
        )

        # Пузырьки — ПОЗЖЕ, чтобы были поверх жидкости
        # но до обводки.

        # Обводка корпуса
        c.create_oval(cx - size, cy - size, cx + size, cy + size,
                      fill="", outline="#4a4a4a", width=2, tags="border")

        # Текст
        self.text_id = c.create_text(
            cx, cy, text="65%",
            font=("Segoe UI", 22, "bold"),
            fill="#ffffff", tags="text"
        )

        # Пузырьки — создаём после маски, чтобы они были видны
        for _ in range(8):
            self._spawn_bubble()

        self._redraw()

    def _spawn_bubble(self):
        # Позиция — внутри круга, ниже уровня жидкости
        # Приблизительно: угол и радиус
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.size * 0.7)
        x = self.cx + radius * math.cos(angle)
        y = self.cy + radius * math.sin(angle)
        rad = random.uniform(2, 5)
        b = self.canvas.create_oval(
            x - rad, y - rad, x + rad, y + rad,
            fill="#ffffff", outline="", tags="bubble"
        )
        self.bubbles.append({"id": b, "x": x, "y": y,
                             "r": rad, "speed": random.uniform(0.3, 1.0)})

    def set_value(self, v):
        self.target = max(0.0, min(100.0, float(v)))

    def tick(self):
        diff = self.target - self.value
        if abs(diff) < 0.3:
            self.value = self.target
        else:
            self.value += diff * 0.15

        self.phase += 0.15
        self._redraw()

        # Пузырьки — вверх и внутри круга
        for b in self.bubbles:
            b["y"] -= b["speed"]
            # Проверка, что пузырёк внутри круга
            dx = b["x"] - self.cx
            dy = b["y"] - self.cy
            if (dx * dx + dy * dy) > (self.size - 5) ** 2 or b["y"] < self.cy - self.size:
                # Пересоздать
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, self.size * 0.6)
                b["x"] = self.cx + radius * math.cos(angle)
                b["y"] = self.cy + radius * math.sin(angle)
            self.canvas.coords(b["id"],
                               b["x"] - b["r"], b["y"] - b["r"],
                               b["x"] + b["r"], b["y"] + b["r"])

    def _redraw(self):
        r = self.r
        cx, cy = self.cx, self.cy

        level_y = cy - r + 2 * r * (1 - self.value / 100)

        # Маска — та же логика, что во 2-м приборе
        pts = []
        steps = 30
        for i in range(steps + 1):
            a = 180 - 180 * i / steps
            rad = math.radians(a - 90)
            x = cx + r * math.cos(rad)
            y = cy + r * math.sin(rad)
            if y <= level_y:
                pts.extend([x, y])
        pts.extend([cx + r, level_y])
        pts.extend([cx - r, level_y])

        if len(pts) >= 6:
            self.canvas.coords(self.mask_poly, *pts)

        # Маску поднять
        self.canvas.tag_raise(self.mask_poly)
        self.canvas.tag_raise(self.text_id)

        self.canvas.itemconfig(self.text_id,
                               text=f"{int(round(self.value))}%")


# ═══════════════════════════════════════════════════════════════════
# 4. ШАР С ПЛАВНЫМ ГРАДИЕНТОМ
# ═══════════════════════════════════════════════════════════════════
class GlossyBall:
    def __init__(self, canvas, cx, cy, size, color, color_light, color_deep):
        self.canvas = canvas
        c = canvas
        r = size

        # Серая тень-обводка
        c.create_oval(cx - r - 3, cy - r - 3,
                      cx + r + 3, cy + r + 3,
                      fill="#d0d0d0", outline="")
        # Белая обводка
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill="#ffffff", outline="")

        # Основной цвет
        c.create_oval(cx - r + 6, cy - r + 6,
                      cx + r - 6, cy + r - 6,
                      fill=color, outline="")

        # Градиент — 4 вложенных овала со светлеющим верхом
        inner_r = r - 6
        for i in range(4):
            ratio = 1 - (i + 1) / 5
            oval_color = self._lerp(color, color_light, ratio * 0.6)
            # Смещаем верх
            c.create_oval(
                cx - inner_r + i * 6,
                cy - inner_r + i * 4,
                cx + inner_r - i * 6,
                cy + inner_r - i * 4 - 8,
                fill="", outline="",
            )
        # Верхняя светлая полоса
        c.create_arc(
            cx - inner_r, cy - inner_r,
            cx + inner_r, cy + inner_r,
            start=20, extent=140,
            style="chord", fill=color_light, outline=""
        )
        # Ещё одна полоса чуть темнее
        c.create_arc(
            cx - inner_r + 6, cy - inner_r + 6,
            cx + inner_r - 6, cy + inner_r - 6,
            start=25, extent=130,
            style="chord", fill=self._lerp(color_light, color, 0.3),
            outline=""
        )

        # Большой белый блик сверху-слева
        c.create_oval(
            cx - r * 0.55, cy - r * 0.55,
            cx - r * 0.15, cy - r * 0.20,
            fill="#ffffff", outline=""
        )
        # Маленький блик
        c.create_oval(
            cx - r * 0.45, cy - r * 0.30,
            cx - r * 0.30, cy - r * 0.15,
            fill="#ffffff", outline=""
        )

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


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class LiquidApp:
    def __init__(self, root):
        self.root = root
        root.title("Анимация уровня жидкостей")
        root.geometry("1200x400")
        root.minsize(1100, 380)
        root.configure(bg=BG)
        root.resizable(False, False)

        tk.Label(root, text="Анимация уровня жидкостей",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 4))

        tk.Label(root,
                 text="Ползунок меняет уровень · пузырьки анимируются",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 12))

        panel = tk.Frame(root, bg=PANEL,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        panel.pack(padx=20, pady=(0, 12))

        self.canvas = tk.Canvas(panel, width=1140, height=240,
                                bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)

        # 5 приборов
        self.dark_arc = DarkArcGauge(self.canvas, cx=120, cy=140, size=90)
        self.dark_fill = DarkFillGauge(self.canvas, cx=340, cy=140, size=90)
        self.wave = WaveLiquidGauge(self.canvas, cx=560, cy=140, size=90)
        self.red_ball = GlossyBall(self.canvas, cx=780, cy=140, size=90,
                                   color=RED, color_light=RED_LIGHT,
                                   color_deep=RED_DEEP)
        self.green_ball = GlossyBall(self.canvas, cx=1000, cy=140, size=90,
                                     color=GREEN_BALL,
                                     color_light=GREEN_BALL_LIGHT,
                                     color_deep=GREEN_BALL_DEEP)

        # Управление
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(padx=20, pady=(0, 16))

        slider_frame = tk.Frame(ctrl, bg=BG)
        slider_frame.pack(side="left", padx=(0, 20))

        tk.Label(slider_frame, text="Уровень, %",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack()

        self.value_label = tk.Label(slider_frame, text="65",
                                    font=("Segoe UI", 11, "bold"),
                                    bg=BG, fg=TEXT)
        self.value_label.pack()

        self.scale = tk.Scale(slider_frame, from_=0, to=100,
                              orient="horizontal", length=200,
                              showvalue=False,
                              bg=BG, fg=TEXT, troughcolor="#d8d8d8",
                              activebackground=BLUE,
                              highlightthickness=0, bd=0,
                              sliderlength=18, width=8,
                              command=self.on_slider)
        self.scale.set(65)
        self.scale.pack()

        self.btn_auto = tk.Button(
            ctrl, text="▶  Авто",
            font=("Segoe UI", 11, "bold"),
            bg=GREEN, fg="#ffffff",
            activebackground=GREEN_DARK, activeforeground="#ffffff",
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
        self._set_all(val)
        self.value_label.config(text=str(int(val)))

    def _set_all(self, val):
        self.dark_arc.set_value(val)
        self.dark_fill.set_value(val)
        self.wave.set_value(val)

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.btn_auto.config(text="⏹  Стоп", bg=RED,
                                 activebackground="#a82419")
            self.auto_phase = 0.0
        else:
            self.btn_auto.config(text="▶  Авто", bg=GREEN,
                                 activebackground=GREEN_DARK)

    def _tick(self):
        if self.auto_mode:
            self.auto_phase += 0.05
            val = 50 + 45 * math.sin(self.auto_phase)
            self._set_all(val)
            self.scale.set(val)
            self.value_label.config(text=str(int(val)))

        self.dark_arc.tick()
        self.dark_fill.tick()
        self.wave.tick()

        self.root.after(33, self._tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = LiquidApp(root)
    root.mainloop()
