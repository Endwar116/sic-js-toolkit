# SIC-JS Toolkit — TROUBLESHOOTING

If something does not work as documented in `README.md` or `QUICKSTART.md`, look here first.

---

## 1. `jsonschema missing` / `ModuleNotFoundError: No module named 'jsonschema'`

**Cause:** `jsonschema` is the only Python dependency, but it is not installed in the
active environment.

**Fix:**

```bash
pip install jsonschema
# or
pip install -r requirements.txt
```

If you are inside a virtualenv (`source .venv/bin/activate`), `pip` installs go into
that venv. If you are not in a venv, `pip` installs go to the system or user Python —
make sure the same Python that runs the toolkit is the one that has `jsonschema`.

Confirm:

```bash
python3 -c "import jsonschema; print(jsonschema.__version__)"
```

## 2. `permission denied` on `sic_verify.sh`

**Cause:** The shell wrapper is not executable.

**Fix:**

```bash
chmod +x src/verifier/sic_verify.sh
chmod +x tests/run_tests.sh
```

You can always invoke it explicitly with `bash`:

```bash
bash src/verifier/sic_verify.sh --file examples/example_file.json --mode toolkit
```

## 3. `timeout in run_tests` / `❌ <name> (TIMEOUT after 30s)`

**Cause:** A sub-test exceeded the per-test timeout (default: **30 seconds** in R52c;
raised from 10 in R52a/R52b after JG's macOS reproducibility test).
On a very slow machine, in a VM under heavy load, or on first-run cold caches,
30 seconds may still be insufficient.

**Reference timing:** on a typical Linux dev machine, the entire 25-test suite
completes in about 4 seconds. Each individual test usually finishes in under 1 second.
If any single test takes more than a few seconds, something is wrong (slow Python
startup, heavy IO contention, or a real bug).

**Fix:** Raise the timeout via the `PER_TEST_TIMEOUT` environment variable:

```bash
PER_TEST_TIMEOUT=60 bash tests/run_tests.sh
```

If raising the timeout to 60 seconds still results in a TIMEOUT, the package or your
environment has a real problem; do not silently extend further. Report through the
delivery channel with `python3 --version`, `uname -a`, and the failing test name.

## 3a. macOS: `[runner] ERROR: Neither timeout nor gtimeout command is available.` / runner exits with code 2

**Cause:** macOS does not ship the GNU `timeout` command, and Homebrew coreutils
(which provides `gtimeout`) is not installed. Without a portable timeout backend,
the runner cannot enforce per-test timeouts; it exits early with code 2 and an
actionable error rather than producing a misleading 24x exit-127 cascade (the
failure mode JG hit in R52b).

**Recommended fix:**

```bash
brew install coreutils       # installs gtimeout
bash bin/smoke-test.sh        # runner auto-detects gtimeout
```

**Air-gapped / no Homebrew fallback (local evaluation only):**

```bash
NO_TIMEOUT=1 bash bin/smoke-test.sh
```

This prints four `WARNING` lines and runs without per-test timeout. **Do not
submit `NO_TIMEOUT=1` runs as official reproducibility evidence** — a hung test
will hang the runner.

**Manual core-tool verification (no runner needed):** see `README.md` →
*Verify core tools manually*. This path needs only Python 3.11+ and `jsonschema`.

## 3b. macOS: `command not found: sha256sum`

**Cause:** macOS ships `shasum -a 256` instead of `sha256sum`. The toolkit's
`MANIFEST.sha256` is in `sha256sum -c` format and the smoke-test calls
`sha256sum -c` explicitly.

**Fix:**

```bash
brew install coreutils       # provides gsha256sum
# Then either alias it for the session:
alias sha256sum='gsha256sum'
# ...or invoke it directly:
gsha256sum -c MANIFEST.sha256
```

## 4. `manifest mismatch` / `sha256sum -c MANIFEST.sha256` reports FAILED

**Cause:** A file in the package has been modified, deleted, or added without
regenerating `MANIFEST.sha256`.

**Fix (if you only ran the test suite and did not edit anything):** the package was
delivered in a corrupted state; report through the delivery channel and do not trust
the contents.

**Fix (if you edited files locally):** `MANIFEST.sha256` is the release-candidate
manifest as shipped. Editing files is fine for evaluation, but it will invalidate the
manifest. To regenerate locally:

```bash
find . -type f \
  -not -path './.git/*' \
  -not -path './*/__pycache__/*' \
  -not -name '*.pyc' \
  -not -name 'MANIFEST.sha256' \
  -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256
sha256sum -c MANIFEST.sha256
```

Note: a locally regenerated manifest is not the release-candidate manifest. Do not
present it as such.

## 5. `canonical hash mismatch` / `CANONICAL_TAMPERED` (exit 9)

**Cause:** `schema/canonical/sic-js-schema-v2.0.json` no longer matches the canonical
SHA-256.

**Expected canonical hash:**

```
efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6
```

**Confirm:**

```bash
sha256sum schema/canonical/sic-js-schema-v2.0.json
```

**Fix:** Do not modify the canonical schema. If you need different fields, use the
toolkit fork (`schema/toolkit/sic-js-schema-v2.0-toolkit.json`) and toolkit mode.
If the file truly differs from the expected hash on a fresh unzip, the package is
corrupted; report through the delivery channel.

## 6. `invalid upstream_type` / verifier rejects a file you wrote

**Cause:** The `upstream_type` value in your file is not one of the three allowed
values, or it does not match the shape of the `upstream` value.

**Allowed shapes (toolkit mode):**

- `upstream_type=none` requires `upstream=null`.
- `upstream_type=cryptographic` requires `upstream` to be a hex string of length
  16 / 32 / 40 / 64 / 96 / 128 (lowercase).
- `upstream_type=file` requires `upstream` to be a label up to 256 characters,
  no path separators, no null bytes.

**Fix:** Either correct the value, or let the writer auto-derive `upstream_type` by
omitting `--upstream-type` when calling `sic_write.py` in toolkit mode.

## 7. `legacy file detected` / exit 6 (`LEGACY_FORMAT_DETECTED`)

**Cause:** A file is being verified in toolkit mode but does not have
`relation.upstream_type`.

**This is intentional behavior, not a bug.** Toolkit mode requires
`upstream_type`; canonical mode does not.

**Fix:** Use canonical mode for files that follow the canonical schema:

```bash
bash src/verifier/sic_verify.sh --file <legacy-file>.json --mode canonical
```

If you intend the file to be a toolkit-mode file, regenerate it with the writer in
toolkit mode, which will populate `upstream_type` automatically.

## 8. `pip install -r requirements.txt` fails with `Could not find a version` / SSL error / network timeout

**Cause:** Your environment cannot reach PyPI. Common causes: corporate firewall,
air-gapped CI, SSL inspection breaking pip, or stale pip cache.

The toolkit has **one** Python runtime dependency (`jsonschema>=4.0.0`).

**Fix (Option A — internal mirror):**

```bash
pip install --index-url https://pypi.your-org.example/simple -r requirements.txt
```

**Fix (Option B — install jsonschema directly):**

```bash
pip install jsonschema
bash bin/smoke-test.sh        # or: bash tests/run_tests.sh
```

**Fix (Option C — fully offline, no install):** if `jsonschema` is already importable
in your Python (`python3 -c 'import jsonschema; print(jsonschema.__version__)'`),
the `pip install` step is not strictly required. Skip the smoke-test and use the
manual core-tool verification path in `README.md` → *Verify core tools manually*.

A `pip install` failure is a **packaging / network** issue, not a toolkit-core
issue. It does not invalidate the toolkit's correctness, only its automated
install path in your specific environment.

---

## Anything else?

If you encounter behavior that this document does not cover, or any of the fixes above
do not resolve the issue, do not ship the package onward. Report through the channel
that delivered the package to you, with:

1. The exact command you ran.
2. The exact error message and exit code.
3. `python3 --version` and `uname -a` output.

The release candidate's purpose is to surface exactly these issues before final
release; reports help close Gate 7.
