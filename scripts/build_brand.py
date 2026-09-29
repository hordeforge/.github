"""Build the HordeForge brand outputs from brand/products.json and brand/glyphs.

Writes brand/tiles/<id>.svg (one 32px tile per product plus the master mark),
brand/banner.svg (the org profile header) and brand/index.html (the brand
sheet). Fails when a tile's glyph color drops under WCAG AA contrast (4.5:1)
against its suite color, or a product names a glyph that does not exist.

Usage: uv run scripts/build_brand.py [--check]
  --check  exit 1 if any output differs from what is committed, write nothing.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class Suite(TypedDict):
    name: str
    color: str


class Product(TypedDict):
    id: str
    codename: str
    name: str
    repo: str
    suite: str
    glyph: str
    emoji: str


class BrandData(TypedDict):
    suites: dict[str, Suite]
    products: list[Product]

PAPER = "#f7f5f0"
INK = "#1a1d21"
PULSE = "#5fd894"
TILE_PX = 32
TILE_RADIUS = 7
GLYPH_OFFSET = 4  # centers the 24px glyph grid in the 32px tile
MIN_CONTRAST = 4.5
SRGB_LINEAR_KNEE = 0.03928
LUMA = (0.2126, 0.7152, 0.0722)


def find_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "brand" / "products.json").is_file():
            return parent
    raise FileNotFoundError("brand/products.json not found above " + str(here))


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= SRGB_LINEAR_KNEE else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return sum(w * c for w, c in zip(LUMA, linear, strict=True))


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def glyph_body(path: Path) -> str:
    """The drawing elements of a 24px stroke glyph, without its <svg> wrapper."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"<svg[^>]*>(.*)</svg>", text, re.DOTALL)
    if match is None:
        raise ValueError(f"{path}: no <svg> element")
    return "".join(line.strip() for line in match.group(1).splitlines())


def tile_svg(label: str, fill: str, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE_PX} {TILE_PX}" '
        f'width="{TILE_PX}" height="{TILE_PX}" role="img" aria-label="{html.escape(label)}">'
        f'<rect width="{TILE_PX}" height="{TILE_PX}" rx="{TILE_RADIUS}" fill="{fill}"/>'
        f'<g transform="translate({GLYPH_OFFSET} {GLYPH_OFFSET})" fill="none" stroke="{PAPER}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>\n'
    )


def master_tile() -> str:
    """The HordeForge mark: paper stems, terminal-green pulse, on ink."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE_PX} {TILE_PX}" '
        f'width="{TILE_PX}" height="{TILE_PX}" role="img" aria-label="HordeForge">'
        f'<rect width="{TILE_PX}" height="{TILE_PX}" rx="{TILE_RADIUS}" fill="{INK}"/>'
        f'<g transform="translate({GLYPH_OFFSET} {GLYPH_OFFSET})" fill="none" stroke-width="2.25" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M5 4v16M19 4v16" stroke="{PAPER}"/>'
        f'<path d="M5 12h3l2-4 4 8 2-4h3" stroke="{PULSE}"/></g></svg>\n'
    )


def banner_svg() -> str:
    """Org profile header, 880x200. Carries its own ink ground so it reads on
    GitHub's light and dark themes alike."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 200" width="880" height="200" '
        'role="img" aria-label="HordeForge: high-performance systems engineering for 7 Days to Die">'
        f'<rect width="880" height="200" rx="20" fill="{INK}"/>'
        '<g transform="translate(56 52) scale(4)" fill="none" stroke-width="2.25" '
        'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M5 4v16M19 4v16" stroke="{PAPER}"/>'
        f'<path d="M5 12h3l2-4 4 8 2-4h3" stroke="{PULSE}"/></g>'
        '<g font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif">'
        f'<text x="200" y="104" font-size="56" font-weight="700" fill="{PAPER}" letter-spacing="-1">HordeForge</text>'
        '<text x="202" y="142" font-size="20" fill="#7f8b94">High-performance systems engineering for 7 Days to Die</text>'
        '</g>'
        f'<path d="M200 164h120" stroke="{PULSE}" stroke-width="3" stroke-linecap="round"/>'
        '</svg>\n'
    )


def inline_icon(body: str, label: str) -> str:
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{html.escape(label)}">{body}</svg>'
    )


def build(root: Path) -> dict[Path, str]:
    brand = root / "brand"
    data: BrandData = json.loads((brand / "products.json").read_text(encoding="utf-8"))
    suites = data["suites"]
    outputs: dict[Path, str] = {
        brand / "tiles" / "hordeforge.svg": master_tile(),
        brand / "banner.svg": banner_svg(),
    }
    errors: list[str] = []
    for suite_id, suite in suites.items():
        ratio = contrast(PAPER, suite["color"])
        if ratio < MIN_CONTRAST:
            errors.append(f"suite {suite_id}: paper on {suite['color']} is {ratio:.2f}:1, under {MIN_CONTRAST}:1")
    for product in data["products"]:
        glyph = brand / "glyphs" / f"{product['glyph']}.svg"
        if not glyph.is_file():
            errors.append(f"{product['id']}: glyph {glyph.name} does not exist")
            continue
        if product["suite"] not in suites:
            errors.append(f"{product['id']}: unknown suite {product['suite']}")
            continue
        label = f"{product['codename']} ({product['name']})"
        outputs[brand / "tiles" / f"{product['id']}.svg"] = tile_svg(
            label, suites[product["suite"]]["color"], glyph_body(glyph)
        )
    if errors:
        raise SystemExit("\n".join(["brand build failed:", *errors]))
    outputs[brand / "index.html"] = sheet_html(brand, data, outputs)
    return outputs


def sheet_html(brand: Path, data: BrandData, outputs: dict[Path, str]) -> str:
    suites = data["suites"]
    tokens = (brand / "tokens.css").read_text(encoding="utf-8")
    swatches = re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-f]{6});", tokens)
    tile_rows = []
    for suite_id, suite in suites.items():
        cards = []
        for product in (p for p in data["products"] if p["suite"] == suite_id):
            svg = outputs[brand / "tiles" / f"{product['id']}.svg"]
            cards.append(
                '<li class="product">'
                + svg.replace("<svg ", '<svg class="tile" ', 1)
                + f'<span class="codename">{html.escape(product["codename"])}</span>'
                + f'<span class="meta">{html.escape(product["name"])}</span>'
                + f'<code>{html.escape(product["repo"])}</code></li>'
            )
        tile_rows.append(
            f'<section class="suite"><h3><span class="dot" style="background:{suite["color"]}"></span>'
            f"{html.escape(suite['name'])} <code>{suite['color']}</code></h3>"
            f'<ul class="products">{"".join(cards)}</ul></section>'
        )
    icons = sorted((brand / "icons").glob("*.svg"))
    icon_cells = "".join(
        f"<li>{inline_icon(glyph_body(p), p.stem)}<code>{p.stem}</code></li>" for p in icons
    )
    swatch_cells = "".join(
        f'<li><span class="chip" style="background:{value}"></span><code>--{name}</code><code>{value}</code></li>'
        for name, value in swatches
    )
    master = outputs[brand / "tiles" / "hordeforge.svg"].replace("<svg ", '<svg class="mark" ', 1)
    return SHEET_TEMPLATE.format(
        tokens=tokens,
        master=master,
        suites="".join(tile_rows),
        icons=icon_cells,
        swatches=swatch_cells,
        count=len(data["products"]),
        icon_count=len(icons),
    )


SHEET_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HordeForge brand</title>
<meta name="description" content="HordeForge marks, product tiles, palette and icon library.">
<style>
{tokens}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--background);color:var(--foreground);font:15px/1.55 var(--font-sans)}}
main{{max-width:72rem;margin:0 auto;padding:3rem 1rem 5rem}}
h1{{font-size:2.5rem;letter-spacing:-0.02em;margin:0}}
h2{{font-size:1.25rem;margin:3rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid var(--border)}}
h3{{font-size:1rem;margin:1.5rem 0 .75rem;display:flex;align-items:center;gap:.5rem}}
code{{font:12.5px/1.4 var(--font-mono);color:var(--muted-foreground)}}
p{{max-width:44rem}}
.hero{{display:flex;align-items:center;gap:1.5rem;padding:2rem;border-radius:var(--radius-card);background:var(--term);color:var(--term-text)}}
.hero p{{margin:.25rem 0 0;color:var(--term-faint)}}
.mark{{width:96px;height:96px;flex:none;border-radius:21px;outline:1px solid var(--term-line)}}
.dot{{width:.75rem;height:.75rem;border-radius:3px;display:inline-block}}
ul{{list-style:none;margin:0;padding:0}}
.products{{display:grid;grid-template-columns:repeat(auto-fill,minmax(13rem,1fr));gap:.75rem}}
.product{{display:grid;grid-template-columns:48px 1fr;grid-template-rows:auto auto auto;column-gap:.75rem;align-items:center;padding:.75rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius-card);box-shadow:var(--shadow-card)}}
.tile{{width:48px;height:48px;grid-row:1/4}}
.codename{{font-weight:600}}
.meta{{color:var(--muted-foreground);font-size:13px}}
.icons{{display:grid;grid-template-columns:repeat(auto-fill,minmax(8rem,1fr));gap:.5rem}}
.icons li{{display:flex;align-items:center;gap:.6rem;padding:.6rem .75rem;background:var(--card);border:1px solid var(--border);border-radius:var(--radius-control)}}
.icon{{width:20px;height:20px;flex:none}}
.swatches{{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.4rem}}
.swatches li{{display:grid;grid-template-columns:1.5rem 1fr auto;gap:.6rem;align-items:center}}
.chip{{width:1.5rem;height:1.5rem;border-radius:5px;border:1px solid var(--border-strong)}}
@media (max-width:40rem){{.hero{{flex-direction:column;align-items:flex-start}}}}
</style>
</head>
<body>
<main>
<header class="hero">{master}<div><h1>HordeForge</h1><p>Marks, product tiles, palette and icon library. Generated by <code>scripts/build_brand.py</code>; the rules live in <code>brand/README.md</code>.</p></div></header>
<h2>Products ({count})</h2>
{suites}
<h2>Icon library ({icon_count})</h2>
<p>24px grid, 2px round stroke, <code>currentColor</code>. Lucide geometry (ISC), vendored in <code>brand/icons</code>.</p>
<ul class="icons">{icons}</ul>
<h2>Palette</h2>
<ul class="swatches">{swatches}</ul>
</main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if outputs are stale; write nothing")
    args = parser.parse_args()
    root = find_root()
    outputs = build(root)
    stale = [p for p, text in outputs.items() if not p.is_file() or p.read_text(encoding="utf-8") != text]
    if args.check:
        for path in stale:
            print(f"stale: {path.relative_to(root)}", file=sys.stderr)
        raise SystemExit(1 if stale else 0)
    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(outputs[path], encoding="utf-8")
        print(f"wrote {path.relative_to(root)}")


if __name__ == "__main__":
    main()
