"""Pre-rendered per-day Strip maps from real map tiles.

Reads the exported week (held sessions with venues) plus geocoded venue
coordinates, fetches one shared CARTO dark_matter tile mosaic, crops a
per-day view, and draws venue pins plus the session list onto a single
PNG per day. Static files: no JavaScript, no runtime tile fetching.

`python3 -m reinvent26.daymaps reinvent2026 --week week.json
--venues-json editorial.json --out-dir static/reinvent26`

Network only touches tile servers (polite: one subdomain, small sleeps).
Tests use synthetic tiles and never touch the network.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.request

TILE_SIZE = 256
ZOOM = 15
USER_AGENT = "reinvent26-daymaps/1.0 (contact via bryanchasko.com)"
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
REQUEST_PAUSE_SECONDS = 0.5
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
AMBER = (245, 197, 66)
GREY = (148, 163, 184)
PANEL = (23, 23, 31)
OFFWHITE = (242, 237, 228)

DAY_LABELS = {
    "2026-11-30": "MON NOV 30",
    "2026-12-01": "TUE DEC 1",
    "2026-12-02": "WED DEC 2",
    "2026-12-03": "THU DEC 3",
    "2026-12-04": "FRI DEC 4",
}


def latlng_to_tile(latitude: float, longitude: float, zoom: int) -> tuple:
    """Slippy-map tile indices for a coordinate."""
    count = 2 ** zoom
    x_tile = int((longitude + 180.0) / 360.0 * count)
    lat_rad = math.radians(latitude)
    y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * count)
    return x_tile, y_tile


def latlng_to_pixel(latitude: float, longitude: float, zoom: int,
                    origin_x: int, origin_y: int) -> tuple:
    """Pixel position inside a mosaic whose top-left tile is origin."""
    from PIL import Image as _Image  # noqa: F401  (keeps import local to use)
    count = 2 ** zoom
    global_x = (longitude + 180.0) / 360.0 * count * TILE_SIZE
    lat_rad = math.radians(latitude)
    global_y = ((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0
                * count * TILE_SIZE)
    return (int(global_x - origin_x * TILE_SIZE),
            int(global_y - origin_y * TILE_SIZE))


def fetch_tile(z: int, x: int, y: int, cache_dir: str):
    """One map tile, cached on disk. Only function that touches network."""
    from PIL import Image
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{z}-{x}-{y}.png")
    if not os.path.exists(path):
        req = urllib.request.Request(
            TILE_URL.format(z=z, x=x, y=y),
            headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(path, "wb") as handle:
                handle.write(resp.read())
        time.sleep(REQUEST_PAUSE_SECONDS)
    return Image.open(path).convert("RGB")


def build_mosaic(venues: list, cache_dir: str):
    """Fetch the smallest tile grid covering every venue (plus margin)."""
    from PIL import Image
    corners = [latlng_to_tile(v["lat"], v["lng"], ZOOM) for v in venues]
    min_x = min(c[0] for c in corners) - 1
    max_x = max(c[0] for c in corners) + 1
    min_y = min(c[1] for c in corners) - 1
    max_y = max(c[1] for c in corners) + 1
    mosaic = Image.new("RGB",
                       ((max_x - min_x + 1) * TILE_SIZE,
                        (max_y - min_y + 1) * TILE_SIZE))
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            tile = fetch_tile(ZOOM, x, y, cache_dir)
            mosaic.paste(tile, ((x - min_x) * TILE_SIZE,
                                (y - min_y) * TILE_SIZE))
    return mosaic, min_x, min_y


def draw_day(date: str, day_held: list, venues: list,
             mosaic, origin: tuple):
    """Composite: map crop left, session list right, attribution bottom."""
    from PIL import Image, ImageDraw, ImageFont
    title_font = ImageFont.truetype(FONT_PATH, 22)
    row_font = ImageFont.truetype(FONT_PATH, 16)
    small_font = ImageFont.truetype(FONT_PATH, 13)
    active = {h["venue"] for h in day_held}
    points = {}
    for venue in venues:
        points[venue["name"]] = latlng_to_pixel(
            venue["lat"], venue["lng"], ZOOM, *origin)
    xs = [points[v][0] for v in active if v in points]
    ys = [points[v][1] for v in active if v in points]
    pad = 90
    left = max(0, min(xs) - pad)
    top = max(0, min(ys) - pad)
    right = min(mosaic.width, max(xs) + pad)
    bottom = min(mosaic.height, max(ys) + pad)
    center_x, center_y = (left + right) // 2, (top + bottom) // 2
    half = 260
    left = max(0, center_x - half)
    top = max(0, center_y - half)
    right = min(mosaic.width, left + half * 2)
    bottom = min(mosaic.height, top + half * 2)
    crop = mosaic.crop((left, top, right, bottom))
    panel_width = 330
    list_bottom = 60 + len(day_held) * 52 + 30
    canvas_height = max(crop.height + 26, list_bottom)
    canvas = Image.new("RGB", (crop.width + panel_width, canvas_height),
                       PANEL)
    canvas.paste(crop, (0, 26))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 2), DAY_LABELS.get(date, date), font=title_font,
              fill=AMBER)
    for venue_name, (px, py) in points.items():
        if not (left <= px <= right and top <= py <= bottom):
            continue
        dot_x, dot_y = px - left, py - top + 26
        color = AMBER if venue_name in active else GREY
        draw.ellipse([dot_x - 7, dot_y - 7, dot_x + 7, dot_y + 7],
                     fill=color, outline=(10, 10, 14), width=2)
        if venue_name == "Venetian":
            draw.ellipse([dot_x - 11, dot_y - 11, dot_x + 11, dot_y + 11],
                         outline=AMBER, width=2)
    row_y = 60
    for item in sorted(day_held, key=lambda h: h["start"]):
        draw.text((crop.width + 14, row_y),
                  f"{item['start']} {item['code']}", font=row_font,
                  fill=OFFWHITE)
        draw.text((crop.width + 14, row_y + 22), item["venue"],
                  font=small_font, fill=GREY)
        row_y += 52
    draw.text((12, canvas.height - 20),
              "(c) OpenStreetMap contributors",
              font=small_font, fill=GREY)
    return canvas


def run(week_path: str, editorial_path: str, out_dir: str,
        cache_dir: str) -> int:
    week = json.load(open(week_path, encoding="utf-8"))
    editorial = json.load(open(editorial_path, encoding="utf-8"))
    venues = editorial["map_venues"]
    os.makedirs(out_dir, exist_ok=True)
    mosaic, origin_x, origin_y = build_mosaic(venues, cache_dir)
    dates = sorted({h.get("date", "") for h in week["held"] if h.get("date")})
    for date in dates:
        day_held = [h for h in week["held"] if h.get("date") == date]
        image = draw_day(date, day_held, venues, mosaic, (origin_x, origin_y))
        out_path = os.path.join(out_dir, f"day-{date}.png")
        image.save(out_path)
        print(f"# wrote {out_path} ({image.width}x{image.height})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="reinvent26 daymaps",
                                     description="render per-day Strip maps")
    parser.add_argument("event_id")
    parser.add_argument("--week", required=True)
    parser.add_argument("--venues-json", required=True,
                        help="editorial.json holding map_venues")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--cache-dir", default="/tmp/re26tiles")
    args = parser.parse_args(argv)
    return run(args.week, args.venues_json, args.out_dir, args.cache_dir)


if __name__ == "__main__":
    raise SystemExit(main())
