import tkinter as tk
from typing import List, Tuple

from src.core.localization.localizer import Localizer


class Renderer:
    def __init__(self, canvas: tk.Canvas, localizer: Localizer | None = None) -> None:
        self.canvas = canvas
        self._localizer = localizer
        self._chromaEnabled = False
        self._voterCount = 0

    def ConfigureChroma(self, enabled: bool, voterCount: int) -> None:
        self._chromaEnabled = bool(enabled)
        count = int(voterCount)
        if count < 0:
            count = 0
        if count > 3:
            count = 3
        self._voterCount = count

    def Render(self, votes: List[Tuple[str, int]], voters: List[str] | None = None) -> None:
        if self.canvas is None:
            return
        try:
            if not self.canvas.winfo_exists():
                return
            self.canvas.update_idletasks()
            self.canvas.delete("all")
        except Exception:
            return

        width = max(self.canvas.winfo_width(), self.canvas.winfo_reqwidth(), 360)
        height = max(self.canvas.winfo_height(), self.canvas.winfo_reqheight(), 220)

        palette = self.__GetPalette()

        # Flattened layout: render directly on the canvas background (no floating card).
        paddingX = 12
        paddingY = 12
        contentX = 0
        contentY = 0
        contentWidth = max(260, width)

        titleText = self.__Text("overlay.poll.title", default="Stream Poll")
        totalVotes = sum(self.__ClampNonNegative(self.__ToInt(count)) for _, count in votes)
        subtitleText = (
            self.__Text("overlay.poll.totalVotes", default=f"Total votes: {totalVotes}", count=totalVotes)
            if totalVotes > 0
            else self.__Text("overlay.poll.waitingVotes", default="Waiting for votes")
        )

        titleSize = max(12, min(18, int(width // 40)))
        bodySize = max(10, min(14, int(width // 55)))

        self.__DrawTextWithOptionalShadow(
            x=contentX + paddingX,
            y=contentY + paddingY,
            text=titleText,
            fill=palette["text"],
            font=("Segoe UI", titleSize, "bold"),
            anchor="nw",
            shadowFill=palette["textShadow"],
        )
        self.__DrawTextWithOptionalShadow(
            x=contentX + paddingX,
            y=contentY + paddingY + (titleSize + 6),
            text=subtitleText,
            fill=palette["subtext"],
            font=("Segoe UI", bodySize),
            anchor="nw",
            shadowFill=palette["textShadow"],
        )

        if not self._chromaEnabled:
            try:
                dividerY = contentY + paddingY + (titleSize + 6) + (bodySize + 8)
                self.canvas.create_line(
                    contentX + paddingX,
                    dividerY,
                    contentX + contentWidth - paddingX,
                    dividerY,
                    fill=palette["border"],
                )
            except Exception:
                pass

        if not votes:
            self.__DrawTextWithOptionalShadow(
                x=contentX + paddingX,
                y=contentY + paddingY + (titleSize + 6) + (bodySize + 22),
                text=self.__Text("overlay.poll.noOptions", default="No options"),
                fill=palette["subtext"],
                font=("Segoe UI", bodySize + 1),
                anchor="nw",
                shadowFill=palette["textShadow"],
            )
            return

        safeVotes = [(str(name), self.__ClampNonNegative(self.__ToInt(count))) for name, count in votes]
        maxVotes = max((count for _, count in safeVotes), default=0)

        headerHeight = paddingY + (titleSize + 6) + (bodySize + 18)
        barsTop = contentY + headerHeight

        leftPad = paddingX
        rightPad = paddingX
        barStartX = contentX + leftPad
        labelX = contentX + contentWidth - rightPad

        availableHeight = max(120, height - headerHeight - paddingY)
        maxRows = max(1, min(len(safeVotes), 10))
        barRowHeight = max(36, min(56, int(availableHeight / maxRows)))
        barHeight = max(10, min(20, int(barRowHeight / 3)))
        barGapY = max(6, int(barRowHeight / 6))

        barMaxWidth = max(160, int(contentWidth - leftPad - rightPad - (92 + (8 if bodySize > 10 else 0))))

        rowY = barsTop
        for optionIndex, (name, count) in enumerate(safeVotes, start=1):
            ratio = (count / maxVotes) if maxVotes > 0 else 0.0
            barWidth = int(barMaxWidth * ratio)
            barWidth = max(0, min(barMaxWidth, barWidth))

            displayName = self.__Truncate(name.strip(), 34)
            nameLine = f"{optionIndex}. {displayName}"
            countLine = f"{count}  ({round(ratio * 100)}%)" if maxVotes > 0 else f"{count}"

            self.__DrawTextWithOptionalShadow(
                x=barStartX,
                y=rowY,
                text=nameLine,
                fill=palette["text"],
                font=("Segoe UI", bodySize + 1, "bold"),
                anchor="nw",
                shadowFill=palette["textShadow"],
            )

            self.__DrawTextWithOptionalShadow(
                x=labelX,
                y=rowY + 2,
                text=countLine,
                fill=palette["subtext"],
                font=("Segoe UI", bodySize),
                anchor="ne",
                shadowFill=palette["textShadow"],
            )

            # Keep the bar clearly separated from the text line.
            textBlockHeight = max(bodySize + 10, int(barRowHeight * 0.50))
            barY = rowY + textBlockHeight
            if not self._chromaEnabled:
                self.__DrawRoundedRect(
                    x=barStartX,
                    y=barY,
                    width=barMaxWidth,
                    height=barHeight,
                    radius=max(6, int(barHeight / 2)),
                    fill=palette["track"],
                    outline="",
                )

            if barWidth > 0:
                self.__DrawGradientPill(
                    x=barStartX,
                    y=barY,
                    width=barWidth,
                    height=barHeight,
                    radius=max(6, int(barHeight / 2)),
                    leftColor=palette["accent1"],
                    rightColor=palette["accent2"],
                )

            rowY += barRowHeight
            if rowY > (contentY + height - paddingY - 42):
                break

        if self._voterCount > 0 and voters:
            displayVoters = [name for name in voters[: self._voterCount] if name and name.strip()]
            if displayVoters:
                prefix = self.__Text("overlay.poll.recentVotersPrefix", default="Recent")
                votersLabel = f"{prefix}: " + ", ".join(self.__Truncate(name, 18) for name in displayVoters)
                self.__DrawTextWithOptionalShadow(
                    x=contentX + paddingX,
                    y=min(rowY + barGapY, contentY + height - paddingY - (bodySize + 8)),
                    text=votersLabel,
                    fill=palette["subtext"],
                    font=("Segoe UI", bodySize),
                    anchor="nw",
                    shadowFill=palette["textShadow"],
                )

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def __ToInt(self, value: int | str) -> int:
        try:
            return int(value)
        except Exception:
            return 0

    def __ClampNonNegative(self, value: int) -> int:
        try:
            if value < 0:
                return 0
            return int(value)
        except Exception:
            return 0

    def __Truncate(self, text: str, maxChars: int) -> str:
        safeText = str(text) if text is not None else ""
        safeText = safeText.replace("\n", " ").replace("\r", " ")
        if len(safeText) <= maxChars:
            return safeText
        if maxChars <= 1:
            return safeText[:maxChars]
        return safeText[: maxChars - 1] + "…"

    def __GetPalette(self) -> dict[str, str]:
        if self._chromaEnabled:
            return {
                "panel": "#00ff00",
                "shadow": "#00ff00",
                "border": "#00ff00",
                "track": "#00ff00",
                "text": "#ffffff",
                "subtext": "#ffffff",
                "textShadow": "#000000",
                "accent1": "#00e5ff",
                "accent2": "#2979ff",
            }
        return {
            "panel": "#141414",
            "shadow": "#000000",
            "border": "#2a2a2a",
            "track": "#222222",
            "text": "#f5f5f5",
            "subtext": "#c9c9c9",
            "textShadow": "",
            "accent1": "#ffb74d",
            "accent2": "#ff7043",
        }

    def __DrawTextWithOptionalShadow(self, x: int, y: int, text: str, fill: str, font: tuple, anchor: str, shadowFill: str) -> None:
        if shadowFill:
            self.canvas.create_text(x + 1, y + 1, text=text, anchor=anchor, fill=shadowFill, font=font)
        self.canvas.create_text(x, y, text=text, anchor=anchor, fill=fill, font=font)

    def __DrawRoundedRect(self, x: int, y: int, width: int, height: int, radius: int, fill: str, outline: str) -> None:
        if width <= 0 or height <= 0:
            return
        radius = max(0, min(int(radius), min(width, height) // 2))
        x0 = x
        y0 = y
        x1 = x + width
        y1 = y + height

        if radius <= 0:
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline)
            return

        self.canvas.create_rectangle(x0 + radius, y0, x1 - radius, y1, fill=fill, outline="")
        self.canvas.create_rectangle(x0, y0 + radius, x1, y1 - radius, fill=fill, outline="")

        self.canvas.create_oval(x0, y0, x0 + (radius * 2), y0 + (radius * 2), fill=fill, outline="")
        self.canvas.create_oval(x1 - (radius * 2), y0, x1, y0 + (radius * 2), fill=fill, outline="")
        self.canvas.create_oval(x0, y1 - (radius * 2), x0 + (radius * 2), y1, fill=fill, outline="")
        self.canvas.create_oval(x1 - (radius * 2), y1 - (radius * 2), x1, y1, fill=fill, outline="")

        if outline:
            self.canvas.create_line(x0 + radius, y0, x1 - radius, y0, fill=outline)
            self.canvas.create_line(x0 + radius, y1, x1 - radius, y1, fill=outline)
            self.canvas.create_line(x0, y0 + radius, x0, y1 - radius, fill=outline)
            self.canvas.create_line(x1, y0 + radius, x1, y1 - radius, fill=outline)

            self.canvas.create_arc(x0, y0, x0 + (radius * 2), y0 + (radius * 2), start=90, extent=90, style="arc", outline=outline)
            self.canvas.create_arc(x1 - (radius * 2), y0, x1, y0 + (radius * 2), start=0, extent=90, style="arc", outline=outline)
            self.canvas.create_arc(x0, y1 - (radius * 2), x0 + (radius * 2), y1, start=180, extent=90, style="arc", outline=outline)
            self.canvas.create_arc(x1 - (radius * 2), y1 - (radius * 2), x1, y1, start=270, extent=90, style="arc", outline=outline)

    def __DrawGradientPill(self, x: int, y: int, width: int, height: int, radius: int, leftColor: str, rightColor: str) -> None:
        width = int(width)
        if width <= 0 or height <= 0:
            return

        r1, g1, b1 = self.__HexToRgb(leftColor)
        r2, g2, b2 = self.__HexToRgb(rightColor)
        steps = max(4, width)

        for stepIndex in range(steps):
            ratio = stepIndex / max(1, steps - 1)
            r = int(r1 + ((r2 - r1) * ratio))
            g = int(g1 + ((g2 - g1) * ratio))
            b = int(b1 + ((b2 - b1) * ratio))
            color = f"#{r:02x}{g:02x}{b:02x}"
            x0 = x + stepIndex
            x1 = x + stepIndex + 1
            self.canvas.create_rectangle(x0, y, x1, y + height, outline="", fill=color)

        if not self._chromaEnabled:
            self.__DrawRoundedRect(x=x, y=y, width=width, height=height, radius=radius, fill="", outline="#000000")

    def __HexToRgb(self, hexColor: str) -> tuple[int, int, int]:
        safe = (hexColor or "").strip().lstrip("#")
        if len(safe) != 6:
            return (255, 255, 255)
        try:
            return (int(safe[0:2], 16), int(safe[2:4], 16), int(safe[4:6], 16))
        except Exception:
            return (255, 255, 255)

    def __DrawGradientBar(self, x: int, y: int, width: int, height: int) -> None:
        # Backwards-compatible helper retained for any older callers.
        self.__DrawGradientPill(x=x, y=y, width=width, height=height, radius=max(1, height // 2), leftColor="#ffb74d", rightColor="#ff7043")
