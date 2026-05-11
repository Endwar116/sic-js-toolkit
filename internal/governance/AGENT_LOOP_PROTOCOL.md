# SIC-JS Toolkit Agent Loop Protocol
# Version: 1.0 / 2026-05-08
# Authority: 德德（架構）× 安安（最終裁決）
# Based on: POWER META PROMPT v2 (LTFF-ready)

---

## 每個 Loop 的強制步驟

每一個 agent loop（每一個 phase 的執行單元）必須按以下順序執行：

### STEP 0 — SECTION 2 推理（動手前）

問自己三個問題，不對外報告答案，只確保自己知道：

**問題 A：** 這個 phase 結束的時候，那個陌生人（LTFF reviewer / 任何 clone 這個 repo 的人）的狀態會從什麼變成什麼？

**問題 B：** 我計劃的每個動作，是讓陌生人更容易懂，還是讓我的輸出看起來更完整？

**問題 C：** 如果我現在消失，老翔拿到我的輸出能不能 review？德德拿到能不能做 sign-off？

三個問題都有答案，才動手。

---

### STEP 1 — 執行 Phase 工作

依 Phase Packet 規格執行。不超出 Phase 範疇。

---

### STEP 2 — Loop 結束自檢（交付前）

每個 loop 結束時，逐項確認：

| 項目 | 檢查內容 |
|---|---|
| SC-1 | DoD 每一項都有 actual evidence（不是寫「已完成」） |
| SC-2 | 沒有 hardcoded 路徑（`/home/ubuntu/`、`/home/claude/`） |
| SC-3 | 所有新增的 JSON 都通過 validator |
| SC-4 | Post-Change Report 存在且完整 |
| SC-5 | 沒有修改 `schema/canonical/`（除非有 DECISION_REQUIRED 授權） |
| SC-6 | 沒有自己決定 DECISION_REQUIRED 的事項 |
| SC-7 | SIC-JS state JSON 已產生並通過 verifier |

**SC-1 到 SC-7 全部通過，才能進行 STEP 3。**

---

### STEP 3 — SIC-JS State 記錄

每個 loop 結束時必須：

1. 執行 `python3 src/writer/sic_write.py` 產生本 loop 的 SIC-JS state JSON
2. 執行 `python3 src/validator/validate_skeleton_v2.py --mode toolkit` 驗證
3. 執行 `python3 sic-state/tools/append_round.py` 寫入 ledger
4. 執行 `python3 sic-state/tools/verify_state.py` 確認完整性

---

### STEP 4 — 交付

每個 phase 的交付包含：

1. **Post-Change Report**（DoD 每項打勾，有 actual evidence）
2. **Toolkit zip**（只包含 toolkit 本身，不包含 ledger/state）
3. **SIC-JS JSON 直接內嵌在 message text**（不是 zip，不是 attachment）

---

## DECISION_REQUIRED 觸發條件

遇到以下情況，立刻停，發 Slack 給德德，不要自己決定：

- canonical schema 有任何需要改動的地方
- 發現測試結果跟規格文件有衝突
- 某個 Gate 判斷 FAIL 但不確定能不能 override
- 發現需要增加新的 CMP 組件

---

## Phase 順序

```
P1A ✅ → P1B ✅ → P2 → P3A → P4 → P5A → Release
```

每個 phase 結束後，等老翔 governance review PASS 才進下一個 phase。

---

## LTFF-ready 最終驗收標準

任何人 clone repo 後執行：

```bash
pip install -r requirements.txt
bash tests/run_tests.sh
```

必須看到：

```
TOTAL: 20  PASS: 20  FAIL: 0
```

如果做不到，就還沒到 LTFF-ready。
