#!/usr/bin/env python3
"""
Shared library for the FinCrime Week module.

Stdlib only (json, html, datetime, pathlib), no import of
generate_delta_pages.py or send_weekly_digest.py, and no import of
requests. scripts/generate_fincrime_week.py and scripts/send_weekly_digest.py
both import from here, so escaping and "which issue is current" logic exist
in exactly one place instead of two independent copies.
"""

import html
import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "fincrime-week"


def esc(s):
    return html.escape(s or "")


def load_latest_published_fincrime_week(reference_date=None, data_dir=None):
    """
    Scans every data/fincrime-week/*.json file and returns the full issue
    dict for the file with the greatest published_at that is <=
    reference_date (default: today). Never derives the target filename from
    reference_date's own ISO week: the Tuesday 08:00 UTC digest send always
    falls at the start of a new ISO week relative to the file it needs, so
    the file must be found by scanning published_at values, not by
    computing a filename. Returns None when no eligible file exists.

    data_dir overrides the default data/fincrime-week/ directory, for
    tests to point at fixture files without touching the real directory.
    """
    reference_date = reference_date or date.today()
    directory = Path(data_dir) if data_dir is not None else DATA_DIR

    best_issue = None
    best_published_at = None

    for path in sorted(directory.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                issue = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        published_at_raw = issue.get("published_at")
        if not published_at_raw:
            continue
        try:
            published_at = date.fromisoformat(published_at_raw)
        except ValueError:
            continue

        if published_at > reference_date:
            continue
        if best_published_at is None or published_at > best_published_at:
            best_published_at = published_at
            best_issue = issue

    return best_issue
