#!/bin/bash
# C2: Writer auto-derive W4 output → feed to Verifier → PASS
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "C2 auto-derive consistency" --current-action "test" \
  --user "TestUser" --round 11 --mode toolkit \
  --upstream a3f8b2c1d4e5f607 \
  --output /tmp/C2_out.json
WRITE_EXIT=$?
bash "$TOOLKIT_DIR/src/verifier/sic_verify.sh" --file /tmp/C2_out.json --mode toolkit
VERIFY_EXIT=$?
echo "C2 write_exit=$WRITE_EXIT verify_exit=$VERIFY_EXIT"
[ $WRITE_EXIT -eq 0 ] && [ $VERIFY_EXIT -eq 0 ] && echo "C2 PASS" || echo "C2 FAIL"
