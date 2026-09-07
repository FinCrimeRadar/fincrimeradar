#!/usr/bin/env python3
"""
Recomputes the sitewide guide word count shown on about.html's
"Words of free content" stat, using the same guide list knowledge.html
already exposes (data-href on .kh-step-data and .kh-article-card), the
same pattern check_reading_time.py already uses to enumerate guides.

Counts each guide's own inline HTML source (script/style stripped, tags
stripped, whitespace-split), which naturally excludes shared nav/footer
chrome since those are empty mount points in the page source, populated
at runtime by js/site-chrome.js.

Run: python scripts/word_count.py
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_reading_time import KNOWLEDGE_HTML, collect_entries  # noqa: E402

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_STYLE_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)


def word_count(html):
    text = SCRIPT_STYLE_RE.sub(" ", html)
    text = TAG_RE.sub(" ", text)
    return len(text.split())


def main():
    html = KNOWLEDGE_HTML.read_text(encoding="utf-8")
    entries = collect_entries(html)
    seen = set()
    total = 0
    missing = []

    for href, _label, _mins in entries:
        if href in seen:
            continue
        seen.add(href)
        guide_path = REPO_ROOT / href.lstrip("/")
        if not guide_path.exists():
            missing.append(href)
            continue
        total += word_count(guide_path.read_text(encoding="utf-8"))

    print(f"Guides counted: {len(seen) - len(missing)}")
    if missing:
        print(f"Missing files (skipped): {len(missing)}")
        for m in missing:
            print(f"  - {m}")
    print(f"Total words: {total}")


if __name__ == "__main__":
    main()
