#!/bin/bash
# W6: --upstream=null (no --upstream-type) → auto-derive none
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "W6 test: auto-derive null" --current-action "test" \
  --user "TestUser" --round 6 --mode toolkit \
  --upstream null \
  --output /tmp/W6_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W6_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='none', f'Expected auto-derived none, got {r[\"upstream_type\"]}'
print('W6 assertions PASS')
"
