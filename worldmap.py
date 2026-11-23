"""worldmap.py — very simplified continent outlines for the "WHERE IT HAPPENED" map.

Coarse (lon, lat) polygons, enough to be recognisable at thumbnail size. Drawn with
Pillow only; no external data, no network. Projection is plain equirectangular.
"""

CONTINENTS = {
    "north_america": [
        (-168, 65), (-150, 70), (-125, 70), (-100, 72), (-80, 73), (-60, 60),
        (-55, 50), (-65, 45), (-70, 42), (-75, 35), (-81, 25), (-97, 26),
        (-105, 20), (-115, 30), (-125, 40), (-130, 55), (-140, 60), (-168, 65),
    ],
    "south_america": [
        (-81, 8), (-60, 10), (-50, 0), (-35, -5), (-38, -15), (-48, -25),
        (-58, -35), (-65, -45), (-70, -55), (-75, -50), (-72, -35), (-70, -20),
        (-75, -10), (-78, 0), (-81, 8),
    ],
    "africa": [
        (-17, 15), (-5, 5), (9, 4), (10, -1), (13, -5), (12, -17), (15, -28),
        (20, -35), (32, -28), (40, -15), (41, -2), (51, 11), (43, 12), (33, 15),
        (32, 31), (10, 37), (0, 36), (-10, 30), (-17, 21), (-17, 15),
    ],
    "europe": [
        (-10, 36), (-9, 44), (-5, 48), (2, 51), (5, 54), (10, 58), (20, 60),
        (30, 60), (40, 55), (40, 48), (28, 41), (20, 40), (15, 38), (12, 45),
        (3, 43), (-5, 36), (-10, 36),
    ],
    "asia": [
        (30, 60), (60, 70), (100, 75), (140, 72), (170, 68), (160, 60),
        (140, 50), (130, 42), (122, 30), (110, 20), (100, 13), (95, 5),
        (80, 8), (70, 25), (60, 25), (48, 30), (35, 36), (28, 41), (40, 48),
        (40, 55), (30, 60),
    ],
    "oceania": [
        (113, -22), (114, -34), (129, -32), (141, -38), (150, -37), (153, -28),
        (146, -19), (135, -14), (128, -15), (122, -17), (113, -22),
    ],
}


def project(lon, lat, box):
    """Equirectangular projection into box = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (90.0 - lat) / 180.0 * (y1 - y0)
    return (x, y)


def draw_map(draw, box, land_fill, outline, grid=None):
    """Draw the continent polygons inside box."""
    for poly in CONTINENTS.values():
        pts = [project(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=land_fill, outline=outline)
    if grid:
        x0, y0, x1, y1 = box
        for lon in (-120, -60, 0, 60, 120):
            x = project(lon, 0, box)[0]
            draw.line([(x, y0), (x, y1)], fill=grid, width=1)
        for lat in (-30, 0, 30, 60):
            y = project(0, lat, box)[1]
            draw.line([(x0, y), (x1, y)], fill=grid, width=1)
