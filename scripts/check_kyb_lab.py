#!/usr/bin/env python3
"""Static contract for the KYB Lab page (kyb-lab.html, js/kyb-lab.js).

The page renders untrusted third party register text, so the script that
renders it must never write markup. This check fails if js/kyb-lab.js contains
any HTML-writing or code-evaluating sink, if the page loads a script outside
the allowlist or carries an ad slot, and if the KYB Lab nav link is missing
from any page whose primary nav links to Screen.
"""

from __future__ import annotations

import re
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
    "new Function",
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
SCREEN_LINK = re.compile(r'<a href="/screen\.html"(?: class="hm")?>Screen</a>')
KYB_LINK = re.compile(r'<a href="/kyb-lab\.html"[^>]*>KYB Lab</a>')
DASHES = re.compile("[–—]")


def strip_js_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


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

    pages = 0
    for path in sorted(ROOT.glob("*.html")) + [ROOT / "partials" / "nav.html"]:
        text = path.read_text(encoding="utf-8")
        if path.name == "partials/footer.html":
            continue
        # Primary nav only: a Screen link in a nav-links or mobile-nav block.
        for m in SCREEN_LINK.finditer(text):
            window = text[max(0, m.start() - 600) : m.end() + 400]
            if "nav-links" not in window and "mobile-nav" not in window and "<nav" not in window:
                continue  # footer link, not the primary nav
            pages += 1
            if not KYB_LINK.search(window):
                problems.append(f"{path.name}: nav links to Screen but not to KYB Lab")

    if problems:
        print("FAIL: KYB Lab static checks")
        for p in problems:
            print("  -", p)
        return 1
    print(f"OK: KYB Lab static checks, {pages} navs link Screen and KYB Lab, no forbidden sinks, scripts allowlisted, no ad slots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
