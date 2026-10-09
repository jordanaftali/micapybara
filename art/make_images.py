"""Build every image in docs/ from the sprite in src/micapybara/sprite.py.

    python art/make_images.py

Needs three Google Fonts (OFL) in art/fonts/: BigShoulders.ttf (Big Shoulders Display),
PlexSans.ttf (IBM Plex Sans) and PlexMono.ttf (IBM Plex Mono Medium).
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from micapybara.sprite import COLORS, MOODS, H, W

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
F = HERE / "fonts"
BG, INK, MUTED, LINE = (17, 20, 23), (231, 234, 237), (154, 163, 172), (44, 50, 56)
KEYS = list(COLORS)


def font(name, size, weight=None):
    f = ImageFont.truetype(str(F / name), size)
    if weight:
        try:
            axes = f.get_variation_axes()
            f.set_variation_by_axes([weight if a.get("name") in (b"Weight", "Weight") else a["default"] for a in axes])
        except Exception:
            pass
    return f


def draw(grid, s, bg=None):
    img = Image.new("RGBA", (W * s, H * s), (0, 0, 0, 0) if bg is None else bg + (255,))
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c:
                img.paste(COLORS[c] + (255,), (x * s, y * s, (x + 1) * s, (y + 1) * s))
    return img


def gif_frame(img):
    pal = [255, 0, 255] + [v for k in KEYS for v in COLORS[k]]
    p = Image.new("P", img.size, 0)
    p.putpalette(pal + [0] * (768 - len(pal)))
    look = {COLORS[k] + (255,): i + 1 for i, k in enumerate(KEYS)}
    src, dst = img.load(), p.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            dst[x, y] = look.get(src[x, y], 0)
    return p


def save_gif(mood, path, s=8, ms=150):
    frames = [gif_frame(draw(g, s)) for g in MOODS[mood]]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0,
                   transparency=0, disposal=2)


DOCS.mkdir(exist_ok=True)
save_gif("happy", DOCS / "dance.gif")
draw(MOODS["happy"][0], 8).save(DOCS / "capybara.png")
draw(MOODS["happy"][0], 2).save(DOCS / "favicon.png")

# frames for the web demo
FRAMES = (json.dumps({
    "w": W, "h": H, "colors": {k: "#%02x%02x%02x" % v for k, v in COLORS.items()},
    "moods": {m: ["".join(c or "." for c in row) for g in fs for row in g] for m, fs in MOODS.items()},
    "counts": {m: len(fs) for m, fs in MOODS.items()},
}, separators=(",", ":")))

(DOCS / "frames.js").write_text("window.MICA = " + FRAMES + ";\n")

# the four moods side by side
labels = {"happy": "tests passed", "content": "all calm",
          "worried": "tests failed", "sleepy": "no runs in 2 days"}
cell = W * 6 + 40
sheet = Image.new("RGB", (cell * 4 + 40, H * 6 + 110), BG)
d = ImageDraw.Draw(sheet)
small = font("PlexMono.ttf", 20)
for i, mood in enumerate(labels):
    img = draw(MOODS[mood][0], 6)
    x = 40 + i * cell
    sheet.paste(img, (x, 24), img)
    d.text((x + W * 3, H * 6 + 42), mood, font=font("PlexSans.ttf", 24, 600), fill=INK, anchor="mm")
    d.text((x + W * 3, H * 6 + 74), labels[mood], font=small, fill=MUTED, anchor="mm")
sheet.save(DOCS / "moods.png", optimize=True)

# a terminal window after a green pytest run
mono = font("PlexMono.ttf", 22)
tw, th = 960, 470
term = Image.new("RGB", (tw, th), (13, 15, 17))
d = ImageDraw.Draw(term)
d.rectangle((0, 0, tw, 40), fill=(32, 36, 40))
for j, c in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
    d.ellipse((18 + j * 24, 13, 32 + j * 24, 27), fill=c)
d.text((tw // 2, 20), "~/my-project", font=font("PlexMono.ttf", 16), fill=MUTED, anchor="mm")
y = 60
d.text((28, y), "$ pytest", font=mono, fill=INK); y += 34
d.text((28, y), "collected 24 items", font=mono, fill=MUTED); y += 34
d.text((28, y), "tests/test_trail.py ........................", font=mono, fill=(98, 197, 84)); y += 40
img = draw(MOODS["happy"][1], 7)
term.paste(img, (40, y - 14), img); y += H * 7 - 10
d.text((28, y), "Mica is dancing! 24 tests passed.", font=mono, fill=INK); y += 32
d.text((28, y), "[##############------] 70/100", font=mono, fill=(238, 132, 38)); y += 32
d.text((28, y), "======= 24 passed in 0.38s =======", font=mono, fill=(98, 197, 84))
term.save(DOCS / "terminal.png", optimize=True)

# 1200x630 link preview
og = Image.new("RGB", (1200, 630), BG)
d = ImageDraw.Draw(og)
x = 80
d.text((x, 78), "PERSONAL PROJECT  ·  PYTHON  ·  PYTEST  ·  PYDANTIC", font=font("PlexMono.ttf", 24), fill=MUTED)
d.text((x, 120), "MICAPYBARA", font=font("BigShoulders.ttf", 150, 800), fill=INK)
d.text((x, 306), "A pixel capybara who lives in your terminal.", font=font("PlexSans.ttf", 36, 400), fill=INK)
d.text((x, 352), "She dances when your tests pass.", font=font("PlexSans.ttf", 36, 400), fill=MUTED)
d.text((x, 430), "$ pytest   ·   $ capy feed", font=font("PlexMono.ttf", 26), fill=(238, 132, 38))
capy = draw(MOODS["happy"][1], 8)
og.paste(capy, (1200 - capy.width - 50, 40), capy)
d.line((x, 560, 1120, 560), fill=LINE, width=2)
name = font("PlexSans.ttf", 26, 600)
d.text((x, 576), "Jordana Naftali", font=name, fill=INK)
nw = d.textlength("Jordana Naftali", font=name)
d.text((x + nw + 24, 580), "Design Engineer  ·  jordanaftali.github.io/micapybara", font=font("PlexMono.ttf", 22), fill=MUTED)
og.save(DOCS / "og-image.png", optimize=True)
print("built:", sorted(p.name for p in DOCS.iterdir()))
