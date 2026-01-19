import tkinter as tk


class DragController:
    def __init__(self) -> None:
        self._windowX = 0
        self._windowY = 0
        self._pointerX = 0
        self._pointerY = 0

    def Begin(self, window: tk.Toplevel, event: tk.Event) -> None:
        self._windowX = window.winfo_x()
        self._windowY = window.winfo_y()
        self._pointerX = event.x_root
        self._pointerY = event.y_root

    def Drag(self, window: tk.Toplevel, event: tk.Event) -> None:
        deltaX = event.x_root - self._pointerX
        deltaY = event.y_root - self._pointerY
        newX = self._windowX + deltaX
        newY = self._windowY + deltaY
        window.geometry(f"+{newX}+{newY}")
