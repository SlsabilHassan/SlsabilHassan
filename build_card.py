#!/usr/bin/env python3
"""
Generate a neofetch-style terminal SVG card for a GitHub profile README.
Left = ASCII-art portrait (from a photo, or a generated placeholder bust).
Right = SYSTEM INFO panel.

Usage:
    python3 build_card.py            # placeholder portrait
    python3 build_card.py photo.jpg  # convert a real photo to ASCII
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance

COLS = 54
# simpler ramp reads cleaner at small sizes:
RAMP = " .:-=+*#%@"

def load_or_make(path):
    if path:
        img = Image.open(path).convert("L")
        # Crop toward head-and-shoulders: central width, upper-biased height,
        # so the blurry background doesn't dominate the ASCII.
        w, h = img.size
        cw, ch = int(w * 0.62), int(h * 0.80)
        x0 = (w - cw) // 2
        y0 = int(h * 0.02)
        img = img.crop((x0, y0, x0 + cw, y0 + ch))
    else:
        # Procedurally draw a head-and-shoulders bust so the placeholder
        # still reads as an ASCII portrait.
        W, H = 400, 440
        img = Image.new("L", (W, H), 8)
        d = ImageDraw.Draw(img)
        # shoulders
        d.ellipse([40, 300, 360, 620], fill=120)
        # neck
        d.rectangle([170, 250, 230, 320], fill=140)
        # head
        d.ellipse([120, 70, 280, 290], fill=175)
        # hair
        d.pieslice([120, 60, 280, 250], 180, 360, fill=70)
        # simple face shading
        d.ellipse([150, 150, 180, 180], fill=110)  # eye socket L
        d.ellipse([220, 150, 250, 180], fill=110)  # eye socket R
        img = img.filter(ImageFilter.GaussianBlur(6))
    return img

def to_ascii(img, invert=False):
    # Boost separation between subject and background, then map luminance.
    img = ImageOps.autocontrast(img, cutoff=3)
    img = ImageEnhance.Contrast(img).enhance(1.35)
    w, h = img.size
    rows = max(1, int(COLS * (h / w) * 0.52))
    img = img.resize((COLS, rows))
    px = img.load()
    lines = []
    n = len(RAMP)
    for y in range(rows):
        row = ""
        for x in range(COLS):
            lum = px[x, y]
            if invert:
                lum = 255 - lum   # dark areas -> denser glyphs (portrait on dark bg)
            row += RAMP[min(n - 1, lum * n // 256)]
        lines.append(row.rstrip() or " ")
    return lines

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---- content of the SYSTEM INFO panel -------------------------------------
USER = "slsabil@wlu"
INFO = [
    ("header", "SYSTEM INFO"),
    ("user", USER),
    ("rule", ""),
    ("kv", ("Subject", "Slsabil Hassan")),
    ("kv", ("Role", "Computer Science Student")),
    ("kv", ("Origin", "Egypt")),
    ("kv", ("Education", "Washington & Lee University")),
    ("kv", ("Focus", "Full-Stack · Machine Learning · Ed-Tech")),
    ("kv", ("Interests", "Product Management · UI/UX Design")),
    ("kv", ("Status", "Building · Learning · Shipping")),
    ("kv", ("ToolChain", "VS Code, Git, Docker, Linux")),
    ("gap", ""),
    ("kv", ("Core Lang", "Python, TypeScript, Java, C++")),
    ("kv", ("Core Frontend", "React, Next.js, Tailwind")),
    ("kv", ("Core Backend", "Node.js, Django, FastAPI")),
    ("kv", ("Core Database", "PostgreSQL, MongoDB, MySQL")),
    ("kv", ("Core Infra", "Docker, AWS, Git")),
    ("gap", ""),
    ("section", "Contact"),
    ("kv", ("Grid Mail", "shassan@mail.wlu.edu")),
    ("kv", ("Grid Portfolio", "slsabilhassan.com")),
    ("kv", ("Grid LinkedIn", "in/slsabilhassan")),
    ("kv", ("Grid GitHub", "SlsabilHassan")),
    ("gap", ""),
    ("section", "Live Stats"),
    ("note", "See live GitHub stat badges below in README"),
]

def build_svg(ascii_lines, theme="dark"):
    if theme == "dark":
        C = dict(bg="#05070d", win="#0a0e17", border="#22d3ee", glow="#22d3ee",
                 dot1="#ff5f56", dot2="#febc2e", dot3="#27c93f",
                 title="#5b6675", prompt_u="#34d399", prompt_p="#38bdf8",
                 ascii="#38bdf8", header="#c084fc", user="#22d3ee",
                 key="#38bdf8", val="#c9d1d9", punct="#5b6675",
                 section="#34d399", note="#8b949e", rule="#1c2431")
    else:
        C = dict(bg="#eef2f7", win="#ffffff", border="#0ea5e9", glow="#7dd3fc",
                 dot1="#ff5f56", dot2="#febc2e", dot3="#27c93f",
                 title="#94a3b8", prompt_u="#059669", prompt_p="#0284c7",
                 ascii="#0369a1", header="#7c3aed", user="#0891b2",
                 key="#0284c7", val="#1e293b", punct="#94a3b8",
                 section="#059669", note="#64748b", rule="#e2e8f0")

    Wd, Ht = 1080, 700
    mono = "'JetBrains Mono','Fira Code','SF Mono',ui-monospace,Menlo,Consolas,monospace"
    px = 34            # left padding inside window
    bar_h = 40
    body_top = bar_h + 46
    left_x = px + 6
    right_x = 470
    fs_a = 12.5        # ascii font size
    lh_a = 13.2        # ascii line height
    fs = 15            # panel font size
    lh = 24            # panel line height

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Ht}" viewBox="0 0 {Wd} {Ht}" font-family="{mono}">')
    p.append(f'''<defs>
      <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="{C['glow']}" flood-opacity="0.9"/>
        <feDropShadow dx="0" dy="0" stdDeviation="16" flood-color="{C['glow']}" flood-opacity="0.35"/>
      </filter>
      <linearGradient id="winbg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{C['win']}"/>
        <stop offset="1" stop-color="{C['bg']}"/>
      </linearGradient>
    </defs>''')
    # backdrop
    p.append(f'<rect width="{Wd}" height="{Ht}" rx="18" fill="{C["bg"]}"/>')
    # window with glow
    p.append(f'<g filter="url(#glow)">')
    p.append(f'<rect x="22" y="22" width="{Wd-44}" height="{Ht-44}" rx="14" fill="url(#winbg)" stroke="{C["border"]}" stroke-width="1.6"/>')
    p.append('</g>')
    # title bar
    p.append(f'<line x1="22" y1="{22+bar_h}" x2="{Wd-22}" y2="{22+bar_h}" stroke="{C["rule"]}" stroke-width="1"/>')
    for i, col in enumerate([C["dot1"], C["dot2"], C["dot3"]]):
        p.append(f'<circle cx="{48+i*22}" cy="{22+bar_h/2}" r="6.5" fill="{col}"/>')
    p.append(f'<text x="{Wd/2}" y="{22+bar_h/2+4}" fill="{C["title"]}" font-size="13" text-anchor="middle">SlsabilHassan / README.md</text>')
    # prompt line
    py = 22 + bar_h + 28
    p.append(f'<text x="{px}" y="{py}" font-size="13.5">'
             f'<tspan fill="{C["prompt_u"]}">{USER}</tspan>'
             f'<tspan fill="{C["punct"]}"> ~ % </tspan>'
             f'<tspan fill="{C["prompt_p"]}">./profile.sh</tspan>'
             f'<tspan fill="{C["punct"]}"> --live</tspan></text>')

    # ASCII portrait (left) — vertically centered in the window body
    win_bottom = Ht - 22
    block_h = len(ascii_lines) * lh_a
    ay = max(body_top + 18, (body_top + win_bottom) / 2 - block_h / 2 + fs_a)
    p.append(f'<text x="{left_x}" y="{ay}" fill="{C["ascii"]}" font-size="{fs_a}" xml:space="preserve" opacity="0.95">')
    for i, line in enumerate(ascii_lines):
        p.append(f'<tspan x="{left_x}" dy="{0 if i==0 else lh_a}">{esc(line)}</tspan>')
    p.append('</text>')

    # SYSTEM INFO panel (right)
    y = body_top + 14
    for kind, data in INFO:
        if kind == "header":
            p.append(f'<text x="{right_x}" y="{y}" fill="{C["header"]}" font-size="{fs}" font-weight="700" letter-spacing="2">{esc(data)}</text>')
            y += lh
        elif kind == "user":
            p.append(f'<text x="{right_x}" y="{y}" fill="{C["user"]}" font-size="{fs}" font-weight="700">{esc(data)}</text>')
            y += lh * 0.7
        elif kind == "rule":
            p.append(f'<line x1="{right_x}" y1="{y-4}" x2="{Wd-40}" y2="{y-4}" stroke="{C["rule"]}" stroke-width="1"/>')
            y += lh * 0.6
        elif kind == "gap":
            y += lh * 0.5
        elif kind == "section":
            p.append(f'<text x="{right_x}" y="{y}" fill="{C["section"]}" font-size="{fs}" font-weight="700">+ {esc(data)}</text>')
            y += lh
        elif kind == "note":
            p.append(f'<text x="{right_x}" y="{y}" fill="{C["note"]}" font-size="13">&#9656; {esc(data)}</text>')
            y += lh
        elif kind == "kv":
            k, v = data
            dots = "." * max(2, 15 - len(k))
            p.append(f'<text x="{right_x}" y="{y}" font-size="{fs}">'
                     f'<tspan fill="{C["key"]}" font-weight="600">{esc(k)}</tspan>'
                     f'<tspan fill="{C["punct"]}"> {dots} </tspan>'
                     f'<tspan fill="{C["val"]}">{esc(v)}</tspan></text>')
            y += lh
    p.append('</svg>')
    return "\n".join(p)

def main():
    photo = sys.argv[1] if len(sys.argv) > 1 else None
    import os
    inv = os.environ.get("INVERT", "1") == "1"
    ascii_lines = to_ascii(load_or_make(photo), invert=bool(photo) and inv)
    for theme in ("dark", "light"):
        svg = build_svg(ascii_lines, theme)
        fn = f"{theme}.svg"
        with open(fn, "w") as f:
            f.write(svg)
        print(f"wrote {fn} ({len(ascii_lines)} ascii rows)")

if __name__ == "__main__":
    main()
