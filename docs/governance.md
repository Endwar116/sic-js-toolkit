# Governance & Boundary

## Canonical vs. Toolkit Fork

The SIC-JS Toolkit operates on a strict boundary between the **canonical schema** and the **toolkit fork**.

### 1. Canonical Schema
- **Location:** `schema/canonical/sic-js-schema-v2.0.json`
- **Integrity:** Hash-locked (`efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6`). Any modification to this file will cause the validator to exit with code 9 (`CANONICAL_TAMPERED`).
- **Scope:** This is the international standard for SIC-JS v2.0. It defines the core structure of a state object but does **not** include the `upstream_type` field.

### 2. Toolkit Fork
- **Location:** `schema/toolkit/sic-js-schema-v2.0-toolkit.json`
- **Scope:** This is a project-local extension. It is identical to the canonical schema, except it adds the `upstream_type` field to the `relation` object.

## Why `upstream_type` is Project-Local

The `upstream_type` field (`none`, `cryptographic`, `file`) is required by this toolkit to enforce strict validation rules on the `upstream` value (e.g., ensuring a cryptographic upstream is exactly 16 hex characters).

However, this level of strictness is a **project-local implementation detail**. The canonical SIC-JS specification remains flexible to accommodate different runtimes and use cases. Therefore, `upstream_type` is implemented as a fork rather than a modification to the canonical schema.

## Validation Modes

The validator (`src/validator/validate_skeleton_v2.py`) supports two modes:

1. **`--mode canonical`**: Validates against the canonical schema. It will **reject** any JSON containing the `upstream_type` field.
2. **`--mode toolkit`**: Validates against the toolkit fork. It **requires** the `upstream_type` field and enforces the associated logic rules.
