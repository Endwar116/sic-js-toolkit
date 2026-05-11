# R52C Portability Report

**Package candidate:** R52c · **State round:** R55 · **Date:** 2026-05-09  
**Author:** Mie Mie (Manus AI), in Chief Engineer mode  
**Driver:** JG low-reasoning macOS engineer reproducibility test on R52b

---

## 1. The original failure

JG ran the R52b smoke-test on macOS (no Homebrew coreutils). Result:

```
TOTAL: 24  PASS:  0  FAIL: 24
```

All 24 tests showed `FAIL (exit 127)`. Root cause: `tests/run_tests.sh` invoked the
GNU `timeout` command unconditionally. macOS does not ship `timeout` by default;
the shell could not find the binary, so each invocation of the form

```
timeout 30 python3 src/validator/validate_skeleton_v2.py ...
```

failed with `command not found` (exit 127) before the actual test command was ever
executed. The 24-test cascade was a misleading symptom; the real failure was
environmental and detected only after every single sub-test had already "failed".

This is not a toolkit-core defect (the validator/writer/verifier worked fine when
invoked directly), but it is a release-blocker: a release candidate that prints
`24x FAIL` on a supported reviewer platform is not shippable.

---

## 2. The fix: portable timeout resolver (with functional probe, R52c-final)

`tests/run_tests.sh` now contains a `_resolve_timeout` function that runs once at
the top of the script:

```bash
_resolve_timeout() {
    if [ "${NO_TIMEOUT:-0}" = "1" ]; then
        TIMEOUT_BIN=""    # explicit opt-out
        return 0
    fi
    if command -v timeout >/dev/null 2>&1; then
        TIMEOUT_BIN="timeout"
    elif command -v gtimeout >/dev/null 2>&1; then
        TIMEOUT_BIN="gtimeout"
    else
        echo "[runner] ERROR: Neither timeout nor gtimeout command is available."
        echo "[runner]   Linux: install GNU coreutils (sudo apt-get install coreutils)."
        echo "[runner]   macOS: brew install coreutils  (provides gtimeout)."
        echo "[runner]   Air-gapped: re-run with NO_TIMEOUT=1 (local evaluation only)."
        echo "[runner]   This is an environment problem, NOT a toolkit-core defect."
        exit 2
    fi
}
```

Each test invocation now goes through a `run_with_timeout` helper that uses
`$TIMEOUT_CMD --kill-after=5s "$PER_TEST_TIMEOUT" "$@"` if `TIMEOUT_CMD` is set,
or runs the command directly if `NO_TIMEOUT=1`. The `--kill-after=5s` clause
ensures a stuck test cannot survive past `PER_TEST_TIMEOUT + 5s`.

`bin/smoke-test.sh` runs the same preflight before creating a venv, so the
"missing prerequisite" message appears immediately, not after a 30-second venv
creation step.

### 2.1 Functional probe (added in R52c-final after own dog-fooding)

During R52c self-dog-fooding the macOS-no-timeout simulation, the first
implementation of the resolver used only `command -v` to decide whether
`timeout` was usable. That allowed a *non-functional* binary named `timeout`
(in our test, a symlink to `/bin/false`) to be selected, after which every
sub-test ran via that broken binary and exited with a non-GNU-timeout error
code — the same misleading 24x cascade R52c was supposed to eliminate.

Fix: each candidate is now subject to a one-shot **functional probe** before
it is accepted as the timeout backend:

```bash
_probe_timeout() {
    local cand="$1"
    command -v "$cand" >/dev/null 2>&1 || return 1
    "$cand" 1 true >/dev/null 2>&1   # GNU timeout returns 0 here
}
```

If both `timeout` and `gtimeout` fail this probe, the runner takes the
"actionable exit-2" branch, exactly as if neither binary existed. The same
probe was added to `bin/smoke-test.sh`'s preflight so the runner and the
preflight stay consistent.

This catches three real-world scenarios that `command -v` alone cannot:

1. macOS systems where a user (or another tool) created a stub `timeout` that
   does not implement the GNU CLI.
2. Container/CI images where `timeout` exists but is part of an alternative
   userland (busybox in some narrow modes can mis-handle the `<seconds>`
   form) and reliably non-zero on the probe.
3. PATH manipulation in test harnesses (this report itself was caught this
   way during dog-fooding).

---

## 3. Validation matrix

| Scenario | How it was simulated | Expected behavior | Observed |
|---|---|---|---|
| Linux native (`timeout` present) | Default `/tmp/r52c_smoke` clean unzip + venv | 25/25 PASS in ~4s | **PASS** — `logs/R52C_RUN_TESTS_FULL_OUTPUT.log` |
| `NO_TIMEOUT=1` fallback | `NO_TIMEOUT=1 bash bin/smoke-test.sh` | 4 WARNING lines + 25/25 PASS | **PASS** — `logs/R52C_NO_TIMEOUT_FALLBACK.log` |
| macOS without coreutils | `env -i PATH=$WRAPDIR:/usr/bin:/bin` where `$WRAPDIR` shadows `timeout` and `gtimeout` to be absent | exit 2 + actionable error message | **PASS** (exit 2 observed) — `logs/R52C_MACOS_NO_TIMEOUT_SIM.log` |
| macOS with coreutils | Cannot simulate without a macOS host; relies on Homebrew + `gtimeout` resolver branch | runner uses `gtimeout`, 25/25 PASS | **DESIGNED, not yet hardware-verified — flagged in Open Items** |

The first three scenarios are fully reproducible from the package itself. The
fourth is a reasoned design claim: the resolver branches to `gtimeout` if and
only if `command -v gtimeout` succeeds, and `gtimeout` is the same binary as
GNU `timeout`. The risk of regression on this path is low because the call
shape is identical.

---

## 4. What "Gate 3 evidence" means now

Gate 3 in `RELEASE_STATUS.md` requires "Test reproducibility (per-test timeout,
no hang, portable across Linux/macOS)". For the gate to be considered prepared,
all of the following must be true:

1. `bash tests/run_tests.sh` on Linux with GNU coreutils prints
   `TOTAL: 25  PASS: 25  FAIL: 0` in under one minute. **(verified, see
   `logs/R52C_RUN_TESTS_FULL_OUTPUT.log`)**
2. `NO_TIMEOUT=1 bash tests/run_tests.sh` produces the same `TOTAL: 25  PASS: 25
   FAIL: 0` line, with four `WARNING` lines preceding it. **(verified, see
   `logs/R52C_NO_TIMEOUT_FALLBACK.log`)**
3. On a macOS-like environment where neither `timeout` nor `gtimeout` exists,
   `bash tests/run_tests.sh` exits with code 2 and prints an actionable error,
   instead of producing a misleading test-failure cascade. **(verified via
   PATH-shadow simulation, see `logs/R52C_MACOS_NO_TIMEOUT_SIM.log`)**
4. `MANIFEST.sha256` covers all shipped files and produces 0 FAILED on a clean
   unzip. **(verified, see `logs/R52C_MANIFEST_CHECK.log`)**

Items 1–4 are covered by R52c. Item 5 (real macOS hardware with Homebrew
`gtimeout`) is **not** covered by R52c because the build environment is Linux.
This is documented as an Open Item below; the design path is sound but only
becomes "verified" when a macOS reviewer reports `gtimeout` was auto-detected
and 25/25 PASS was observed.

---

## 5. What `NO_TIMEOUT=1` is and is not

`NO_TIMEOUT=1` is a deliberate escape hatch for one specific situation: a
reviewer wants to confirm the toolkit's correctness on a host where they cannot
install GNU `timeout` (corporate macOS without Homebrew, an air-gapped review
machine, an OS image they cannot modify).

It is **not**:

- A way to silence test failures.
- A way to ship "passing" evidence in a Gate 3 submission.
- The default path for any environment that has `timeout` or `gtimeout`.

The runner prints four explicit `WARNING` lines whenever this path is taken,
both to the terminal and to any captured log, so a downstream reviewer can
immediately see that the run was without per-test timeout protection.

---

## 6. Open Items for downstream

| Item | Status | Owner | Notes |
|---|---|---|---|
| Real macOS hardware verification (Homebrew `gtimeout` branch) | **Pending** | A future reviewer | Runner code is identical to the Linux branch on this path; risk of regression is low. |
| Windows / WSL portability | Out of scope for `1.0.0-rc.1` | — | Documented as out of scope in `README.md`. |
| Replace `timeout` with a Python-native per-test wrapper | Considered, deferred | Mie Mie | A pure-Python wrapper would remove the OS dependency entirely, but introduces complexity (signal handling, subprocess teardown). Deferred to post-`1.0.0` if cross-OS friction warrants. |

---

## 7. Self-check vs Acceptance Bar

| Bar | Status |
|---|---|
| `install_path` (clean venv `pip install -r requirements.txt`) | **PASS** |
| `test_path` (`25/25 PASS` in clean venv) | **PASS** |
| `test_path` portable (Linux native, NO_TIMEOUT, macOS-no-timeout sim) | **PASS** |
| `manifest_path` (`sha256sum -c MANIFEST.sha256` 0 FAILED) | **PASS** |
| `state_path` (R55 SIC-JS state verifier PASS) | **PASS** |
| `package_clarity` (README/QUICKSTART/TROUBLESHOOTING/PACKAGE_MAP/RELEASE_STATUS/CHANGELOG present and consistent) | **PASS** |
| `claim_safety` (no `production-certified` / `formal standard` claims; only superseded files mention old version numbers) | **PASS** |
| `public_internal_boundary` (`internal/`, `internal/superseded_logs/` correctly isolated from user-facing root) | **PASS** |
| `output_rule` (single zip + in-message R55 JSON) | Verified at delivery time |

---

## 8. Conclusion

R52c closes the JG macOS reproducibility blocker on R52b. The runner now
behaves correctly on three distinct environments (Linux native, NO_TIMEOUT
fallback, and a simulated macOS-without-coreutils host) and degrades
gracefully with actionable errors on the one environment we cannot fully
verify from a Linux build host (real macOS with Homebrew). Documentation
across `README.md`, `QUICKSTART.md`, and `TROUBLESHOOTING.md` is consistent
on the new behavior and explicitly tells reviewers what to do on each
platform. Gate 3 is prepared. Gates 1, 2, 4, 5, 6 are unchanged from R52b.
Gate 7 remains pending the project owner's final release ruling.
