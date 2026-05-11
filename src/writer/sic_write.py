"""
sic_write.py — CMP-04 Writer

Produces SIC-JS v2.0 state objects in canonical or toolkit mode.

Auto-derive rules (toolkit mode only, when --upstream-type not given):
- upstream null/missing → upstream_type=none
- upstream matches [a-f0-9]{16} → upstream_type=cryptographic  
- upstream non-empty non-hex → upstream_type=file (with safety checks)

Self-validation: writer output is automatically piped to validator.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

EXIT_PASS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_INVALID_USAGE = 2
EXIT_UNSAFE_UPSTREAM = 5

CRYPTO_HEX_PATTERN = re.compile(r'^[a-f0-9]{16}$')


def auto_derive_upstream_type(upstream):
    """Auto-derive upstream_type from upstream value."""
    if upstream is None or upstream == '' or upstream == 'null':
        return 'none', None
    if CRYPTO_HEX_PATTERN.match(upstream):
        return 'cryptographic', upstream
    # Else file
    return 'file', upstream


def check_unsafe_upstream(upstream):
    """Raise if upstream value is unsafe."""
    if not isinstance(upstream, str):
        return
    if '..' in upstream:
        raise ValueError(f"UNSAFE_UPSTREAM: path traversal: {upstream!r}")
    if upstream.startswith('/') or upstream.startswith('\\'):
        raise ValueError(f"UNSAFE_UPSTREAM: absolute path: {upstream!r}")
    if '\x00' in upstream:
        raise ValueError("UNSAFE_UPSTREAM: null bytes")
    if len(upstream) > 256:
        raise ValueError(f"UNSAFE_UPSTREAM: too long ({len(upstream)})")


def build_record(args):
    """Build SIC-JS record from args."""
    # Process upstream
    upstream = args.upstream
    if upstream == 'null':
        upstream = None
    
    # Determine mode
    mode = args.mode if args.mode else 'canonical'
    
    # Validate canonical mode constraint
    if mode == 'canonical' and args.upstream_type is not None:
        raise ValueError(
            "INVALID_USAGE: --upstream-type is not allowed in canonical mode. "
            "Use --mode toolkit to use upstream_type."
        )
    
    # Build record
    record = {
        "sic_version": "2.0",
        "round": args.round,
        "entity": {
            "name": args.entity_name,
            "model": args.entity_model
        },
        "state": {
            "context": args.context,
            "current_action": args.current_action
        },
        "relation": {
            "user": args.user
        },
        "event": None,
        "intent": None
    }
    
    # Add upstream based on mode
    if mode == 'canonical':
        if upstream is not None:
            if not CRYPTO_HEX_PATTERN.match(upstream):
                raise ValueError(
                    f"canonical mode: upstream must be 16 lowercase hex or null, got {upstream!r}"
                )
            record['relation']['upstream'] = upstream
    else:
        # Toolkit mode
        if args.upstream_type:
            ut = args.upstream_type
            # Validate consistency
            if ut == 'none':
                if upstream is not None:
                    raise ValueError(
                        f"upstream_type=none requires upstream=null, got {upstream!r}"
                    )
            elif ut == 'cryptographic':
                if upstream is None or not CRYPTO_HEX_PATTERN.match(upstream):
                    raise ValueError(
                        f"upstream_type=cryptographic requires 16 hex, got {upstream!r}"
                    )
            elif ut == 'file':
                if upstream is None:
                    raise ValueError("upstream_type=file requires upstream value")
                if CRYPTO_HEX_PATTERN.match(upstream):
                    raise ValueError(
                        "upstream_type=file but upstream looks like crypto hash"
                    )
                check_unsafe_upstream(upstream)
        else:
            # Auto-derive
            ut, upstream = auto_derive_upstream_type(upstream)
            if ut == 'file':
                check_unsafe_upstream(upstream)
            print(f"[WRITER] auto-derived upstream_type={ut} (writer convenience behavior, not protocol rule)",
                  file=sys.stderr)
        
        record['relation']['upstream_type'] = ut
        record['relation']['upstream'] = upstream
    
    return record, mode


def self_validate_record(record, mode, output_path=None):
    """Validate writer output even when the final destination is stdout."""
    validator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'validator', 'validate_skeleton_v2.py'
    )
    temp_path = None
    validation_path = output_path
    try:
        if validation_path is None:
            with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as tmp:
                json.dump(record, tmp, indent=2, ensure_ascii=False)
                temp_path = tmp.name
                validation_path = temp_path
        result = subprocess.run(
            ['python3', validator_path, '--file', validation_path, '--mode', mode],
            capture_output=True
        )
        if result.returncode != 0:
            print("❌ Writer output failed self-validation:", file=sys.stderr)
            stderr = result.stderr.decode().strip()
            stdout = result.stdout.decode().strip()
            if stderr:
                print(stderr, file=sys.stderr)
            if stdout:
                print(stdout, file=sys.stderr)
            sys.exit(result.returncode)
        target = output_path if output_path else 'stdout'
        print(f"✅ Self-validated [mode={mode}]: {target}", file=sys.stderr)
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(description='SIC-JS v2.0 Writer (CMP-04)')
    parser.add_argument('--entity-name', required=True)
    parser.add_argument('--entity-model', required=True)
    parser.add_argument('--context', required=True)
    parser.add_argument('--current-action', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--round', type=int, default=1)
    parser.add_argument('--upstream', default=None,
                        help="upstream value or 'null' for null")
    parser.add_argument('--upstream-type', choices=['none', 'cryptographic', 'file'])
    parser.add_argument('--mode', choices=['canonical', 'toolkit'])
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--no-self-validate', action='store_true',
                        help='Skip self-validation (NOT recommended)')
    
    args = parser.parse_args()
    
    try:
        record, mode = build_record(args)
    except ValueError as e:
        msg = str(e)
        if "UNSAFE" in msg:
            print(f"❌ {msg}", file=sys.stderr)
            sys.exit(EXIT_UNSAFE_UPSTREAM)
        elif "INVALID_USAGE" in msg:
            print(f"❌ {msg}", file=sys.stderr)
            sys.exit(EXIT_INVALID_USAGE)
        else:
            print(f"❌ {msg}", file=sys.stderr)
            sys.exit(EXIT_VALIDATION_FAILED)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        output_path = args.output
    else:
        output_path = None
    
    # Self-validate
    if not args.no_self_validate:
        self_validate_record(record, mode, output_path)

    if not args.output:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    
    sys.exit(EXIT_PASS)


if __name__ == '__main__':
    main()
