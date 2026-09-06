#!/usr/bin/env python3
"""
Fails loud if a guide's own hero "N min read" figure diverges from the
Knowledge Hub's own computed reading time for that same guide, so the
two can't silently drift apart again (see BACKLOG.md, stablecoin
series polish pass, 2026-09-06: five guides' hero figures had gone
stale against the Hub's own numbers).

Covers both places knowledge.html records a reading-time figure:
- Flagship series parts: data-mins on each .kh-step-data entry.
- Standalone guides: the "N MIN" text inside each .kh-article-card's
  own .kh-read span.

Run: python scripts/check_reading_time.py
Exit 0: every checked guide's hero figure matches the Hub's own
number. Exit 1: at least one mismatch, listed individually.

A guide listed in knowledge.html but with no hero "N min read" figure
of its own (some Evidence Essay-treatment guides use a different hero
layout with no reading-time badge at all) is out of scope, not a
failure, and is silently skipped, not reported.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_HTML = REPO_ROOT / "knowledge.html"

STEP_RE = re.compile(
    r'<div class="kh-step-data"\s+data-href="([^"]+)"\s+data-label="([^"]*)"\s+data-mins="(\d+)\s*MIN"'
)
CARD_RE = re.compile(
    r'<a href="([^"]+)" class="kh-article-card"[^>]*>(.*?)</a>', re.S
)
CARD_TITLE_RE = re.compile(r'kh-item-title">([^<]*)<')
CARD_READ_RE = re.compile(r'kh-read">(\d+)\s*MIN')
HERO_MIN_RE = re.compile(r'(?:[⏱📖]\s*)?(\d+)\s*min read')


def collect_entries(html):
    """Returns a list of (href, label, hub_mins) from both flagship
    .kh-step-data entries and standalone .kh-article-card entries."""
    entries = [(href, label, mins) for href, label, mins in STEP_RE.findall(html)]
    for href, inner in CARD_RE.findall(html):
        mins_m = CARD_READ_RE.search(inner)
        if not mins_m:
            continue  # no reading-time badge on this card at all, nothing to compare
        title_m = CARD_TITLE_RE.search(inner)
        label = title_m.group(1) if title_m else href
        entries.append((href, label, mins_m.group(1)))
    return entries


def main():
    html = KNOWLEDGE_HTML.read_text(encoding="utf-8")
    mismatches = []
    checked = 0
    skipped = 0

    for href, label, hub_mins in collect_entries(html):
        guide_path = REPO_ROOT / href.lstrip("/")
        if not guide_path.exists():
            mismatches.append(f"{href}: listed in knowledge.html but file not found on disk")
            continue
        guide_html = guide_path.read_text(encoding="utf-8")
        m = HERO_MIN_RE.search(guide_html)
        if not m:
            skipped += 1
            continue  # no hero figure of its own, out of scope, not a failure
        hero_mins = m.group(1)
        checked += 1
        if hero_mins != hub_mins:
            mismatches.append(f"{href} ({label}): hero says {hero_mins} min read, Hub's own figure says {hub_mins} MIN")

    if mismatches:
        print(f"FAIL: {len(mismatches)} reading-time mismatch(es) found ({checked} guides checked, {skipped} skipped, out of scope):")
        for m in mismatches:
            print(f"  - {m}")
        sys.exit(1)

    print(f"OK: all {checked} guides' hero reading time match knowledge.html's own figures ({skipped} skipped, no hero figure of their own, out of scope).")


if __name__ == "__main__":
    main()
