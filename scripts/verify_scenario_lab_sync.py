#!/usr/bin/env python3
"""Verify the live Scenario Lab API serves exactly the repository's cases.

Compares sorted entity_id lists and per-module counts (a case with no
"module" property counts as kyc). Count-only agreement is not enough.
Polls the live endpoint until it matches or the deadline passes.
"""

import argparse
import json
import sys
import time
import urllib.request
from collections import Counter

LIVE_URL = "https://fincrimeradar-api.onrender.com/scenario-lab/cases"


def summarise(payload, label):
    """Return (sorted entity_id list, per-module Counter). Raises ValueError if malformed or any entity_id repeats."""
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"{label}: payload is not a non-empty JSON array")
    ids, modules = [], Counter()
    for i, case in enumerate(payload):
        if not isinstance(case, dict):
            raise ValueError(f"{label}: item {i} is not an object")
        eid = case.get("entity_id")
        if not isinstance(eid, str) or not eid:
            raise ValueError(f"{label}: item {i} has no string entity_id")
        module = case.get("module", "kyc")
        if not isinstance(module, str) or not module:
            raise ValueError(f"{label}: item {i} has an invalid module")
        ids.append(eid)
        modules[module] += 1
    dupes = sorted(i for i, n in Counter(ids).items() if n > 1)
    if dupes:
        raise ValueError(f"{label}: duplicate entity_id values: {dupes}")
    return sorted(ids), modules


def compare(expected_payload, actual_payload):
    """Return a list of mismatch descriptions, empty when identical. Raises ValueError if malformed."""
    exp_ids, exp_mod = summarise(expected_payload, "repository")
    act_ids, act_mod = summarise(actual_payload, "live")
    problems = []
    missing = sorted((Counter(exp_ids) - Counter(act_ids)).elements())
    extra = sorted((Counter(act_ids) - Counter(exp_ids)).elements())
    if missing:
        problems.append(f"missing IDs (in repository, not live): {missing}")
    if extra:
        problems.append(f"extra IDs (live, not in repository): {extra}")
    if len(exp_ids) != len(act_ids) or exp_mod != act_mod:
        problems.append(
            f"count mismatch: expected total {len(exp_ids)} {dict(sorted(exp_mod.items()))}, "
            f"actual total {len(act_ids)} {dict(sorted(act_mod.items()))}"
        )
    return problems


def fetch_live(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.load(resp)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-file", default="scenario-lab/data/cases.json")
    ap.add_argument("--url", default=LIVE_URL)
    ap.add_argument("--timeout", type=int, default=1500, help="total seconds to keep polling")
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--request-timeout", type=int, default=90, help="per request, covers cold start")
    args = ap.parse_args(argv)

    with open(args.repo_file, encoding="utf-8") as f:
        expected = json.load(f)

    deadline = time.monotonic() + args.timeout
    attempt, last = 0, []
    while True:
        attempt += 1
        try:
            last = compare(expected, fetch_live(args.url, args.request_timeout))
        except (OSError, ValueError) as e:  # URLError, HTTPError, timeout, JSONDecodeError are all subclasses
            last = [f"{type(e).__name__}: {e}"]
        if not last:
            print(f"Scenario Lab live API matches repository after {attempt} attempt(s).")
            return 0
        print(f"attempt {attempt}: not yet matching ({last[0][:200]})", flush=True)
        if time.monotonic() + args.interval > deadline:
            break
        time.sleep(args.interval)

    print(f"::error::Scenario Lab live API did not match the repository within {args.timeout}s")
    for p in last:
        print(f"  {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
