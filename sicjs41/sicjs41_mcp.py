#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sicjs41_mcp.py — MCP server (stdio, JSON-RPC 2.0, one message per line) for the SIC-JS 4.1 toolkit. Stdlib only.
SIC-JS 4.1 的 MCP 伺服器：標準輸入輸出、JSON-RPC 2.0、一行一則訊息；只用標準函式庫。作者：德德（IMCC），2026-11-26，MIT。

Needs sicjs41.py in the same folder. / 需要同資料夾的 sicjs41.py。
Claude Code:    claude mcp add sicjs41 -- python3 /path/to/sicjs41_mcp.py
Claude Desktop: {"mcpServers": {"sicjs41": {"command": "python3", "args": ["/path/to/sicjs41_mcp.py"]}}}
Env SICJS41_LOG_ROOT (optional): if set, log_path arguments must stay inside this folder. / 設了就只准寫這個資料夾裡的日誌。
Tools: sicjs_rules, sicjs_template, sicjs_validate, sicjs_append, sicjs_next, sicjs_verify.  Prompt: sicjs_quickload.
"""
import importlib.util, json, os, sys, traceback

sys.dont_write_bytecode = True  # keep the kit folder clean / 不在工具資料夾留下快取檔

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sicjs41", os.path.join(_HERE, "sicjs41.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)
K.schema()  # frozen-hash check at start-up; exits if the embedded schema was modified

SERVER = {"name": "sicjs41", "version": K.VERSION}
PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"]
ROOT = os.environ.get("SICJS41_LOG_ROOT")

def _obj(props, req=()):
    return {"type": "object", "properties": props, "required": list(req), "additionalProperties": False}

STR = {"type": "string"}
TOOLS = [
    {"name": "sicjs_rules", "description": "SIC-JS 4.1 normative summary (N/G/A/T/X rules, task state machine, completed gate). 規範摘要。",
     "inputSchema": _obj({"lang": {"type": "string", "enum": ["zh", "en"]}})},
    {"name": "sicjs_template", "description": "A minimal valid governed SIC-JS 4.1 packet to start from. 最小合規封包範本。",
     "inputSchema": _obj({"agent": STR, "model": STR, "task_id": {"type": "string", "description": "e.g. AB-1 or PROJ-AB-12"},
                          "title": STR, "deliverable": STR, "user": STR, "user_intent": STR})},
    {"name": "sicjs_validate", "description": "Validate one packet: frozen schema + semantic rules, optionally against earlier packets (transitions, rounds). Returns pass, errors, warnings. 驗證單包。",
     "inputSchema": _obj({"packet": {"type": "object"}, "previous": {"type": "array", "items": {"type": "object"}}}, ["packet"])},
    {"name": "sicjs_append", "description": "Validate a full packet, then append it to a JSONL ledger as {seq, prev_hash, packet, hash}. Fail-closed. 驗證後寫入日誌。",
     "inputSchema": _obj({"log_path": STR, "packet": {"type": "object"}, "require_approval_prefix": STR}, ["log_path", "packet"])},
    {"name": "sicjs_next", "description": "Write the next packet by carrying the last one forward. The tool fills explicit fields (round, time, upstream hash, governance); you declare only implicit ones: action, description, pending, core_question, status, task, evidence, approval, verifier. 延續上一包，只宣告隱性欄位。",
     "inputSchema": _obj({"log_path": STR, "declare": {"type": "object"}, "dry_run": {"type": "boolean"}, "require_approval_prefix": STR}, ["log_path", "declare"])},
    {"name": "sicjs_verify", "description": "Verify a ledger: frozen schema hash, hash chain, every packet, cross-packet history. 驗鏈。",
     "inputSchema": _obj({"log_path": STR}, ["log_path"])},
]
PROMPTS = [{"name": "sicjs_quickload", "description": "Load SIC-JS 4.1 working rules and a template into this conversation. 快速載入。",
            "arguments": [{"name": "lang", "description": "zh or en", "required": False},
                          {"name": "agent", "description": "your agent name", "required": False}]}]

def _path(p):
    p = os.path.abspath(os.path.expanduser(p))
    if ROOT and os.path.commonpath([p, os.path.abspath(ROOT)]) != os.path.abspath(ROOT):
        raise ValueError("log_path outside SICJS41_LOG_ROOT")
    return p

def call_tool(name, a):
    if name == "sicjs_rules":
        return K.RULES[a.get("lang", "zh")]
    if name == "sicjs_template":
        return K.template(a.get("agent", "ExampleAgent"), a.get("model", "unknown-model"), a.get("task_id"), a.get("title"),
                          a.get("deliverable"), a.get("user", "安安"), a.get("user_intent", "(paste the user's words verbatim)"))
    if name == "sicjs_validate":
        return K.validate_packet(a["packet"], previous=a.get("previous") or None)
    if name == "sicjs_append":
        return K.append_packet(_path(a["log_path"]), a["packet"], a.get("require_approval_prefix"))
    if name == "sicjs_next":
        lp = _path(a["log_path"])
        pkt = K.next_packet(lp, a.get("declare") or {})
        if a.get("dry_run"):
            r = K.validate_packet(pkt, previous=[x["packet"] for x in K.read_log(lp)]); r["packet"] = pkt; return r
        return K.append_packet(lp, pkt, a.get("require_approval_prefix"))
    if name == "sicjs_verify":
        return K.verify_log(_path(a["log_path"]))
    raise KeyError("unknown tool " + name)

def handle(msg):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        want = params.get("protocolVersion")
        return {"protocolVersion": want if want in PROTOCOLS else PROTOCOLS[0],
                "capabilities": {"tools": {"listChanged": False}, "prompts": {"listChanged": False}},
                "serverInfo": SERVER,
                "instructions": "SIC-JS 4.1 (SICJS-4.1-FR-002). Use sicjs_next to log each step; declare only implicit fields. "
                                "Never mark completed without evidence, an approval and a verifier other than yourself."}
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        try:
            out = call_tool(name, args)
            text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False, indent=1)
            failed = isinstance(out, dict) and out.get("pass") is False
            return {"content": [{"type": "text", "text": text}], "isError": bool(failed)}
        except SystemExit as e:
            return {"content": [{"type": "text", "text": str(e)}], "isError": True}
        except Exception as e:  # tool errors are reported in the result, not as protocol errors
            return {"content": [{"type": "text", "text": "%s: %s" % (type(e).__name__, e)}], "isError": True}
    if method == "prompts/list":
        return {"prompts": PROMPTS}
    if method == "prompts/get":
        a = params.get("arguments") or {}
        lang = a.get("lang") if a.get("lang") in ("zh", "en") else "zh"
        return {"description": "SIC-JS 4.1 quick load",
                "messages": [{"role": "user", "content": {"type": "text", "text": K.quickload(lang, a.get("agent") or "(your name)")}}]}
    raise LookupError(method)

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}) + "\n"); sys.stdout.flush(); continue
        if "id" not in msg:  # notification (e.g. notifications/initialized): no reply
            continue
        try:
            res = {"jsonrpc": "2.0", "id": msg["id"], "result": handle(msg)}
        except LookupError:
            res = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32601, "message": "method not found: %s" % msg.get("method")}}
        except Exception as e:
            res = {"jsonrpc": "2.0", "id": msg["id"], "error": {"code": -32603, "message": str(e), "data": traceback.format_exc()[-500:]}}
        sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n"); sys.stdout.flush()

if __name__ == "__main__":
    main()
