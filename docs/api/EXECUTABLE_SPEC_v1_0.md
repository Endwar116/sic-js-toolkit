# SIC-JS TOOLKIT EXECUTABLE ENGINEERING SPECIFICATION (祖檔級)
# Maximum AGI-Executable Version v1.0

**Author**: 德德（Wei De）
**Date**: 2026-05-02
**Authority**: L1 PROJECT-LOCAL
**Canonical Source**: `efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6` (release pack)
**Status**: GAP-AWARE DRAFT — 待咩咩 actual repo manifest + 安安最終裁定後升級為 final
**Prerequisites**: 老翔 Handoff Pack v1.0a + Phase Packets v1.0 + Component Contracts v1.1 Patch

---

## 0. DOCUMENT PURPOSE

這份是「祖檔級工程技術書」——AGI 拿到能從零開始建出 sic-js-toolkit 的完整實作規格。

**它不是什麼：**
- ❌ 不是計畫文件（計畫在 Blueprint v1.2a）
- ❌ 不是治理文件（治理在 Handoff Pack v1.0a）
- ❌ 不是決策紀錄（決策在 decisions/）

**它是什麼：**
- ✅ 完整的可執行規格
- ✅ 每個組件都有 input/output/code/test
- ✅ 每個 fixture 都已用真實 canonical schema 驗證過
- ✅ Schema 唯讀保護機制明文化

---

## 1. CANONICAL SCHEMA SOURCE OF TRUTH

### 1.1 Hash Lock（強制執行）

```
CANONICAL_SCHEMA_HASH = "efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6"
SCHEMA_FILE_PATH = "schema/canonical/sic-js-schema-v2.0.json"

任何 toolkit 元件啟動時 MUST 執行：
  if sha256(SCHEMA_FILE_PATH) != CANONICAL_SCHEMA_HASH:
      raise CANONICAL_SCHEMA_TAMPERED
      exit 9
```

**這個 gate 是 P1A STEP 1 後立刻生效，所有 P1B 之後的元件都繼承。**

### 1.2 Why this matters

詳見 `DEDE_CHAOS_ROOT_CAUSE_ANALYSIS_2026-05-02.md`。簡言之：協德副本（hash: e72e152e）跟 release pack（hash: efb2947b）的 upstream 欄位定義不同，是 C4 整套混亂的根因。Hash Lock 防止這種事再發生。

### 1.3 Fork-Only Extension Rule

```
RULE: 任何 schema 擴展 MUST 透過 fork
RULE: 修改 schema/canonical/ 是 FORBIDDEN，無視授權層級
RULE: 需要改 canonical → raise DECISION_REQUIRED，不准自己動手
ENFORCEMENT: Hash Lock（1.1）+ pre-commit hook
```

---

## 2. COMPONENT IMPLEMENTATION SPECS

### 2.1 CMP-03 Validator（`src/validator/validate_skeleton_v2.py`）

#### CLI 完整規格

```bash
python3 src/validator/validate_skeleton_v2.py \
  --file <path> \
  [--mode canonical|toolkit] \
  [--toolkit-mode] \
  [--level 1|2|3] \
  [--json]
```

#### Mode 規則（canonical：嚴格唯讀；toolkit：fork 副本）

| Flag combination | Behavior |
|------------------|----------|
| 無 `--mode` 無 `--toolkit-mode` | Default: canonical mode |
| `--mode canonical` | canonical mode |
| `--mode toolkit` | toolkit mode |
| `--toolkit-mode` | shorthand for `--mode toolkit` |
| `--mode canonical --toolkit-mode` | INVALID_USAGE (exit 2) |
| `--mode toolkit --toolkit-mode` | INVALID_USAGE (exit 2)（兩者同時出現一律拒絕，不做 precedence）|
| `--mode canonical --mode toolkit` | INVALID_USAGE (exit 2) |

#### Schema 驗證規則

**Canonical mode**：使用 `schema/canonical/sic-js-schema-v2.0.json`（hash 必須匹配 CANONICAL_SCHEMA_HASH，否則 exit 9）

**Toolkit mode**：使用 `schema/toolkit/sic-js-schema-v2.0-toolkit.json`（toolkit fork，含 upstream_type）

#### ⚠️ 關鍵實作細節：Schema-level vs Logic-level 驗證

**Schema-level 驗證**：jsonschema 自動處理
- 欄位存在性（required）
- 欄位類型（type）
- 欄位 enum（upstream_type ∈ {none, cryptographic, file}）
- additionalProperties

**Logic-level 驗證**：必須在 validator code 額外實作
- upstream 跟 upstream_type 的一致性（這是 schema 抓不到的）

**經驗證**：在 toolkit mode 下，以下 fixture 都會 schema-PASS，但邏輯應該 FAIL：

```
V4: upstream_type=none, upstream='somevalue'      → schema PASS, logic FAIL
V5: upstream_type=cryptographic, upstream=null    → schema PASS, logic FAIL
V6: upstream_type=cryptographic, upstream=filename→ schema PASS, logic FAIL
V7: upstream_type=file, upstream=null             → schema PASS, logic FAIL
V8: upstream_type=file, upstream='a3f8b2c1d4e5f607' → schema PASS, logic FAIL
V9: upstream_type=file, upstream='../etc/passwd'  → schema PASS, logic FAIL
```

**所以 validator 必須在 schema validation 後跑 logic validation：**

```python
def validate_logic_consistency(record):
    rel = record['relation']
    ut = rel.get('upstream_type')
    up = rel.get('upstream')
    
    if ut == 'none' and up is not None:
        raise LogicError("upstream_type=none requires upstream=null")
    
    if ut == 'cryptographic':
        if up is None:
            raise LogicError("upstream_type=cryptographic requires upstream value")
        if not re.match(r'^[a-f0-9]{16}$', up):
            raise LogicError("upstream_type=cryptographic requires 16 lowercase hex")
    
    if ut == 'file':
        if up is None:
            raise LogicError("upstream_type=file requires upstream value")
        if re.match(r'^[a-f0-9]{16}$', up):
            raise LogicError("upstream_type=file but upstream looks like crypto hash")
        if '..' in up or up.startswith('/') or up.startswith('\\'):
            raise LogicError("UNSAFE_UPSTREAM: path traversal not allowed")
        if '\x00' in up:
            raise LogicError("UNSAFE_UPSTREAM: null bytes not allowed")
        if len(up) > 256:
            raise LogicError("UNSAFE_UPSTREAM: label too long")
```

#### Error Codes

| Exit | Code | When |
|------|------|------|
| 0 | (success) | PASS |
| 1 | VALIDATION_FAILED | schema or logic validation failed |
| 2 | INVALID_USAGE | bad CLI / mode conflict |
| 3 | INPUT_NOT_FOUND | input file 不存在 |
| 4 | SCHEMA_NOT_FOUND | schema file 不存在 |
| 5 | UNSAFE_UPSTREAM | 安全違規（traversal/null bytes/...）|
| 6 | LEGACY_FORMAT_DETECTED | toolkit mode 但缺 upstream_type |
| 7 | INTERNAL_ERROR | 程式異常 |
| 9 | CANONICAL_SCHEMA_TAMPERED | canonical schema hash 不符 |

---

### 2.2 CMP-04 Writer（`src/writer/sic_write.sh` 或 Python）

#### CLI 完整規格

```bash
python3 src/writer/sic_write.py \
  --entity-name <name> \
  --entity-model <model> \
  --context <text> \
  --current-action <text> \
  --user <name> \
  [--upstream <value>] \
  [--upstream-type none|cryptographic|file] \
  [--output <path>] \
  [--mode canonical|toolkit] \
  [--round <int>]
```

#### Default Mode 規則

```
Default mode: canonical
  → 不傳 --mode 時，產出純 canonical SIC-JS（無 upstream_type）

--mode toolkit 時：
  → 產出含 upstream_type 的 SIC-JS（toolkit fork 格式）

Canonical mode + --upstream-type 一起出現
  → INVALID_USAGE (exit 2)
  → Writer 不得在 canonical mode 偷偷輸出 upstream_type
```

#### Auto-Derive 規則（只在 toolkit mode 且 --upstream-type 未提供時）

| upstream value | derived upstream_type |
|----------------|----------------------|
| 缺失 / null | `none` |
| 16 lowercase hex | `cryptographic` |
| 安全的 non-empty non-hex string | `file` |
| 不安全（traversal/長度等）| 拒絕產出，exit 5 |

Auto-derive 必須輸出 log：
```
[WRITER] auto-derived upstream_type=X (writer convenience behavior, not protocol rule)
```

#### Writer 產出後自我驗證

Writer 產出 JSON 後 MUST 自動跑 validator 驗證：

```python
def write_and_self_validate(output_path, mode):
    # ... write JSON ...
    
    # Self-validate
    result = subprocess.run([
        'python3', 'src/validator/validate_skeleton_v2.py',
        '--file', output_path,
        '--mode', mode
    ])
    if result.returncode != 0:
        raise WriterError(f"Writer output failed self-validation. exit={result.returncode}")
```

這條規則防止 writer 跟 validator 出現分歧。

---

### 2.3 CMP-05 Verifier（`src/verifier/sic_verify.sh`）

#### 設計原則

**Thin wrapper only**。完全委派給 CMP-03 validator。**禁止 sic_verify.sh 內部有任何獨立驗證邏輯。**

#### CLI

```bash
bash src/verifier/sic_verify.sh \
  --file <path> \
  [--mode canonical|toolkit] \
  [--level 1|2|3]
```

#### 實作（極簡）

```bash
#!/bin/bash
set -e

# Parse args (forward to validator)
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --file|--mode|--level|--toolkit-mode|--json)
      ARGS+=("$1")
      shift
      if [[ $# -gt 0 && ! "$1" =~ ^-- ]]; then
        ARGS+=("$1")
        shift
      fi
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

# Call validator (single source of truth)
python3 "$(dirname "$0")/../validator/validate_skeleton_v2.py" "${ARGS[@]}"
```

---

## 3. 19 TEST FIXTURES（已用 efb2947b 驗證）

### 3.1 Writer Tests (W1-W6)

W1-W6 是腳本測試，跑 sic_write.sh 然後驗證輸出。

```bash
# tests/W1_writer_none_null.sh
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --upstream-type none --upstream null \
  --mode toolkit \
  --output /tmp/W1_out.json
EXPECT: exit 0, /tmp/W1_out.json contains upstream_type="none", upstream=null

# tests/W2_writer_crypto_hex.sh
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --upstream-type cryptographic --upstream a3f8b2c1d4e5f607 \
  --mode toolkit \
  --output /tmp/W2_out.json
EXPECT: exit 0

# tests/W3_writer_file_label.sh
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --upstream-type file --upstream "XIED_v58.json" \
  --mode toolkit \
  --output /tmp/W3_out.json
EXPECT: exit 0

# tests/W4_writer_auto_hex.sh — auto-derive cryptographic
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --upstream a3f8b2c1d4e5f607 \
  --mode toolkit \
  --output /tmp/W4_out.json
EXPECT: exit 0, output contains upstream_type="cryptographic", log contains "auto-derived"

# tests/W5_writer_auto_label.sh — auto-derive file
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --upstream "XIED_v58.json" \
  --mode toolkit \
  --output /tmp/W5_out.json
EXPECT: exit 0, output contains upstream_type="file"

# tests/W6_writer_auto_null.sh — auto-derive none
python3 src/writer/sic_write.py \
  --entity-name "test" --entity-model "TestModel" \
  --context "test" --current-action "test" --user "test" \
  --mode toolkit \
  --output /tmp/W6_out.json
EXPECT: exit 0, output contains upstream_type="none", upstream=null
```

### 3.2 Verifier Tests (V1-V9)

實際 fixture JSON 檔案已產出，路徑：`tests/fixtures/V1_*.json` 到 `tests/fixtures/V9_*.json`

```
V1 (PASS): upstream_type=none, upstream=null
V2 (PASS): upstream_type=cryptographic, upstream='a3f8b2c1d4e5f607'
V3 (PASS): upstream_type=file, upstream='XIED_v58.json'

V4 (FAIL logic): upstream_type=none, upstream='somevalue'
V5 (FAIL logic): upstream_type=cryptographic, upstream=null
V6 (FAIL logic): upstream_type=cryptographic, upstream='XIED_v2.json'
V7 (FAIL logic): upstream_type=file, upstream=null
V8 (FAIL logic): upstream_type=file, upstream='a3f8b2c1d4e5f607' (looks like crypto)
V9 (FAIL logic): upstream_type=file, upstream='../etc/passwd' (UNSAFE_UPSTREAM)
```

**重要**：V4-V9 schema validation PASS 但 logic validation 必須 FAIL。這是 validator code 必須額外實作的邏輯（見 §2.1）。

### 3.3 Consistency Tests (C1-C3)

```
C1: Writer W2 output → feed Verifier toolkit mode → expect PASS
C2: Writer W4 (auto-derived) output → feed Verifier toolkit mode → expect PASS
C3: Writer W1/W2/W3 each → Verifier agrees on all three types → expect all PASS
```

### 3.4 Legacy Test (L1)

```json
// tests/fixtures/L1_legacy.json
// 純 canonical SIC-JS（無 upstream_type）
{
  "sic_version": "2.0",
  "round": 10,
  "entity": {"name": "test", "model": "TestModel"},
  "state": {"context": "c", "current_action": "a"},
  "relation": {"user": "u"},
  "event": null,
  "intent": null
}

EXPECT (toolkit mode): FAIL with LEGACY_FORMAT_DETECTED (exit 6)
EXPECT (canonical mode): PASS (這是合法 canonical SIC-JS)
```

---

## 4. SCHEMA FORK CONSTRUCTION SPEC

### 4.1 Toolkit Fork = Full Copy + 三處修改

```python
import copy
import json

# Read canonical (with hash check)
canonical = json.load(open('schema/canonical/sic-js-schema-v2.0.json'))
assert sha256(canonical_text) == 'efb2947b...'  # MUST hold

# Build fork
toolkit = copy.deepcopy(canonical)

# Modification 1: Title and description
toolkit['title'] = 'SIC-JS v2.0 Toolkit Fork Schema'
toolkit['description'] = 'Toolkit fork. upstream_type is project-local extension, NOT canonical.'

# Modification 2: Add upstream_type to relation.properties
toolkit['properties']['relation']['properties']['upstream_type'] = {
    'type': 'string',
    'enum': ['none', 'cryptographic', 'file'],
    'description': 'TOOLKIT PROJECT-LOCAL EXTENSION. NOT SIC-JS v2.0 canonical.'
}

# Modification 3: Add upstream_type to relation.required
toolkit['properties']['relation']['required'].append('upstream_type')

# Modification 4: Relax upstream pattern (allow filename)
# Note: this is in toolkit fork only; canonical keeps strict 16-hex
toolkit['properties']['relation']['properties']['upstream'] = {
    'type': ['string', 'null'],
    'minLength': 1,
    'description': 'Format depends on upstream_type. cryptographic: 16 hex; file: semantic label; none: null.'
}

# Save
json.dump(toolkit, open('schema/toolkit/sic-js-schema-v2.0-toolkit.json', 'w'),
          indent=2, ensure_ascii=False)
```

### 4.2 Verification

After fork creation:

```python
# Canonical hash unchanged
assert sha256(canonical_file) == 'efb2947b...'

# Toolkit fork has upstream_type
assert 'upstream_type' in toolkit['properties']['relation']['properties']
assert 'upstream_type' in toolkit['properties']['relation']['required']

# Run all 19 fixtures
# V1-V3, L1 → toolkit schema validates correctly
# Canonical mode test: clean SIC-JS without upstream_type → PASS
# Canonical mode test: SIC-JS with upstream_type → FAIL (additionalProperties: false)
```

---

## 5. REPO TARGET STRUCTURE（依咩咩 scaffolding 對齊）

```
sic-js-toolkit/
├── README.md
├── schema/
│   ├── canonical/
│   │   └── sic-js-schema-v2.0.json     [hash: efb2947b... LOCKED]
│   └── toolkit/
│       └── sic-js-schema-v2.0-toolkit.json
├── src/
│   ├── validator/
│   │   └── validate_skeleton_v2.py
│   ├── writer/
│   │   └── sic_write.py
│   ├── verifier/
│   │   └── sic_verify.sh
│   ├── drift/
│   │   └── (P5 onwards)
│   └── utils/
│       └── hash_lock.py                [shared canonical hash check]
├── tests/
│   ├── fixtures/
│   │   ├── V1_none_null.json
│   │   ├── V2_crypto_hex.json
│   │   ├── ... (V3-V9, L1)
│   ├── unit/
│   │   ├── W1_writer_none_null.sh
│   │   ├── ... (W2-W6)
│   ├── integration/
│   │   ├── C1_writer_to_verifier.sh
│   │   └── (C2, C3)
│   └── legacy/
│       └── L1_test.sh
├── docs/
│   ├── governance/
│   ├── migration/
│   ├── release/
│   └── api/
├── reports/
│   ├── reviews/
│   └── c4/
└── decisions/
```

---

## 6. EXECUTION ORDER（給 AGI）

```
STEP 1: Hash Lock setup
  - 把 release pack 的 sic-js-schema-v2.0.json 複製到 schema/canonical/
  - 計算 SHA-256，確認 = efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6
  - 在 src/utils/hash_lock.py 寫入 CANONICAL_SCHEMA_HASH 常數

STEP 2: Build toolkit fork
  - 依 §4.1 規格，從 canonical full-copy 出 schema/toolkit/sic-js-schema-v2.0-toolkit.json
  - 確認三項修改都有
  - 確認 canonical 在 fork 過程中沒被改動（hash 還是 efb2947b）

STEP 3: Implement CMP-03 Validator
  - 依 §2.1 規格實作 src/validator/validate_skeleton_v2.py
  - 包含 schema validation + logic validation + hash lock check
  - 9 個 error codes 全部處理

STEP 4: Implement CMP-04 Writer
  - 依 §2.2 規格實作 src/writer/sic_write.py
  - Auto-derive 邏輯
  - Self-validation

STEP 5: Implement CMP-05 Verifier
  - 依 §2.3 規格寫 src/verifier/sic_verify.sh
  - Thin wrapper, 委派 CMP-03

STEP 6: Place test fixtures
  - 19 個 fixtures 放進 tests/fixtures/、tests/unit/、tests/integration/、tests/legacy/

STEP 7: Run all tests
  - W1-W6: 全部 PASS
  - V1-V3: PASS（schema + logic）
  - V4-V9: schema PASS but logic FAIL（這是設計）
  - C1-C3: PASS
  - L1: toolkit mode FAIL with LEGACY_FORMAT_DETECTED (exit 6)
        canonical mode PASS

STEP 8: Self-validation closure
  - 跑 hash check：canonical schema 還是 efb2947b
  - 跑 cross-validation：writer 產出可以通過 verifier
  - 跑 fork independence：canonical 沒被 fork 過程污染
```

---

## 7. WHAT THIS SPEC DOES NOT YET COVER（已知 gap）

1. **咩咩的實際 repo manifest**：Phase 結構跟 scaffolding 已對齊，但檔案 hash manifest 還沒拿到
2. **C4-8/C4-9 遷移策略**：等安安裁定（A 文件 only or B 半自動 script）
3. **CMP-13 帳本系統實作細節**：架構已定（IP/TCP wrapper），但 P1A 不做
4. **drift detection（CMP-06+）**：P5 之後才規劃
5. **External review package（P5B）**：是另一個獨立工作包，不在這份規格內

---

## 8. APPENDIX: VALIDATED FIXTURES INVENTORY

以下 fixtures 已用 efb2947b canonical schema + 對應 toolkit fork 跑過 jsonschema 驗證：

```
tests/fixtures/V1_none_null.json         schema PASS, logic PASS, expected PASS ✅
tests/fixtures/V2_crypto_hex.json        schema PASS, logic PASS, expected PASS ✅
tests/fixtures/V3_file_label.json        schema PASS, logic PASS, expected PASS ✅
tests/fixtures/V4_none_nonnull.json      schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/V5_crypto_null.json       schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/V6_crypto_label.json      schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/V7_file_null.json         schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/V8_file_hex.json          schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/V9_file_traversal.json    schema PASS, logic FAIL, expected FAIL ⚠
tests/fixtures/L1_legacy.json            schema FAIL (toolkit), schema PASS (canonical) ✅
```

⚠ 標記項目顯示「為什麼 logic-level validation 是必須的」——schema 抓不到 upstream/upstream_type 的一致性問題。validator code 必須補上。

---

**Document End**
**Author**: 德德（Wei De）
**Status**: GAP-AWARE DRAFT — 升級為 final 需要：
1. 咩咩 actual repo manifest（補 §5 對齊）
2. 安安 C4-8 裁定（補 §7-2）
3. 老翔合版 confirm（merge Phase Packets + Contracts + 本文件）
