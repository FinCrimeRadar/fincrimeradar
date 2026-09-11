#!/usr/bin/env python3
"""Static contract checks for the Money Mule or Victim Case File."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "money-mule-or-victim-case-file.html"
DATA_SCRIPT = ROOT / "js" / "money-mule-case-file-data.js"
SCRIPT = ROOT / "js" / "money-mule-case-file.js"

# Stage 3 to 8 strings that only exist once evidence is disclosed. Each must
# live in the data file but never leak into the static HTML shell, which is
# how the progressive-disclosure contract is checked without a browser.
PROGRESSIVE_DISCLOSURE_STRINGS = (
    "Client Settlement Assistant",
    "seventeen months",
    "own position on the five hypotheses",
    "The messages change the picture",
    "seventeen attempted calls",
    "three year account history",
)

ALLOWED_EVENT_NAMES = {"case_file_stage_complete", "case_file_reasoning_shift"}
FORBIDDEN_TELEMETRY_KEYS = (
    "hypothesisState",
    "decisionRecord",
    "knowledgeTimeline",
    "redTeamCompleted",
    "decisionChangeSelections",
)


class KnowledgeCountParser(HTMLParser):
    """Mirror the Knowledge Hub's guide-count inputs from its static markup."""

    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, str | None]] = []
        self.text_by_id: dict[str, list[str]] = {"khHeroCount": [], "khStatGuides": []}
        self.standalone_guides = 0
        self.series_guides = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        classes = set((attributes.get("class") or "").split())
        ancestor_ids = {item_id for _, item_id in self.stack}
        if "khArticlesGrid" in ancestor_ids and "kh-article-card" in classes:
            self.standalone_guides += 1
        if "khFlagData" in ancestor_ids and "kh-step-data" in classes:
            self.series_guides += 1
        if tag not in self.VOID_ELEMENTS:
            self.stack.append((tag, element_id))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for _, element_id in reversed(self.stack):
            if element_id in self.text_by_id:
                self.text_by_id[element_id].append(data)
                break

    def count_text(self, element_id: str) -> int:
        value = "".join(self.text_by_id[element_id]).strip()
        require(value.isdigit(), f"Knowledge Hub {element_id} is not a numeric static count")
        return int(value)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    html = GUIDE.read_text(encoding="utf-8")
    data_script = DATA_SCRIPT.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    guide_standard = (ROOT / "GUIDE_STANDARD.md").read_text(encoding="utf-8")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))

    require(GUIDE.exists(), "money-mule-or-victim-case-file.html is missing")

    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    require(not duplicates, f"duplicate IDs: {duplicates}")
    require('href="#main-content"' in html and 'id="main-content"' in html, "skip link target is missing")
    require(html.count("<h1") == 1, "expected exactly one h1")

    heading_levels = [int(level) for level in re.findall(r"<h([1-6])\b", html)]
    for previous, current in zip(heading_levels, heading_levels[1:]):
        require(current <= previous + 1, f"heading order skips from h{previous} to h{current}")

    json_ld = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    require(len(json_ld) == 2, "expected Article and BreadcrumbList JSON-LD blocks")
    structured = [json.loads(block) for block in json_ld]
    article = next((item for item in structured if item.get("@type") == "Article"), None)
    breadcrumbs = next((item for item in structured if item.get("@type") == "BreadcrumbList"), None)
    require(article is not None, "Article JSON-LD missing")
    for prop in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "mainEntityOfPage", "image"):
        require(prop in article, f"Article property missing: {prop}")
    require(article.get("articleSection") == "Case File", "Article articleSection must be Case File")
    require(breadcrumbs is not None and len(breadcrumbs.get("itemListElement", [])) == 3, "BreadcrumbList is incomplete")

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)"', html)
    require(canonical and og_url and canonical.group(1) == og_url.group(1), "canonical and Open Graph URL differ")
    require(canonical.group(1) in sitemap, "canonical URL missing from sitemap")

    require('/money-mule-or-victim-case-file.html' in knowledge, "Knowledge Hub card missing")
    require('kh-format-label">Case File<' in knowledge, "visible Case File label missing from Knowledge Hub card")

    knowledge_counts = KnowledgeCountParser()
    knowledge_counts.feed(knowledge)
    declared_count = knowledge_counts.standalone_guides + knowledge_counts.series_guides
    hero_count = knowledge_counts.count_text("khHeroCount")
    stat_count = knowledge_counts.count_text("khStatGuides")
    require(hero_count == stat_count == declared_count, (
        "Knowledge Hub guide counts differ: "
        f"hero={hero_count}, stat={stat_count}, declared={declared_count}"
    ))

    new_slug = "money-mule-or-victim-case-file"
    require(new_slug in relations, "new relation entry missing")
    for target in relations[new_slug]:
        require(target in relations and new_slug in relations[target], f"new relation is not reciprocal: {new_slug} -> {target}")
    expected_targets = {"money-mule-financial-crime-networks-handbook", "false-positive-playbook"}
    require(set(relations[new_slug]) == expected_targets, f"unexpected related slugs: {relations[new_slug]}")

    guide_claims = [item for item in ledger if item.get("guide") == GUIDE.name]
    require(len(guide_claims) > 0, "no ledger claims found for the Case File")
    require(all(item.get("status") == "verified" for item in guide_claims), "all Case File ledger claims must be verified")

    for label, text in ((GUIDE.name, html), (DATA_SCRIPT.name, data_script), (SCRIPT.name, script)):
        require("—" not in text, f"em dash found in {label}")
        require("–" not in text, f"en dash found in {label}")

    for phrase in PROGRESSIVE_DISCLOSURE_STRINGS:
        require(phrase in data_script, f"progressive disclosure phrase missing from data file: {phrase}")
        require(phrase not in html, f"progressive disclosure phrase leaked into static HTML: {phrase}")

    require("innerHTML" not in script, "page script must not inject HTML reasoning")

    # The page never calls gtag('event', <literal>) directly: it routes every
    # telemetry event through emitAggregateEvent(name, parameters), which is
    # the sole place that calls gtag('event', name, parameters). So the event
    # name contract is checked at the emitAggregateEvent call sites, and the
    # gtag call itself is checked for any literal event name that bypasses
    # that wrapper. Neither call site nests parentheses inside its own
    # argument list, so a non-greedy [^)]* match against each call is enough.
    wrapped_event_names = re.findall(r"emitAggregateEvent\(\s*'([^']+)'", script)
    require(len(wrapped_event_names) > 0, "no emitAggregateEvent call sites found")
    require(set(wrapped_event_names) <= ALLOWED_EVENT_NAMES, f"unexpected event name(s): {sorted(set(wrapped_event_names) - ALLOWED_EVENT_NAMES)}")
    direct_gtag_events = re.findall(r"gtag\(\s*'event'\s*,\s*'([^']+)'", script)
    require(set(direct_gtag_events) <= ALLOWED_EVENT_NAMES, f"unexpected literal event name reaching gtag directly: {direct_gtag_events}")

    require("fcr_cookie_consent_v2" in script, "telemetry consent key missing")
    require("consentGranted()" in script, "telemetry consent gate missing")

    gtag_calls = re.findall(r"gtag\([^)]*\)", script)
    emit_calls = re.findall(r"emitAggregateEvent\([^)]*\)", script)
    for call in gtag_calls + emit_calls:
        for forbidden in FORBIDDEN_TELEMETRY_KEYS:
            require(forbidden not in call, f"sensitive state key leaked into telemetry call: {forbidden} in {call!r}")

    require(
        "Case File | Default Knowledge Hub with investigative compositions | Experimental pending Experiment 02 evaluation" in guide_standard,
        "GUIDE_STANDARD.md is missing the Case File format-registry row",
    )
    require("### Experiment 02 Case File contract" in guide_standard, "GUIDE_STANDARD.md is missing the Experiment 02 Case File contract heading")

    print("OK: Money Mule or Victim Case File static contract passed")
    print(f"OK: {len(ids)} unique IDs, {len(guide_claims)} ledger claims, {len(wrapped_event_names)} telemetry event call sites")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration) as error:
        fail(str(error))
