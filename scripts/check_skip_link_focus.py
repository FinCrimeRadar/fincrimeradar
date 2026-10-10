#!/usr/bin/env python3
"""Static contract: on every tracked page with a #main-content skip link, the
skip link is the first focusable element in <body> and its target carries
tabindex="-1"."""

from __future__ import annotations

import re
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
        self.skip_link = None  # attrs of the #main-content skip link
        self.css = []
        self._style = False
        self.target = None  # attrs of #main-content

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "style":
            self._style = True
        if tag == "a" and a.get("href") == "#main-content" and self.skip_link is None:
            self.skip_link = a
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

    def handle_data(self, data):
        if self._style:
            self.css.append(data)

    def handle_endtag(self, tag):
        if tag == "style":
            self._style = False
        if tag in ("noscript", "template", "script", "style") and self.skip_depth:
            self.skip_depth -= 1


POSITIONING = re.compile(r"(?:^|;)\s*(?:position|left|right|top|bottom|clip|transform)\s*:", re.I)


def has_focus_rule(css: str, classes: list[str]) -> bool:
    """True if some selector targets one of the skip link classes with :focus."""
    return any(re.search(r"\." + re.escape(c) + r"\s*:focus(?:-visible)?", css) for c in classes)


def main() -> int:
    brand = (ROOT / "brand.css").read_text(encoding="utf-8") if (ROOT / "brand.css").exists() else ""
    files = subprocess.check_output(["git", "ls-files", "*.html"], cwd=ROOT, text=True).split()
    errors, checked = [], 0
    for f in files:
        html = (ROOT / f).read_text(encoding="utf-8")
        if 'href="#main-content"' not in html:
            continue
        s = Scan()
        s.feed(html)
        s.close()
        checked += 1
        if not s.first or s.first[1].get("href") != "#main-content":
            errors.append(f"{f}: first focusable in body is {s.first[0] + ' ' + str(s.first[1].get('href') or s.first[1].get('class')) if s.first else 'none'}, not the skip link")
        classes = (s.skip_link or {}).get("class", "").split()
        if POSITIONING.search((s.skip_link or {}).get("style", "")):
            errors.append(f"{f}: skip link carries an inline positioning style")
        css = "\n".join(s.css) + (brand if "brand.css" in html else "")
        if not has_focus_rule(css, classes):
            errors.append(f"{f}: no :focus rule for skip link class {classes}")
        if s.target is None:
            errors.append(f"{f}: no #main-content target")
        elif s.target.get("tabindex") != "-1":
            errors.append(f"{f}: #main-content lacks tabindex=\"-1\"")
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    print(f"OK: {checked} skip-link pages, skip link first in tab order, no inline positioning, :focus rule present, targets carry tabindex=-1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
