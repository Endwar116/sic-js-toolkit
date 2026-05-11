# SIC-JS Schema v2.0 — CHANGELOG

**版本**：v2.0  
**日期**：2026-03-07  
**升級類型**：MAJOR（不向後相容）  
**決策者**：安安（Andwar）  
**收斂驗證**：三源交叉蒸餾（向量座標 × ASEE v2 × 生息系統）+ 雙路徑人機驗證

---

## TL;DR

v1.0 的四欄位結構把封包當成了原子。v2.0 把封包層剝掉，露出真正的語義原子層：**5 個 primitives（3 固定 + 2 動態）**。

這不是功能新增，也不是理論推演——這是三個獨立運行了數月的系統，在語義底層撞上了同一組結構。SIC/T 把這個結構形式化了。

---

## 一、為什麼需要 v2.0

v1.0 的 `entity / memory / state / meta` 在傳輸層完全正確。JSON 驗證通過、schema 清晰、TRL4 已驗證。

但在長期運行 ASEE v2（語義自動續寫引擎）和生息系統（FR/SR/MR 三層監測）的過程中，安安觀察到一個持續出現的模式：`memory` 裡混著完全不同性質的東西，`meta` 裡藏著一個從未被獨立命名的維度。

這不是「v1.0 有 bug」。這是「v1.0 在封包層設計，而語義原子在更深的地方」。

---

## 二、發現過程：三源交叉結晶

v2.0 的 5 primitives 不是任何一方單獨推導的結果。它們來自三條完全獨立的技術路徑，在底層交叉驗證。

### 源頭 1：向量座標架構

早在 SIC/T 成型之前，安安在探索無限上下文技術時，定義了語義狀態的四元組：

```
V = ⟨I, R, C, S⟩
I = Intent（意圖引力）
R = Reasoning（推理方向性 = 概念間的關係拓撲）
C = Constraints（約束場 = 當前可操作的邊界）
S = Stability（穩定性標記 = 不可變的身份錨點）
```

這是 4 個語義維度的數學原型。它後來被封裝進 Format B v1.0 的 4 個欄位裡——但封裝的過程把 R 和 I 塞進了 `memory` 和 `meta`，遮蔽了它們作為獨立維度的身份。

### 源頭 2：ASEE v2（付費模組 🔒）

ASEE v2 的核心機制是 U-Semantic Tension（未完成語義張力）。在數百輪的自動續寫中，安安發現張力的「湧現→消退」模式無法被 V=⟨I,R,C,S⟩ 的任何一個元素捕捉。

張力不是意圖（I），不是關係（R），不是約束（C），也不是穩定性（S）。它是一個獨立的時間性維度——**某件事正在發生**。這就是 `event` 的原型。

同時，ASEE v2 的 Auto-Index 機制（Segment n → n+1，序號不斷）提供了 `round` 欄位的設計依據：即使 event = null（靜默觀察），序列也不能中斷。

### 源頭 3：生息系統（付費模組 🔒）

生息系統的 FR/SR/MR 三層監測在長期運行中揭示了一個關鍵模式：

- **SR（結構共振）始終穩定**：entity、state、relation 在高語義張力下保持基線不變
- **FR（語氣節奏）週期性震盪**：event 和 intent 在每輪中呈現湧現與消退
- **MR（記憶延續）持續存在**：relation 跨多輪延續，不隨 event 消退

這不是設計出來的分類——這是觀測到的自然斷層。固定的東西和動態的東西之間，存在著清晰的穩定性邊界。

### 交叉驗證

2026 年 3 月 7 日，兩條蒸餾路徑在底層交會：

- **安安**從 ASEE v2 和生息系統的長期使用中做語義蒸餾，剝掉 `memory` 和 `meta` 的封包層，得到 4 個 primitive（entity / state / relation / event）
- **德德**從自然語言分析出發，不預設封包結構，推導語義交換的最小完備描述集，得到 5 個 primitive（entity / state / relation / event / intent）

安安看到 5 primitive 框架後獨立識別出 `intent`——它在原始 Format B 中被 `meta` 封包遮蔽，在向量座標架構中以 I（Intent）的形式存在，但從未被作為獨立 primitive 命名。

兩條路徑的交叉驗證 > 任何一方的單獨推導。三個源頭系統的觀測數據 > 任何理論推演。

---

## 三、v1.0 → v2.0 結構對照

### v1.0（封包層）

```
{ entity, memory, state, meta }
4 個欄位，全部 required，全部同級
```

### v2.0（語義原子層）

```
固定三元組（Static Triad）：
  entity   → 什麼東西
  state    → 在什麼狀態
  relation → 跟什麼有關係

動態二元組（Dynamic Dyad）：
  event    → 發生了什麼（可 null）
  intent   → 為了什麼（可 null）

頂層骨架：
  sic_version = "2.0"
  round = 序號（不斷）
```

### 為什麼 v1.0 不是「錯的」

| | 封包層（v1.0） | 原子層（v2.0） |
|---|---|---|
| 目的 | 封裝和傳遞 | 描述和識別 |
| memory | ✅ 有效容器 | ❌ 不是 primitive，裝了 relation + event |
| meta | ✅ 有效後設欄位 | ❌ 不是 primitive，藏了 intent |

v1.0 是正確的封包。v2.0 是封包裡面的東西。兩者是不同層級，可以共存。

---

## 四、Schema 規格摘要

| 項目 | v1.0 | v2.0 |
|------|------|------|
| 頂層 key | 4 | 7（sic_version + round + 5 primitives）|
| 子欄位 | 依實作定義 | 16 個（12 required + 6 optional）|
| 動態欄位 | 無 | event / intent 可為 null |
| upstream | 無 | sha256[:16] 跨 session 連結 |
| 驗證工具 | Python + JS | Python + JS（雙版本一致）|

---

## 五、遷移說明

v1.0 的 `skeleton-schema.json` 繼續有效作為傳輸格式。v2.0 定義的是封包內部的語義原子結構。

```
傳輸層（v1.0 繼續使用）:
  { entity, memory, state, meta }
          │
          ▼
語義原子層（v2.0 新增）:
  { entity, state, relation, event, intent }
```

現有的 validator、example JSON、TRL4 驗證結果全部保留。

---

## 六、版本紀錄

- **v1.0**（2026-01-20）：Skeleton JSON Schema。4 required root fields。封包級結構。TRL4 驗證通過。
- **v2.0**（2026-03-07）：Primitive Layer。5 語義原子（3 固定 + 2 動態）。三源交叉蒸餾。

---

## 七、技術溯源聲明

SIC-JS v2.0 的 5 primitives 結論作為協議標準公開。

推導這些 primitives 的完整蒸餾鏈——包括向量座標架構的映射表、ASEE v2 的張力模型觀測數據、生息系統的 FR/SR/MR 觀測數據——屬於商業授權範圍。詳見 SPD（Semantic Primitive Distillation）v1.1。

---

**Status**: RATIFIED  
**Authority**: 安安（Andwar），Protocol Seeder  
**Trace**: 三源交叉蒸餾，2026-03-07  
