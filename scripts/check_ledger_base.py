#!/usr/bin/env python3
"""Guard against the stale-base ledger write-back bug (BACKLOG.md, third
occurrence, root cause 2026-08-23): a WIP built from a cached read of
verification-ledger.json silently drops whatever claimIds sat at the tail
of the array at snapshot time when it's later written back over the file.

Compares the working tree's claimId set against HEAD's. Fails loud if any
claimId committed in HEAD is missing from the working tree.

Usage:
    python scripts/check_ledger_base.py

Run this before starting, and before committing, any session that touches
verification-ledger.json.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "verification-ledger.json"


def claim_ids(entries):
    return {e["claimId"] for e in entries if isinstance(e, dict) and "claimId" in e}


def load_head_ledger():
    result = subprocess.run(
        ["git", "show", "HEAD:verification-ledger.json"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"ERROR: could not read verification-ledger.json from HEAD: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def main():
    if not LEDGER_PATH.exists():
        print(f"ERROR: {LEDGER_PATH} not found in working tree.", file=sys.stderr)
        sys.exit(1)

    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        working_entries = json.load(f)

    head_ids = claim_ids(load_head_ledger())
    working_ids = claim_ids(working_entries)

    missing = sorted(head_ids - working_ids)
    if missing:
        print(f"FAIL: {len(missing)} claimId(s) in HEAD are missing from the working tree.", file=sys.stderr)
        print("This is the stale-base write-back signature (BACKLOG.md, ledger section): a WIP", file=sys.stderr)
        print("built from a cached snapshot dropped these when written back. Refresh the WIP", file=sys.stderr)
        print("against live HEAD before continuing, don't add to a stale copy.", file=sys.stderr)
        for claim_id in missing:
            print(f"  - {claim_id}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: all {len(head_ids)} HEAD claimIds present in working tree ({len(working_ids)} total).")
    sys.exit(0)


if __name__ == "__main__":
    main()
