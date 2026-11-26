/* sicjs41.js — SIC-JS 4.1 (SICJS-4.1-FR-002) single-packet validator for the browser and Node, no dependencies.
   瀏覽器與 Node 用的 SIC-JS 4.1 單包驗證器，無相依套件。Port of sicjs41.py (德德, IMCC, 2026-11-26, MIT).
   Usage: SICJS41.validate(packet, schema) -> {pass, errors, warnings}. The caller supplies the frozen schema object. */
(function (root) {
  "use strict";
  var ISSUANCE = "SICJS-4.1-FR-002";
  var RFC3339 = /^(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(\.\d+)?([Zz]|[+-](\d{2}):(\d{2}))$/;
  function isDateTime(s) {
    var m = RFC3339.exec(s); if (!m) return false;
    var y = +m[1], mo = +m[2], d = +m[3], h = +m[4], mi = +m[5], se = +m[6];
    if (mo < 1 || mo > 12 || h > 23 || mi > 59 || se > 60) return false;
    var dim = [31, (y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1];
    if (d < 1 || d > dim) return false;
    if (m[9] && (+m[9] > 23 || +m[10] > 59)) return false;
    return true;
  }
  function typeOk(v, t) {
    switch (t) {
      case "object": return v !== null && typeof v === "object" && !Array.isArray(v);
      case "array": return Array.isArray(v);
      case "string": return typeof v === "string";
      case "boolean": return typeof v === "boolean";
      case "null": return v === null;
      case "integer": return typeof v === "number" && Number.isInteger(v);
      case "number": return typeof v === "number" && isFinite(v);
    }
    return false;
  }
  function jeq(a, b) {
    if (a === b) return true;
    if (typeof a !== typeof b || a === null || b === null) return false;
    if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) return false; for (var i = 0; i < a.length; i++) if (!jeq(a[i], b[i])) return false; return true; }
    if (typeof a === "object") { if (Array.isArray(b)) return false; var ka = Object.keys(a), kb = Object.keys(b); if (ka.length !== kb.length) return false; for (var j = 0; j < ka.length; j++) if (!(ka[j] in b) || !jeq(a[ka[j]], b[ka[j]])) return false; return true; }
    return false;
  }
  function resolve(root, ref) {
    var node = root; ref.slice(2).split("/").forEach(function (p) { node = node[p.replace(/~1/g, "/").replace(/~0/g, "~")]; }); return node;
  }
  function chars(s) { return Array.from(s).length; }
  function check(inst, sch, root, path, errs) {
    if (sch === true || (sch && typeof sch === "object" && Object.keys(sch).length === 0)) return;
    if (sch === false) { errs.push([path, "false schema"]); return; }
    if (sch.$ref) check(inst, resolve(root, sch.$ref), root, path, errs);
    if (sch.type !== undefined) {
      var ts = Array.isArray(sch.type) ? sch.type : [sch.type];
      if (!ts.some(function (t) { return typeOk(inst, t); })) { errs.push([path, "type: expected " + ts.join("|")]); return; }
    }
    if ("const" in sch && !jeq(inst, sch["const"])) errs.push([path, "const: expected " + JSON.stringify(sch["const"])]);
    if (sch["enum"] && !sch["enum"].some(function (e) { return jeq(inst, e); })) errs.push([path, "enum: " + JSON.stringify(inst) + " not in " + JSON.stringify(sch["enum"])]);
    if (typeof inst === "string") {
      if (sch.minLength !== undefined && chars(inst) < sch.minLength) errs.push([path, "minLength " + sch.minLength]);
      if (sch.pattern !== undefined && !(new RegExp(sch.pattern, "u")).test(inst)) errs.push([path, "pattern " + sch.pattern]);
      if (sch.format === "date-time" && !isDateTime(inst)) errs.push([path, "format date-time (RFC 3339)"]);
    }
    if (typeOk(inst, "number") && sch.minimum !== undefined && inst < sch.minimum) errs.push([path, "minimum " + sch.minimum]);
    if (Array.isArray(inst)) {
      if (sch.minItems !== undefined && inst.length < sch.minItems) errs.push([path, "minItems " + sch.minItems]);
      if (sch.uniqueItems) { outer: for (var i = 0; i < inst.length; i++) for (var j = 0; j < i; j++) if (jeq(inst[i], inst[j])) { errs.push([path, "uniqueItems"]); break outer; } }
      if (sch.items !== undefined) inst.forEach(function (x, k) { check(x, sch.items, root, path.concat([k]), errs); });
    }
    if (typeOk(inst, "object")) {
      (sch.required || []).forEach(function (r) { if (!(r in inst)) errs.push([path, "required: " + r]); });
      var props = sch.properties || {};
      Object.keys(inst).forEach(function (k) {
        if (k in props) check(inst[k], props[k], root, path.concat([k]), errs);
        else if ("additionalProperties" in sch) {
          if (sch.additionalProperties === false) errs.push([path, "additionalProperties: " + k + " not allowed"]);
          else if (typeof sch.additionalProperties === "object") check(inst[k], sch.additionalProperties, root, path.concat([k]), errs);
        }
      });
    }
    (sch.allOf || []).forEach(function (s) { check(inst, s, root, path, errs); });
    if (sch.oneOf) {
      var branch = sch.oneOf.map(function (s) { var e = []; check(inst, s, root, path, e); return e; });
      var ok = branch.filter(function (b) { return b.length === 0; }).length;
      if (ok !== 1) {
        errs.push([path, "oneOf: " + ok + " branches matched, need exactly 1"]);
        var near = branch.filter(function (b) { return b.length && !(b.length === 1 && b[0][0].join(".") === path.join(".") && b[0][1].indexOf("type:") === 0); });
        if (ok === 0 && near.length) { near.sort(function (a, b) { return a.length - b.length; }); near[0].forEach(function (e) { errs.push(e); }); }
      }
    }
    if (sch["if"] !== undefined) {
      var e2 = []; check(inst, sch["if"], root, path, e2);
      if (e2.length === 0) { if (sch.then !== undefined) check(inst, sch.then, root, path, errs); }
      else if (sch["else"] !== undefined) check(inst, sch["else"], root, path, errs);
    }
  }
  function semantic(p) {
    var sem = [], warn = [], task = p.task;
    if (task && typeof task === "object" && !Array.isArray(task)) {
      if (Number.isInteger(task.created_round) && Number.isInteger(p.round) && task.created_round > p.round) sem.push("task.created_round (" + task.created_round + ") must be <= round (" + p.round + ")");
    }
    var st = p.state;
    if (st && typeof st === "object" && ("current_action" in st) && st.current_action === null) warn.push("semantic_rupture: state.current_action is null (N-004)");
    if (Array.isArray(p.extensions)) {
      var ids = p.extensions.filter(function (x) { return x && typeof x.id === "string"; }).map(function (x) { return x.id; });
      if (new Set(ids).size !== ids.length) sem.push("extensions[].id must be unique (X-002)");
      p.extensions.forEach(function (x) { if (x && typeof x === "object") (x.depends_on || []).forEach(function (d) { if (ids.indexOf(d) < 0) sem.push("extension dependency '" + d + "' is not declared (X-004)"); }); });
    }
    var ex = p.execution;
    if (ex && typeof ex === "object") (((ex.authority || {}).permissions) || []).forEach(function (pm) { if (pm && typeof pm === "object" && pm.enforcement_ref == null) warn.push("permission '" + pm.action + "' is declarative only: enforcement_ref is null"); });
    var gov = p.governance || {};
    if (gov.issuance_id !== ISSUANCE) sem.push("governance.issuance_id mismatch (must be " + ISSUANCE + ")");
    if (((gov.lineage || {}).inherits_from || []).indexOf("3.0") < 0) sem.push("governance.lineage.inherits_from must include 3.0");
    var asr = p.assurance || {};
    if (gov.conformance_profile === "attested" || gov.conformance_profile === "transparent") {
      if (asr.verification_status === "verified" && !(asr.attestation_refs && asr.attestation_refs.length)) sem.push("attested/transparent verified packet requires attestation_refs (A-003)");
    }
    if (task && task.status === "completed") {
      var ident = (p.entity || {}).identity_ref, vs = asr.verifier_refs || [];
      if (ident && vs.length && vs.every(function (v) { return v === ident; })) sem.push("No Sole Self-Certification: acting entity is the only verifier (A-004)");
    }
    return [sem, warn];
  }
  function validate(packet, schema) {
    var errs = [];
    check(packet, schema, schema, [], errs);
    var out = errs.map(function (e) { return "schema [" + (e[0].join(".") || "<root>") + "]: " + e[1]; });
    var sw = (packet && typeof packet === "object" && !Array.isArray(packet)) ? semantic(packet) : [[], []];
    out = out.concat(sw[0]);
    return { pass: out.length === 0, errors: out, warnings: sw[1] };
  }
  var api = { validate: validate, isDateTime: isDateTime, ISSUANCE: ISSUANCE, VERSION: "1.0.0" };
  if (typeof module !== "undefined" && module.exports) module.exports = api; else root.SICJS41 = api;
})(typeof self !== "undefined" ? self : this);
