import tkinter as tk
import math
import random
import time


# ─── Палитра ─────────────────────────────────────────────────────
BG = "#f4f4f4"
CASE_OUTER = "#1a1a1a"     # внешний чёрный корпус
CASE_INNER = "#0a0a0a"     # внутренний чёрный
CASE_EDGE = "#3a3a3a"      # лёгкий серый край
SCALE_TEXT = "#e8b8e8"     # сиреневая подпись дБ
LR_TEXT = "#c8c8c8"        # светло-серые L и R
GRID_DIM = "#1a1a2a"       # тусклые сегменты

# Цвета сегментов по уровню
SEG_COLORS = [
    "#1e90ff",  # глубокий синий
    "#1e90ff",  # синий
    "#4a7cff",  # сине-сиреневый
    "#7a5cff",  # сиреневый
    "#a04aff",  # фиолетовый
    "#c83acc",  # маджента
    "#e54ab0",  # розовый
    "#ff3a6a",  # розово-красный
    "#ff2a3a",  # красный
    "#ff1a1a",  # ярко-красный
]

ACCENT = "#0a84ff"
TEXT = "#1c1c1e"
MUTED = "#888888"


# ─── VU-метр ─────────────────────────────────────────────────────
class VUMeter:
    def __init__(self, canvas, x, y, w, h):
        """
        canvas — Canvas
        x, y   — левый верхний угол корпуса
        w, h   — ширина и высота
        """
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # 40 сегментов в каждом ряду
        self.segments = 40
        # Уровни L и R (0…1)
        self.level_l = 0.3
        self.level_r = 0.25
        # Пики (для индикатора удержания)
        self.peak_l = 0.3
        self.peak_r = 0.25

        # Привязка dB к позиции сегмента
        # -20 dB → сегмент 0; +6 dB → сегмент 40
        self.db_min = -20
        self.db_max = 6

        # Отступы
        self.pad = 14
        self.label_w = 24      # ширина зоны для L/R
        self.row_h = 26        # высота одного ряда
        self.scale_h = 26      # высота зоны шкалы dB

        # Рисуем
        self._draw_case()
        self._draw_rows()

    # ─── Корпус ─────────────────────────────────────────────────
    def _draw_case(self):
        c = self.canvas

        # Внешняя светлая окантовка
        c.create_rectangle(
            self.x - 3, self.y - 3,
            self.x + self.w + 3, self.y + self.h + 3,
            fill="#e8e8e8", outline=""
        )
        # Чёрный корпус
        c.create_rectangle(
            self.x, self.y,
            self.x + self.w, self.y + self.h,
            fill=CASE_OUTER, outline=CASE_EDGE, width=1
        )
        # Внутренний тёмный
        c.create_rectangle(
            self.x + 4, self.y + 4,
            self.x + self.w - 4, self.y + self.h - 4,
            fill=CASE_INNER, outline=""
        )

    # ─── Ряды сегментов ─────────────────────────────────────────
    def _draw_rows(self):
        c = self.canvas

        # Верхний ряд — L
        self.row_l_y = self.y + self.pad
        self._draw_row(self.row_l_y, "L", is_top=True)

        # Зона шкалы dB
        self.scale_y = self.row_l_y + self.row_h + 4

        # Нижний ряд — R
        self.row_r_y = self.scale_y + self.scale_h
        self._draw_row(self.row_r_y, "R", is_top=False)

        # Рисуем шкалу dB
        self._draw_db_scale()

        # Первичная отрисовка сегментов
        self.seg_l_ids = []
        self.seg_r_ids = []
        self._create_segments("L", self.row_l_y, self.seg_l_ids)
        self._create_segments("R", self.row_r_y, self.seg_r_ids)

        # Индикаторы пиков
        self.peak_l_id = None
        self.peak_r_id = None

        # Подписи L и R
        c.create_text(
            self.x + self.label_w / 2 + 6,
            self.row_l_y + self.row_h / 2,
            text="L",
            font=("Segoe UI", 12, "bold"),
            fill=LR_TEXT,
        )
        c.create_text(
            self.x + self.label_w / 2 + 6,
            self.row_r_y + self.row_h / 2,
            text="R",
            font=("Segoe UI", 12, "bold"),
            fill=LR_TEXT,
        )

    def _draw_row(self, y, label, is_top):
        c = self.canvas

        # Тонкая подложка
        c.create_rectangle(
            self.x + self.label_w + 4, y,
            self.x + self.w - 8, y + self.row_h,
            fill="#14141e", outline=""
        )

    # ─── Сегменты ───────────────────────────────────────────────
    def _create_segments(self, channel, y, ids_list):
        c = self.canvas

        x_start = self.x + self.label_w + 8
        x_end = self.x + self.w - 10
        row_w = x_end - x_start

        seg_gap = 1
        seg_w = (row_w - (self.segments - 1) * seg_gap) / self.segments

        for i in range(self.segments):
            sx = x_start + i * (seg_w + seg_gap)
            # Рисуем тусклый сегмент (заполнение — при обновлении)
            rect = c.create_rectangle(
                sx, y + 3,
                sx + seg_w, y + self.row_h - 3,
                fill=GRID_DIM, outline=""
            )
            ids_list.append(rect)

    # ─── Шкала dB ───────────────────────────────────────────────
    def _draw_db_scale(self):
        c = self.canvas

        # Подписи дБ
        db_marks = [-20, -15, -10, -6, -3, 0, +1, +3, +6]

        x_start = self.x + self.label_w + 8
        x_end = self.x + self.w - 10
        row_w = x_end - x_start

        # Позиция метки dB в ряду (линейно от -20 до +6)
        for db in db_marks:
            pct = (db - self.db_min) / (self.db_max - self.db_min)
            x = x_start + row_w * pct

            text = f"{db:+d}" if db > 0 else str(db)
            c.create_text(
                x, self.scale_y + self.scale_h / 2,
                text=text,
                font=("Consolas", 8, "bold"),
                fill=SCALE_TEXT,
            )

    # ─── Обновление сегментов по уровню ─────────────────────────
    def _update_channel(self, ids_list, level, peak):
        """Обновляет цвет сегментов для одного канала."""
        active = int(round(level * self.segments))

        for i, seg_id in enumerate(ids_list):
            if i < active:
                # Цвет по позиции сегмента (0…9 индексов палитры)
                color_idx = min(9, int(i / self.segments * 10))
                color = SEG_COLORS[color_idx]
                self.canvas.itemconfig(seg_id, fill=color)
            else:
                self.canvas.itemconfig(seg_id, fill=GRID_DIM)

    # ─── Установка уровня ───────────────────────────────────────
    def set_levels(self, l, r):
        self.level_l = max(0, min(1, l))
        self.level_r = max(0, min(1, r))

        # Обновляем пики с удержанием
        self.peak_l = max(self.peak_l * 0.995, self.level_l)
        self.peak_r = max(self.peak_r * 0.995, self.level_r)

        self._update_channel(self.seg_l_ids, self.level_l, self.peak_l)
        self._update_channel(self.seg_r_ids, self.level_r, self.peak_r)

        # Рисуем индикаторы пиков
        self._draw_peak(self.peak_l, self.row_l_y, "l")
        self._draw_peak(self.peak_r, self.row_r_y, "r")

    def _draw_peak(self, peak, y, channel):
        c = self.canvas

        x_start = self.x + self.label_w + 8
        x_end = self.x + self.w - 10
        row_w = x_end - x_start

        px = x_start + row_w * peak

        if channel == "l":
            if self.peak_l_id is not None:
                c.delete(self.peak_l_id)
            if peak > 0.02:
                self.peak_l_id = c.create_rectangle(
                    px - 1, y + 3,
                    px + 1, y + self.row_h - 3,
                    fill="#ff80d0", outline=""
                )
            else:
                self.peak_l_id = None
        else:
            if self.peak_r_id is not None:
                c.delete(self.peak_r_id)
            if peak > 0.02:
                self.peak_r_id = c.create_rectangle(
                    px - 1, y + 3,
                    px + 1, y + self.row_h - 3,
                    fill="#ff80d0", outline=""
                )
            else:
                self.peak_r_id = None


# ═══════════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════════════
class VUApp:
    def __init__(self, root):
        self.root = root
        root.title("VU Meter")
        root.geometry("900x480")
        root.minsize(780, 420)
        root.configure(bg=BG)
        root.resizable(False, False)

        self.animate = False
        self.phase = 0.0

        # ═══ Заголовок ═══════════════════════════════════════════
        tk.Label(root, text="VU-метр",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 4))

        tk.Label(root, text="Двухрядный индикатор уровня L / R",
                 font=("Segoe UI", 10),
                 bg=BG, fg=MUTED).pack(pady=(0, 14))

        # ═══ Canvas с прибором ═══════════════════════════════════
        self.canvas = tk.Canvas(root, width=820, height=180,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(pady=(0, 14))

        self.vu = VUMeter(self.canvas,
                          x=10, y=10, w=800, h=160)

        # ═══ Ползунки L / R ══════════════════════════════════════
        sliders = tk.Frame(root, bg=BG)
        sliders.pack(pady=(0, 10))

        # L
        l_frame = tk.Frame(sliders, bg=BG)
        l_frame.pack(side="left", padx=20)

        tk.Label(l_frame, text="L", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack()
        self.scale_l = tk.Scale(
            l_frame, from_=0, to=100,
            orient="horizontal", length=340,
            showvalue=False,
            bg=BG, fg=TEXT,
            troughcolor="#d8d4cd",
            activebackground=ACCENT,
            highlightthickness=0, bd=0,
            sliderlength=20, width=10,
            command=self.on_manual_change,
        )
        self.scale_l.set(30)
        self.scale_l.pack()

        # R
        r_frame = tk.Frame(sliders, bg=BG)
        r_frame.pack(side="left", padx=20)

        tk.Label(r_frame, text="R", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack()
        self.scale_r = tk.Scale(
            r_frame, from_=0, to=100,
            orient="horizontal", length=340,
            showvalue=False,
            bg=BG, fg=TEXT,
            troughcolor="#d8d4cd",
            activebackground=ACCENT,
            highlightthickness=0, bd=0,
            sliderlength=20, width=10,
            command=self.on_manual_change,
        )
        self.scale_r.set(25)
        self.scale_r.pack()

        # ═══ Кнопки ══════════════════════════════════════════════
        btns = tk.Frame(root, bg=BG)
        btns.pack(pady=(0, 20))

        self.btn_play = self._btn(btns, "▶  Играть музыку",
                                  self.toggle_music,
                                  color="#2ecc71")
        self.btn_play.pack(side="left", padx=4)

        self._btn(btns, "Тишина", self.silence).pack(
            side="left", padx=4)
        self._btn(btns, "Максимум", self.max_level).pack(
            side="left", padx=4)

        # Клавиатура
        root.bind("<space>", lambda e: self.toggle_music())

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
    def on_manual_change(self, value=None):
        if self.animate:
            return
        l = self.scale_l.get() / 100
        r = self.scale_r.get() / 100
        self.vu.set_levels(l, r)

    def silence(self):
        self.animate = False
        self.btn_play.config(text="▶  Играть музыку")
        self.scale_l.set(0)
        self.scale_r.set(0)

    def max_level(self):
        self.animate = False
        self.btn_play.config(text="▶  Играть музыку")
        self.scale_l.set(100)
        self.scale_r.set(100)

    def toggle_music(self):
        self.animate = not self.animate
        if self.animate:
            self.btn_play.config(text="⏹  Остановить")
            self._music_tick()
        else:
            self.btn_play.config(text="▶  Играть музыку")

    def _music_tick(self):
        """Симуляция «звука» — уровни пляшут как на реальном приборе."""
        if not self.animate:
            return

        self.phase += 0.15

        # Разные волны для L и R + случайный шум
        base_l = 0.5 + 0.4 * math.sin(self.phase)
        base_r = 0.5 + 0.4 * math.sin(self.phase * 0.9 + 1.2)

        noise_l = random.uniform(-0.08, 0.08)
        noise_r = random.uniform(-0.08, 0.08)

        l = max(0.05, min(1.0, base_l + noise_l))
        r = max(0.05, min(1.0, base_r + noise_r))

        # Иногда громкий пик
        if random.random() < 0.02:
            l = min(1.0, l + 0.2)
        if random.random() < 0.02:
            r = min(1.0, r + 0.2)

        self.vu.set_levels(l, r)
        self.scale_l.set(l * 100)
        self.scale_r.set(r * 100)

        self.root.after(60, self._music_tick)


# ─── Запуск ──────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = VUApp(root)
    root.mainloop()
