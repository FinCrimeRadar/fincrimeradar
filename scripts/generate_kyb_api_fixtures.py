#!/usr/bin/env python3
"""Regenerate the KYB Lab browser-test responses from the API itself.

Runs the real fincrimeradar-api KYB routes (routes_kyb_lab.py) against the API
repository's synthetic fixtures (tests/fixtures/kyb, reserved ZZ company
numbers, no live register data) with the upstream faked, and saves the JSON the
API really returns, so the frontend tests never depend on hand-built shapes.

    python scripts/generate_kyb_api_fixtures.py --api-repo ../fincrimeradar-api

Run it with the API repository's Python environment (it needs fastapi, pydantic,
requests and pytest). Output: scripts/fixtures/kyb/api_*.json plus MANIFEST.json
(the API commit it ran against, the nine indicator strings as the API's own tests
fix them, and a SHA-256 for every fixture). Re-run it when the API response shape
changes, and commit the result.

    python scripts/generate_kyb_api_fixtures.py --check

regenerates into a temporary directory and fails if the committed fixtures differ
from what the API produces now (freshness check). scripts/check_kyb_lab.py runs a
cheaper check that needs no API repository: it verifies the manifest hashes, which
catches a hand edited fixture.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "fixtures" / "kyb"


def lf_sha256(path: Path) -> str:
    """SHA-256 of the file with CRLF folded to LF, so the hash is the same on every checkout."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-repo", default=str(HERE.parents[1] / "fincrimeradar-api"))
    ap.add_argument("--check", action="store_true", help="regenerate to a temp dir and compare with the committed fixtures")
    args = ap.parse_args()
    out_dir = Path(tempfile.mkdtemp(prefix="kyb-fixtures-")) if args.check else OUT
    api = Path(args.api_repo).resolve()
    sys.path.insert(0, str(api))
    sys.path.insert(0, str(api / "tests"))

    import test_kyb_lab as t  # the API repo's own test helpers and fixtures
    import routes_kyb_lab as kyb
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(kyb.router)
    client = TestClient(app)

    def setup(routes):
        kyb.reset_state_for_tests()
        kyb.COMPANIES_HOUSE_API_KEY = t.TEST_KEY
        kyb._utcnow = lambda: t.NOW
        kyb.time.sleep = lambda s: None
        kyb._http_get = t.Upstream(routes)

    def get(number, headers=None):
        return client.get(f"/api/kyb/company/{number}", headers=headers or {})

    def save(name, response):
        out_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "status": response.status_code,
            "headers": {k: v for k, v in response.headers.items() if k.lower() == "retry-after"},
            "body": response.json(),
        }
        (out_dir / f"api_{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8", newline=chr(10)
        )
        print(f"api_{name}.json: HTTP {response.status_code}")

    # 1. Hand-authored upstream set from the API's own fixtures (all sections present).
    setup(t.default_routes())
    save("default", get(t.NUM))

    # 2. The three synthetic bundles, replayed exactly as the API tests replay them.
    for label in t.SYNTHETIC:
        number, routes = t.synthetic_routes(t.synthetic_bundle(label))
        setup(routes)
        save(label, get(number))

    # 3. Every sub-resource 404: the register did not return any section.
    number, routes = t.synthetic_routes(t.synthetic_bundle("active_ltd_outstanding_charges"))
    only_profile = {p: v for p, v in routes.items() if p == f"/company/{number}"}
    setup(only_profile)
    save("not_returned", get(number))

    # 4. Unsupported entity type.
    routes = t.default_routes()
    profile = t.fixture("profile_active_ltd")
    profile["type"] = "registered-society-non-jurisdictional"
    routes[t.PATHS["profile"]] = profile
    setup(routes)
    save("unsupported", get(t.NUM))

    # 5. Many officers: feed the API 45 officers and a total of 60 so it truncates.
    routes = t.default_routes()
    officers = t.fixture("officers")
    base = officers["items"]
    many = []
    for i in range(45):
        item = copy.deepcopy(base[i % len(base)])
        item["name"] = f"SYNTHETIC OFFICER {i:02d}"
        many.append(item)
    officers["items"] = many
    officers["total_results"] = 60
    routes[t.PATHS["officers"]] = officers
    setup(routes)
    save("many_officers", get(t.NUM))

    # 5b. All nine indicators at once, built exactly as the API's own nine string test builds it.
    profile = t.fixture("profile_active_ltd")
    profile["accounts"]["next_accounts"]["overdue"] = True
    profile["confirmation_statement"]["overdue"] = True
    profile["previous_company_names"] = [
        {"name": "OLD NAME LIMITED", "effective_from": "2019-01-01", "ceased_on": "2020-01-01"}
    ]
    officers = t.officers_with(*t.overdue_officers()["items"], *t.removed_officers()["items"])
    routes = t.default_routes(officers=officers)
    routes[t.PATHS["profile"]] = profile
    setup(routes)
    save("all_nine_indicators", get(t.NUM))

    # 6. Error responses as the API really sends them.
    setup(t.default_routes())
    save("error_422", get("not%20valid"))
    setup({})
    save("error_404", get(t.NUM))
    kyb.COMPANIES_HOUSE_API_KEY = ""
    save("error_503", get(t.NUM))
    kyb.COMPANIES_HOUSE_API_KEY = t.TEST_KEY
    setup(t.default_routes())
    last = None
    for _ in range(12):
        last = get(t.NUM)
        if last.status_code == 429:
            break
    save("error_429", last)
    kyb.reset_state_for_tests()

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=api, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=api, capture_output=True, text=True)
    commit = head.stdout.strip()
    if head.returncode != 0 or not commit or dirty.returncode != 0 or dirty.stdout.strip():
        print("ERROR: the API repository must be a git checkout with no uncommitted changes, so the manifest records a real commit")
        return 2
    manifest = {
        "api_repo_commit": commit,
        "nine_does_not_establish": t.NINE_DOES_NOT_ESTABLISH,
        "files": {f.name: lf_sha256(f) for f in sorted(out_dir.glob("api_*.json"))},
    }
    (out_dir / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8", newline=chr(10)
    )

    if args.check:
        def norm(path: Path) -> bytes:
            return path.read_bytes().replace(b"\r\n", b"\n")

        generated = {f.name for f in out_dir.glob("api_*.json")}
        committed = {f.name for f in OUT.glob("api_*.json")}
        stale = sorted(n for n in generated & committed if norm(out_dir / n) != norm(OUT / n))
        stale += [f"{n} (not generated any more)" for n in sorted(committed - generated)]
        stale += [f"{n} (not committed)" for n in sorted(generated - committed)]
        old = json.loads((OUT / "MANIFEST.json").read_text(encoding="utf-8"))
        if old["nine_does_not_establish"] != manifest["nine_does_not_establish"]:
            stale.append("the nine indicator strings")
        if stale:
            print("STALE fixtures (regenerate with this script and commit):", ", ".join(stale))
            return 1
        moved = "" if old["api_repo_commit"] == commit else f" (API commit moved from {old['api_repo_commit'][:7]} to {commit[:7]}, no response change)"
        print("OK: committed fixtures match what the API produces now" + moved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
