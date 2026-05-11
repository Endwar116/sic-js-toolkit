#!/bin/bash
# run_tests.sh — SIC-JS Toolkit Test Runner (R52c)
#
# Per-test timeout to prevent runner hang.
# Default per-test timeout: 30s (override via PER_TEST_TIMEOUT env var).
# Default --kill-after grace period: 5s (override via KILL_AFTER env var).
# PYTHONDONTWRITEBYTECODE=1 prevents __pycache__ creation during tests.
#
# Portable timeout handling (R52c):
#   - Uses GNU `timeout` if available.
#   - Falls back to `gtimeout` (macOS Homebrew coreutils package name).
#   - If neither is available, exits early with an actionable error message
#     (NOT 24x exit 127). Use NO_TIMEOUT=1 as a local-evaluation fallback.
#
# Exit code: 0 if all pass, 1 if any fail, 2 if missing dependency (early exit).

set +e  # Continue on errors to count all failures
export PYTHONDONTWRITEBYTECODE=1  # Prevent .pyc generation during tests

TOOLKIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="$TOOLKIT_ROOT/src/validator/validate_skeleton_v2.py"
WRITER="$TOOLKIT_ROOT/src/writer/sic_write.py"
VERIFIER="$TOOLKIT_ROOT/src/verifier/sic_verify.sh"
FIXTURES="$TOOLKIT_ROOT/tests/fixtures"
TMPDIR="$(mktemp -d)"

PER_TEST_TIMEOUT="${PER_TEST_TIMEOUT:-30}"  # seconds per sub-test
KILL_AFTER="${KILL_AFTER:-5}"               # SIGKILL grace period after timeout
NO_TIMEOUT="${NO_TIMEOUT:-0}"               # 1 = run without any timeout (local eval only)

# ============================================================
# Portable timeout resolver (R52c, hardened)
#
# Strategy:
#   1. NO_TIMEOUT=1   -> explicit local-eval fallback, skip resolver.
#   2. `timeout`      -> functional probe (`timeout 1 true` returns 0).
#   3. `gtimeout`     -> functional probe (same).
#   4. None usable    -> exit 2 with actionable error (NOT 24x exit-127).
#
# Functional probe is required because `command -v` may locate a binary
# named `timeout` that is not GNU coreutils (e.g. a macOS shadow stub,
# a non-GNU `/usr/bin/timeout`, or a broken symlink). Without a probe,
# such a binary would be invoked once per test and trigger a misleading
# 24x failure cascade.
# ============================================================
TIMEOUT_CMD=""
TIMEOUT_MODE=""

_probe_timeout() {
    # $1 = candidate command name (timeout|gtimeout)
    # Returns 0 if candidate behaves like GNU timeout, non-zero otherwise.
    local cand="$1"
    command -v "$cand" >/dev/null 2>&1 || return 1
    # GNU timeout: `<cmd> 1 true` should exit 0.
    "$cand" 1 true >/dev/null 2>&1
}

if [ "$NO_TIMEOUT" = "1" ]; then
    TIMEOUT_MODE="disabled"
    echo "[runner] WARNING: NO_TIMEOUT=1 set. Tests will run WITHOUT per-test timeout."
    echo "[runner] WARNING: This is a LOCAL EVALUATION FALLBACK only."
    echo "[runner] WARNING: A hung test will hang the entire runner. Do NOT use this path"
    echo "[runner] WARNING: for official reproducibility evidence."
    echo ""
elif _probe_timeout timeout; then
    TIMEOUT_CMD="timeout"
    TIMEOUT_MODE="timeout"
elif _probe_timeout gtimeout; then
    TIMEOUT_CMD="gtimeout"
    TIMEOUT_MODE="gtimeout"
else
    cat >&2 <<'EOF'
[runner] ERROR: No usable `timeout` / `gtimeout` command found.
(Either neither is on PATH, or both failed the functional probe
 `<cmd> 1 true` -> exit 0, indicating they are not GNU coreutils timeout.)

The test runner uses per-test timeouts to prevent hangs. Without a working
timeout command, a single hung test would freeze the whole runner.

Resolution by platform:

  Linux (Debian/Ubuntu/RHEL/CentOS):
    `timeout` ships with GNU coreutils and should already be installed.
    If missing: sudo apt-get install coreutils

  macOS:
    macOS does not ship GNU `timeout`. Install via Homebrew:
        brew install coreutils
    After install, the command is named `gtimeout` (this script auto-detects it).

  Local evaluation fallback (NOT for official reproducibility):
    NO_TIMEOUT=1 bash tests/run_tests.sh
    This skips timeout protection. Use only for quick local checks where
    you trust the tests will complete.

This is NOT a toolkit-core failure. The validator, writer, and verifier
can still be invoked manually. See README.md > "Verify core tools manually".

Exiting early to avoid a misleading 24x "exit 127" failure cascade.
EOF
    exit 2
fi

if [ -n "$TIMEOUT_CMD" ]; then
    echo "[runner] timeout backend: $TIMEOUT_CMD (per-test=${PER_TEST_TIMEOUT}s, kill-after=${KILL_AFTER}s)"
    echo ""
fi

# ============================================================
# run_with_timeout <name> <expected_exit> -- <command...>
# ============================================================
PASS=0
FAIL=0
FAILED_TESTS=()

run_with_timeout() {
    local name="$1"
    local expected="$2"
    shift 2
    [ "$1" = "--" ] && shift
    local rc
    if [ "$TIMEOUT_MODE" = "disabled" ]; then
        "$@" > /dev/null 2>&1
        rc=$?
    else
        "$TIMEOUT_CMD" --kill-after="${KILL_AFTER}s" "${PER_TEST_TIMEOUT}" "$@" > /dev/null 2>&1
        rc=$?
    fi
    if [ "$rc" = "124" ]; then
        echo "  ❌ $name (TIMEOUT after ${PER_TEST_TIMEOUT}s) — try PER_TEST_TIMEOUT=60 bash tests/run_tests.sh"
        FAIL=$((FAIL+1))
        FAILED_TESTS+=("$name (TIMEOUT)")
        return 124
    fi
    if [ "$expected" = "$rc" ]; then
        echo "  ✅ $name (exit=$rc)"
        PASS=$((PASS+1))
    else
        echo "  ❌ $name (expected=$expected, got=$rc)"
        FAIL=$((FAIL+1))
        FAILED_TESTS+=("$name")
    fi
    return "$rc"
}

# Helper for inline timeouted commands (W4 derive check, W_stdout)
inline_timeout() {
    local secs="$1"
    shift
    if [ "$TIMEOUT_MODE" = "disabled" ]; then
        "$@"
    else
        "$TIMEOUT_CMD" --kill-after="${KILL_AFTER}s" "$secs" "$@"
    fi
}

# ============================================================
# W1-W6: Writer tests
# ============================================================
echo "[Writer Tests W1-W6]"

run_with_timeout "W1_writer_none_null" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --upstream-type none --upstream null \
    --mode toolkit --output "$TMPDIR/W1.json"

run_with_timeout "W2_writer_crypto_hex" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --upstream-type cryptographic --upstream a3f8b2c1d4e5f607 \
    --mode toolkit --output "$TMPDIR/W2.json"

run_with_timeout "W3_writer_file_label" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --upstream-type file --upstream XIED_v58.json \
    --mode toolkit --output "$TMPDIR/W3.json"

run_with_timeout "W4_writer_auto_crypto" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --upstream a3f8b2c1d4e5f607 \
    --mode toolkit --output "$TMPDIR/W4.json"

# Verify auto-derived value (separate inline check)
if [ -f "$TMPDIR/W4.json" ]; then
    DERIVED=$(inline_timeout 5 python3 -c "import json; print(json.load(open('$TMPDIR/W4.json'))['relation']['upstream_type'])" 2>/dev/null)
    if [ "$DERIVED" = "cryptographic" ]; then
        echo "  ✅ W4_auto_derive_check (got: cryptographic)"
        PASS=$((PASS+1))
    else
        echo "  ❌ W4_auto_derive_check (got: $DERIVED, expected cryptographic)"
        FAIL=$((FAIL+1))
        FAILED_TESTS+=("W4_auto_derive_check")
    fi
fi

run_with_timeout "W5_writer_auto_file" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --upstream "XIED_v58.json" \
    --mode toolkit --output "$TMPDIR/W5.json"

run_with_timeout "W6_writer_auto_none" 0 -- python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --mode toolkit --output "$TMPDIR/W6.json"

# ============================================================
# V1-V10: Verifier tests
# ============================================================
echo ""
echo "[Verifier Tests V1-V10]"

run_with_timeout "V1_none_null" 0 -- bash "$VERIFIER" --file "$FIXTURES/V1_none_null.json" --mode toolkit
run_with_timeout "V2_crypto_hex" 0 -- bash "$VERIFIER" --file "$FIXTURES/V2_crypto_hex.json" --mode toolkit
run_with_timeout "V3_file_label" 0 -- bash "$VERIFIER" --file "$FIXTURES/V3_file_label.json" --mode toolkit
run_with_timeout "V4_none_nonnull (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V4_none_nonnull.json" --mode toolkit
run_with_timeout "V5_crypto_null (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V5_crypto_null.json" --mode toolkit
run_with_timeout "V6_crypto_label (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V6_crypto_label.json" --mode toolkit
run_with_timeout "V7_file_null (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V7_file_null.json" --mode toolkit
run_with_timeout "V8_file_hex (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V8_file_hex.json" --mode toolkit
run_with_timeout "V9_file_traversal (expect UNSAFE)" 5 -- bash "$VERIFIER" --file "$FIXTURES/V9_file_traversal.json" --mode toolkit
run_with_timeout "V10_invalid_datetime (expect FAIL)" 1 -- bash "$VERIFIER" --file "$FIXTURES/V10_invalid_datetime.json" --mode toolkit

# ============================================================
# C1-C3: Consistency tests (writer→verifier)
# ============================================================
echo ""
echo "[Consistency Tests C1-C3]"

run_with_timeout "C1_writer_W2_to_verifier" 0 -- bash "$VERIFIER" --file "$TMPDIR/W2.json" --mode toolkit
run_with_timeout "C2_writer_W4_auto_to_verifier" 0 -- bash "$VERIFIER" --file "$TMPDIR/W4.json" --mode toolkit

PASS_C3=true
for f in W1 W2 W3; do
    inline_timeout "$PER_TEST_TIMEOUT" bash "$VERIFIER" --file "$TMPDIR/$f.json" --mode toolkit > /dev/null 2>&1 || PASS_C3=false
done
if [ "$PASS_C3" = "true" ]; then
    echo "  ✅ C3_writer_W1W2W3_consistency"
    PASS=$((PASS+1))
else
    echo "  ❌ C3_writer_W1W2W3_consistency"
    FAIL=$((FAIL+1))
    FAILED_TESTS+=("C3_writer_W1W2W3_consistency")
fi

# ============================================================
# L1: Legacy test
# ============================================================
echo ""
echo "[Legacy Test L1]"

run_with_timeout "L1_legacy_toolkit_mode (expect LEGACY)" 6 -- bash "$VERIFIER" --file "$FIXTURES/L1_legacy.json" --mode toolkit
run_with_timeout "L1_legacy_canonical_mode (expect PASS)" 0 -- bash "$VERIFIER" --file "$FIXTURES/L1_legacy.json" --mode canonical

# ============================================================
# CLI Regression Tests
# ============================================================
echo ""
echo "[CLI Regression Tests]"

run_with_timeout "CLI_mode_toolkit_plus_toolkit_mode (expect INVALID_USAGE)" 2 -- python3 "$VALIDATOR" --file "$FIXTURES/V1_none_null.json" --mode toolkit --toolkit-mode

# W_stdout: writer to stdout, then verifier
inline_timeout "$PER_TEST_TIMEOUT" python3 "$WRITER" \
    --entity-name test --entity-model TestModel \
    --context c --current-action a --user u \
    --mode canonical > "$TMPDIR/W_stdout.json" 2>/dev/null
rc=$?
if [ "$rc" = "0" ]; then
    echo "  ✅ W_stdout_self_validate (exit=0)"
    PASS=$((PASS+1))
else
    echo "  ❌ W_stdout_self_validate (got=$rc)"
    FAIL=$((FAIL+1))
    FAILED_TESTS+=("W_stdout_self_validate")
fi
run_with_timeout "W_stdout_verifier" 0 -- bash "$VERIFIER" --file "$TMPDIR/W_stdout.json" --mode canonical

# ============================================================
# Summary
# ============================================================
TOTAL=$((PASS+FAIL))
echo ""
echo "====================================="
echo "TOTAL: $TOTAL  PASS: $PASS  FAIL: $FAIL"
echo "====================================="

if [ $FAIL -gt 0 ]; then
    echo "Failed tests:"
    for t in "${FAILED_TESTS[@]}"; do
        echo "  - $t"
    done
    rm -rf "$TMPDIR"
    exit 1
fi

rm -rf "$TMPDIR"
exit 0
