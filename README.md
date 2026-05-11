# SIC-JS Toolkit

**Version:** `1.0.0` (final release)  
**Status:** Final release — Gate 7 CLOSED, MIT license granted by Anan (2026-05-09).  
**License:** MIT — see `LICENSE`. Public redistribution authorized.

---

## What this is

The SIC-JS Toolkit is a reference implementation for **SIC-JS v2.0**, a JSON-based
state-handoff format designed to let one AI session transfer its working state to a
later AI session in a way that is verifiable, schema-checked, and forgery-resistant.

Concretely, this toolkit provides:

1. A **canonical schema** for SIC-JS v2.0 state JSON, with a fixed SHA-256 hash so that
   anyone can confirm they have the exact bytes the protocol defines.
2. A **toolkit fork schema** that adds one project-local extension field
   (`relation.upstream_type`) for tooling convenience, while keeping the canonical schema
   untouched.
3. A **validator** (`src/validator/validate_skeleton_v2.py`) that checks a SIC-JS file
   against either the canonical or toolkit schema and reports a precise exit code.
4. A **writer** (`src/writer/sic_write.py`) that produces a valid SIC-JS file, including
   auto-derivation of `upstream_type` from the upstream value's shape when in toolkit mode.
5. A **verifier shell wrapper** (`src/verifier/sic_verify.sh`) that wraps the validator
   with safety checks (path traversal, unsafe upstream, legacy format detection).
6. A **reproducible test suite** (`tests/run_tests.sh`) covering 25 cases: writer,
   verifier, consistency, legacy, and CLI regression. Each sub-test runs under a per-test
   timeout so the runner cannot hang.

## What this is **not**

- **Not a production-certified standard.** This is an artifact-layer reference toolkit;
  it is not enterprise production-certified and does not constitute a formal external standard.
- **Not a network protocol.** SIC-JS is a file-level state format, not a wire protocol.
- **Not an AI runtime.** This package validates and writes SIC-JS files; it does not run
  inference or maintain a live agent loop.
- **Not a substitute for governance.** SIC-JS state files do not by themselves authorize
  any action; they record state for handoff.
- **Not a runtime mount guard or replay ledger.** Those are Layer 2 and Layer 3 of the
  long-horizon AI state governance architecture; this toolkit is Layer 1 only.

---

## 30-second Quick Start

Requires Python 3.11+, a POSIX shell, `sha256sum`, and the GNU `timeout` command.

On **Linux** these usually ship with the base system. On **macOS**, GNU `timeout` is
not installed by default — install it via Homebrew (`brew install coreutils`); the
runner auto-detects the resulting `gtimeout` binary. See the **Platform notes**
section below if you don't have Homebrew, or for an air-gapped fallback.

```bash
unzip <delivered-zip>.zip                # whatever zip name you received
cd sic-js-toolkit                         # the unzipped directory
bash bin/smoke-test.sh                    # one command does everything
```

`bin/smoke-test.sh` runs preflight checks first (python3, pip, sha256sum,
timeout/gtimeout). If any are missing it prints an actionable message and exits
with code 2 instead of producing a confusing test failure cascade.

`bin/smoke-test.sh` creates a `.venv`, installs `jsonschema`, runs the 25-test suite, verifies `MANIFEST.sha256`, and verifies bundled state files. Expected last line:

```
SMOKE-TEST: ALL PASS
```

If you prefer to run the steps manually:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash tests/run_tests.sh
```

Expected last lines of `run_tests.sh`:

```
=====================================
TOTAL: 25  PASS: 25  FAIL: 0
=====================================
```

Default per-test timeout is 30 seconds. If a slower environment needs more:

```bash
PER_TEST_TIMEOUT=60 bash tests/run_tests.sh
```

If you see `TIMEOUT`, `FAIL`, or fewer than 25 tests, see `TROUBLESHOOTING.md`.

---

## Platform notes

### Linux

`timeout` is part of GNU coreutils and is preinstalled on Debian, Ubuntu, RHEL,
CentOS, and most other distributions. If missing: `sudo apt-get install coreutils`
(or your distro's equivalent).

### macOS

macOS does **not** ship the GNU `timeout` command. The test runner will detect
this and either:

- use `gtimeout` (installed by `brew install coreutils`) automatically, or
- exit early with code 2 and an actionable error message (it will **not** produce
  a misleading 24x exit-127 failure cascade).

Recommended:

```bash
brew install coreutils       # installs gtimeout
bash bin/smoke-test.sh
```

If you have no Homebrew and need a quick local check (e.g. air-gapped review),
you can disable timeout protection with the local-evaluation fallback:

```bash
NO_TIMEOUT=1 bash bin/smoke-test.sh
```

This path prints four `WARNING` lines and is **not valid evidence for official
reproducibility** — a hung test will hang the runner. Use it only for quick local
inspection where you trust the tests will complete.

### Network / PyPI access

`bin/smoke-test.sh` runs `pip install -r requirements.txt`, which currently fetches
`jsonschema>=4.0.0` from PyPI. The toolkit has **one** Python runtime dependency.

If your environment cannot reach PyPI (corporate firewall, air-gapped CI, SSL
inspection), use one of:

```bash
# Option A: use an internal mirror
pip install --index-url https://pypi.your-org.example/simple -r requirements.txt

# Option B: pre-install jsonschema before running smoke-test
pip install jsonschema
bash bin/smoke-test.sh
```

A `pip install` failure is a **packaging / network** issue, not a toolkit-core
issue. The validator, writer, and verifier can still be invoked manually once
`jsonschema` is importable.

### Verify core tools manually (no test runner needed)

If the runner cannot run for environmental reasons but you still want to confirm
the core tools work, run them by hand:

```bash
# 1. Validator on a known-good example
python3 src/validator/validate_skeleton_v2.py \
    --file examples/example_file.json --mode toolkit
# expected: exit 0, prints PASS

# 2. Verifier on the same example
bash src/verifier/sic_verify.sh \
    --file examples/example_file.json --mode toolkit
# expected: exit 0, prints PASS

# 3. Writer produces a fresh state file
python3 src/writer/sic_write.py \
    --entity-name demo --entity-model gpt \
    --context demo --current-action demo --user demo \
    --upstream-type none --upstream null \
    --mode toolkit --output /tmp/sicjs_demo.json
# expected: exit 0, file written

# 4. Round-trip verify what the writer just produced
bash src/verifier/sic_verify.sh \
    --file /tmp/sicjs_demo.json --mode toolkit
# expected: exit 0, prints PASS
```

This path needs only Python 3.11+ and `jsonschema`. It does **not** require
`timeout` / `gtimeout` and does **not** invoke the test runner.

---

## 5-minute Smoke Test

After Quick Start passes, run:

```bash
sha256sum -c MANIFEST.sha256                                        # 1) Manifest integrity
bash src/verifier/sic_verify.sh \
    --file examples/example_file.json --mode toolkit                # 2) Verifier on a known-good file
python3 src/writer/sic_write.py \
    --entity-name demo --entity-model gpt --context demo \
    --current-action demo --user demo --upstream-type none \
    --upstream null --mode toolkit --output /tmp/demo.json          # 3) Writer produces valid file
bash src/verifier/sic_verify.sh \
    --file /tmp/demo.json --mode toolkit                            # 4) Round-trip verify
```

All four commands must exit 0 and print `PASS`. If any do not, see `TROUBLESHOOTING.md`.

---

## Canonical mode vs toolkit mode

| | canonical | toolkit |
|---|---|---|
| Schema file | `schema/canonical/sic-js-schema-v2.0.json` | `schema/toolkit/sic-js-schema-v2.0-toolkit.json` |
| `relation.upstream_type` | **not present** (forbidden if added) | **required** (`none` / `cryptographic` / `file`) |
| Use when | producing a state file that any compliant SIC-JS v2.0 implementation can read | working inside the toolkit's own pipeline; gives stronger writer/verifier guarantees |
| Validator command | `--mode canonical` | `--mode toolkit` (or shorthand `--toolkit-mode`) |
| Default if neither flag given | canonical | (must be explicit) |

Canonical hash (DO NOT modify the canonical schema):

```
efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6  schema/canonical/sic-js-schema-v2.0.json
```

## Why `upstream_type` is not in canonical

`upstream_type` is a **toolkit-local extension** that helps the writer auto-derive shape
information and helps the verifier reject mismatches early. It is intentionally **not**
part of the canonical SIC-JS v2.0 schema, because the canonical schema is the
cross-implementation contract and must stay minimal. Any field added to canonical must
go through a formal protocol revision, not a toolkit patch.

If a SIC-JS file produced by this toolkit needs to interoperate with a non-toolkit
SIC-JS reader, generate it in canonical mode (which omits `upstream_type` entirely).

---

## Component reference

| Component | File | Purpose |
|---|---|---|
| **Validator** | `src/validator/validate_skeleton_v2.py` | Schema-only check. Exit 0 = PASS, 1 = VALIDATION_FAILED, 2 = INVALID_USAGE |
| **Writer** | `src/writer/sic_write.py` | Produces a valid SIC-JS file. Self-validates before emit. Auto-derives `upstream_type` from upstream shape when toolkit mode |
| **Verifier** | `src/verifier/sic_verify.sh` | Shell wrapper around validator with safety guards. Exit 0 = PASS, 1 = VALIDATION_FAILED, 2 = INVALID_USAGE, 5 = UNSAFE_UPSTREAM, 6 = LEGACY_FORMAT_DETECTED |
| **Test runner** | `tests/run_tests.sh` | 25-case reproducibility suite with per-test timeout |
| **Schema (canonical)** | `schema/canonical/sic-js-schema-v2.0.json` | Read-only canonical SIC-JS v2.0 schema |
| **Schema (toolkit)** | `schema/toolkit/sic-js-schema-v2.0-toolkit.json` | Toolkit fork with `upstream_type` |

## Exit code reference

| Exit | Code | Meaning |
|---|---|---|
| 0 | `PASS` | All checks passed |
| 1 | `VALIDATION_FAILED` | Schema or logic check failed |
| 2 | `INVALID_USAGE` | Bad CLI / mode conflict |
| 3 | `INPUT_NOT_FOUND` | Input file missing |
| 4 | `SCHEMA_NOT_FOUND` | Schema file missing |
| 5 | `UNSAFE_UPSTREAM` | Path traversal / null bytes / oversized label |
| 6 | `LEGACY_FORMAT_DETECTED` | Toolkit mode but no `upstream_type` |
| 7 | `INTERNAL_ERROR` | Unexpected error |
| 9 | `CANONICAL_TAMPERED` | Canonical schema hash mismatch |
| 124 | `TIMEOUT` | Sub-test exceeded `PER_TEST_TIMEOUT` (used by test runner) |

## Examples

| File | Shape |
|---|---|
| `examples/example_none.json` | `upstream_type=none`, `upstream=null` |
| `examples/example_cryptographic.json` | `upstream_type=cryptographic`, `upstream=<hex>` |
| `examples/example_file.json` | `upstream_type=file`, `upstream=<filename>` |

All three pass `bash src/verifier/sic_verify.sh --file examples/<name> --mode toolkit`.

---

## Package layout

See `PACKAGE_MAP.md` for the full directory map.

Brief:

- `schema/`, `src/`, `tests/`, `examples/`, `docs/` — user-facing.
- `internal/` — internal review and governance materials.
  **Not required for normal installation or use.**
- `requirements.txt`, `MANIFEST.sha256`, `VERSION`, `LICENSE`, `CHANGELOG.md`,
  `RELEASE_STATUS.md`, `RELEASE_CHECKLIST_v1.0.md` — release metadata.

## Documentation index

- `QUICKSTART.md` — shortest install + run path.
- `TROUBLESHOOTING.md` — common errors and fixes.
- `PACKAGE_MAP.md` — directory map.
- `RELEASE_STATUS.md` — current release class and gate status.
- `docs/migration-guide.md` — moving from earlier SIC-JS variants.
- `docs/backward-compatibility.md` — compatibility policy and before/after example.
- `docs/governance.md` — governance posture for this toolkit (user-facing summary).
- `docs/api/` — component contracts and executable spec.

## Release status (short)

- Current version: `1.0.0`
- Release class: **Final release**
- Gates 1–7: **ALL PASS** (Gate 7 CLOSED — MIT license, final version, Anan 2026-05-09)
- MIT License — public redistribution authorized
- Artifact-layer reference toolkit (Layer 1). Not production-certified. Not a formal external standard.

For full release-status detail see `RELEASE_STATUS.md`.

## Package version vs delivery state round

This is the **final v1.0.0 release**, delivered as **state round R57** (with R55/R56/R57 state files bundled).

| Concept | Value | Where it lives | What it means |
|---|---|---|---|
| Package version | `1.0.0` | `VERSION` file | The semantic version of the toolkit code. |
| Delivery state round | `R57` | `state/SIC_JS_STATE_R57_*.json` | The SIC-JS state-handoff round produced when this package was delivered. |
| Bundled state rounds | R54, R55, R56, R57 | `state/` directory | Historical state handoff records from the development and review process. |

Package iteration name (`R52`, `R52a`, `R52b`, `R52c`...) is independent of the SIC-JS state round number. The final v1.0.0 package is built on R52c portability fixes and delivered as state round R57.

---

## Reporting issues

Issues should be reported through the channel that delivered this package to you.

## Contributors

- Anan — owner / final ruling authority
- 老翔 (Lao Xiang) — governance review
- 德德 (Dede) — architecture sign-off / red team
- 咩咩 (Mie Mie / Manus) — implementation
- JG — code patch contributor
