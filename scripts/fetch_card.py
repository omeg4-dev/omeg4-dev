#!/usr/bin/env python3
"""Build the animated fetch-style profile card as two SVGs (dark + light).

Usage: python scripts/fetch_card.py            -> writes assets/fetch-dark.svg, assets/fetch-light.svg
Needs: fontTools (subsets JetBrains Mono so the block characters line up on every device).
"""
from __future__ import annotations

import base64
import io
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = Path("/usr/share/fonts/TTF/JetBrainsMonoNLNerdFontMono-Regular.ttf")
FONT_BOLD = Path("/usr/share/fonts/TTF/JetBrainsMonoNLNerdFontMono-Bold.ttf")

USER, HOST = "omega", "cachyos"

BANNER = [
    " ██████╗ ███╗   ███╗███████╗ ██████╗  █████╗ ",
    "██╔═══██╗████╗ ████║██╔════╝██╔════╝ ██╔══██╗",
    "██║   ██║██╔████╔██║█████╗  ██║  ███╗███████║",
    "██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║",
    "╚██████╔╝██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║",
    " ╚═════╝ ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝",
]

LOGO = [
    '                        ΩΩΩΩΩΩΩΩΩΩΩ',
    '                   ΩΩΩωωωωωωωωωωωωωωωΩΩΩ',
    '                 ΩΩωωωωωωΩΩΩΩΩΩΩΩΩωωωωωωΩΩ',
    '              ΩΩωωωωΩΩ               ΩΩωωωωΩΩ',
    '             ΩωωωωΩ                     ΩωωωωΩ',
    '           ΩΩωωωΩ                         ΩωωωΩΩ',
    '          ΩΩωωΩΩ                           ΩΩωωΩΩ',
    '         ΩΩωωΩΩ                             ΩΩωωΩΩ',
    '         ΩωωΩΩ                               ΩΩωωΩ',
    '        ΩωωωΩ                                 ΩωωωΩ',
    '        Ωωωω                                   ωωωΩ',
    '        ωωωΩ                                   ΩωωΩ',
    '        ωωωΩ                                   Ωωωω',
    '        ΩωωΩ                                   ΩωωΩ',
    '        ΩωωΩΩ                                  ωωωΩ',
    '        ΩωωωΩ                                 ΩωωωΩ',
    '         ΩωωωΩ                               ΩωωωΩ',
    '          ΩωωωΩ                             ΩωωωΩ',
    '  ΩΩΩΩΩΩΩΩΩωωωωΩ                           ΩωωωωΩΩΩΩΩΩΩΩΩ',
    ' ΩωωωωωωωωωωωωωωΩΩ                       ΩΩωωωωωωωωωωωωωωΩ',
    'ΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩ                   ΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩΩ',
]

INFO = [
    ("OS", "CachyOS x86_64"),
    ("WM", "Hyprland (Wayland)"),
    ("Shell", "zsh"),
    ("Terminal", "kitty"),
    ("Editor", "VS Code"),
    ("CPU", "Ryzen 7 5700X"),
    ("GPU", "GeForce RTX 4060"),
    ("Packages", "yes"),
    ("Langs", "Python · Kotlin · JS · QML"),
    ("Into", "graffiti · minecraft · gaming"),
    ("Status", "student from Germany"),
]

THEMES = {
    "dark": dict(ink="#f0f3f6", soft="#b7bdc4", muted="#7d8590", line="#ffffff2e", bar="#ffffff0d",
                 o1="#ffffff", o2="#8b949e", w1="#6e7681", w2="#30363d"),
    "light": dict(ink="#0b0d10", soft="#3d444d", muted="#6e7781", line="#0000002e", bar="#0000000a",
                  o1="#000000", o2="#6e7781", w1="#8c959f", w2="#d0d7de"),
}

SIZE = 15            # font px
CW = SIZE * 0.6      # JetBrains Mono advance = 600/1000 em
PAD_X, PAD_TOP = 26, 54
LOGO_SIZE = 9.5      # the omega art is 59 columns, so it gets a smaller font
LCW = LOGO_SIZE * 0.6
TYPE_SPEED = 0.07    # s per typed char


def font_face(path: Path, family: str, weight: int, text: str) -> str:
    opts = subset.Options()
    opts.flavor = "woff"
    opts.layout_features = []
    opts.name_IDs = []
    opts.hinting = False
    font = TTFont(path)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff');}}")


def line_height() -> float:
    f = TTFont(FONT)
    hhea, upm = f["hhea"], f["head"].unitsPerEm
    return round((hhea.ascent - hhea.descent) / upm * SIZE, 2)


def build(theme: str) -> str:
    c = THEMES[theme]
    LH = line_height()
    label_w = max(len(k) for k, _ in INFO) + 2
    title = f"{USER}@{HOST}"
    info_lines: list[tuple[str, str]] = [(title, "title"), ("─" * len(title), "rule")]
    info_lines += [(f"{k:<{label_w}}{v}", "kv") for k, v in INFO]
    info_cols = max(len(s) for s, _ in info_lines)
    logo_cols = max(len(r) for r in LOGO)
    LLH = LH * LOGO_SIZE / SIZE
    logo_w, logo_h = logo_cols * LCW, len(LOGO) * LLH
    gap_px = 3 * CW
    inner = max(len(BANNER[0]) * CW, logo_w + gap_px + info_cols * CW)
    width = round(PAD_X * 2 + inner)
    body: list[str] = []
    t = 0.6  # animation clock (s)
    y = PAD_TOP

    def typed(cmd: str, y: float, start: float) -> tuple[str, float]:
        parts = [f'<text x="{PAD_X}" y="{y}" class="p">❯</text>']
        x0 = PAD_X + 2 * CW
        for i, ch in enumerate(cmd):
            d = start + i * TYPE_SPEED
            parts.append(f'<text x="{x0 + i * CW:.2f}" y="{y}" class="c f" style="animation-delay:{d:.2f}s">{escape(ch)}</text>')
        return "".join(parts), start + len(cmd) * TYPE_SPEED + 0.35

    def reveal(text: str, x: float, y: float, cls: str, delay: float) -> str:
        return (f'<text x="{x:.2f}" y="{y:.2f}" class="{cls} f" xml:space="preserve" '
                f'style="animation-delay:{delay:.2f}s">{escape(text)}</text>')

    # 1) figlet OMEGA
    s, t = typed("figlet omega", y, t)
    body.append(s)
    y += LH * 1.25
    for i, row in enumerate(BANNER):
        body.append(reveal(row, PAD_X, y + i * (LH - 0.6), "b", t + i * 0.06))
    t += len(BANNER) * 0.06 + 0.5
    y += len(BANNER) * LH + LH * 0.9

    # 2) fastfetch
    s, t = typed("fastfetch", y, t)
    body.append(s)
    y += LH * 1.25
    info_h = (len(info_lines) + 2) * LH
    block_h = max(logo_h, info_h)
    ly = y - LH * 0.75 + (block_h - logo_h) / 2      # top edge of the logo box
    # outline (Ω) and fill (ω) as separate layers, each lit on a diagonal ramp like the real config
    for i, row in enumerate(LOGO):
        yy = ly + (i + 0.78) * LLH
        d = t + i * 0.035
        outline = "".join(ch if ch == "Ω" else " " for ch in row)
        fill = "".join(ch if ch == "ω" else " " for ch in row)
        for txt, cls in ((fill, "lw"), (outline, "lo")):
            if txt.strip():
                body.append(reveal(txt, PAD_X, yy, cls, d))
    defs = "".join(
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{PAD_X}" y1="{ly:.1f}" '
        f'x2="{PAD_X + logo_w:.1f}" y2="{ly + logo_h:.1f}"><stop offset="0" stop-color="{c[a]}"/>'
        f'<stop offset="1" stop-color="{c[b]}"/></linearGradient>'
        for gid, a, b in (("go", "o1", "o2"), ("gw", "w1", "w2")))
    ix = PAD_X + logo_w + gap_px
    for i, (txt, kind) in enumerate(info_lines):
        d = t + 0.15 + i * 0.09
        yy = y + i * LH
        if kind == "kv":
            k, v = txt[:label_w], txt[label_w:]
            body.append(reveal(k, ix, yy, "k", d) + reveal(v, ix + label_w * CW, yy, "v", d))
        elif kind == "title":
            body.append(reveal(USER, ix, yy, "k", d) + reveal("@", ix + len(USER) * CW, yy, "m", d)
                        + reveal(HOST, ix + (len(USER) + 1) * CW, yy, "k", d))
        else:
            body.append(reveal(txt, ix, yy, "m", d))
    # greyscale palette blocks, like fastfetch's colour row
    by = y + (len(info_lines) + 1) * LH
    greys = ["#000000", "#2b2b2b", "#555555", "#7f7f7f", "#a9a9a9", "#d4d4d4", "#ffffff"]
    d = t + 0.15 + len(info_lines) * 0.09 + 0.1
    for i, g in enumerate(greys):
        body.append(f'<rect x="{ix + i * 3 * CW:.2f}" y="{by - LH * 0.78:.2f}" width="{3 * CW:.2f}" '
                    f'height="{LH * 0.95:.2f}" fill="{g}" class="f" style="animation-delay:{d + i * 0.05:.2f}s"/>')
    t = d + len(greys) * 0.05 + 0.4
    y += max(block_h, info_h) + LH * 0.4

    # 3) idle prompt with blinking cursor
    body.append(f'<text x="{PAD_X}" y="{y}" class="p f" style="animation-delay:{t:.2f}s">❯</text>')
    body.append(f'<rect x="{PAD_X + 2 * CW:.2f}" y="{y - LH * 0.75:.2f}" width="{CW:.2f}" height="{LH * 0.95:.2f}" '
                f'fill="{c["ink"]}" class="cur" style="animation-delay:{t:.2f}s"/>')
    height = round(y + LH * 1.1)

    all_text = "ΩωΩ" + "".join(BANNER + LOGO) + "".join(s for s, _ in info_lines) + "❯figletomegafastfetch─·@" + "".join(k + v for k, v in INFO)
    css = (
        font_face(FONT, "JBM", 400, all_text) + font_face(FONT_BOLD, "JBM", 700, all_text) +
        f"text{{font-family:'JBM',ui-monospace,monospace;font-size:{SIZE}px;fill:{c['soft']};white-space:pre}}"
        f".b{{fill:{c['ink']}}}.k{{fill:{c['ink']};font-weight:700}}.v{{fill:{c['soft']}}}.m{{fill:{c['muted']}}}"
        f".lo{{fill:url(#go);font-size:{LOGO_SIZE}px;font-weight:700}}.lw{{fill:url(#gw);font-size:{LOGO_SIZE}px}}"
        f".p{{fill:{c['ink']};font-weight:700}}.c{{fill:{c['ink']}}}.t{{fill:{c['muted']};font-size:12px}}"
        ".f{opacity:0;animation:in .25s ease-out forwards}"
        "@keyframes in{to{opacity:1}}"
        ".cur{opacity:0;animation:blink 1.1s steps(1) infinite}"
        "@keyframes blink{0%{opacity:1}50%{opacity:0}}"
        "@media (prefers-reduced-motion:reduce){.f,.cur{animation:none;opacity:1}}"
    )
    frame = (
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{c["line"]}"/>'
        f'<path d="M0.5 32 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V32 Z" fill="{c["bar"]}"/>'
        f'<line x1="0.5" y1="32" x2="{width - 0.5}" y2="32" stroke="{c["line"]}"/>'
        + "".join(f'<circle cx="{20 + i * 18}" cy="16.5" r="5" fill="none" stroke="{c["muted"]}"/>' for i in range(3))
        + f'<text x="{width / 2}" y="20.5" text-anchor="middle" class="t">{USER}@{HOST}: ~</text>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{USER}@{HOST} fetch card">'
        f"<defs>{defs}</defs><style>{css}</style>{frame}{''.join(body)}</svg>\n"
    )


def main() -> None:
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    for theme in THEMES:
        p = out / f"fetch-{theme}.svg"
        p.write_text(build(theme), encoding="utf-8")
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size // 1024} KiB")


if __name__ == "__main__":
    main()
