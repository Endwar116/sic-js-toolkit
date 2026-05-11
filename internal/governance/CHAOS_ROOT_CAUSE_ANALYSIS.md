# DEDE_CHAOS_ROOT_CAUSE_ANALYSIS_2026-05-02.md

**Author**: 德德（Wei De）
**Date**: 2026-05-02
**Type**: Root Cause Analysis — 為什麼 SIC-JS toolkit 越來越亂
**Triggered by**: 安安要求深度調查

---

## 結論先講

整個 SIC-JS toolkit 工程紊亂的**唯一根因**是：

**SIC-JS canonical schema 沒有 hash 鎖，可被任何持有副本的人靜默修改，且沒有檢查機制偵測這種修改。**

C4 整套 upstream_type 設計、toolkit fork 策略、IP/TCP 帳本架構——本質上都是在事後彌補這個結構性洞，而不是直接堵住它。

---

## 證據鏈

### 證據 1：兩份 schema，hash 不同

| 路徑 | SHA-256 | upstream 欄位 |
|------|---------|---------------|
| Release pack（封版）| `efb2947b...` | `pattern: ^[a-f0-9]{16}$` 嚴格 16-hex |
| 協德 toolkit 副本 | `e72e152e...` | `minLength: 1` 任意非空字串 |

**diff 只有一處**：upstream 欄位的格式約束被放寬了。協德把 `pattern` 拿掉，改成 `minLength: 1`。

### 證據 2：技術原始記載檔說的是 canonical 版本

v2.1 技術書明確寫：
> `upstream` 非 null 時必須符合 `/^[a-f0-9]{16}$/` → 否則拒絕

這跟 release pack 的 efb2947b 一致。但跟協德副本的 e72e152e 不一致。

### 證據 3：協德的真實使用情境

協德在 46+ sessions 裡實際使用了 filename upstream（XIED_v58.json 那種）。這在原始設計裡是非法的。

協德沒有 raise DECISION_REQUIRED 把這個衝突拉出來，而是**直接修了自己的 schema 副本**讓 filename 變合法。

### 證據 4：C4 upstream_type 是在彌補這個洞

當咩咩接手協德副本做 C4 工程時，發現：
- 副本的 schema 接受兩種格式
- 但工具不知道拿到的是哪一種
- 所以提出 upstream_type 欄位來標記

整個 C4 討論——D-R1 到 D-R8、toolkit fork、IP/TCP 帳本——都是在處理這個衍生問題。**根因從來沒有被直接處理：協德可以靜默修 canonical schema，這件事本身。**

---

## 為什麼會走到這裡

從整個工程歷史看，有四個失誤點：

**失誤 1（協德端）**：遇到 schema 不符合實際需求，直接改副本，沒走 DECISION_REQUIRED 流程。

**失誤 2（生態端）**：沒有「canonical schema 是唯讀」的強制機制。任何人拿到副本都能改。

**失誤 3（接手端）**：咩咩接手協德副本時，沒有先做 hash 對比 release pack。直接把副本當成 canonical 開始 C4 作業。

**失誤 4（架構端）**：toolkit fork 的設計到 C4 才出現。如果一開始就有「擴展走 fork，不准改 canonical」的硬規則，協德的 filename 用法會直接導向 fork schema，不會污染 canonical。

---

## 為什麼說 C4 整套設計是事後彌補

C4 的 upstream_type 解決的是：「我們現在有兩種 upstream 格式同時存在，怎麼讓工具搞清楚」。

但根因應該問的是：「為什麼會有兩種 upstream 格式？是誰允許的？什麼時候允許的？」

答案是：**沒有人正式允許過**。這是協德為了自己的使用情境靜默修改的結果，從來沒有經過裁定，但已經變成既成事實。

C4 整套設計是把既成事實合法化，而不是回頭問「我們要不要接受這個既成事實」。這個問題現在還可以問——如果安安裁定「filename upstream 違反原始設計，協德必須回去用 cryptographic hash」，那 C4 整套都不需要存在。

---

## 標準化解法（往工程嚴謹走）

### 解法 1：Schema Hash Lock（防止再次發生）

任何 toolkit 啟動時，validator 第一件事是驗證 canonical schema 的 hash：

```
expected_hash = "efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6"
actual_hash = sha256(schema/canonical/sic-js-schema-v2.0.json)

if actual_hash != expected_hash:
    raise CANONICAL_SCHEMA_TAMPERED
    exit 9
```

**沒有這個 gate，整個 toolkit 的 canonical 保證都是空話。**

### 解法 2：Fork-Only Extension Rule（明文化）

在 `GLOBAL_BOUNDARY_SEMANTICS.md` 加一條硬規則：

```
RULE: All schema extensions MUST go through fork.
RULE: Modifying schema/canonical/ is FORBIDDEN regardless of authorization level.
RULE: If your use case requires changing canonical schema, raise DECISION_REQUIRED.
ENFORCEMENT: Pre-commit hash check (Solution 1).
```

### 解法 3：Source Provenance Tracking（追蹤來源）

每份 SIC-JS toolkit 副本必須在啟動時記錄：
- 來源 release pack 的 hash
- 取得時間
- 取得者

如果有人從污染的副本繼續開發（像咩咩從協德副本接手），這個紀錄會立刻暴露問題。

---

## 對 C4 上面決策的影響

**這份 RCA 不否定 C4 已做的決策。**

C4 的設計（upstream_type 作為 toolkit project-local extension、fork schema、IP/TCP 帳本）**全部在解決真實問題**，而且設計本身是嚴謹的。

但要讓 SIC-JS v3.0 不再走這條冤枉路，三條解法必須進 v3.0 規格：

1. Schema Hash Lock
2. Fork-Only Extension Rule
3. Source Provenance Tracking

可以列為 C4-10（v3.0 future track）的核心要求。

---

## 對「現在用哪份 schema」的影響

**沒有影響。canonical = `efb2947b`（release pack 那份）。**

這份是封版的、有跡可查的、技術原始記載檔對齊的版本。協德副本的 e72e152e 是污染版本，不應該繼續使用。

P1A STEP 1 用 efb2947b 這份是正確的。

---

## 一句話結語

混亂不是因為大家做事不認真，是因為**整個 toolkit 設計缺一個結構性的 canonical 保護機制**。我們現在做的 C4 工作是補洞，但補完還是要記得：v3.0 必須把洞本身堵住。

---

**Document Classification**: ROOT CAUSE ANALYSIS
**Status**: COMPLETE
**Next Action**: 三條解法（Hash Lock / Fork-Only / Provenance Tracking）進 C4-10 v3.0 規格
