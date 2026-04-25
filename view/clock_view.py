"""Apple-like analog clock view with smooth animation and capitals panel."""

from __future__ import annotations
import math
import tkinter as tk

from model.clock_model import ClockSnapshot


class ClockView:
    """Draws and updates the analog clock interface."""

    APP_BG = "#e9e9eb"
    FACE_BG = "#f4f4f5"
    FACE_STROKE = "#e3e3e5"
    MAJOR_TICK = "#5f6368"
    MINOR_TICK = "#c4c7cc"
    NUMERAL = "#4c4f54"
    HOUR_HAND = "#111111"
    MIN_HAND = "#0c0c0c"
    SEC_HAND = "#ff9800"
    CENTER_RING = "#1a1a1a"
    SHADOW = "#d2d3d7"
    PANEL_BG = "#f7f7f8"
    PANEL_TEXT = "#50545b"

    WIDTH = 1180
    HEIGHT = 720
    CX = 410
    CY = 360
    RADIUS = 240

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Reloj")
        self.root.resizable(False, False)
        self.root.configure(bg=self.APP_BG)

        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg=self.APP_BG,
            highlightthickness=0,
        )
        self.canvas.pack()

        self._city_time_ids: list[int] = []
        self._draw_static_parts()

    def _draw_static_parts(self) -> None:
        cx, cy, r = self.CX, self.CY, self.RADIUS

        self._create_rounded_rect(
            cx - r - 70 + 8,
            cy - r - 70 + 10,
            cx + r + 70 + 8,
            cy + r + 70 + 10,
            radius=90,
            fill=self.SHADOW,
            outline="",
        )

        self._create_rounded_rect(
            cx - r - 70,
            cy - r - 70,
            cx + r + 70,
            cy + r + 70,
            radius=90,
            fill=self.FACE_BG,
            outline=self.FACE_STROKE,
            width=2,
        )

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            if i % 5 == 0:
                x1 = cx + (r - 6) * cos_a
                y1 = cy + (r - 6) * sin_a
                x2 = cx + (r - 42) * cos_a
                y2 = cy + (r - 42) * sin_a
                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.MAJOR_TICK,
                    width=5,
                    capstyle=tk.ROUND,
                )
            else:
                x1 = cx + (r - 10) * cos_a
                y1 = cy + (r - 30) * sin_a
                x2 = cx + (r - 30) * cos_a
                y2 = cy + (r - 42) * sin_a
                self.canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.MINOR_TICK,
                    width=4,
                    capstyle=tk.ROUND,
                )

        for label, deg in (("12", -90), ("3", 0), ("6", 90), ("9", 180)):
            angle = math.radians(deg)
            tx = cx + (r - 86) * math.cos(angle)
            ty = cy + (r - 86) * math.sin(angle)
            self.canvas.create_text(
                tx,
                ty,
                text=label,
                fill=self.NUMERAL,
                font=("Helvetica", 54 if label in {"12", "6"} else 52, "normal"),
            )

        self._create_rounded_rect(
            780,
            130,
            1140,
            590,
            radius=26,
            fill=self.PANEL_BG,
            outline="#e0e1e4",
            width=2,
        )

        self.canvas.create_text(
            960,
            170,
            text="Hora nacional",
            fill=self.PANEL_TEXT,
            font=("Helvetica", 20, "bold"),
        )

        self._national_label_id = self.canvas.create_text(
            960,
            205,
            text="Bogota",
            fill=self.PANEL_TEXT,
            font=("Helvetica", 14),
        )

        self._national_time_id = self.canvas.create_text(
            960,
            250,
            text="00:00:00",
            fill="#1f2329",
            font=("Courier", 30, "bold"),
        )

        self.canvas.create_line(820, 285, 1100, 285, fill="#d9dade", width=2)

        self.canvas.create_text(
            960,
            315,
            text="Capitales",
            fill=self.PANEL_TEXT,
            font=("Helvetica", 16, "bold"),
        )

        y = 350
        for _ in range(5):
            item_id = self.canvas.create_text(
                960,
                y,
                text="",
                fill="#2e3238",
                font=("Courier", 14),
            )
            self._city_time_ids.append(item_id)
            y += 42

    def _create_rounded_rect(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        radius: float,
        **kwargs,
    ) -> int:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def update(self, snapshot: ClockSnapshot) -> None:
        self._draw_hands(snapshot.hour, snapshot.minute, snapshot.second)
        self.canvas.itemconfig(self._national_label_id, text=snapshot.national_label)
        self.canvas.itemconfig(self._national_time_id, text=snapshot.national_time)

        for idx, item_id in enumerate(self._city_time_ids):
            if idx < len(snapshot.city_times):
                city, current_time = snapshot.city_times[idx]
                self.canvas.itemconfig(item_id, text=f"{city:18} {current_time}")
            else:
                self.canvas.itemconfig(item_id, text="")

    def _draw_hands(self, h: int, m: int, s_float: float) -> None:
        self.canvas.delete("hand")
        cx, cy, r = self.CX, self.CY, self.RADIUS

        minute_float = m + (s_float / 60.0)
        hour_float = (h % 12) + (minute_float / 60.0)

        s_angle = math.radians((s_float * 6.0) - 90)
        m_angle = math.radians((minute_float * 6.0) - 90)
        h_angle = math.radians((hour_float * 30.0) - 90)

        def draw_hand(
            angle: float,
            length: float,
            width: int,
            color: str,
            tail: float,
        ) -> None:
            x2 = cx + length * math.cos(angle)
            y2 = cy + length * math.sin(angle)
            xt = cx - tail * math.cos(angle)
            yt = cy - tail * math.sin(angle)
            self.canvas.create_line(
                xt,
                yt,
                x2,
                y2,
                fill=color,
                width=width,
                capstyle=tk.ROUND,
                tags="hand",
            )

        draw_hand(h_angle, r * 0.40, 16, self.HOUR_HAND, tail=12)
        draw_hand(m_angle, r * 0.66, 14, self.MIN_HAND, tail=14)
        draw_hand(s_angle, r * 0.76, 5, self.SEC_HAND, tail=36)

        self.canvas.create_oval(
            cx - 12,
            cy - 12,
            cx + 12,
            cy + 12,
            fill="#ffffff",
            outline=self.CENTER_RING,
            width=3,
            tags="hand",
        )
        self.canvas.create_oval(
            cx - 4,
            cy - 4,
            cx + 4,
            cy + 4,
            fill=self.SEC_HAND,
            outline="",
            tags="hand",
        )
