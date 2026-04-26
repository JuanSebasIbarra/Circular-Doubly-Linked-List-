
from __future__ import annotations
import tkinter as tk

from model.clock_model import ClockModel
from view.clock_view  import ClockView


class ClockController:


    TICK_MS = 16

    def __init__(self, root: tk.Tk, model: ClockModel, view: ClockView) -> None:
        self.root  = root
        self.model = model
        self.view  = view
        self.view.on_time_mode_toggled = self._handle_time_mode_toggle
        self.view.on_timezones_changed = self._handle_timezones_changed


    def start(self) -> None:
        """Begin the clock loop. Call once after constructing all MVC parts."""
        self._tick()

    # ── Tick loop ─────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        """Called at high frequency to keep second hand motion fluid."""
        snapshot = self.model.tick()
        self.view.update(snapshot)

        self.root.after(self.TICK_MS, self._tick)

    def _handle_time_mode_toggle(self, enabled_24h: bool) -> None:
        """Handle switch state changes from view."""
        self.model.set_24_hour_mode(enabled_24h)

    def _handle_timezones_changed(self, selected: list[str]) -> None:
        """Handle selected capitals sent by the modal selector."""
        self.model.set_active_timezones(selected)
