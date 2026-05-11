#!/bin/bash
# sic_verify.sh — CMP-05 Verifier (thin wrapper)
#
# Architecture: this script has NO independent validation logic.
# It only forwards arguments to CMP-03 validator (single source of truth).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR="$SCRIPT_DIR/../validator/validate_skeleton_v2.py"

if [ ! -f "$VALIDATOR" ]; then
    echo "❌ Validator not found: $VALIDATOR" >&2
    exit 4
fi

# Forward all arguments to validator
python3 "$VALIDATOR" "$@"
