# HordeForge Repository Standards

The rules every repository under [github.com/hordeforge](https://github.com/hordeforge)
follows. They are not aspirations: each one is already load-bearing in the
majority of the suite, and this document exists so a new repository starts
compliant instead of being retrofitted.

A rule here beats a local preference. A repository that cannot follow one says
so in its own `AGENTS.md`, with the reason.

---

## 1. Required files

Every repository has these, no exceptions:

| File | Why |
|---|---|
| `README.md` | Codename header, badges, quick start, then detail. See §2. |
| `AGENTS.md` | Agent-facing rules. Binds human contributors too. See §3. |
| `LICENSE` | MIT unless the tree vendors something incompatible. |
| `Makefile` | The single entry point for every operation. See §4. |
| `.gitignore` | Must cover build output, caches, venvs, `.scratch/`, and any local secret file. |
| `.gitattributes` | LF pinned, either `* text=auto eol=lf` or an equivalent per-extension form. A CRLF checkout breaks every shebang. Compiled artifacts are marked `binary`. |
| `.github/workflows/ci.yml` | See §5. |
| `.github/dependabot.yml` | Lockfile plus `github-actions` ecosystem, weekly. |

Add when the trigger applies, not before:

| File | Trigger |
|---|---|
| `SECURITY.md` | The repository handles credentials, accepts untrusted input, or ships something that runs on a public server. |
| `CHANGELOG.md` | The repository has cut a release tag. |
| `CONTRIBUTING.md` | The build has a gate a newcomer would otherwise weaken by accident. |
| `TODO.md` | Tracked work that is not yet an issue. |
| `.editorconfig` | The tree mixes languages with different indent conventions. |

## 2. README

The first eight lines are fixed shape, because they are what a visitor and the
org profile both read:

```markdown
# 🎯 Codename (Descriptive Name)

> **Part of [HordeForge](https://github.com/hordeforge)**: High-Performance Systems Engineering for 7 Days to Die.

![CI](https://github.com/hordeforge/REPO/actions/workflows/ci.yml/badge.svg)
![coverage](https://raw.githubusercontent.com/hordeforge/REPO/badges/coverage.svg)
![license](https://img.shields.io/github/license/hordeforge/REPO)
![release](https://img.shields.io/github/v/release/hordeforge/REPO)
```

- **Every repository has a codename.** Hybrid title: emoji, codename,
  parenthesised descriptive name. The codename is the one used in
  [`profile/README.md`](profile/README.md) and in the `Mods/` folder name.
- **The coverage badge is only claimed if CI regenerates it.** A badge that
  points at a stale `badges` branch is worse than no badge.
- Swap `release` for `last commit` until the first tag exists. Never show a
  release badge for a repository with no releases.
- Quick start comes before detail, and it must be copy-pasteable on a clean
  checkout. State the one line that proves the plumbing works offline.
- **A new repository is added to [`profile/README.md`](profile/README.md) in
  the same change that makes it public.** An unlisted repository is invisible.

## 3. AGENTS.md

One file, at the root, covering:

- **What this repository is** and, explicitly, what it does not own. Overlap
  between siblings is the most expensive kind of drift.
- **Critical rules** the reader must not discover by breaking them.
- **Gates that must not be weakened.** Name them. A gate nobody can name gets
  relaxed to make a change pass.
- **Commands**: the real invocations, with the flags that matter.
- **Layout** and a docs map.
- **Sibling projects**: which repository owns the thing you are about to
  reimplement here.
- Stock-game reverse engineering belongs in `7dtd-engine-research`, never
  duplicated locally.

`AGENTS.md` applies to human contributors too. Do not maintain a second copy
of the same rules under another filename; `CLAUDE.md`, if present, is a
one-line pointer to `AGENTS.md`.

## 4. Makefile

The Makefile is the interface. CI, contributors, and agents all go through it,
so a step that only exists in someone's shell history does not exist.

- `help` is the first target and the default goal. `make` with no argument
  prints what the repository can do.
- `check` is the full static verdict: lint, format check, type check, compile.
- `test` runs the suite offline, with no credential and no game install.
- `coverage` produces the report the badge is built from, wherever a suite
  exists.
- `clean` removes only generated output, never a source or a local config.
- Every target is in `.PHONY`.
- **Optional tooling degrades with a printed note on a dev host and hard-fails
  in CI.** The pattern, used verbatim across the suite:

  ```make
  lint:
  	@if command -v ruff >/dev/null 2>&1; then \
  		ruff check .; \
  	elif [ -n "$${CI:-}" ]; then \
  		echo "ERROR: CI requires ruff; e.g. uv tool install ruff" >&2; \
  		exit 1; \
  	else \
  		echo "note: ruff not installed; skipped python linting"; \
  	fi
  ```

  Silence is the failure mode this prevents: a skipped check that reads like a
  passed one.

## 5. CI

`ci.yml` runs on `push` to `main` and on every `pull_request`, and:

- **Pins every action to a full commit SHA**, with the version tag in a
  trailing comment. A mutable tag is a supply-chain hole; Dependabot keeps the
  SHAs current.
- Declares `permissions: contents: read` at the top. A job that genuinely
  needs to write raises its own `permissions` block, and runs only on `main`
  pushes so a pull request never sees the token.
- Sets `concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }`.
- Sets `timeout-minutes` on every job.
- Installs from the committed lockfile with hash verification
  (`uv sync --locked`, `bun install --frozen-lockfile`, `dotnet restore
  --locked-mode`). A CI run that resolves fresh is not reproducing anything.
- Runs `make check test`, not an inline copy of those commands.
- **Exercises the installed entry point**, not only the source tree, so a
  broken console script fails in CI rather than in a consumer's checkout.

## 6. Toolchain

- **Python: `uv`, never `pip`.** Dev tooling is pinned in a PEP 735
  `[dependency-groups] dev` list with exact `==` versions for linters and type
  checkers, because their verdicts change between releases. `uv.lock` is
  committed.
- **JS/TS: `bun`, never `npm`/`npx`/`node`.**
- **Everything is committed at one version.** A lockfile that CI does not
  verify is decoration.

## 7. What never enters the tree

- Credentials, API keys, machine paths, game installs, copyrighted game
  assets.
- Local secret config. The convention is a committed `config.toml` plus a
  gitignored `config.local.toml`, with a committed `config.local.toml.example`
  showing the shape.
- Build output, caches, venvs, coverage data, `dist/`.
- **Scratch files.** Every temporary, experimental, or bisect file goes in
  `.scratch/` at the repository root, which is gitignored. Never in `src/`,
  never loose in the root, never in `/tmp`.
- Logs, `repro.out`, `*.err`, `TestResults/`, superseded scripts kept "just in
  case". Delete them; git remembers.
- `Co-Authored-By` trailers or tool-generated attribution in commits, pull
  requests, code comments, or docs.

## 8. Releases

Tag-driven. Bump the version in its one canonical place, land that on `main`,
then push a matching `vX.Y.Z` tag. The release workflow re-runs the suite on
the tagged tree and publishes artifacts built from exactly that tree. **A tag
that disagrees with the manifest fails the release** instead of publishing a
mismatched artifact.

The version has exactly one canonical home per repository (`pyproject.toml`,
`ModInfo.xml`, a `*Version.cs` constant). Every other copy is documented as a
mirror and checked.

**The tag gate is required even where publishing is manual.** A repository
whose artifact cannot be built on a hosted runner still runs a `release.yml`
that does nothing but compare the tag to the manifest and fail on a mismatch.
That check is the part that protects consumers; the upload is convenience.

## 9. Evidence

The house rule that outranks style. Claims in a README, a changelog, or a
report are graded, and the grade is stated:

- **compiled**: it builds.
- **probed**: it ran under instrumentation.
- **executed**: it ran for real, in the game, on a host.

Never describe the first as the third. A platform absent from CI is asserted,
never proven: extend the matrix before extending the claim. An advisory
verdict from a model or a heuristic is evidence, never an acceptance.

---

## Current drift

Tracked so it gets fixed rather than normalised. Last swept 2026-08-25, when
the list below was closed out:

- ~~`7dtd-wasm` has no `ci.yml`.~~ Added, running the new `make check-ci`:
  the game-free half of `make check`. The `bridge` and `bridge-check` halves
  need a dedicated server install and stay a developer-host gate.
- ~~`7dtd-server-optimizer` has no `LICENSE`.~~ Added (MIT, matching every
  sibling), so its README license badge now resolves.
- ~~`7dtd-server-guard` has no `.gitattributes`.~~ Added. (`7dtd-wasm` was
  also on this list and should not have been: it already pins LF
  per-extension and marks `*.wasm binary`. Miscounted from a directory
  listing rather than the file.)
- ~~Only four repositories have `dependabot.yml`.~~ All fourteen have one,
  each covering the surfaces that actually exist in that tree: `uv`, `nuget`,
  `cargo`, `pip`, and `github-actions` everywhere.
- ~~`7dtd-asset-pipeline`, `7dtd-vision-review` and `7dtd-wasm` are missing
  from [`profile/README.md`](profile/README.md).~~ False alarm: the published
  profile already lists all fourteen. The **local working copy** of this
  repository under `hordeforge/.github/` had diverged from what is published,
  which is its own hazard: read the repository, not the copy on your disk.
- ~~Four READMEs have no codename header.~~ `7dtd-asset-pipeline` and
  `7dtd-engine-research` were missing their emoji; `7dtd-fastconnect` and
  `7dtd-playtest` were missing their codename entirely, although the org
  profile had been listing them as Hotwire and Vanguard for months. All
  fourteen now match §2.
- ~~The banner line is split between an em-dash and a colon variant.~~ All
  fourteen use the colon.
- ~~Several repositories have no `.scratch/` rule.~~ Added to the five that
  lacked one. `7dtd-fastconnect` had been ignoring a single scratch filename
  by hand; the glob replaces it.
- ~~`7dtd-engine-research` is Codex in the org profile and Schematics in its
  own README.~~ Schematics wins on evidence: seven references across the
  workspace, including the repository's own README and the `sibling-repos.md`
  cross-links two other repositories publish, against two in this repository
  alone. The profile and this repository's `AGENTS.md` now say Schematics.
- ~~Only `7dtd-asset-pipeline` has a `release.yml`.~~ Ten of fourteen now
  have one, and every one of those gates the tag against the version the
  repository actually ships, so a mistyped or forgotten bump is rejected
  instead of becoming a release nobody can reproduce. `7dtd-asset-pipeline`
  and `7dtd-vision-review` publish artifacts too (sdist, wheel, and a
  CycloneDX SBOM from the committed lock file). The mod repositories gate the
  tag and stop there: `make package` compiles against the dedicated server's
  own assemblies, which a hosted runner does not have, and publishing a zip
  CI cannot build would be a claim rather than evidence. A maintainer with a
  game install still runs `make package` and attaches the archive.

  The four without one each have a reason: `7dtd-engine-research`
  (documentation, nothing versioned), `7dtd-server-container` (container
  images, versioned by the base game), `7dtd-server-guard` (no build yet,
  Phase 2), and `zdtd-server`, which already gates the tag inside `make
  check` via `scripts/check-release.sh` and uploads its binary from
  `ci.yml`. That last one was on this list in error.


Still open:

- **`7dtd-server-guard` has test projects but no `build` or `test` target.**
  Its `make ci` is a docs gate only; the suite lands in Phase 2 (see its
  `TODO.md`). Until then the repository cannot satisfy §4.
- **Five repositories claim no coverage badge**: `7dtd-engine-research` and
  `7dtd-wasm` publish none, `7dtd-fps-bots` and `7dtd-server-guard` have no
  `coverage` target, and `zdtd-server` uses a SonarCloud quality gate
  instead. None of them shows a stale badge, which is the rule that matters,
  but the gap is real.
