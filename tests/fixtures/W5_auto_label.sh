#!/bin/bash
# W5: --upstream=XIED_v2.json (no --upstream-type) → auto-derive file
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "W5 test: auto-derive label" --current-action "test" \
  --user "TestUser" --round 5 --mode toolkit \
  --upstream XIED_v2.json \
  --output /tmp/W5_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W5_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='file', f'Expected auto-derived file, got {r[\"upstream_type\"]}'
print('W5 assertions PASS')
"
