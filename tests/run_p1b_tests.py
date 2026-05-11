#!/usr/bin/env python3
"""
SIC-JS Toolkit P1B Test Suite — Python runner
Runs: W1-W6 (writer), V1-V10 (verifier), C1-C3 (consistency), L1 (legacy)
Expected: W1-W6 PASS, V1-V3 PASS, V4-V9 FAIL (correct), V10 FAIL, C1-C3 PASS, L1 FAIL

Usage:
    python3 tests/run_p1b_tests.py
    (run from toolkit root directory)
"""
import subprocess, json, os, sys, tempfile

# Derive toolkit root from this file's location — no hardcoded paths
TOOLKIT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VALIDATOR = os.path.join(TOOLKIT_ROOT, "src", "validator", "validate_skeleton_v2.py")
WRITER = os.path.join(TOOLKIT_ROOT, "src", "writer", "sic_write.py")
FIXTURES = os.path.join(TOOLKIT_ROOT, "tests", "fixtures")

TOTAL = PASS = FAIL = 0


def run_validator(filepath, mode="toolkit"):
    r = subprocess.run(
        [sys.executable, VALIDATOR, "--file", filepath, "--mode", mode],
        capture_output=True, timeout=10
    )
    return r.returncode


def run_writer(out_path, upstream_type=None, upstream=None, mode="toolkit", round_n=99):
    cmd = [
        sys.executable, WRITER,
        "--entity-name", "TestEntity",
        "--entity-model", "TestModel",
        "--context", "test",
        "--current-action", "test",
        "--user", "TestUser",
        "--round", str(round_n),
        "--mode", mode,
        "--output", out_path
    ]
    if upstream_type:
        cmd += ["--upstream-type", upstream_type]
    if upstream:
        cmd += ["--upstream", upstream]
    r = subprocess.run(cmd, capture_output=True, timeout=10)
    return r.returncode


def check(name, expect_pass, exit_code):
    global TOTAL, PASS, FAIL
    TOTAL += 1
    ok = (expect_pass and exit_code == 0) or (not expect_pass and exit_code != 0)
    symbol = "✅" if ok else "❌"
    label = "PASS" if expect_pass else "FAIL"
    print(f"  {symbol} {name} (expect {label}) exit={exit_code}")
    if ok:
        PASS += 1
    else:
        FAIL += 1


def find_fixture(prefix, ext=".json"):
    """Find fixture file by prefix in fixtures directory."""
    for name in os.listdir(FIXTURES):
        if name.startswith(prefix) and name.endswith(ext):
            return os.path.join(FIXTURES, name)
    return None


print("=== SIC-JS Toolkit P1B Test Suite ===\n")

# --- Writer Tests W1-W6 ---
print("--- Writer Tests ---")
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    tmp = f.name

# W1: none/null
exit_code = run_writer(tmp, upstream_type="none", upstream="null", round_n=1)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "none" and (r.get("upstream") is None or r.get("upstream") == "null")
    check("W1_none_null", True, 0 if ok else 1)
else:
    check("W1_none_null", True, exit_code)

# W2: cryptographic/hex
exit_code = run_writer(tmp, upstream_type="cryptographic", upstream="a3f8b2c1d4e5f607", round_n=2)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "cryptographic" and r.get("upstream") == "a3f8b2c1d4e5f607"
    check("W2_crypto_hex", True, 0 if ok else 1)
else:
    check("W2_crypto_hex", True, exit_code)

# W3: file/label
exit_code = run_writer(tmp, upstream_type="file", upstream="XIED_v2.json", round_n=3)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "file" and r.get("upstream") == "XIED_v2.json"
    check("W3_file_label", True, 0 if ok else 1)
else:
    check("W3_file_label", True, exit_code)

# W4: auto-derive hex
exit_code = run_writer(tmp, upstream="a3f8b2c1d4e5f607", round_n=4)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "cryptographic"
    check("W4_auto_hex", True, 0 if ok else 1)
else:
    check("W4_auto_hex", True, exit_code)

# W5: auto-derive label
exit_code = run_writer(tmp, upstream="XIED_v2.json", round_n=5)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "file"
    check("W5_auto_label", True, 0 if ok else 1)
else:
    check("W5_auto_label", True, exit_code)

# W6: auto-derive null
exit_code = run_writer(tmp, upstream="null", round_n=6)
if exit_code == 0:
    d = json.load(open(tmp))
    r = d["relation"]
    ok = r.get("upstream_type") == "none"
    check("W6_auto_null", True, 0 if ok else 1)
else:
    check("W6_auto_null", True, exit_code)

# --- Verifier Tests V1-V10 ---
print("\n--- Verifier Tests ---")
for V in ["V1_none_null", "V2_crypto_hex", "V3_file_label"]:
    f = find_fixture(V)
    if f:
        check(V, True, run_validator(f))
    else:
        check(V + "_MISSING", True, 1)

for V in ["V4_none_nonnull", "V5_crypto_null", "V6_crypto_label",
          "V7_file_null", "V8_file_hex", "V9_file_traversal"]:
    f = find_fixture(V)
    if f:
        check(V, False, run_validator(f))
    else:
        check(V + "_MISSING", False, 0)

# V10 invalid datetime
f = find_fixture("V10_invalid_datetime")
if f:
    check("V10_invalid_datetime", False, run_validator(f))

# --- Consistency Tests C1-C3 ---
print("\n--- Consistency Tests ---")

# C1: W2 output → verifier PASS
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    c1_tmp = f.name
run_writer(c1_tmp, upstream_type="cryptographic", upstream="a3f8b2c1d4e5f607", round_n=10)
check("C1_writer_to_verifier", True, run_validator(c1_tmp))

# C2: auto-derive W4 → verifier PASS
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    c2_tmp = f.name
run_writer(c2_tmp, upstream="a3f8b2c1d4e5f607", round_n=11)
check("C2_auto_derive_consistent", True, run_validator(c2_tmp))

# C3: all three types
c3_pass = True
for ut, up in [("none", "null"), ("cryptographic", "a3f8b2c1d4e5f607"), ("file", "XIED_v2.json")]:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        c3_tmp = f.name
    run_writer(c3_tmp, upstream_type=ut, upstream=up, round_n=12)
    if run_validator(c3_tmp) != 0:
        c3_pass = False
check("C3_all_types_consistent", True, 0 if c3_pass else 1)

# --- Legacy Test L1 ---
print("\n--- Legacy Test ---")
f = find_fixture("L1_legacy")
if f:
    check("L1_legacy_toolkit_mode", False, run_validator(f))

# --- Summary ---
print(f"\nTOTAL: {TOTAL}  PASS: {PASS}  FAIL: {FAIL}")
if FAIL == 0:
    print("🟢 ALL P1B TESTS PASSED")
else:
    print("🔴 SOME P1B TESTS FAILED")

# Cleanup
try:
    os.unlink(tmp)
    os.unlink(c1_tmp)
    os.unlink(c2_tmp)
    os.unlink(c3_tmp)
except Exception:
    pass

sys.exit(FAIL)
