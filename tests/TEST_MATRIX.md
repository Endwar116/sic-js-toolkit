# SIC-JS Toolkit Test Matrix
# Version: 1.0 / 2026-05-08
# Authority: 咩咩 (Manus AI) — F1 P2

---

## Overview

This matrix documents all 20 P1B test cases plus the 5 baseline tests in `run_tests.sh`.

**P1B Total: 20 tests** (run via `python3 tests/run_p1b_tests.py`)  
**Baseline Total: 25 tests** (run via `bash tests/run_tests.sh`)

---

## P1B Test Cases

### Writer Tests (W1–W6)

These tests verify that `src/writer/sic_write.py` correctly produces SIC-JS JSON with the right `upstream_type` and `upstream` values.

| Test Name | Input | Expected `upstream_type` | Expected `upstream` | Expected Exit | Pass Condition |
|---|---|---|---|---|---|
| W1_none_null | `--upstream-type none --upstream null` | `none` | `null` | 0 | Writer exits 0, output has `upstream_type=none` |
| W2_crypto_hex | `--upstream-type cryptographic --upstream a3f8b2c1d4e5f607` | `cryptographic` | `a3f8b2c1d4e5f607` | 0 | Writer exits 0, output has `upstream_type=cryptographic` |
| W3_file_label | `--upstream-type file --upstream XIED_v2.json` | `file` | `XIED_v2.json` | 0 | Writer exits 0, output has `upstream_type=file` |
| W4_auto_hex | `--upstream a3f8b2c1d4e5f607` (no `--upstream-type`) | `cryptographic` (auto-derived) | `a3f8b2c1d4e5f607` | 0 | Writer auto-derives `cryptographic` from 16-char hex |
| W5_auto_label | `--upstream XIED_v2.json` (no `--upstream-type`) | `file` (auto-derived) | `XIED_v2.json` | 0 | Writer auto-derives `file` from non-hex string |
| W6_auto_null | `--upstream null` (no `--upstream-type`) | `none` (auto-derived) | `null` | 0 | Writer auto-derives `none` from null upstream |

### Verifier Tests (V1–V10)

These tests verify that `src/validator/validate_skeleton_v2.py` correctly accepts valid fixtures and rejects invalid ones.

| Test Name | Fixture | `upstream_type` | `upstream` | Expected Exit | Pass Condition |
|---|---|---|---|---|---|
| V1_none_null | `V1_none_null.json` | `none` | `null` | 0 | Valid: none/null combination |
| V2_crypto_hex | `V2_crypto_hex.json` | `cryptographic` | `a3f8b2c1d4e5f607` | 0 | Valid: cryptographic/hex combination |
| V3_file_label | `V3_file_label.json` | `file` | `XIED_v2.json` | 0 | Valid: file/label combination |
| V4_none_nonnull | `V4_none_nonnull.json` | `none` | `somevalue` | 1 | Invalid: none requires null upstream |
| V5_crypto_null | `V5_crypto_null.json` | `cryptographic` | `null` | 1 | Invalid: cryptographic requires non-null upstream |
| V6_crypto_label | `V6_crypto_label.json` | `cryptographic` | `XIED_v2.json` | 1 | Invalid: cryptographic requires 16-char hex |
| V7_file_null | `V7_file_null.json` | `file` | `null` | 1 | Invalid: file requires non-null upstream |
| V8_file_hex | `V8_file_hex.json` | `file` | `a3f8b2c1d4e5f607` | 1 | Invalid: file upstream must not look like hex hash |
| V9_file_traversal | `V9_file_traversal.json` | `file` | `../etc/passwd` | 5 | UNSAFE_UPSTREAM: path traversal rejected |
| V10_invalid_datetime | `V10_invalid_datetime.json` | `file` | `valid.json` | 1 | Invalid: `created_at` not ISO 8601 format |

### Consistency Tests (C1–C3)

These tests verify that the Writer and Verifier agree — output from Writer must pass Verifier.

| Test Name | Description | Expected Exit | Pass Condition |
|---|---|---|---|
| C1_writer_to_verifier | Writer W2 output (cryptographic/hex) → Verifier toolkit mode | 0 | Writer output passes Verifier |
| C2_auto_derive_consistent | Writer auto-derive (hex input) → Verifier toolkit mode | 0 | Auto-derived type passes Verifier |
| C3_all_types_consistent | Writer W1/W2/W3 each → Verifier agrees on all three types | 0 | All three type combinations pass Verifier |

### Legacy Test (L1)

| Test Name | Fixture | Mode | Expected Exit | Pass Condition |
|---|---|---|---|---|
| L1_legacy_toolkit_mode | `L1_legacy.json` (no `upstream_type`) | toolkit | 6 | LEGACY_FORMAT_DETECTED: missing upstream_type in toolkit mode |

---

## Exit Code Reference

| Exit Code | Meaning |
|---|---|
| 0 | PASS — validation successful |
| 1 | VALIDATION_FAILED — schema or semantic rule violation |
| 2 | INVALID_USAGE — conflicting CLI arguments |
| 3 | INPUT_NOT_FOUND — file not found |
| 4 | SCHEMA_NOT_FOUND — schema file not found |
| 5 | UNSAFE_UPSTREAM — path traversal or security violation |
| 6 | LEGACY_FORMAT_DETECTED — missing `upstream_type` in toolkit mode |
| 7 | INTERNAL_ERROR |

---

## How to Run

```bash
# From toolkit root
python3 tests/run_p1b_tests.py    # P1B suite (20 tests)
bash tests/run_tests.sh           # Baseline suite (25 tests)
```

Both runners use relative paths derived from `__file__` / `${BASH_SOURCE[0]}` — no hardcoded paths.
