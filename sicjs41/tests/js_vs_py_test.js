// sicjs41.js vs sicjs41.py on generated cases (the Python tool is the reference here; its parity with the
// official IMCC validator is documented in the README). Usage: node js_vs_py_test.js KIT_DIR
// 頁內驗證器 sicjs41.js 與 sicjs41.py 對同一批案例比對結論。
const fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const kit = path.resolve(process.argv[2] || "..");
const V = require(path.join(kit, "sicjs41.js"));
const schema = JSON.parse(fs.readFileSync(path.join(kit, "sic-js-schema-v4.1.json"), "utf8"));
const base = JSON.parse(execFileSync("python3", ["-I", path.join(kit, "sicjs41.py"), "template", "--agent", "T", "--model", "m", "--task-id", "KT-1", "--title", "t", "--deliverable", "d"]).toString());
base.state.current_action = "x";
const clone = o => JSON.parse(JSON.stringify(o));
const muts = {
  ok: p => p, extra_root_key: p => { p.x = 1; }, bad_version: p => { p.sic_version = "4.2"; }, round_zero: p => { p.round = 0; },
  bool_round: p => { p.round = true; }, missing_current_action: p => { delete p.state.current_action; }, null_current_action: p => { p.state.current_action = null; },
  bad_status: p => { p.task.status = "done"; }, completed_no_assurance: p => { p.task.status = "completed"; }, created_round_gt_round: p => { p.task.created_round = 5; },
  issuance_mismatch: p => { p.governance.issuance_id = "SICJS-4.1-FR-001"; }, no_lineage_30: p => { p.governance.lineage.inherits_from = ["2.0"]; },
  event_null: p => { p.event = null; }, intent_missing_user_intent: p => { delete p.intent.user_intent; }, bad_datetime: p => { p.event.timestamp = "2026-13-45 99:99"; },
  bad_task_id: p => { p.task.id = "TASK-1"; }, bad_upstream: p => { p.relation.upstream = "xyz"; },
  self_verified_completed: p => { p.task.status = "completed"; p.assurance = { evidence_refs: ["e"], approval_refs: ["a"], verifier_refs: [p.entity.identity_ref], integrity_refs: [], verification_status: "verified" }; },
  good_completed: p => { p.task.status = "completed"; p.assurance = { evidence_refs: ["e"], approval_refs: ["user://anan"], verifier_refs: ["tool://ci"], integrity_refs: [], verification_status: "verified" }; },
  dup_extension: p => { p.extensions = [{ id: "org.x/a", version: "1.0.0", required: false, schema_ref: "s", depends_on: [] }, { id: "org.x/a", version: "1.0.0", required: false, schema_ref: "s", depends_on: [] }]; },
};
let diff = 0, n = 0;
const tmp = fs.mkdtempSync(path.join(require("os").tmpdir(), "sj-"));
for (const [name, f] of Object.entries(muts)) {
  const p = clone(base); f(p); n++;
  const js = V.validate(p, schema).pass;
  const file = path.join(tmp, name + ".json"); fs.writeFileSync(file, JSON.stringify(p));
  let py = true; try { execFileSync("python3", ["-I", path.join(kit, "sicjs41.py"), "validate", file], { stdio: "pipe" }); } catch (e) { py = false; }
  if (js !== py) { diff++; console.log("DIFF", name, "js", js, "py", py); }
}
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`JS vs PY cases=${n} differ=${diff}`); process.exit(diff ? 1 : 0);
