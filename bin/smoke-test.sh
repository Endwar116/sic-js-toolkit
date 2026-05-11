#!/bin/bash
# bin/smoke-test.sh — One-command smoke test for SIC-JS Toolkit (R52c)
#
# Purpose: from a fresh unzip, run the complete acceptance pipeline:
#   0) preflight (python3, pip, sha256sum, timeout/gtimeout)
#   1) create venv
#   2) install dependencies
#   3) run the 25-test suite
#   4) verify MANIFEST.sha256
#   5) verify the bundled SIC-JS state file(s)
#
# Usage:
#   cd <unzipped-toolkit-root>
#   bash bin/smoke-test.sh
#
# Local evaluation fallback (if you do not have GNU coreutils on macOS):
#   NO_TIMEOUT=1 bash bin/smoke-test.sh
#   This skips per-test timeout protection. Use only for quick local checks.
#
# Exit code:
#   0 = all checks passed
#   1 = a check failed (see output for which step)
#   2 = preflight missing dependency (actionable error printed)
#   3 = pip install failed (network / PyPI access issue, see message)

set -e
export PYTHONDONTWRITEBYTECODE=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$TOOLKIT_ROOT"

NO_TIMEOUT="${NO_TIMEOUT:-0}"

echo "======================================================"
echo "SIC-JS Toolkit smoke-test (R52c)"
echo "Toolkit root: $TOOLKIT_ROOT"
echo "OS:           $(uname -s -r 2>&1)"
echo "======================================================"

# -----------------------------------------------------------
# Step 0: PREFLIGHT
# -----------------------------------------------------------
echo ""
echo "[0/5] Preflight checks..."
PREFLIGHT_FAIL=0

# python3
if command -v python3 >/dev/null 2>&1; then
    echo "  python3: $(python3 --version 2>&1)"
else
    echo "  python3: MISSING"
    PREFLIGHT_FAIL=1
fi

# pip
if python3 -m pip --version >/dev/null 2>&1; then
    echo "  pip:     $(python3 -m pip --version 2>&1 | awk '{print $1, $2}')"
else
    echo "  pip:     MISSING (try: python3 -m ensurepip --upgrade)"
    PREFLIGHT_FAIL=1
fi

# sha256sum
if command -v sha256sum >/dev/null 2>&1; then
    echo "  sha256sum: present"
elif command -v shasum >/dev/null 2>&1; then
    echo "  sha256sum: MISSING (macOS has 'shasum -a 256' but the manifest uses sha256sum format)"
    echo "             Install GNU coreutils: brew install coreutils"
    echo "             After install you can: alias sha256sum='gsha256sum'"
    PREFLIGHT_FAIL=1
else
    echo "  sha256sum: MISSING"
    PREFLIGHT_FAIL=1
fi

# timeout / gtimeout (CRITICAL — root cause of R52b macOS failure)
# R52c hardening: probe with `<cmd> 1 true` to ensure the binary really
# behaves like GNU coreutils timeout (not just a same-named shadow stub).
_probe_timeout_smoke() {
    local cand="$1"
    command -v "$cand" >/dev/null 2>&1 || return 1
    "$cand" 1 true >/dev/null 2>&1
}
if [ "$NO_TIMEOUT" = "1" ]; then
    echo "  timeout: SKIPPED (NO_TIMEOUT=1; local evaluation fallback)"
elif _probe_timeout_smoke timeout; then
    echo "  timeout: $(command -v timeout) (functional probe PASS)"
elif _probe_timeout_smoke gtimeout; then
    echo "  timeout: $(command -v gtimeout) (using gtimeout from coreutils, functional probe PASS)"
else
    cat <<'EOF'
  timeout: MISSING or NON-FUNCTIONAL
  (Neither `timeout` nor `gtimeout` is on PATH, OR both failed the
   functional probe `<cmd> 1 true` -> exit 0, indicating they are not
   GNU coreutils timeout.)

  This is REQUIRED for the test runner. Without it, the runner cannot
  enforce per-test timeouts and would either hang or report 24x exit 127.

  Resolution:
    - Linux: install GNU coreutils (Debian/Ubuntu: sudo apt-get install coreutils)
    - macOS: brew install coreutils (then `gtimeout` is auto-detected)
    - Local fallback (NOT for official reproducibility):
        NO_TIMEOUT=1 bash bin/smoke-test.sh

  This is NOT a toolkit-core failure. The validator, writer, and verifier
  can still be invoked manually:
    bash src/verifier/sic_verify.sh --file examples/example_file.json --mode toolkit
EOF
    PREFLIGHT_FAIL=1
fi

if [ "$PREFLIGHT_FAIL" = "1" ]; then
    echo ""
    echo "  Preflight FAILED. Address the missing dependencies above and re-run."
    exit 2
fi
echo "  Preflight PASS."

# -----------------------------------------------------------
# Step 1: venv
# -----------------------------------------------------------
echo ""
echo "[1/5] Creating virtual environment (.venv)..."
if [ -d .venv ]; then
    echo "  .venv already exists — reusing."
else
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# -----------------------------------------------------------
# Step 2: install
# -----------------------------------------------------------
echo ""
echo "[2/5] Installing dependencies (jsonschema)..."
if ! pip install --quiet -r requirements.txt 2>/tmp/sicjs_pip_err; then
    cat <<'EOF'
  pip install FAILED.

  Common causes:
    - No network access to PyPI (corporate firewall, air-gapped env)
    - SSL inspection breaking pip
    - Stale pip cache

  Resolution:
    - Use an internal PyPI mirror:
        pip install --index-url https://pypi.your-org.example/simple -r requirements.txt
    - Or pre-install jsonschema:
        pip install jsonschema
    - This is a NETWORK / PACKAGING issue, not a toolkit-core issue.
      You can still verify core tools manually:
        bash src/verifier/sic_verify.sh --file examples/example_file.json --mode toolkit

  pip stderr:
EOF
    cat /tmp/sicjs_pip_err
    rm -f /tmp/sicjs_pip_err
    exit 3
fi
rm -f /tmp/sicjs_pip_err
echo "  jsonschema: $(python3 -c 'import jsonschema; print(jsonschema.__version__)')"

# -----------------------------------------------------------
# Step 3: tests
# -----------------------------------------------------------
echo ""
echo "[3/5] Running tests/run_tests.sh ..."
set +e
bash tests/run_tests.sh
TEST_RC=$?
set -e
if [ "$TEST_RC" != "0" ]; then
    echo "  TESTS FAILED (exit=$TEST_RC). See output above."
    exit 1
fi

# -----------------------------------------------------------
# Step 4: manifest
# -----------------------------------------------------------
echo ""
echo "[4/5] Verifying MANIFEST.sha256 ..."
set +e
MANIFEST_OUT="$(sha256sum -c MANIFEST.sha256 2>&1)"
set -e
FAILED_LINES="$(echo "$MANIFEST_OUT" | grep -c FAILED || true)"
OK_LINES="$(echo "$MANIFEST_OUT" | grep -c ': OK$' || true)"
echo "  MANIFEST: $OK_LINES OK, $FAILED_LINES FAILED"
if [ "$FAILED_LINES" != "0" ]; then
    echo "$MANIFEST_OUT" | grep -E "FAILED|WARNING" | head -20
    echo "  MANIFEST CHECK FAILED."
    exit 1
fi

# -----------------------------------------------------------
# Step 5: state verify
# -----------------------------------------------------------
echo ""
echo "[5/5] Verifying bundled state files (toolkit mode)..."
STATE_FAIL=0
for f in state/*.json; do
    [ -f "$f" ] || continue
    if bash src/verifier/sic_verify.sh --file "$f" --mode toolkit > /dev/null 2>&1; then
        echo "  $f: PASS"
    else
        echo "  $f: FAIL"
        STATE_FAIL=$((STATE_FAIL+1))
    fi
done
if [ "$STATE_FAIL" != "0" ]; then
    echo "  STATE VERIFY FAILED for $STATE_FAIL file(s)."
    exit 1
fi

# -----------------------------------------------------------
# Done
# -----------------------------------------------------------
echo ""
echo "======================================================"
echo "SMOKE-TEST: ALL PASS"
echo "======================================================"
exit 0
