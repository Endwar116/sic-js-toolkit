# Changelog

All notable changes to the SIC-JS Toolkit will be documented in this file.

## [1.0.0] - 2026-05-09 (Final Release — Gate 7 CLOSED)

**Package:** final v1.0.0 (built on R52c portability fixes)  
**Delivery state round:** R57  
**Gate 7:** CLOSED — GREEN LIGHT GIVEN by Anan (Protocol Seeder), 2026-05-09

### Changed (final release packaging)
- **MIT License**: `LICENSE_PENDING.md` replaced by formal MIT `LICENSE`.
- **VERSION**: Updated from `1.0.0-rc.1` to `1.0.0`.
- **RELEASE_STATUS.md**: Updated to reflect final release status, Gate 7 CLOSED, layered scope (JG framing: Layer 1 toolkit / Layer 2 runtime guard / Layer 3 replay ledger), and claim boundary.
- **CHANGELOG.md**: This entry.
- **MANIFEST.sha256**: Regenerated to cover all final changes.
- **State round consistency**: R57 state body round, file name, message text, and ledger HEAD are consistent (fixes R55 round mismatch identified by Lao Xiang).

### Open items (non-blocking)
- Homebrew gtimeout branch: real-machine macOS verification with `gtimeout` via Homebrew (JG).
- Layer 2 runtime mount guard: pre-send gate and output guardrail (future work).
- Layer 3 replay ledger: cross-agent replay and audit infrastructure (future work).
- JG paper / corpus freeze: case study paper based on R52B/R52C engineering sequence.

## [1.0.0-rc.1] - 2026-05-09 (Release Candidate, R52c iteration)

**Package candidate:** R52c (supersedes R52b)  
**Delivery state round:** R55

### Fixed (JG low-reasoning macOS engineer reproducibility test on R52b)
- `tests/run_tests.sh` now uses a portable timeout resolver: prefers `timeout`,
  falls back to `gtimeout` (Homebrew coreutils on macOS), and exits with code 2
  plus an actionable error if neither is available. **No more 24x exit-127
  cascade on macOS without coreutils.**
- New `NO_TIMEOUT=1` opt-in fallback for air-gapped local evaluation; prints four
  `WARNING` lines and runs without per-test timeout. Explicitly marked as **not
  valid evidence for official reproducibility**.
- `bin/smoke-test.sh` runs preflight checks (`python3`, `pip`, `sha256sum`,
  `timeout`/`gtimeout`/`NO_TIMEOUT`) **before** creating a venv. Missing
  prerequisites print actionable instructions and exit with code 2 instead of
  producing a confusing failure cascade later.
- `timeout` invocation now includes `--kill-after=5s` so a stuck test cannot
  outlive its timeout indefinitely.
- `RELEASE_STATUS.md` Gate 3 evidence corrected: was pointing to non-existent
  `R52A_RUN_TESTS_FULL_OUTPUT.log`; now points to `R52C_RUN_TESTS_FULL_OUTPUT.log`
  plus macOS / NO_TIMEOUT simulation logs and `R52C_PORTABILITY_REPORT.md`.
- Stale `R52B_MANIFEST_CHECK.log` (carried internal-restructuring noise) replaced
  with a fresh `R52C_MANIFEST_CHECK.log` produced from a clean unzip + clean venv.
  Older logs moved to `internal/superseded_logs/` and explicitly labeled
  `SUPERSEDED`.

### Added (R52c documentation hardening)
- `README.md` **Platform notes** section: Linux / macOS / Network-PyPI /
  Manual-core-tool-verification subsections.
- `QUICKSTART.md` **On macOS** section + updated prerequisites + manual-fallback
  via `pip install jsonschema` for offline environments.
- `TROUBLESHOOTING.md` new section 3a (macOS no-timeout) and 3b
  (`sha256sum` missing on macOS) and section 8 (`pip install` failures).
- `internal/reports/R52C_PORTABILITY_REPORT.md` documents the portable-timeout
  design, validation matrix (Linux native, NO_TIMEOUT fallback, simulated macOS
  no-timeout), and what evidence is acceptable for Gate 3.

## [1.0.0-rc.1] - 2026-05-08 (Release Candidate, R52b iteration — superseded by R52c)

**Package candidate:** R52b (supersedes R52a)  
**Delivery state round:** R54

### Fixed (Lao Xiang R52a re-review)
- `__pycache__/*.pyc` no longer leaks into the release zip. Added `.gitignore`,
  exported `PYTHONDONTWRITEBYTECODE=1` in test runner, explicit cleanup before manifest.
- `tests/run_tests.sh` per-test timeout raised from 10s to 30s default; cold-start
  and slow-CI environments no longer falsely trigger TIMEOUT.
- Stale `R52A_MANIFEST_CHECK.log` (carried 14 stale FAILED entries from before the
  `internal/` restructuring) removed; replaced with `R52B_MANIFEST_CHECK.log`.
- `R52a` / `R53` naming overlap clarified: `RELEASE_STATUS.md` and `README.md` now
  explicitly document "package candidate vs delivery state round".

### Added (Chief Engineer R52b additional fixes)
- `bin/smoke-test.sh` — one-command end-to-end verification (venv + install + tests +
  manifest + state verify) for any stranger to confirm the package in their environment.
- `.gitignore` — standard Python ignore set so cloning + running tests does not dirty
  the working tree.
- `README.md` and `QUICKSTART.md` no longer hardcode the R52a zip filename; use
  `<delivered-zip>.zip` placeholder.
- `TROUBLESHOOTING.md` updated to reflect 30s timeout and reference timing baseline.

### Internal
- `internal/reports/CHIEF_ENGINEER_R52B_AUDIT.md` documents Lao Xiang's 7 requested
  fixes plus 5 Chief-Engineer-identified systemic vulnerabilities.

## [1.0.0-rc.1] - 2026-05-08 (Release Candidate, R52a iteration — superseded)

### Added
- **Toolkit Schema Fork**: Added `schema/toolkit/sic-js-schema-v2.0-toolkit.json` with the `upstream_type` extension.
- **Writer Auto-Derive**: `sic_write.py` now automatically derives `upstream_type` (`cryptographic`, `file`, or `none`) if not explicitly provided.
- **Extended Test Suite**: Added 20 new test cases (W1-W6, V1-V10, C1-C3, L1) covering writer, verifier, consistency, and legacy formats.
- **Python Test Runner**: Added `tests/run_p1b_tests.py` for cross-platform test execution without hardcoded paths.
- **Documentation**:
  - `docs/governance.md`: Explains the boundary between canonical schema and toolkit fork.
  - `docs/migration-guide.md`: Guide for migrating legacy formats.
  - `docs/backward-compatibility.md`: Details on `LEGACY_FORMAT_DETECTED` (exit 6).
  - `tests/TEST_MATRIX.md`: Comprehensive documentation of all test cases.
- **Examples**: Added `examples/` directory with valid JSON files for all three `upstream_type` values.

### Changed
- **Validator**: `validate_skeleton_v2.py` now supports `--mode canonical` (strict) and `--mode toolkit` (requires `upstream_type`).
- **Verifier**: `sic_verify.sh` now delegates entirely to the validator.
- **README**: Updated with Quick Start instructions and explicit "What this is NOT" architectural boundaries.

### Security
- **Path Traversal Protection**: Validator now correctly exits with code 5 (`UNSAFE_UPSTREAM`) when path traversal attempts are detected in `upstream_type=file`.
- **Hash Lock**: Canonical schema integrity is guarded by `src/utils/hash_lock.py` (exit 9 `CANONICAL_TAMPERED`).

## [0.1.0] - 2026-05-02

### Added
- Initial F0 scaffolding release.
- Canonical schema `sic-js-schema-v2.0.json` (hash: `efb2947b...`).
- Basic validator, writer, and verifier implementations.
- Baseline test suite (`tests/run_tests.sh`).
