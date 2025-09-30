#!/usr/bin/env python3
# envsubst-windows-linux — CLI
# Zero-deps, cross-platform ${VAR}/{{VAR}} substitution with .env support.

import argparse
import os
import sys
from pathlib import Path

from core import (
    load_env_file,
    collect_files,
    substitute_text,
    list_missing_vars,
    make_preview_diff,
)

def parse_args():
    p = argparse.ArgumentParser(
        description="Substitute ${VAR} / {{VAR}} from env/.env into files."
    )
    p.add_argument("paths", nargs="+", help="Files or directories (globs allowed).")
    p.add_argument("--env", dest="env_path", default=None,
                   help="Path to .env (optional).")
    p.add_argument("--in-place", action="store_true",
                   help="Write changes back to the same files.")
    p.add_argument("--out", dest="out_dir", default=None,
                   help="Write outputs to this directory (mirrors structure).")
    p.add_argument("--safe", action="store_true",
                   help="Leave unknown placeholders untouched (no error).")
    p.add_argument("--check", action="store_true",
                   help="Only check for missing variables; exit 1 if any.")
    p.add_argument("--dry-run", action="store_true",
                   help="Do not write; print a simple diff-like preview.")
    p.add_argument("--encoding", default="utf-8",
                   help="File encoding (default: utf-8).")
    return p.parse_args()

def main():
    args = parse_args()

    if args.in_place and args.out_dir:
        print("ERROR: Use either --in-place or --out, not both.", file=sys.stderr)
        return 2

    # Build variable map: environment first, then override by .env if provided.
    env_map = dict(os.environ)
    if args.env_path:
        env_map.update(load_env_file(args.env_path))

    files = collect_files(args.paths)
    if not files:
        print("No files matched.", file=sys.stderr)
        return 1

    # Pre-check: aggregate all missing variables across inputs
    missing_global = set()
    for f in files:
        try:
            text = Path(f).read_text(encoding=args.encoding)
        except Exception as e:
            print(f"WARN: Could not read {f}: {e}", file=sys.stderr)
            continue
        missing_global.update(list_missing_vars(text, env_map))

    if args.check:
        if missing_global:
            print("Missing variables detected:")
            for k in sorted(missing_global):
                print(f" - {k}")
            return 1
        print("All variables present.")
        return 0

    if missing_global and not (args.safe or args.dry_run):
        print("Missing variables detected (use --check first or --safe to ignore):", file=sys.stderr)
        for k in sorted(missing_global):
            print(f" - {k}", file=sys.stderr)
        return 1

    exit_code = 0
    for f in files:
        try:
            text = Path(f).read_text(encoding=args.encoding)
            rendered = substitute_text(text, env_map, safe=args.safe)
        except Exception as e:
            print(f"ERROR: {f}: {e}", file=sys.stderr)
            exit_code = exit_code or 1
            continue

        if args.dry_run:
            preview = make_preview_diff(text, rendered, str(f))
            sys.stdout.write(preview + ("\n" if not preview.endswith("\n") else ""))
            continue

        if args.in_place:
            try:
                Path(f).write_text(rendered, encoding=args.encoding)
                print(f"Wrote {f}")
            except Exception as e:
                print(f"ERROR: Could not write {f}: {e}", file=sys.stderr)
                exit_code = exit_code or 1
        elif args.out_dir:
            out_base = Path(args.out_dir)
            # keep relative structure when possible
            rel = Path(f).resolve().relative_to(Path().resolve())
            out_path = out_base / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                out_path.write_text(rendered, encoding=args.encoding)
                print(f"Wrote {out_path}")
            except Exception as e:
                print(f"ERROR: Could not write {out_path}: {e}", file=sys.stderr)
                exit_code = exit_code or 1
        else:
            print(f"--- {f} ---")
            sys.stdout.write(rendered)
            if not rendered.endswith("\n"):
                print()

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
