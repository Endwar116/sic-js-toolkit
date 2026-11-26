# SIC-JS 4.1 Toolkit Manual (English)

Version: v1.0 | Date: 2026-11-26 | Author: Dede (`agent://imcc/德德`) | Decision owner: Anan (`user://anan`)
Chinese version: `SICJS41_工具包手冊_中文版_v1.0_2026_11_26.md` (same content).
Status: the toolkit is Dede's reference implementation, not part of the frozen protocol; the protocol itself is IMCC `protocols/SIC-JS_4.1_FR-002/`.

**In one line: one Python file plus one MCP server, nothing to install, to write, validate and chain SIC-JS 4.1 records; with no tools at all, paste the quick-load prompt into a chat.**

## 1. Versions

| Version | Status | How this kit treats it |
|---|---|---|
| 4.1 (`SICJS-4.1-FR-002`) | Frozen, ratified by Anan on 2026-09-17 | The main body; the schema file is embedded byte for byte |
| 4.2 (`SICJS-4.2-PF-001`) | Draft, not frozen; Anan handles 4.2 herself | Differences described in the page's appendix only; the tools do not support it |

## 2. Contents

| File | Purpose |
|---|---|
| `sicjs41.py` | Main tool: template, validate, history, append, carry forward, verify chain, canonical hash, write schema. Python standard library only (tested on Python 3.13). |
| `sicjs41_mcp.py` | MCP server (stdio, JSON-RPC 2.0) exposing the same functions to chat assistants. Keep it in the same folder as `sicjs41.py`. |
| `sicjs41.js` | Single-packet validator for browsers and Node (same schema and semantic rules; no history, no writing); the page's in-page validator is this file. |
| `sic-js-schema-v4.1.json` | The frozen schema file, sha256 `23c15b4c…2ac56ca7`, matching `registry/canonical_hashes.json`. |
| `SICJS41_Quick_Load_Prompt_EN_v1.0_2026_11_26.md` and the Chinese one | Paste into a new conversation when no tools are available. |
| This manual, zh and en | Usage and limits. |

## 3. Four ways to use it

### 3.1 Chat only, no tools

Paste the quick-load prompt into a new conversation. The model ends each reply with a packet.
Limit: without tools the time, round and hashes are written by the model itself, so they are claims, not verified state (A-001).

### 3.2 Command line

```bash
python3 sicjs41.py template --agent Dede --model claude-opus-5-5 --task-id KT-1 --title Title --deliverable Deliverable > p.json
python3 sicjs41.py append log.jsonl p.json            # validate, then write entry 1; nothing is written on failure
python3 sicjs41.py next log.jsonl --declare '{"action":"write code","description":"finished sicjs41.py","pending":["tests"]}'
python3 sicjs41.py verify log.jsonl                    # frozen hash + chain + every packet + history
python3 sicjs41.py validate packet.json --prev previous.json
python3 sicjs41.py rules --lang en
python3 sicjs41.py quickload --lang en
```

How `next` splits the work: round, time, the previous hash (`relation.upstream`) and governance come from the tool; `--declare` carries only implicit fields: `action`, `description`, `pending`, `core_question`, `context`, `status`, `task` (when switching tasks), `evidence`, `approval`, `verifier`.
To write `completed`, `--declare` must give `evidence`, `approval` and `verifier`, and the verifier must not be only yourself. IMCC can add `--require-approval-prefix user://anan` so approvals must come from Anan.

### 3.3 Chat assistants through MCP

```bash
claude mcp add sicjs41 -- python3 /path/to/sicjs41_mcp.py
```

Claude Desktop configuration:

```json
{"mcpServers": {"sicjs41": {"command": "python3", "args": ["/path/to/sicjs41_mcp.py"], "env": {"SICJS41_LOG_ROOT": "/path/to/logs"}}}}
```

Tools: `sicjs_rules`, `sicjs_template`, `sicjs_validate`, `sicjs_append`, `sicjs_next`, `sicjs_verify`.
Prompt: `sicjs_quickload` (the quick-load prompt).
With `SICJS41_LOG_ROOT` set, log paths must stay inside that folder.

### 3.4 Agent CLIs through hooks

A hook records explicit facts only (event name, tool name, session) and never invents implicit fields for the model; `current_action` is null, which validation reports as a "semantic rupture" WARN. That follows N-004 by design; it is not an error.
The model later declares the implicit fields with the MCP tool `sicjs_next`.
Claude Code `settings.json` example:

```json
{"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "python3 /path/to/sicjs41.py next /path/to/log.jsonl --from-hook"}]}]}}
```

### 3.5 Python API

```python
import importlib.util
s = importlib.util.spec_from_file_location("sicjs41", "/path/to/sicjs41.py"); k = importlib.util.module_from_spec(s); s.loader.exec_module(k)
k.validate_packet(packet, previous=[...])   # {"pass", "errors", "warnings"}
k.append_packet("log.jsonl", packet)        # validate, then append
k.next_packet("log.jsonl", {"action": "...", "description": "..."})
k.verify_log("log.jsonl")
k.sha256_uri(obj)                           # SICJS-C14N-1
```

## 4. Ledger envelope

Each line is `{seq, prev_hash, packet, hash}`.
`hash` is the sha256 of `{seq, prev_hash, packet}` after SICJS-C14N-1 canonicalization (sorted keys, no whitespace, UTF-8, no floats), written as `sha256:` plus 64 hex characters.
The first entry's `prev_hash` is `GENESIS`.
This is the same format as Dede's existing ledger; all of its packets (written by another tool) verify with this kit.
Note: the chain proves the record was not changed, not that it is true (A-005); a logger the acting agent controls is not an independent verifier (T-002).

## 5. What is checked, and how it differs from the official validator

| Item | This kit | Official `sic_validate.py` |
|---|---|---|
| Schema structure (every keyword the 4.1 schema uses) | Own 2020-12 subset implementation | `jsonschema` package |
| Semantic rules (issuance, lineage includes 3.0, created_round, unique and resolvable extensions, attested needs attestation, sole self-certification) | Ported from the official code | Yes |
| Cross-packet history (rounds increase, legal transitions, created_round fixed, deliverable-change warning) | Ported from the official code | `validate_history.py` |
| date-time format | Always checked | Checked only when `rfc3339-validator` is installed |
| Execution attestation, signatures, expected execution contracts (attested/transparent) | **Not checked** | `verify_execution_trace.py`, `verify_packet_conformance.py` |
| Approval must come from a named party | Optional local flag | No |

Differential test (2026-11-26): 73 cases on the first run (17 official fixtures and examples, Dede's ledger at 34 packets, 17 deliberately broken variants, 5 history sets) and 74 on the pre-publication rerun (35 packets). With date-time checking available to the official validator, the two disagree on zero cases both times. Without it, only the bad-timestamp case differs, for the reason above.

## 6. Test results

| ID | What | Result |
|---|---|---|
| T1 | Embedded schema, schema file and frozen hash agree | Pass |
| T2 | Differential test against the official validator | 73 and, on rerun, 74 cases; zero disagreements |
| T3 | Append, verify, tamper, self-certification, illegal transition, reopening a terminal state | 14/14 pass |
| T4 | MCP: initialize, tools/list, tools/call, prompts/get, error handling | 12/12 pass |
| T5 | `sicjs41.js` matches the official verdicts on single-packet cases; the page does not overflow on phone or desktop and the dialog opens | 69 cases, zero disagreements; screenshots pass |
| T6 | A fresh-context model, given the quick-load prompt, writes packets that pass the official validator | **Not tested** (needs an API key) |

## 7. Limits and non-claims

- The tool is not a root of trust (T-001); whose machine it runs on, and who can change it, decides what it can prove.
- The hash chain proves integrity, not truth (A-005).
- Execution attestation for attested/transparent profiles is not verified; use the official package for that.
- An external extension registry is accepted only through the Python API (`external_extension_ids`); the command line has no flag for it.
- The quick-load prompt sets `change_authority_refs` to `user://anan` (IMCC); other teams should use their own change authority.
- Dede built and tested this kit; no other vendor or person has re-run it independently yet.

## 8. Version history

| Version | sha256 of sicjs41.py | What changed |
|---|---|---|
| 1.0.0 | `2d947d8b784d88ad1047d2df9761e8d98b3b17752cff8b283470075df168bd4a` | First release (this is what ledger entry 35 recorded) |
| 1.0.0 (second build under the same number, withdrawn) | `80d937b02040bdbd8d06d5e8bd41c43b0bf371c737fe6108cd2a73ebc2ff511a` | oneOf failures also list the closest branch's errors; the version label was not bumped, which broke SIC-JS's own G-001 (identifiers are never reused) |
| 1.0.1 | see `manifest.json` | Same content as the row above with the version label corrected; every test re-run |

The current version and hash are always those in the technical page's `kit/manifest.json`.
