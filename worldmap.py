#!/usr/bin/env python3
"""worldmap.py - very simplified continent outlines for the "WHERE IT HAPPENED" panel.

Each continent is a coarse (lon, lat) polygon. They are intentionally imprecise:
the panel is a stylised locator, not a survey map. No external data, no network.
"""

# Coarse outlines, lon/lat degrees. Good enough to be recognisable at ~300 px wide.
CONTINENTS = {
    "N-America": [
        (-168, 65), (-150, 70), (-125, 72), (-100, 73), (-80, 70), (-60, 60), (-52, 50),
        (-65, 45), (-70, 42), (-75, 35), (-81, 25), (-97, 18), (-105, 20), (-115, 30),
        (-125, 40), (-125, 49), (-135, 58), (-150, 60),
    ],
    "S-America": [
        (-80, 10), (-60, 12), (-50, 0), (-35, -6), (-38, -22), (-48, -25), (-58, -38),
        (-66, -55), (-73, -52), (-73, -40), (-71, -18), (-80, -5),
    ],
    "Europe": [
        (-10, 36), (-10, 44), (-2, 48), (-5, 58), (5, 60), (12, 64), (22, 70), (32, 70),
        (40, 66), (40, 55), (30, 45), (26, 41), (16, 40), (9, 37), (0, 36),
    ],
    "Africa": [
        (-17, 15), (-10, 5), (9, 4), (10, -1), (12, -7), (14, -22), (18, -35), (28, -34),
        (35, -25), (41, -15), (51, 12), (43, 12), (33, 22), (32, 31), (10, 37), (0, 36),
        (-10, 30), (-17, 21),
    ],
    "Asia": [
        (40, 66), (60, 70), (78, 74), (100, 76), (120, 73), (140, 72), (162, 70), (180, 66),
        (180, 50), (160, 45), (145, 35), (140, 30), (122, 30), (120, 22), (108, 20),
        (105, 10), (100, 5), (95, 10), (90, 22), (80, 10), (72, 22), (62, 25), (55, 25),
        (50, 30), (45, 40), (40, 45),
    ],
    "Oceania": [
        (113, -22), (115, -34), (130, -32), (145, -38), (153, -28), (147, -18), (135, -12),
        (125, -14),
    ],
}

# Small islands/regions drawn as filled blobs so recognisable spots are not empty water.
ISLANDS = {
    "UK": [(3.5, -6), (1.5, 51), (-5, 55), (-5, 58), (0, 57), (0, 53)],
    "Japan": [(140, 45), (136, 36), (131, 31), (129, 33), (135, 40), (139, 42)],
}


def project(lon, lat, x0, y0, w, h):
    """Equirectangular projection of lon/lat into the pixel box (x0,y0,w,h)."""
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (90.0 - lat) / 180.0 * h
    return (x, y)


def polys(x0, y0, w, h):
    """Return [(name, [(px,py), ...]), ...] for all continents + islands."""
    out = []
    for name, pts in CONTINENTS.items():
        out.append((name, [project(lo, la, x0, y0, w, h) for lo, la in pts]))
    for name, pts in ISLANDS.items():
        out.append((name, [project(lo, la, x0, y0, w, h) for lo, la in pts]))
    return out


if __name__ == "__main__":
    # tiny self-check: every vertex lands inside the box
    for name, pts in polys(0, 0, 360, 180):
        for x, y in pts:
            assert 0 <= x <= 360 and 0 <= y <= 180, (name, x, y)
    print("worldmap ok:", len(CONTINENTS), "continents,", len(ISLANDS), "islands")
