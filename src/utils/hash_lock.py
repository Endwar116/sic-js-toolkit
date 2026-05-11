"""
hash_lock.py — Canonical Schema Hash Lock

This module enforces the canonical schema hash invariant.
Any toolkit component that loads canonical schema MUST call
verify_canonical_lock() first.

If the canonical schema hash does not match CANONICAL_SCHEMA_HASH,
the system refuses to operate.

This protects against:
- Silent canonical schema modification (the C4-1 contamination root cause)
- Drift between release pack and toolkit copy
- Unauthorized schema extension
"""

import hashlib
import json
import os
import sys

# Locked canonical schema hash from release pack (sealed by 協議中樞|4)
# Source of truth: 德德 release pack (D-F1-A RESOLVED)
CANONICAL_SCHEMA_HASH = "efb2947b2ea3817bb8cf739116229b781148a3f802b59b4f32005211c8ce26e6"

# Default canonical schema path relative to toolkit root
DEFAULT_CANONICAL_PATH = "schema/canonical/sic-js-schema-v2.0.json"

# Exit code for hash mismatch
EXIT_CANONICAL_TAMPERED = 9


class CanonicalSchemaTampered(Exception):
    """Raised when canonical schema hash does not match locked value."""
    pass


def compute_hash(file_path):
    """Compute SHA-256 of file contents."""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_canonical_lock(canonical_path=None, raise_on_mismatch=True):
    """
    Verify canonical schema hash matches locked value.
    
    Args:
        canonical_path: Path to canonical schema (default: DEFAULT_CANONICAL_PATH)
        raise_on_mismatch: If True, raise exception on mismatch.
                           If False, return False on mismatch.
    
    Returns:
        True if hash matches, False if mismatch (and raise_on_mismatch=False)
    
    Raises:
        CanonicalSchemaTampered: if hash mismatch and raise_on_mismatch=True
        FileNotFoundError: if canonical schema file not found
    """
    if canonical_path is None:
        # Find canonical schema relative to toolkit root
        toolkit_root = find_toolkit_root()
        canonical_path = os.path.join(toolkit_root, DEFAULT_CANONICAL_PATH)
    
    if not os.path.exists(canonical_path):
        raise FileNotFoundError(f"Canonical schema not found: {canonical_path}")
    
    actual_hash = compute_hash(canonical_path)
    if actual_hash != CANONICAL_SCHEMA_HASH:
        if raise_on_mismatch:
            raise CanonicalSchemaTampered(
                f"Canonical schema hash mismatch.\n"
                f"  Expected: {CANONICAL_SCHEMA_HASH}\n"
                f"  Actual:   {actual_hash}\n"
                f"  File:     {canonical_path}\n"
                f"This indicates the canonical schema has been modified.\n"
                f"Restore from release pack or escalate DECISION_REQUIRED."
            )
        return False
    return True


def find_toolkit_root(start_dir=None):
    """Find toolkit root by walking up looking for schema/canonical/."""
    if start_dir is None:
        start_dir = os.path.dirname(os.path.abspath(__file__))
    
    current = start_dir
    while current != os.path.dirname(current):  # not at filesystem root
        canonical_dir = os.path.join(current, "schema", "canonical")
        if os.path.isdir(canonical_dir):
            return current
        current = os.path.dirname(current)
    
    raise FileNotFoundError(
        "Cannot locate toolkit root. "
        "Expected schema/canonical/ directory in some ancestor."
    )


if __name__ == "__main__":
    # CLI: python3 hash_lock.py [canonical_path]
    canonical_path = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        verify_canonical_lock(canonical_path)
        print(f"✅ Canonical schema hash verified: {CANONICAL_SCHEMA_HASH}")
        sys.exit(0)
    except CanonicalSchemaTampered as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(EXIT_CANONICAL_TAMPERED)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(4)
