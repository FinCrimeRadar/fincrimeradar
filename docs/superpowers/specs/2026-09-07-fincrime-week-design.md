# FinCrime Week (manually curated editorial module)

## Problem

The weekly digest's news section (`NEWS_ROUNDUP_LIBRARY` / `get_this_weeks_news()`
in `scripts/send_weekly_digest.py`) is a deterministic ISO-week rotation
through a manually curated, currently-empty list, with no homepage presence
and no standalone archive page. We're replacing it with FinCrime Week: a
manually curated weekly news roundup that has a homepage teaser section, a
standalone archive page (`fincrime-week.html`), and a digest section, all
driven from one JSON file per week under `data/fincrime-week/`.

No RSS, search, API discovery, LLM generation, or network calls anywhere in
this feature. It is exactly as automated as `NEWS_ROUNDUP_LIBRARY` was:
Pratik writes the JSON by hand, a generator script validates and renders it.

## Data model

`data/fincrime-week/YYYY-WNN.json` (e.g. `2026-W37.json`), one file per
published week, ships empty this round (`.gitkeep` only, no sample content).

Top level: `week`, `period_start`, `period_end`, `published_at`, `author`,
`items[]`.

Each item: `id`, `headline`, `source_name`, `source_url`, `published_date`,
`jurisdiction`, `category`, `signal`, `what_happened`, `why_it_matters`,
`radar_implication`, `primary_source` (bool), `reviewed` (bool).

- `signal` enum (why it matters): `CRITICAL`, `REGULATORY`, `ENFORCEMENT`,
  `EMERGING`, `WATCH`
- `category` enum (what domain): `AML_CTF`, `SANCTIONS`, `FRAUD`, `CRYPTO`,
  `CORRUPTION`, `ASSET_RECOVERY`, `FINANCIAL_CRIME`

`published_at`, `period_start`, `period_end`, and `published_date` are all
plain ISO 8601 calendar dates (`YYYY-MM-DD`, no time component, no
timezone). The Monday 08:00 UTC digest send is treated as
`reference_date=date.today()` at send time, so date-level comparison is
sufficient throughout and there's no datetime/timezone parsing anywhere in
this feature.

Sourcing: each item's `source_url` / `primary_source` / `reviewed` fields
are the sourcing mechanism for this manually curated log, not
`verification-ledger.json` (that ledger governs guide prose; this is a
per-item attributed news log, same convention `NEWS_ROUNDUP_LIBRARY` used).
Any item asserting regulatory scope or applicability (not just "regulator X
fined firm Y") needs the external adversarial review CLAUDE.md §7 already
requires for that class of claim — the generator can't detect this, so it's
flagged per item in the delivery report at content-authoring time, not
enforced in code.

## Architecture

```
scripts/fincrime_week_lib.py   <- shared library, stdlib only, no cross-imports
        esc(s)
        load_latest_published_fincrime_week(reference_date=None)
              |                                    |
              v                                    v
scripts/generate_fincrime_week.py       scripts/send_weekly_digest.py
  validates data/fincrime-week/*.json     build_digest_html() calls
  renders index.html FINCRIME_WEEK        load_latest_published_fincrime_week()
  block + fincrime-week.html archive      None -> no section (safe-empty,
                                           same as old empty library)
```

`scripts/fincrime_week_lib.py` is new and deliberately dependency-free:
stdlib only (`json`, `html`, `datetime`, `pathlib`, `urllib.parse`), no
import of `generate_delta_pages` or `send_weekly_digest`, no `requests`.
Both `generate_fincrime_week.py` and `send_weekly_digest.py` import from it,
so the "which issue is current" logic and the escaping helper exist in
exactly one place instead of two independent copies.

### `load_latest_published_fincrime_week(reference_date=None)`

Scans every `data/fincrime-week/*.json` file (never derives a target
filename from `reference_date`'s own ISO week — the Monday 08:00 UTC digest
send always falls at the start of a new ISO week relative to the file it
needs), parses `published_at` on each, and returns the full issue dict for
the file with the greatest `published_at` that is `<= reference_date`
(default: today). Returns `None` when no eligible file exists (empty
directory, or every file's `published_at` is in the future relative to
`reference_date`).

### `scripts/generate_fincrime_week.py`

No model calls, search calls, RSS readers, or network fetches. Imports
`esc()` and `load_latest_published_fincrime_week()` from
`fincrime_week_lib`.

**Validation**, scoped to the file being processed (not the whole archive):
required fields present; unique `id`s within the file; unique `source_url`s
within the file; valid ISO dates; `category` and `signal` each one of the
defined enum values; `what_happened` / `why_it_matters` /
`radar_implication` non-empty; `reviewed` is `true` for every item;
`source_url` is HTTPS with a non-empty hostname (`urllib.parse`); filename's
week matches the top-level `week` field; `period_start` falls within the
ISO week declared by `week`; `period_end` equals `period_start` plus six
days; `published_at` is not earlier than `period_end`. `published_date` is
**not** required to fall inside the weekly period — editorial judgement
call, left alone. Every text field (`headline`, `source_name`,
`jurisdiction`, `category`, `what_happened`, `why_it_matters`,
`radar_implication`, `author`) is escaped via `fincrime_week_lib.esc()`
before rendering. On any validation failure: print the file, the failing
item's `id`, and the failing field, exit non-zero.

**Homepage rendering:** a new `<section>` in `index.html`, sibling to
`updates-band` and `main.zone-light` — inserted between the `updates-band`
`</section>` (line 273) and `<main class="zone-light">` (line 275), **not**
a bento cell, so it can't inherit `.c-news`/`.cell` global rules (component
isolation, CLAUDE.md §14). Content lives between explicit markers:

```html
<!-- FINCRIME_WEEK_START -->
...
<!-- FINCRIME_WEEK_END -->
```

Sourced from `load_latest_published_fincrime_week()` with no
`reference_date` (today, at generation time). Within the selected issue's
`items[]`: `items[0]` is the lead story, `items[1:5]` are supporting, in
whatever order they're written in the JSON — no scoring or sorting logic.
Shows the period date range, a "Read the full briefing" link to
`fincrime-week.html`, and an archive link. If the loader returns `None`,
the marker block is emptied — no header, no placeholder.

**Archive rendering:** `fincrime-week.html`, a new standalone page using the
same skeleton as an existing guide page — hardcoded nav (copied from a guide
page, not the JS-driven `#site-nav` mount), `<div id="site-footer"></div>` +
`/js/site-chrome.js` for the footer, `/brand.css` + the same Google Fonts
link. Lists every published issue in reverse chronological order (by
`published_at`), full content per item. Reuses the existing `.callout`
new/info/warning pattern — the page-scoped inline CSS block copied from a
guide page, not added to `brand.css` — for `what_happened` / `why_it_matters`
/ `radar_implication`, rather than a new visual system. Preserves named
author, publication date, primary-source attribution per item, and a link
to `editorial-standards.html`.

### `send_weekly_digest.py` changes

Delete `NEWS_ROUNDUP_LIBRARY` and `get_this_weeks_news()` entirely. Import
`load_latest_published_fincrime_week` from `fincrime_week_lib`.
`build_digest_html()` calls it; `None` renders no FinCrime Week section,
matching the safe-empty behaviour the old library had when empty
(`get_this_weeks_guides` still ungated, `Scenario Lab` block untouched).
When an issue is found, the email section mirrors the homepage shape —
lead story plus supporting stories (`items[0]`, `items[1:5]`) — styled
consistently with the digest's existing inline-styled cards, with a link to
`{SITE}/fincrime-week.html`.

### Sitemap

One manual `<url>` entry for `fincrime-week.html` added to `sitemap.xml`
now — not generator-managed, unlike `delta/*.html`, because this URL never
changes run to run. `data/fincrime-week/*.json` is never added to
`sitemap.xml`.

## Testing

`scripts/test_fincrime_week.py`, `unittest` (stdlib, no new dependency),
importing `fincrime_week_lib`, `generate_fincrime_week`, and
`send_weekly_digest` directly. Covers: valid weekly file; malformed JSON;
duplicate `id` within file; duplicate `source_url` within file; missing
required field; invalid `signal` value; invalid `category` value;
`reviewed` false; filename/week mismatch; `period_start` outside declared
ISO week; `period_end` not exactly six days after `period_start`;
`published_at` earlier than `period_end`; non-HTTPS or hostname-less
`source_url`; HTML escaping of a field containing markup characters;
homepage marker replacement; archive reverse-chronological ordering;
correct Monday-rollover selection by `load_latest_published_fincrime_week`;
exclusion of a future-dated `published_at`; correct latest-issue selection
where several files exist; `None` returned, and digest renders no section,
when no eligible issue exists.

## Explicitly out of scope

- RSS, web search, API discovery, LLM generation, automated summaries, or
  any external network call anywhere in this feature.
- Any change to the current AdSense implementation, CMP implementation, the
  Flagship Guides / `.c-news` module, or any unrelated homepage section.
- Sequencing this work around the current AdSense review — independent.
- Routing sourcing through `verification-ledger.json`.
- Real week content this round — `data/fincrime-week/` ships with a
  `.gitkeep` only; Pratik adds real weekly files by hand going forward.
- Committing or pushing before implementation, tests, and the rendered diff
  have been independently reviewed.
