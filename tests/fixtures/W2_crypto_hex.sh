#!/bin/bash
# W2: upstream-type=cryptographic, upstream=a3f8b2c1d4e5f607 → expect PASS
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "W2 test: cryptographic" --current-action "test" \
  --user "TestUser" --round 2 --mode toolkit \
  --upstream-type cryptographic --upstream a3f8b2c1d4e5f607 \
  --output /tmp/W2_out.json
echo "exit: $?"
python3 -c "
import json
with open('/tmp/W2_out.json') as f: d=json.load(f)
r=d['relation']
assert r['upstream_type']=='cryptographic', f'Expected cryptographic, got {r[\"upstream_type\"]}'
assert r['upstream']=='a3f8b2c1d4e5f607', f'Expected hex, got {r[\"upstream\"]}'
print('W2 assertions PASS')
"
