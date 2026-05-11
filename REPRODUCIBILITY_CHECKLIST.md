# SIC-JS Toolkit v1.0.0 — Reproducibility Checklist

This checklist is provided for external reviewers, auditors, and release managers to systematically verify the integrity, completeness, and reproducibility of the SIC-JS Toolkit v1.0.0 release package.

## 1. Package Integrity

- [ ] **ZIP SHA-256 Verified:** The SHA-256 hash of the delivered zip file matches the hash provided in the delivery message.
- [ ] **Root Directory Correct:** The zip extracts to a root directory named `sic-js-toolkit-v1.0.0/`.
- [ ] **MANIFEST PASS:** Running `sha256sum -c MANIFEST.sha256` reports all files as `OK` with 0 `FAILED`.

## 2. Release Metadata & Hygiene

- [ ] **MIT LICENSE Present:** The `LICENSE` file exists and contains the formal MIT License text.
- [ ] **No LICENSE_PENDING:** The `LICENSE_PENDING.md` file has been removed.
- [ ] **VERSION 1.0.0:** The `VERSION` file contains exactly `1.0.0`.
- [ ] **README Final Status:** `README.md` reflects the final v1.0.0 status, MIT license, and Gate 7 CLOSED.
- [ ] **PACKAGE_MAP Final Status:** `PACKAGE_MAP.md` reflects the final v1.0.0 status and references `LICENSE` instead of `LICENSE_PENDING.md`.
- [ ] **No PyCache:** The package contains no `__pycache__` directories or `.pyc` files.

## 3. Execution & Testing

- [ ] **Smoke-Test PASS:** Running `bash bin/smoke-test.sh` (or `NO_TIMEOUT=1 bash bin/smoke-test.sh` if GNU timeout is unavailable) completes with `SMOKE-TEST: ALL PASS`.
- [ ] **Tests 25/25 PASS:** The internal test suite (`tests/run_tests.sh`) reports `TOTAL: 25 PASS: 25 FAIL: 0`.
- [ ] **R57 Verifier PASS:** Running `bash src/verifier/sic_verify.sh --file state/SIC_JS_STATE_R57_*.json --mode toolkit` exits with code 0 (PASS).

## 4. State & Schema Consistency

- [ ] **State Body Round Matches Filename:** The `"round"` field inside `state/SIC_JS_STATE_R55_*.json`, `R56_*.json`, and `R57_*.json` matches their respective filenames (55, 56, 57).
- [ ] **Canonical Schema Hash Unchanged:** The canonical schema (`schema/canonical/sic-js-schema-v2.0.json`) remains untouched and its hash matches the documented baseline.
- [ ] **Toolkit Schema Fork Exists:** The toolkit schema (`schema/toolkit/sic-js-schema-v2.0-toolkit.json`) is present and correctly extends the canonical schema.
- [ ] **Examples Validate:** The JSON files in `examples/` pass validation against the toolkit schema.

## 5. Governance & Boundaries

- [ ] **CLAIM_BOUNDARY.md Present:** The file exists and clearly delineates allowed vs. disallowed claims.
- [ ] **RELEASE_NOTES_v1.0.0.md Present:** The external release notes are included and accurately reflect the release scope.
- [ ] **EXTERNAL_REVIEWER_README.md Present:** The guide for external reviewers is included.
