"""Mica, an original pixel-art capybara, drawn in code.

A sprite is a grid of color keys (or None for transparent). Every mood is a
short list of frames. The terminal, the GIF and the web demo all draw from here.
"""

from __future__ import annotations

W, H = 34, 26

COLORS: dict[str, tuple[int, int, int]] = {
    "O": (58, 36, 24),     # outline
    "B": (156, 104, 62),   # body
    "D": (122, 78, 44),    # shade
    "L": (196, 146, 98),   # belly
    "E": (24, 16, 12),     # eye
    "W": (250, 250, 245),  # eye shine
    "N": (74, 46, 30),     # nose
    "R": (238, 132, 38),   # orange
    "G": (70, 150, 70),    # leaf
    "M": (90, 130, 220),   # music note
    "T": (110, 170, 240),  # tear and rain
    "C": (150, 160, 172),  # cloud
    "Z": (180, 190, 210),  # sleepy z
}

Grid = list[list[str | None]]


def _ellipse(g: Grid, cx: float, cy: float, rx: float, ry: float, c: str) -> None:
    for y in range(H):
        for x in range(W):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                g[y][x] = c


def _rect(g: Grid, x0: int, y0: int, x1: int, y1: int, c: str | None) -> None:
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            g[y][x] = c


def _px(g: Grid, x: int, y: int, c: str | None) -> None:
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c


def capybara(dx: int = 0, dy: int = 0, legs=(3, 3, 3, 3), head: int = 0, eye: str = "open",
             note=None, orange: bool = True, tear: bool = False, cloud: int | None = None,
             zz: int | None = None) -> Grid:
    """Draw one frame. eye: 'open', 'happy' (closed, smiling) or 'sleep'."""
    g: Grid = [[None] * W for _ in range(H)]
    ox, oy = 3 + dx, 6 + dy
    # body, back shading, belly
    _ellipse(g, ox + 10, oy + 9, 9.6, 5.4, "B")
    for x in range(ox + 3, ox + 18):
        for y in (oy + 4, oy + 5):
            if g[y][x] == "B" and (y == oy + 4 or x % 3 == 0):
                g[y][x] = "D"
    for x in range(ox + 5, ox + 16):
        _px(g, x, oy + 13, "L")
    # head: boxy snout, capybara style
    hy = oy + head
    _rect(g, ox + 16, hy + 3, ox + 25, hy + 10, "B")
    _rect(g, ox + 22, hy + 5, ox + 27, hy + 10, "B")
    for x, y in ((ox + 16, hy + 3), (ox + 27, hy + 5), (ox + 27, hy + 10)):
        _px(g, x, y, None)
    _rect(g, ox + 17, hy + 4, ox + 24, hy + 4, "D")
    _rect(g, ox + 17, hy + 1, ox + 18, hy + 2, "D")              # ear
    if eye == "open":
        _rect(g, ox + 21, hy + 5, ox + 22, hy + 6, "E")
        _px(g, ox + 21, hy + 5, "W")
    elif eye == "happy":                                          # little upside-down U
        _px(g, ox + 20, hy + 6, "E"); _rect(g, ox + 21, hy + 5, ox + 22, hy + 5, "E"); _px(g, ox + 23, hy + 6, "E")
    else:                                                         # sleeping line
        _rect(g, ox + 20, hy + 6, ox + 23, hy + 6, "E")
    _rect(g, ox + 26, hy + 6, ox + 27, hy + 7, "N")
    _px(g, ox + 24, hy + 9, "D")
    if orange:
        _rect(g, ox + 19, hy, ox + 21, hy + 2, "R")
        _px(g, ox + 19, hy, None); _px(g, ox + 21, hy, None)
        _px(g, ox + 21, hy - 1, "G"); _px(g, ox + 22, hy - 1, "G")
    for x, ln in zip((ox + 4, ox + 8, ox + 14, ox + 18), legs):
        _rect(g, x, oy + 13, x + 1, oy + 13 + ln, "D")
    # outline every empty pixel that touches the capybara
    body = {(x, y) for y in range(H) for x in range(W) if g[y][x] and g[y][x] in "BDLENW"}
    for x, y in body:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and g[ny][nx] is None:
                g[ny][nx] = "O"
    # extras drawn on top
    if tear:
        _px(g, ox + 21, hy + 8, "T"); _px(g, ox + 21, hy + 9, "T")
    if note is not None:
        nx, ny = note
        _rect(g, nx, ny, nx, ny + 4, "M"); _rect(g, nx - 2, ny + 3, nx - 1, ny + 4, "M")
        _px(g, nx + 1, ny, "M"); _px(g, nx + 2, ny + 1, "M")
    if cloud is not None:
        cx = 4 + cloud
        _rect(g, cx, 1, cx + 7, 3, "C"); _rect(g, cx + 2, 0, cx + 5, 0, "C")
        for i, x in enumerate(range(cx + 1, cx + 8, 3)):
            _px(g, x, 5 + (i + cloud) % 2, "T")
    if zz is not None:
        zx, zy = 27, 2 - zz
        _rect(g, zx, zy, zx + 4, zy, "Z")
        _px(g, zx + 3, zy + 1, "Z"); _px(g, zx + 2, zy + 2, "Z"); _px(g, zx + 1, zy + 3, "Z")
        _rect(g, zx, zy + 4, zx + 4, zy + 4, "Z")
    return g


MOODS: dict[str, list[Grid]] = {
    "happy": [
        capybara(0, 0, (3, 3, 3, 3), 0, "happy", (2, 4)),
        capybara(-1, -2, (5, 1, 1, 5), -1, "happy", (2, 2)),
        capybara(0, 0, (3, 3, 3, 3), 1, "happy", (2, 0)),
        capybara(1, -2, (1, 5, 5, 1), -1, "happy", (14, 2)),
        capybara(0, 0, (3, 3, 3, 3), 0, "happy", (14, 1)),
        capybara(0, -1, (4, 2, 4, 2), 1, "happy", (14, 0)),
    ],
    "content": [
        capybara(eye="open"), capybara(eye="open"), capybara(eye="open"), capybara(eye="sleep"),
    ],
    "worried": [
        capybara(head=2, eye="open", tear=True, cloud=0),
        capybara(head=2, eye="open", tear=True, cloud=1),
    ],
    "sleepy": [
        capybara(dy=1, legs=(2, 2, 2, 2), head=2, eye="sleep", orange=False, zz=0),
        capybara(dy=1, legs=(2, 2, 2, 2), head=2, eye="sleep", orange=False, zz=1),
        capybara(dy=1, legs=(2, 2, 2, 2), head=2, eye="sleep", orange=False, zz=2),
    ],
}


def frame(mood: str, i: int = 0) -> Grid:
    frames = MOODS[mood]
    return frames[i % len(frames)]
