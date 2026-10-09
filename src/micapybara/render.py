"""Draw a sprite in the terminal.

Each character cell shows two pixels stacked: the top one as the text color
of an upper half block (▀) and the bottom one as the background color.
So a 34 x 26 sprite takes 34 columns and 13 lines.
"""

from __future__ import annotations

import os
import sys

from .sprite import COLORS, Grid

RESET = "\x1b[0m"


def use_color(stream=None) -> bool:
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(stream, "isatty") and stream.isatty()


def to_ansi(grid: Grid, color: bool = True) -> str:
    lines = []
    for y in range(0, len(grid), 2):
        top_row = grid[y]
        bottom_row = grid[y + 1] if y + 1 < len(grid) else [None] * len(top_row)
        out = []
        for top, bottom in zip(top_row, bottom_row):
            if not color:
                out.append({(True, True): "█", (True, False): "▀", (False, True): "▄"}.get((bool(top), bool(bottom)), " "))
            elif top and bottom:
                (r1, g1, b1), (r2, g2, b2) = COLORS[top], COLORS[bottom]
                out.append(f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m▀{RESET}")
            elif top:
                r, g, b = COLORS[top]
                out.append(f"\x1b[38;2;{r};{g};{b}m▀{RESET}")
            elif bottom:
                r, g, b = COLORS[bottom]
                out.append(f"\x1b[38;2;{r};{g};{b}m▄{RESET}")
            else:
                out.append(" ")
        lines.append("".join(out).rstrip())
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)
