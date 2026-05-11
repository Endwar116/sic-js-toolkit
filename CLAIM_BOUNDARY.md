# SIC-JS Toolkit v1.0.0 — Claim Boundary

To maintain scientific and engineering rigor, and to prevent over-promising the capabilities of this software, we strictly define the allowed and disallowed claims regarding the SIC-JS Toolkit v1.0.0.

## Allowed Claims

These statements are accurate, supported by evidence, and authorized for public communication:

- **Artifact-Layer Reference Toolkit:** "SIC-JS Toolkit v1.0.0 is an MIT-licensed, artifact-layer reference toolkit."
- **Included Components:** "It provides a JSON schema, writer, validator, verifier, examples, tests, manifest, and smoke-test."
- **Purpose:** "It makes AI state handoff artifacts more inspectable, reproducible, and structurally sound."
- **Architectural Role:** "It serves as the foundational Layer 1 (the artifact layer) for a proposed long-horizon AI state governance architecture, acting as the bedrock for future runtime mount guards (Layer 2) and replay ledgers (Layer 3)."
- **Reproducibility:** "The 25-case test suite passes reliably on clean Linux and macOS environments."

## Disallowed Claims

These statements are inaccurate, unsupported, or represent future work. They **must not** be made:

- ~~"SIC-JS Toolkit solves AGI drift."~~ (It provides the format to mitigate it, but does not solve it alone).
- ~~"It guarantees cross-AI continuity."~~ (Continuity requires runtime enforcement, which this toolkit does not provide).
- ~~"It is an enterprise production-certified platform."~~ (It is a reference implementation).
- ~~"It is a formal external standard."~~ (It is a proposed format, not yet adopted by external standards bodies).
- ~~"It guarantees runtime state mounting."~~ (This requires Layer 2: Runtime Mount Guard).
- ~~"It proves the 10-round relay experiment."~~ (The experiment requires Layer 3 and cross-model validation).
- ~~"It replaces human governance."~~ (It augments human oversight by making state inspectable).

## Context: The Three-Layer Architecture

This toolkit is explicitly scoped as **Layer 1** of a broader architecture:

| Layer | Name | Description | Status |
|---|---|---|---|
| **Layer 1** | **Toolkit (this package)** | Schema, writer, verifier, manifest, examples, docs | **v1.0.0 — RELEASED** |
| Layer 2 | Runtime Mount Guard | Pre-send gate, output guardrail, round continuity checker, fail-closed, human-readable aftertext | Future work |
| Layer 3 | Replay / Witness Ledger | Cross-round, cross-model, cross-agent replay, audit, diff, fork | Future work |

By adhering to these boundaries, we ensure that the SIC-JS Toolkit is evaluated on its actual merits as a robust artifact layer, rather than on the promises of the full architecture it aims to support.
