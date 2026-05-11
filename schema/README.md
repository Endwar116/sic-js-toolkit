# SIC-JS Schema Directory

**Authority:** 德德（架構）× 安安（最終裁決）  
**Status:** F1 Active — P1A Closed  
**Last updated:** 2026-05-08

---

## Two Schemas, One Bloodline

This directory contains two schema files that share the same canonical core but serve different purposes.

### `canonical/sic-js-schema-v2.0.json`

The **canonical SIC-JS v2.0 schema**. This is the international protocol-level definition. It is frozen.

- **SHA-256:** `efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6`
- **Source:** 德德 release pack (D-F1-A RESOLVED)
- **Rule:** `additionalProperties: false` — no extensions allowed
- **Does NOT contain:** `upstream_type`
- **Use when:** Validating SIC-JS JSON for cross-system, cross-organization, or international runtime use

### `toolkit/sic-js-schema-v2.0-toolkit.json`

A **project-local fork** of the canonical schema. It adds one field: `upstream_type`.

- **SHA-256:** `fd92237e2bffaad87f7172574aefd3c25c30e09181898e36f7d27bd9a255cb61`
- **Fork method:** Full copy (NOT `allOf`/`$ref` inheritance — per P1A spec)
- **Extension:** `relation.upstream_type` — `enum: ["none", "cryptographic", "file"]`
- **Declaration:** `upstream_type` is a **PROJECT-LOCAL EXTENSION. NOT SIC-JS v2.0 canonical.**
- **Use when:** Validating SIC-JS JSON produced by the SIC-JS Toolkit within this project

---

## The Boundary Rule

> `upstream_type` MUST NOT be written into the canonical schema.  
> Any SIC-JS JSON that includes `upstream_type` will be **rejected** by canonical mode validation.  
> This is correct behavior, not a bug.

---

## Decision Reference

- **D-F1-A:** RESOLVED — 德德 release pack is the canonical source of truth for `sic-js-schema-v2.0.json`
- **D-F0-A:** CLOSED — F0 formally approved by Anan 2026-05-08
- **D-F1-B:** CLOSED — F1 coding authorized by Anan 2026-05-08
