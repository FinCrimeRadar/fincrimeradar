#!/usr/bin/env python3
"""
FinCrimeRadar FinCrime Week: validates every data/fincrime-week/*.json
weekly issue file and renders the static homepage section, the
fincrime-week.html archive page.

No model calls, search calls, RSS readers, or network fetches anywhere in
this script. Every text field is escaped via fincrime_week_lib.esc() before
rendering. Content is entirely manually curated: this script only
validates and renders what's already written under data/fincrime-week/.

Usage: python scripts/generate_fincrime_week.py
Exits non-zero, printing the file, item id, and failing field, on the
first validation failure.
"""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fincrime_week_lib import DATA_DIR, esc, load_latest_published_fincrime_week

SITE = "https://fincrimeradar.org"
INDEX_HTML_PATH = Path(__file__).resolve().parent.parent / "index.html"
ARCHIVE_HTML_PATH = Path(__file__).resolve().parent.parent / "fincrime-week.html"

MARKER_START = "<!-- FINCRIME_WEEK_START -->"
MARKER_END = "<!-- FINCRIME_WEEK_END -->"

REQUIRED_TOP_LEVEL_FIELDS = ("week", "period_start", "period_end", "published_at", "author", "items")
REQUIRED_ITEM_FIELDS = (
    "id", "headline", "source_name", "source_url", "published_date",
    "jurisdiction", "category", "signal", "what_happened", "why_it_matters",
    "radar_implication", "primary_source", "reviewed",
)
NON_EMPTY_TEXT_FIELDS = ("what_happened", "why_it_matters", "radar_implication")

SIGNAL_VALUES = {"CRITICAL", "REGULATORY", "ENFORCEMENT", "EMERGING", "WATCH"}
CATEGORY_VALUES = {
    "AML_CTF", "SANCTIONS", "FRAUD", "CRYPTO", "CORRUPTION",
    "ASSET_RECOVERY", "FINANCIAL_CRIME",
}

WEEK_PATTERN = re.compile(r"^(\d{4})-W(\d{2})$")


class ValidationError(Exception):
    """Carries the file, item id (None for a file-level check), and the
    failing field, so main() can print exactly what CLAUDE.md requires on
    a validation failure."""

    def __init__(self, path, item_id, field, message):
        self.path = path
        self.item_id = item_id
        self.field = field
        location = "<file-level>" if item_id is None else item_id
        super().__init__(f"{path}: item={location} field={field}: {message}")


def _iso_date(path, item_id, field, value):
    if not isinstance(value, str):
        raise ValidationError(path, item_id, field, f"not a string: {value!r}")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError(path, item_id, field, f"not a valid ISO date: {value!r}")


def validate_file(path):
    """Validates one weekly issue file. Every check is scoped to this file
    alone, never against the rest of the archive. Returns the parsed dict
    on success. Raises ValidationError (or ValueError for malformed JSON)
    on the first failure found."""
    path = Path(path)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: malformed JSON: {e}") from e

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in data or data[field] is None:
            raise ValidationError(path, None, field, "missing required top-level field")

    items = data["items"]
    if not isinstance(items, list):
        raise ValidationError(path, None, "items", "must be a list")

    seen_ids = set()
    seen_urls = set()
    for item in items:
        item_id = item.get("id")

        for field in REQUIRED_ITEM_FIELDS:
            if field not in item or item[field] is None:
                raise ValidationError(path, item_id, field, "missing required field")

        if item_id in seen_ids:
            raise ValidationError(path, item_id, "id", "duplicate id within file")
        seen_ids.add(item_id)

        source_url = item["source_url"]
        if source_url in seen_urls:
            raise ValidationError(path, item_id, "source_url", "duplicate source_url within file")
        seen_urls.add(source_url)

        _iso_date(path, item_id, "published_date", item["published_date"])

        if item["category"] not in CATEGORY_VALUES:
            raise ValidationError(path, item_id, "category", f"not a valid category: {item['category']!r}")
        if item["signal"] not in SIGNAL_VALUES:
            raise ValidationError(path, item_id, "signal", f"not a valid signal: {item['signal']!r}")

        for field in NON_EMPTY_TEXT_FIELDS:
            if not str(item[field]).strip():
                raise ValidationError(path, item_id, field, "must be non-empty")

        if item["reviewed"] is not True:
            raise ValidationError(path, item_id, "reviewed", "must be true before publication")

        parsed_url = urlparse(source_url)
        if parsed_url.scheme != "https" or not parsed_url.hostname:
            raise ValidationError(path, item_id, "source_url", f"must be HTTPS with a hostname: {source_url!r}")

    week_str = data["week"]
    m = WEEK_PATTERN.match(week_str)
    if not m:
        raise ValidationError(path, None, "week", f"not in YYYY-WNN format: {week_str!r}")
    iso_year, iso_week = int(m.group(1)), int(m.group(2))

    if path.stem != week_str:
        raise ValidationError(
            path, None, "week", f"filename {path.name!r} does not match week field {week_str!r}"
        )

    try:
        week_monday = date.fromisocalendar(iso_year, iso_week, 1)
        week_sunday = date.fromisocalendar(iso_year, iso_week, 7)
    except ValueError:
        raise ValidationError(path, None, "week", f"not a valid ISO calendar week: {week_str!r}")

    period_start = _iso_date(path, None, "period_start", data["period_start"])
    period_end = _iso_date(path, None, "period_end", data["period_end"])
    published_at = _iso_date(path, None, "published_at", data["published_at"])

    if not (week_monday <= period_start <= week_sunday):
        raise ValidationError(
            path, None, "period_start",
            f"{period_start.isoformat()} falls outside ISO week {week_str} "
            f"({week_monday.isoformat()} to {week_sunday.isoformat()})",
        )

    if period_end != period_start + timedelta(days=6):
        raise ValidationError(
            path, None, "period_end",
            f"{period_end.isoformat()} is not exactly six days after period_start {period_start.isoformat()}",
        )

    if published_at < period_end:
        raise ValidationError(
            path, None, "published_at",
            f"{published_at.isoformat()} is earlier than period_end {period_end.isoformat()}",
        )

    return data


def load_all_valid_issues(data_dir=None):
    """Validates every file under data_dir, fail-fast on the first
    failure. Returns a list of (path, data) tuples, filename order."""
    directory = Path(data_dir) if data_dir is not None else DATA_DIR
    return [(path, validate_file(path)) for path in sorted(directory.glob("*.json"))]


# ---------------- Homepage rendering ----------------

def _fmt_date(iso_str):
    return date.fromisoformat(iso_str).strftime("%d %b %Y")


def _category_label(category):
    return category.replace("_", " ")


def render_homepage_fragment(reference_date=None, data_dir=None):
    """Returns the HTML fragment for the homepage section, or an empty
    string when no eligible issue exists (or the eligible issue has no
    items), rendering nothing between the markers, no header, no
    placeholder."""
    issue = load_latest_published_fincrime_week(reference_date=reference_date, data_dir=data_dir)
    if not issue or not issue.get("items"):
        return ""

    items = issue["items"]
    lead = items[0]
    supporting = items[1:5]

    lead_html = f"""
      <a class="fcw-lead" href="/fincrime-week.html" data-hover>
        <span class="fcw-chip">{esc(lead["signal"])} &middot; {esc(_category_label(lead["category"]))}</span>
        <h3>{esc(lead["headline"])}</h3>
        <p>{esc(lead["why_it_matters"])}</p>
        <span class="fcw-src">{esc(lead["source_name"])} &middot; {esc(lead["jurisdiction"])}</span>
      </a>"""

    supporting_html = "".join(
        f"""
      <a class="fcw-item" href="/fincrime-week.html" data-hover>
        <span class="fcw-chip fcw-chip-sm">{esc(i["signal"])}</span>
        <span class="fcw-item-head">{esc(i["headline"])}</span>
        <span class="fcw-src">{esc(i["source_name"])}</span>
      </a>"""
        for i in supporting
    )

    return f"""
<section class="fcw-section" aria-label="FinCrime Week">
  <div class="fcw-head">
    <span class="fcw-eyebrow">FinCrime Week</span>
    <span class="fcw-period">{_fmt_date(issue["period_start"])} &ndash; {_fmt_date(issue["period_end"])}</span>
  </div>
  <div class="fcw-grid">
    {lead_html}
    <div class="fcw-supporting">{supporting_html}
    </div>
  </div>
  <div class="fcw-links">
    <a class="fcw-cta" href="/fincrime-week.html" data-hover>Read the full briefing &rarr;</a>
    <a class="fcw-archive-link" href="/fincrime-week.html#archive" data-hover>Archive</a>
  </div>
</section>"""


def inject_homepage_section(html_text, fragment):
    start = html_text.index(MARKER_START) + len(MARKER_START)
    end = html_text.index(MARKER_END)
    if start > end:
        raise ValueError("FINCRIME_WEEK markers are missing or out of order in index.html")
    return html_text[:start] + "\n" + fragment + "\n" + html_text[end:]


# ---------------- Archive page rendering ----------------

def render_item_full(item):
    primary_badge = (
        '<span class="fcw-primary-badge">Primary source</span>'
        if item.get("primary_source")
        else ""
    )
    return f"""
    <article class="fcw-story">
      <h3>{esc(item["headline"])}</h3>
      <p class="fcw-story-meta">
        {esc(item["signal"])} &middot; {esc(_category_label(item["category"]))} &middot; {esc(item["jurisdiction"])}
        &middot; <a href="{esc(item["source_url"])}" rel="noopener" target="_blank">{esc(item["source_name"])}</a>
        {primary_badge}
      </p>
      <div class="callout info">
        <div class="callout-icon">&#128220;</div>
        <div class="callout-body">
          <div class="callout-title">What happened</div>
          <div class="callout-text">{esc(item["what_happened"])}</div>
        </div>
      </div>
      <div class="callout warning">
        <div class="callout-icon">&#9888;</div>
        <div class="callout-body">
          <div class="callout-title">Why it matters</div>
          <div class="callout-text">{esc(item["why_it_matters"])}</div>
        </div>
      </div>
      <div class="callout new">
        <div class="callout-icon">&#128225;</div>
        <div class="callout-body">
          <div class="callout-title">Radar implication</div>
          <div class="callout-text">{esc(item["radar_implication"])}</div>
        </div>
      </div>
    </article>"""


def render_issue_article(data):
    items_html = "".join(render_item_full(item) for item in data["items"])
    return f"""
  <article class="fcw-issue" id="{esc(data["week"])}">
    <header class="fcw-issue-head">
      <h2>{_fmt_date(data["period_start"])} &ndash; {_fmt_date(data["period_end"])}</h2>
      <p class="fcw-byline">
        Written by {esc(data["author"])} &middot; Published {_fmt_date(data["published_at"])}
        &middot; <a href="/editorial-standards.html">Editorial standards</a>
      </p>
    </header>
    {items_html}
  </article>"""


PAGE_STYLE = """
  :root {
    --white:#ffffff; --off:#f7f8fa; --border:#e4e7ec;
    --muted:#6b7280; --text:#111827; --navy:#0f2044;
    --accent:#00c4a7; --accent-h:#00a892; --success:#16a34a;
  }
  * { box-sizing:border-box; }
  html { scroll-behavior:smooth; }
  body { margin:0; font-family:'Inter',system-ui,sans-serif; background:var(--off); color:var(--text); line-height:1.7; }

  nav { position:sticky; top:0; z-index:200; display:flex; align-items:center; justify-content:space-between; padding:0 2rem; height:72px; background:rgba(255,255,255,0.97); backdrop-filter:blur(8px); border-bottom:1px solid var(--border); }
  .nav-brand { display:flex; align-items:center; gap:8px; text-decoration:none; }
  .nav-links { display:flex; align-items:center; gap:1.25rem; }
  .nav-links a { font-size:13px; color:#374151; text-decoration:none; transition:color 0.15s; }
  .nav-links a:hover { color:var(--accent); }
  .nav-cta { padding:7px 16px; background:var(--accent); color:#fff !important; border-radius:6px; font-size:13px; font-weight:500; text-decoration:none; }
  .nav-cta:hover { background:var(--accent-h); color:#fff; }
  .nav-hamburger { display:none; background:none; border:none; font-size:22px; cursor:pointer; color:var(--navy); padding:4px 6px; line-height:1; }
  .mobile-nav { display:none; position:fixed; top:72px; left:0; right:0; background:#fff; border-bottom:1px solid var(--border); flex-direction:column; z-index:99; padding:0.5rem 0; box-shadow:0 8px 24px rgba(0,0,0,0.08); }
  .mobile-nav.open { display:flex; }
  .mobile-nav a { padding:14px 1.5rem; font-size:15px; color:#374151; text-decoration:none; font-weight:500; border-bottom:1px solid #f3f4f6; transition:background 0.1s; }
  .mobile-nav a:hover { background:#f9fafb; }
  .mobile-nav .mobile-nav-cta { margin:0.75rem 1.5rem 0.5rem; background:var(--accent); color:#fff !important; border-radius:8px; text-align:center; border-bottom:none; }
  @media(max-width:767px) {
    nav { padding:0 1rem; }
    .nav-hamburger { display:block; }
    .nav-links { display:none; }
    .nav-brand img { height:40px !important; width:auto !important; max-width:160px !important; }
  }

  .fcw-hero { max-width:900px; margin:0 auto; padding:3rem 1.5rem 1rem; }
  .fcw-hero .eyebrow { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:var(--accent); }
  .fcw-hero h1 { font-size:clamp(1.8rem,4vw,2.6rem); font-weight:700; color:var(--navy); margin:0.6rem 0 0.75rem; }
  .fcw-hero p { color:var(--muted); font-size:15px; max-width:640px; }

  .fcw-archive { max-width:900px; margin:0 auto; padding:1rem 1.5rem 4rem; }
  .fcw-empty { color:var(--muted); font-size:15px; padding:2rem 0; }
  .fcw-issue { border:1px solid var(--border); border-radius:14px; background:var(--white); padding:1.75rem 2rem; margin-bottom:1.5rem; }
  .fcw-issue-head h2 { font-size:20px; color:var(--navy); margin:0 0 6px; }
  .fcw-byline { font-size:12.5px; color:var(--muted); margin:0 0 1.25rem; }
  .fcw-byline a { color:var(--accent); text-decoration:none; }
  .fcw-byline a:hover { text-decoration:underline; }
  .fcw-story { padding-top:1rem; margin-top:1rem; border-top:1px solid var(--border); }
  .fcw-story:first-of-type { border-top:none; margin-top:0; }
  .fcw-story h3 { font-size:16px; color:var(--navy); margin:0 0 6px; }
  .fcw-story-meta { font-size:12px; color:var(--muted); margin:0 0 10px; text-transform:uppercase; letter-spacing:0.3px; }
  .fcw-story-meta a { color:var(--accent); text-decoration:none; }
  .fcw-story-meta a:hover { text-decoration:underline; }
  .fcw-primary-badge { display:inline-block; margin-left:6px; padding:2px 7px; border-radius:4px; background:#dcfce7; color:#166534; font-size:10px; font-weight:700; letter-spacing:0.3px; text-transform:uppercase; }

  .callout { border-radius:10px; padding:1.1rem 1.4rem; margin:1rem 0; display:flex; gap:12px; }
  .callout-icon { font-size:18px; flex-shrink:0; margin-top:1px; }
  .callout-body { flex:1; }
  .callout-title { font-size:12px; font-weight:700; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.4px; }
  .callout-text { font-size:13.5px; line-height:1.6; }
  .callout.info { background:#eff6ff; border:1px solid #bfdbfe; }
  .callout.info .callout-title { color:#1e40af; }
  .callout.info .callout-text { color:#1e3a8a; }
  .callout.warning { background:#fffbeb; border:1px solid #fde68a; }
  .callout.warning .callout-title { color:#92400e; }
  .callout.warning .callout-text { color:#78350f; }
  .callout.new { background:#f0fdf4; border:1px solid #86efac; border-left:3px solid var(--success); }
  .callout.new .callout-title { color:#166534; }
  .callout.new .callout-text { color:#14532d; }

  footer { background:var(--white); border-top:1px solid var(--border); padding:2rem; text-align:center; font-size:12px; color:var(--muted); margin-top:2rem; }
  footer a { color:var(--muted); text-decoration:none; margin:0 8px; }
  footer a:hover { color:var(--accent); }
"""

NAV_HTML = """<nav>
  <a class="nav-brand" href="/">
    <img src="/logo.png" alt="FinCrimeRadar" width="660" height="237" style="height:44px;width:auto;max-width:200px;object-fit:contain;object-position:left center;display:block;" />
  </a>
  <div class="nav-links">
    <a href="/knowledge.html">Knowledge Hub</a>
    <a href="/fincrime-week.html">FinCrime Week</a>
    <a href="/scenario-lab.html">Scenario Lab</a>
    <a href="/screen.html" class="nav-cta">Try the tool &rarr;</a>
  </div>
  <button class="nav-hamburger" id="navHamburger" onclick="toggleMobileNav()" aria-label="Toggle menu">&#9776;</button>
</nav>
<div class="mobile-nav" id="mobileNav">
  <a href="/knowledge.html">Knowledge Hub</a>
  <a href="/fincrime-week.html">FinCrime Week</a>
  <a href="/scenario-lab.html">Scenario Lab</a>
  <a href="/screen.html" class="mobile-nav-cta">Try the tool &rarr;</a>
</div>
<script>
  function toggleMobileNav(){
    document.getElementById('mobileNav').classList.toggle('open');
  }
</script>"""


def render_archive_page(issues_desc):
    if issues_desc:
        body = "".join(render_issue_article(data) for _, data in issues_desc)
    else:
        body = '<p class="fcw-empty">No FinCrime Week issues published yet. Check back soon.</p>'

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FinCrime Week | FinCrimeRadar</title>
<meta name="description" content="FinCrime Week: a practitioner-curated weekly briefing on AML, sanctions, fraud and financial crime developments, with primary sources and radar implications for every story.">
<link rel="canonical" href="{SITE}/fincrime-week.html">
<meta name="robots" content="index, follow">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/brand.css">
<style>{PAGE_STYLE}</style>
</head>
<body>
{NAV_HTML}

<div class="fcw-hero">
  <span class="eyebrow">Manually curated, primary-sourced</span>
  <h1>FinCrime Week</h1>
  <p>Every published issue, in full, most recent first. Written and reviewed by a financial crime specialist and former Acting MLRO, sourced directly from regulators, courts and government publications.</p>
</div>

<div class="fcw-archive" id="archive">
{body}
</div>

<div id="site-footer"></div>
<script defer src="/js/site-chrome.js"></script>
</body>
</html>"""


# ---------------- Main ----------------

def main():
    try:
        issues = load_all_valid_issues()
    except (ValidationError, ValueError) as e:
        sys.exit(f"ABORT: {e}")

    issues_desc = sorted(issues, key=lambda pair: pair[1]["published_at"], reverse=True)

    fragment = render_homepage_fragment()
    index_html = INDEX_HTML_PATH.read_text(encoding="utf-8")
    try:
        index_html = inject_homepage_section(index_html, fragment)
    except ValueError as e:
        sys.exit(f"ABORT: {e}")
    INDEX_HTML_PATH.write_text(index_html, encoding="utf-8")

    ARCHIVE_HTML_PATH.write_text(render_archive_page(issues_desc), encoding="utf-8")

    print(f"Validated {len(issues)} weekly issue file(s). Homepage and archive page written.")


if __name__ == "__main__":
    main()
