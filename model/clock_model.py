"""Business logic for a timezone-aware analog clock backed by a CDLL."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from .TickBuffer import TickBuffer


@dataclass
class ClockSnapshot:
    """Immutable value object passed from Model to View each frame."""
    hour: int
    minute: int
    second: float
    national_label: str
    national_time: str
    city_times: list[tuple[str, str]]


class ClockModel:
    """Encapsulates clock state with timezone-accurate and smooth time updates."""

    TICK_CAPACITY = 3600
    NATIONAL_ZONE = ZoneInfo("America/Bogota")

    CAPITAL_TIMEZONES: list[tuple[str, ZoneInfo]] = [
        ("Bogota", ZoneInfo("America/Bogota")),
        ("Lima", ZoneInfo("America/Lima")),
        ("Quito", ZoneInfo("America/Guayaquil")),
        ("Ciudad de Mexico", ZoneInfo("America/Mexico_City")),
        ("Madrid", ZoneInfo("Europe/Madrid")),
    ]

    def __init__(self) -> None:
        self.tick_history: TickBuffer = TickBuffer(
            capacity=self.TICK_CAPACITY
        )
        self._last_recorded_second: tuple[int, int, int] | None = None

    def tick(self) -> ClockSnapshot:
        """Record time and return a timezone-accurate frame snapshot."""
        bogota_now = datetime.now(self.NATIONAL_ZONE)

        h = bogota_now.hour
        m = bogota_now.minute
        s_float = bogota_now.second + (bogota_now.microsecond / 1_000_000)

        current_second_key = (h, m, bogota_now.second)
        if self._last_recorded_second != current_second_key:
            self.tick_history.append(h, m, bogota_now.second, label="tick")
            self._last_recorded_second = current_second_key

        city_times = [
            (city, datetime.now(zone).strftime("%H:%M:%S"))
            for city, zone in self.CAPITAL_TIMEZONES
        ]

        return ClockSnapshot(
            hour=h,
            minute=m,
            second=s_float,
            national_label="Hora nacional (Bogota)",
            national_time=bogota_now.strftime("%H:%M:%S"),
            city_times=city_times,
        )
