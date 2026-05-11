# SIC-JS Toolkit v1.0.0 — External Reviewer Guide

Welcome. If you are an external technical reviewer, grant evaluator, or research partner, this guide is designed to help you navigate and evaluate the SIC-JS Toolkit v1.0.0 efficiently.

## Recommended Review Path

To understand the context, verify the artifacts, and evaluate the architecture, we recommend the following sequence:

1. **Context (3 minutes):** Read `TECHNICAL_HANDOFF_ONE_PAGER.md` to understand what this toolkit is, what it is not, and why it exists.
2. **Verification (5 minutes):** Run the smoke-test to verify reproducibility in your environment.
   ```bash
   bash bin/smoke-test.sh
   ```
3. **Orientation (5 minutes):** Read `README.md` and `PACKAGE_MAP.md` to understand the directory structure and usage instructions.
4. **Architecture (10 minutes):** Review the schema boundary and examples.
   - Read `schema/README.md` to understand the separation between the canonical schema and the toolkit fork.
   - Inspect the JSON files in `examples/`.
5. **Governance (5 minutes):** Review `RELEASE_STATUS.md` and `CLAIM_BOUNDARY.md` to evaluate the project's engineering rigor and claim safety.
6. **Integrity (2 minutes):** Verify the package manifest.
   ```bash
   sha256sum -c MANIFEST.sha256
   ```

## What to Evaluate

We invite you to evaluate the toolkit across the following dimensions:

### 1. Reproducibility
Does the test suite (`tests/run_tests.sh`) execute reliably in your environment? Does the smoke-test (`bin/smoke-test.sh`) correctly identify missing dependencies and fail-close with actionable remediation?

### 2. Schema Boundary
Is the separation between the hash-locked canonical schema (`schema/canonical/`) and the extensible toolkit schema (`schema/toolkit/`) clear and technically sound?

### 3. CLI Usability
Are the writer (`src/writer/sic_write.py`), validator (`src/validator/validate_skeleton_v2.py`), and verifier (`src/verifier/sic_verify.sh`) intuitive and well-documented? Do they handle edge cases gracefully?

### 4. Documentation Clarity
Are the user-facing documents (`README.md`, `QUICKSTART.md`, `TROUBLESHOOTING.md`) clear, accurate, and helpful?

### 5. Claim Safety
Does the project maintain strict boundaries regarding what it achieves? (See `CLAIM_BOUNDARY.md`). Are the limitations honestly disclosed?

### 6. Packaging Hygiene
Is the release package clean? (e.g., no `__pycache__`, no `.git`, correct `VERSION`, formal `LICENSE`, accurate `MANIFEST.sha256`).

## Internal Materials

You will notice an `internal/` directory containing post-change reports and governance materials. These are preserved for traceability and audit purposes but are **not required** for normal installation, use, or technical evaluation of the toolkit itself.

Thank you for your time and rigorous review.
