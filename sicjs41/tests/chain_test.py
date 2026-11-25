#!/usr/bin/env python3
"""T3 寫入／驗鏈／竄改測試 / append, verify and tamper test. Usage: chain_test.py KIT_DIR [EXISTING_LEDGER.jsonl]"""
import json, os, sys, subprocess, tempfile, shutil
kit = sys.argv[1]
ledger = sys.argv[2] if len(sys.argv) > 2 else None
T = os.path.join(kit, "sicjs41.py")
def run(*a, stdin=None):
    p = subprocess.run([sys.executable, "-I", T, *a], capture_output=True, text=True, input=stdin)
    return p.returncode, (p.stdout + p.stderr).strip()
ok = True
def expect(name, cond, detail=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  " + detail[:300])); ok &= cond
d = tempfile.mkdtemp()
try:
    # 1 cross-implementation: the existing ledger written by another tool verifies here
    if ledger:
        rc, o = run("verify", ledger); expect("verify an existing ledger written by another tool", rc == 0, o)
    # 2 template -> append -> next x2 -> verify
    L = os.path.join(d, "log.jsonl"); P = os.path.join(d, "p.json")
    rc, o = run("template", "--agent", "TestAgent", "--model", "test-model", "--task-id", "KT-1", "--title", "t", "--deliverable", "d")
    pkt = json.loads(o); pkt["state"]["current_action"] = "set up"; json.dump(pkt, open(P, "w"), ensure_ascii=False)
    rc, o = run("append", L, P); expect("append template packet", rc == 0 and "#1" in o, o)
    rc, o = run("next", L, "--declare", json.dumps({"action": "write code", "description": "wrote sicjs41.py", "pending": ["tests"]}))
    expect("next with model-declared implicit fields", rc == 0 and "#2" in o, o)
    rc, o = run("next", L, "--from-hook", stdin=json.dumps({"hook_event_name": "Stop", "session_id": "abc123", "cwd": "/tmp"}))
    expect("next from hook (explicit facts only, current_action null -> WARN)", rc == 0 and "semantic_rupture" in o, o)
    rc, o = run("verify", L); expect("verify fresh log", rc == 0 and "PASS 3 entries" in o, o)
    # 3 fail-closed: illegal transition, self-completion
    rc, o = run("next", L, "--declare", json.dumps({"status": "completed", "action": "done", "description": "claim done",
               "evidence": ["file:x"], "approval": ["agent://local/TestAgent"], "verifier": ["agent://local/TestAgent"]}))
    expect("self-certified completion refused (A-004)", rc == 1 and "NOT WRITTEN" in o and "Sole Self-Certification" in o, o)
    rc, o = run("next", L, "--declare", json.dumps({"status": "completed", "action": "done", "description": "claim done"}))
    expect("completion without evidence refused (A-002)", rc == 1 and "NOT WRITTEN" in o, o)
    rc, o = run("next", L, "--declare", json.dumps({"status": "pending", "action": "x", "description": "x"}))
    expect("illegal transition in_progress->pending refused (N-003)", rc == 1 and "illegal transition" in o, o)
    rc, o = run("next", L, "--require-approval-prefix", "user://anan", "--declare", json.dumps({"status": "completed", "action": "done", "description": "done",
               "evidence": ["file:x"], "approval": ["user://someone"], "verifier": ["tool://ci"]}))
    expect("local rule: approval must come from user://anan", rc == 1 and "local rule" in o, o)
    rc, o = run("next", L, "--require-approval-prefix", "user://anan", "--declare", json.dumps({"status": "completed", "action": "done", "description": "done",
               "evidence": ["file:x"], "approval": ["user://anan#msg-1"], "verifier": ["tool://ci"]}))
    expect("completion with evidence + external approval + independent verifier accepted", rc == 0 and "#4" in o, o)
    rc, o = run("next", L, "--declare", json.dumps({"status": "in_progress", "action": "reopen", "description": "reopen"}))
    expect("terminal completed cannot reopen (N-003)", rc == 1 and "illegal transition" in o, o)
    # 4 tamper: change one byte in entry 2
    lines = open(L, encoding="utf-8").read().splitlines()
    lines[1] = lines[1].replace("wrote sicjs41.py", "wrote sicjs41.pz", 1)
    T2 = os.path.join(d, "tampered.jsonl"); open(T2, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    rc, o = run("verify", T2); expect("one changed byte -> verify fails", rc == 1 and "entry 2" in o, o)
    lines = open(L, encoding="utf-8").read().splitlines(); del lines[1]
    T3 = os.path.join(d, "dropped.jsonl"); open(T3, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    rc, o = run("verify", T3); expect("deleted entry -> verify fails", rc == 1, o)
    # 5 modified schema file refused
    S = os.path.join(d, "s.json"); b = open(os.path.join(kit, "sic-js-schema-v4.1.json"), "rb").read().replace(b'"4.1"', b'"4.2"', 1); open(S, "wb").write(b)
    p = subprocess.run([sys.executable, "-I", "-c", "import importlib.util,sys;s=importlib.util.spec_from_file_location('k',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.schema(sys.argv[2])", T, S], capture_output=True, text=True)
    expect("modified schema file refused (frozen hash)", p.returncode != 0 and "frozen" in (p.stdout + p.stderr), p.stderr)
finally:
    shutil.rmtree(d)
print("CHAIN TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
