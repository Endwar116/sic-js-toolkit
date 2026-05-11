# SIC-JS Toolkit — RELEASE STATUS

| Field | Value |
|---|---|
| **Current version** | `1.0.0` |
| **Release class** | **Final release** |
| **Release date** | 2026-05-09 |
| **Package** | `final v1.0.0` (built on R52c portability fixes) |
| **Delivery state round** | `R57` (see `state/SIC_JS_STATE_R57_*.json`) |
| **Gate 1–6 status** | PASS — evidence present in `internal/reports/` |
| **Gate 7 status** | **CLOSED — GREEN LIGHT GIVEN** (Anan, 2026-05-09) |
| **License** | **MIT** (see `LICENSE`) |
| **Public redistribution authorized** | **Yes** |

## Plain language

This is the **final release** of SIC-JS Toolkit v1.0.0, issued under the MIT License.

Gate 7 was formally granted by Anan (Protocol Seeder) on 2026-05-09. The toolkit has
passed all seven release gates, including cross-platform portability verification on
Linux and macOS (JG real-machine verification, 2026-05-09).

### Layered scope (JG framing, adopted 2026-05-09)

SIC-JS Toolkit v1.0.0 is **Layer 1** of a three-layer long-horizon AI state governance
architecture:

| Layer | Name | Description | Status |
|---|---|---|---|
| **Layer 1** | Toolkit (this package) | Schema, writer, verifier, manifest, examples, docs | **v1.0.0 — RELEASED** |
| Layer 2 | Runtime mount guard | Pre-send gate, output guardrail, round continuity checker, fail-closed, human-readable aftertext | Future work |
| Layer 3 | Replay / witness ledger | Cross-round, cross-model, cross-agent replay, audit, diff, fork | Future work |

### Claim boundary

Accurate claims for v1.0.0: "SIC-JS Toolkit v1.0.0 is formally released under MIT license." "It is the first public technical layer for long-horizon AI state governance." "25/25 reproducibility tests pass on a clean install (Linux and macOS verified)."

Claims that remain **inaccurate** and must not be made: ~~solves all runtime drift~~ ~~guarantees live multi-agent collaboration continuity~~ ~~production-certified~~ ~~formal external standard~~ ~~solves direction lock-in (E6 experiment incomplete)~~

## Gate-by-gate

| Gate | Description | Status | Evidence |
|---|---|---|---|
| Gate 1 | Schema integrity (canonical hash, toolkit fork boundary) | **PASS** | `internal/reports/P1A_HASH_RECORD.md`, `internal/reports/P1A_POST_CHANGE_REPORT.md` |
| Gate 2 | Component implementation (validator, writer, verifier) | **PASS** | `internal/reports/P1B_POST_CHANGE_REPORT.md` |
| Gate 3 | Test reproducibility (per-test timeout, portable Linux/macOS) | **PASS** | `internal/reports/P2_POST_CHANGE_REPORT.md`, `internal/reports/CHIEF_ENGINEER_R52B_AUDIT.md`, `internal/reports/R52C_PORTABILITY_REPORT.md`, `logs/R52C_RUN_TESTS_FULL_OUTPUT.log`, `logs/R52C_MACOS_NO_TIMEOUT_SIM.log`, `logs/R52C_NO_TIMEOUT_FALLBACK.log` |
| Gate 4 | User-facing documentation (README, examples, migration, governance) | **PASS** | `internal/reports/P3A_POST_CHANGE_REPORT.md` |
| Gate 5 | Backward compatibility policy | **PASS** | `internal/reports/P4_POST_CHANGE_REPORT.md`, `docs/backward-compatibility.md` |
| Gate 6 | Release checklist + changelog + version | **PASS** | `internal/reports/P5A_POST_CHANGE_REPORT.md`, `RELEASE_CHECKLIST_v1.0.md`, `CHANGELOG.md`, `VERSION` |
| Gate 7 | Owner final release ruling | **CLOSED — GREEN LIGHT** | Anan ruling 2026-05-09: MIT license, VERSION 1.0.0, final release |

## Package history

| Package | Round | Key change |
|---|---|---|
| R52a | R53 | Lao Xiang review patches |
| R52b | R54 | JG macOS reproducibility test; 24x exit-127 cascade identified |
| R52c | R55 | Portable timeout resolver + functional probe; macOS fail-closed exit-2 |
| **v1.0.0 (final)** | **R57** | **MIT LICENSE, VERSION 1.0.0, state round consistency, Gate 7 CLOSED** |

## Open items (non-blocking)

| Item | Description | Owner |
|---|---|---|
| Homebrew gtimeout branch | Real-machine macOS verification with `gtimeout` via Homebrew | JG |
| Layer 2 runtime mount guard | Pre-send gate and output guardrail implementation | Future |
| Layer 3 replay ledger | Cross-agent replay and audit infrastructure | Future |
| JG paper / corpus freeze | Case study paper based on R52B/R52C engineering sequence | JG |
