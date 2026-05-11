# SIC-JS Toolkit v1.0 Release Checklist

**Date:** 2026-05-08  
**Target Version:** 1.0.0-rc.1  
**Status:** READY FOR FINAL SIGN-OFF

---

## Gate 1: Schema fork complete and tested
- [x] `schema/canonical/sic-js-schema-v2.0.json` hash is `efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6`
- [x] `schema/toolkit/sic-js-schema-v2.0-toolkit.json` contains `upstream_type`
- **Status: ✅ PASS**

## Gate 2: Writer/Verifier synchronized
- [x] W1-W6 writer tests PASS
- [x] V1-V10 verifier tests PASS (including correct rejections)
- [x] C1-C3 consistency tests PASS
- **Status: ✅ PASS**

## Gate 3: Test suite reproducible
- [x] No hardcoded paths (`/home/ubuntu/`, etc.) in test runners
- [x] `tests/TEST_MATRIX.md` documents all 20 cases
- [x] 20/20 PASS in clean environment (`pip install -r requirements.txt && bash tests/run_tests.sh`)
- **Status: ✅ PASS**

## Gate 4: Documentation complete
- [x] `README.md` includes Quick Start
- [x] `README.md` explicitly states what the toolkit is NOT
- [x] `docs/governance.md` explains canonical vs toolkit boundary
- [x] `examples/` contains valid JSON for all three `upstream_type` values
- **Status: ✅ PASS**

## Gate 5: Backward compatibility defined
- [x] `docs/backward-compatibility.md` exists
- [x] `LEGACY_FORMAT_DETECTED` (exit 6) is documented
- [x] Manual migration before/after examples provided
- **Status: ✅ PASS**

## Gate 6: No DECISION_REQUIRED pending
- [x] D-F0-A (F0 approval): CLOSED
- [x] D-F1-B (F1 coding authorization): CLOSED
- [x] D-MIGRATE-A (Migration script): CLOSED (Option A: Docs only)
- [x] D-INSTR-COMMIT (Project instruction): CLOSED
- **Status: ✅ PASS**

## Gate 7: Release approved by 安安 + 德德
- [ ] 老翔 governance review
- [ ] 德德 architecture sign-off
- [ ] 安安 final release ruling
- **Status: ⏳ PENDING**
