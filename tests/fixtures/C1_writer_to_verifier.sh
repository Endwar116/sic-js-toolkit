#!/bin/bash
# C1: Writer W2 output → feed to Verifier → PASS
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
  --entity-name "TestEntity" --entity-model "TestModel" \
  --context "C1 consistency test" --current-action "test" \
  --user "TestUser" --round 10 --mode toolkit \
  --upstream-type cryptographic --upstream a3f8b2c1d4e5f607 \
  --output /tmp/C1_out.json
WRITE_EXIT=$?
bash "$TOOLKIT_DIR/src/verifier/sic_verify.sh" --file /tmp/C1_out.json --mode toolkit
VERIFY_EXIT=$?
echo "C1 write_exit=$WRITE_EXIT verify_exit=$VERIFY_EXIT"
[ $WRITE_EXIT -eq 0 ] && [ $VERIFY_EXIT -eq 0 ] && echo "C1 PASS" || echo "C1 FAIL"
