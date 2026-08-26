#!/usr/bin/env python3
"""Validate, audit, and scan against verification-ledger.json.

Usage:
    python scripts/check_ledger.py validate
    python scripts/check_ledger.py overdue
    python scripts/check_ledger.py scan <guide.html>
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "verification-ledger.json"

REQUIRED_TOP_FIELDS = [
    "claimId", "guide", "claimText", "claimType",
    "source", "verifiedOn", "reviewDue", "status",
]
REQUIRED_SOURCE_FIELDS = ["title", "url", "publisher", "date"]

# internal-consistency: reconciles two representations of the same fact within a
#   single guide (e.g. a decision-tree label vs. its own worked example), not an
#   external regulatory/statistical claim.
# process-record: an internal audit-trail entry documenting a guide's own review
#   history (e.g. a legal review register), not a factual claim about the world.
ALLOWED_CLAIM_TYPES = {
    "statistic", "regulatory", "enforcement", "definition",
    "internal-consistency", "process-record",
}
# verified: sourced to a primary/named-study reference and confirmed.
# needs-review: sourced but not yet confirmed, or due for re-check.
# unverifiable-remove: could not be sourced and has been (or should be) removed from the guide.
# retained-as-estimate: kept in the guide, disclosed in-text as an unverified industry estimate, no primary source claimed.
ALLOWED_STATUSES = {"verified", "needs-review", "unverifiable-remove", "retained-as-estimate"}

DATE_FORMAT = "%Y-%m-%d"


def load_ledger(path=LEDGER_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_date(value):
    return datetime.strptime(value, DATE_FORMAT).date()


def validate(entries):
    """Check every entry against the ledger schema. Return a list of error strings."""
    errors = []
    seen_ids = set()

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"<entry index {i}>: entry is not an object")
            continue

        label = entry.get("claimId", f"<entry index {i}>")

        for field in REQUIRED_TOP_FIELDS:
            # unverifiable-remove and retained-as-estimate entries document a claim
            # with no real primary/named-study reference. A missing 'source' here
            # means "none found," not an incomplete entry; inventing one to satisfy
            # the schema would be worse than the gap itself. process-record entries
            # are internal audit-trail records of a guide's own review history, not
            # externally-sourceable factual claims, so they carry no source by design.
            if field == "source" and (
                entry.get("status") in ("unverifiable-remove", "retained-as-estimate")
                or entry.get("claimType") == "process-record"
            ):
                continue
            if field not in entry:
                errors.append(f"{label}: missing field '{field}'")

        claim_id = entry.get("claimId")
        if claim_id:
            if claim_id in seen_ids:
                errors.append(f"{label}: duplicate claimId")
            seen_ids.add(claim_id)

        claim_type = entry.get("claimType")
        if claim_type is not None and claim_type not in ALLOWED_CLAIM_TYPES:
            errors.append(
                f"{label}: claimType '{claim_type}' not in {sorted(ALLOWED_CLAIM_TYPES)}"
            )

        status = entry.get("status")
        if status is not None and status not in ALLOWED_STATUSES:
            errors.append(
                f"{label}: status '{status}' not in {sorted(ALLOWED_STATUSES)}"
            )

        source = entry.get("source")
        if source is None:
            if status == "verified" and claim_type != "process-record":
                errors.append(f"{label}: status 'verified' requires a non-null 'source'")
        elif not isinstance(source, dict):
            errors.append(f"{label}: 'source' is not an object")
        else:
            for field in REQUIRED_SOURCE_FIELDS:
                if field not in source:
                    errors.append(f"{label}: source missing field '{field}'")
            if "date" in source:
                try:
                    _parse_date(source["date"])
                except (ValueError, TypeError):
                    errors.append(f"{label}: source.date '{source['date']}' is not YYYY-MM-DD")

        for date_field in ("verifiedOn", "reviewDue"):
            if date_field in entry:
                try:
                    _parse_date(entry[date_field])
                except (ValueError, TypeError):
                    errors.append(
                        f"{label}: {date_field} '{entry[date_field]}' is not YYYY-MM-DD"
                    )

    return errors


def overdue(entries, today=None):
    """Return entries whose reviewDue date is in the past relative to today."""
    today = today or date.today()
    results = []
    for entry in entries:
        review_due = entry.get("reviewDue")
        if not review_due:
            continue
        try:
            due_date = _parse_date(review_due)
        except (ValueError, TypeError):
            continue
        if due_date < today:
            results.append(entry)
    return results


# ---------------------------------------------------------------------------
# scan: extract visible prose text from a guide HTML file and flag candidate
# hard claims. This is a candidate finder, not a classifier: it surfaces
# possible material claims, a human decides which ones are real.
# ---------------------------------------------------------------------------

# NOTE: this is a candidate finder, not a completeness guarantee. It surfaces
# what its tag scope and regex vocabulary can see; it will not catch every
# material claim (e.g. a real figure phrased with a noun or wrapped in a tag
# nobody thought to list here). A human read is always the backstop. A clean
# scan is evidence of nothing being caught, not proof nothing was missed.
PROSE_TAGS = {"p", "li", "td", "h2", "h3", "h4", "div"}
EXCLUDED_TAGS = {"script", "style"}

REGEX_PERCENT = re.compile(r"\b\d+(?:\.\d+)?\s?%")
REGEX_CURRENCY = re.compile(
    r"[$£€]\s?\d[\d,]*(?:\.\d+)?\s?(?:million|billion|thousand|m|bn|k)?\b",
    re.IGNORECASE,
)
REGEX_REGULATION = re.compile(
    r"\b(?:FCA|FinCEN|JMLSG|POCA|MLR\s?2017|FCG\s?\d+(?:\.\d+)*[A-Z]?|SYSC\s?\d+(?:\.\d+)*)\b"
)
REGEX_COUNT = re.compile(
    r"\b\d[\d,]*(?:\s?[-–]\s?\d[\d,]*)?\+?\s+"
    r"(?:SARs?|alerts?|records?|rules?|models?|scenarios?)\b",
    re.IGNORECASE,
)

CANDIDATE_PATTERNS = [
    ("percentage", REGEX_PERCENT),
    ("currency", REGEX_CURRENCY),
    ("regulation", REGEX_REGULATION),
    ("count", REGEX_COUNT),
]


class VisibleTextExtractor(HTMLParser):
    """Collects visible text chunks from PROSE_TAGS, with their source line
    number, while excluding script/style content, tag attributes, and class
    names entirely (attrs are never read as text)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag_stack = []
        self.chunks = []  # list of (line_number, text)

    def handle_starttag(self, tag, attrs):
        self.tag_stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        for i in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[i] == tag:
                del self.tag_stack[i:]
                break

    def _capturing(self):
        if any(t in EXCLUDED_TAGS for t in self.tag_stack):
            return False
        return any(t in PROSE_TAGS for t in self.tag_stack)

    def handle_data(self, data):
        if not data.strip():
            return
        if self._capturing():
            line, _col = self.getpos()
            self.chunks.append((line, data.strip()))


def extract_visible_text(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    parser = VisibleTextExtractor()
    parser.feed(html)
    return parser.chunks


def scan(html_path):
    """Extract visible prose text and flag candidate hard claims.

    Returns a list of dicts: {line, category, match, context}.
    """
    candidates = []
    for line, text in extract_visible_text(html_path):
        for category, pattern in CANDIDATE_PATTERNS:
            for m in pattern.finditer(text):
                candidates.append({
                    "line": line,
                    "category": category,
                    "match": m.group(0),
                    "context": text,
                })
    return candidates


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_validate(args):
    entries = load_ledger()
    errors = validate(entries)
    if not errors:
        print(f"OK: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} valid.")
        return 0
    print(f"FAIL: {len(errors)} issue(s) found.")
    for e in errors:
        print(f"  - {e}")
    return 1


def cmd_overdue(args):
    entries = load_ledger()
    due = overdue(entries)
    if not due:
        print("OK: no overdue entries.")
        return 0
    print(f"{len(due)} overdue entr{'y' if len(due) == 1 else 'ies'}:")
    for entry in due:
        print(f"  - {entry.get('claimId')} (reviewDue {entry.get('reviewDue')})")
    return 1


def cmd_scan(args):
    html_path = Path(args.guide)
    if not html_path.is_absolute():
        html_path = REPO_ROOT / html_path
    if not html_path.exists():
        print(f"ERROR: {html_path} not found.")
        return 1

    candidates = scan(html_path)
    if not candidates:
        print("No candidate claims found.")
        return 0

    print(f"{len(candidates)} candidate(s) in {html_path.name}:")
    for c in candidates:
        print(f"  line {c['line']:>4}  [{c['category']:<10}] {c['match']!r}  -- {c['context']}")
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate every ledger entry against the schema.")
    sub.add_parser("overdue", help="List entries whose reviewDue date has passed.")

    scan_parser = sub.add_parser("scan", help="Scan a guide HTML file for candidate hard claims.")
    scan_parser.add_argument("guide", help="Path to the guide HTML file, e.g. tm-guide.html")

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(cmd_validate(args))
    elif args.command == "overdue":
        sys.exit(cmd_overdue(args))
    elif args.command == "scan":
        sys.exit(cmd_scan(args))


if __name__ == "__main__":
    main()
