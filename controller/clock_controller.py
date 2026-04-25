"""Controller that coordinates model updates and view rendering."""

from __future__ import annotations
import tkinter as tk

from model.clock_model import ClockModel
from view.clock_view  import ClockView


class ClockController:
    """
    MVC Controller — the single point of coupling between Model and View.

    Parameters
    ----------
    root  : tk.Tk      – Tkinter root window owned by main.py
    model : ClockModel – business logic / CDLL storage
    view  : ClockView  – all Tkinter widgets and drawing
    """

    TICK_MS = 16

    def __init__(self, root: tk.Tk, model: ClockModel, view: ClockView) -> None:
        self.root  = root
        self.model = model
        self.view  = view
        self.view.on_time_mode_toggled = self._handle_time_mode_toggle

    # ── Public ────────────────────────────────────────────────────────────────

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
