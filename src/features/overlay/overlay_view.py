from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk


@dataclass(frozen=True)
class OverlayView:
    header: tk.Frame | None
    canvas: tk.Canvas
    closeButton: tk.Button | None
