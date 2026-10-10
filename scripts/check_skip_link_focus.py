#!/usr/bin/env python3
"""Static contract: on every tracked page with a #main-content skip link, the
skip link is the first focusable element in <body> and its target carries
tabindex="-1"."""

from __future__ import annotations

import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOID = {"meta", "link", "br", "img", "input", "hr", "source", "area", "base", "col", "embed", "wbr"}


class Scan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.skip_depth = 0  # inside noscript/template/script/style
        self.first = None
        self.skip_link = False
        self.target = None  # attrs of #main-content

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.in_body = True
        if a.get("id") == "main-content":
            self.target = a
        if tag in ("noscript", "template", "script", "style"):
            self.skip_depth += 1
            return
        if not self.in_body or self.skip_depth or self.first is not None:
            return
        ti = a.get("tabindex")
        focusable = (
            (tag == "a" and "href" in a)
            or tag in ("button", "select", "textarea", "summary")
            or (tag == "input" and a.get("type") != "hidden")
            or (ti is not None and ti.lstrip("-").isdigit() and int(ti) >= 0)
        ) and "disabled" not in a and ti != "-1"
        if focusable:
            self.first = (tag, a)

    def handle_endtag(self, tag):
        if tag in ("noscript", "template", "script", "style") and self.skip_depth:
            self.skip_depth -= 1


def main() -> int:
    files = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True).split()
    errors, checked = [], 0
    for f in files:
        html = (ROOT / f).read_text(encoding="utf-8")
        if 'href="#main-content"' not in html:
            continue
        s = Scan()
        s.feed(html)
        checked += 1
        if not s.first or s.first[1].get("href") != "#main-content":
            errors.append(f"{f}: first focusable in body is {s.first[0] + ' ' + str(s.first[1].get('href') or s.first[1].get('class')) if s.first else 'none'}, not the skip link")
        if s.target is None:
            errors.append(f"{f}: no #main-content target")
        elif s.target.get("tabindex") != "-1":
            errors.append(f"{f}: #main-content lacks tabindex=\"-1\"")
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    print(f"OK: {checked} skip-link pages, skip link first in tab order, targets carry tabindex=-1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
