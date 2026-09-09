#!/usr/bin/env python3
"""Narrow static contract checks for Experiment 01 only."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "app-scam-decision-framework.html"
SCRIPT = ROOT / "js" / "app-scam-decision-framework.js"
METHODOLOGY_UPDATE_DATE = "8 September 2026"


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


def text_only(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def main() -> None:
    html = GUIDE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    methodology = (ROOT / "methodology.html").read_text(encoding="utf-8")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))

    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    require(not duplicates, f"duplicate IDs: {duplicates}")
    require('href="#main-content"' in html and 'id="main-content"' in html, "skip link target is missing")
    require(html.count("<h1") == 1, "expected exactly one h1")
    require("Evidence reviewed</dt>" in html and "Last reviewed</dt>" in html, "evidence and last-reviewed dates must both be visible")

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
    require(breadcrumbs is not None and len(breadcrumbs.get("itemListElement", [])) == 3, "BreadcrumbList is incomplete")

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)"', html)
    require(canonical and og_url and canonical.group(1) == og_url.group(1), "canonical and Open Graph URL differ")
    require(canonical.group(1) in sitemap, "canonical URL missing from sitemap")
    require('/app-scam-decision-framework.html' in knowledge, "Knowledge Hub card missing")
    require('kh-format-label">Framework<' in knowledge, "visible Framework label missing from Knowledge Hub card")

    knowledge_counts = KnowledgeCountParser()
    knowledge_counts.feed(knowledge)
    declared_count = knowledge_counts.standalone_guides + knowledge_counts.series_guides
    hero_count = knowledge_counts.count_text("khHeroCount")
    stat_count = knowledge_counts.count_text("khStatGuides")
    require(hero_count == stat_count == declared_count, (
        "Knowledge Hub guide counts differ: "
        f"hero={hero_count}, stat={stat_count}, declared={declared_count}"
    ))

    expected_update = f"Last updated: {METHODOLOGY_UPDATE_DATE}"
    require(methodology.count(expected_update) == 1, "methodology Experiment 01 update date is missing or duplicated")
    require("Last updated: 12 July 2026" not in methodology, "stale methodology update date remains")
    metadata_dates = re.findall(r'"dateModified"\s*:\s*"([^"]+)"', methodology)
    require(not metadata_dates or metadata_dates == ["2026-09-08"], "methodology dateModified metadata is out of sync")
    require(re.search(r'<span class="fcr-format">\s*Framework\s*</span>', html) is not None,
            "public Framework label is missing or exposes internal experiment numbering")
    for public_name, public_html in ((GUIDE.name, html), ("knowledge.html", knowledge), ("methodology.html", methodology)):
        require("Experiment 01" not in public_html, f"internal experiment numbering exposed in {public_name}")

    scenarios: dict[str, str] = {}
    for scenario_id in ("one", "two"):
        match = re.search(rf'<section class="fcr-section" id="scenario-{scenario_id}"[^>]*>(.*?)</section>', html, re.S)
        require(match is not None, f"scenario {scenario_id} section missing")
        scenarios[scenario_id] = match.group(1)
    require(len(re.findall(r'<section class="fcr-section" id="scenario-(?:one|two)"', html)) == 2, "expected two materially distinct scenario sections")

    decision_contracts = {
        "one": ("contractor", "contractor-decision"),
        "two": ("warning", "warning-decision"),
    }
    for scenario_id, scenario in scenarios.items():
        number = 1 if scenario_id == "one" else 2
        for label in ("Source", "Application", "Action", "What Would Change My Decision?"):
            require(label in scenario, f"scenario {number} missing {label}")
        scenario_key, radio_name = decision_contracts[scenario_id]
        form = re.search(rf'<form class="fcr-choice" data-decision-form data-scenario-id="{scenario_key}">(.*?)</form>', scenario, re.S)
        require(form is not None, f"scenario {number} decision form is missing or misplaced")
        form_html = form.group(1)
        require(form_html.count("<fieldset>") == 1 and form_html.count("<legend>") == 1, f"scenario {number} decision is not one native fieldset")
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', form_html)
        require(len(radios) == 4, f"scenario {number} must contain four decision options")
        require(all(f'name="{radio_name}"' in radio for radio in radios), f"scenario {number} radio group is inconsistent")
        require(sum('data-grade="best"' in radio for radio in radios) == 1, f"scenario {number} must contain one best-reasoned option")
        require('class="fcr-feedback" aria-live="polite" role="status"' in form_html, f"scenario {number} feedback is not a polite status")

        record = re.search(r'<div class="fcr-record"[^>]*>(.*?)</div>', scenario, re.S)
        require(record is not None, f"scenario {number} Decision Record is missing or misplaced")
        record_html = record.group(1)
        require("<dl>" in record_html and "</dl>" in record_html, f"scenario {number} Decision Record is not semantic")
        for field in ("Facts", "Assumptions", "Indicators", "Mitigants", "Decision", "Rationale"):
            require(re.search(rf'<dt[^>]*>{field}</dt>', record_html) is not None, f"scenario {number} Decision Record field missing: {field}")

    faq = re.search(r'<section class="fcr-section fcr-details" id="faq">(.*?)</section>', html, re.S)
    require(faq is not None and faq.group(1).count("<details>") >= 5, "FAQ native details structure incomplete")
    require(faq.group(1).count("<details>") == faq.group(1).count("<summary>"), "FAQ details and summary counts differ")

    patterns: dict[str, list[str]] = {}
    for match in re.finditer(r'<div class="fcr-pattern" data-pattern-id="([^"]+)">(.*?)</dl>\s*</div>', html, re.S):
        patterns.setdefault(match.group(1), []).append(text_only(match.group(2)))
    require(len(patterns) == 5, f"expected five Risk/Signal/Response patterns, found {len(patterns)}")
    for pattern_id, copies in patterns.items():
        require(len(copies) == 2, f"{pattern_id} must appear inline and in closing grid")
        require(copies[0] == copies[1], f"{pattern_id} inline and closing copies differ")

    knowledge = re.search(r'<section class="fcr-section fcr-quiz" id="knowledge-check">(.*?)</section>', html, re.S)
    require(knowledge is not None, "knowledge check section missing")
    knowledge_html = knowledge.group(1)
    require('id="knowledgeForm"' in knowledge_html, "knowledge form is missing or misplaced")
    knowledge_fieldsets = re.findall(r'<fieldset>(.*?)</fieldset>', knowledge_html, re.S)
    require(len(knowledge_fieldsets) == 5, "knowledge check must contain five fieldsets")
    for number, fieldset in enumerate(knowledge_fieldsets, start=1):
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fieldset)
        require(len(radios) == 3, f"knowledge question {number} must contain three options")
        require(sum('data-correct="true"' in radio for radio in radios) == 1, f"knowledge question {number} must contain one correct option")
    require(html.count('data-correct="true"') == knowledge_html.count('data-correct="true"'), "correct-answer markers must remain inside the knowledge check")
    require('id="knowledgeFeedback"' in knowledge_html and 'aria-live="polite" role="status"' in knowledge_html, "knowledge feedback is not a polite status")
    require('id="saveFrameworkStatus" aria-live="polite" role="status"' in html, "export feedback is not a polite status")
    require('id="fcrClosingPatterns"' in html and "fcrClosingPatterns" in script, "export is not sourced from closing DOM")
    require("innerHTML" not in script, "page script must not inject HTML reasoning")
    for phrase in ("£85,000", "civil dispute guidance", "gross negligence threshold", "Nominal Performance Trap"):
        require(phrase not in script, f"material reasoning leaked into JavaScript: {phrase}")

    require("fcr_cookie_consent_v2" in script and "consentGranted()" in script, "telemetry consent gate missing")
    for forbidden in ("customer_name", "account_number", "free_text", "Decision Record", "record-heading"):
        require(forbidden not in script, f"sensitive Decision Record telemetry risk: {forbidden}")

    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited_ids = set(re.findall(r'href="#source-(\d+)"', html))
    require(cited_ids <= source_ids, f"undefined source references: {sorted(cited_ids - source_ids)}")
    require(source_ids == set(map(str, range(1, 14))), "expected source records 1 to 13")

    guide_claims = [item for item in ledger if item.get("guide") == GUIDE.name]
    require(len(guide_claims) == 13, f"expected 13 ledger claims, found {len(guide_claims)}")
    require(all(item.get("status") == "verified" for item in guide_claims), "all Experiment 01 ledger claims must be verified")

    new_slug = "app-scam-decision-framework"
    require(new_slug in relations, "new relation entry missing")
    for target in relations[new_slug]:
        require(target in relations and new_slug in relations[target], f"new relation is not reciprocal: {new_slug} -> {target}")

    require("class=\"card\"" not in html and "class=\"btn\"" not in html, "experimental classes must remain namespaced")
    require("[class*=" not in html, "page-local CSS must not add broad substring selectors")

    print("OK: Experiment 01 static contract passed")
    print(f"OK: {len(ids)} unique IDs, 2 scenarios, 5 patterns in two placements, 13 ledger claims")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration) as error:
        fail(str(error))
