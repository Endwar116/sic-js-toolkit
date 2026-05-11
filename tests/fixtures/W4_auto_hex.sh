#!/bin/bash
# W4: --upstream=a3f8b2c1d4e5f607 (no --upstream-type) → auto-derive cryptographic
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "W4 test: auto-derive hex" --current-action "test" \
  --user "TestUser" --round 4 --mode toolkit \
  --upstream a3f8b2c1d4e5f607 \
  --output /tmp/W4_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W4_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='cryptographic', f'Expected auto-derived cryptographic, got {r[\"upstream_type\"]}'
print('W4 assertions PASS')
"
