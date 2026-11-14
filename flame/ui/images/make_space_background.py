# ruff: noqa: E501
"""Draw the site's space background (colours in the dominant blue family, 60-30-10 rule), `space_background.svg`: stars, small spiral galaxies, planets.

An original drawing made of simple shapes (no photo, no outside image). Run it again to change the drawing:

    uv run python flame/ui/images/make_space_background.py

The random draw is seeded, so the same file comes out each time.
"""

import math
import random
from pathlib import Path

WIDTH, HEIGHT = 1600, 1000
OUT = Path(__file__).with_name("space_background.svg")
rng = random.Random(2026)


def _dots(points: list[tuple[float, float]], width: float, color: str, opacity: float) -> str:
    """Many round dots in one short path: each dot is a zero-length line with round ends (keeps the file small)."""
    moves = "".join(f"M{x:.0f} {y:.0f}h0" for x, y in points)
    return (
        f'<path d="{moves}" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
        f'opacity="{opacity}" fill="none"/>'
    )


def stars() -> str:
    """Hundreds of faint stars, a few bright ones with four soft spikes, some of which twinkle."""
    parts = []
    # The faint stars, in groups of one size, tint and brightness.
    for width, color, opacity, count in [
        (0.9, "#ffffff", 0.35, 170),
        (1.1, "#dfe6ff", 0.55, 140),
        (1.4, "#ffeedd", 0.6, 90),
        (1.8, "#cdd8ff", 0.75, 60),
        (2.2, "#ffffff", 0.85, 30),
    ]:
        points = [(rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)) for _ in range(count)]
        parts.append(_dots(points, width, color, opacity))
    for i in range(26):
        x, y = rng.uniform(0, WIDTH), rng.uniform(0, HEIGHT)
        size = rng.uniform(4, 9)
        twinkle = ' class="tw"' if i % 2 == 0 else ""
        delay = f' style="animation-delay:{rng.uniform(0, 6):.1f}s"' if twinkle else ""
        parts.append(
            f'<g transform="translate({x:.0f} {y:.0f})"{twinkle}{delay}>'
            f'<circle r="{size * 0.9:.1f}" fill="url(#glow)"/>'
            f'<path d="M0 -{size:.1f}L0.5 0L0 {size:.1f}L-0.5 0ZM-{size:.1f} 0L0 0.5L{size:.1f} 0L0 -0.5Z" '
            f'fill="#fff" opacity="0.7"/><circle r="1.3" fill="#fff"/></g>'
        )
    return "".join(parts)


def galaxy(cx: float, cy: float, size: float, tilt: float, turn: float, tint: str) -> str:
    """A small spiral galaxy: a glowing core and two arms of dots, seen at an angle."""
    # Dots near the core are brighter: three rings of brightness, each drawn as one path.
    rings: dict[int, list[tuple[float, float]]] = {0: [], 1: [], 2: []}
    for arm in range(2):
        for step in range(170):
            t = step / 170
            angle = arm * math.pi + t * 3.4 * math.pi
            radius = size * (0.08 + 0.92 * t)
            spread = size * 0.07 * (0.4 + t)
            x = radius * math.cos(angle) + rng.gauss(0, spread)
            y = radius * math.sin(angle) + rng.gauss(0, spread)
            rings[min(2, int(t * 3))].append((x, y))
    dots = [_dots(rings[0], 2.4, tint, 0.95), _dots(rings[1], 2.0, tint, 0.65), _dots(rings[2], 1.6, tint, 0.4)]
    return (
        f'<g transform="translate({cx} {cy}) rotate({turn}) scale(1 {tilt})" opacity="1">'
        f'<ellipse rx="{size * 1.15:.0f}" ry="{size * 1.15:.0f}" fill="url(#halo)"/>'
        f'{"".join(dots)}<circle r="{size * 0.22:.1f}" fill="url(#core)"/></g>'
    )


def planet(cx: float, cy: float, r: float, gradient: str, ring: bool = False, bands: bool = False) -> str:
    """A planet lit from the upper left, with an optional ring and soft cloud bands."""
    clip = f"clip{int(cx)}{int(cy)}"
    band_lines = ""
    if bands:
        band_lines = "".join(
            f'<ellipse cx="{cx}" cy="{cy + offset * r:.1f}" rx="{r * 1.1:.1f}" ry="{r * 0.07:.1f}" '
            f'fill="#fff" opacity="{0.05 + 0.04 * (i % 2):.2f}"/>'
            for i, offset in enumerate([-0.55, -0.3, -0.05, 0.2, 0.45, 0.7])
        )
    body = (
        f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 1.35:.1f}" fill="url(#atmo)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gradient})"/>'
        f'<g clip-path="url(#{clip})">{band_lines}</g>'
        # The night side: a soft shade towards the lower right, no hard edge.
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#shade)"/>'
    )
    if not ring:
        return body
    # The ring: the whole ellipse behind the planet, then its near half again in front of it.
    ellipse = (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 2.0:.1f}" ry="{r * 0.42:.1f}" fill="none" '
        f'stroke="url(#ring)" stroke-width="{r * 0.22:.1f}"/>'
    )
    near = f"near{int(cx)}{int(cy)}"
    return (
        f'<clipPath id="{near}"><rect x="{cx - r * 3}" y="{cy}" width="{r * 6}" height="{r * 3}"/></clipPath>'
        f'<g transform="rotate(-14 {cx} {cy})" opacity="0.5">{ellipse}</g>'
        + body
        + f'<g transform="rotate(-14 {cx} {cy})" opacity="0.9"><g clip-path="url(#{near})">{ellipse}</g></g>'
    )


# The SVG gradients, one per line: long lines, kept whole so that each colour stop stays readable.
DEFS = """<defs>
<radialGradient id="glow"><stop offset="0" stop-color="#fff" stop-opacity="0.55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop offset="0" stop-color="#fffaf0"/><stop offset="0.35" stop-color="#ffe2b8" stop-opacity="0.8"/><stop offset="1" stop-color="#ffb37a" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop offset="0" stop-color="#b9a4ff" stop-opacity="0.35"/><stop offset="1" stop-color="#6d4bd8" stop-opacity="0"/></radialGradient>
<radialGradient id="atmo"><stop offset="0.72" stop-color="#8fb4ff" stop-opacity="0.18"/><stop offset="1" stop-color="#8fb4ff" stop-opacity="0"/></radialGradient>
<radialGradient id="giant" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#cdd6f6"/><stop offset="0.5" stop-color="#6574b4"/><stop offset="1" stop-color="#1b2150"/></radialGradient>
<radialGradient id="red" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#e3a58c"/><stop offset="0.6" stop-color="#8a4a44"/><stop offset="1" stop-color="#26142a"/></radialGradient>
<radialGradient id="ice" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#c8f1ff"/><stop offset="0.55" stop-color="#4f9bd6"/><stop offset="1" stop-color="#132a5c"/></radialGradient>
<radialGradient id="violet" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#d2d6f2"/><stop offset="0.55" stop-color="#5c64a6"/><stop offset="1" stop-color="#1a1d45"/></radialGradient>
<radialGradient id="grey" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#eeeef2"/><stop offset="0.6" stop-color="#8b8c99"/><stop offset="1" stop-color="#25263a"/></radialGradient>
<linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="#c9d1ee" stop-opacity="0"/><stop offset="0.2" stop-color="#c9d1ee"/><stop offset="0.5" stop-color="#8d98c8" stop-opacity="0.6"/><stop offset="0.8" stop-color="#c9d1ee"/><stop offset="1" stop-color="#c9d1ee" stop-opacity="0"/></linearGradient>
<linearGradient id="shade" x1="0.15" y1="0.15" x2="0.9" y2="0.9"><stop offset="0.38" stop-color="#02030a" stop-opacity="0"/><stop offset="1" stop-color="#02030a" stop-opacity="0.9"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
</defs>"""

# Twinkling stars, still for visitors who ask for less motion.
STYLE = (
    "<style>@keyframes tw{0%,100%{opacity:1}50%{opacity:.35}}.tw{animation:tw 5s ease-in-out infinite}"
    "@media (prefers-reduced-motion: reduce){.tw{animation:none}}</style>"
)


def drawing() -> str:
    """The whole picture. Planets and galaxies sit near the edges, where the cards leave the page visible."""
    nebulae = (
        '<g filter="url(#soft)" opacity="0.5">'
        '<ellipse cx="260" cy="180" rx="260" ry="120" fill="#2e3a8c"/>'
        '<ellipse cx="1350" cy="760" rx="300" ry="140" fill="#1d3f9e"/>'
        '<ellipse cx="900" cy="80" rx="220" ry="70" fill="#26306e" opacity="0.6"/></g>'
    )
    galaxies = (
        galaxy(1390, 150, 90, 0.45, -25, "#d9ccff")
        + galaxy(150, 760, 120, 0.38, 20, "#dfe4ff")
        + galaxy(760, 930, 55, 0.5, 60, "#c9dcff")
        + galaxy(560, 110, 38, 0.55, -40, "#e6dcff")
    )
    planets = (
        planet(1500, 930, 140, "giant", ring=True, bands=True)
        + planet(95, 120, 34, "red")
        + planet(1230, 420, 16, "ice")
        + planet(430, 560, 11, "grey")
        + planet(1040, 980, 22, "violet", bands=True)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'preserveAspectRatio="xMidYMid slice">{DEFS}{STYLE}{nebulae}{stars()}{galaxies}{planets}</svg>'
    )


if __name__ == "__main__":
    OUT.write_text(drawing())
    print(f"{OUT.name}: {OUT.stat().st_size // 1024} KB")
