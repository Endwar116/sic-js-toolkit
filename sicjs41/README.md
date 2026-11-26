# SIC-JS 4.1 kit (`sicjs41/`)

Version 1.0.1 · 2026-11-26 · issuance `SICJS-4.1-FR-002` (frozen) · MIT, same as this repository.

This folder is separate from the SIC-JS **v2.0** toolkit at the repository root; nothing outside `sicjs41/` was changed, and the root `MANIFEST.sha256` still verifies.

## What is here

| File | Purpose |
|---|---|
| `sicjs41.py` | One-file toolkit, Python standard library only: template, validate, history, append, next, verify, hash, schema. The frozen schema is embedded and checked against its frozen SHA-256 before every use. |
| `sicjs41_mcp.py` | MCP server (stdio, JSON-RPC 2.0): six tools (`sicjs_rules`, `sicjs_template`, `sicjs_validate`, `sicjs_append`, `sicjs_next`, `sicjs_verify`) and one prompt (`sicjs_quickload`). Keep it next to `sicjs41.py`. |
| `sicjs41.js` | Single-packet validator for browsers and Node, no dependencies. |
| `sic-js-schema-v4.1.json` | The frozen 4.1 schema, sha256 `23c15b4c758a1c48d1631e2c4c499b822ef2a3905fb67b00ea64d32f2ac56ca7`. Never regenerate it from Markdown. |
| `SICJS41_Quick_Load_Prompt_EN_…md`, `SICJS41_快速載入提示_中文版_…md` | Paste into a new conversation when no tools are available. |
| `SICJS41_Toolkit_Manual_EN_…md`, `SICJS41_工具包手冊_中文版_…md` | Usage, ledger envelope, differences from the official validator, limits. Read these first. |
| `tests/` | `chain_test.py` (append, verify, tamper), `mcp_client_test.py` (MCP protocol), `js_vs_py_test.js` (JavaScript vs Python verdicts). |

## Quick start

```bash
python3 sicjs41.py template --agent NAME --model MODEL --task-id KT-1 --title "title" --deliverable "deliverable" > p.json
python3 sicjs41.py append log.jsonl p.json
python3 sicjs41.py next log.jsonl --declare '{"action":"...","description":"...","pending":["..."]}'
python3 sicjs41.py verify log.jsonl
claude mcp add sicjs41 -- python3 /path/to/sicjs41/sicjs41_mcp.py
```

Run the tests from this folder: `python3 -I tests/chain_test.py .`, `python3 -I tests/mcp_client_test.py .`, `node tests/js_vs_py_test.js .`.

## Evidence and limits

- Differential test against the official IMCC validator (`sic_validate.py`, `validate_history.py`, with `rfc3339-validator` installed): 74 cases, zero disagreements. That test needs the IMCC 4.1 package, which is not in this repository, so it is reported here rather than shipped.
- The JavaScript validator agreed with the official verdicts on 69 single-packet cases.
- Not covered: execution attestation and signatures for the attested and transparent profiles.
- A hash chain proves a record was not changed, not that it is true; this kit is not a root of trust.
- Built and tested by Dede (IMCC) only; no other vendor or person has re-run it yet.

## 中文說明

這個資料夾是 SIC-JS 4.1（凍結版 `SICJS-4.1-FR-002`）的工具包，跟根目錄的 SIC-JS v2.0 工具包分開；根目錄的檔案一個都沒改，`MANIFEST.sha256` 仍然驗得過。

- `sicjs41.py`：一支檔，只用 Python 標準函式庫；凍結 schema 內嵌，每次使用前比對凍結雜湊。
- `sicjs41_mcp.py`：MCP 伺服器，六個工具加一個快速載入提示。
- `sicjs41.js`：瀏覽器與 Node 用的單包驗證器。
- 快速載入提示與手冊各有中文版和英文版，先讀手冊。
- 與 IMCC 官方驗證器差異測試 74 案零差異；那個測試需要 IMCC 的 4.1 套件，所以只在這裡報告結果，不附測試資料。
- 不檢查 attested、transparent 兩種等級的執行證明與簽章。
- 雜湊鏈只證明沒被改，不證明內容是真的；這個工具包不是信任根。
- 目前只有德德（IMCC）自己做、自己測，還沒有其他廠牌或其他人獨立重跑。
