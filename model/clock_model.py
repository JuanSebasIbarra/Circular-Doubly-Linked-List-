"""Business logic for a timezone-aware analog clock backed by a CDLL."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from .TickBuffer import TickBuffer


@dataclass
class ClockSnapshot:

    hour: int
    minute: int
    second: float
    national_label: str
    national_time: str
    city_times: list[tuple[str, str]]


class ClockModel:


    TICK_CAPACITY = 3600
    NATIONAL_ZONE = ZoneInfo("America/Bogota")

    ALL_TIMEZONES: list[tuple[str, ZoneInfo]] = [
        ("Bogota",               ZoneInfo("America/Bogota")),
        ("Lima",                 ZoneInfo("America/Lima")),
        ("Quito",                ZoneInfo("America/Guayaquil")),
        ("Ciudad de Mexico",     ZoneInfo("America/Mexico_City")),
        ("Madrid",               ZoneInfo("Europe/Madrid")),
        ("Buenos Aires",         ZoneInfo("America/Argentina/Buenos_Aires")),
        ("Nueva York",           ZoneInfo("America/New_York")),
        ("Londres",              ZoneInfo("Europe/London")),
        ("Tokyo",                ZoneInfo("Asia/Tokyo")),
        ("Sydney",               ZoneInfo("Australia/Sydney")),
    ]

    CAPITAL_TIMEZONES: list[tuple[str, ZoneInfo]] = ALL_TIMEZONES[:5]

    def __init__(self) -> None:
        self.tick_history: TickBuffer = TickBuffer(
            capacity=self.TICK_CAPACITY
        )
        self._last_recorded_second: tuple[int, int, int] | None = None
        self._is_24_hour_mode: bool = False

    def set_24_hour_mode(self, enabled: bool) -> None:
        """Enable or disable 24-hour display mode."""
        self._is_24_hour_mode = enabled

    def set_active_timezones(self, selected: list[str]) -> None:
        """Replace visible capitals with a user-selected subset (max 5)."""
        if not selected:
            self.CAPITAL_TIMEZONES = self.ALL_TIMEZONES[:5]
            return

        selected_limited = selected[:5]
        selected_set = set(selected_limited)
        filtered = [
            (name, zone)
            for name, zone in self.ALL_TIMEZONES
            if name in selected_set
        ]

        self.CAPITAL_TIMEZONES = filtered or self.ALL_TIMEZONES[:5]

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
            (city, self._format_time(datetime.now(zone)))
            for city, zone in self.CAPITAL_TIMEZONES
        ]

        return ClockSnapshot(
            hour=h,
            minute=m,
            second=s_float,
            national_label="Hora nacional (Bogota)",
            national_time=self._format_time(bogota_now),
            city_times=city_times,
        )

    def _format_time(self, dt: datetime) -> str:
        """Format datetime according to the selected 12h/24h mode."""
        if self._is_24_hour_mode:
            return dt.strftime("%H:%M:%S")
        return dt.strftime("%I:%M:%S %p").lstrip("0")
