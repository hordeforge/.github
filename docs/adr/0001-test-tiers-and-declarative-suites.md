# 0001. Test tiers and declarative suites

Status: Accepted (2026-09-01)

## Context

Eight places in the workspace started a stock dedicated server for a test:
`7dtd-sandbox` (`sb launch-server`), `7dtd-playtest` (`start_stock_dedicated`),
`7dtd-loadgen` (`start_dedicated_prefab.sh`), `7dtd-realearth` (three
`start_dedicated_*.sh`), `7dtd-server-optimizer` (`run_server.sh`),
`7dtd-vision-review` (`e2e.sh`), `7dtd-wasm` (frozen evidence scripts), and
`7dtd-server-container` (`entrypoint.sh`, production). Four of them carried
their own serverconfig XML rewriter, three their own `serveradmin.xml` seed,
and only Safehouse allocated ports; everything else hardcoded 26900 / 8081 /
8087 / 27025, which is why loadgen carries an `RE_TELNET_PORT` override to
dodge a busy host.

Three consequences made this worth deciding rather than tolerating.

**The orchestrator was a second sandbox.** `playtest_run.py` held
`write_stock_config`, `start_stock_dedicated`, `_rewrite_platform_cfg` (which
backed up and rewrote `platform.cfg` inside the user's Steam install),
`fresh_save`, and a blanket `pkill 7DaysToDieServer.x86_64` that reached every
sandbox instance on the machine. `--target sandbox` was added beside that code
rather than replacing it, so `--target stock` still wrote into the Steam
install while `--target sandbox` did not.

**Suites were declarative in name only.** `suites/*.json` declared ids,
targets and case refs, but nothing resolved a `ref` against `Catalog.cs`,
nothing staged the `mods` list, and `PLAYTEST_SUITE` still shipped a bare
string to the client, which rebuilt the queue itself. The JSON was a report
payload and a lint target.

**The schema contradicted itself.** `fresh` was `const: true` while `target`
included `live`, so a suite against a production server could not be written
honestly: the harness must not wipe a host it does not own.

## Decision

Four tiers, one direction of dependency.

```text
tier 0  provision    sb fetch-base / fetch-server-base            7dtd-sandbox
tier 1  environment  sb create/stage/up/render-config/wipe/stop   7dtd-sandbox
tier 2  harness      playtest_run: drive, assert, score           7dtd-playtest
tier 3  cases        suites/*.json + IScenarioProvider            playtest (stock) / mod repos (their own)

production           7dtd-server-container, outside the stack, attach-only
```

Two invariants:

- Nothing above tier 1 opens a serverconfig, allocates a port, or execs the
  dedicated binary.
- Nothing below tier 2 knows what a suite is.

### Two axes replace five targets

`--target stock|sandbox|attach|zdtd|live` conflated who owns the process with
which server is under test. It becomes:

| Axis | Values | Meaning |
|---|---|---|
| `--provision` | `managed` \| `attach` | Safehouse brings the server up and tears it down, or it is already running and playtest touches no lifecycle |
| `--server` | `stock` \| `zdtd` | which server is under test (unchanged flag, now named as the backend axis) |
| `--readonly` | attach-only flag | the host must never be written to (a production `7dtd-server-container` LAN server) |

A managed stock run is always a Safehouse instance. There is no path that
starts a dedicated inside the user's Steam install.

### Safehouse is declarative and deterministic

An instance is described by two files and everything else is derived from them:
`instance.env` (identity, port block, `SERVER_ADMINS`) and `instance.props`
(the serverconfig properties it runs with). Three fixes make that hold:

- **The serverconfig is rebuilt from the pristine base template on every
  launch**, never edited in place. In-place editing accumulates: a suite that
  set `MaxSpawnedZombies=0` left it set for the next suite that said nothing
  about spawns, which quietly changed what that suite measured. Undeclaring a
  property now returns it to the stock value.
- **Ports are derived from the instance name**, not from creation order. The
  old allocator scanned existing instances and handed out the next free block,
  so the same instance got different ports on different machines and a
  recorded port did not reproduce. `ServerPort`, `TelnetPort` and
  `UserDataFolder` are instance-owned; `sb render-config` refuses them.
- **Admins are declared, not discovered.** Seeding enumerated whatever client
  instances existed on the machine, so an unrelated instance changed the
  server's `serveradmin.xml`. `SERVER_ADMINS` is the declaration.

The run report records the serverconfig properties actually applied (minus the
per-run telnet secret), so a report names the world it measured.

### Safehouse owns the environment

`sb` gains `up` (start detached, block until the game port listens, exit
coded), `stage` (copy built modlets into the instance), and `render-config`
(set serverconfig properties on the instance). `scripts/sbconfig.py` is the
workspace's one serverconfig renderer and `serveradmin.xml` seeder; `sb` calls
it, and `7dtd-loadgen` calls it through `SANDBOX_ROOT`. Teardown is
`sb stop <instance>`, which matches processes by that instance's own
`SB_INSTANCE`, so a run cannot kill another instance's server.

### Suites become the input

A suite document declares provision, backend, readonly, fresh, the modlets to
stage, and a flat `server` map of serverconfig properties handed to
`sb render-config`. The orchestrator passes the declared case refs to the
client through `PLAYTEST_CASE_REFS`; `Runner` keeps only cases whose
`catalog.SUITE.CASE` ref appears there. An offline gate
(`scripts/test_suite_refs.py`) fails when a declared ref has no
implementation, and when a declared suite omits a case its Add method builds.

`fresh` is now derived and checked: a managed run must be fresh, an attach run
must not claim to be, and `readonly` requires attach. A live suite is
representable and honest.

`ref` keeps pointing at C#. JSON owns what and where; C# owns how. A JSON DSL
for driving a Unity client is not on the table.

### Mod-local playtests

A mod repo keeps its own `IScenarioProvider` and its own suite JSON beside it,
and runs `playtest_run.py --suite-file <path>`. `load_external_suite` refuses a
suite id that shadows a built-in stock-fidelity suite. Stock-fidelity suites
stay in `7dtd-playtest` only.

### Production stays alone

`7dtd-server-container` keeps its own `@TOKEN@` template and `assert_rendered`
boot check. Forcing production through the lab renderer buys nothing and risks
a boot path that is already tested. Playtest reaches it only as
`--no-server --readonly`, and never deploys, stages or restarts it.

## Consequences

- `playtest_run.py` loses `write_stock_config`, `start_stock_dedicated`,
  `_rewrite_platform_cfg`, `_atomic_write_bytes`, `_literal_replacement`,
  `fresh_save` and `wait_stock_dedicated_ready`, and stops reading
  `7dtd-loadgen/scripts/serverconfig_loadgen.xml`.
- `GAME_PROC_PATTERNS` no longer contains `7DaysToDieServer.x86_64`. A managed
  dedicated is stopped by instance name.
- `--port` and `--admin-port` are refused on a managed run: Safehouse allocates
  the instance's 5-port block, and an operator port would send the harness at a
  port the server never binds.
- `7dtd-loadgen` no longer ships `scripts/render_serverconfig.py`; its runtime
  scripts resolve `SANDBOX_ROOT` and fail by name when the sibling checkout is
  absent. The rerun-convergence gate for that renderer moved to
  `7dtd-sandbox/scripts/test_sbconfig.py`.
- Resolving a target is read-only. It used to create the instance so ports were
  known during validation, which made an offline gate calling `main()` leave a
  multi-gigabyte game copy behind. Port validation now follows `sb up`.
- Existing instances keep the ports recorded in their `instance.env`; only new
  instances get a name-derived block. An instance created before
  `SERVER_ADMINS` existed falls back to admitting its `client-<pair>` name.

## Deliberately not done

- `7dtd-realearth`, `7dtd-server-optimizer` and `7dtd-vision-review` still
  carry their own `start_dedicated_*.sh`. They work, they are not on the
  playtest path, and converting them needs a live run per repo to verify.
- The exclusivity lock still covers client and server together, so two suites
  cannot run concurrently even on instances with disjoint port blocks. With
  Safehouse owning instances the server half is already implicit in the
  instance directory; split the lock when parallel suites are actually wanted.
- Catalog suites other than `smoke` and `core` have no suite document yet.
  They are listed in `UNDECLARED_SUITES` so the choice stays explicit.
