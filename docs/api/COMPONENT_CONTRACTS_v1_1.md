# Component Contracts v1.1 — Patch Update
# 修正 CMP-03/04/05 + CMP-13 架構裁定

**Date**: 2026-05-02
**Authority**: 德德（架構裁定）× 安安（2026-05-01 裁定 CMP-13 架構）
**Supersedes**: CMP-03/04/05 in COMPONENT_CONTRACTS/ (老翔 International Handoff Pack v1.0)

---

## CMP-03 Validator — v1.1（修正）

### 修正點
1. `--mode` default 明確定義
2. `--mode` vs `--toolkit-mode` 衝突行為定義

### CLI（完整）
```bash
python3 validators/validate_skeleton_v2.py \
  --file <path> \
  [--mode canonical|toolkit] \
  [--level 1|2|3] \  # RESERVED_FOR_FUTURE: accepted but has no behavior in v1.x
  [--json]

# Shortcut（等同於 --mode toolkit）：
python3 validators/validate_skeleton_v2.py --file <path> --toolkit-mode
```

### Mode 規則（新增）
```
Default mode: canonical
  → 不傳 --mode 時，走 canonical schema 驗證
  → canonical mode 拒絕 upstream_type 欄位

--toolkit-mode 是 --mode toolkit 的 shorthand
  → 兩者語義相同

衝突處理（新增）：
  → --mode canonical --toolkit-mode → INVALID_USAGE (exit 2)
  → --mode toolkit --toolkit-mode → INVALID_USAGE (exit 2)（任何 --mode 和 --toolkit-mode 同時出現一律拒絕）
  → --mode canonical --mode toolkit → INVALID_USAGE (exit 2)
  → 若只有 --mode，--mode 優先
```

### Error Codes（不變）
| Code | Exit | Meaning |
|------|------|---------|
| — | 0 | PASS |
| VALIDATION_FAILED | 1 | validation failed |
| INVALID_USAGE | 2 | bad CLI or conflicting flags |
| INPUT_NOT_FOUND | 3 | input file missing |
| SCHEMA_NOT_FOUND | 4 | schema file missing |
| UNSAFE_UPSTREAM | 5 | unsafe upstream value |
| LEGACY_FORMAT_DETECTED | 6 | upstream_type missing in toolkit mode |
| INTERNAL_ERROR | 7 | unexpected error |

### Boundary Behavior（不變）
- no file mutation
- no silent migration
- toolkit mode validates upstream/upstream_type consistency
- string "null" is not JSON null

---

## CMP-04 Writer — v1.1（修正）

### 修正點
1. `--mode` default 明確定義

### CLI（完整）
```bash
bash scripts/sic_write.sh \
  --entity-name <name> \
  --context <text> \
  [--upstream <value>] \
  [--upstream-type none|cryptographic|file] \
  [--output <path>] \
  [--mode canonical|toolkit] \
  [--json]
```

### Mode 規則（新增）
```
Default mode: canonical
  → 不傳 --mode 時，產出 canonical 格式（不含 upstream_type）
  → toolkit mode 時，產出含 upstream_type 的格式
```

### Auto-Derive（不變，但加 canonical note）
```
只有 --mode toolkit 時才 auto-derive upstream_type
Canonical mode 不產出 upstream_type
```

| upstream | derived type |
|----------|-------------|
| missing/null | none |
| 16 lowercase hex | cryptographic |
| safe non-empty non-hex | file |

Auto-derive log: `[WRITER] auto-derived upstream_type=X (convenience behavior, not protocol rule)`

### Boundary Behavior（不變）
- upstream_type=none → upstream=null
- cryptographic requires 16 lowercase hex
- file requires safe semantic label
- unsafe label → FAIL
- writer output must pass validator with same --mode

---

## CMP-05 Verifier — v1.1（不變）

Verifier 的 contract 不需要修正。`--mode` default 繼承自 CMP-03。

---

## CMP-13 Ledger System — 架構裁定（新增）

### 安安裁定（2026-05-01）
```
安安裁定：「帳本格式是 SIC-JS 作為一個欄位放在帳本 JSON 裡，
          不是直接用 SIC-JS 加欄位。（IP/TCP 邏輯）」
```

### 架構設計（RESOLVED）
```
帳本一筆紀錄的格式：

{
  "ledger_id": "session_<id>_round_<N>",
  "session_id": "<global_unique_id>",
  "timestamp": "<ISO8601>",
  "files_produced": ["<path>", ...],
  "slack_refs": ["<ts>", ...],
  "is_correction": false,
  "corrects_round": null,
  "checksum": "<sha256 of key fields>",
  "sic_js": {
    "sic_version": "2.0",
    "round": N,
    "entity": {...},
    "state": {...},
    "relation": {...},
    "event": {...},
    "intent": {...}
  }
}

重點：
- SIC-JS block 是 "sic_js" 欄位，原封不動，不加不改
- 帳本格式是帳本自己的格式
- session_id 解決 round 碰撞問題（不同 session 都有 round=1）
- checksum = sha256(session_id + round + timestamp + event.description)
```

### CMP-13 Scope Ruling（新增）
```
COMPONENT_SCOPE_RULING
candidate: CMP-13 (Ledger System)
decision: DEFER_V1_1
reason: 帳本格式已裁定，但實作超出 toolkit v1.0 核心範圍。
        sic-state/ 目錄已在 P0 closure package 中存在，
        但正式成為 toolkit 組件需要 v1.1 規劃。
required_contract: 帳本格式（本文件已定義）
required_tests: 待 v1.1 定義
owner: 德德（架構）× 安安（裁決）
```

---

**文件結束**
**產出者**：德德（Wei De）
**日期**：2026-05-02
**Status**：ACTIVE — 取代 老翔 pack 中的對應 contracts
