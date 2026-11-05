"""Export the live week as JSON for the bryanchasko.com/reinvent26 page.

`python3 -m reinvent26.export_week reinvent2026 --out <path>/week.json`

Reads the live schedule and the cached catalog (run `sessions` first),
computes held seats, favorites, and find-me windows, and attaches the
latest nightly watcher report. Read-only: never reserves or writes
personal time. The site template renders this file; regenerate it to
refresh the page.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

from reinvent26 import api, auth, cache, cli, findme, mapper

EVENT_ID = "reinvent2026"
CODE_RE = re.compile(r"\b([A-Z]{2,4}\d{3,4}(?:-R\d?|-S)?)\b")


def session_entry(item: dict) -> dict:
    """Catalog session narrowed to the fields the week page renders."""
    speakers = item.get("speakers") or []
    start = str(item.get("startTime") or "")
    return {
        "code": item.get("abbreviation") or item.get("code") or item.get("sessionId"),
        "title": item.get("title") or "",
        "date": start[:10],
        "start": start[11:16],
        "end": str(item.get("endTime") or "")[11:16],
        "venue": item.get("venue") or "",
        "room": item.get("room") or "",
        "speakers": [s.get("name", "") for s in speakers if isinstance(s, dict)],
        "level": item.get("level") or "",
        "seat": item.get("seatAvailability") or item.get("seat_availability") or "",
    }


def watcher_latest(watcher_dir: str) -> dict:
    """New-session codes from the latest nightly watcher report, if any."""
    try:
        names = sorted(f for f in os.listdir(watcher_dir)
                       if f.startswith("new-sessions-") and f.endswith(".md"))
    except OSError:
        return {"report": None, "added": [], "opportunities": []}
    if not names:
        return {"report": None, "added": [], "opportunities": []}
    report = names[-1]
    text = open(os.path.join(watcher_dir, report), encoding="utf-8").read()
    added_section = re.split(r"## all added sessions",
                             text, maxsplit=1)
    added_text = added_section[1] if len(added_section) > 1 else ""
    opp_section = re.split(r"## opportunities.*?\n", text, maxsplit=1)
    opp_text = opp_section[1].split("##", 1)[0] if len(opp_section) > 1 else ""
    return {
        "report": report.replace("new-sessions-", "").replace(".md", ""),
        "added": sorted(set(CODE_RE.findall(added_text)) - {"none"}),
        "opportunities": sorted(set(CODE_RE.findall(opp_text)) - {"none"}),
    }


def build_week(schedule: dict, catalog: list, watcher_dir: str,
               generated_at: str) -> dict:
    """Pure build: schedule plus catalog rows in, week dict out."""
    by_id = {s.get("sessionId"): s for s in catalog if isinstance(s, dict)}
    items = cli._confirmed_items(schedule, catalog)
    for item in items:
        full = by_id.get(item.get("sessionId"), {})
        for key, value in full.items():
            if key not in item or not item.get(key):
                item[key] = value
    node = schedule.get("schedule", {}) if isinstance(schedule, dict) else {}
    reserved_ids = set(
        r if isinstance(r, str) else r.get("sessionId")
        for r in node.get("reserved", [])
    )
    held = [s for s in items
            if s.get("sessionId") in reserved_ids or s.get("code") in reserved_ids]
    favorites = [s for s in items
                 if s.get("sessionId") not in reserved_ids
                 and s.get("code") not in reserved_ids
                 and (s.get("startTime") or s.get("sessionTime"))]
    windows = [
        {"date": str(day), "start": start.strftime("%H:%M"),
         "end": end.strftime("%H:%M"), "minutes": minutes, "part": part}
        for day, start, end, minutes, part in findme.day_gaps(held)
    ]
    held_entries = [session_entry(s) for s in held if s.get("startTime")]
    favorites_entries = [session_entry(s) for s in favorites if s.get("startTime")]
    timeline = ([dict(entry, kind="held") for entry in held_entries]
                + [dict(window, kind="open") for window in windows])
    timeline.sort(key=lambda e: (e.get("date", ""), e.get("start", "")))
    config = mapper._load_config()
    legs = []
    by_day: dict = {}
    for entry in held_entries:
        by_day.setdefault(entry["date"], []).append(entry)
    for date, day_held in by_day.items():
        ordered = sorted(day_held, key=lambda e: e["start"])
        for first, second in zip(ordered, ordered[1:]):
            minutes = mapper._gap_needed(
                {"venue": first["venue"]}, {"venue": second["venue"]}, config)
            if first["venue"] == second["venue"]:
                mode, label = "walk", "in-venue walk, about 10 minutes"
            else:
                mode = "shuttle"
                label = f"shuttle, about {minutes} minutes (estimate)"
            legs.append({"kind": "leg", "date": date,
                         "start": first["end"], "end": first["end"],
                         "ord": 1,
                         "from_venue": first["venue"],
                         "to_venue": second["venue"],
                         "mode": mode, "label": label})
    timeline = timeline + legs
    for entry in timeline:
        entry.setdefault("ord", 0 if entry["kind"] == "held" else 2)
    timeline.sort(key=lambda e: (e.get("date", ""), e.get("start", ""),
                                 e.get("ord", 9)))
    return {
        "generated_at": generated_at,
        "event_id": EVENT_ID,
        "held": held_entries,
        "favorites": favorites_entries,
        "windows": windows,
        "timeline": timeline,
        "watcher": watcher_latest(watcher_dir),
    }


def run(event_id: str, out: str, watcher_dir: str) -> int:
    token = auth.stored_access_token()
    if not token:
        print("error: not signed in", file=sys.stderr)
        return 2
    catalog = cache.load_cached_sessions(event_id)
    if not catalog:
        print("error: no catalog cache", file=sys.stderr)
        return 2
    try:
        schedule = api.get_schedule(event_id, token)
    except api.EventsError as exc:
        print(f"error: schedule read failed: {exc}", file=sys.stderr)
        return 1
    week = build_week(schedule, catalog, watcher_dir,
                      _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d"))
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(week, handle, indent=1)
        handle.write("\n")
    print(f"# wrote {out}: {len(week['held'])} held, "
          f"{len(week['favorites'])} favorites", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="reinvent26 export-week",
                                     description="export the live week as page JSON")
    parser.add_argument("event_id", nargs="?", default=EVENT_ID)
    parser.add_argument("--out", required=True, help="output JSON path")
    parser.add_argument("--watcher-dir", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "docs", "new-sessions"),
        help="nightly watcher report directory")
    args = parser.parse_args(argv)
    return run(args.event_id, args.out, args.watcher_dir)


if __name__ == "__main__":
    raise SystemExit(main())
