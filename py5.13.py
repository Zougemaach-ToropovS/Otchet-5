import tkinter as tk
import math


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#3a3a3a"
PANEL = "#4a4a4a"
DARK = "#2a2a2a"
BORDER_DARK = "#1a1a1a"

LED_BG = "#0a1a0a"
LED_GREEN = "#2aff2a"
LED_GREEN_DIM = "#1a8a1a"
LED_RED = "#ff2a2a"
LED_YELLOW = "#ffd000"

KNOB_BG = "#2a2a2a"
KNOB_EDGE = "#1a1a1a"
KNOB_MARK = "#e8e8e8"

LABEL_GRAY = "#c8c8c8"
LABEL_YELLOW = "#d4c878"
GREEN_BTN = "#1a5a1a"


# ═══════════════════════════════════════════════════════════════════
# LED-ДИСПЛЕЙ
# ═══════════════════════════════════════════════════════════════════
class LEDDisplay:
    def __init__(self, canvas, x, y, w, h, initial="0"):
        self.canvas = canvas
        canvas.create_rectangle(x, y, x + w, y + h,
                                fill=LED_BG, outline=BORDER_DARK, width=2)
        canvas.create_rectangle(x + 2, y + 2, x + w - 2, y + h - 2,
                                fill="", outline="#0a3a0a", width=1)
        self.text_id = canvas.create_text(
            x + w / 2, y + h / 2,
            text=initial,
            font=("Consolas", 18, "bold"),
            fill=LED_GREEN,
        )

    def set(self, text):
        self.canvas.itemconfig(self.text_id, text=text)


# ═══════════════════════════════════════════════════════════════════
# КРУТИЛКА
# ═══════════════════════════════════════════════════════════════════
class Knob:
    def __init__(self, canvas, cx, cy, r,
                 min_val=0, max_val=100, initial=50,
                 label="", unit="", on_change=None):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.r = r
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.label = label
        self.unit = unit
        self.on_change = on_change

        self.start_angle = -135
        self.end_angle = 135

        self._draw()
        self._redraw()

    def _draw(self):
        c = self.canvas
        cx, cy, r = self.cx, self.cy, self.r

        # Дуга шкалы
        c.create_arc(cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8,
                     start=45, extent=270,
                     style="arc", outline=BORDER_DARK, width=2)

        # Деления и подписи
        for v in range(0, 11):
            a = self.start_angle + (self.end_angle - self.start_angle) * v / 10
            rad = math.radians(a - 90)
            x1 = cx + (r + 4) * math.cos(rad)
            y1 = cy + (r + 4) * math.sin(rad)
            x2 = cx + (r + 10) * math.cos(rad)
            y2 = cy + (r + 10) * math.sin(rad)
            c.create_line(x1, y1, x2, y2, fill="#8a8a8a", width=1)

            if v % 2 == 0:
                val = self.min_val + (self.max_val - self.min_val) * v / 10
                xl = cx + (r + 22) * math.cos(rad)
                yl = cy + (r + 22) * math.sin(rad)
                c.create_text(xl, yl, text=self._format(val),
                              font=("Segoe UI", 7, "bold"),
                              fill=LABEL_YELLOW)

        # Тень
        c.create_oval(cx - r + 3, cy - r + 5,
                      cx + r + 3, cy + r + 5,
                      fill="#1a1a1a", outline="")

        # Тело крутилки
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=KNOB_BG, outline=KNOB_EDGE, width=2)
        c.create_oval(cx - r * 0.8, cy - r * 0.8,
                      cx + r * 0.8, cy + r * 0.8,
                      fill="#3a3a3a", outline="#1a1a1a", width=1)
        c.create_oval(cx - r * 0.6, cy - r * 0.6,
                      cx + r * 0.6, cy + r * 0.6,
                      fill="#4a4a4a", outline="#2a2a2a", width=1)

        # Метка
        self.marker_id = c.create_line(
            cx, cy, cx, cy - r * 0.85,
            fill=KNOB_MARK, width=3, capstyle="round"
        )

        if self.label:
            c.create_text(cx, cy + r + 30,
                          text=self.label,
                          font=("Segoe UI", 8, "bold"),
                          fill=LABEL_GRAY)

        self.value_label_id = c.create_text(
            cx, cy + r + 44,
            text="",
            font=("Consolas", 8, "bold"),
            fill=LABEL_YELLOW,
        )

    def _redraw(self):
        a = self.start_angle + (self.end_angle - self.start_angle) * \
            (self.value - self.min_val) / (self.max_val - self.min_val)
        rad = math.radians(a - 90)
        x = self.cx + self.r * 0.85 * math.cos(rad)
        y = self.cy + self.r * 0.85 * math.sin(rad)
        self.canvas.coords(self.marker_id, self.cx, self.cy, x, y)

        val_text = f"{self._format(self.value)} {self.unit}".strip()
        self.canvas.itemconfig(self.value_label_id, text=val_text)

        if self.on_change:
            self.on_change(self.value)

    def _format(self, v):
        if v >= 1000:
            return f"{v/1000:.1f}k"
        return f"{v:.0f}"

    def set_value(self, v):
        self.value = max(self.min_val, min(self.max_val, v))
        self._redraw()


# ═══════════════════════════════════════════════════════════════════
# ОКНО ГЕНЕРАТОРА
# ═══════════════════════════════════════════════════════════════════
class GeneratorWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("Генератор сигналов звуковой частоты")
        self.win.geometry("740x560")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)

        self.canvas = tk.Canvas(self.win, width=720, height=530,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        self.frequency = 1000.0
        self.level = 20.0
        self.playing = False
        self.phase = 0.0

        self.channel = tk.StringVar(value="left_right")
        self.waveform = tk.StringVar(value="sine")

        self.channel_radios = []
        self.waveform_radios = []

        self._draw_panels()
        self._draw_displays()
        self._draw_switches()
        self._draw_knobs()
        self._draw_buttons()
        self._draw_oscilloscope()

        self._update_radios()
        self.tick()

    # ─── Панели ────────────────────────────────────────────────
    def _draw_panels(self):
        c = self.canvas
        c.create_rectangle(5, 5, 355, 195, fill=PANEL,
                           outline=BORDER_DARK, width=1)
        c.create_rectangle(360, 5, 715, 195, fill=PANEL,
                           outline=BORDER_DARK, width=1)
        c.create_rectangle(5, 200, 715, 490, fill=PANEL,
                           outline=BORDER_DARK, width=1)

        c.create_text(180, 20, text="Левый канал",
                      font=("Segoe UI", 10, "bold"), fill=LABEL_GRAY)
        c.create_text(537, 20, text="Правый канал",
                      font=("Segoe UI", 10, "bold"), fill=LABEL_GRAY)

    # ─── Дисплеи ───────────────────────────────────────────────
    def _draw_displays(self):
        self.disp_freq_l = LEDDisplay(self.canvas, 20, 35, 155, 50, "01000 Гц")
        self.disp_lvl_l = LEDDisplay(self.canvas, 185, 35, 155, 50, "020 мВ")
        self.disp_freq_r = LEDDisplay(self.canvas, 375, 35, 155, 50, "01000 Гц")
        self.disp_lvl_r = LEDDisplay(self.canvas, 540, 35, 155, 50, "020 мВ")

    # ─── Радиокнопки ───────────────────────────────────────────
    def _draw_switches(self):
        c = self.canvas

        c.create_text(70, 105, text="Канал",
                      font=("Segoe UI", 9, "bold"), fill=LABEL_GRAY)

        channel_opts = [
            ("left_right", "Левый+Правый", 15, 125),
            ("left",       "Левый канал",  15, 148),
            ("right",      "Правый канал", 15, 171),
        ]
        for value, text, x, y in channel_opts:
            self._make_radio(x, y, text, value, self.channel_radios, "channel")

        c.create_text(230, 105, text="Вид сигнала",
                      font=("Segoe UI", 9, "bold"), fill=LABEL_GRAY)

        waveform_opts = [
            ("sine",     "Синусоида",     160, 125),
            ("square",   "Прямоугольн.",  160, 148),
            ("triangle", "Треугольный",   160, 171),
            ("sawtooth", "Пилообразный",  265, 148),
        ]
        for value, text, x, y in waveform_opts:
            self._make_radio(x, y, text, value, self.waveform_radios, "waveform")

    def _make_radio(self, x, y, text, value, list_ref, group):
        c = self.canvas

        # Кружок — фон
        circle = c.create_oval(x, y, x + 12, y + 12,
                               fill=DARK, outline="#c8c8c8", width=1)
        # Точка (скрыта по умолчанию)
        dot_id = c.create_oval(x + 3, y + 3, x + 9, y + 9,
                               fill=LED_GREEN, outline="")
        # Текст
        label = c.create_text(x + 18, y + 6, text=text, anchor="w",
                              font=("Segoe UI", 9), fill=LABEL_GRAY)

        # Клик — переключить
        def click(e):
            if group == "channel":
                self.channel.set(value)
            else:
                self.waveform.set(value)
            self._update_radios()

        for item in (circle, dot_id, label):
            c.tag_bind(item, "<Button-1>", click)
            c.tag_bind(item, "<Enter>",
                       lambda e, ci=circle: c.itemconfig(ci, outline="#2aff2a"))

        def leave(e, ci=circle):
            c.itemconfig(ci, outline="#c8c8c8")
        c.tag_bind(circle, "<Leave>", leave)

        list_ref.append({"value": value, "dot_id": dot_id})

    def _update_radios(self):
        ch = self.channel.get()
        wf = self.waveform.get()
        for r in self.channel_radios:
            state = "normal" if r["value"] == ch else "hidden"
            self.canvas.itemconfig(r["dot_id"], state=state)
        for r in self.waveform_radios:
            state = "normal" if r["value"] == wf else "hidden"
            self.canvas.itemconfig(r["dot_id"], state=state)

    # ─── Крутилки ──────────────────────────────────────────────
    def _draw_knobs(self):
        self.knob_freq = Knob(
            self.canvas, cx=120, cy=350, r=50,
            min_val=20, max_val=20000, initial=1000,
            label="Частота", unit="Гц",
            on_change=self._on_freq_change,
        )
        self.knob_level = Knob(
            self.canvas, cx=290, cy=350, r=50,
            min_val=0, max_val=100, initial=20,
            label="Уровень", unit="мВ",
            on_change=self._on_level_change,
        )
        self.knob_freq_r = Knob(
            self.canvas, cx=460, cy=350, r=50,
            min_val=20, max_val=20000, initial=1000,
            label="Частота П", unit="Гц",
        )
        self.knob_level_r = Knob(
            self.canvas, cx=630, cy=350, r=50,
            min_val=0, max_val=100, initial=20,
            label="Амплитуда П", unit="мВ",
        )

    def _on_freq_change(self, v):
        self.frequency = v
        self.disp_freq_l.set(f"{int(v):05d} Гц")

    def _on_level_change(self, v):
        self.level = v
        self.disp_lvl_l.set(f"{int(v):03d} мВ")

    # ─── Кнопки ────────────────────────────────────────────────
    def _draw_buttons(self):
        c = self.canvas

        # ВЫХОД
        btn_exit = c.create_rectangle(560, 100, 690, 145,
                                      fill="#5a1010", outline=LED_RED, width=2)
        exit_text = c.create_text(625, 122, text="Выход",
                                  font=("Consolas", 14, "bold"),
                                  fill=LED_RED)

        def close_win(e):
            self.win.destroy()

        for item in (btn_exit, exit_text):
            c.tag_bind(item, "<Button-1>", close_win)
        c.tag_bind(btn_exit, "<Enter>",
                   lambda e: c.itemconfig(btn_exit, fill="#8a2020"))
        c.tag_bind(btn_exit, "<Leave>",
                   lambda e: c.itemconfig(btn_exit, fill="#5a1010"))

        # СТАРТ
        self.btn_start = c.create_rectangle(380, 100, 500, 145,
                                            fill=GREEN_BTN,
                                            outline="#3a8a3a", width=2)
        self.start_text = c.create_text(440, 122, text="Старт",
                                        font=("Consolas", 14, "bold"),
                                        fill=LED_GREEN)

        def start(e):
            self.start_generation()

        for item in (self.btn_start, self.start_text):
            c.tag_bind(item, "<Button-1>", start)
        c.tag_bind(self.btn_start, "<Enter>",
                   lambda e: c.itemconfig(self.btn_start, fill="#2a7a2a"))
        c.tag_bind(self.btn_start, "<Leave>",
                   lambda e: c.itemconfig(self.btn_start, fill=GREEN_BTN))

        # СТОП
        btn_stop = c.create_rectangle(510, 100, 550, 145,
                                      fill=DARK, outline="#5a5a5a", width=2)
        stop_text = c.create_text(530, 122, text="Стоп",
                                  font=("Consolas", 10, "bold"),
                                  fill="#8a8a8a")

        def stop(e):
            self.stop_generation()

        for item in (btn_stop, stop_text):
            c.tag_bind(item, "<Button-1>", stop)

        # Логотип
        c.create_text(50, 505, text="ГСЧ-01",
                      anchor="w",
                      font=("Consolas", 11, "bold"),
                      fill=LABEL_GRAY)

        # Решётка
        for i in range(6):
            c.create_line(700, 495 + i * 3, 712, 495 + i * 3,
                          fill="#2a2a2a")

    # ─── Осциллограф ───────────────────────────────────────────
    def _draw_oscilloscope(self):
        c = self.canvas
        c.create_rectangle(20, 415, 200, 470,
                           fill="#0a1a0a", outline=BORDER_DARK, width=1)
        c.create_text(110, 408, text="ФОРМА СИГНАЛА",
                      font=("Consolas", 8, "bold"),
                      fill=LED_GREEN_DIM)

        # Создаём линию с начальными координатами (не пустую!)
        init_pts = [20, 442, 200, 442]
        self.osc_line = c.create_line(*init_pts, fill=LED_GREEN, width=2)

    def _update_oscilloscope(self):
        pts = []
        w = 180
        h = 55
        x0, y0 = 20, 415
        wf = self.waveform.get()

        for i in range(51):
            t = i / 50
            x = x0 + t * w
            if wf == "sine":
                y = math.sin(t * 4 * math.pi)
            elif wf == "square":
                y = 1 if (t * 4) % 1 < 0.5 else -1
            elif wf == "triangle":
                p = (t * 4) % 1
                y = 4 * abs(p - 0.5) - 1
            else:
                p = (t * 4) % 1
                y = 1 - 2 * p
            py = y0 + h / 2 - y * (h / 2 - 6)
            pts.extend([x, py])

        self.canvas.coords(self.osc_line, *pts)

    # ─── Управление ────────────────────────────────────────────
    def start_generation(self):
        self.playing = True
        self.canvas.itemconfig(self.start_text, fill="#ffffff")

    def stop_generation(self):
        self.playing = False
        self.canvas.itemconfig(self.start_text, fill=LED_GREEN)

    # ─── Тик ───────────────────────────────────────────────────
    def tick(self):
        self._update_oscilloscope()

        if self.playing:
            self.phase += 0.3
            freq = int(self.frequency)
            lvl = int(self.level)
            jitter = int(2 * math.sin(self.phase))
            self.disp_freq_l.set(f"{freq + jitter:05d} Гц")
            self.disp_lvl_l.set(f"{lvl + jitter:03d} мВ")
            self.disp_freq_r.set(f"{freq + jitter:05d} Гц")
            self.disp_lvl_r.set(f"{lvl + jitter:03d} мВ")

        self.win.after(60, self.tick)


# ═══════════════════════════════════════════════════════════════════
# ГЛАВНОЕ ОКНО
# ═══════════════════════════════════════════════════════════════════
class GeneratorApp:
    def __init__(self, root):
        self.root = root
        root.title("Генератор сигналов звуковой частоты")
        root.geometry("740x600")
        root.configure(bg=BG)

        # Заголовок
        tk.Label(root, text="ГСЧ-01 · Генератор сигналов",
                 font=("Consolas", 14, "bold"),
                 bg=BG, fg=LED_GREEN).pack(pady=(15, 5))

        tk.Label(root, text="Нажмите кнопку, чтобы открыть окно генератора",
                 font=("Segoe UI", 10),
                 bg=BG, fg=LABEL_GRAY).pack(pady=(0, 20))

        # Кнопка открыть
        tk.Button(root, text="▶  Открыть генератор",
                  font=("Segoe UI", 12, "bold"),
                  bg=GREEN_BTN, fg=LED_GREEN,
                  activebackground="#2a7a2a",
                  activeforeground="#ffffff",
                  bd=2, padx=30, pady=16, cursor="hand2",
                  command=self.open_generator).pack(pady=10)

        # Кнопка открыть ещё
        tk.Button(root, text="+ Открыть ещё одно окно",
                  font=("Segoe UI", 11, "bold"),
                  bg=DARK, fg=LABEL_GRAY,
                  activebackground="#1a1a1a",
                  activeforeground=LED_GREEN,
                  bd=1, padx=20, pady=12, cursor="hand2",
                  command=self.open_generator).pack(pady=6)

        # Логотип
        tk.Label(root, text="ГСЧ-01",
                 font=("Consolas", 10, "bold"),
                 bg=BG, fg="#5a5a5a").pack(side="bottom", pady=15)

    def open_generator(self):
        GeneratorWindow(self.root)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorApp(root)
    root.mainloop()
