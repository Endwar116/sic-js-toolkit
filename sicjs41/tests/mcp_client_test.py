#!/usr/bin/env python3
"""T4 MCP 腳本客戶端：送 initialize、tools/list、tools/call、prompts/get，比對回應欄位。Usage: mcp_client_test.py KIT_DIR"""
import json, os, subprocess, sys, tempfile, shutil
kit = sys.argv[1]
d = tempfile.mkdtemp()
p = subprocess.Popen([sys.executable, "-I", os.path.join(kit, "sicjs41_mcp.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, text=True, env={**os.environ, "SICJS41_LOG_ROOT": d})
n = 0
def rpc(method, params=None, notify=False):
    global n
    m = {"jsonrpc": "2.0", "method": method}
    if params is not None: m["params"] = params
    if not notify: n += 1; m["id"] = n
    p.stdin.write(json.dumps(m, ensure_ascii=False) + "\n"); p.stdin.flush()
    return None if notify else json.loads(p.stdout.readline())
ok = True
def expect(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + str(detail)[:400])); ok &= bool(cond)
def text(r): return r["result"]["content"][0]["text"]
try:
    r = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}})
    expect("initialize: protocolVersion, tools capability, serverInfo", r["result"]["protocolVersion"] == "2025-06-18" and "tools" in r["result"]["capabilities"] and r["result"]["serverInfo"]["name"] == "sicjs41", r)
    rpc("notifications/initialized", {}, notify=True)
    r = rpc("tools/list", {})
    names = [t["name"] for t in r["result"]["tools"]]
    expect("tools/list: six tools with inputSchema", names == ["sicjs_rules", "sicjs_template", "sicjs_validate", "sicjs_append", "sicjs_next", "sicjs_verify"] and all("inputSchema" in t for t in r["result"]["tools"]), names)
    r = rpc("tools/call", {"name": "sicjs_template", "arguments": {"agent": "McpAgent", "task_id": "MC-1", "title": "t", "deliverable": "d"}})
    pkt = json.loads(text(r)); expect("tools/call sicjs_template returns a packet", pkt["sic_version"] == "4.1" and pkt["task"]["id"] == "MC-1", r)
    r = rpc("tools/call", {"name": "sicjs_validate", "arguments": {"packet": pkt}})
    res = json.loads(text(r)); expect("tools/call sicjs_validate on template: pass", res["pass"] and not r["result"]["isError"], res)
    bad = dict(pkt); bad["extra"] = 1
    r = rpc("tools/call", {"name": "sicjs_validate", "arguments": {"packet": bad}})
    expect("tools/call sicjs_validate on bad packet: isError + FAIL", r["result"]["isError"] and "additionalProperties" in text(r), r)
    L = os.path.join(d, "mcp.jsonl")
    r = rpc("tools/call", {"name": "sicjs_append", "arguments": {"log_path": L, "packet": pkt}})
    expect("tools/call sicjs_append writes #1", json.loads(text(r)).get("written") and json.loads(text(r))["seq"] == 1, r)
    r = rpc("tools/call", {"name": "sicjs_next", "arguments": {"log_path": L, "declare": {"action": "step two", "description": "did step two"}}})
    expect("tools/call sicjs_next writes #2", json.loads(text(r)).get("seq") == 2, r)
    r = rpc("tools/call", {"name": "sicjs_next", "arguments": {"log_path": L, "declare": {"status": "completed", "action": "done", "description": "claim"}}})
    expect("tools/call sicjs_next refuses completion without evidence", r["result"]["isError"] and json.loads(text(r))["written"] is False, r)
    r = rpc("tools/call", {"name": "sicjs_verify", "arguments": {"log_path": L}})
    expect("tools/call sicjs_verify passes 2 entries", json.loads(text(r))["pass"] and json.loads(text(r))["entries"] == 2, r)
    r = rpc("tools/call", {"name": "sicjs_verify", "arguments": {"log_path": "/etc/passwd"}})
    expect("log path outside SICJS41_LOG_ROOT refused", r["result"]["isError"] and "outside" in text(r), r)
    r = rpc("prompts/get", {"name": "sicjs_quickload", "arguments": {"lang": "en"}})
    expect("prompts/get sicjs_quickload returns the loader", "SIC-JS 4.1 quick load" in r["result"]["messages"][0]["content"]["text"], r)
    r = rpc("nonexistent/method", {})
    expect("unknown method -> JSON-RPC -32601", r.get("error", {}).get("code") == -32601, r)
finally:
    p.stdin.close(); p.wait(timeout=10); shutil.rmtree(d)
print("MCP TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
