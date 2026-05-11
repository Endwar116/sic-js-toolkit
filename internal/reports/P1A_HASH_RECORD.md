# P1A Hash Record

**Date:** 2026-05-08  
**Authority:** 咩咩 (Manus AI) — F1 P1A execution

---

## Schema Hash Verification

| File | SHA-256 | Status |
|---|---|---|
| `schema/canonical/sic-js-schema-v2.0.json` | `efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6` | ✅ Matches 德德 release pack |
| `schema/toolkit/sic-js-schema-v2.0-toolkit.json` | `fd92237e2bffaad87f7172574aefd3c25c30e09181898e36f7d27bd9a255cb61` | ✅ Toolkit fork (full copy + upstream_type) |

## Source

Canonical schema sourced from 德德 release pack (D-F1-A RESOLVED).  
Hash verified against known-good value from R45 chief engineer review (2026-05-07).

## Verification Command

```bash
sha256sum schema/canonical/sic-js-schema-v2.0.json
# Expected: efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6
```
