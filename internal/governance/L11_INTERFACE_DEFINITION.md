# SIC-JS ↔ L11-Collab-Lite Interface Definition v1.0

**Authority**: 德德（架構）× 老翔（治理）× 安安（最終裁決）
**Date**: 2026-05-02
**Decision**: SEPARATE_WITH_INTERFACE
**Status**: INTERFACE DEFINED — runtime integration deferred to post-P2/L11-evidence

---

## 0. 邊界宣告

| 問題 | SIC-JS Toolkit 管 | L11-Collab-Lite 管 |
|------|------------------|-------------------|
| JSON state 合不合法 | ✅ | ❌ |
| upstream_type 是否 project-local | ✅ | ❌ |
| validator / writer / verifier | ✅ | ❌ |
| test fixtures | ✅ | ❌ |
| 誰該做這個任務 | ❌ | ✅ |
| 要不要安安裁決 | ❌ | ✅ |
| agent loop 是否浪費時間 | ❌ | ✅ |
| owner overload 是否發生 | ❌ | ✅ |
| artifact parent-child trace | 部分 | ✅ |
| release / deploy route | 部分 | ✅ |

---

## Interface A：SIC-JS artifact metadata → L11

每個 SIC-JS Toolkit 輸出包可以附一個 metadata 檔案。
L11-Collab-Lite 用這個判斷路由、是否需要安安、是否 freeze。

**Schema（可選附加，不影響 SIC-JS 本體）：**

```json
{
  "artifact_id": "string",
  "artifact_type": "string",
  "sic_js_state_ref": "string | null",
  "phase": "string",
  "parent_task": "string | null",
  "producer": "string",
  "status": "PASS | PASS_WITH_NOTES | PARTIAL | FAIL",
  "requires_owner_ruling": true | false,
  "next_gate": "string | null",
  "forbidden_claims": ["string"]
}
```

**使用規則：**
- 這個 metadata 是 optional，不是 SIC-JS schema 的一部分
- 不得加進 sic-js-schema-v2.0.json（canonical）或 toolkit fork
- 放在各自輸出包的根目錄，命名：`L11_ARTIFACT_META.json`
- SIC-JS Toolkit 的任何 validator / writer / verifier 不讀這份

---

## Interface B：L11 route decision record → SIC-JS reports

L11-Collab-Lite 每次路由後，產一個 route decision record。
這個 record 可以被 SIC-JS Toolkit 的 reports/ 目錄引用。

**Schema：**

```json
{
  "route_id": "ROUTE-YYYY-MM-DD-NNN",
  "task": "string",
  "gravity_level": "G0_LOW | G1_MEDIUM | G2_HIGH | G3_CRITICAL",
  "route": "single_agent_direct | peer_review | multi_agent | owner_ruling",
  "assigned_to": "string",
  "reviewers": ["string"],
  "owner_ruling_required": true | false,
  "reason": "string",
  "forbidden_escalation": ["string"],
  "output_required": ["string"]
}
```

**Gravity 定義（L11-Collab-Lite 的 7 條最小規則基礎）：**

| Level | 定義 | 路由 |
|-------|------|------|
| G0_LOW | 靜態工程、文案、HTML/CSS/JS | single_agent_direct |
| G1_MEDIUM | 文件 patch、合版、review | peer_review（1 reviewer）|
| G2_HIGH | canonical 邊界、schema 變更、release gate | multi_agent + 德德 review |
| G3_CRITICAL | canonical source 裁定、P0/P1A authorization、deploy | owner_ruling（安安）|

---

## L11-Collab-Lite 最小規則包（7 條）

```
Rule 1: Gravity Classification
  G0 = 單個 agent 在 30 分鐘內可完成 = 不進 agent loop
  G1 = 需要 peer review = 最多一個 reviewer
  G2 = 涉及架構邊界 = 德德 + 老翔
  G3 = 涉及 canonical / owner ruling = 安安

Rule 2: Route Decision Record
  每次任務路由都要產一份 route_decision.json

Rule 3: Owner Ruling Gate
  只有 G3 任務才送到安安
  其他全部在 AI 層解決

Rule 4: Agent Loop Freeze Rule
  如果同一個任務已超過 4 個 agent 輪次沒有結論 = FREEZE
  強制降級：德德直接裁定或送安安

Rule 5: Owner Overload Stop Rule
  如果安安在 30 分鐘內被問超過 3 件事 = STOP
  老翔負責過濾、合併、降優先級

Rule 6: Artifact Parent Linkage
  每個 artifact 必須有 parent_task 引用
  沒有 parent_task = 不接受進任何 phase

Rule 7: Collaboration Failure Semantics
  agent 回傳 DECISION_REQUIRED = 自動升一級
  agent 連續兩次 DECISION_REQUIRED on same topic = 強制 owner ruling
```

---

## 現在不做什麼

- ❌ 不把 L11 runtime 塞進 SIC-JS Toolkit v1.0 core
- ❌ 不讓 SIC-JS Toolkit 等 L11 完成才前進
- ❌ 不讓 L11 以未驗證 runtime 形式阻塞 P1A/P1B
- ❌ 不做 runtime integration（deferred）

## 什麼時候才做 runtime integration

```
條件 A: SIC-JS Toolkit P2 完成（test suite + docs 完整）
條件 B: L11-Collab-Lite 有 5+ 個真實協作事件的 route decision 紀錄
條件 C: 安安裁定「可以整合了」
三個條件全部為 TRUE，才開始 runtime integration 設計
```

---

## 給扣翔的話

L11 的 canonical event record 可以保持現狀，不需要現在改動。
如果你的 event record 想記錄 SIC-JS snapshot，在 `payload` 裡加一個 nullable `sic_js` 欄位就夠了：

```python
# In L11 canonical event record
"payload": {
    "sic_js": None  # Optional SIC-JS v2.0 state snapshot
    # ... existing payload fields
}
```

不強制。L11 本體不依賴 SIC-JS。

## 給咩咩的話

SIC-JS Toolkit 的每個 phase 輸出包，在 reports/ 目錄下可以附加一份 `L11_ARTIFACT_META.json`（Interface A）。
這是可選的，不影響 toolkit 的任何 validator / schema / tests。
CMP-01 到 CMP-09 不需要改動。

---

**Document Classification**: INTERFACE DEFINITION
**Next Review**: 當 SIC-JS Toolkit P2 完成後
**Maintained by**: 德德（架構）
