#!/usr/bin/env python3
"""Static contract for the KYB Lab page (kyb-lab.html, js/kyb-lab.js).

The page renders untrusted third party register text, so the script that
renders it must never write markup. This check fails if js/kyb-lab.js contains
any HTML-writing or code-evaluating sink, if the page loads a script outside
the allowlist or carries an ad slot, and if the KYB Lab nav link is missing
from any page whose primary nav links to Screen.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "js" / "kyb-lab.js"
PAGE = ROOT / "kyb-lab.html"
SITEMAP = ROOT / "sitemap.xml"

FORBIDDEN_SINKS = [
    "innerHTML",
    "outerHTML",
    "insertAdjacentHTML",
    "document.write",
    "eval(",
    "Function(",
    "DOMParser",
    "createContextualFragment",
    ".src =",
    ".src=",
    "setAttribute('on",
    'setAttribute("on',
    "setTimeout(\"",
    "setTimeout('",
    "srcdoc",
]
ALLOWED_SCRIPT_SRC = (
    "https://fundingchoicesmessages.google.com/",
    "https://www.googletagmanager.com/",
    "/js/kyb-lab.js",
    "/js/site-chrome.js",
    "/brand.js",
)
KYB_LINK = re.compile(r'<a href="/kyb-lab\.html"[^>]*>KYB Lab</a>')
DASHES = re.compile("[\u2013\u2014]")


def strip_js_comments(src: str) -> str:
    """Remove // and /* */ comments (whole line or trailing), leaving string contents alone."""
    out: list[str] = []
    i, n = 0, len(src)
    quote = ""
    while i < n:
        ch = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if quote:
            out.append(ch)
            if ch == chr(92) and i + 1 < n:
                out.append(nxt)
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "'\"`":
            quote = ch
            out.append(ch)
        elif ch == "/" and nxt == "/":
            while i < n and src[i] != chr(10):
                i += 1
            continue
        elif ch == "/" and nxt == "*":
            end = src.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def div_block(text: str, open_pattern: str) -> str | None:
    """The balanced <div> block that starts at the first match of open_pattern, or None."""
    m = re.search(open_pattern, text)
    if not m:
        return None
    depth = 0
    for tag in re.finditer(r"<div\b|</div>", text[m.start() :]):
        depth += 1 if tag.group(0) == "<div" else -1
        if depth == 0:
            return text[m.start() : m.start() + tag.end()]
    return None


def main() -> int:
    problems: list[str] = []

    js = JS.read_text(encoding="utf-8")
    code = strip_js_comments(js)
    for sink in FORBIDDEN_SINKS:
        if sink in code:
            problems.append(f"js/kyb-lab.js contains forbidden sink {sink!r}")
    if DASHES.search(js):
        problems.append("js/kyb-lab.js contains an em or en dash")
    if "https://fincrimeradar-api.onrender.com" not in js:
        problems.append("js/kyb-lab.js does not name the production API base")

    page = PAGE.read_text(encoding="utf-8")
    if DASHES.search(page):
        problems.append("kyb-lab.html contains an em or en dash")
    for src in re.findall(r"<script[^>]*\ssrc=\"([^\"]+)\"", page):
        if not src.startswith(ALLOWED_SCRIPT_SRC):
            problems.append(f"kyb-lab.html loads a script outside the allowlist: {src}")
    if re.search(r"adsbygoogle|pagead2|class=\"[^\"]*\bad[-_ ]?slot", page, re.I):
        problems.append("kyb-lab.html contains an ad script or ad slot")
    if 'rel="canonical" href="https://fincrimeradar.org/kyb-lab.html"' not in page:
        problems.append("kyb-lab.html canonical link missing or wrong")
    if "https://fincrimeradar.org/kyb-lab.html" not in SITEMAP.read_text(encoding="utf-8"):
        problems.append("sitemap.xml has no entry for kyb-lab.html")
    if not (ROOT / "kyb-lab-social-card.png").exists():
        problems.append("kyb-lab-social-card.png is missing")

    # Test responses are synthetic: reserved ZZ company numbers only, never live register data.
    for fixture in sorted((ROOT / "scripts" / "fixtures" / "kyb").glob("api_*.json")):
        numbers = re.findall(r'"company_number":\s*"([^"]*)"', fixture.read_text(encoding="utf-8"))
        for number in numbers:
            if not re.fullmatch(r"ZZ\d{6}", number):
                problems.append(f"{fixture.name}: company number {number!r} is not a reserved ZZ number")

    # Hand edit detection (cheap, needs no API repo): each committed fixture must match the
    # hash the generator recorded, taken over LF normalised bytes. This proves the fixtures
    # were not edited by hand; it does not prove they are current. For that run
    #   python scripts/generate_kyb_api_fixtures.py --check
    fixture_dir = ROOT / "scripts" / "fixtures" / "kyb"
    try:
        manifest = json.loads((fixture_dir / "MANIFEST.json").read_text(encoding="utf-8"))
        recorded = manifest["files"]
        nine = manifest["nine_does_not_establish"]
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"fixtures/kyb/MANIFEST.json is missing or unreadable: {exc!r}")
        recorded, nine = {}, {}
    on_disk = {f.name for f in fixture_dir.glob("api_*.json")}
    if on_disk != set(recorded):
        problems.append(f"fixtures differ from the manifest: {sorted(on_disk ^ set(recorded))}")
    for name, digest in recorded.items():
        path = fixture_dir / name
        if path.exists() and hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != digest:
            problems.append(f"{name} does not match the generator manifest, regenerate it instead of editing it")
    if len(nine) != 9:
        problems.append("the manifest does not carry the nine indicator strings")

    # Every page with a static desktop nav must carry KYB Lab in BOTH the desktop and the mobile nav.
    # Pages that take their nav from partials/nav.html at runtime (#site-nav) have no static nav
    # and are covered through the partial, which is itself checked here.
    pages = 0
    tracked = subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for rel in tracked:
        text = (ROOT / rel).read_text(encoding="utf-8")
        desktop = div_block(text, r'<div class="nav-links"')
        if desktop is None:
            continue
        pages += 1
        mobile = div_block(text, r'<div class="mobile-nav"')
        if not KYB_LINK.search(desktop):
            problems.append(f"{rel}: the desktop nav has no KYB Lab link")
        if mobile is None:
            problems.append(f"{rel}: has a desktop nav but no mobile nav block")
        elif not KYB_LINK.search(mobile):
            problems.append(f"{rel}: the mobile nav has no KYB Lab link")

    if problems:
        print("FAIL: KYB Lab static checks")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: KYB Lab static checks, {pages} pages with a static desktop nav carry KYB Lab in desktop and mobile navs, no forbidden sinks, scripts allowlisted, no ad slots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
