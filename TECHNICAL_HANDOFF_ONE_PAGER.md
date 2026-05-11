# SIC-JS Toolkit v1.0.0 — Technical Handoff One-Pager

## What this is

SIC-JS Toolkit v1.0.0 is an **artifact-layer reference toolkit** for SIC-JS v2.0.
SIC-JS (Semantic Intent Context - JSON State) is a JSON-based state-handoff format
designed to let one AI session transfer its working state to a later AI session in a
way that is verifiable, schema-checked, and forgery-resistant.

This toolkit provides the foundational artifact layer (Layer 1) for long-horizon AI
state governance.

## What this is NOT

- **Not a full AGI runtime.** This package validates and writes SIC-JS files; it does
  not run inference or maintain a live agent loop.
- **Not a production-certified enterprise platform.** It is a reference implementation
  intended for research, evaluation, and integration testing.
- **Not a runtime mount guard.** It does not actively intercept AI outputs or enforce
  state mounting at runtime (that is Layer 2).
- **Not a replay ledger.** It does not provide cross-agent replay, diffing, or audit
  infrastructure (that is Layer 3).

## Why it matters

Without a verifiable state-handoff format, long-horizon AI tasks suffer from "AGI drift"
— the loss of semantic intent, context, and constraints across session boundaries.
By standardizing the artifact layer, this toolkit makes AI state handoffs inspectable,
reproducible, and structurally sound, laying the groundwork for reliable multi-agent
collaboration.

## What is included

1. **Canonical Schema**: The hash-locked `sic-js-schema-v2.0.json`.
2. **Toolkit Schema Fork**: Adds the `relation.upstream_type` extension.
3. **Validator & Verifier**: Tools to check SIC-JS files against the schemas.
4. **Writer**: Tool to produce valid SIC-JS files with auto-derivation.
5. **Test Suite**: A reproducible 25-case test suite with portable timeout handling.
6. **Smoke-Test**: A preflight script that fail-closes with actionable remediation.
7. **Documentation**: Examples, migration guides, and governance documentation.

## How to verify in 5 minutes

On a Linux or macOS machine with Python 3.11+, `sha256sum`, and GNU `timeout` (or `gtimeout`):

```bash
unzip SIC_JS_TOOLKIT_v1.0.0_FINAL_2026-05-09.zip
cd sic-js-toolkit-v1.0.0
bash bin/smoke-test.sh
```

Expected output: `SMOKE-TEST: ALL PASS`

## Current status

- **Version**: 1.0.0
- **License**: MIT
- **Release Class**: Final release (Gate 7 CLOSED)
- **Portability**: Verified on Linux and macOS

## Suggested citation / label

**Label**: `SIC-JS Toolkit v1.0.0 (Artifact-Layer Reference Implementation)`
