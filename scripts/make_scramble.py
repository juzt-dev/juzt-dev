#!/usr/bin/env python3
"""Generate assets/scramble.svg - a looping text-scramble ("decoder") banner.

Pure SVG + SMIL, no JS, so it animates inside a GitHub README <img>.
Each glyph cell flickers through random characters before locking onto
its final letter, then scrambles back out at the end of the cycle.

    python3 scripts/make_scramble.py
"""
import random
from pathlib import Path

random.seed(7)

W, H = 840, 230
CYCLE = 13.0                     # seconds per loop
STEP = 0.055                     # how long each random glyph is shown
SCRAMBLE = 5                     # random glyphs before the real one
POOL = "!<>-_/\\[]{}=+*^?#$%&@01XZ░▒▓█"
NOISE = ["#7AA2F7", "#BB9AF7", "#7DCFFF", "#565F89", "#9ECE6A"]
FONT = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace"

# (text, y, font-size, colour, weight, t_in, t_out, char stagger)
LINES = [
    ("$ ./juzt --connect",              46,  14, "#565F89", 400, 0.0, 11.8, 0.025),
    ("LET'S BUILD SOMETHING",           104, 44, "#C0CAF5", 700, 0.5, 11.8, 0.045),
    ("peterhoo.com · ciuslabs.com",     140, 16, "#7AA2F7", 400, 1.3, 11.8, 0.018),
]
ROTATING = (["open to collaborations",
             "ship fast, iterate faster",
             "console.log() is a debugger. fight me."],
            186, 18, "#9ECE6A", 400, 2.2, 3.2, 2.7, 0.022)  # start, slot, hold, stagger


def r(x):
    return f"{x:.3f}".rstrip("0").rstrip(".")


def esc(c):
    return {"<": "&lt;", ">": "&gt;", "&": "&amp;"}.get(c, c)


def visible(start, end):
    """SMIL opacity animation: visible only within [start, end) of the cycle."""
    start, end = max(0.0, start), min(CYCLE, end)
    if end <= start:
        return None
    a, b = start / CYCLE, end / CYCLE
    if a == 0:
        vals, kt = "1;0", f"0;{r(b)}"
    else:
        vals, kt = "0;1;0", f"0;{r(a)};{r(b)}"
    return (f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" '
            f'calcMode="discrete" dur="{CYCLE}s" repeatCount="indefinite"/>')


out = []


def cell(x, y, size, colour, weight, ch, t_in, t_out):
    """One character: scramble in, hold, scramble out."""
    if ch == " ":
        return
    segs = []
    for k in range(SCRAMBLE):
        segs.append((t_in + k * STEP, t_in + (k + 1) * STEP, random.choice(POOL), random.choice(NOISE)))
    lock = t_in + SCRAMBLE * STEP
    segs.append((lock, t_out, ch, colour))
    for k in range(SCRAMBLE):
        segs.append((t_out + k * STEP, t_out + (k + 1) * STEP, random.choice(POOL), random.choice(NOISE)))
    for s, e, g, c in segs:
        anim = visible(s, e)
        if anim:
            fw = f' font-weight="{weight}"' if g == ch and weight != 400 else ""
            out.append(f'<text x="{r(x)}" y="{y}" font-size="{size}" fill="{c}"{fw} opacity="0">{esc(g)}{anim}</text>')


def line(text, y, size, colour, weight, t_in, t_out, stagger):
    cw = size * 0.6
    x0 = W / 2 - len(text) * cw / 2 + cw / 2
    for i, ch in enumerate(text):
        cell(x0 + i * cw, y, size, colour, weight, ch, t_in + i * stagger, t_out + i * stagger * 0.4)


for spec in LINES:
    line(*spec)

phrases, y, size, colour, weight, start, slot, hold, stagger = ROTATING
for n, p in enumerate(phrases):
    t = start + n * slot
    line(p, y, size, colour, weight, t, t + hold, stagger)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Let's build something - peterhoo.com · ciuslabs.com">
<defs>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7AA2F7"/><stop offset=".5" stop-color="#BB9AF7"/><stop offset="1" stop-color="#7DCFFF"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7AA2F7" stop-opacity="0"/><stop offset=".5" stop-color="#7AA2F7" stop-opacity=".10"/><stop offset="1" stop-color="#7AA2F7" stop-opacity="0"/>
  </linearGradient>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#1F2335"/>
  </pattern>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%">
    <feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="card"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14"/></clipPath>
</defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="#0D1117"/>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  <rect x="0" y="-60" width="{W}" height="60" fill="url(#scan)">
    <animate attributeName="y" values="-60;{H}" dur="4s" repeatCount="indefinite"/>
  </rect>
  <circle cx="22" cy="20" r="4.5" fill="#F7768E"/><circle cx="38" cy="20" r="4.5" fill="#E0AF68"/><circle cx="54" cy="20" r="4.5" fill="#9ECE6A"/>
  <text x="{W-20}" y="24" font-family="{FONT}" font-size="11" fill="#3B4261" text-anchor="end">juzt@ciuslabs: ~</text>
  <g font-family="{FONT}" text-anchor="middle" filter="url(#glow)">
{chr(10).join(out)}
  </g>
  <rect x="{W/2 + len(LINES[0][0])*LINES[0][2]*0.3 + 4}" y="{LINES[0][1]-12}" width="8" height="14" fill="#7AA2F7" opacity="0">
    <animate attributeName="opacity" values="0;1;0;1;0" keyTimes="0;.2;.4;.6;.8" calcMode="discrete" dur="1s" repeatCount="indefinite" begin="0s"/>
  </rect>
</g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="none" stroke="url(#edge)" stroke-opacity=".55" stroke-width="1.5"/>
</svg>
'''
Path(__file__).resolve().parent.parent.joinpath("assets/scramble.svg").write_text(svg, encoding="utf-8")
print(f"wrote assets/scramble.svg ({len(svg)//1024} KB, {len(out)} glyph frames)")
