#!/bin/bash
# W1: upstream-type=none, upstream=null → expect PASS, upstream_type=none, upstream=null
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" \
  --entity-model "TestModel" \
  --context "W1 test: none/null" \
  --current-action "test" \
  --user "TestUser" \
  --round 1 \
  --mode toolkit \
  --upstream-type none \
  --upstream null \
  --output /tmp/W1_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W1_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='none', f'Expected none, got {r[\"upstream_type\"]}'
assert r['upstream'] is None or r['upstream']=='null', f'Expected null, got {r[\"upstream\"]}'
print('W1 assertions PASS')
"
