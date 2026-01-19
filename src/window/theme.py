from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    background: str = "#121212"
    surface: str = "#1e1e1e"
    surfaceAlt: str = "#252526"
    surfaceDeep: str = "#0f0f0f"

    text: str = "#ffffff"
    textMuted: str = "#bdbdbd"
    textFaint: str = "#8a8a8a"

    accent: str = "#0078d4"
    accentHover: str = "#0a84ff"

    button: str = "#2b2b2b"
    buttonHover: str = "#3a3a3a"

    danger: str = "#c42b1c"
    dangerHover: str = "#e03a2a"


class Theme:
    Palette = ThemePalette()

    @staticmethod
    def Apply(root: object) -> None:
        """Apply configures ttk styles and a few tk defaults.

        Safe to call multiple times.
        """

        palette = Theme.Palette

        try:
            configureMethod = getattr(root, "configure", None)
            if callable(configureMethod):
                configureMethod(bg=palette.surface)
        except Exception:
            pass

        # ttk styling
        try:
            from tkinter import ttk

            style = ttk.Style(root)  # type: ignore[arg-type]
            try:
                style.theme_use("clam")
            except Exception:
                pass

            style.configure("TFrame", background=palette.surface)
            style.configure("TLabel", background=palette.surface, foreground=palette.text)

            style.configure(
                "Treeview",
                background=palette.surfaceDeep,
                fieldbackground=palette.surfaceDeep,
                foreground=palette.text,
                borderwidth=0,
                rowheight=22,
            )
            style.configure(
                "Treeview.Heading",
                background=palette.surfaceAlt,
                foreground=palette.text,
                relief="flat",
            )
            style.map(
                "Treeview",
                background=[("selected", palette.button)],
                foreground=[("selected", palette.text)],
            )

            style.configure("TNotebook", background=palette.surface, borderwidth=0)
            style.configure(
                "TNotebook.Tab",
                background=palette.button,
                foreground=palette.text,
                padding=(10, 6),
            )
            style.map(
                "TNotebook.Tab",
                background=[("selected", palette.accent), ("active", palette.buttonHover)],
                foreground=[("selected", palette.text), ("active", palette.text)],
            )

            style.configure(
                "Accent.TButton",
                background=palette.accent,
                foreground=palette.text,
                borderwidth=0,
                focusthickness=0,
                padding=(10, 6),
            )
            style.map(
                "Accent.TButton",
                background=[("active", palette.accentHover), ("disabled", palette.surfaceAlt)],
                foreground=[("disabled", palette.textFaint)],
            )

            style.configure(
                "Neutral.TButton",
                background=palette.button,
                foreground=palette.text,
                borderwidth=0,
                focusthickness=0,
                padding=(10, 6),
            )
            style.map(
                "Neutral.TButton",
                background=[("active", palette.buttonHover), ("disabled", palette.surfaceAlt)],
                foreground=[("disabled", palette.textFaint)],
            )

            # Progress bars (used as a busy indicator)
            style.configure(
                "Busy.Horizontal.TProgressbar",
                troughcolor=palette.surfaceAlt,
                background=palette.accent,
                lightcolor=palette.accent,
                darkcolor=palette.accent,
                bordercolor=palette.surfaceAlt,
            )
        except Exception:
            pass

    @staticmethod
    def TryAddHover(widget: object, normal: str, hover: str) -> None:
        """TryAddHover wires a simple hover effect for tk widgets."""

        try:
            bindMethod = getattr(widget, "bind", None)
            configureMethod = getattr(widget, "configure", None)
            if not callable(bindMethod) or not callable(configureMethod):
                return

            def onEnter(event: object) -> None:
                try:
                    configureMethod(bg=hover)
                except Exception:
                    pass

            def onLeave(event: object) -> None:
                try:
                    configureMethod(bg=normal)
                except Exception:
                    pass

            bindMethod("<Enter>", onEnter)
            bindMethod("<Leave>", onLeave)
        except Exception:
            pass
