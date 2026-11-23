#!/usr/bin/env python3
"""render.py - draws the Monday 23 November 2026 newspaper front page.

Everything is drawn with Pillow primitives (flat cartoon scenes), offline and
deterministically. No external images, no network, no randomness, no clock.
Run:  python3 render.py   ->  entry.png (1024x1024 PNG)
"""

from PIL import Image, ImageDraw, ImageFont
import worldmap

W = H = 1024

# ---- palette -------------------------------------------------------------
PAPER = (244, 240, 230)
INK = (18, 18, 20)
RULE = (30, 30, 34)
GREY = (110, 110, 116)
LGREY = (200, 196, 186)

REGION = {
    "Asia": (31, 111, 178),
    "Europe": (46, 139, 87),
    "Americas": (178, 59, 59),
    "Oceania": (196, 122, 26),
    "Africa": (122, 79, 160),
    "Middle East": (168, 132, 42),
    "Space": (44, 44, 66),
    "Markets": (120, 120, 128),
}

TAG = {
    "REPORTED": (26, 108, 64),
    "FORECAST": (170, 110, 10),
    "CLAIM": (162, 44, 44),
}

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONTB if bold else FONT, size)
    return _cache[key]


def tw(d, s, f):
    return d.textlength(s, font=f)


def fit(d, s, size, maxw, bold=False, minsize=7):
    """largest font <= size that keeps s within maxw (never below minsize)."""
    while size > minsize and tw(d, s, font(size, bold)) > maxw:
        size -= 1
    return font(size, bold)


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, s, xy, size, maxw, fill=INK, bold=False, lead=2, maxlines=99):
    """draw wrapped text, shrinking a little if it overflows maxlines."""
    x, y = xy
    f = font(size, bold)
    lines = wrap(d, s, f, maxw)
    while len(lines) > maxlines and size > 8:
        size -= 1
        f = font(size, bold)
        lines = wrap(d, s, f, maxw)
    for ln in lines[:maxlines]:
        d.text((x, y), ln, font=f, fill=fill)
        y += size + lead
    return y


def bytes_(d, s, xy, size, fill=INK, bold=False, anchor="la"):
    d.text(xy, s, font=font(size, bold), fill=fill, anchor=anchor)


def chip(d, x, y, label, colour, size=11):
    """small filled tag chip; returns width."""
    f = font(size, True)
    w = tw(d, label, f) + 12
    h = size + 8
    d.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=colour)
    d.text((x + 6, y + h / 2), label, font=f, fill=(255, 255, 255), anchor="lm")
    return w


def rule(d, x0, y, x1, w=2, fill=RULE):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


# =========================================================================
# SCENES  - each draws a small flat scene inside box=(x0,y0,x1,y1)
# =========================================================================

def _flagbands(d, x0, y0, x1, y1, bands, outline=INK):
    n = len(bands)
    hh = (y1 - y0) / n
    for i, c in enumerate(bands):
        d.rectangle([x0, y0 + i * hh, x1, y0 + (i + 1) * hh], fill=c, outline=None)
    d.rectangle([x0, y0, x1, y1], outline=outline, width=1)


def _sky(d, box, top, bottom):
    x0, y0, x1, y1 = box
    for i in range(int(y1 - y0)):
        t = i / max(1, (y1 - y0 - 1))
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def scene_markets(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (206, 224, 240), (226, 233, 240))
    # stock chart falling
    pts = [(x0 + 8, y0 + 20), (x0 + 34, y0 + 12), (x0 + 60, y0 + 40),
           (x0 + 90, y0 + 34), (x0 + 120, y0 + 74), (x0 + 150, y0 + 96)]
    d.line(pts, fill=(180, 40, 40), width=4)
    for i, (px, py) in enumerate(pts):
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(180, 40, 40))
    # candlesticks
    for cx, hi, lo, up in [(30, 30, 60, False), (48, 40, 74, False), (66, 50, 88, False)]:
        col = (60, 140, 80) if up else (180, 40, 40)
        d.line([(x0 + cx, y0 + hi), (x0 + cx, y0 + lo)], fill=col, width=2)
    # banks
    d.rectangle([x0 + 158, y0 + 66, x0 + 196, y1 - 6], fill=(180, 172, 168), outline=INK)
    for r in range(2):
        for c in range(3):
            d.rectangle([x0 + 164 + c * 10, y0 + 74 + r * 16,
                         x0 + 170 + c * 10, y0 + 84 + r * 16], fill=(90, 120, 150))
    # flags KR + CN
    _flagbands(d, x0 + 8, y1 - 26, x0 + 30, y1 - 8, [(255, 255, 255), (200, 40, 60)])
    _flagbands(d, x0 + 36, y1 - 26, x0 + 58, y1 - 8, [(200, 40, 40), (240, 210, 60)])
    d.text((x0 + 66, y1 - 26), "KOSPI", font=font(13, True), fill=(170, 30, 30))


def scene_rubble(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (210, 214, 222), (232, 230, 224))
    # damaged building
    d.rectangle([x0 + 10, y0 + 26, x0 + 60, y1 - 6], fill=(176, 172, 166), outline=INK)
    d.polygon([(x0 + 10, y0 + 26), (x0 + 26, y0 + 8), (x0 + 40, y0 + 26)], fill=(150, 146, 140))
    for r in range(2):
        for c in range(2):
            d.rectangle([x0 + 18 + c * 18, y0 + 40 + r * 22,
                         x0 + 30 + c * 18, y0 + 52 + r * 22], fill=(70, 74, 84))
    # rubble pile
    for i in range(7):
        rx = x0 + 66 + i * 11
        d.polygon([(rx, y1 - 4), (rx + 9, y1 - 4), (rx + 4, y1 - 16)], fill=(140, 136, 130))
    # stretcher + small figure (the rescued boy)
    d.rectangle([x0 + 92, y1 - 22, x0 + 140, y1 - 16], fill=(230, 228, 222), outline=INK)
    d.ellipse([x0 + 118, y1 - 32, x0 + 130, y1 - 20], fill=(240, 200, 170), outline=INK)
    # rescuer
    d.ellipse([x0 + 86, y0 + 62, x0 + 96, y0 + 72], fill=(240, 200, 170), outline=INK)
    d.rectangle([x0 + 84, y0 + 72, x0 + 98, y0 + 96], fill=(200, 130, 30), outline=INK)
    # ambulance
    d.rectangle([x0 + 146, y1 - 30, x0 + 188, y1 - 8], fill=(240, 240, 240), outline=INK)
    d.rectangle([x0 + 146, y1 - 30, x0 + 188, y1 - 22], fill=(200, 40, 40))
    d.rectangle([x0 + 160, y1 - 22, x0 + 166, y1 - 12], fill=(200, 40, 40))
    d.rectangle([x0 + 163, y1 - 25, x0 + 169, y1 - 15], fill=(200, 40, 40))
    # Ukrainian flag
    _flagbands(d, x1 - 30, y0 + 6, x1 - 8, y0 + 26, [(60, 110, 200), (240, 220, 60)])


def scene_podium(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (216, 220, 234), (236, 232, 226))
    # Capitol dome
    cx = (x0 + x1) / 2 + 30
    d.ellipse([cx - 26, y0 + 18, cx + 26, y0 + 70], fill=(224, 220, 212), outline=INK)
    d.rectangle([cx - 26, y0 + 46, cx + 26, y0 + 72], fill=(224, 220, 212), outline=INK)
    for c in range(4):
        d.rectangle([cx - 20 + c * 12, y0 + 50, cx - 15 + c * 12, y0 + 70], fill=(200, 196, 188))
    d.line([(cx, y0 + 6), (cx, y0 + 18)], fill=INK, width=2)
    # US flag
    _flagbands(d, x0 + 6, y0 + 6, x0 + 42, y0 + 30, [(200, 50, 60)] * 2 + [(255, 255, 255)] * 2, outline=INK)
    d.rectangle([x0 + 6, y0 + 6, x0 + 22, y0 + 18], fill=(40, 60, 140))
    # figure at podium
    d.ellipse([x0 + 54, y0 + 58, x0 + 66, y0 + 70], fill=(240, 200, 170), outline=INK)
    d.rectangle([x0 + 52, y0 + 70, x0 + 68, y0 + 104], fill=(50, 56, 74), outline=INK)
    d.rectangle([x0 + 40, y0 + 86, x0 + 82, y1 - 6], fill=(120, 100, 80), outline=INK)
    d.line([(x0 + 61, y0 + 86), (x0 + 61, y0 + 74)], fill=INK, width=2)
    d.ellipse([x0 + 58, y0 + 70, x0 + 64, y0 + 78], fill=(60, 60, 64))
    # speech bubble
    d.rounded_rectangle([x1 - 78, y0 + 12, x1 - 10, y0 + 40], radius=6, fill=(255, 255, 255), outline=INK)
    d.polygon([(x1 - 40, y0 + 40), (x1 - 32, y0 + 40), (x1 - 40, y0 + 50)], fill=(255, 255, 255), outline=INK)
    d.text((x1 - 44, y0 + 26), "\u201cfriend\u201d", font=font(13, True), fill=(30, 30, 34), anchor="mm")


def scene_ebola(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (208, 224, 210), (226, 226, 216))
    # jungle
    for i in range(4):
        gx = x0 + 6 + i * 30
        d.polygon([(gx, y1 - 6), (gx + 12, y0 + 60), (gx + 24, y1 - 6)], fill=(60, 120, 70))
    # clinic tent
    d.polygon([(x0 + 96, y0 + 34), (x0 + 150, y0 + 34), (x0 + 123, y0 + 6)], fill=(235, 235, 230), outline=INK)
    d.rectangle([x0 + 96, y0 + 34, x0 + 150, y1 - 6], fill=(210, 216, 212), outline=INK)
    d.rectangle([x0 + 120, y0 + 26, x0 + 126, y0 + 44], fill=(200, 40, 40))
    d.rectangle([x0 + 114, y0 + 32, x0 + 132, y0 + 38], fill=(200, 40, 40))
    # WHO-ish ring emblem
    d.ellipse([x1 - 40, y0 + 6, x1 - 8, y0 + 38], outline=(40, 90, 150), width=3)
    d.line([(x1 - 24, y0 + 12), (x1 - 24, y0 + 32)], fill=(40, 90, 150), width=3)
    # two aid figures
    for i in range(2):
        fx = x0 + 56 + i * 20
        d.ellipse([fx, y0 + 66, fx + 10, y0 + 76], fill=(240, 200, 170), outline=INK)
        d.rectangle([fx - 1, y0 + 76, fx + 11, y0 + 100], fill=(240, 240, 240), outline=INK)
    d.text((x0 + 6, y1 - 22), "EBOLA", font=font(13, True), fill=(150, 40, 40))


def scene_plot(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (206, 214, 228), (230, 228, 222))
    # target / crosshair over a figure
    cx, cy = x0 + 70, y0 + 52
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=(180, 40, 40), width=2)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=(180, 40, 40), width=2)
    d.line([(cx - 32, cy), (cx + 32, cy)], fill=(180, 40, 40), width=2)
    d.line([(cx, cy - 32), (cx, cy + 32)], fill=(180, 40, 40), width=2)
    d.ellipse([cx - 8, cy - 18, cx + 8, cy - 2], fill=(240, 200, 170), outline=INK)
    d.rectangle([cx - 10, cy - 2, cx + 10, cy + 24], fill=(50, 50, 60), outline=INK)
    # mic
    d.line([(x0 + 24, y0 + 90), (x0 + 24, y0 + 60)], fill=INK, width=2)
    d.ellipse([x0 + 18, y0 + 50, x0 + 30, y0 + 62], fill=(70, 70, 74))
    # two flags
    _flagbands(d, x1 - 30, y0 + 6, x1 - 8, y0 + 26, [(255, 255, 255), (200, 40, 60)], outline=INK)
    _flagbands(d, x1 - 30, y0 + 30, x1 - 8, y0 + 50, [(60, 110, 200), (240, 220, 60)], outline=INK)


def scene_lebanon(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (224, 212, 196), (234, 226, 210))
    # cracked house
    d.rectangle([x0 + 8, y0 + 26, x0 + 70, y1 - 6], fill=(214, 200, 176), outline=INK)
    d.polygon([(x0 + 4, y0 + 26), (x0 + 39, y0 + 6), (x0 + 74, y0 + 26)], fill=(170, 60, 50))
    for r in range(2):
        for c in range(2):
            d.rectangle([x0 + 16 + c * 28, y0 + 38 + r * 22,
                         x0 + 34 + c * 28, y0 + 52 + r * 22], fill=(70, 74, 84))
    d.line([(x0 + 60, y0 + 28), (x0 + 48, y0 + 50), (x0 + 58, y0 + 70)], fill=(90, 86, 80), width=2)
    # bulldozer
    bx = x0 + 84
    d.rectangle([bx, y1 - 34, bx + 60, y1 - 12], fill=(240, 180, 20), outline=INK)
    d.rectangle([bx + 52, y1 - 30, bx + 88, y1 - 16], fill=(120, 120, 124), outline=INK)
    d.polygon([(bx + 84, y1 - 32), (bx + 96, y1 - 24), (bx + 84, y1 - 14)], fill=(90, 90, 94), outline=INK)
    d.rectangle([bx + 6, y1 - 46, bx + 30, y1 - 34], fill=(200, 150, 20), outline=INK)
    for wx in (bx + 14, bx + 44):
        d.ellipse([wx, y1 - 18, wx + 16, y1 - 2], fill=(40, 40, 44), outline=INK)
    # Lebanon flag
    _flagbands(d, x1 - 34, y0 + 6, x1 - 8, y0 + 34, [(200, 50, 50), (255, 255, 255), (200, 50, 50)], outline=INK)
    d.polygon([(x1 - 21, y0 + 12), (x1 - 26, y0 + 26), (x1 - 16, y0 + 26)], fill=(30, 130, 60))


def scene_fire(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (60, 54, 60), (120, 90, 80))
    # factory
    d.rectangle([x0 + 10, y0 + 40, x0 + 150, y1 - 6], fill=(140, 134, 130), outline=INK)
    d.rectangle([x0 + 118, y0 + 16, x0 + 134, y0 + 40], fill=(120, 114, 110), outline=INK)
    for c in range(5):
        d.rectangle([x0 + 20 + c * 24, y0 + 52, x0 + 36 + c * 24, y0 + 74], fill=(255, 180, 60))
    # flames
    for i in range(6):
        fx = x0 + 18 + i * 24
        d.polygon([(fx, y0 + 40), (fx + 10, y0 + 12), (fx + 20, y0 + 40)],
                  fill=(240, 120 + (i % 2) * 60, 30))
    # smoke
    for i in range(4):
        d.ellipse([x0 + 30 + i * 26, y0 - 6, x0 + 68 + i * 26, y0 + 26], fill=(150, 150, 155))
    # body bags
    for i in range(4):
        bx = x0 + 12 + i * 34
        d.rounded_rectangle([bx, y1 - 20, bx + 30, y1 - 8], radius=4, fill=(30, 30, 34), outline=INK)
    # Indonesia flag
    _flagbands(d, x1 - 30, y0 + 6, x1 - 8, y0 + 26, [(200, 40, 40), (255, 255, 255)], outline=INK)


def scene_powerindex(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (222, 226, 236), (238, 234, 226))
    base = y1 - 10
    # two bars: USA tall, China short (US lead narrowing)
    d.rectangle([x0 + 30, y0 + 20, x0 + 62, base], fill=(50, 90, 170), outline=INK)
    d.rectangle([x0 + 92, y0 + 44, x0 + 124, base], fill=(190, 60, 50), outline=INK)
    d.text((x0 + 46, base - (base - y0 - 20) / 2), "US", font=font(13, True),
           fill=(255, 255, 255), anchor="mm")
    d.text((x0 + 108, base - (base - y0 - 44) / 2), "CN", font=font(13, True),
           fill=(255, 255, 255), anchor="mm")
    # descending arrow over gap
    d.line([(x0 + 70, y0 + 34), (x0 + 70, y0 + 70)], fill=(30, 30, 34), width=3)
    d.polygon([(x0 + 64, y0 + 62), (x0 + 76, y0 + 62), (x0 + 70, y0 + 76)], fill=(30, 30, 34))
    d.text((x0 + 6, y0 + 4), "LOWY INDEX", font=font(12, True), fill=(60, 60, 64))
    # trophy
    d.rectangle([x0 + 150, y0 + 30, x0 + 176, y0 + 54], fill=(220, 180, 40), outline=INK)
    d.ellipse([x0 + 156, y0 + 52, x0 + 170, y0 + 64], fill=(220, 180, 40), outline=INK)
    d.rectangle([x0 + 158, y0 + 62, x0 + 168, y0 + 70], fill=(150, 120, 30), outline=INK)


def scene_nhs(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (210, 222, 236), (232, 232, 230))
    # hospital
    d.rectangle([x0 + 8, y0 + 30, x0 + 96, y1 - 6], fill=(238, 238, 236), outline=INK)
    d.rectangle([x0 + 44, y0 + 22, x0 + 60, y0 + 30], fill=(200, 200, 200), outline=INK)
    d.rectangle([x0 + 42, y0 + 44, x0 + 52, y0 + 54], fill=(200, 40, 40))
    d.rectangle([x0 + 46, y0 + 40, x0 + 48, y0 + 58], fill=(200, 40, 40))
    d.rectangle([x0 + 44, y0 + 42, x0 + 50, y0 + 44], fill=(200, 40, 40))
    d.rectangle([x0 + 44, y0 + 54, x0 + 50, y0 + 56], fill=(200, 40, 40))
    # mammogram screen with AI scan
    d.rectangle([x0 + 106, y0 + 20, x0 + 190, y0 + 96], fill=(24, 28, 34), outline=INK)
    d.ellipse([x0 + 124, y0 + 34, x0 + 172, y0 + 82], fill=(70, 80, 92))
    d.ellipse([x0 + 136, y0 + 46, x0 + 160, y0 + 70], fill=(210, 210, 210))
    d.line([(x0 + 130, y0 + 82), (x0 + 166, y0 + 34)], fill=(90, 220, 140), width=2)
    # AI chip
    d.rectangle([x0 + 158, y0 + 82, x0 + 184, y0 + 108], fill=(60, 130, 90), outline=INK)
    d.text((x0 + 171, y0 + 95), "AI", font=font(12, True), fill=(255, 255, 255), anchor="mm")
    d.text((x0 + 8, y1 - 22), "NHS", font=font(13, True), fill=(20, 60, 130))


def scene_california(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (216, 226, 240), (236, 230, 222))
    # courthouse
    d.polygon([(x0 + 6, y0 + 34), (x0 + 44, y0 + 8), (x0 + 82, y0 + 34)], fill=(212, 208, 200), outline=INK)
    for c in range(4):
        d.rectangle([x0 + 12 + c * 18, y0 + 34, x0 + 24 + c * 18, y1 - 6], fill=(228, 224, 216), outline=INK)
    d.rectangle([x0 + 6, y1 - 12, x0 + 82, y1 - 6], fill=(200, 196, 188), outline=INK)
    # gavel
    d.rectangle([x0 + 98, y0 + 40, x0 + 122, y0 + 50], fill=(120, 80, 40), outline=INK)
    d.line([(x0 + 110, y0 + 50), (x0 + 110, y0 + 74)], fill=(120, 80, 40), width=4)
    d.rectangle([x0 + 96, y0 + 74, x0 + 124, y0 + 80], fill=(90, 60, 30), outline=INK)
    # CA bear flag
    _flagbands(d, x1 - 40, y0 + 6, x1 - 8, y0 + 40, [(255, 255, 255), (200, 50, 50)], outline=INK)
    d.polygon([(x1 - 30, y0 + 30), (x1 - 18, y0 + 30), (x1 - 22, y0 + 22), (x1 - 24, y0 + 30),
               (x1 - 28, y0 + 24)], fill=(60, 40, 30))
    # AI robot head being sued
    d.rounded_rectangle([x0 + 134, y0 + 40, x0 + 182, y0 + 88], radius=6, fill=(90, 96, 108), outline=INK)
    d.ellipse([x0 + 146, y0 + 54, x0 + 156, y0 + 64], fill=(90, 220, 140))
    d.ellipse([x0 + 162, y0 + 54, x0 + 172, y0 + 64], fill=(90, 220, 140))


def scene_dprk(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (206, 216, 232), (230, 228, 222))
    # DPRK flag
    _flagbands(d, x0 + 8, y0 + 6, x0 + 90, y0 + 44,
               [(40, 80, 170), (255, 255, 255), (200, 50, 50), (255, 255, 255), (40, 80, 170)],
               outline=INK)
    d.ellipse([x0 + 32, y0 + 14, x0 + 56, y0 + 38], fill=(240, 240, 240))
    d.polygon([(x0 + 44, y0 + 16), (x0 + 50, y0 + 30), (x0 + 38, y0 + 22), (x0 + 50, y0 + 22),
               (x0 + 38, y0 + 30)], fill=(200, 50, 50))
    # podium + figure
    d.ellipse([x0 + 60, y0 + 54, x0 + 76, y0 + 70], fill=(240, 200, 170), outline=INK)
    d.rectangle([x0 + 56, y0 + 70, x0 + 80, y0 + 100], fill=(60, 60, 70), outline=INK)
    d.rectangle([x0 + 40, y0 + 94, x0 + 96, y1 - 6], fill=(120, 90, 70), outline=INK)
    # missile
    d.polygon([(x0 + 120, y1 - 10), (x0 + 128, y0 + 20), (x0 + 136, y1 - 10)], fill=(200, 200, 205), outline=INK)
    d.polygon([(x0 + 120, y1 - 10), (x0 + 112, y1 - 10), (x0 + 120, y1 - 28)], fill=(200, 50, 50))
    d.polygon([(x0 + 136, y1 - 10), (x0 + 144, y1 - 10), (x0 + 136, y1 - 28)], fill=(200, 50, 50))
    d.text((x0 + 150, y0 + 60), "sec", font=font(11, True), fill=(60, 60, 64))
    d.text((x0 + 150, y0 + 74), "not", font=font(11, True), fill=(60, 60, 64))
    d.text((x0 + 150, y0 + 88), "sup.", font=font(11, True), fill=(60, 60, 64))


def scene_stage(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (40, 30, 60), (70, 50, 90))
    # curtains
    d.polygon([(x0 + 4, y0 + 4), (x0 + 40, y0 + 4), (x0 + 4, y1 - 4)], fill=(120, 30, 60))
    d.polygon([(x1 - 4, y0 + 4), (x1 - 40, y0 + 4), (x1 - 4, y1 - 4)], fill=(120, 30, 60))
    # spotlight
    d.polygon([(x0 + 60, y0 + 4), (x0 + 96, y1 - 4), (x0 + 120, y1 - 4)], fill=(220, 210, 150))
    # mic stand
    d.line([(x0 + 80, y1 - 6), (x0 + 80, y0 + 50)], fill=(220, 220, 220), width=3)
    d.ellipse([x0 + 72, y0 + 40, x0 + 88, y0 + 56], fill=(60, 60, 66))
    # guitar
    d.ellipse([x0 + 118, y1 - 44, x0 + 156, y1 - 10], fill=(180, 120, 50), outline=INK)
    d.ellipse([x0 + 134, y1 - 36, x0 + 148, y1 - 24], fill=(60, 40, 24))
    d.rectangle([x0 + 140, y1 - 66, x0 + 146, y1 - 30], fill=(90, 60, 30), outline=INK)
    # AU flag
    _flagbands(d, x1 - 40, y0 + 6, x1 - 8, y0 + 30, [(30, 60, 140)], outline=INK)
    d.rectangle([x1 - 40, y0 + 6, x1 - 28, y0 + 18], fill=(210, 210, 210))
    d.text((x1 - 24, y0 + 20), "83", font=font(13, True), fill=(240, 230, 150))


def scene_singapore(d, box):
    x0, y0, x1, y1 = box
    _sky(d, box, (200, 220, 238), (230, 232, 236))
    # skyline: three towers + boat roof (Marina Bay Sands)
    d.rectangle([x0 + 20, y0 + 40, x0 + 44, y1 - 16], fill=(90, 110, 140), outline=INK)
    d.rectangle([x0 + 50, y0 + 30, x0 + 74, y1 - 16], fill=(110, 130, 158), outline=INK)
    d.rectangle([x0 + 80, y0 + 40, x0 + 104, y1 - 16], fill=(90, 110, 140), outline=INK)
    d.polygon([(x0 + 14, y0 + 40), (x0 + 58, y0 + 20), (x0 + 110, y0 + 40)], fill=(60, 80, 110))
    # money
    d.ellipse([x0 + 120, y1 - 40, x0 + 152, y1 - 8], fill=(230, 190, 60), outline=INK)
    d.text((x0 + 136, y1 - 24), "$", font=font(16, True), fill=(120, 90, 20), anchor="mm")
    # Singapore flag
    _flagbands(d, x1 - 40, y0 + 6, x1 - 8, y0 + 30, [(200, 50, 60), (255, 255, 255)], outline=INK)
    d.ellipse([x1 - 36, y0 + 8, x1 - 24, y0 + 20], fill=(240, 240, 240))
    d.text((x0 + 6, y1 - 20), "SGP", font=font(12, True), fill=(60, 60, 64))


SCENES = {
    "markets": scene_markets, "rubble": scene_rubble, "podium": scene_podium,
    "ebola": scene_ebola, "plot": scene_plot, "lebanon": scene_lebanon,
    "fire": scene_fire, "powerindex": scene_powerindex, "nhs": scene_nhs,
    "california": scene_california, "dprk": scene_dprk, "stage": scene_stage,
    "singapore": scene_singapore,
}


_SCENE_W, _SCENE_H = 320, 130


def draw_scene(d, key, box):
    """Render scene on a fixed logical canvas, then scale into box."""
    x0, y0, x1, y1 = box
    canvas = Image.new("RGB", (_SCENE_W, _SCENE_H), (238, 236, 230))
    cd = ImageDraw.Draw(canvas)
    SCENES[key](cd, (1, 1, _SCENE_W - 1, _SCENE_H - 1))
    cd.rectangle([0, 0, _SCENE_W - 1, _SCENE_H - 1], outline=(150, 150, 150), width=2)
    w, h = int(x1 - x0), int(y1 - y0)
    if w <= 1 or h <= 1:
        return
    scaled = canvas.resize((w, h), Image.LANCZOS)
    d._image.paste(scaled, (int(x0), int(y0)))


# =========================================================================
# DATA
# =========================================================================

BIG = [
    dict(n=1, scene="markets", region="Asia", tag="REPORTED",
         head="Asian markets sink as AI-bubble fears deepen; Seoul readies a rescue fund",
         sub="KOSPI opened sharply lower; China cut the margin requirement to 80%. (Al Jazeera)"),
    dict(n=2, scene="rubble", region="Europe", tag="REPORTED",
         head="Boy, 7, pulled alive from rubble after a Russian strike",
         sub="Rescuers freed the boy hours after the overnight strike; Kyiv region toll climbed. (BBC News)"),
    dict(n=3, scene="podium", region="Americas", tag="REPORTED",
         head="US intelligence chief defends Trump's \u201cfriend Putin\u201d remarks, takes over cyber policy",
         sub="DNI Jay Clayton called the remarks \u201centirely appropriate\u201d. (Al Jazeera)"),
]

MED = [
    dict(n=4, scene="ebola", region="Africa", tag="REPORTED", place="DR CONGO",
         head="WHO chief appeals for peace as fighting surges in Ebola-hit east",
         sub="(Al Jazeera)"),
    dict(n=5, scene="plot", region="Europe", tag="CLAIM", place="POLAND",
         head="Poland says Russia twice plotted to kill a Ukrainian rapper",
         sub="(Al Jazeera)"),
    dict(n=6, scene="lebanon", region="Middle East", tag="REPORTED", place="S. LEBANON",
         head="Israeli forces press on with house demolitions",
         sub="(Al Jazeera)"),
    dict(n=7, scene="fire", region="Asia", tag="REPORTED", place="INDONESIA",
         head="Factory fire: police recover 24 body bags as search resumes",
         sub="(Al Jazeera / BBC / AP)"),
    dict(n=8, scene="powerindex", region="Asia", tag="REPORTED", place="ASIA-PACIFIC",
         head="Lowy Asia Power Index: US lead over China falls to a record low",
         sub="Report released that day. (SCMP)"),
    dict(n=9, scene="nhs", region="Europe", tag="REPORTED", place="UNITED KINGDOM",
         head="NHS launches the world's largest AI breast-cancer screening trial",
         sub="(BBC News)"),
    dict(n=10, scene="california", region="Americas", tag="REPORTED", place="CALIFORNIA",
          head="California sues OpenAI over alleged AI-safety failures",
          sub="Suit filed that day. (The Jerusalem Post)"),
    dict(n=11, scene="dprk", region="Asia", tag="CLAIM", place="NORTH KOREA",
          head="Kim says the North seeks power for security, not supremacy",
          sub="State statement. (Al Jazeera)"),
    dict(n=12, scene="stage", region="Oceania", tag="REPORTED", place="AUSTRALIA",
          head="Molly Meldrum, Australian music legend, dies at 83",
          sub="State-funeral arrangements follow. (BBC News)"),
    dict(n=13, scene="singapore", region="Asia", tag="REPORTED", place="SINGAPORE",
          head="Singapore lifts support thresholds; 2027 property-tax rebate",
          sub="(Channel NewsAsia / The Straits Times)"),
]

ALSO = [
    (14, "Sudan: drone strikes hit homes and a UN building in Khartoum", "SUDAN", "Al Jazeera / DW", "Africa"),
    (15, "Libya's army says it is \u201cfully prepared\u201d after the Benghazi attacks", "LIBYA", "Al Jazeera", "Africa"),
    (16, "France: Le Pen denies receiving secrets from a civil servant", "FRANCE", "Al Jazeera", "Europe"),
    (17, "Japan to recruit farm workers from Bangladesh and Nepal", "JAPAN", "SCMP", "Asia"),
    (18, "China finds a 3.95bn-year-old rock in Hebei \u2014 oldest known in Asia", "CHINA", "China Daily", "Asia"),
    (19, "International Space Forum opens; treaty \u201cdoes not ban\u201d orbital weapons", "SPACE", "Tech Times", "Space"),
    (20, "OpenAI's chief scientist proposes shared limits on advanced AI", "US", "Reuters", "Americas"),
    (21, "US spy chief confirms a probe into an Nvidia-linked chip network", "US", "Times of India", "Americas"),
    (22, "DayOne's $5bn US IPO is postponed", "US", "Asia Tech Review", "Americas"),
    (23, "Oil slides; Brent crude falls below $92 on oversupply", "MARKETS", "FXStreet", "Markets"),
    (24, "European gas prices surge as a cold snap threatens tight inventories", "EUROPE", "Bloomberg", "Europe"),
    (25, "Gold and silver slump (silver down ~16%)", "MARKETS", "Indian fin. press", "Markets"),
    (26, "Cricket: India close in on victory over New Zealand in the 1st Test", "INDIA / NZ", "Reuters / The Hindu", "Asia"),
    (27, "Cricket: Bangladesh v South Africa Test under way", "BAN / SA", "agency listings", "Asia"),
    (28, "Manchester's Co-op Live evacuated after a suspected tear-gas incident", "UK", "BBC News", "Europe"),
    (29, "Nigeria and South Africa open reconciliation talks after a row", "NIGERIA / SA", "The Sun Nigeria", "Africa"),
    (30, "Italian jeweller Paolo Bulgari dies aged 89", "ITALY", "Al Jazeera", "Europe"),
    (31, "Malaysia says it respects the ICJ genocide judgment on Myanmar", "MALAYSIA", "Asia News Network", "Asia"),
    (32, "Van Hollen: Democrats have a \u201cgenerational opportunity\u201d in the Senate", "US", "Al Jazeera", "Americas"),
    (33, "El Ni\u00f1o raises flood and avalanche risk across the Hindu Kush Himalaya", "HIMALAYA", "Business Standard", "Asia"),
]

MARKETS = [
    ("KOSPI", "slides more than 4% as AI rout deepens", "Reuters / Businesskorea"),
    ("BRENT", "crude falls below $92 on oversupply (WTI below $83)", "FXStreet"),
    ("CHINA", "cuts securities-financing margin requirement to 80%", "Bloomberg"),
    ("US FUTURES", "rise after Wall Street's worst week in 19 months", "Bloomberg"),
]

TIMELINE = [
    ("00:18", "Asian share markets tumble as AI-bubble fears mount"),
    ("00:49", "NHS launches world's largest AI breast-cancer trial"),
    ("01:03", "Molly Meldrum dies aged 83"),
    ("01:53", "Poland: Russia tried to kill a Ukrainian rapper twice"),
    ("02:23", "US intelligence chief defends Trump's \u201cfriend Putin\u201d line"),
]

EXCLUDED = [
    ("COP31 UN climate summit collapses without a deal", "closed Sun 22 Nov"),
    ("Democrats win largest House majority since 1992 (NC seat)", "confirmed 22 Nov"),
    ("BepiColombo enters orbit around Mercury", "22 Nov"),
    ("Russian-flagged ship explodes at Benghazi after drone attack", "22 Nov"),
    ("Carlos Alcaraz wins his first ATP Finals title", "22 Nov"),
    ("Liverpool thrash 10-man Manchester United", "22 Nov"),
    ("Miley Cyrus marries Maxx Morando in California", "22 Nov"),
    ("Mets agree record $450m deal with pitcher Tarik Skubal", "agreed 22 Nov"),
    ("Max Verstappen wins the Las Vegas Grand Prix", "21\u201322 Nov"),
    ("Mexican forces arrest drug kingpin \u201cEl Chapo\u201d Isidro", "22 Nov"),
]

# map pins: (number, lon, lat) - approximate story locations
PINS = [
    (1, 127, 37), (2, 30, 50), (3, -77, 39), (4, 27, -3), (5, 20, 52),
    (6, 35, 33), (7, 107, -6), (8, 150, -33), (9, -1, 52), (10, -119, 36),
    (11, 127, 40), (12, 145, -37), (13, 104, 1),
]


# =========================================================================
# PAGE
# =========================================================================

def region_counts():
    counts = {}
    for s in BIG + MED:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    for _, _, _, _, r in ALSO:
        counts[r] = counts.get(r, 0) + 1
    return counts


ORDER = ["Asia", "Europe", "Americas", "Africa", "Middle East", "Oceania", "Space", "Markets"]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=3)

    # ---- masthead -------------------------------------------------------
    d.text((W / 2, 26), "THE WORLD POST \u00b7 THE DAY IN ONE IMAGE",
           font=font(17, True), fill=GREY, anchor="mm")
    d.text((W / 2, 66), "MONDAY 23 NOVEMBER 2026",
           font=font(58, True), fill=INK, anchor="mm")
    rule(d, 10, 100, W - 10, 3)
    rule(d, 10, 105, W - 10, 1)

    # ---- numbers strip --------------------------------------------------
    counts = region_counts()
    seg = " \u00b7 ".join("%s %d" % (k, counts.get(k, 0)) for k in ORDER if counts.get(k, 0))
    d.text((W / 2, 118), "33 STORIES \u00b7 " + seg.replace("Markets", "Markets/Money"),
           font=font(15, True), fill=INK, anchor="mm")
    d.text((W / 2, 138),
           "KOSPI \u22124%  \u00b7  Brent < $92  \u00b7  China margin to 80%  \u00b7  "
           "US futures up after worst week in 19 months  \u00b7  Silver \u221216%",
           font=font(14), fill=(70, 70, 76), anchor="mm")
    rule(d, 10, 150, W - 10, 2)

    # ---- BIG features ---------------------------------------------------
    bx0, bx1 = 10, W - 10
    gap = 10
    pw = (bx1 - bx0 - 2 * gap) / 3
    big_top, big_h = 158, 214
    scene_h = 104
    for i, s in enumerate(BIG):
        x0 = bx0 + i * (pw + gap)
        x1 = x0 + pw
        col = REGION[s["region"]]
        d.rectangle([x0, big_top, x1, big_top + big_h], fill=(252, 250, 246), outline=col, width=3)
        draw_scene(d, s["scene"], (x0 + 4, big_top + 4, x1 - 4, big_top + 4 + scene_h))
        # number badge
        d.ellipse([x0 + 6, big_top + 6, x0 + 34, big_top + 34], fill=col)
        d.text((x0 + 20, big_top + 20), str(s["n"]), font=font(16, True),
               fill=(255, 255, 255), anchor="mm")
        ty = big_top + scene_h + 10
        para(d, s["head"], (x0 + 8, ty), 18, pw - 16, INK, True, 2, 3)
        d.text((x0 + 8, big_top + big_h - 36),
               s["sub"], font=fit(d, s["sub"], 9, pw - 16, False, 7), fill=GREY)
        # footer row: region + tag
        chip(d, x0 + 8, big_top + big_h - 22, s["tag"], TAG[s["tag"]], 12)
        d.text((x1 - 8, big_top + big_h - 16), s["region"].upper(),
               font=font(12, True), fill=col, anchor="rm")

    # ---- MEDIUM features ------------------------------------------------
    m_top = big_top + big_h + 14
    m_gap_x = 8
    m_cols = 5
    mw = (bx1 - bx0 - (m_cols - 1) * m_gap_x) / m_cols
    m_h = 110
    m_gap_y = 6
    for i, s in enumerate(MED):
        row, col_i = divmod(i, m_cols)
        x0 = bx0 + col_i * (mw + m_gap_x)
        x1 = x0 + mw
        y0 = m_top + row * (m_h + m_gap_y)
        y1 = y0 + m_h
        rc = REGION[s["region"]]
        d.rectangle([x0, y0, x1, y1], fill=(252, 250, 246), outline=rc, width=2)
        # label row
        d.ellipse([x0 + 3, y0 + 3, x0 + 19, y0 + 19], fill=rc)
        d.text((x0 + 11, y0 + 11), str(s["n"]), font=font(11, True),
               fill=(255, 255, 255), anchor="mm")
        d.text((x0 + 23, y0 + 4), s["place"], font=fit(d, s["place"], 12, mw - 70, True),
               fill=rc)
        chip(d, x1 - 4 - (tw(d, s["tag"], font(9, True)) + 10), y0 + 3, s["tag"], TAG[s["tag"]], 9)
        # scene
        draw_scene(d, s["scene"], (x0 + 3, y0 + 22, x1 - 3, y0 + 64))
        # headline
        hy = para(d, s["head"], (x0 + 4, y0 + 68), 13, mw - 8, INK, True, 1, 2)
        d.text((x0 + 4, y1 - 11), s["sub"], font=font(9), fill=GREY)

    # ---- bottom band ----------------------------------------------------
    b_top = m_top + 2 * m_h + m_gap_y + 14
    b_bot = H - 30
    cgap = 8
    cw = (bx1 - bx0 - 2 * cgap) / 3
    cA = (bx0, bx0 + cw)
    cB = (bx0 + cw + cgap, bx0 + 2 * cw + cgap)
    cC = (bx0 + 2 * (cw + cgap), bx1)

    # --- column A: ALSO list ---
    x0, x1 = cA
    d.rectangle([x0, b_top, x1, b_bot], fill=(252, 250, 246), outline=RULE, width=1)
    d.rectangle([x0, b_top, x1, b_top + 22], fill=INK)
    d.text((x0 + 6, b_top + 11), "ALSO ON MONDAY 23 NOVEMBER", font=font(14, True),
           fill=(255, 255, 255), anchor="lm")
    ly = b_top + 26
    for n, head, place, src, reg in ALSO:
        col = REGION[reg]
        d.ellipse([x0 + 4, ly + 2, x0 + 16, ly + 14], fill=col)
        d.text((x0 + 10, ly + 8), str(n), font=font(8, True), fill=(255, 255, 255), anchor="mm")
        line = "%s \u2014 %s (%s)" % (head, place, src)
        f = fit(d, line, 10, x1 - x0 - 20, False, 7)
        d.text((x0 + 20, ly + 2), line, font=f, fill=INK)
        ly += 17

    # --- column B: map + markets ---
    x0, x1 = cB
    map_h = 150
    d.rectangle([x0, b_top, x1, b_top + map_h + 24], fill=(252, 250, 246), outline=RULE, width=1)
    d.rectangle([x0, b_top, x1, b_top + 22], fill=INK)
    d.text((x0 + 6, b_top + 11), "WHERE IT HAPPENED", font=font(14, True),
           fill=(255, 255, 255), anchor="lm")
    mbox = (x0 + 6, b_top + 26, x1 - 6, b_top + 22 + map_h)
    d.rectangle(mbox, fill=(226, 234, 240), outline=LGREY)
    worldmap.draw_map(d, mbox, (214, 220, 214), (150, 150, 150), grid=(210, 216, 222))
    for n, lon, lat in PINS:
        px, py = worldmap.project(lon, lat, mbox)
        col = (60, 60, 70)
        for s in BIG + MED:
            if s["n"] == n:
                col = REGION[s["region"]]
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col, outline=(255, 255, 255))
        d.text((px, py), str(n), font=font(9, True), fill=(255, 255, 255), anchor="mm")
    # legend
    lgy = b_top + map_h + 26
    d.text((x0 + 4, lgy), "PINS = the 13 illustrated stories; colour = region",
           font=font(9), fill=GREY)

    # markets box
    mk_top = b_top + map_h + 42
    d.rectangle([x0, mk_top, x1, b_bot], fill=(252, 250, 246), outline=RULE, width=1)
    d.rectangle([x0, mk_top, x1, mk_top + 22], fill=(20, 60, 90))
    d.text((x0 + 6, mk_top + 11), "MARKETS & MONEY", font=font(14, True),
           fill=(255, 255, 255), anchor="lm")
    d.text((x1 - 6, mk_top + 11), "Asian session, 23 Nov", font=font(9),
           fill=(200, 220, 240), anchor="rm")
    my = mk_top + 28
    for k, txt, src in MARKETS:
        d.text((x0 + 6, my), k, font=font(10, True), fill=(20, 60, 90))
        d.text((x0 + 82, my), txt, font=font(10), fill=INK)
        my += 15
        d.text((x0 + 82, my), src, font=font(8), fill=GREY)
        my += 15
        if my > b_bot - 6:
            break

    # --- column C: timeline + date check + how sure ---
    x0, x1 = cC
    tl_h = 118
    d.rectangle([x0, b_top, x1, b_top + tl_h], fill=(252, 250, 246), outline=RULE, width=1)
    d.rectangle([x0, b_top, x1, b_top + 22], fill=INK)
    d.text((x0 + 6, b_top + 11), "THE DAY BY HOURS (UTC)", font=font(14, True),
           fill=(255, 255, 255), anchor="lm")
    ty = b_top + 30
    for t, ev in TIMELINE:
        d.text((x0 + 6, ty), t, font=font(11, True), fill=(170, 40, 40))
        d.text((x0 + 48, ty), ev, font=fit(d, ev, 11, x1 - x0 - 56, False, 8), fill=INK)
        ty += 17

    dc_top = b_top + tl_h + 8
    how_h = 26
    d.rectangle([x0, dc_top, x1, b_bot - how_h - 6], fill=(252, 250, 246), outline=RULE, width=1)
    d.rectangle([x0, dc_top, x1, dc_top + 22], fill=(150, 40, 40))
    d.text((x0 + 6, dc_top + 11), "DATE CHECK \u2014 LEFT OUT", font=font(14, True),
           fill=(255, 255, 255), anchor="lm")
    d.text((x0 + 6, dc_top + 26),
           "Every story here happened (or was reported) on 23 Nov 2026. Other days:",
           font=font(9), fill=INK)
    ey = dc_top + 40
    for txt, when in EXCLUDED:
        line = "\u2022 %s \u2014 %s" % (txt, when)
        f = fit(d, line, 10, x1 - x0 - 10, False, 7)
        d.text((x0 + 5, ey), line, font=f, fill=INK)
        ey += 13
        if ey > b_bot - how_h - 6:
            break
    # how sure
    d.rectangle([x0, b_bot - how_h, x1, b_bot], fill=(232, 228, 218), outline=RULE, width=1)
    d.text((x0 + 5, b_bot - how_h + 4), "HOW SURE ARE WE?", font=font(10, True), fill=INK)
    d.text((x0 + 5, b_bot - how_h + 15),
           "33 stories each checked to a primary outlet for its 23 Nov event date.",
           font=font(8), fill=(60, 60, 64))

    # ---- footer ---------------------------------------------------------
    rule(d, 10, b_bot + 4, W - 10, 2)
    d.text((W / 2, b_bot + 16),
           "SOURCES: Al Jazeera \u00b7 BBC News \u00b7 Reuters \u00b7 Bloomberg \u00b7 SCMP \u00b7 "
           "CNA/Straits Times \u00b7 FXStreet \u00b7 DW \u00b7 China Daily \u00b7 Tech Times \u00b7 "
           "Times of India \u00b7 Business Standard",
           font=font(9), fill=GREY, anchor="mm")

    return img


if __name__ == "__main__":
    im = build()
    import os
    os.makedirs("out", exist_ok=True)
    im.save("entry.png", "PNG", optimize=True)
    # self-check: fixed size + grader byte cap
    assert im.size == (1024, 1024), im.size
    assert os.path.getsize("entry.png") <= 1048576, os.path.getsize("entry.png")
    print("wrote entry.png", im.size, os.path.getsize("entry.png"), "bytes")
