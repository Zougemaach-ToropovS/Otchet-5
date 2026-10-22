import tkinter as tk
import math
import random
import time


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#1a1a1a"
PANEL = "#2a2a2a"
BORDER = "#3a3a3a"
TEXT = "#e8e8e8"
MUTED = "#888888"
GOLD = "#d4a843"
SILVER = "#b8b8c0"
RED_LED = "#ff2a2a"
TAPE_BROWN = "#4a3a28"

# Корпуса кассет
CASSETTE_STYLES = [
    {
        "name": "Maxell UD-60",
        "year": "1970",
        "case_color": "#f0f0e8",
        "label_color": "#d4782a",
        "stripe_color": "#d4782a",
        "text_color": "#1a1a1a",
        "brand_text": "maxell",
        "side_text": "UD",
        "type_text": "ULTRA DYNAMIC",
    },
    {
        "name": "TDK D-90",
        "year": "1979",
        "case_color": "#f5f5f5",
        "label_color": "#1a4a9e",
        "stripe_color": "#1a4a9e",
        "text_color": "#1a1a1a",
        "brand_text": "TDK",
        "side_text": "D",
        "type_text": "DYNAMIC",
    },
    {
        "name": "Sony CHF-90",
        "year": "1983",
        "case_color": "#f5d020",
        "label_color": "#1a1a1a",
        "stripe_color": "#1a1a1a",
        "text_color": "#1a1a1a",
        "brand_text": "SONY",
        "side_text": "CHF",
        "type_text": "HF",
    },
    {
        "name": "BASF Ferro Extra",
        "year": "1985",
        "case_color": "#c8202a",
        "label_color": "#f0f0f0",
        "stripe_color": "#f0f0f0",
        "text_color": "#f0f0f0",
        "brand_text": "BASF",
        "side_text": "I",
        "type_text": "FERRO EXTRA",
    },
    {
        "name": "Denon DX-90",
        "year": "1987",
        "case_color": "#1a1a1a",
        "label_color": "#c8202a",
        "stripe_color": "#c8202a",
        "text_color": "#e8e8e8",
        "brand_text": "DENON",
        "side_text": "DX",
        "type_text": "HIGH DENSITY",
    },
]


# ═══════════════════════════════════════════════════════════════════
# КАССЕТА С АНИМИРОВАННЫМИ КАТУШКАМИ
# ═══════════════════════════════════════════════════════════════════
class Cassette:
    def __init__(self, canvas, x, y, w, h, style):
        """
        canvas — полотно
        x, y — левый верхний угол
        w, h — ширина и высота
        style — словарь с цветами и текстом
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.style = style

        # Углы катушек (в градусах)
        self.left_angle = 0
        self.right_angle = 0

        # Скорость вращения
        self.spin_speed = 0.0

        self._draw_case()
        self._draw_window()
        self._draw_reels()
        self._draw_label()

    # ─── Корпус кассеты ────────────────────────────────────────
    def _draw_case(self):
        c = self.canvas
        x, y, w, h = self.x, self.y, self.w, self.h

        # Тень
        c.create_rectangle(x + 4, y + 6, x + w + 4, y + h + 6,
                           fill="#0a0a0a", outline="", tags="case_shadow")

        # Основной корпус
        c.create_rectangle(x, y, x + w, y + h,
                           fill=self.style["case_color"],
                           outline="#2a2a2a", width=2)

        # Верхняя полоса-заголовок
        stripe_h = h * 0.20
        c.create_rectangle(x + 2, y + 2, x + w - 2, y + stripe_h,
                           fill=self.style["stripe_color"], outline="")

        # Бренд на полосе
        c.create_text(x + w * 0.15, y + stripe_h / 2,
                      text=self.style["brand_text"],
                      font=("Segoe UI", 14, "bold"),
                      fill="#ffffff" if self.style["stripe_color"] != "#f0f0f0" else "#1a1a1a")

        # Год выпуска
        c.create_text(x + w * 0.85, y + stripe_h / 2,
                      text=self.style["year"],
                      font=("Segoe UI", 8),
                      fill="#ffffff" if self.style["stripe_color"] != "#f0f0f0" else "#1a1a1a")

    # ─── Окно с катушками ──────────────────────────────────────
    def _draw_window(self):
        c = self.canvas
        x, y, w, h = self.x, self.y, self.w, self.h

        # Прозрачное окно — тёмный фон внутри
        win_x = x + w * 0.08
        win_y = y + h * 0.25
        win_w = w * 0.84
        win_h = h * 0.55

        c.create_rectangle(win_x, win_y, win_x + win_w, win_y + win_h,
                           fill="#1a1a1a", outline="#3a3a3a", width=2,
                           tags="tape_window")

        # Сохраняем координаты окна для катушек
        self.win_x = win_x
        self.win_y = win_y
        self.win_w = win_w
        self.win_h = win_h

    # ─── Катушки ───────────────────────────────────────────────
    def _draw_reels(self):
        c = self.canvas
        cx1 = self.win_x + self.win_w * 0.25
        cx2 = self.win_x + self.win_w * 0.75
        cy = self.win_y + self.win_h / 2
        r = self.win_h * 0.42

        self.reel_centers = [(cx1, cy), (cx2, cy)]
        self.reel_r = r

        self.left_reel_items = []
        self.right_reel_items = []

        self._draw_single_reel(cx1, cy, r, self.left_reel_items, 0)
        self._draw_single_reel(cx2, cy, r, self.right_reel_items, 0)

        # Лента между катушками — тонкая линия
        c.create_line(cx1 + r, cy, cx2 - r, cy,
                      fill=TAPE_BROWN, width=2, tags="tape")

        # Направляющие ролики в углах
        c.create_oval(self.win_x + 8, self.win_y + self.win_h - 14,
                      self.win_x + 18, self.win_y + self.win_h - 4,
                      fill="#4a4a4a", outline="#2a2a2a", tags="roller")
        c.create_oval(self.win_x + self.win_w - 18, self.win_y + self.win_h - 14,
                      self.win_x + self.win_w - 8, self.win_y + self.win_h - 4,
                      fill="#4a4a4a", outline="#2a2a2a", tags="roller")

    def _draw_single_reel(self, cx, cy, r, items_list, angle):
        """Рисует одну катушку с вращающимся сердцевиком."""
        c = self.canvas

        # Внешний диск — тёмный
        outer = c.create_oval(cx - r, cy - r, cx + r, cy + r,
                              fill="#2a2a2a", outline="#4a4a4a", width=2)
        items_list.append(outer)

        # Внутренний диск — светлый
        inner = c.create_oval(cx - r * 0.7, cy - r * 0.7,
                              cx + r * 0.7, cy + r * 0.7,
                              fill="#4a4a4a", outline="#5a5a5a", width=1)
        items_list.append(inner)

        # Зубцы катушки (вращаются вместе с angle)
        for i in range(6):
            a = angle + i * 60
            rad = math.radians(a - 90)
            x1 = cx + r * 0.25 * math.cos(rad)
            y1 = cy + r * 0.25 * math.sin(rad)
            x2 = cx + r * 0.75 * math.cos(rad)
            y2 = cy + r * 0.75 * math.sin(rad)
            line = c.create_line(x1, y1, x2, y2,
                                 fill="#8a8a8a", width=2,
                                 capstyle="round")
            items_list.append(line)

        # Центральное отверстие
        hole = c.create_oval(cx - r * 0.15, cy - r * 0.15,
                             cx + r * 0.15, cy + r * 0.15,
                             fill="#1a1a1a", outline="#6a6a6a", width=1)
        items_list.append(hole)

    def _redraw_reels(self):
        """Перерисовывает катушки под новым углом."""
        c = self.canvas

        # Удаляем старые элементы катушек
        for item in self.left_reel_items + self.right_reel_items:
            c.delete(item)
        self.left_reel_items = []
        self.right_reel_items = []

        cx1, cy1 = self.reel_centers[0]
        cx2, cy2 = self.reel_centers[1]
        r = self.reel_r

        self._draw_single_reel(cx1, cy1, r, self.left_reel_items, self.left_angle)
        self._draw_single_reel(cx2, cy2, r, self.right_reel_items, self.right_angle)

        # Ленту и ролики поднимаем наверх
        c.tag_raise("tape")
        c.tag_raise("roller")

    # ─── Наклейка с типом ──────────────────────────────────────
    def _draw_label(self):
        c = self.canvas
        x, y, w, h = self.x, self.y, self.w, self.h

        # Нижняя часть — наклейка
        label_y = y + h * 0.82
        label_h = h * 0.16

        c.create_rectangle(x + w * 0.08, label_y,
                           x + w * 0.92, label_y + label_h,
                           fill=self.style["label_color"], outline="")

        c.create_text(x + w * 0.5, label_y + label_h / 2,
                      text=self.style["type_text"],
                      font=("Segoe UI", 8, "bold"),
                      fill=self.style["text_color"])

    # ─── Анимация ──────────────────────────────────────────────
    def tick(self):
        """Обновление углов катушек."""
        if abs(self.spin_speed) > 0.01:
            self.left_angle = (self.left_angle + self.spin_speed) % 360
            self.right_angle = (self.right_angle + self.spin_speed) % 360
            self._redraw_reels()

    def start_spin(self, speed=5.0):
        self.spin_speed = speed

    def stop_spin(self):
        self.spin_speed = 0.0


# ═══════════════════════════════════════════════════════════════════
# ОКНО С ОДНОЙ КАССЕТОЙ
# ═══════════════════════════════════════════════════════════════════
class CassetteWindow:
    def __init__(self, parent, style, index):
        self.style = style
        self.index = index
        self.spin_speed = 0.0

        self.win = tk.Toplevel(parent)
        self.win.title(f"Кассета — {style['name']}")
        self.win.geometry("340x260")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)

        # Позиция окна — каскадом
        self.win.geometry(f"+{100 + index * 40}+{100 + index * 40}")

        # Canvas
        self.canvas = tk.Canvas(self.win, width=320, height=200,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(pady=(15, 5))

        # Создаём кассету
        self.cassette = Cassette(self.canvas, x=20, y=10,
                                 w=280, h=170, style=style)

        # Кнопки
        btns = tk.Frame(self.win, bg=BG)
        btns.pack(pady=(0, 10))

        self.btn_play = tk.Button(btns, text="▶ Воспроизвести",
                                  font=("Segoe UI", 10, "bold"),
                                  bg="#2ea87a", fg="#ffffff",
                                  activebackground="#1e8a5c",
                                  activeforeground="#ffffff",
                                  bd=0, padx=16, pady=8, cursor="hand2",
                                  command=self.toggle_play)
        self.btn_play.pack(side="left", padx=4)

        tk.Button(btns, text="⏹ Стоп",
                  font=("Segoe UI", 10, "bold"),
                  bg="#c8202a", fg="#ffffff",
                  activebackground="#a01820",
                  activeforeground="#ffffff",
                  bd=0, padx=16, pady=8, cursor="hand2",
                  command=self.stop).pack(side="left", padx=4)

        # Запуск анимации
        self.tick()

    def toggle_play(self):
        if self.cassette.spin_speed == 0:
            self.cassette.start_spin(5.0)
            self.btn_play.config(text="⏸ Пауза", bg="#d4782a")
        else:
            self.cassette.stop_spin()
            self.btn_play.config(text="▶ Воспроизвести", bg="#2ea87a")

    def stop(self):
        self.cassette.stop_spin()
        self.btn_play.config(text="▶ Воспроизвести", bg="#2ea87a")

    def tick(self):
        self.cassette.tick()
        self.win.after(33, self.tick)


# ═══════════════════════════════════════════════════════════════════
# ГЛАВНОЕ ОКНО МАГНИТОФОНА
# ═══════════════════════════════════════════════════════════════════
class TapeDeckApp:
    def __init__(self, root):
        self.root = root
        root.title("Кассетный магнитофон")
        root.geometry("720x620")
        root.minsize(680, 580)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.cassette_windows = []
        self.playing = False
        self.play_phase = 0.0

        # ─── Верхняя часть — магнитофон ────────────────────────
        deck_frame = tk.Frame(root, bg=PANEL,
                              highlightthickness=1,
                              highlightbackground=BORDER)
        deck_frame.pack(fill="x", padx=20, pady=(20, 12))

        # Название
        tk.Label(deck_frame, text="TAPE DECK",
                 font=("Consolas", 14, "bold"),
                 bg=PANEL, fg=GOLD).pack(pady=(12, 4))

        tk.Label(deck_frame, text="стереофонический кассетный магнитофон",
                 font=("Segoe UI", 9),
                 bg=PANEL, fg=MUTED).pack(pady=(0, 10))

        # Canvas с отсеком для кассеты
        self.deck_canvas = tk.Canvas(deck_frame, width=600, height=180,
                                     bg="#0a0a0a", highlightthickness=0)
        self.deck_canvas.pack(padx=20, pady=(0, 10))

        # Отсек для кассеты — прямоугольник
        self.deck_canvas.create_rectangle(30, 15, 570, 165,
                                          fill="#1a1a1a",
                                          outline="#3a3a3a", width=2)

        # Имитация механизма внутри отсека
        for i in range(5):
            self.deck_canvas.create_line(
                60 + i * 100, 30, 60 + i * 100, 150,
                fill="#2a2a2a", width=1
            )

        # Текст «вставьте кассету»
        self.deck_text = self.deck_canvas.create_text(
            300, 90, text="ВСТАВЬТЕ КАССЕТУ",
            font=("Consolas", 14, "bold"),
            fill="#3a3a3a",
        )

        # Индикаторы уровня L и R
        self.l_led = self.deck_canvas.create_rectangle(
            560, 30, 566, 150, fill="#0a2a0a", outline="")
        self.r_led = self.deck_canvas.create_rectangle(
            575, 30, 581, 150, fill="#0a2a0a", outline="")

        # ─── Кнопки управления ─────────────────────────────────
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(pady=(0, 14))

        self.btn_open = tk.Button(ctrl, text="📂  Все кассеты",
                                  font=("Segoe UI", 11, "bold"),
                                  bg=GOLD, fg="#1a1a1a",
                                  activebackground="#b89038",
                                  activeforeground="#1a1a1a",
                                  bd=0, padx=24, pady=12, cursor="hand2",
                                  command=self.open_all_cassettes)
        self.btn_open.pack(side="left", padx=6)

        self.btn_play = tk.Button(ctrl, text="▶  PLAY",
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#2ea87a", fg="#ffffff",
                                  activebackground="#1e8a5c",
                                  activeforeground="#ffffff",
                                  bd=0, padx=24, pady=12, cursor="hand2",
                                  command=self.toggle_deck_play)
        self.btn_play.pack(side="left", padx=6)

        self.btn_stop = tk.Button(ctrl, text="⏹  STOP",
                                  font=("Segoe UI", 11, "bold"),
                                  bg="#c8202a", fg="#ffffff",
                                  activebackground="#a01820",
                                  activeforeground="#ffffff",
                                  bd=0, padx=24, pady=12, cursor="hand2",
                                  command=self.stop_deck)
        self.btn_stop.pack(side="left", padx=6)

        # ─── Список легендарных кассет ─────────────────────────
        tk.Label(root, text="ЛЕГЕНДАРНЫЕ КАССЕТЫ",
                 font=("Consolas", 10, "bold"),
                 bg=BG, fg=GOLD).pack(pady=(8, 6))

        list_frame = tk.Frame(root, bg=BG)
        list_frame.pack(fill="x", padx=20, pady=(0, 16))

        for i, style in enumerate(CASSETTE_STYLES):
            btn = tk.Button(
                list_frame,
                text=f"{style['brand_text']} {style['side_text']}  ·  {style['year']}  ·  {style['type_text']}",
                font=("Segoe UI", 10, "bold"),
                bg=style["case_color"],
                fg=style["text_color"] if style["text_color"] != "#f0f0f0" else "#1a1a1a",
                activebackground=style["label_color"],
                activeforeground="#ffffff",
                bd=0, padx=16, pady=10, cursor="hand2",
                anchor="w",
                command=lambda idx=i: self.open_cassette_window(idx),
            )
            btn.pack(fill="x", pady=2)

        # ─── Тик-цикл ─────────────────────────────────────────
        self._tick()

    # ─── Открыть все кассеты ───────────────────────────────────
    def open_all_cassettes(self):
        for i, style in enumerate(CASSETTE_STYLES):
            self.open_cassette_window(i)

    def open_cassette_window(self, index):
        # Проверяем, не открыто ли уже
        for w in self.cassette_windows:
            if w.index == index and w.win.winfo_exists():
                w.win.lift()
                return
        cw = CassetteWindow(self.root, CASSETTE_STYLES[index], index)
        self.cassette_windows.append(cw)

    # ─── Управление магнитофоном ───────────────────────────────
    def toggle_deck_play(self):
        self.playing = not self.playing
        if self.playing:
            self.btn_play.config(text="⏸  PAUSE", bg="#d4782a")
            self.deck_canvas.itemconfig(self.deck_text, text="▶  ИГРАЕТ",
                                        fill=GOLD)
        else:
            self.btn_play.config(text="▶  PLAY", bg="#2ea87a")
            self.deck_canvas.itemconfig(self.deck_text, text="ПАУЗА",
                                        fill="#d4782a")

    def stop_deck(self):
        self.playing = False
        self.play_phase = 0.0
        self.btn_play.config(text="▶  PLAY", bg="#2ea87a")
        self.deck_canvas.itemconfig(self.deck_text, text="ОСТАНОВЛЕНО",
                                    fill="#c8202a")
        self._update_leds(0)

    def _update_leds(self, level):
        """Обновляет индикаторы уровня."""
        for led, x in [(self.l_led, 560), (self.r_led, 575)]:
            h = int((150 - 30) * level)
            self.deck_canvas.coords(led, x, 150 - h, x + 6, 150)
            color = "#0a2a0a" if level < 0.1 else "#20c020"
            self.deck_canvas.itemconfig(led, fill=color)

    # ─── Тик-цикл ──────────────────────────────────────────────
    def _tick(self):
        if self.playing:
            self.play_phase += 0.15
            # Имитация уровня сигнала
            level = 0.5 + 0.4 * math.sin(self.play_phase) + random.uniform(-0.1, 0.1)
            level = max(0, min(1, level))
            self._update_leds(level)
        else:
            self._update_leds(0)

        self.root.after(50, self._tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TapeDeckApp(root)
    root.mainloop()
