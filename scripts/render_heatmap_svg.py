# scripts/render_heatmap_svg.py
import json

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3
LEGEND_H = 20
FOOTER_H = 24
LEFT_PAD = 30
TOP_PAD = 20

def load():
    with open("data/contributions.json", encoding="utf-8") as f:
        return json.load(f)

def build_svg(data):
    days = data["days"]
    stats = data["stats"]

    # bucket days into weeks (columns), Sun-Sat rows — assume days sorted ascending
    weeks = []
    week = []
    for d in days:
        week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)

    cols = len(weeks)
    width = LEFT_PAD + cols * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + LEGEND_H + FOOTER_H

    out = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#0d1117">']
    out.append(f'''<style>
      .cell {{ opacity: 0; animation: reveal 0.3s ease forwards; }}
      @keyframes reveal {{ to {{ opacity: 1; }} }}
    </style>''')

    for wi, week in enumerate(weeks):
        for di, d in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            level = min(d["level"], len(PALETTE) - 1)
            color = PALETTE[level]
            delay = (wi + di) * 0.012  # diagonal stagger
            out.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{d["date"]}: {d["count"]} contributions</title>'
                f'</rect>'
            )

    # legend
    ly = TOP_PAD + 7 * (CELL + GAP) + 4
    out.append(f'<text x="{LEFT_PAD}" y="{ly+10}" font-family="monospace" font-size="10" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 35
    for i, color in enumerate(PALETTE):
        out.append(f'<rect x="{lx + i*(CELL+GAP)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    out.append(f'<text x="{lx + len(PALETTE)*(CELL+GAP) + 5}" y="{ly+10}" font-family="monospace" font-size="10" fill="#8b949e">More</text>')

    # footer stats
    fy = ly + LEGEND_H + 8
    footer = f'{stats["total"]:,} contributions in the last year - streak {stats["current_streak"]}d - longest {stats["longest_streak"]}d'
    out.append(f'<text x="{LEFT_PAD}" y="{fy}" font-family="monospace" font-size="11" fill="#c9d1d9">{footer}</text>')

    out.append("</svg>")
    return "\n".join(out)

if __name__ == "__main__":
    data = load()
    svg = build_svg(data)
    with open("contrib-heatmap.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote contrib-heatmap.svg")
