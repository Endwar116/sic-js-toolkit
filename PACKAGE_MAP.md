# SIC-JS Toolkit — PACKAGE_MAP

A directory-by-directory map of what is in this final v1.0.0 release and what each
directory is for. Use this to know what to read, what to run, and what to ignore for
normal use.

## Top-level files

| File | Purpose |
|---|---|
| `README.md` | What the toolkit is, what it is not, and how to start. **Read this first.** |
| `QUICKSTART.md` | Shortest install + run path. |
| `TROUBLESHOOTING.md` | Common errors and fixes. |
| `PACKAGE_MAP.md` | This file. |
| `RELEASE_STATUS.md` | Current version, release class, and gate status. |
| `RELEASE_CHECKLIST_v1.0.md` | Detailed gate-by-gate release checklist (internal-facing but kept at root for reviewer access). |
| `CHANGELOG.md` | Version history. |
| `VERSION` | Plain-text version (`1.0.0`). |
| `LICENSE` | MIT License. Public redistribution authorized. |
| `MANIFEST.sha256` | SHA-256 manifest of all files for integrity checking. Verify with `sha256sum -c MANIFEST.sha256`. |
| `requirements.txt` | Python dependencies (only `jsonschema`). |

## Directory map

```
sic-js-toolkit/
├── schema/                         # SIC-JS v2.0 schemas
│   ├── README.md                   # Boundary between canonical and toolkit
│   ├── canonical/                  # Read-only canonical SIC-JS v2.0 schema (hash-locked)
│   │   └── sic-js-schema-v2.0.json
│   └── toolkit/                    # Toolkit fork with relation.upstream_type
│       └── sic-js-schema-v2.0-toolkit.json
│
├── src/                            # Implementation
│   ├── validator/                  # Schema + logic validation, dual mode
│   ├── writer/                     # State writer (auto-derives upstream_type in toolkit mode)
│   ├── verifier/                   # Shell wrapper around validator with safety guards
│   └── utils/                      # Shared utilities (e.g. canonical hash lock)
│
├── tests/                          # Reproducibility test suite
│   ├── run_tests.sh                # 25-case test runner with per-test timeout
│   ├── run_p1b_tests.py            # Python re-runner used during P1B development
│   ├── run_p1b_tests.sh            # Shell re-runner used during P1B development
│   ├── TEST_MATRIX.md              # Test-id → expected-exit map
│   └── fixtures/                   # Test input files
│
├── examples/                       # Valid SIC-JS files for hands-on inspection
│   ├── example_none.json
│   ├── example_cryptographic.json
│   └── example_file.json
│
├── docs/                           # User-facing documentation
│   ├── governance.md               # Toolkit governance posture (user-facing summary)
│   ├── migration-guide.md          # Moving from earlier SIC-JS variants
│   ├── backward-compatibility.md   # Compatibility policy + before/after example
│   ├── SIC-JS_v2.0_CHANGELOG.md    # Schema-level change log
│   └── api/                        # Component contracts and executable spec
│       ├── COMPONENT_CONTRACTS_v1_1.md
│       └── EXECUTABLE_SPEC_v1_0.md
│
├── internal/                       # Internal review and governance materials.
│   │                               # NOT required for normal installation or use.
│   ├── governance/                 # Phase packets, agent-loop protocol, chaos analysis,
│   │                               # interface definitions used during development.
│   └── reports/                    # Per-phase post-change reports (P1A, P1B, P2, P3A, P4, P5A)
│                                   # for governance traceability.
│
└── logs/                           # Command logs captured during development and review
                                    # (run_tests.sh full output, manifest check, environment info).
```

## What to read for what purpose

- **You want to install and run the test suite once:**
  Read `QUICKSTART.md`. That is enough.

- **You want to understand what SIC-JS is:**
  Read `README.md` and `schema/README.md`.

- **You want to write your own SIC-JS files:**
  Read `README.md` → "Component reference" and `docs/api/COMPONENT_CONTRACTS_v1_1.md`.

- **You want to verify the integrity of the package:**
  Run `sha256sum -c MANIFEST.sha256`. See also `TROUBLESHOOTING.md` § 4.

- **You hit an error:**
  Read `TROUBLESHOOTING.md`.

- **You want to know whether you can redistribute this:**
  Read `LICENSE` (MIT license — public redistribution authorized).

- **You are reviewing release readiness:**
  Read `RELEASE_STATUS.md`, then `RELEASE_CHECKLIST_v1.0.md`, then
  `internal/reports/` per-phase post-change reports.

- **You are not sure whether to read a file:**
  If it is in `internal/`, you almost certainly do not need to read it for normal use.
  If it is at the top level, in `docs/`, in `examples/`, or in `tests/`, it is part
  of normal use.

## What is intentionally not included

- **No CI configuration** — the test runner is designed to be invoked directly with
  `bash tests/run_tests.sh`; integration with CI systems is downstream work.
- **No installer / package metadata for PyPI** — this is a reference toolkit release,
  not a PyPI distribution.
- **No `.git/`** — this is a release-pack snapshot, not the development repository.
- **No `__pycache__/`** — pycache is excluded from release packs and from the manifest.
