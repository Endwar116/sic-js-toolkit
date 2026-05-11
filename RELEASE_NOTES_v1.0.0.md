# SIC-JS Toolkit v1.0.0 — Release Notes

**Release Date:** 2026-05-09  
**Release Name:** SIC-JS Toolkit v1.0.0 (Final Release)  
**License:** MIT License  
**Release Class:** Artifact-Layer Reference Toolkit (Layer 1)

We are pleased to announce the final v1.0.0 release of the SIC-JS (Semantic Intent Context - JSON State) Toolkit. This release marks the closure of Gate 7 and the transition from a release candidate to a stable, MIT-licensed reference implementation.

## Highlights

This release solidifies the foundational artifact layer for long-horizon AI state governance. Key features include:

- **Schema Separation:** A strict boundary between the hash-locked canonical schema (`sic-js-schema-v2.0.json`) and the extensible toolkit fork (`sic-js-schema-v2.0-toolkit.json`), ensuring protocol integrity while allowing tooling flexibility.
- **Robust Tooling:** A complete suite of CLI tools, including a Writer (with auto-derivation of upstream types), a Validator (supporting dual modes), and a Verifier (with built-in safety guards against path traversal and legacy formats).
- **Reproducible Test Suite:** A 25-case test suite (`tests/run_tests.sh`) that rigorously verifies writer output, verifier logic, consistency, and legacy format detection.
- **macOS Timeout Portability:** A portable timeout resolver that gracefully handles the absence of GNU `timeout` on macOS, falling back to `gtimeout` or providing an actionable fail-closed error, eliminating confusing failure cascades.
- **Smoke-Test Preflight:** A one-command verification script (`bin/smoke-test.sh`) that checks dependencies, installs requirements in an isolated virtual environment, runs the test suite, verifies the manifest, and checks bundled state files.
- **External Reviewer Documentation:** Comprehensive guides tailored for external technical reviewers, grant evaluators, and researchers, including a Technical Handoff One-Pager, a Grant Handoff Summary, and a Reproducibility Checklist.
- **Manifest Integrity:** A complete SHA-256 manifest covering all files, ensuring the package has not been tampered with.

## Known Limitations

To maintain transparency and claim safety, we explicitly note what this toolkit does **not** currently do:

- **No Runtime Mount Guard:** This toolkit does not actively intercept AI outputs or enforce state mounting at runtime. (This is planned for Layer 2).
- **No Replay Ledger:** It does not provide infrastructure for cross-agent replay, diffing, or auditing of state transitions. (This is planned for Layer 3).
- **No Cross-AI Relay Results Yet:** While designed for cross-model collaboration, empirical results from large-scale relay experiments (e.g., the 10-round relay) are not included in this artifact layer release.
- **Not Enterprise Production Certified:** This is a reference implementation intended for research, evaluation, and integration testing, not a drop-in enterprise production platform.

## Next Work

With Layer 1 (the artifact layer) now stable and released, future development will focus on the higher layers of the architecture:

1. **Layer 2 (Runtime Mount Guard):** Implementing pre-send gates, output guardrails, and round continuity checkers to enforce state mounting during live AI sessions.
2. **Layer 3 (Replay Ledger):** Building the infrastructure for cross-round, cross-model, and cross-agent replay, audit, and fork capabilities.
3. **Cross-Model Relay Experiment:** Conducting and publishing the results of multi-agent relay experiments using diverse LLM backends.
4. **Paper / Technical Report:** Publishing a case study paper detailing the engineering sequence, architectural findings, and the mitigation of AGI drift.

We thank all contributors, reviewers, and the Protocol Seeder for their rigorous feedback and dedication to engineering excellence.
