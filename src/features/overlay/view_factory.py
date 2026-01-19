import tkinter as tk
from typing import Callable

from src.features.overlay.overlay_view import OverlayView


class ViewFactory:
    def Build(
        self,
        window: tk.Toplevel,
        onClose: Callable[[], None],
        bgColor: str,
        controlsVisible: bool,
        closeButtonText: str,
    ) -> OverlayView:
        canvas = tk.Canvas(window, bg=bgColor, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        closeButton: tk.Button | None = None
        if controlsVisible:
            closeButton = tk.Button(
                window,
                text=str(closeButtonText or "Close"),
                command=onClose,
                bg="#2b2b2b",
                fg="#ffffff",
                activebackground="#3a3a3a",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                borderwidth=0,
                width=7,
                height=1,
                highlightthickness=0,
            )
            closeButton.place(relx=1.0, x=-10, y=10, anchor="ne")

        return OverlayView(header=None, canvas=canvas, closeButton=closeButton)
