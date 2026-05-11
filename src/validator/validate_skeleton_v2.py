"""
validate_skeleton_v2.py — CMP-03 Validator

Validates SIC-JS v2.0 state objects in two modes:
- canonical: strict v2.0 (no upstream_type allowed)
- toolkit: project-local fork (upstream_type required)

Implements two layers of validation:
1. Schema-level (jsonschema): structure, types, enums, additionalProperties
2. Logic-level (this code): upstream/upstream_type consistency, safety
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

import jsonschema

# Add src/utils to path for hash_lock import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utils'))
from hash_lock import (
    verify_canonical_lock, find_toolkit_root,
    CanonicalSchemaTampered, EXIT_CANONICAL_TAMPERED
)

# Exit codes
EXIT_PASS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_INVALID_USAGE = 2
EXIT_INPUT_NOT_FOUND = 3
EXIT_SCHEMA_NOT_FOUND = 4
EXIT_UNSAFE_UPSTREAM = 5
EXIT_LEGACY_FORMAT = 6
EXIT_INTERNAL = 7
# 9 = EXIT_CANONICAL_TAMPERED (from hash_lock)

CRYPTO_HEX_PATTERN = re.compile(r'^[a-f0-9]{16}$')


class ValidationError(Exception):
    def __init__(self, exit_code, message):
        self.exit_code = exit_code
        super().__init__(message)


def validate_iso8601(value, field_name):
    """Reject invalid ISO8601-like timestamps without optional jsonschema extras."""
    if value is None:
        return
    if not isinstance(value, str) or 'T' not in value:
        raise ValidationError(
            EXIT_VALIDATION_FAILED,
            f"{field_name} must be ISO8601 date-time string, got {value!r}"
        )
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError(
            EXIT_VALIDATION_FAILED,
            f"{field_name} must be ISO8601 date-time string, got {value!r}"
        )


def validate_logic(record, mode):
    """
    Logic-level validation for upstream/upstream_type consistency.
    Schema does NOT enforce this — must be done in code.
    """
    rel = record.get('relation', {})
    upstream = rel.get('upstream')

    entity = record.get('entity', {})
    validate_iso8601(entity.get('created_at'), 'entity.created_at')
    event = record.get('event')
    if isinstance(event, dict):
        validate_iso8601(event.get('timestamp'), 'event.timestamp')
    
    if mode == 'canonical':
        # Canonical mode: upstream must match strict 16-hex pattern OR be null
        if upstream is not None:
            if not CRYPTO_HEX_PATTERN.match(upstream):
                raise ValidationError(
                    EXIT_VALIDATION_FAILED,
                    f"canonical mode: upstream must be 16 lowercase hex or null, got {upstream!r}"
                )
        # Canonical mode: upstream_type MUST NOT exist
        if 'upstream_type' in rel:
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                "canonical mode: upstream_type field is project-local extension, not allowed in canonical SIC-JS"
            )
        return
    
    # Toolkit mode validation
    if 'upstream_type' not in rel:
        raise ValidationError(
            EXIT_LEGACY_FORMAT,
            "LEGACY_FORMAT_DETECTED: toolkit mode requires upstream_type field. "
            "This SIC-JS was produced before upstream_type was required. "
            "See docs/migration/ for migration guide."
        )
    
    ut = rel['upstream_type']
    
    if ut == 'none':
        if upstream is not None:
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                f"upstream_type=none requires upstream=null, got {upstream!r}"
            )
        return
    
    if ut == 'cryptographic':
        if upstream is None:
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                "upstream_type=cryptographic requires upstream value (cannot be null)"
            )
        if not CRYPTO_HEX_PATTERN.match(upstream):
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                f"upstream_type=cryptographic requires 16 lowercase hex, got {upstream!r}"
            )
        return
    
    if ut == 'file':
        if upstream is None:
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                "upstream_type=file requires upstream value (cannot be null)"
            )
        if CRYPTO_HEX_PATTERN.match(upstream):
            raise ValidationError(
                EXIT_VALIDATION_FAILED,
                "upstream_type=file but upstream looks like cryptographic hash (16 hex). "
                "Use upstream_type=cryptographic instead."
            )
        # Safety checks
        if '..' in upstream:
            raise ValidationError(
                EXIT_UNSAFE_UPSTREAM,
                f"UNSAFE_UPSTREAM: path traversal not allowed: {upstream!r}"
            )
        if upstream.startswith('/'):
            raise ValidationError(
                EXIT_UNSAFE_UPSTREAM,
                f"UNSAFE_UPSTREAM: absolute path not allowed: {upstream!r}"
            )
        if '\\' in upstream:
            raise ValidationError(
                EXIT_UNSAFE_UPSTREAM,
                f"UNSAFE_UPSTREAM: backslash not allowed: {upstream!r}"
            )
        if '\x00' in upstream:
            raise ValidationError(
                EXIT_UNSAFE_UPSTREAM,
                f"UNSAFE_UPSTREAM: null bytes not allowed"
            )
        if len(upstream) > 256:
            raise ValidationError(
                EXIT_UNSAFE_UPSTREAM,
                f"UNSAFE_UPSTREAM: label too long (max 256, got {len(upstream)})"
            )


def validate_record(record, mode, toolkit_root):
    """Run schema validation + logic validation."""
    # Choose schema
    if mode == 'canonical':
        schema_path = os.path.join(toolkit_root, 'schema/canonical/sic-js-schema-v2.0.json')
    elif mode == 'toolkit':
        schema_path = os.path.join(toolkit_root, 'schema/toolkit/sic-js-schema-v2.0-toolkit.json')
    else:
        raise ValidationError(EXIT_INVALID_USAGE, f"Unknown mode: {mode}")
    
    if not os.path.exists(schema_path):
        raise ValidationError(EXIT_SCHEMA_NOT_FOUND, f"Schema not found: {schema_path}")
    
    with open(schema_path) as f:
        schema = json.load(f)
    
    # Schema-level validation
    try:
        jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as e:
        # Check if it's a missing upstream_type (legacy)
        if mode == 'toolkit' and 'upstream_type' in str(e.message):
            raise ValidationError(
                EXIT_LEGACY_FORMAT,
                f"LEGACY_FORMAT_DETECTED: {e.message}"
            )
        raise ValidationError(EXIT_VALIDATION_FAILED, f"Schema validation failed: {e.message}")
    
    # Logic-level validation
    validate_logic(record, mode)


def main():
    parser = argparse.ArgumentParser(description='SIC-JS v2.0 Validator (CMP-03)')
    parser.add_argument('--file', required=True, help='Path to SIC-JS JSON file to validate')
    parser.add_argument('--mode', choices=['canonical', 'toolkit'], help='Validation mode')
    parser.add_argument('--toolkit-mode', action='store_true',
                        help='Shorthand for --mode toolkit (mutually exclusive with --mode)')
    parser.add_argument('--level', choices=['1', '2', '3'], default='3', help='Validation level')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')
    
    args = parser.parse_args()
    
    # Mode conflict resolution: --mode and --toolkit-mode together = INVALID_USAGE
    if args.toolkit_mode and args.mode is not None:
        msg = "INVALID_USAGE: --mode and --toolkit-mode are mutually exclusive"
        if args.json:
            print(json.dumps({"status": "INVALID_USAGE", "message": msg}))
        else:
            print(msg, file=sys.stderr)
        sys.exit(EXIT_INVALID_USAGE)
    
    # Determine final mode
    if args.toolkit_mode:
        mode = 'toolkit'
    elif args.mode:
        mode = args.mode
    else:
        mode = 'canonical'  # Default
    
    # Find toolkit root (locates canonical schema for hash check)
    try:
        toolkit_root = find_toolkit_root(os.path.dirname(os.path.abspath(args.file)))
    except FileNotFoundError:
        # Fall back to assuming toolkit root is parent of script dir
        toolkit_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Hash lock check (canonical schema integrity)
    try:
        verify_canonical_lock(os.path.join(toolkit_root, 'schema/canonical/sic-js-schema-v2.0.json'))
    except CanonicalSchemaTampered as e:
        if args.json:
            print(json.dumps({"status": "CANONICAL_TAMPERED", "message": str(e)}))
        else:
            print(f"❌ {e}", file=sys.stderr)
        sys.exit(EXIT_CANONICAL_TAMPERED)
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"status": "SCHEMA_NOT_FOUND", "message": str(e)}))
        else:
            print(f"❌ {e}", file=sys.stderr)
        sys.exit(EXIT_SCHEMA_NOT_FOUND)
    
    # Load input
    if not os.path.exists(args.file):
        msg = f"Input file not found: {args.file}"
        if args.json:
            print(json.dumps({"status": "INPUT_NOT_FOUND", "message": msg}))
        else:
            print(f"❌ {msg}", file=sys.stderr)
        sys.exit(EXIT_INPUT_NOT_FOUND)
    
    try:
        with open(args.file) as f:
            record = json.load(f)
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON: {e}"
        if args.json:
            print(json.dumps({"status": "VALIDATION_FAILED", "message": msg}))
        else:
            print(f"❌ {msg}", file=sys.stderr)
        sys.exit(EXIT_VALIDATION_FAILED)
    
    # Validate
    try:
        validate_record(record, mode, toolkit_root)
        if args.json:
            print(json.dumps({"status": "PASS", "mode": mode, "file": args.file}))
        else:
            print(f"✅ PASS [mode={mode}] {args.file}")
        sys.exit(EXIT_PASS)
    except ValidationError as e:
        if args.json:
            status_map = {
                EXIT_VALIDATION_FAILED: "VALIDATION_FAILED",
                EXIT_LEGACY_FORMAT: "LEGACY_FORMAT_DETECTED",
                EXIT_UNSAFE_UPSTREAM: "UNSAFE_UPSTREAM",
                EXIT_SCHEMA_NOT_FOUND: "SCHEMA_NOT_FOUND",
            }
            print(json.dumps({
                "status": status_map.get(e.exit_code, "ERROR"),
                "exit_code": e.exit_code,
                "message": str(e),
                "mode": mode,
                "file": args.file
            }))
        else:
            print(f"❌ FAIL [mode={mode}] [exit={e.exit_code}] {e}", file=sys.stderr)
        sys.exit(e.exit_code)
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "INTERNAL_ERROR", "message": str(e)}))
        else:
            print(f"❌ Internal error: {e}", file=sys.stderr)
        sys.exit(EXIT_INTERNAL)


if __name__ == '__main__':
    main()
