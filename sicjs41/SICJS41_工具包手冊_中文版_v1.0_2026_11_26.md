# SIC-JS 4.1 工具包手冊（中文版）

版本：v1.0｜日期：2026-11-26｜作者：德德（`agent://imcc/德德`）｜決定者：安安（`user://anan`）
英文版：`SICJS41_Toolkit_Manual_EN_v1.0_2026_11_26.md`（內容相同）。
狀態：工具包是德德做的參考實作，不是凍結協議的一部分；協議本身以 IMCC `protocols/SIC-JS_4.1_FR-002/` 為準。

**一句話：一支 Python 檔加一支 MCP 伺服器，不用安裝任何套件，就能寫出、驗證、串鏈 SIC-JS 4.1 紀錄；只有對話、沒有工具時，貼快速載入提示就能用。**

## 1. 版本現況

| 版本 | 狀態 | 本包怎麼處理 |
|---|---|---|
| 4.1（`SICJS-4.1-FR-002`） | 凍結，2026-09-17 由安安批准 | 正文；schema 原檔逐位元組內嵌 |
| 4.2（`SICJS-4.2-PF-001`） | 草案，沒有凍結；安安說 4.2 由她自己處理 | 只在技術頁附錄說明差異，工具不支援 |

## 2. 包裡有什麼

| 檔案 | 用途 |
|---|---|
| `sicjs41.py` | 主工具：範本、驗證、跨包歷史、寫入、延續上一包、驗鏈、正規化雜湊、輸出 schema。只用 Python 標準函式庫（在 Python 3.13 測過）。 |
| `sicjs41_mcp.py` | MCP 伺服器（stdio、JSON-RPC 2.0），讓對話助手呼叫上面的功能。要跟 `sicjs41.py` 放同一個資料夾。 |
| `sicjs41.js` | 瀏覽器與 Node 用的單包驗證器（同一套 schema 與語義規則，不含跨包歷史與寫入），技術頁的頁內驗證器就是它。 |
| `sic-js-schema-v4.1.json` | 凍結 schema 原檔，sha256 `23c15b4c…2ac56ca7`，與 `registry/canonical_hashes.json` 一致。 |
| `SICJS41_快速載入提示_中文版_v1.0_2026_11_26.md`、英文版 | 沒有工具時，貼進新對話用。 |
| 本手冊中英兩份 | 用法與限制。 |

## 3. 四種用法

### 3.1 只有對話，沒有工具

把快速載入提示整段貼進新對話。
模型會在每輪回覆最後附一個封包。
限制：沒有工具時，時間、round、雜湊都是模型自己寫的，只能當宣稱，不能當已驗證（A-001）。

### 3.2 指令列

```bash
python3 sicjs41.py template --agent 德德 --model claude-opus-5-5 --task-id KT-1 --title 標題 --deliverable 交付物 > p.json
python3 sicjs41.py append log.jsonl p.json            # 驗證後寫第 1 筆；不過就不寫
python3 sicjs41.py next log.jsonl --declare '{"action":"寫程式","description":"完成 sicjs41.py","pending":["測試"]}'
python3 sicjs41.py verify log.jsonl                    # 凍結雜湊＋鏈＋每一包＋跨包歷史
python3 sicjs41.py validate 封包.json --prev 上一包.json
python3 sicjs41.py rules --lang zh                     # 規範摘要
python3 sicjs41.py quickload --lang zh                 # 印出快速載入提示
```

`next` 的分工：round、時間、上一包雜湊（`relation.upstream`）、governance 由工具填；`--declare` 只放隱性欄位：`action`、`description`、`pending`、`core_question`、`context`、`status`、`task`（換任務時）、`evidence`、`approval`、`verifier`。
要寫 `completed`，必須在 `--declare` 給 `evidence`、`approval`、`verifier`，而且驗證者不能只有自己；IMCC 的家規可以再加 `--require-approval-prefix user://anan`，讓核准一定要來自安安。

### 3.3 對話助手接 MCP

```bash
claude mcp add sicjs41 -- python3 /路徑/sicjs41_mcp.py
```

Claude Desktop 的設定檔：

```json
{"mcpServers": {"sicjs41": {"command": "python3", "args": ["/路徑/sicjs41_mcp.py"], "env": {"SICJS41_LOG_ROOT": "/路徑/日誌資料夾"}}}}
```

工具：`sicjs_rules`、`sicjs_template`、`sicjs_validate`、`sicjs_append`、`sicjs_next`、`sicjs_verify`。
提示：`sicjs_quickload`（等於快速載入提示）。
`SICJS41_LOG_ROOT` 有設時，日誌路徑只能在那個資料夾裡。

### 3.4 agent CLI 接 hook

hook 只記顯性事實（事件名稱、工具名稱、session），不替模型編隱性欄位；`current_action` 寫 null，驗證時會出 WARN「語義斷裂」，這是照 N-004 的設計，不是錯。
模型之後再用 MCP 的 `sicjs_next` 補宣告隱性欄位。
Claude Code `settings.json` 範例：

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "python3 /路徑/sicjs41.py next /路徑/log.jsonl --from-hook"}]}]}}
```

### 3.5 Python API

```python
import importlib.util
s = importlib.util.spec_from_file_location("sicjs41", "/路徑/sicjs41.py"); k = importlib.util.module_from_spec(s); s.loader.exec_module(k)
k.validate_packet(packet, previous=[...])   # {"pass", "errors", "warnings"}
k.append_packet("log.jsonl", packet)        # 驗證後寫入
k.next_packet("log.jsonl", {"action": "...", "description": "..."})
k.verify_log("log.jsonl")
k.sha256_uri(obj)                           # SICJS-C14N-1
```

## 4. 日誌信封

每一行是 `{seq, prev_hash, packet, hash}`。
`hash` 是 `{seq, prev_hash, packet}` 經 SICJS-C14N-1 正規化（鍵排序、無空白、UTF-8、禁止浮點數）後的 sha256，寫成 `sha256:` 加 64 個十六進位字。
第一筆的 `prev_hash` 是 `GENESIS`。
這個格式跟德德現有日誌相同；德德日誌的全部封包（另一支工具寫的）用本工具驗鏈通過。
注意：鏈只證明紀錄沒被改，不證明內容是真的（A-005）；寫日誌的工具若被行動中的 agent 控制，就不能當獨立驗證者（T-002）。

## 5. 驗了什麼、跟官方驗證器差在哪

| 項目 | 本工具 | 官方 `sic_validate.py` |
|---|---|---|
| schema 結構（4.1 schema 用到的所有關鍵字） | 自己實作的 2020-12 子集 | `jsonschema` 套件 |
| 語義規則（issuance、lineage 含 3.0、created_round、擴充唯一與相依、attested 需證明、唯一自我認證） | 照官方程式移植 | 有 |
| 跨包歷史（round 遞增、合法轉換、created_round 不變、交付物改動警告） | 照官方程式移植 | `validate_history.py` |
| 時間格式 date-time | 一律檢查 | 只有裝了 `rfc3339-validator` 才檢查 |
| 執行證明、簽章、預期執行契約（attested／transparent profile） | **不檢查** | `verify_execution_trace.py`、`verify_packet_conformance.py` |
| 核准一定要來自某人 | 選用的家規旗標 | 沒有 |

差異測試（2026-11-26）：第一次 73 個案例（官方測試封包與範例 17、德德日誌當時 34 包、故意做壞的變體 17、歷史測試組 5），發布前重跑 74 個（日誌 35 包）；官方驗證器在裝好時間格式檢查的環境下，兩邊結論不同的數量都是零。
沒裝時間格式檢查時，只有「時間格式錯」那一案不同，原因如上表。

## 6. 測試結果

| 編號 | 內容 | 結果 |
|---|---|---|
| T1 | 內嵌 schema、檔案 schema、凍結雜湊三者一致 | 通過 |
| T2 | 與官方驗證器差異測試 | 73 案與重跑 74 案，結論不同都是零 |
| T3 | 寫入、驗鏈、竄改、自我認證、非法轉換、終點重開 | 14／14 通過 |
| T4 | MCP：initialize、tools/list、tools/call、prompts/get、錯誤處理 | 12／12 通過 |
| T5 | `sicjs41.js` 對單包案例的結論與官方驗證器一致；技術頁手機與桌面不溢出、對話框可開 | 69 案結論不同為零；截圖檢查通過 |
| T6 | 快速載入提示貼進全新對話後，模型寫的封包過官方驗證器 | **未測**（需要 API 金鑰） |

## 7. 限制與不宣稱

- 工具不是信任根（T-001）；它跑在誰的機器上、誰能改它，決定它能證明多少。
- 雜湊鏈證明完整性，不證明真實（A-005）。
- 不支援 attested／transparent profile 的執行證明驗證；需要時用官方套件。
- 外部擴充登記表只在 Python API 收（`external_extension_ids`），指令列沒有旗標。
- 快速載入提示把 `change_authority_refs` 寫成 `user://anan`（IMCC 用）；別的團隊要換成自己的變更權人。
- 工具包是德德做、德德測的，還沒有另一家廠牌或另一個人獨立重跑。

## 8. 版本紀錄

| 版本 | sicjs41.py 的 sha256 | 改了什麼 |
|---|---|---|
| 1.0.0 | `2d947d8b784d88ad1047d2df9761e8d98b3b17752cff8b283470075df168bd4a` | 第一版（日誌第 35 筆記的就是這份） |
| 1.0.0（同號第二份，已作廢） | `80d937b02040bdbd8d06d5e8bd41c43b0bf371c737fe6108cd2a73ebc2ff511a` | oneOf 不過時多列出最接近那一支的錯誤；版本號忘了改，違反 SIC-JS 自己的 G-001（識別碼不可重用） |
| 1.0.1 | `a70f3b7e429e256e9e72bc7e5136cbd6d53125e067256270db5e12faca68eb72` | 內容同上一列，只把版本號改正；所有測試重跑。`--version` 還不會驗凍結 schema，但上一版 manifest 寫成會驗，寫錯了 |
| 1.0.2 | 見 `manifest.json` | `--version` 先驗內嵌的凍結 schema 再印版本，壞了就以代碼 1 拒絕；內嵌副本損壞、或輸入讀不到 JSON 時，只給一行 FAIL，不丟程式追蹤訊息；所有測試重跑 |

`--version` 的自我檢查只抓得到檔案損壞或被改了一部分。
整個檔案被換掉時，只有從工具外面比對 sha256 才抓得到，所以載入時一定要自己算 sha256 跟 manifest 比。

現行版本與雜湊一律以技術頁的 `kit/manifest.json` 為準。
