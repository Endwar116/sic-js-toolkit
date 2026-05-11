#!/bin/bash
# W3: upstream-type=file, upstream=XIED_v2.json → expect PASS
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "W3 test: file label" --current-action "test" \
  --user "TestUser" --round 3 --mode toolkit \
  --upstream-type file --upstream XIED_v2.json \
  --output /tmp/W3_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W3_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='file', f'Expected file, got {r[\"upstream_type\"]}'
assert r['upstream']=='XIED_v2.json', f'Expected XIED_v2.json, got {r[\"upstream\"]}'
print('W3 assertions PASS')
"
