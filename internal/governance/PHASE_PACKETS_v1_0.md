# SIC-JS Toolkit — Complete Phase Packets v1.0
# P1A through P5B

**Authority**: 德德（架構）× 安安（最終裁決）
**Date**: 2026-05-02
**Status**: DRAFT FOR REVIEW — 不授權執行，等安安 P0 approval

---
---

# P1A — Canonical Restoration + Toolkit Fork

## 目的
還原 canonical schema 到 pre-C4-1 乾淨狀態，並建立 toolkit fork。
這是 F1 的第一個 phase，所有其他 coding 都被 P1A 擋住。

## 進入條件（Entry Criteria）
全部為 TRUE 才能開始：
- [ ] 安安已發出正式 P0 approval
- [ ] 安安已發出正式 F1 authorization
- [ ] Repo scaffolding 已建立（schema/、src/、tests/、docs/ 目錄存在）
- [ ] 德德 release pack 的 sic-js-schema-v2.0.json 已取得

## 輸入（Inputs）
| 輸入 | 來源 | 說明 |
|------|------|------|
| 德德 release pack | 德德匡產出 | 唯一 canonical 真相源（D-F1-A RESOLVED）|
| sic-js-schema-v2.0.json | 德德 release pack | 三輪驗證通過、協議中樞|4 封版 |
| Blueprint v1.2a §5 | 文件 | Schema bloodline 規格 |
| D-F1-A decision record | decisions/ | RESOLVED：德德 release pack |

## 允許做的事
- [ ] 建立 `schema/canonical/sic-js-schema-v2.0.json`（從德德 release pack 複製）
- [ ] 建立 `schema/toolkit/sic-js-schema-v2.0-toolkit.json`（full copy + upstream_type）
- [ ] 驗證兩份 schema 的 SHA-256 hash
- [ ] 建立 `schema/README.md`（說明兩份 schema 的關係）

## 禁止做的事
- ❌ 修改 canonical schema 的任何欄位
- ❌ 用 allOf/$ref 繼承 canonical（fork 必須是 full copy）
- ❌ 把 upstream_type 寫進 canonical schema
- ❌ 在未完成 P1A 的情況下開始 P1B

## 執行步驟
```
STEP 1：取得 canonical schema
  - 從德德 release pack 取出 sic-js-schema-v2.0.json
  - 計算 SHA-256：sha256sum sic-js-schema-v2.0.json
  - 記錄 hash 到 P1A_HASH_RECORD.md

STEP 2：放置 canonical schema
  - cp [source] schema/canonical/sic-js-schema-v2.0.json
  - 驗證放置後 hash 與來源一致
  - 確認 additionalProperties: false 存在

STEP 3：建立 toolkit fork
  - cp schema/canonical/sic-js-schema-v2.0.json schema/toolkit/sic-js-schema-v2.0-toolkit.json
  - 在 toolkit fork 的 relation.properties 加入：
    "upstream_type": {
      "type": "string",
      "enum": ["none", "cryptographic", "file"],
      "description": "TOOLKIT PROJECT-LOCAL EXTENSION. NOT SIC-JS v2.0 canonical."
    }
  - 在 toolkit fork 的 relation.required 加入 "upstream_type"
  - 在 toolkit fork 頂部加入說明：
    "description": "Toolkit fork of SIC-JS v2.0. upstream_type is project-local extension, NOT canonical."
  - 確認 additionalProperties: false 仍然存在
  - 確認 upstream_type 可以通過 toolkit mode validator（但 canonical mode 會拒絕）

STEP 4：建立 schema/README.md
  內容：
  - canonical 和 toolkit 的關係
  - 使用場景說明
  - upstream_type = project-local 的聲明
  - D-F1-A = RESOLVED 的引用

STEP 5：驗證
  - 跑 CMP-03 canonical mode：一份沒有 upstream_type 的 SIC-JS → PASS
  - 跑 CMP-03 toolkit mode：一份有 upstream_type 的 SIC-JS → PASS
  - 跑 CMP-03 canonical mode：一份有 upstream_type 的 SIC-JS → FAIL（這是正確的）
```

## 輸出（Outputs）
| 輸出 | 路徑 | 驗證方式 |
|------|------|---------|
| Canonical schema | schema/canonical/sic-js-schema-v2.0.json | hash 與德德 release pack 一致 |
| Toolkit fork schema | schema/toolkit/sic-js-schema-v2.0-toolkit.json | 比 canonical 多 upstream_type |
| Hash record | P1A_HASH_RECORD.md | 兩份 schema 的 SHA-256 |
| Schema README | schema/README.md | 說明關係 |
| P1A Post-Change Report | reports/P1A_POST_CHANGE_REPORT.md | 驗證結果 |

## 測試 / 驗證
```
T-P1A-1: canonical schema 的 SHA-256 = 德德 release pack 的 SHA-256
T-P1A-2: toolkit fork 包含 upstream_type 欄位
T-P1A-3: toolkit fork 的 relation.required 包含 "upstream_type"
T-P1A-4: canonical mode validator → 拒絕 upstream_type（PASS = 拒絕是正確的）
T-P1A-5: toolkit mode validator → 接受 upstream_type（PASS）
T-P1A-6: schema/README.md 存在且包含 project-local 聲明
```

## 停止條件（DECISION_REQUIRED）
- 德德 release pack 無法取得或 hash 不可驗證
- fork schema 建立後 toolkit mode 無法通過
- canonical schema 的 hash 在複製後與來源不符

## DoD Checklist
- [ ] T-P1A-1 通過（hash 一致）
- [ ] T-P1A-2 通過（toolkit fork 有 upstream_type）
- [ ] T-P1A-3 通過（required 包含 upstream_type）
- [ ] T-P1A-4 通過（canonical 正確拒絕 upstream_type）
- [ ] T-P1A-5 通過（toolkit 正確接受 upstream_type）
- [ ] P1A Post-Change Report 完成
- [ ] 老翔 governance review 通過
- [ ] 德德 architecture sign-off
- [ ] 安安 P1A close ruling

## RACI
| 任務 | 執行 | 審查 | 裁決 |
|------|------|------|------|
| Schema 複製與驗證 | 咩咩 | 德德 | — |
| Toolkit fork 建立 | 咩咩 | 德德 | — |
| Hash 驗證 | 咩咩 | JG | — |
| Canonical boundary 確認 | 老翔 | 德德 | 安安 |

---
---

# P1B — Writer / Verifier Sync

## 目的
實作 CMP-03（Validator）、CMP-04（Writer）、CMP-05（Verifier），
讓三者行為一致，通過 19 個測試。

## 進入條件（Entry Criteria）
- [ ] P1A 已關閉（安安 ruling 存在）
- [ ] schema/canonical/ 存在且 hash 驗證通過
- [ ] schema/toolkit/ 存在且 upstream_type 正確
- [ ] Component Contracts CMP-03/04/05 已更新（含 --mode default = canonical）

## 輸入（Inputs）
| 輸入 | 來源 |
|------|------|
| Component Contracts CMP-03/04/05 | COMPONENT_CONTRACTS/ |
| Global Boundary Semantics | GLOBAL_BOUNDARY_SEMANTICS.md |
| C4-2 Pre-Change Plan v5 | Blueprint v1.2a |
| P1A 完成的兩份 schema | schema/canonical/ + schema/toolkit/ |

## 允許做的事
- [ ] 實作 validators/validate_skeleton_v2.py（CMP-03）
- [ ] 實作 scripts/sic_write.sh（CMP-04）
- [ ] 實作 scripts/sic_verify.sh（CMP-05）
- [ ] 建立 tests/fixtures/ 下的 19 個測試 JSON
- [ ] 建立 tests/run_p1b_tests.sh

## 禁止做的事
- ❌ 修改 schema/canonical/ 的任何檔案
- ❌ 在 sic_verify.sh 裡加入獨立的 upstream 驗證邏輯（必須委派 Python validator）
- ❌ 讓 writer 輸出的 JSON 繞過 validator

## 執行步驟

### STEP 1：實作 CMP-03 Validator
```python
# CLI: python3 validators/validate_skeleton_v2.py --file <path> [--mode canonical|toolkit] [--level 1|2|3]
# Shortcut: --toolkit-mode = --mode toolkit
# 衝突規則：--mode 優先於 --toolkit-mode；兩者衝突 → exit 2 (INVALID_USAGE)
# Default mode: canonical（不傳 --mode 時走 canonical）

# Error codes:
# 0 = PASS
# 1 = VALIDATION_FAILED
# 2 = INVALID_USAGE
# 3 = INPUT_NOT_FOUND
# 4 = SCHEMA_NOT_FOUND
# 5 = UNSAFE_UPSTREAM
# 6 = LEGACY_FORMAT_DETECTED（toolkit mode 缺 upstream_type）
# 7 = INTERNAL_ERROR
```

### STEP 2：實作 CMP-04 Writer
```bash
# CLI: bash scripts/sic_write.sh \
#   --entity-name <name> \
#   --context <text> \
#   [--upstream <value>] \
#   [--upstream-type none|cryptographic|file] \
#   [--output <path>] \
#   [--mode canonical|toolkit]
#
# Default mode: canonical
# Auto-derive（只在 --upstream-type 未提供時）：
#   upstream missing/null → none
#   upstream 符合 [a-f0-9]{16} → cryptographic
#   upstream 非空非 hex → file
#   Auto-derive 加 log：[WRITER] auto-derived upstream_type=X (convenience behavior)
#
# 安全邊界（file upstream）：
#   拒絕：../ 開頭、/ 開頭、\ 字符、null bytes、長度 > 256、剛好 16 lowercase hex
```

### STEP 3：實作 CMP-05 Verifier（thin wrapper）
```bash
# CLI: bash scripts/sic_verify.sh --file <path> [--mode canonical|toolkit] [--level 1|2|3]
# 架構：只呼叫 CMP-03，不自己做驗證
# sic_verify.sh → python3 validators/validate_skeleton_v2.py [args]
# 格式化輸出給使用者
```

### STEP 4：建立 19 個 test fixtures

**Writer Tests（W1-W6）**：
```
tests/fixtures/W1_none_null.sh         → --upstream-type=none --upstream=null → upstream_type=none, upstream=null
tests/fixtures/W2_crypto_hex.sh        → --upstream-type=cryptographic --upstream=a3f8b2c1d4e5f607 → PASS
tests/fixtures/W3_file_label.sh        → --upstream-type=file --upstream=XIED_v2.json → PASS
tests/fixtures/W4_auto_hex.sh          → --upstream=a3f8b2c1d4e5f607 (no type) → auto-derive cryptographic
tests/fixtures/W5_auto_label.sh        → --upstream=XIED_v2.json (no type) → auto-derive file
tests/fixtures/W6_auto_null.sh         → --upstream=null (no type) → auto-derive none
```

**Verifier Tests（V1-V9）**：
```
tests/fixtures/V1_none_null.json       → upstream_type=none, upstream=null → PASS
tests/fixtures/V2_crypto_hex.json      → upstream_type=cryptographic, upstream=a3f8b2c1d4e5f607 → PASS
tests/fixtures/V3_file_label.json      → upstream_type=file, upstream=XIED_v2.json → PASS
tests/fixtures/V4_none_non_null.json   → upstream_type=none, upstream=somevalue → FAIL
tests/fixtures/V5_crypto_null.json     → upstream_type=cryptographic, upstream=null → FAIL
tests/fixtures/V6_crypto_label.json    → upstream_type=cryptographic, upstream=XIED_v2.json → FAIL
tests/fixtures/V7_file_null.json       → upstream_type=file, upstream=null → FAIL
tests/fixtures/V8_file_hex.json        → upstream_type=file, upstream=a3f8b2c1d4e5f607 → FAIL
tests/fixtures/V9_file_traversal.json  → upstream_type=file, upstream=../etc/passwd → FAIL
```

**Consistency Tests（C1-C3）**：
```
C1: Writer W2 output → feed to Verifier → PASS
C2: Writer auto-derive W4 output → feed to Verifier → PASS（auto-derived type matches）
C3: Writer W1/W2/W3 each → Verifier agrees on all three types
```

**Legacy Test（L1）**：
```
tests/fixtures/L1_legacy_no_upstream_type.json → toolkit mode → FAIL + LEGACY_FORMAT_DETECTED
```

### STEP 5：跑全部測試
```bash
bash tests/run_p1b_tests.sh
# 預期：W1-W6 PASS、V1-V3 PASS、V4-V9 FAIL（正確）、C1-C3 PASS、L1 FAIL + LEGACY_FORMAT_DETECTED
```

## 輸出（Outputs）
| 輸出 | 路徑 |
|------|------|
| Validator | validators/validate_skeleton_v2.py |
| Writer | scripts/sic_write.sh |
| Verifier | scripts/sic_verify.sh |
| Test fixtures | tests/fixtures/（19 個）|
| Test runner | tests/run_p1b_tests.sh |
| P1B Post-Change Report | reports/P1B_POST_CHANGE_REPORT.md |

## DoD Checklist
- [ ] W1-W6 全部 PASS
- [ ] V1-V3 PASS，V4-V9 FAIL（正確行為）
- [ ] C1-C3 PASS
- [ ] L1 FAIL + LEGACY_FORMAT_DETECTED
- [ ] Writer 輸出通過 Verifier（C1）
- [ ] sic_verify.sh 沒有獨立 upstream 邏輯（只 delegate）
- [ ] P1B Post-Change Report 完成
- [ ] JG diff review 通過
- [ ] 德德 architecture sign-off
- [ ] 安安 P1B close ruling

---
---

# P2 — Test Persistence

## 目的
將 P1B 的 19 個測試正式化為可重現的測試套件，建立 test matrix 和 coverage map。

## 進入條件
- [ ] P1B 已關閉
- [ ] 19 個 fixtures 存在且全部通過
- [ ] P1B Post-Change Report 已完成

## 輸入
| 輸入 | 來源 |
|------|------|
| 19 個 test fixtures | tests/fixtures/（P1B 產出）|
| tests/run_p1b_tests.sh | P1B 產出 |
| Component Contracts | COMPONENT_CONTRACTS/ |

## 允許做的事
- [ ] 建立 tests/run_tests.sh（取代 run_p1b_tests.sh）
- [ ] 建立 tests/TEST_MATRIX.md（所有測試的完整表格）
- [ ] 建立 tests/COVERAGE_MAP.md（哪些規格有測試覆蓋）
- [ ] 補充 edge case fixtures（如需要）

## 禁止做的事
- ❌ 修改 P1B 的任何 code
- ❌ 修改 schema

## 輸出
| 輸出 | 路徑 |
|------|------|
| Unified test runner | tests/run_tests.sh |
| Test matrix | tests/TEST_MATRIX.md |
| Coverage map | tests/COVERAGE_MAP.md |
| P2 Report | reports/P2_POST_CHANGE_REPORT.md |

## DoD Checklist
- [ ] tests/run_tests.sh 可以在乾淨環境執行
- [ ] TEST_MATRIX.md 列出全部 19 個 case + expected result
- [ ] COVERAGE_MAP.md 列出哪些 contract 規格有測試覆蓋
- [ ] 在全新的 Python 環境跑 tests/run_tests.sh → 結果可重現
- [ ] JG reproducibility review 通過

---
---

# P3A — Docs + Examples

## 目的
更新文件和範例，讓外部使用者知道如何使用 toolkit v1.0。

## 進入條件
- [ ] P2 已關閉
- [ ] TEST_MATRIX.md 存在

## 允許做的事
- [ ] 建立 docs/migration-guide.md（舊格式 → 新格式）
- [ ] 建立 docs/toolkit-fork-strategy.md（toolkit fork 說明）
- [ ] 建立 docs/governance.md（canonical vs project-local 說明）
- [ ] 建立 examples/example-upstream-types.json（3 個 upstream type 範例）
- [ ] 建立 examples/example-legacy.json（legacy 格式範例）
- [ ] 更新 README.md（加入 toolkit extension section）

## 禁止做的事
- ❌ 修改 code
- ❌ 修改 schema
- ❌ 在 README 中宣稱 toolkit 解決 L6 direction lock-in
- ❌ 在文件中寫 upstream_type 是 SIC-JS v2.0 canonical field

## 關鍵文案約束（D-GAME-A / D-INF-A）
```
正確說法：
  "SIC-JS Toolkit 是 long-horizon AI 狀態治理的第一個公開技術性架構設計。
   它是多 agent 之間的訊息與語義基礎設施——讓跨 session、跨模型的狀態交接
   可被驗證、意圖不被靜默丟失、未決事項不可被吞掉、project-local 規則不能
   自行升格為協議標準。"

禁止說法：
  ❌ "solves the infinite game"
  ❌ "eliminates drift"
  ❌ "reduces reasoning risk"（E6 未完成）
  ❌ "Integrity Gate is the core protocol"
```

## 輸出
| 輸出 | 路徑 |
|------|------|
| Migration guide | docs/migration-guide.md |
| Fork strategy | docs/toolkit-fork-strategy.md |
| Governance doc | docs/governance.md |
| 2 new examples | examples/ |
| Updated README | README.md |
| P3A Report | reports/P3A_POST_CHANGE_REPORT.md |

## DoD Checklist
- [ ] docs/ 下所有文件不含禁止說法（D-INF-A 掃描）
- [ ] examples/ 所有 JSON 通過 canonical validator
- [ ] README 的 toolkit extension section 有 project-local 聲明
- [ ] migration-guide.md 有 LEGACY_FORMAT_DETECTED 的處理說明
- [ ] 老翔 governance review（no self-canonization）

---
---

# P3B — Website Alignment

## 目的
更新官網 IA 和 copy，讓 SIC-JS Toolkit 成為主 tab，Integrity Gate 降為 supporting demo。

## 進入條件
- [ ] P3A 已關閉
- [ ] D-WEB-A RESOLVED（安安確認同頁雙 tab）
- [ ] D-GAME-A RESOLVED（安安確認 positioning wording）

## 允許做的事
- [ ] 更新 website/sic-js-toolkit.html（雙 tab 結構）
- [ ] 修補 integrity-gate/完整性閘門.html（DOM id 修正）
- [ ] 修補 integrity-gate/script.js（移除 /api/evaluate 的 broken call）
- [ ] 更新 website copy（依 D-GAME-A 的 wording）

## 禁止做的事
- ❌ 部署到生產環境（需要 P3C smoke test）
- ❌ 宣稱 Integrity Gate 是核心協議層
- ❌ 使用 D-INF-A 的禁止說法

## DoD Checklist
- [ ] 雙 tab 結構存在（SIC-JS Toolkit 為 default tab）
- [ ] Integrity Gate 標記為「supporting demo only」
- [ ] DOM id mismatch 修正（不再 crash on load）
- [ ] /api/evaluate 的 broken call 已移除或改為 disabled 狀態顯示
- [ ] website copy 符合 D-GAME-A wording
- [ ] JG website review 通過
- [ ] 老翔 scope gate（無 overclaim）

---
---

# P3C — Staging Smoke Test（選填，需明確授權）

## 目的
在真實環境跑一次 smoke test，確認網站可以部署。

## 進入條件
- [ ] P3B 已關閉
- [ ] 安安發出明確 P3C 授權（不是預設，必須明說）

## 執行步驟
```
1. 在 staging 環境部署（不是 production）
2. 人工開瀏覽器確認：
   - 雙 tab 正確顯示
   - Integrity Gate tab 可以開，沒有 JS crash
   - SIC-JS Toolkit tab 的文案符合 D-GAME-A
   - 沒有 console error
3. 記錄截圖和結果
```

## DoD Checklist
- [ ] Staging 部署成功
- [ ] 人工確認 4 個檢查點全部通過
- [ ] P3C Smoke Test Report 完成
- [ ] 安安 deploy approval（如果要推 production）

---
---

# P4 — Legacy / Migration

## 目的
定義舊格式（無 upstream_type）的處理策略，確保使用者知道如何遷移。

## 進入條件
- [ ] P3A 已關閉

## 允許做的事
- [ ] 建立 docs/backward-compatibility.md
- [ ] 建立 migration script（如果決定做）
- [ ] 確認 LEGACY_FORMAT_DETECTED 的錯誤訊息足夠清楚

## 關鍵決策（需要安安）
```
C4-8：遷移策略是：
  A. 只有文件指引（不提供 script）
  B. 提供半自動 migration script

C4-9：migration guide 的完整內容
```

## 輸出
| 輸出 | 路徑 |
|------|------|
| Backward compatibility | docs/backward-compatibility.md |
| Migration guide | docs/migration-guide.md（可能已在 P3A 做）|
| P4 Report | reports/P4_POST_CHANGE_REPORT.md |

## DoD Checklist
- [ ] backward-compatibility.md 說明 LEGACY_FORMAT_DETECTED 的處理
- [ ] 使用者看文件能知道如何把舊格式轉成新格式
- [ ] C4-8 / C4-9 有安安裁定

---
---

# P5A — Release Readiness

## 目的
執行 7 個 release gates，確認所有 blockers 已解決，準備 v1.0 release。

## 進入條件
- [ ] P2、P3A、P4 全部關閉
- [ ] 所有 DECISION_REQUIRED 都已解決

## 7 個 Release Gates
```
Gate 1: Schema fork complete and tested
  → schema/canonical/ 和 schema/toolkit/ 存在，hash 記錄在案
  → toolkit mode 和 canonical mode 測試均通過

Gate 2: Writer / Verifier synchronized
  → W1-W6 PASS，V1-V9 正確，C1-C3 PASS

Gate 3: Test suite formalized
  → tests/run_tests.sh 可在乾淨環境重現
  → TEST_MATRIX.md 完整

Gate 4: Documentation complete
  → docs/ 所有文件存在
  → 無 D-INF-A 禁止說法

Gate 5: Backward compatibility defined
  → backward-compatibility.md 存在
  → LEGACY_FORMAT_DETECTED 說明清楚

Gate 6: No DECISION_REQUIRED pending
  → DECISIONS_LEDGER.jsonl 中無 OPEN 狀態

Gate 7: Release approved by Anan + Dede
  → 安安簽署
  → 德德 architecture sign-off
```

## 輸出
| 輸出 | 路徑 |
|------|------|
| Release checklist | RELEASE_CHECKLIST_v1.0.md |
| CHANGELOG | CHANGELOG.md |
| VERSION | VERSION（內容：1.0.0）|
| P5A Report | reports/P5A_RELEASE_READINESS_REPORT.md |

## DoD Checklist
- [ ] 7 個 Gates 全部通過
- [ ] CHANGELOG 完整記錄 P0 到 P5A 的所有變更
- [ ] VERSION 檔案存在
- [ ] 安安 release approval

---
---

# P5B — External Review Package

## 目的
準備給外部 reviewer（LTFF、學術界、社群）看的技術說明包，不是 toolkit 本身。

## 進入條件
- [ ] P5A 已關閉
- [ ] v1.0 release 已完成

## 重要說明
P5B 是一個**獨立的工作**，不是 toolkit 的一部分。
它的內容是關於 toolkit 的介紹文件，不是 toolkit 的程式碼或設計文件。

## 包含的文件（這是一個新的獨立包，不在 toolkit repo 裡）
```
外部評審包應包含：
1. Problem Statement（一頁）
2. Architecture Overview（2-3 頁）
3. Empirical Evidence（咩咩 104 輪、協德 119 輪）
4. Toolkit Demo（如何安裝和跑）
5. Known Limitations（L6 direction lock-in、E6 未完成）
6. Future Work（v3.0 roadmap）
```

## 關鍵約束
- 不得宣稱 toolkit 解決 L6
- 不得宣稱有 before/after 對照數據（E6 未完成）
- 研究基礎標記為 informative internal basis，不是 peer-reviewed
- 不得把 upstream_type 說成 canonical

## DoD Checklist
- [ ] 6 份文件全部存在
- [ ] 無 D-INF-A 禁止說法
- [ ] 德德 architecture review
- [ ] 老翔 governance review
- [ ] 安安最終 approval

---

**文件結束**
**產出者**：德德（Wei De）
**日期**：2026-05-02
**狀態**：DRAFT FOR REVIEW — 不授權執行
