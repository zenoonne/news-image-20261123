#!/usr/bin/env python3
"""render.py - draws the Monday 23 November 2026 newspaper front page.

Everything is drawn with Pillow primitives (flat cartoon scenes), fully offline and
deterministically: no external images, no network, no randomness, no clock.
Run:  python3 render.py   ->  entry.png (1024x1024 PNG, <= 1 MiB)
"""

from PIL import Image, ImageDraw, ImageFont
import worldmap

W = H = 1024

# ---- palette -------------------------------------------------------------
PAPER = (243, 239, 228)
INK = (20, 20, 22)
RULE = (28, 28, 32)
GREY = (104, 104, 110)
LGREY = (203, 198, 187)
WHITE = (250, 249, 245)

REGION = {
    "ASIA": (28, 106, 176),
    "EUROPE": (33, 122, 88),
    "AMERICAS": (176, 54, 54),
    "MIDDLE EAST": (156, 120, 30),
    "AFRICA": (120, 74, 158),
    "OCEANIA": (192, 116, 22),
    "WORLD": (46, 46, 68),
    "MARKETS": (94, 98, 110),
}
TAG = {
    "REPORTED": (26, 110, 66),
    "FORECAST": (168, 108, 8),
    "CLAIM": (162, 44, 44),
}

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_cache = {}


def F(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONTB if bold else FONT, size)
    return _cache[key]


def tw(d, s, f):
    return d.textlength(s, font=f)


def fit(d, s, size, maxw, bold=False, minsize=6):
    while size > minsize and tw(d, s, F(size, bold)) > maxw:
        size -= 1
    return F(size, bold)


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


def one_line(d, s, f, maxw):
    """Truncate s to a single line that fits maxw."""
    if tw(d, s, f) <= maxw:
        return s
    out = s
    while out and tw(d, out + "\u2026", f) > maxw:
        out = out[:-1]
    return out.rstrip() + "\u2026"


def para(d, s, xy, size, maxw, fill=INK, bold=False, lead=2, maxlines=99):
    x, y = xy
    f = F(size, bold)
    lines = wrap(d, s, f, maxw)
    while len(lines) > maxlines and size > 7:
        size -= 1
        f = F(size, bold)
        lines = wrap(d, s, f, maxw)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += size + lead
    return y


def chip(d, x, y, text, color, size=10, pad=4):
    f = F(size, True)
    w = tw(d, text, f) + 2 * pad
    h = size + 5
    d.rectangle([x, y, x + w, y + h], fill=color)
    d.text((x + pad, y + 2), text, font=f, fill=WHITE)
    return w, h


# ---- scene primitives ----------------------------------------------------
def sky(d, box, top, bot):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=bot)
    d.rectangle([x, y, x + w, y + int(h * 0.55)], fill=top)


def ground(d, box, frac, color):
    x, y, w, h = box
    gy = y + int(h * frac)
    d.rectangle([x, gy, x + w, y + h], fill=color)
    return gy


def building(d, x, base, w, h, color, win=(238, 232, 210), cols=2, rows=3):
    d.rectangle([x, base - h, x + w, base], fill=color)
    mw = w / (cols + 1)
    mh = h / (rows + 1)
    for c in range(cols):
        for r in range(rows):
            wx = x + mw * (c + 0.5) - mw * 0.22
            wy = base - h + mh * (r + 0.6)
            d.rectangle([wx, wy, wx + mw * 0.44, wy + mh * 0.42], fill=win)


def flag(d, x, y, w, h, stripes):
    d.line([(x, y), (x, y + h * 2.1)], fill=(70, 70, 74), width=2)
    n = len(stripes)
    for i, c in enumerate(stripes):
        d.rectangle([x + 2, y + i * h / n, x + 2 + w, y + (i + 1) * h / n], fill=c)


def star(d, cx, cy, r, color, n=5):
    import math
    pts = []
    for i in range(n * 2):
        ang = -math.pi / 2 + i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


# ---- the 13 scenes -------------------------------------------------------
def sc_market(d, box):
    sky(d, box, (232, 238, 246), (245, 242, 234))
    x, y, w, h = box
    gy = ground(d, box, 0.74, (222, 218, 206))
    nb = (w - 24) / 6
    for i, bh in enumerate((10, 15, 13, 20, 28, 44)):
        bx = x + 12 + i * nb
        d.rectangle([bx, gy - bh, bx + nb - 5, gy], fill=(196, 60, 60) if i < 3 else (60, 150, 92))
    pts = [(x + 14 + i * (w - 28) / 6, gy - 4 - i * (h * 0.075)) for i in range(7)]
    d.line(pts, fill=(198, 150, 30), width=4, joint="curve")
    d.polygon([(pts[-1][0], pts[-1][1] - 9), (pts[-1][0] - 12, pts[-1][1] + 5),
               (pts[-1][0] + 3, pts[-1][1] + 5)], fill=(198, 150, 30))
    d.text((x + 46, y + 6), "NVIDIA +31%", font=F(14, True), fill=(176, 40, 40))
    d.text((x + 46, y + 24), "NASDAQ +6.5%", font=F(12, True), fill=(40, 90, 150))


def sc_ship(d, box):
    sky(d, box, (196, 214, 236), (120, 158, 200))
    x, y, w, h = box
    sea = ground(d, box, 0.5, (74, 120, 172))
    for i in range(3):
        d.line([(x + 6 + i * (w / 3), sea + i * 12), (x + w - 6, sea + i * 12)], fill=(96, 138, 186), width=2)
    d.polygon([(x + 54, sea + 4), (x + w - 54, sea + 4), (x + w - 70, sea + 26), (x + 68, sea + 26)], fill=(64, 64, 70))
    d.rectangle([x + 108, sea - 24, x + w - 118, sea + 4], fill=(88, 88, 94))
    d.rectangle([x + w - 152, sea - 38, x + w - 118, sea - 24], fill=(150, 60, 60))
    flag(d, x + w - 150, sea - 64, 22, 8, [(250, 250, 250), (40, 70, 170), (200, 40, 40)])
    d.polygon([(x + 78, sea - 24), (x + 92, sea - 50), (x + 106, sea - 24)], fill=(232, 130, 30))
    d.polygon([(x + 86, sea - 24), (x + 100, sea - 62), (x + 114, sea - 24)], fill=(240, 176, 40))
    d.ellipse([x + 60, sea - 74, x + 140, sea - 40], fill=(150, 150, 150))
    for dx in (x + 30, x + w - 70):
        d.line([(dx, sea - 78), (dx + 16, sea - 82), (dx + 32, sea - 78)], fill=(40, 40, 44), width=2)
        d.line([(dx + 16, sea - 82), (dx + 16, sea - 70)], fill=(40, 40, 44), width=2)


def sc_gulf(d, box):
    sky(d, box, (240, 220, 190), (244, 226, 198))
    x, y, w, h = box
    sea = ground(d, box, 0.56, (62, 112, 158))
    d.ellipse([x + w - 66, y + 8, x + w - 18, y + 56], fill=(240, 196, 120))
    d.polygon([(x + w - 96, sea + 4), (x + w - 22, sea + 4), (x + w - 34, sea + 24), (x + w - 84, sea + 24)], fill=(52, 52, 58))
    d.rectangle([x + w - 74, sea - 14, x + w - 40, sea + 4], fill=(96, 96, 100))
    d.polygon([(x + 16, sea + 6), (x + 118, sea + 6), (x + 108, sea + 24), (x + 26, sea + 24)], fill=(70, 74, 80))
    d.rectangle([x + 68, sea - 22, x + 106, sea + 6], fill=(90, 94, 100))
    d.arc([x + 40, y + 12, x + w - 100, sea - 18], start=205, end=335, fill=(190, 60, 60), width=3)
    d.arc([x + 70, y + 26, x + w - 70, sea - 26], start=200, end=325, fill=(190, 60, 60), width=3)
    flag(d, x + 18, sea - 54, 20, 8, [(60, 120, 60), (250, 250, 250), (200, 40, 40)])
    flag(d, x + w - 42, sea - 54, 20, 8, [(40, 60, 140), (250, 250, 250), (200, 40, 40)])


def sc_football(d, box):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=(46, 128, 76))
    for i in range(1, 4):
        d.line([(x + i * w / 4, y), (x + i * w / 4, y + h)], fill=(60, 150, 92), width=2)
    d.rectangle([x + w / 2 - 22, y + 8, x + w / 2 + 22, y + h - 8], outline=(236, 238, 230), width=2)
    d.ellipse([x + w / 2 - 9, y + h / 2 - 9, x + w / 2 + 9, y + h / 2 + 9], outline=(236, 238, 230), width=2)
    gx = x + w - 50
    d.rectangle([gx - 12, y + h - 30, gx + 12, y + h - 16], fill=(216, 170, 40))
    d.rectangle([gx - 20, y + h - 52, gx + 20, y + h - 30], fill=(228, 184, 48))
    d.ellipse([gx - 20, y + h - 52, gx + 20, y + h - 34], fill=(250, 220, 110))
    d.line([(gx - 20, y + h - 48), (gx - 30, y + h - 36)], fill=(228, 184, 48), width=5)
    d.line([(gx + 20, y + h - 48), (gx + 30, y + h - 36)], fill=(228, 184, 48), width=5)
    d.ellipse([x + 14, y + h - 44, x + 30, y + h - 28], fill=(250, 250, 250), outline=(30, 30, 30), width=2)
    star(d, x + 22, y + h - 36, 6, (40, 40, 44), 5)


def sc_handshake(d, box):
    sky(d, box, (222, 234, 244), (238, 240, 236))
    x, y, w, h = box
    base = ground(d, box, 0.76, (150, 160, 150))
    d.rectangle([x + 26, base - 40, x + 88, base], fill=(120, 132, 150))
    d.rectangle([x + w - 88, base - 40, x + w - 26, base], fill=(120, 132, 150))
    for cx in (x + 50, x + w - 50):
        d.ellipse([cx - 9, base - 80, cx + 9, base - 62], fill=(210, 172, 130))
        d.rectangle([cx - 11, base - 62, cx + 11, base - 24], fill=(80, 80, 90))
    d.line([(x + 56, base - 52), (x + w - 56, base - 52)], fill=(210, 172, 130), width=7)
    flag(d, x + 16, y + 14, 22, 8, [(240, 150, 40), (250, 250, 250), (40, 130, 60)])
    flag(d, x + w - 40, y + 14, 22, 8, [(200, 40, 50), (40, 60, 150)])
    d.text((x + w / 2 - 24, y + 12), "$1.6bn", font=F(13, True), fill=(30, 110, 60))


def sc_capitol(d, box):
    sky(d, box, (214, 226, 240), (236, 238, 240))
    x, y, w, h = box
    base = ground(d, box, 0.82, (160, 166, 172))
    cx = x + w / 2
    d.rectangle([cx - 40, base - 36, cx + 40, base], fill=(226, 224, 214))
    d.pieslice([cx - 34, base - 66, cx + 34, base - 10], 180, 360, fill=(238, 236, 226))
    d.ellipse([cx - 9, base - 88, cx + 9, base - 66], fill=(238, 236, 226))
    d.line([(cx, base - 98), (cx, base - 88)], fill=(150, 150, 150), width=2)
    for i in range(4):
        d.rectangle([cx - 34 + i * 22, base - 36, cx - 28 + i * 22, base], fill=(206, 204, 194))
    d.rectangle([x + 12, base - 26, x + 72, base - 6], fill=(250, 250, 248), outline=(120, 120, 124))
    for i in range(3):
        d.line([(x + 18, base - 21 + i * 5), (x + 64, base - 21 + i * 5)], fill=(150, 150, 154), width=1)


def sc_rubble(d, box):
    sky(d, box, (226, 208, 186), (238, 224, 200))
    x, y, w, h = box
    base = ground(d, box, 0.85, (196, 178, 150))
    for bx, bw, bh in ((x + 10, 44, 54), (x + 62, 36, 40), (x + 106, 48, 62), (x + 164, 38, 46)):
        d.polygon([(bx, base), (bx, base - bh), (bx + bw * 0.4, base - bh * 0.7),
                   (bx + bw * 0.6, base - bh), (bx + bw, base - bh * 0.8), (bx + bw, base)],
                  fill=(120, 112, 104))
    d.ellipse([x + 92, y + 8, x + 146, y + 44], fill=(172, 168, 162))
    d.ellipse([x + 122, y + 20, x + 172, y + 52], fill=(152, 150, 146))
    d.polygon([(x + w - 34, y + 10), (x + w - 20, y + 34), (x + w - 48, y + 34)], fill=(220, 170, 20))
    d.rectangle([x + w - 36, y + 32, x + w - 30, y + 46], fill=(60, 56, 50))


def sc_drone_sudan(d, box):
    sky(d, box, (232, 214, 190), (240, 228, 206))
    x, y, w, h = box
    base = ground(d, box, 0.84, (198, 180, 150))
    building(d, x + 12, base, 38, 50, (150, 140, 126))
    building(d, x + 58, base, 40, 62, (168, 156, 140))
    d.rectangle([x + w - 92, base - 56, x + w - 16, base], fill=(96, 130, 176))
    d.ellipse([x + w - 60, base - 40, x + w - 44, base - 24], outline=(250, 250, 250), width=2)
    d.line([(x + 98, y + 20), (x + 118, y + 24), (x + 138, y + 20)], fill=(44, 44, 48), width=2)
    d.line([(x + 118, y + 24), (x + 118, y + 34)], fill=(44, 44, 48), width=2)
    d.ellipse([x + 150, base - 54, x + 174, base - 30], fill=(180, 180, 184))


def sc_court(d, box):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 222))
    base = ground(d, box, 0.86, (200, 188, 170))
    d.rectangle([x + 18, base - 40, x + 90, base - 6], fill=(150, 120, 84))
    d.rectangle([x + 22, base - 46, x + 86, base - 40], fill=(120, 92, 60))
    d.rectangle([x + 44, base - 58, x + 64, base - 46], fill=(90, 70, 48))
    d.line([(x + 28, base - 62), (x + 82, base - 76)], fill=(90, 70, 48), width=6)
    sx = x + w - 56
    d.line([(sx, base - 74), (sx, base - 16)], fill=(110, 110, 116), width=3)
    d.line([(sx - 30, base - 66), (sx + 30, base - 66)], fill=(110, 110, 116), width=3)
    d.arc([sx - 40, base - 66, sx - 4, base - 42], 0, 180, fill=(110, 110, 116), width=2)
    d.arc([sx + 4, base - 66, sx + 40, base - 42], 0, 180, fill=(110, 110, 116), width=2)


def sc_shield(d, box):
    x, y, w, h = box
    sky(d, box, (226, 232, 240), (240, 240, 244))
    base = ground(d, box, 0.84, (208, 206, 214))
    for bx in (x + 14, x + 62):
        d.rectangle([bx, base - 40, bx + 42, base], fill=(60, 64, 74))
        d.rectangle([bx + 4, base - 36, bx + 38, base - 8], fill=(150, 200, 224))
    sx, sy = x + w - 70, y + 16
    d.polygon([(sx + 28, sy), (sx + 54, sy + 10), (sx + 54, sy + 38), (sx + 28, sy + 54),
               (sx + 2, sy + 38), (sx + 2, sy + 10)], fill=(40, 120, 90))
    d.text((x + 112, y + 6), "$43.9bn", font=F(14, True), fill=(30, 110, 70))


def sc_lashes(d, box):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=(226, 220, 210))
    base = ground(d, box, 0.9, (190, 180, 170))
    for i in range(3):
        d.line([(x + 22 + i * 8, y + 10), (x + 22 + i * 8, y + h - 10)], fill=(120, 118, 120), width=3)
    cx = x + w / 2 + 10
    d.ellipse([cx - 10, base - 72, cx + 10, base - 52], fill=(214, 176, 134))
    d.rectangle([cx - 13, base - 52, cx + 13, base - 18], fill=(150, 60, 70))
    d.line([(cx - 13, base - 18), (cx - 19, base)], fill=(90, 90, 96), width=4)
    d.line([(cx + 13, base - 18), (cx + 19, base)], fill=(90, 90, 96), width=4)
    d.line([(cx + 40, base - 86), (cx + 20, base - 36)], fill=(120, 90, 60), width=3)


def sc_music(d, box):
    x, y, w, h = box
    sky(d, box, (60, 52, 74), (96, 84, 108))
    d.polygon([(x + 10, y + h - 10), (x + 70, y + 6), (x + 120, y + 6), (x + 180, y + h - 10)], fill=(120, 104, 132))
    base = ground(d, box, 0.88, (50, 44, 62))
    d.polygon([(x + 20, base - 22), (x + 78, base - 22), (x + 70, base - 4), (x + 28, base - 4)], fill=(190, 140, 70))
    d.rectangle([x + 78, base - 26, x + 96, base - 18], fill=(120, 88, 50))
    d.ellipse([x + 92, base - 34, x + 134, base - 18], fill=(150, 104, 58))
    star(d, x + w - 34, y + 26, 13, (250, 208, 80), 5)
    star(d, x + w - 60, y + 44, 7, (250, 208, 80), 5)


def sc_health(d, box):
    x, y, w, h = box
    sky(d, box, (222, 236, 240), (240, 244, 244))
    base = ground(d, box, 0.84, (208, 214, 214))
    building(d, x + 10, base, 56, 58, (200, 208, 212), cols=2, rows=3)
    d.rectangle([x + 32, base - 34, x + 44, base], fill=(150, 200, 210))
    d.rectangle([x + 80, base - 48, x + 140, base - 6], fill=(48, 54, 66))
    d.ellipse([x + 95, base - 40, x + 125, base - 18], fill=(120, 190, 210))
    d.rectangle([x + w - 40, base - 40, x + w - 8, base - 12], fill=(40, 120, 90))
    d.line([(x + w - 30, base - 26), (x + w - 24, base - 20)], fill=(200, 240, 220), width=2)
    d.line([(x + w - 24, base - 20), (x + w - 16, base - 30)], fill=(200, 240, 220), width=2)
    d.rectangle([x + w - 58, y + 10, x + w - 12, y + 36], fill=(230, 120, 120))
    d.text((x + w - 50, y + 15), "AI", font=F(13, True), fill=WHITE)


def sc_energy(d, box):
    x, y, w, h = box
    sky(d, box, (216, 226, 236), (236, 238, 240))
    base = ground(d, box, 0.86, (206, 204, 198))
    # storage tanks
    for bx in (x + 14, x + 60):
        d.ellipse([bx, base - 42, bx + 40, base - 22], fill=(180, 186, 190))
        d.rectangle([bx, base - 32, bx + 40, base], fill=(168, 174, 180))
    # pipe to flame
    d.line([(x + 100, base - 10), (x + 150, base - 10)], fill=(150, 150, 156), width=6)
    # flame
    d.polygon([(x + 168, base - 10), (x + 182, base - 44), (x + 196, base - 10)], fill=(230, 130, 40))
    d.polygon([(x + 176, base - 10), (x + 184, base - 30), (x + 192, base - 10)], fill=(70, 150, 220))
    # thermometer
    tx = x + w - 46
    d.rectangle([tx - 6, y + 16, tx + 6, base - 4], fill=(240, 240, 240), outline=(90, 90, 96))
    d.ellipse([tx - 12, base - 16, tx + 12, base + 8], fill=(200, 50, 50))
    d.rectangle([tx - 3, y + 34, tx + 3, base - 6], fill=(200, 50, 50))
    d.text((x + w / 2 - 34, y + 6), "PRICES UP", font=F(11, True), fill=(176, 40, 40))


SCENES = {
    "market": sc_market, "ship": sc_ship, "gulf": sc_gulf, "football": sc_football,
    "energy": sc_energy,
    "handshake": sc_handshake, "capitol": sc_capitol, "rubble": sc_rubble,
    "dronesudan": sc_drone_sudan, "court": sc_court, "shield": sc_shield,
    "lashes": sc_lashes, "music": sc_music, "health": sc_health,
}


# ---- story data (all events of Monday 23 November 2026) ------------------
BIG = [
    dict(n=1, region="MARKETS", tag="REPORTED", scene="market", loc="NEW YORK",
         h="Nvidia reinstates Jensen Huang as CEO; AI stocks roar back to a record day",
         s="US stocks surge as Trump says he 'made the deal'; Megaspeed blacklisted. The Guardian / AP"),
    dict(n=2, region="EUROPE", tag="REPORTED", scene="ship", loc="LIBYA COAST",
         h="Ukraine's sea drones strike two Russian ships off Libya, Kyiv confirms",
         s="Seven drones sank the Merkury; Libya demands answers. The Guardian / AP"),
    dict(n=3, region="MIDDLE EAST", tag="CLAIM", scene="gulf", loc="HORMUZ",
         h="US-Iran Gulf standoff deepens as sanctions escalate and Tehran vows to hit back",
         s="Washington targets 'shadow banking'; Iran claims strikes on US sites. Al Jazeera"),
]

MED = [
    dict(n=4, region="EUROPE", tag="REPORTED", scene="football", loc="LONDON",
         h="UK confirmed as host of the 2035 Women's World Cup",
         s="Fifa announces the four-nation bid. The Guardian (15:09 UTC)"),
    dict(n=5, region="ASIA", tag="REPORTED", scene="handshake", loc="DELHI",
         h="India pledges $1.6bn to Nepal in a reset of ties",
         s="Modi meets Nepali PM Balendra Shah. BBC (13:39 UTC)"),
    dict(n=6, region="AMERICAS", tag="REPORTED", scene="capitol", loc="WASHINGTON",
         h="California Democrat to resign over sexual-misconduct evidence",
         s="Lawmakers call for answers. BBC (21:29 UTC)"),
    dict(n=7, region="MIDDLE EAST", tag="CLAIM", scene="rubble", loc="GAZA",
         h="Israeli attacks have turned Gaza into a 'toxic wasteland', Oxfam says",
         s="Rights group's assessment of the destruction. BBC / The Guardian"),
    dict(n=8, region="AFRICA", tag="REPORTED", scene="dronesudan", loc="KHARTOUM",
         h="Sudan: drone strikes hit homes and a UN building in Khartoum",
         s="Khartoum residential areas hit. DW / France 24"),
    dict(n=9, region="EUROPE", tag="REPORTED", scene="court", loc="PARIS",
         h="Gisele Pelicot 'deeply shocked' as nude photos promote a book; she will sue",
         s="Publisher and author face legal action. The Guardian (18:12 UTC)"),
    dict(n=10, region="AMERICAS", tag="REPORTED", scene="shield", loc="NEW YORK",
         h="CrowdStrike to buy Zscaler in a $43.9bn cybersecurity mega-deal",
         s="Deal announced as the market rallied. The Guardian / AP"),
    dict(n=11, region="MIDDLE EAST", tag="REPORTED", scene="lashes", loc="TEHRAN",
         h="Iran flogs singer Parastoo Ahmadi for performing without a headscarf",
         s="Lawyers confirm the punishment. Al Jazeera / BBC"),
    dict(n=12, region="OCEANIA", tag="REPORTED", scene="music", loc="MELBOURNE",
         h="Molly Meldrum, Australian music legend, dies aged 83",
         s="Tributes and state-funeral talk. BBC / The Guardian"),
    dict(n=13, region="EUROPE", tag="REPORTED", scene="energy", loc="EUROPE",
         h="Gas prices surge as a cold snap feeds supply fears",
         s="Forecast cold snap lifts energy prices. The Guardian"),
]

LIST = [
    ("US blacklists AI-chip firm Megaspeed after Nvidia scandal", "ASIA", "BBC"),
    ("Israel's southern Syria incursion triggers fear", "MIDDLE EAST", "Al Jazeera"),
    ("Eisenkot invites Netanyahu party to coalition talks", "MIDDLE EAST", "France 24"),
    ("Germany: metalworkers strike over pay", "EUROPE", "DW"),
    ("Turkey: mass protest over media crackdown", "EUROPE", "DW / France 24"),
    ("US states sue SpaceX over Grok AI abuse content", "AMERICAS", "Al Jazeera"),
    ("Trump blocks Army's Iowa explosives detonation", "AMERICAS", "BBC"),
    ("Andrew received GBP750,000 from Turkish businessman", "EUROPE", "BBC"),
    ("Don Toliver postpones shows after Manchester scare", "EUROPE", "BBC / AP"),
    ("Finland summons Russian envoy over airspace breach", "EUROPE", "France 24"),
    ("Leaked data: 1,000+ Russian military suicides", "EUROPE", "The Guardian"),
    ("UN chief seeks global AI-safety framework", "WORLD", "France 24"),
    ("FBI probes hack of its crime database", "AMERICAS", "AP / France 24"),
    ("Zimbabwe preacher arrested on sex-assault claims", "AFRICA", "BBC"),
    ("Bangladesh garment workers reject pay offer", "ASIA", "Al Jazeera"),
    ("Colombia drone attack on police base injures civilians", "AMERICAS", "Al Jazeera"),
    ("Trump deported a US citizen to Mexico, DoJ admits", "AMERICAS", "The Guardian"),
    ("NHS launches biggest AI breast-cancer trial", "EUROPE", "BBC"),
    ("Seattle airport: ICE arrests father and daughter", "AMERICAS", "BBC / AP"),
    ("WHO chief: peace plea as DR Congo Ebola fighting surges", "AFRICA", "Al Jazeera"),
]

COUNTS = [("ASIA", 3), ("EUROPE", 11), ("AMERICAS", 8), ("MIDDLE EAST", 5),
          ("AFRICA", 3), ("OCEANIA", 1), ("WORLD", 1), ("MARKETS", 1)]

STATS = [
    "NVIDIA +31.48%", "NASDAQ +6.1%", "DOW +1,324", "S&P 500 +4.4%", "ZSCALER DEAL $43.9bn",
]

MARKETS = [
    ("NVIDIA", "+31.48% to $165.05; +$952bn (a US record)", "The Guardian"),
    ("NASDAQ", "+6.1% close as AI stocks roar back", "CNBC"),
    ("DOW", "+2.8% (+1,324 pts) on the day", "CNBC"),
    ("S&P 500", "+4.4% close after the rebound", "CNBC"),
    ("DEALS", "CrowdStrike to buy Zscaler for $43.9bn", "CNBC / The Guardian"),
]

TIMELINE = [
    ("11:42", "Ukraine confirms sea-drone strike off Libya"),
    ("13:39", "India pledges $1.6bn to Nepal"),
    ("15:09", "Fifa confirms UK as 2035 World Cup host"),
    ("16:49", "Nvidia reinstates Jensen Huang as CEO"),
    ("18:04", "Iran flogs singer Parastoo Ahmadi"),
    ("22:15", "US to blacklist chip firm Megaspeed"),
]

EXCL = [
    "COP31 climate summit collapses without a deal - 22 Nov",
    "Democrats win largest House majority since 1992 - 22 Nov",
    "Russian warship sinks at Benghazi after drone attack - 22 Nov",
    "Miley Cyrus marries Maxx Morando in California - 22 Nov",
    "Carlos Alcaraz wins his first ATP Finals title - 22 Nov",
    "Liverpool beat Manchester United in Pochettino's first game - 22 Nov",
    "Paolo Bulgari, Italian jeweller, dies aged 89 - 22 Nov",
    "BepiColombo enters orbit around Mercury - 22 Nov",
]

PINS = [
    (1, -74.0, 40.7), (2, 20.0, 32.1), (3, 56.5, 26.5), (4, -0.1, 51.5),
    (5, 80.0, 28.0), (6, -121.5, 38.5), (7, 34.4, 31.4), (8, 32.5, 15.6),
    (9, 2.3, 48.9), (10, -74.0, 40.7), (11, 51.4, 35.7), (12, 145.0, -37.8),
    (13, 13.4, 52.5),
]


def frame(d, x, y, w, h, col=RULE, width=2, fill=None):
    if fill is not None:
        d.rectangle([x, y, x + w, y + h], fill=fill)
    d.rectangle([x, y, x + w, y + h], outline=col, width=width)


def region_chip(d, x, y, region):
    return chip(d, x, y, region, REGION.get(region, GREY), size=9, pad=4)


def tag_chip(d, x, y, tag):
    return chip(d, x, y, tag, TAG.get(tag, GREY), size=9, pad=4)


# ---- sections ------------------------------------------------------------
def masthead(d):
    d.rectangle([0, 0, W, 92], fill=WHITE)
    d.line([(0, 92), (W, 92)], fill=RULE, width=3)
    d.text((W / 2, 10), "THE WORLD POST  \u00b7  THE DAY IN ONE IMAGE",
           font=F(15, True), fill=GREY, anchor="ma")
    f = fit(d, "MONDAY 23 NOVEMBER 2026", 56, W - 30, bold=True)
    d.text((W / 2, 28), "MONDAY 23 NOVEMBER 2026", font=f, fill=INK, anchor="ma")


def numbers_strip(d):
    y = 96
    d.rectangle([6, y, W - 6, y + 50], fill=(238, 234, 224), outline=LGREY, width=1)
    f0 = F(12, True)
    d.text((14, y + 5), "33 STORIES OF THE DAY", font=f0, fill=INK)
    x = 14 + tw(d, "33 STORIES OF THE DAY", f0) + 12
    for i, (name, c) in enumerate(COUNTS):
        if i:
            d.text((x, y + 7), "\u00b7", font=F(11, True), fill=GREY)
            x += 10
        s = "%s %d" % (name.title(), c)
        f = F(11, True)
        d.text((x, y + 6), s, font=f, fill=REGION.get(name, GREY))
        x += tw(d, s, f) + 8
    # stats line
    sx = 14
    for s in STATS:
        f = F(10, True)
        d.text((sx, y + 30), s, font=f, fill=(150, 40, 40))
        sx += tw(d, s, f) + 20


def loc_chip(d, x, y, w, text):
    f = F(10, True)
    wd = tw(d, text, f) + 14
    d.rectangle([x + w - wd, y, x + w, y + 15], fill=(24, 30, 44))
    d.text((x + w - wd / 2, y + 2), text, font=f, fill=(240, 240, 240), anchor="ma")


def paste_scene(img, x, y, w, h, name):
    """Draw a scene on a throwaway 100px-tall canvas, scale to h, paste (clips overflow)."""
    tmp = Image.new("RGB", (w, 100), WHITE)
    SCENES[name](ImageDraw.Draw(tmp), (0, 0, w, 100))
    if h != 100:
        tmp = tmp.resize((w, h))
    img.paste(tmp, (x, y))


def big_feature(img, d, x, y, w, h, it):
    frame(d, x, y, w, h, col=REGION.get(it["region"], RULE), width=3, fill=WHITE)
    paste_scene(img, x + 4, y + 4, w - 8, 100, it["scene"])
    d.rectangle([x + 4, y + 4, x + w - 4, y + 104], outline=LGREY, width=1)
    d.ellipse([x + 8, y + 8, x + 40, y + 40], fill=REGION.get(it["region"], RULE))
    d.text((x + 24, y + 24), str(it["n"]), font=F(18, True), fill=WHITE, anchor="mm")
    loc_chip(d, x + 8, y + 8, w - 16, it["loc"])
    hy = para(d, it["h"], (x + 8, y + 108), 18, w - 16, fill=INK, bold=True, lead=1, maxlines=3)
    xc = x + 8
    xc += region_chip(d, xc, hy + 2, it["region"])[0] + 5
    tag_chip(d, xc, hy + 2, it["tag"])
    para(d, it["s"], (x + 8, hy + 20), 11, w - 16, fill=GREY, lead=1, maxlines=2)


def med_feature(img, d, x, y, w, h, it):
    frame(d, x, y, w, h, col=REGION.get(it["region"], RULE), width=2, fill=WHITE)
    paste_scene(img, x + 3, y + 3, w - 6, 70, it["scene"])
    d.rectangle([x + 3, y + 3, x + w - 3, y + 73], outline=LGREY, width=1)
    d.ellipse([x + 6, y + 6, x + 26, y + 26], fill=REGION.get(it["region"], RULE))
    d.text((x + 16, y + 16), str(it["n"]), font=F(12, True), fill=WHITE, anchor="mm")
    loc_chip(d, x + 5, y + 5, w - 10, it["loc"])
    hy = para(d, it["h"], (x + 6, y + 77), 14, w - 12, fill=INK, bold=True, lead=1, maxlines=3)
    xc = x + 6
    xc += region_chip(d, xc, hy, it["region"])[0] + 3
    tag_chip(d, xc, hy, it["tag"])
    para(d, it["s"], (x + 6, hy + 16), 10, w - 12, fill=GREY, lead=1, maxlines=2)


def also_list(d, x, y, w, h):
    frame(d, x, y, w, h, col=RULE, width=2, fill=WHITE)
    d.rectangle([x, y, x + w, y + 21], fill=INK)
    d.text((x + 7, y + 4), "ALSO ON MONDAY 23 NOVEMBER", font=F(13, True), fill=WHITE)
    yy = y + 26
    f = F(10, False)
    fb = F(10, True)
    srcf = F(8, True)
    for i, (t, reg, src) in enumerate(LIST):
        d.rectangle([x + 6, yy + 2, x + 9, yy + 11], fill=REGION.get(reg, GREY))
        d.text((x + 12, yy), "%d." % (i + 14), font=fb, fill=INK)
        avail = w - 40 - tw(d, src, srcf) - 8
        d.text((x + 30, yy), one_line(d, t, f, avail), font=f, fill=INK)
        d.text((x + w - 6, yy + 1), src, font=srcf, fill=GREY, anchor="ra")
        yy += 12


def map_panel(d, x, y, w, h):
    frame(d, x, y, w, h, col=RULE, width=2, fill=WHITE)
    d.rectangle([x, y, x + w, y + 20], fill=INK)
    d.text((x + 7, y + 3), "WHERE IT HAPPENED", font=F(12, True), fill=WHITE)
    mx, my, mw, mh = x + 6, y + 24, w - 12, h - 46
    d.rectangle([mx, my, mx + mw, my + mh], fill=(226, 236, 242))
    for name, poly in worldmap.polys(mx, my, mw, mh):
        d.polygon(poly, fill=(196, 208, 190), outline=(150, 164, 150))
    for n, lo, la in PINS:
        px, py = worldmap.project(lo, la, mx, my, mw, mh)
        col = (176, 54, 54) if n <= 3 else (28, 106, 176)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=col, outline=WHITE, width=1)
        d.text((px, py), str(n), font=F(9, True), fill=WHITE, anchor="mm")
    d.text((x + 7, y + h - 20), "Pins = the 13 illustrated stories.  Red 1-3, blue 4-13.",
           font=F(9, False), fill=GREY)


def markets_box(d, x, y, w, h):
    frame(d, x, y, x + w, y + h, col=RULE, width=2, fill=WHITE)
    d.rectangle([x, y, x + w, y + 20], fill=(176, 54, 54))
    d.text((x + 7, y + 3), "MARKETS & MONEY  \u00b7  23 NOV", font=F(12, True), fill=WHITE)
    yy = y + 24
    for k, v, src in MARKETS:
        d.text((x + 6, yy), k, font=F(10, True), fill=(150, 40, 40))
        lines = wrap(d, v, F(10, False), w - 78)
        d.text((x + 70, yy), lines[0], font=F(10, False), fill=INK)
        yy += 20


def timeline_box(d, x, y, w, h):
    frame(d, x, y, w, h, col=RULE, width=2, fill=WHITE)
    d.rectangle([x, y, x + w, y + 20], fill=INK)
    d.text((x + 7, y + 3), "THE DAY BY HOURS (UTC)", font=F(12, True), fill=WHITE)
    yy = y + 24
    for t, ev in TIMELINE:
        d.text((x + 6, yy), t, font=F(10, True), fill=(150, 40, 40))
        d.text((x + 46, yy), one_line(d, ev, F(10, False), w - 54), font=F(10, False), fill=INK)
        yy += 15


def datecheck_box(d, x, y, w, h):
    frame(d, x, y, w, h, col=(162, 44, 44), width=2, fill=(250, 244, 240))
    d.rectangle([x, y, x + w, y + 20], fill=(162, 44, 44))
    d.text((x + 7, y + 3), "DATE CHECK \u2014 LEFT OUT AS OTHER DAYS' NEWS", font=F(10, True), fill=WHITE)
    yy = y + 22
    yy = para(d, "Every story here happened (or was first reported) on 23 Nov 2026.",
              (x + 6, yy), 9, w - 12, fill=INK, maxlines=1)
    for e in EXCL:
        d.text((x + 8, yy), "\u00b7 " + one_line(d, e, F(8, False), w - 16), font=F(8, False), fill=(96, 62, 62))
        yy += 11


def howsure(d, x, y, w, h):
    frame(d, x, y, w, h, col=RULE, width=1, fill=(238, 234, 224))
    d.text((x + 8, y + 3), "HOW SURE ARE WE?  33 stories, each checked against a primary outlet "
           "for its EVENT date (23 Nov 2026); 8 other-day stories left out (see DATE CHECK).",
           font=F(10, True), fill=INK)


def footer(d):
    d.text((W / 2, 1004), "SOURCES: BBC News \u00b7 The Guardian \u00b7 Al Jazeera \u00b7 AP \u00b7 DW \u00b7 France 24  "
           "\u00b7  Compiled from primary outlets, 23 November 2026",
           font=F(10, False), fill=GREY, anchor="ma")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    masthead(d)
    numbers_strip(d)

    by, bh, bw, gap = 152, 214, 330, 8
    for i, it in enumerate(BIG):
        big_feature(img, d, 8 + i * (bw + gap), by, bw, bh, it)

    mx0, mw, mgap, mh = 8, 197, 6, 166
    my0 = by + bh + 6
    for i, it in enumerate(MED):
        med_feature(img, d, mx0 + (i % 5) * (mw + mgap), my0 + (i // 5) * (mh + 5), mw, mh, it)

    by2 = my0 + 2 * (mh + 5) + 4            # ~716
    bot = 986
    also_list(d, 8, by2, 344, bot - by2)
    map_panel(d, 358, by2, 312, 150)
    markets_box(d, 358, by2 + 156, 312, bot - (by2 + 156))
    timeline_box(d, 676, by2, 340, 126)
    datecheck_box(d, 676, by2 + 132, 340, bot - (by2 + 132))
    howsure(d, 8, bot + 2, W - 16, 14)
    footer(d)

    img.save("entry.png", "PNG", optimize=True)
    print("wrote entry.png", img.size, "bottom y=", by2)


if __name__ == "__main__":
    main()
