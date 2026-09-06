#!/usr/bin/env python3
"""
Fails loud if a guide's own hero "N min read" figure diverges from the
Knowledge Hub's own computed reading time for that same guide (the
data-mins on its .kh-step-data entry in knowledge.html), so the two
can't silently drift apart again (see BACKLOG.md, stablecoin series
polish pass, 2026-09-06: five guides' hero figures had gone stale
against the Hub's own numbers).

Run: python scripts/check_reading_time.py
Exit 0: every guide with a .kh-step-data entry matches its own hero
figure. Exit 1: at least one mismatch, listed individually.

Guides not yet listed in knowledge.html's #khFlagData (standalone
.kh-article-card entries, or a guide with no Hub entry yet) are not
checked here; there is no Hub-computed figure to compare against.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_HTML = REPO_ROOT / "knowledge.html"

STEP_RE = re.compile(
    r'<div class="kh-step-data"\s+data-href="([^"]+)"\s+data-label="([^"]*)"\s+data-mins="(\d+)\s*MIN"'
)
HERO_MIN_RE = re.compile(r'(?:[⏱📖]\s*)?(\d+)\s*min read')


def main():
    html = KNOWLEDGE_HTML.read_text(encoding="utf-8")
    mismatches = []
    checked = 0

    for href, label, hub_mins in STEP_RE.findall(html):
        guide_path = REPO_ROOT / href.lstrip("/")
        if not guide_path.exists():
            mismatches.append(f"{href}: listed in knowledge.html but file not found on disk")
            continue
        guide_html = guide_path.read_text(encoding="utf-8")
        m = HERO_MIN_RE.search(guide_html)
        if not m:
            mismatches.append(f"{href} ({label}): no hero \"N min read\" figure found to check against Hub's {hub_mins} MIN")
            continue
        hero_mins = m.group(1)
        checked += 1
        if hero_mins != hub_mins:
            mismatches.append(f"{href} ({label}): hero says {hero_mins} min read, Hub's own data-mins says {hub_mins} MIN")

    if mismatches:
        print(f"FAIL: {len(mismatches)} reading-time mismatch(es) found ({checked} guides checked):")
        for m in mismatches:
            print(f"  - {m}")
        sys.exit(1)

    print(f"OK: all {checked} guides' hero reading time match knowledge.html's own data-mins.")


if __name__ == "__main__":
    main()
