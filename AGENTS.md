# AGENTS.md - HordeForge 7DTD Workspace

High-level rules and architecture boundaries for the **[HordeForge](https://github.com/hordeforge)** sibling repositories. Prefer the per-project `AGENTS.md` when working inside a single repo; this file owns workspace boundaries and the evidence loop.

Canonical modding guide: [`MODDING_BEST_PRACTICES.md`](MODDING_BEST_PRACTICES.md)

---

## Knowledge Map (Agent Traversal)

Workspace-wide graph + wiki (curated corpus; see `.graphifyignore`):

| Path | Use |
|---|---|
| [`graphify-out/wiki/index.md`](graphify-out/wiki/index.md) | Start here: community articles, crawl surface |
| [`graphify-out/GRAPH_REPORT.md`](graphify-out/GRAPH_REPORT.md) | God nodes, surprises, suggested questions |
| [`graphify-out/graph.json`](graphify-out/graph.json) | Structured graph for `graphify query` / `path` / `explain` |
| [`graphify-out/graph.html`](graphify-out/graph.html) | Interactive graph (browser) |

Agent order: this file → `graphify-out/wiki/` (or `graphify query "…"`) → project `AGENTS.md` / `docs/INDEX.md` → code.

Corpus is curated by [`.graphifyignore`](.graphifyignore) (no `third-party/`, no IL dumps, no builds/saves). Rebuild from workspace root:

```bash
make graphify          # default: AST + markdown structure (no LLM; reliable)
make graphify-llm      # optional ollama/cloud semantic
make graphify-wiki     # re-export wiki from existing graph.json
```

---

## Projects & Repositories

| Project / Product | Local Folder | Remote GitHub Repository | Primary Role | Details |
|---|---|---|---|---|
| **⚡ BloodWire** *(ZDTD Server)* | `zdtd-server/` | [`hordeforge/zdtd-server`](https://github.com/hordeforge/zdtd-server) | Native Zig dedicated rewrite (client wire); **not** mod host, **not** APM target | [`zdtd-server/AGENTS.md`](zdtd-server/AGENTS.md) |
| **🔥 Crucible** *(EfficientServer)* | `7dtd-server-optimizer/` | [`hordeforge/7dtd-server-optimizer`](https://github.com/hordeforge/7dtd-server-optimizer) | EfficientServer: reviewed Harmony performance governor & AI LOD fix | [`7dtd-server-optimizer/AGENTS.md`](7dtd-server-optimizer/AGENTS.md) |
| **☣️ Geiger** *(Server APM)* | `7dtd-server-apm/` | [`hordeforge/7dtd-server-apm`](https://github.com/hordeforge/7dtd-server-apm) | Host + optional bridge measurement, compare, budget, eBPF export | [`7dtd-server-apm/AGENTS.md`](7dtd-server-apm/AGENTS.md) |
| **😱 Screamer** *(HordeLoadGen)* | `7dtd-loadgen/` | [`hordeforge/7dtd-loadgen`](https://github.com/hordeforge/7dtd-loadgen) | Controlled LiteNetLib synthetic protocol clients and stress testing | [`7dtd-loadgen/AGENTS.md`](7dtd-loadgen/AGENTS.md) |
| **🤖 Clanker** *(FPS Bots Mod)* | `7dtd-fps-bots/` | [`hordeforge/7dtd-fps-bots`](https://github.com/hordeforge/7dtd-fps-bots) | Server-side FPS combat bots with neural decision brains & Web UI | [`7dtd-fps-bots/AGENTS.md`](7dtd-fps-bots/AGENTS.md) |
| **🛡️ Landclaim** *(ServerGuard)* | `7dtd-server-guard/` | [`hordeforge/7dtd-server-guard`](https://github.com/hordeforge/7dtd-server-guard) | Server-side behavioral validation, inventory conservation, & anti-cheat | [`7dtd-server-guard/AGENTS.md`](7dtd-server-guard/AGENTS.md) |
| **🌍 Pangea** *(RealEarth)* | `7dtd-realearth/` | [`hordeforge/7dtd-realearth`](https://github.com/hordeforge/7dtd-realearth) | 1:1 scale Earth GIS terrain, tile streaming, YDim column expand | [`7dtd-realearth/AGENTS.md`](7dtd-realearth/AGENTS.md) |
| **⚡ Hotwire** *(FastConnect)* | `7dtd-fastconnect/` | [`hordeforge/7dtd-fastconnect`](https://github.com/hordeforge/7dtd-fastconnect) | Client join-by-IP / auto-join / boot skip helper (no gameplay) | [`7dtd-fastconnect/AGENTS.md`](7dtd-fastconnect/AGENTS.md) |
| **🛡️ Vanguard** *(Playtest Runner)* | `7dtd-playtest/` | [`hordeforge/7dtd-playtest`](https://github.com/hordeforge/7dtd-playtest) | Stock-client scenario suite (drive + assert; scores real play) | [`7dtd-playtest/AGENTS.md`](7dtd-playtest/AGENTS.md) |
| **🏰 Outpost** *(Server Container)* | `7dtd-server-container/` | [`hordeforge/7dtd-server-container`](https://github.com/hordeforge/7dtd-server-container) | LAN dedicated server deployment (Podman container; Navezgane + mods) | [`7dtd-server-container/AGENTS.md`](7dtd-server-container/AGENTS.md) |
| **📜 Schematics** *(Engine Research)* | `7dtd-engine-research/` | [`hordeforge/7dtd-engine-research`](https://github.com/hordeforge/7dtd-engine-research) | Dedicated engine RE narratives (loop, AI, net, save, terrain APIs, Cecil dumps) | [`7dtd-engine-research/AGENTS.md`](7dtd-engine-research/AGENTS.md) |
| **🏭 Shamway** *(Asset Pipeline)* | `7dtd-asset-pipeline/` | [`hordeforge/7dtd-asset-pipeline`](https://github.com/hordeforge/7dtd-asset-pipeline) | Mod-owned AssetBundle build, editorless bundle synthesis, and the offline gates for silent asset failures | [`7dtd-asset-pipeline/AGENTS.md`](7dtd-asset-pipeline/AGENTS.md) |

---

## Boundaries (Do Not Blur)

```text
Screamer (loadgen)   → creates demand (LiteNetLib synthetic bots)
Geiger (apm)         → measures and gates evidence
Crucible (optimizer) → applies reviewed runtime optimization patches
Landclaim (guard)    → validates server-observable player actions and records evidence
Pangea (realearth)   → terrain product (optional world under test)
BloodWire (zdtd)     → optional Zig dedi (client-wire rewrite; not a mod host)
Hotwire (connect)    → client join-by-IP / boot skip only
Vanguard (playtest)  → stock-client gameplay scenarios + host scorer (not a server fix)
Shamway (assets)     → builds and gates a mod's own AssetBundle (client content, not a server path)
```

- Projects are **independent git trees**. None silently installs or rewrites another.
- **Measure and optimize live in different DLLs** (`HordeForge_Geiger` bridge vs `0_HordeForge_Crucible`) for **stock** dedi.
- **Host topology** (CCD/NUMA/affinity/IRQ) is ops, not a game mod: see `7dtd-server-optimizer/docs/HOST_TUNING.md`.
- **Engine expand** (YDim) lives only in RealEarth, never EfficientServer, APM, or zdtd.
- **Load bots** live only in `7dtd-loadgen` (not under RealEarth tools or zdtd).
- **Anti-cheat behavior and exploit validation** live only in `7dtd-server-guard`.
- **Container server deployment** (image, config template, mod staging from sibling `dist/`) lives only in `7dtd-server-container`. It hosts no mod code, no measurement, and no game RE.
- **Mod asset bundles are built only through `7dtd-asset-pipeline`.** It owns the build, the container and revision gates, and the editorless writer; it owns no art and no mod. Mods keep their own assets, generators and provenance.
- **Stock-game research lives only in `7dtd-engine-research`.** All reverse-engineering of the shipped dedicated server belongs there (`docs/` and `tools/`). Reimplementation code and mods stay in their own repos. Method: [`7dtd-engine-research/docs/re-methodology.md`](7dtd-engine-research/docs/re-methodology.md).
- **zdtd-server** does not ship game DLLs or bulk IL; protocol facts come from `7dtd-engine-research/docs`.
- **zdtd-server is not a 7dtd-server-apm target** (no Mono bridge). It has its **own** metrics/profiler under `zdtd-server/src/apm/`. Validate with loadgen + those dumps. **zdtd-server does not load mods**.

---

## Evidence Loop

```text
reproducible Screamer (loadgen) workload
  → Geiger (APM) baseline capture
  → one explicit Crucible (optimizer or host) change
  → same workload + Geiger APM compare / budget
  → Vanguard (playtest) gameplay soak for fidelity
```

Lower CPU alone is not acceptance. Same world, seed, bot count, duration, collectors, and server config for baseline vs candidate.

---

## Target Environment

| Field | Value |
|---|---|
| Game | V **3.2.0** (b9), Henpocalypse line |
| Runtime | Unity Mono (not IL2CPP) |
| Dedicated tick rate | **20 TPS** (50 ms budget), single-threaded main loop |
| Client (this machine) | `~/.local/share/Steam/steamapps/common/7 Days To Die` |
| Dedicated | `~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server` |
| In-game mod DLLs | **net48** + stock `0_TFP_Harmony` |
| Loadgen | **net8.0** external process |
| Host Python | **3.11+** via **`uv`** only (never pip) |

Any C# code mod forces the server EAC-off (`-noeac`); only XML-only mods run under EAC. Loadgen bots also require EAC disabled.

---

## Critical Workspace Rules

1. **Do not redistribute** game assemblies or bulk IL. RE dumps under `7dtd-engine-research/il/` are regenerable; narratives under `7dtd-engine-research/docs/`.
2. **Do not invent optim patches** without a baseline and a fidelity plan.
3. **Change one lever at a time** (one EfficientServer feature group, or one host knob, or one RealEarth path).
4. **Install / engine-patch commands write into Steam dirs.** Stop game/server, confirm paths, keep backups.
5. **Secrets** (telnet, dashboard) via env only; never in argv or commits.
6. **No AI attribution** in commits, docs, PRs, or comments.
7. **No em dashes** in any text shipped from this workspace.
8. Prefer project `make` / documented scripts over ad-hoc copies into `Mods/`.
9. **Name for what it does; never a name that can be misread.** Config keys, C# fields, function params, flags: the name must state the true behavior so a reader infers it without the docs.
10. **Do not mod client behaviour to paper over missing server features.** When the stock client fails because zdtd (or any server under test) lacks a package, field, order, or sim path, implement that on the **server**. Client mods (`7dtd-fastconnect` and friends) may only do join/automation plumbing.

---

## Where to Put Work

| Goal | Put it in |
|---|---|
| Missing wire/sim so stock client can play | **server** (`zdtd-server` or stock dedi path), never client Harmony workarounds |
| Join N bots / soak dedicated | `7dtd-loadgen` |
| Stock client join-by-IP / auto-join | `7dtd-fastconnect` |
| Automated real-client play suites | `7dtd-playtest` |
| Capture, compare, budget, export | `7dtd-server-apm` |
| Reviewed AI LOD / mesh / dedicated skips | `7dtd-server-optimizer` |
| Server-side anti-cheat evidence / impossible-action rejection | `7dtd-server-guard` |
| Earth tiles, bake-world, YDim expand | `7dtd-realearth` |
| Dedicated loop RE narrative | `7dtd-engine-research/docs/` |
| Raw Cecil dump regeneration | `7dtd-engine-research/tools/` (build.sh) -> `7dtd-engine-research/il/` |
| Host CCD/NUMA procedure | `7dtd-server-optimizer/docs/HOST_TUNING.md` (ops, not DLL) |

---

## Safety

Captures, generated worlds, tile packs, build outputs, and server userdata can be large runtime artifacts, not source. Do not commit secrets, session dumps, or game `Assembly-CSharp.dll`.
