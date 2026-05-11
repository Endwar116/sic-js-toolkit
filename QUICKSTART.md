# SIC-JS Toolkit — QUICKSTART

The shortest possible path from "I have the zip" to "I have a confirmed PASS."

## Prerequisites

- Python 3.11 or newer (`python3 --version`)
- `bash`, `sha256sum`, `pip` (`python3 -m pip --version`)
- GNU `timeout` command:
  - **Linux**: usually preinstalled (`coreutils`).
  - **macOS**: `brew install coreutils` (script auto-detects `gtimeout`).
  - **Air-gapped / no Homebrew**: use `NO_TIMEOUT=1` fallback (see below).

`bin/smoke-test.sh` runs preflight first. If a prerequisite is missing it prints an
actionable error and exits with code 2 (it does **not** produce a misleading test
failure cascade).

## The one command (recommended)

```bash
unzip <delivered-zip>.zip
cd sic-js-toolkit
bash bin/smoke-test.sh
```

Expected last line: `SMOKE-TEST: ALL PASS`

## The five commands (manual path)

```bash
unzip <delivered-zip>.zip
cd sic-js-toolkit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash tests/run_tests.sh
```

## Expected output (last lines)

```
=====================================
TOTAL: 25  PASS: 25  FAIL: 0
=====================================
```

If you see exactly that, the package is correctly installed and reproducible on your machine.

## What if the runner takes too long?

The runner enforces a per-test timeout of **30 seconds** (override with
`PER_TEST_TIMEOUT=N bash tests/run_tests.sh`). If a sub-test times out, the runner
prints `❌ <name> (TIMEOUT after 30s)` and continues; it will not hang.

On fast machines a complete run takes about 4 seconds; on slow CI/VM environments it
may take 10–20 seconds. If you see `TIMEOUT` even after raising to 60 seconds, see
`TROUBLESHOOTING.md` → "timeout in run_tests".

## On macOS

macOS does not ship the GNU `timeout` command. Recommended:

```bash
brew install coreutils       # installs gtimeout (auto-detected)
bash bin/smoke-test.sh
```

If you do not have Homebrew, the runner will exit early with code 2 and an
actionable error (it will **not** report 24x exit-127). For a quick local check
in that case:

```bash
NO_TIMEOUT=1 bash bin/smoke-test.sh
```

This prints four `WARNING` lines and runs without per-test timeout. **Do not
submit `NO_TIMEOUT=1` runs as official reproducibility evidence.**

## What if `pip install` fails?

The only required dependency is `jsonschema`. `pip install -r requirements.txt`
fetches it from PyPI. If your environment cannot reach PyPI:

```bash
# Option A: internal mirror
pip install --index-url https://pypi.your-org.example/simple -r requirements.txt

# Option B: install jsonschema directly (any source you have access to)
pip install jsonschema
```

Then retry `bash bin/smoke-test.sh` (or `bash tests/run_tests.sh` for tests only).

A `pip install` failure is a **packaging / network** issue, not a toolkit-core issue.
The core tools can still be invoked manually — see `README.md` →
*Verify core tools manually*.

## After PASS, what next?

1. Read `README.md` for what the toolkit is and is not.
2. Read `PACKAGE_MAP.md` to understand directory layout.
3. Read `RELEASE_STATUS.md` to understand the current release class.
4. If you encounter any issue, see `TROUBLESHOOTING.md`.
5. To produce or verify your own SIC-JS files, see the **Component reference** and
   **5-minute Smoke Test** sections of `README.md`.

If anything in this QUICKSTART does not work as described, the package is not in a
release-candidate state; do not use it. Report through the channel that delivered the
package to you.
