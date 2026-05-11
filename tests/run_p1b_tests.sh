#!/bin/bash
# SIC-JS Toolkit F1 P1B Test Runner
# Runs: W1-W6 (writer), V1-V9 (verifier), C1-C3 (consistency), L1 (legacy)
# Expected: W1-W6 PASS, V1-V3 PASS, V4-V9 FAIL (correct), C1-C3 PASS, L1 FAIL+LEGACY

set -e
TOOLKIT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURES="$TOOLKIT_DIR/tests/fixtures"
VALIDATOR="python3 $TOOLKIT_DIR/src/validator/validate_skeleton_v2.py"
VERIFIER="bash $TOOLKIT_DIR/src/verifier/sic_verify.sh"

TOTAL=0; PASS=0; FAIL=0

run_test() {
  local name="$1"
  local expect_pass="$2"  # "PASS" or "FAIL"
  local exit_code="$3"

  TOTAL=$((TOTAL+1))
  if [ "$expect_pass" = "PASS" ] && [ "$exit_code" -eq 0 ]; then
    echo "  ✅ $name (expect PASS) (exit=$exit_code)"
    PASS=$((PASS+1))
  elif [ "$expect_pass" = "FAIL" ] && [ "$exit_code" -ne 0 ]; then
    echo "  ✅ $name (expect FAIL) (exit=$exit_code)"
    PASS=$((PASS+1))
  else
    echo "  ❌ $name (expect $expect_pass) (exit=$exit_code)"
    FAIL=$((FAIL+1))
  fi
}

echo "=== SIC-JS Toolkit F1 P1B Test Suite ==="
echo ""

# Writer Tests W1-W6
echo "--- Writer Tests ---"
for W in W1 W2 W3 W4 W5 W6; do
  bash "$FIXTURES/${W}_"*.sh > /tmp/w_out.txt 2>&1
  EXIT=$?
  grep -q "assertions PASS\|PASS" /tmp/w_out.txt && EXIT=0 || EXIT=1
  run_test "$W" "PASS" "$EXIT"
done

# Verifier Tests V1-V9
echo ""
echo "--- Verifier Tests ---"
for V in V1 V2 V3; do
  $VERIFIER --file "$FIXTURES/${V}_"*.json --mode toolkit > /dev/null 2>&1
  run_test "$V" "PASS" "$?"
done
for V in V4 V5 V6 V7 V8 V9; do
  $VERIFIER --file "$FIXTURES/${V}_"*.json --mode toolkit > /dev/null 2>&1
  run_test "$V" "FAIL" "$?"
done
# V10 invalid datetime
$VERIFIER --file "$FIXTURES/V10_invalid_datetime.json" --mode toolkit > /dev/null 2>&1
run_test "V10" "FAIL" "$?"

# Consistency Tests C1-C3
echo ""
echo "--- Consistency Tests ---"
for C in C1 C2 C3; do
  bash "$FIXTURES/${C}_"*.sh > /tmp/c_out.txt 2>&1
  grep -q "PASS" /tmp/c_out.txt && EXIT=0 || EXIT=1
  run_test "$C" "PASS" "$EXIT"
done

# Legacy Test L1
echo ""
echo "--- Legacy Test ---"
$VERIFIER --file "$FIXTURES/L1_legacy.json" --mode toolkit > /dev/null 2>&1
run_test "L1_legacy_toolkit_mode" "FAIL" "$?"

echo ""
echo "TOTAL: $TOTAL  PASS: $PASS  FAIL: $FAIL"
[ $FAIL -eq 0 ] && echo "🟢 ALL P1B TESTS PASSED" || echo "🔴 SOME P1B TESTS FAILED"
exit $FAIL
