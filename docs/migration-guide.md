# SIC-JS Toolkit Migration Guide

## Overview

This guide explains how to migrate legacy SIC-JS state files to the new toolkit format, which requires the `upstream_type` field.

## What is LEGACY_FORMAT_DETECTED?

If you run the validator in `toolkit` mode on an older SIC-JS file, you will see this error:

```
❌ FAIL [mode=toolkit] [exit=6] LEGACY_FORMAT_DETECTED: 'upstream_type' is a required property
```

This means your JSON file is missing the `upstream_type` field inside the `relation` object. The canonical SIC-JS v2.0 schema does not require this field, but the **toolkit fork** does, in order to explicitly define the relationship between the current state and its upstream source.

## How to Fix It

To fix this, you must manually add the `upstream_type` field to the `relation` object in your JSON file.

### Valid `upstream_type` Values

1. **`none`**: Use this when there is no upstream dependency. The `upstream` field must be `null`.
2. **`cryptographic`**: Use this when the upstream is a 16-character lowercase hex hash.
3. **`file`**: Use this when the upstream is a filename or label (e.g., `XIED_v2.json`).

### Example Migration

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

## Using the Writer

If you are generating new state files, use the provided `sic_write.py` script. It will automatically derive the correct `upstream_type` based on the `upstream` value you provide, ensuring your output is always compliant with the toolkit schema.
