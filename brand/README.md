# HordeForge brand

<img src="tiles/hordeforge.svg" width="64" height="64" alt="HordeForge mark">

The rules every HordeForge surface follows: READMEs, web UIs, generated
reports, favicons. The brand sheet [`index.html`](index.html) shows all of it
rendered; open it locally or through a raw-file preview.

| File | What it is |
|---|---|
| [`products.json`](products.json) | Product roster: codename, descriptive name, repo, suite, glyph, emoji. The one source the build reads |
| [`tokens.css`](tokens.css) | The palette, radii, fonts, in shadcn/ui token names |
| [`glyphs/`](glyphs) | 24px product glyphs (two custom, the rest Lucide) |
| [`icons/`](icons) | 24px UI icon library (Lucide subset) |
| [`tiles/`](tiles) | Generated 32px product tiles and the master mark |
| [`banner.svg`](banner.svg) | Generated org profile header |
| [`avatar.png`](avatar.png) | 512px master mark for the GitHub org avatar (`rsvg-convert -w 512 tiles/hordeforge.svg -o avatar.png`; uploaded by hand in org settings, GitHub has no API for it) |
| [`index.html`](index.html) | Generated brand sheet |

Regenerate after editing `products.json`, a glyph, or `tokens.css`:

```bash
uv run scripts/build_brand.py          # writes tiles, banner, sheet
uv run scripts/build_brand.py --check  # CI form: fails when outputs are stale
```

The build fails when a suite color gives the paper glyph less than 4.5:1
contrast, or a product names a glyph that is not in `glyphs/`.

## The mark

An H whose crossbar is a tick trace: the 20 TPS heartbeat every HordeForge
tool measures, forges, or defends. Paper stems, terminal-green pulse
(`#5fd894`), ink tile (`#1a1d21`), corner radius 7 at 32px.

- Use [`tiles/hordeforge.svg`](tiles/hordeforge.svg) as is. Do not recolor
  the pulse, outline the tile, or set the mark on a busy image.
- Single-color contexts (a favicon mask, an embossed print) use
  [`glyphs/hordeforge.svg`](glyphs/hordeforge.svg) in `currentColor`.
- Minimum size 16px. Clear space around the tile: one quarter of its width.
- The wordmark is the name set in the system sans at weight 700, never
  redrawn or italicized: **HordeForge**, one word, capital H and F.

## Product tiles

Every product is a tile: its **suite color** as the ground, its **glyph** in
paper (`#f7f5f0`), 2px stroke on the 24px grid, centered in 32px with radius 7.
The tile is the product's favicon, README icon, and app icon.

| Suite | Color | Products |
|---|---|---|
| Servers & Engine | `#0f5c37` signal green | BloodWire, Crucible, Pangea |
| Observability & Testing | `#1f4e8c` gauge blue | Geiger, Screamer, Vanguard, Hotwire, Safehouse, Deadeye |
| Security, AI & Infrastructure | `#4b2f8a` guard violet | Landclaim, Clanker, Outpost, Schematics, Quarantine |
| Modding Toolkit | `#7c4a14` forge bronze | Anvil, Shamway, Unityz, Wrench |

- A suite color identifies a product and nothing else. It never marks state,
  a button, or a chart series; a UI's own palette does that.
- Codenames and emoji are unique across the org. Check `products.json`
  before adding a product; the emoji leads the README title; the profile
  tables show the tile instead.
- A new product needs a row in `products.json`, a glyph, a rebuild, and the
  profile README row, in one change.

## Palette

[`tokens.css`](tokens.css) holds every value, named after the shadcn/ui
contract so a Tailwind v4 + shadcn app publishes it with `@theme inline`
unchanged. The palette is the "paper cockpit":

- **Paper** (`#f7f5f0`) is the ground; cards are `#fffdf8` with one shadow.
- **Signal green** (`#0f5c37`) is the only action and live-state color.
- **State is a word in a pill**, with a tone behind it: green ok, amber
  warning (`#6b4a00`), red destructive (`#8a2318`). Never color alone.
- **The terminal** (`#101418`) is the one dark surface: charts, logs,
  consoles. Its green is `#5fd894`, its red `#ff7364`, its key amber
  `#ffd8a0`.

Body text on paper and on cards meets WCAG AA; check any new pairing before
shipping it.

## Type

System stacks only, no webfonts: pages load offline and from a game host.

- **Sans reads, mono is the machine.** Headings, labels, buttons, prose and
  stats are sans; ids, paths, commands, logs and key names are mono.
- Tabular numerals on every number a reader compares.
- Sentence case for headings and buttons. No ALL CAPS beyond short state
  words in a pill.

## Icons

[`icons/`](icons) is the UI set: Lucide geometry on a 24px grid, 2px round
stroke, `currentColor`, so an icon takes its text color. The Lucide ISC
license ships beside the files.

- An icon sits next to a word, not in place of one. Icon-only controls carry
  an `aria-label`.
- 16px in dense tables, 20px in navigation, 24px standalone. Never scale the
  stroke.
- A repo vendors the icons it uses (copy the SVG path data); nothing loads an
  icon font or a CDN at runtime.
- Adding an icon: copy it from `lucide-static` (1.48.0, the version vendored
  here), strip the license comment and `class`, keep `LICENSE-lucide`.

## Voice

Plain, specific, measured. Say what a tool does and what it proves, with the
number: "holds 20 TPS with 64 bots", not "blazing fast". No marketing
adjectives, no exclamation marks, no em dashes.
