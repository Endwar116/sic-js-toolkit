#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sicjs41.py — SIC-JS 4.1 portable toolkit (issuance SICJS-4.1-FR-002), single file, Python standard library only.
SIC-JS 4.1 可攜工具包：單一檔案、只用 Python 標準函式庫。作者：德德（IMCC），2026-11-26，MIT。

The frozen machine schema is embedded byte-for-byte and checked against its frozen SHA-256 before every use;
a modified copy is refused (fail-closed). Nothing here regenerates a schema from Markdown.
內嵌的凍結 schema 每次使用前都比對凍結雜湊，被改過就拒絕執行；本檔不從 Markdown 反推 schema。

Commands / 指令:
  sicjs41.py quickload [--lang zh|en]          paste-into-chat loader / 貼進新對話的快速載入提示
  sicjs41.py rules [--lang zh|en]              condensed normative rules / 規範摘要
  sicjs41.py template [--agent A --task-id ID --title T --deliverable D]   minimal valid packet / 最小合規封包
  sicjs41.py validate PACKET.json [--prev PREV.json]                      schema + semantic (+ transition) / 單包驗證
  sicjs41.py history PACKET.json ...                                       cross-packet history / 跨包歷史
  sicjs41.py append LOG.jsonl PACKET.json|-                                validate, then append an envelope / 驗證後寫入
  sicjs41.py next LOG.jsonl --declare '{"action":...}' [--from-hook]       carry forward + model-declared fields / 延續上一包
  sicjs41.py verify LOG.jsonl                                              frozen hash + chain + packets + history / 驗鏈
  sicjs41.py hash FILE.json                                                SICJS-C14N-1 sha256 / 正規化雜湊
  sicjs41.py schema [--out FILE]                                           write the frozen schema bytes / 輸出凍結 schema
Exit code 0 = pass, 1 = fail. Python API: validate_packet(), check_history(), append_packet(), next_packet(), verify_log().

Limits / 限制: hash = integrity, not truth (A-005); this tool is not a root of trust (T-001); completion still needs an
independent verifier and an approval (A-004). Differences from the official validator are listed in the manual.
"""
import argparse, base64, copy, datetime as _dt, hashlib, json, os, re, sys, zlib

VERSION = "1.0.1"  # 1.0.0 = sha256 2d947d8b…; 1.0.1 adds closest-branch detail to oneOf errors and a new version label
ISSUANCE = "SICJS-4.1-FR-002"
SCHEMA_SHA256 = "23c15b4c758a1c48d1631e2c4c499b822ef2a3905fb67b00ea64d32f2ac56ca7"
_SCHEMA_ZB64 = (
    "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")
_SCHEMA_CACHE = {}

LEGAL = {"pending": {"in_progress", "archived", "dismissed"}, "in_progress": {"completed", "archived", "dismissed"},
         "archived": {"pending", "in_progress"}, "completed": set(), "dismissed": set()}
TOP_ORDER = ["sic_version", "governance", "task", "execution", "round", "entity", "state", "relation", "assurance",
             "event", "intent", "extensions"]
GOVERNANCE = {
    "issuance_id": ISSUANCE, "lifecycle": "frozen", "conformance_profile": "governed",
    "lineage": {"inherits_from": ["3.0"], "supersedes": ["SICJS-4.1-FR-001"], "reverts_to": None},
    "ruleset_refs": ["sicjs://rules/v4.1/fr002"], "decision_refs": [], "change_authority_refs": ["user://anan"],
    "version_policy": {"mode": "monotonic_append_only", "reuse": "forbidden", "rollback": "new_higher_identifier_only",
                       "consumed_on_issuance": True},
    "identifier_policy": {"reuse": "forbidden", "ordered_serials": "monotonic", "retired_ids": "tombstoned",
                          "registry_ref": "registry/version_registry.json"},
    "trust_boundary": {"self_certification": "forbidden", "verifier_separation_required": True, "root_of_trust_refs": [],
                       "enforcement_boundary_refs": [], "protected_signing_key_refs": [],
                       "note": "Governed profile. Hash chain proves log integrity only, not truth (A-005)."},
}

# ---------------------------------------------------------------- schema (frozen bytes)
def schema_bytes(path=None):
    """Frozen schema bytes; refuses anything whose sha256 is not the frozen anchor. / 雜湊不符就拒絕。"""
    if path:
        b = open(path, "rb").read()
    else:
        b = zlib.decompress(base64.b64decode(_SCHEMA_ZB64))
    got = hashlib.sha256(b).hexdigest()
    if got != SCHEMA_SHA256:
        raise SystemExit("FAIL frozen-schema: sha256 %s != frozen %s (refusing a modified schema)" % (got, SCHEMA_SHA256))
    return b

def schema(path=None):
    if path not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[path] = json.loads(schema_bytes(path).decode("utf-8"))
    return _SCHEMA_CACHE[path]

# ---------------------------------------------------------------- JSON Schema 2020-12 subset (every keyword the 4.1 schema uses)
_RFC3339 = re.compile(r"^(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(\.\d+)?([Zz]|[+-](\d{2}):(\d{2}))$")

def _is_datetime(s):
    m = _RFC3339.match(s)
    if not m:
        return False
    y, mo, d, h, mi, se = (int(m.group(i)) for i in range(1, 7))
    try:
        _dt.datetime(y, mo, d, h, mi, min(se, 59))
    except ValueError:
        return False
    if se > 60 or (m.group(9) and (int(m.group(9)) > 23 or int(m.group(10)) > 59)):
        return False
    return True

def _type_ok(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list), "string": isinstance(v, str),
            "boolean": isinstance(v, bool), "null": v is None,
            "integer": isinstance(v, int) and not isinstance(v, bool),
            "number": isinstance(v, (int, float)) and not isinstance(v, bool)}.get(t, False)

def _jeq(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_jeq(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_jeq(x, y) for x, y in zip(a, b))
    return a == b

def _resolve(root, ref):
    if not ref.startswith("#/"):
        raise ValueError("only local $ref supported: " + ref)
    node = root
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node

def _check(inst, sch, root, path, errs, fmt=True):
    if sch is True or sch == {}:
        return
    if sch is False:
        errs.append((path, "false schema")); return
    if "$ref" in sch:
        _check(inst, _resolve(root, sch["$ref"]), root, path, errs, fmt)
    t = sch.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_type_ok(inst, x) for x in ts):
            errs.append((path, "type: expected %s" % "|".join(ts))); return
    if "const" in sch and not _jeq(inst, sch["const"]):
        errs.append((path, "const: expected %s" % json.dumps(sch["const"], ensure_ascii=False)))
    if "enum" in sch and not any(_jeq(inst, e) for e in sch["enum"]):
        errs.append((path, "enum: %s not in %s" % (json.dumps(inst, ensure_ascii=False)[:40], sch["enum"])))
    if isinstance(inst, str):
        if "minLength" in sch and len(inst) < sch["minLength"]:
            errs.append((path, "minLength %d" % sch["minLength"]))
        if "pattern" in sch and not re.search(sch["pattern"], inst):
            errs.append((path, "pattern %s" % sch["pattern"]))
        if fmt and sch.get("format") == "date-time" and not _is_datetime(inst):
            errs.append((path, "format date-time (RFC 3339)"))
    if _type_ok(inst, "number") and "minimum" in sch and inst < sch["minimum"]:
        errs.append((path, "minimum %s" % sch["minimum"]))
    if isinstance(inst, list):
        if "minItems" in sch and len(inst) < sch["minItems"]:
            errs.append((path, "minItems %d" % sch["minItems"]))
        if sch.get("uniqueItems"):
            for i in range(len(inst)):
                if any(_jeq(inst[i], inst[j]) for j in range(i)):
                    errs.append((path, "uniqueItems")); break
        if "items" in sch:
            for i, x in enumerate(inst):
                _check(x, sch["items"], root, path + [i], errs, fmt)
    if isinstance(inst, dict):
        for r in sch.get("required", []):
            if r not in inst:
                errs.append((path, "required: %s" % r))
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                _check(v, props[k], root, path + [k], errs, fmt)
            elif "additionalProperties" in sch:
                ap = sch["additionalProperties"]
                if ap is False:
                    errs.append((path, "additionalProperties: %s not allowed" % k))
                elif isinstance(ap, dict):
                    _check(v, ap, root, path + [k], errs, fmt)
    for sub in sch.get("allOf", []):
        _check(inst, sub, root, path, errs, fmt)
    if "oneOf" in sch:
        branch = [_errs(inst, sub, root, path, fmt) for sub in sch["oneOf"]]
        ok = sum(1 for b in branch if not b)
        if ok != 1:
            errs.append((path, "oneOf: %d branches matched, need exactly 1" % ok))
            near = [b for b in branch if b and not (len(b) == 1 and b[0][0] == path and b[0][1].startswith("type:"))]
            if ok == 0 and near:  # show why the closest branch failed / 顯示最接近那一支為什麼不過
                errs.extend(min(near, key=len))
    if "if" in sch:
        if not _errs(inst, sch["if"], root, path, fmt):
            if "then" in sch:
                _check(inst, sch["then"], root, path, errs, fmt)
        elif "else" in sch:
            _check(inst, sch["else"], root, path, errs, fmt)

def _errs(inst, sch, root, path, fmt):
    e = []
    _check(inst, sch, root, path, e, fmt)
    return e

def schema_errors(packet, schema_path=None, check_format=True):
    root = schema(schema_path)
    return ["schema [%s]: %s" % (".".join(map(str, p)) or "<root>", m) for p, m in _errs(packet, root, root, [], check_format)]

# ---------------------------------------------------------------- semantic rules (ported from the official sic_validate.py)
def semantic(packet, external_extension_ids=()):
    sem, warn = [], []
    task = packet.get("task")
    if isinstance(task, dict):
        cr, rr = task.get("created_round"), packet.get("round")
        if isinstance(cr, int) and isinstance(rr, int) and cr > rr:
            sem.append("task.created_round (%s) must be <= round (%s)" % (cr, rr))
    st = packet.get("state")
    if isinstance(st, dict) and st.get("current_action", "__missing__") is None:
        warn.append("semantic_rupture: state.current_action is null (N-004)")
    exts = packet.get("extensions")
    if isinstance(exts, list):
        ids = [x.get("id") for x in exts if isinstance(x, dict) and isinstance(x.get("id"), str)]
        if len(ids) != len(set(ids)):
            sem.append("extensions[].id must be unique (X-002)")
        for x in exts:
            if isinstance(x, dict):
                for dep in x.get("depends_on", []) or []:
                    if dep not in ids and dep not in set(external_extension_ids):
                        sem.append("extension dependency %r is not declared (X-004)" % dep)
    ex = packet.get("execution")
    if isinstance(ex, dict):
        for p in (ex.get("authority") or {}).get("permissions", []) or []:
            if isinstance(p, dict) and p.get("enforcement_ref") is None:
                warn.append("permission %r is declarative only: enforcement_ref is null" % p.get("action"))
    gov = packet.get("governance") or {}
    if gov.get("issuance_id") != ISSUANCE:
        sem.append("governance.issuance_id mismatch (must be %s)" % ISSUANCE)
    if "3.0" not in ((gov.get("lineage") or {}).get("inherits_from") or []):
        sem.append("governance.lineage.inherits_from must include 3.0")
    asr = packet.get("assurance") or {}
    if gov.get("conformance_profile") in ("attested", "transparent"):
        if asr.get("verification_status") == "verified" and not asr.get("attestation_refs"):
            sem.append("attested/transparent verified packet requires attestation_refs (A-003)")
    if isinstance(task, dict) and task.get("status") == "completed":
        ident = (packet.get("entity") or {}).get("identity_ref")
        vers = asr.get("verifier_refs") or []
        if ident and vers and all(v == ident for v in vers):
            sem.append("No Sole Self-Certification: acting entity is the only verifier (A-004)")
    return sem, warn

def check_history(packets, allow_task_switch=True):
    """Cross-packet rules (ported from the official validate_history.py). / 跨包規則。"""
    errs, warns, prev_round, prev_task, snaps = [], [], None, None, {}
    for i, r in enumerate(packets):
        rr = r.get("round")
        if not isinstance(rr, int) or isinstance(rr, bool):
            errs.append("packet[%d] round missing/non-integer" % i)
        elif prev_round is not None and rr <= prev_round:
            errs.append("packet[%d] round %d not greater than previous %d" % (i, rr, prev_round))
        if isinstance(rr, int):
            prev_round = rr
        t = r.get("task")
        if not isinstance(t, dict):
            prev_task = None; continue
        tid = t.get("id")
        if not tid:
            continue
        if prev_task and not allow_task_switch and tid != prev_task.get("id"):
            errs.append("task id changed within a single task-lineage history: %s -> %s" % (prev_task.get("id"), tid))
        if tid not in snaps:
            snaps[tid] = {"created_round": t.get("created_round"), "status": t.get("status"), "deliverable": t.get("deliverable")}
        else:
            s = snaps[tid]
            if t.get("created_round") != s["created_round"]:
                errs.append("%s: created_round mutated (N-002)" % tid)
            old, new = s["status"], t.get("status")
            if old != new and new not in LEGAL.get(old, set()):
                errs.append("%s: illegal transition %s->%s (N-003)" % (tid, old, new))
            if s["deliverable"] != t.get("deliverable") and (r.get("event") or {}).get("trigger") != "task_revision_approved":
                warns.append("%s: deliverable changed without event.trigger=task_revision_approved" % tid)
            s["status"], s["deliverable"] = new, t.get("deliverable")
        prev_task = t
    return errs, warns

def validate_packet(packet, previous=None, schema_path=None, check_format=True, external_extension_ids=()):
    """Return {'pass', 'errors', 'warnings'}; previous = list of earlier packets for transition checks."""
    errs = schema_errors(packet, schema_path, check_format)
    sem, warn = semantic(packet, external_extension_ids)
    errs += sem
    if previous:
        herr, hwarn = check_history(list(previous) + [packet])
        errs += herr; warn += hwarn
    return {"pass": not errs, "errors": errs, "warnings": warn}

# ---------------------------------------------------------------- SICJS-C14N-1 and the ledger envelope
def _c14n_check(v):
    if isinstance(v, float):
        raise ValueError("SICJS-C14N-1 forbids floating-point numbers")
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, str):
                raise ValueError("object keys must be strings")
            _c14n_check(x)
    elif isinstance(v, list):
        for x in v:
            _c14n_check(x)
    elif not (v is None or isinstance(v, (str, int, bool))):
        raise ValueError("unsupported type: %s" % type(v).__name__)

def canonical_bytes(obj):
    _c14n_check(obj)
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def sha256_uri(obj):
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()

def envelope_hash(env):
    return sha256_uri({k: env[k] for k in ("seq", "prev_hash", "packet")})

def read_log(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def append_packet(log_path, packet, require_approval_prefix=None):
    """Validate (single + history) then append {seq, prev_hash, packet, hash}. Fail-closed. / 不過就不寫。"""
    rows = read_log(log_path)
    hist = [r["packet"] for r in rows]
    res = validate_packet(packet, previous=hist)
    if require_approval_prefix and (packet.get("task") or {}).get("status") == "completed":
        if not any(str(a).startswith(require_approval_prefix) for a in (packet.get("assurance") or {}).get("approval_refs", [])):
            res["errors"].append("local rule: completed needs an approval from %s" % require_approval_prefix)
            res["pass"] = False
    if not res["pass"]:
        res["written"] = False
        return res
    env = {"seq": len(rows) + 1, "prev_hash": rows[-1]["hash"] if rows else "GENESIS", "packet": packet}
    env["hash"] = envelope_hash(env)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(env, ensure_ascii=False) + "\n")
    res.update(written=True, seq=env["seq"], hash=env["hash"])
    return res

def verify_log(log_path):
    rows = read_log(log_path)
    out = {"pass": False, "entries": len(rows), "errors": [], "warnings": []}
    if not rows:
        out["errors"].append("empty log: refusing to claim anything"); return out
    schema()  # frozen-hash check
    prev, hist = "GENESIS", []
    for i, env in enumerate(rows, 1):
        if env.get("seq") != i or env.get("prev_hash") != prev or envelope_hash(env) != env.get("hash"):
            out["errors"].append("entry %d: chain broken or content changed" % i); return out
        r = validate_packet(env["packet"])
        out["errors"] += ["entry %d: %s" % (i, e) for e in r["errors"]]
        out["warnings"] += ["entry %d: %s" % (i, w) for w in r["warnings"]]
        prev = env["hash"]; hist.append(env["packet"])
    herr, hwarn = check_history(hist)
    out["errors"] += ["history: " + e for e in herr]
    out["warnings"] += ["history: " + w for w in hwarn]
    out["pass"] = not out["errors"]
    out["last_hash"] = prev
    return out

# ---------------------------------------------------------------- packet construction
def now_iso(tz_hours=8):
    return _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=tz_hours))).isoformat(timespec="seconds")

def template(agent="ExampleAgent", model="unknown-model", task_id=None, title=None, deliverable=None, user="安安",
             user_intent="(paste the user's words verbatim)", identity_ref=None):
    ts = now_iso()
    p = {"sic_version": "4.1", "governance": copy.deepcopy(GOVERNANCE)}
    if task_id:
        p["task"] = {"id": task_id, "title": title or task_id, "deliverable": deliverable or "(deliverable)",
                     "status": "in_progress", "created_round": 1, "owner": agent, "priority": "P1", "time_horizon": "short"}
    p.update({"round": 1,
              "entity": {"name": agent, "model": model, "origin": "chat", "created_at": ts,
                         "identity_ref": identity_ref or "agent://local/" + agent},
              "state": {"context": "(where this work happens)", "current_action": "(what I am doing now)", "pending": [], "tone": "audit"},
              "relation": {"user": user, "anchor_memory": None, "linked_entities": [], "upstream": None, "links": []},
              "event": {"timestamp": ts, "description": "(what just happened)", "trigger": "user_instruction"},
              "intent": {"user_intent": user_intent, "system_intent": "governed SIC-JS 4.1 state", "core_question": "(the question this round answers)"},
              "extensions": []})
    return p

def next_packet(log_path, declare, from_hook=None):
    """Carry the last packet forward; explicit fields by tool, implicit fields from `declare` (or null from a hook).
    顯性欄位由工具帶，隱性欄位由模型宣告（declare）；hook 呼叫時隱性欄位不編，current_action 用 null。"""
    rows = read_log(log_path)
    if not rows:
        raise SystemExit("FAIL: empty log; start with `template` + `append` / 空日誌：先用 template 再 append")
    last = rows[-1]["packet"]
    p = copy.deepcopy(last)
    ts = now_iso()
    p["round"] = last["round"] + 1
    p["relation"]["upstream"] = rows[-1]["hash"][7:23]
    p["event"] = {"timestamp": ts, "description": "", "trigger": "milestone"}
    p.pop("assurance", None)
    d = dict(declare or {})
    if from_hook is not None:
        h = from_hook
        p["state"]["current_action"] = None
        p["event"]["trigger"] = "hook:" + str(h.get("hook_event_name", "unknown"))
        facts = ["hook=%s" % h.get("hook_event_name")] + ["%s=%s" % (k, str(h[k])[:60]) for k in ("tool_name", "session_id", "cwd") if h.get(k)]
        p["event"]["description"] = "; ".join(facts)
    if "action" in d: p["state"]["current_action"] = d["action"]
    if "description" in d: p["event"]["description"] = d["description"]
    if "trigger" in d: p["event"]["trigger"] = d["trigger"]
    if "pending" in d: p["state"]["pending"] = list(d["pending"])
    if "context" in d: p["state"]["context"] = d["context"]
    if "core_question" in d: p["intent"]["core_question"] = d["core_question"]
    if "user_intent" in d: p["intent"]["user_intent"] = d["user_intent"]
    if "status" in d and isinstance(p.get("task"), dict): p["task"]["status"] = d["status"]
    if "task" in d:  # switching to a new task: {"id","title","deliverable"}
        t = d["task"]
        prior = [x["packet"]["task"] for x in rows if (x["packet"].get("task") or {}).get("id") == t["id"]]
        p["task"] = {"id": t["id"], "title": t.get("title", t["id"]), "deliverable": t.get("deliverable", "(deliverable)"),
                     "status": t.get("status", "in_progress"), "created_round": prior[0]["created_round"] if prior else p["round"],
                     "owner": p["entity"]["name"], "priority": t.get("priority", "P1"), "time_horizon": t.get("time_horizon", "short")}
    if any(k in d for k in ("evidence", "approval", "verifier")) or (p.get("task") or {}).get("status") == "completed":
        done = (p.get("task") or {}).get("status") == "completed"
        p["assurance"] = {"evidence_refs": d.get("evidence", []), "approval_refs": d.get("approval", []),
                          "verifier_refs": d.get("verifier", []), "integrity_refs": [],
                          "verification_status": "verified" if done else "unverified", "claim_refs": [], "run_binding": None,
                          "attestation_level": "chained", "trace_ref": None, "execution_root_digest": None,
                          "attestation_refs": [], "transparency_refs": []}
    if not p["event"]["description"]:
        p["event"]["description"] = "(no description declared)"
    return {k: p[k] for k in TOP_ORDER if k in p}

# ---------------------------------------------------------------- texts
RULES = {"zh": """SIC-JS 4.1（SICJS-4.1-FR-002，凍結）規範摘要
六原語：task 要做什麼｜entity 誰｜state 現在狀態｜relation 關係｜event 發生什麼｜intent 為什麼。4.1 不加第七個。
四層：governance 規範與版本｜execution 執行邊界｜assurance 證據與驗證｜extensions 模組描述。
頂層順序：sic_version, governance, task?, execution?, round, entity, state, relation, assurance?, event, intent, extensions?；不得有其他頂層鍵（X-001）。
task 狀態：pending, in_progress, completed, dismissed, archived。
合法轉換：pending→in_progress/archived/dismissed；in_progress→completed/archived/dismissed；archived→pending/in_progress；completed、dismissed 是終點。
N-001 六原語語義與五狀態機不變。N-002 task.id、created_round 不可改。N-003 終點不可重開。N-004 current_action 鍵一定要有，可為 null（語義斷裂），不可為了過驗證而編。
G-001 版本與 issuance 識別碼不可重用。G-002 歷史只增不改，回滾用新的更高 issuance。G-003 凍結後改語義要用更高協議版本。G-004 協議治理與執行政策分開。
A-001 宣稱不等於已驗證。A-002 缺必要證據就沒有已驗證的完成。A-003 宣稱已驗證的外部效果，依 profile 需要可信證明。A-004 行動者不能是自己完成的唯一認證者。A-005 雜湊不能被說成語義為真的證明。A-006 隱藏推理不能當執行證據，只有留存的可觀察產物可以。
T-001 SIC-JS 不能是自己的信任根。T-002 行動者能單方改動或繞過的驗證者不算獨立。T-003 認證外部執行的簽章金鑰不應讓行動中的模型拿到。T-004 怕重放的證明要綁 run_id＋nonce。
X-001 核心 schema 封閉。X-002 擴充用唯一的命名空間 ID 與外部 schema/state 參照。X-003 required 擴充要有可用的 schema_ref。X-004 depends_on 要能解析。
完成閘門：status=completed 時，assurance.verification_status=verified，evidence_refs、approval_refs、verifier_refs 各至少 1 個，且行動者不是唯一驗證者。
attested／transparent profile 另需 execution、run_binding、trace_ref、execution_root_digest、attestation_refs≥1、root_of_trust_refs≥1；transparent 再加 transparency_refs≥1 與 attestation_level=transparency_witnessed。""",
         "en": """SIC-JS 4.1 (SICJS-4.1-FR-002, frozen) normative summary
Six primitives: task (what ought to be done) | entity (who) | state (current) | relation | event (what happened) | intent (why). No seventh primitive.
Four layers: governance | execution | assurance | extensions.
Top-level order: sic_version, governance, task?, execution?, round, entity, state, relation, assurance?, event, intent, extensions?; no other top-level keys (X-001).
task.status: pending, in_progress, completed, dismissed, archived.
Legal transitions: pending->in_progress/archived/dismissed; in_progress->completed/archived/dismissed; archived->pending/in_progress; completed and dismissed are terminal.
N-001 six primitives and the five-state machine preserved. N-002 task.id and created_round immutable. N-003 terminal states never reopen. N-004 state.current_action key must exist; null means semantic rupture and must not be replaced by invented text.
G-001 identifiers never reused. G-002 append-only history; rollback by a new higher issuance. G-003 post-freeze semantic change needs a higher protocol version. G-004 protocol governance distinct from runtime policy.
A-001 a claim is not verified state. A-002 missing required evidence means no verified completion. A-003 claimed-verified external effects need trusted attestation when the profile requires it. A-004 the acting agent is never the sole certifier of its own completion. A-005 a hash is not proof of semantic truth. A-006 hidden chain-of-thought is not execution evidence; only persisted observable artifacts are.
T-001 SIC-JS is not its own root of trust. T-002 a verifier the agent can modify or bypass is not independent. T-003 signing keys for external execution should be unavailable to the acting model. T-004 replay-sensitive attestations are bound to run_id + nonce.
X-001 core schema closed. X-002 unique namespaced extension ids with external schema/state refs. X-003 required extensions declare a usable schema_ref. X-004 depends_on must resolve.
Completed gate: status=completed needs assurance.verification_status=verified and at least one evidence_ref, approval_ref and verifier_ref, and the acting entity is not the only verifier.
attested/transparent profiles also need execution, run_binding, trace_ref, execution_root_digest, attestation_refs>=1, root_of_trust_refs>=1; transparent adds transparency_refs>=1 and attestation_level=transparency_witnessed."""}

QUICKLOAD = {"zh": """【SIC-JS 4.1 快速載入｜SICJS-4.1-FR-002（凍結版）】
從現在起，你在這個對話裡用 SIC-JS 4.1 記錄自己的工作狀態。照下面做：

1. 每一輪回覆的最後，附一個 SIC-JS 4.1 封包（一段 JSON）。
2. 頂層鍵照這個順序：sic_version、governance、task（有任務才放）、round、entity、state、relation、assurance（要宣稱證據或完成才放）、event、intent、extensions。不准加別的頂層鍵。
3. sic_version 固定 "4.1"。governance 整塊照下面範本原樣複製，不要改任何字。
4. round 每輪加 1，要從上一個封包讀，不能憑記憶。relation.upstream 填上一包雜湊的前 16 個十六進位字，沒有就寫 null。
5. task.status 只能是 pending、in_progress、completed、dismissed、archived。
   合法轉換：pending→in_progress/archived/dismissed；in_progress→completed/archived/dismissed；archived→pending/in_progress；completed 和 dismissed 是終點，不能再開。
   task.id 格式是大寫字母加數字，例如 AB-1 或 PROJ-AB-12（最後一段最多兩個字母、數字 1 到 999）；task.id 和 task.created_round 一旦寫下就不能改。
   priority 只能是 P0、P1、P2；time_horizon 只能是 short、medium、long。
6. 你不能自己宣布完成。
   要寫 completed，assurance 必須有：verification_status="verified"，evidence_refs、approval_refs、verifier_refs 各至少一個，而且驗證者不能只有你自己。
   拿不到使用者的核准，就維持 in_progress。
7. state.current_action 這個鍵一定要有；不知道現在在做什麼就寫 null（代表狀態斷掉了），不要編。
8. 宣稱不等於已驗證；雜湊只證明內容沒被改，不證明內容是真的；不要把看不到的推理過程當證據。
9. 時間、round、雜湊、工具事件這類「顯性欄位」，有工具或 hook 代填時以工具為準；你只負責「隱性欄位」：state.current_action、event.description、intent.core_question、state.pending。
10. intent.user_intent 放使用者的原話，逐字照抄，不要改寫。
11. 如果這個對話接了 sicjs41 工具（MCP 或指令列）：交出前先用 sicjs_validate 檢查；寫進日誌用 sicjs_next 或 sicjs_append，不要自己算雜湊。

範本（第一輪照填，括號裡換成真的內容）：
@@TEMPLATE@@""",
             "en": """[SIC-JS 4.1 quick load | SICJS-4.1-FR-002 (frozen)]
From now on, record your working state in this conversation with SIC-JS 4.1. Do this:

1. End every reply with one SIC-JS 4.1 packet (a JSON block).
2. Top-level keys in this order: sic_version, governance, task (only when there is a task), round, entity, state, relation, assurance (only when claiming evidence or completion), event, intent, extensions. No other top-level keys.
3. sic_version is always "4.1". Copy the governance block from the template below exactly; change nothing in it.
4. round goes up by 1 each reply; read it from the previous packet, never from memory. relation.upstream is the first 16 hex characters of the previous packet's hash, or null.
5. task.status is one of pending, in_progress, completed, dismissed, archived.
   Legal moves: pending->in_progress/archived/dismissed; in_progress->completed/archived/dismissed; archived->pending/in_progress; completed and dismissed are final.
   task.id is capital letters plus a number, e.g. AB-1 or PROJ-AB-12 (last part at most two letters, number 1 to 999); task.id and task.created_round never change once written.
   priority is P0, P1 or P2; time_horizon is short, medium or long.
6. You cannot declare your own completion.
   To write completed, assurance needs verification_status="verified" and at least one evidence_ref, approval_ref and verifier_ref, and you must not be the only verifier.
   Without the user's approval, stay in_progress.
7. The state.current_action key must always exist; if you do not know what you are doing, write null (the state broke). Never invent one.
8. A claim is not verified; a hash proves the content was not changed, not that it is true; hidden reasoning is never evidence.
9. Explicit fields (time, round, hashes, tool events) come from a tool or hook when one is present; you fill only the implicit fields: state.current_action, event.description, intent.core_question, state.pending.
10. intent.user_intent holds the user's words verbatim; do not paraphrase.
11. If the sicjs41 tool is connected (MCP or command line): run sicjs_validate before handing a packet over; write to the log with sicjs_next or sicjs_append, never compute hashes yourself.

Template (fill it in for round 1; replace the brackets with real content):
@@TEMPLATE@@"""}

def quickload(lang="zh", agent="(your name)"):
    t = template(agent=agent, model="(model)", task_id="AB-1", title="(task title)", deliverable="(deliverable)",
                 user="(user)", user_intent="(user's words verbatim)", identity_ref="agent://local/(your name)")
    t["entity"]["created_at"] = t["event"]["timestamp"] = "(ISO 8601 time with offset, e.g. 2026-11-26T10:00:00+08:00)"
    return QUICKLOAD[lang].replace("@@TEMPLATE@@", json.dumps(t, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------- CLI
def _load_json(path):
    return json.load(sys.stdin) if path == "-" else json.load(open(path, encoding="utf-8"))

def _report(res):
    for w in res.get("warnings", []):
        print("WARN:", w)
    for e in res.get("errors", []):
        print("FAIL:", e)
    return 0 if res.get("pass") else 1

def main(argv=None):
    ap = argparse.ArgumentParser(description="SIC-JS 4.1 portable toolkit (stdlib only) / SIC-JS 4.1 可攜工具包")
    ap.add_argument("--version", action="version", version="sicjs41 " + VERSION + " / " + ISSUANCE)
    sp = ap.add_subparsers(dest="cmd", required=True)
    q = sp.add_parser("quickload"); q.add_argument("--lang", default="zh", choices=["zh", "en"]); q.add_argument("--agent", default="(your name)")
    r = sp.add_parser("rules"); r.add_argument("--lang", default="zh", choices=["zh", "en"])
    t = sp.add_parser("template")
    for k, dflt in (("agent", "ExampleAgent"), ("model", "unknown-model"), ("task-id", None), ("title", None), ("deliverable", None), ("user", "安安")):
        t.add_argument("--" + k, default=dflt)
    v = sp.add_parser("validate"); v.add_argument("packet"); v.add_argument("--prev", nargs="*", default=[])
    v.add_argument("--no-format", action="store_true", help="do not assert format date-time (matches jsonschema without rfc3339-validator)")
    h = sp.add_parser("history"); h.add_argument("packets", nargs="+"); h.add_argument("--strict-task", action="store_true")
    a = sp.add_parser("append"); a.add_argument("log"); a.add_argument("packet"); a.add_argument("--require-approval-prefix")
    n = sp.add_parser("next"); n.add_argument("log"); n.add_argument("--declare", default="{}"); n.add_argument("--from-hook", action="store_true")
    n.add_argument("--dry-run", action="store_true"); n.add_argument("--require-approval-prefix")
    y = sp.add_parser("verify"); y.add_argument("log")
    s = sp.add_parser("hash"); s.add_argument("file")
    o = sp.add_parser("schema"); o.add_argument("--out")
    x = ap.parse_args(argv)
    if x.cmd == "quickload":
        print(quickload(x.lang, x.agent)); return 0
    if x.cmd == "rules":
        print(RULES[x.lang]); return 0
    if x.cmd == "template":
        print(json.dumps(template(x.agent, x.model, x.task_id, x.title, x.deliverable, x.user), ensure_ascii=False, indent=1)); return 0
    if x.cmd == "validate":
        res = validate_packet(_load_json(x.packet), previous=[_load_json(p) for p in x.prev], check_format=not x.no_format)
        rc = _report(res); print("PASS" if rc == 0 else "RESULT: FAIL"); return rc
    if x.cmd == "history":
        e, w = check_history([_load_json(p) for p in x.packets], allow_task_switch=not x.strict_task)
        rc = _report({"pass": not e, "errors": e, "warnings": w}); print("PASS" if rc == 0 else "RESULT: FAIL"); return rc
    if x.cmd == "append":
        res = append_packet(x.log, _load_json(x.packet), x.require_approval_prefix)
        rc = _report(res); print(("#%d %s" % (res["seq"], res["hash"][7:19])) if res.get("written") else "NOT WRITTEN (fail-closed)"); return rc
    if x.cmd == "next":
        hook = json.load(sys.stdin) if x.from_hook else None
        pkt = next_packet(x.log, json.loads(x.declare), hook)
        if x.dry_run:
            res = validate_packet(pkt, previous=[r["packet"] for r in read_log(x.log)])
            print(json.dumps(pkt, ensure_ascii=False, indent=1)); return _report(res)
        res = append_packet(x.log, pkt, x.require_approval_prefix)
        rc = _report(res); print(("#%d %s" % (res["seq"], res["hash"][7:19])) if res.get("written") else "NOT WRITTEN (fail-closed)"); return rc
    if x.cmd == "verify":
        res = verify_log(x.log)
        rc = _report(res)
        print(("PASS %d entries, last %s" % (res["entries"], res.get("last_hash", "")[:19])) if rc == 0 else "RESULT: FAIL"); return rc
    if x.cmd == "hash":
        print(sha256_uri(_load_json(x.file))); return 0
    if x.cmd == "schema":
        b = schema_bytes()
        if x.out:
            open(x.out, "wb").write(b); print("wrote %s sha256:%s" % (x.out, hashlib.sha256(b).hexdigest()))
        else:
            sys.stdout.write(b.decode("utf-8"))
        return 0

if __name__ == "__main__":
    sys.exit(main())
