#!/usr/bin/env python3
"""Generate snake SVG from GitHub contribution data."""
import urllib.request
import json
import os
import sys
from datetime import datetime, timedelta

USER = "qtonnnn"
COLS = 53  # weeks to show
CELL = 11
PAD = 2
H = CELL * 7 + PAD * 8
W = CELL * COLS + PAD * (COLS + 1) + 100  # extra for labels
GRID_Y0 = 50

LEVELS = [
    ("#161b22", 0),  # 0 contributions
    ("#3a1a4a", 1),
    ("#6c3483", 2),
    ("#8e44ad", 3),
    ("#9b59b6", 4),  # highest
]

def fetch():
    url = f"https://github-contributions-api.jogruber.de/v4/{USER}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"API 1 fail: {e}", file=sys.stderr)
    url = f"https://api.github.com/users/{USER}/events/public"
    return None

def main():
    print("Fetching contribution data...", file=sys.stderr)
    data = fetch()
    if not data:
        print("Using empty grid (API unavailable)", file=sys.stderr)
        contributions = [[0]*7 for _ in range(COLS)]
    else:
        contribs_list = data.get("contributions", [])
        # Map date -> count
        cnt = {c["date"]: c["count"] for c in contribs_list}
        # Take last COLS*7 days
        end = datetime.utcnow().date()
        start = end - timedelta(days=COLS*7 - 1)
        # align start to a Sunday
        start = start - timedelta(days=(start.weekday() + 1) % 7)
        contributions = [[0]*7 for _ in range(COLS)]
        d = start
        for w in range(COLS):
            for dow in range(7):
                if d > end:
                    contributions[w][dow] = 0
                else:
                    contributions[w][dow] = cnt.get(d.isoformat(), 0)
                d += timedelta(days=1)
                if d > end + timedelta(days=7):
                    break
            if d > end + timedelta(days=7):
                break

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {GRID_Y0 + H + 30}" width="{W}" height="{GRID_Y0 + H + 30}">']
    svg.append('<style>.lbl{font:9px system-ui;fill:#8b949e}.mn{font:bold 11px system-ui;fill:#9b59b6}</style>')
    svg.append(f'<rect width="{W}" height="{GRID_Y0 + H + 30}" fill="#0d1117"/>')
    svg.append('<text x="20" y="30" class="mn">🐍 qtonnnn — contribution graph</text>')
    # day labels
    days = ["Mon", "Wed", "Fri"]
    for i, d in enumerate(days):
        y = GRID_Y0 + PAD + i * (CELL + PAD) * 2 + 4
        svg.append(f'<text x="20" y="{y}" class="lbl">{d}</text>')
    # cells
    for w in range(COLS):
        for dow in range(7):
            x = 60 + w * (CELL + PAD)
            y = GRID_Y0 + PAD + dow * (CELL + PAD)
            level = contributions[w][dow]
            color = LEVELS[min(4, level)][0]
            svg.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    svg.append('</svg>')
    out_dark = sys.argv[1] if len(sys.argv) > 1 else "github-contribution-grid-snake-dark.svg"
    out_light = sys.argv[2] if len(sys.argv) > 2 else "github-contribution-grid-snake.svg"
    with open(out_dark, "w") as f:
        f.write("\n".join(svg))
    # light version: same colors but lighter background
    svg_light = "\n".join(svg).replace('fill="#0d1117"', 'fill="#ffffff"')
    with open(out_light, "w") as f:
        f.write(svg_light)
    print(f"Wrote {out_dark} and {out_light}", file=sys.stderr)

if __name__ == "__main__":
    main()
