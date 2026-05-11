# Backward Compatibility

## Overview

The SIC-JS Toolkit v1.0 introduces the `upstream_type` field in the **toolkit fork** of the schema (`schema/toolkit/sic-js-schema-v2.0-toolkit.json`). This field is required when validating state files in `toolkit` mode.

This document explains how backward compatibility is handled for older SIC-JS state files that do not contain this field.

## What is the "Legacy Format"?

A "legacy format" SIC-JS file is a valid SIC-JS v2.0 file that conforms to the **canonical schema** but lacks the `upstream_type` field required by the toolkit fork.

Example of a legacy format `relation` object:
```json
"relation": {
  "user": "Alice",
  "upstream": "a3f8b2c1d4e5f607"
}
```

## Validation Behavior

When you run the validator (`src/validator/validate_skeleton_v2.py`) on a legacy format file:

1. **Canonical Mode (`--mode canonical`)**: The file will **PASS** validation (exit code 0), because the canonical schema does not require `upstream_type`.
2. **Toolkit Mode (`--mode toolkit`)**: The file will **FAIL** validation with exit code 6 (`LEGACY_FORMAT_DETECTED`).

```bash
$ python3 src/validator/validate_skeleton_v2.py --file legacy.json --mode toolkit
❌ FAIL [mode=toolkit] [exit=6] LEGACY_FORMAT_DETECTED: 'upstream_type' is a required property
```

## Manual Migration

**There is no automated migration script.** As decided by the project governance (Decision D-MIGRATE-A), users must manually update their legacy files to comply with the toolkit schema.

To migrate a legacy file, you must add the `upstream_type` field to the `relation` object. The value must be one of: `none`, `cryptographic`, or `file`.

### Before/After Example

**Before (Legacy Format):**
```json
{
  "sic_version": "2.0",
  "round": 1,
  "entity": { "name": "Agent", "model": "Model" },
  "state": { "context": "...", "current_action": "..." },
  "relation": {
    "user": "Alice",
    "upstream": "a3f8b2c1d4e5f607"
  },
  "event": null,
  "intent": null
}
```

**After (Toolkit Format):**
```json
{
  "sic_version": "2.0",
  "round": 1,
  "entity": { "name": "Agent", "model": "Model" },
  "state": { "context": "...", "current_action": "..." },
  "relation": {
    "user": "Alice",
    "upstream_type": "cryptographic",
    "upstream": "a3f8b2c1d4e5f607"
  },
  "event": null,
  "intent": null
}
```

For more details on choosing the correct `upstream_type`, see the [Migration Guide](migration-guide.md).
