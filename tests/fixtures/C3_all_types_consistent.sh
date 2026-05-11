#!/bin/bash
# C3: Writer W1/W2/W3 each → Verifier agrees on all three types
TOOLKIT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PASS=0; FAIL=0

for TYPE_ARG in "none null" "cryptographic a3f8b2c1d4e5f607" "file XIED_v2.json"; do
  TYPE=$(echo $TYPE_ARG | cut -d' ' -f1)
  UPSTREAM=$(echo $TYPE_ARG | cut -d' ' -f2)
  python3 "$TOOLKIT_DIR/src/writer/sic_write.py" \
    --entity-name "TestEntity" --entity-model "TestModel" \
    --context "C3 type=$TYPE" --current-action "test" \
    --user "TestUser" --round 12 --mode toolkit \
    --upstream-type "$TYPE" --upstream "$UPSTREAM" \
    --output /tmp/C3_${TYPE}_out.json 2>/dev/null
  bash "$TOOLKIT_DIR/src/verifier/sic_verify.sh" --file /tmp/C3_${TYPE}_out.json --mode toolkit > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "  C3[$TYPE] PASS"
    PASS=$((PASS+1))
  else
    echo "  C3[$TYPE] FAIL"
    FAIL=$((FAIL+1))
  fi
done

echo "C3 TOTAL: $((PASS+FAIL)) PASS: $PASS FAIL: $FAIL"
[ $FAIL -eq 0 ] && echo "C3 PASS" || echo "C3 FAIL"
