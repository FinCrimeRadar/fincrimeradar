#!/usr/bin/env python3
"""Static release contract for the Recommendation 16 Intelligence Brief."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GUIDE_NAME = "fatf-recommendation-16-intelligence-brief.html"
GUIDE = ROOT / GUIDE_NAME
SCRIPT = ROOT / "js" / "fatf-recommendation-16-intelligence-brief.js"
CARD = ROOT / "fatf-recommendation-16-intelligence-brief-social-card.png"
SLUG = "fatf-recommendation-16-intelligence-brief"
CANONICAL = f"https://fincrimeradar.org/{GUIDE_NAME}"
CARD_URL = f"https://fincrimeradar.org/{SLUG}-social-card.png"
TITLE = "FATF Recommendation 16: The Payment Transparency Reset"
PAGE_DESCRIPTION = (
    "What revised FATF Recommendation 16 changes, what remains unsettled, "
    "and what payment and financial crime teams should prepare for before 2030."
)
SOCIAL_DESCRIPTION = (
    "How fraud, alignment and better data reshape payment chain control."
)
LOCKED_SUBTITLE = (
    "What changed, what remains unsettled, and what payment and financial crime "
    "teams should prepare for before 2030."
)
RELATED = {
    "crypto-travel-rule-sunrise-guide",
    "app-scam-decision-framework",
}
REQUIRED_SECTIONS = {
    "intelligence-status",
    "executive-assessment",
    "intelligence-timeline",
    "what-changed",
    "payment-chain-implications",
    "sanctions-clarification",
    "settled-versus-draft",
    "implementation-radar",
    "decision-horizon",
    "operational-preparation",
    "assessment-change",
    "worked-decisions",
    "risk-signals",
    "knowledge-check",
    "faq",
    "update-trigger",
    "sources",
    "related-intelligence",
}
ALLOWED_EVENTS = {
    "scenario_complete",
    "knowledge_check_complete",
    "card_export",
}


class KnowledgeCountParser(HTMLParser):
    """Mirror the Knowledge Hub count inputs from static markup."""

    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.count_text: dict[str, list[str]] = {
            "khHeroCount": [],
            "khStatGuides": [],
        }
        self.standalone = 0
        self.series = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        ancestors = {item_id for _, item_id in self.stack}
        if "khArticlesGrid" in ancestors and "kh-article-card" in classes:
            self.standalone += 1
        if "khFlagData" in ancestors and "kh-step-data" in classes:
            self.series += 1
        if tag not in self.VOID_ELEMENTS:
            self.stack.append((tag, attributes.get("id")))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for _, element_id in reversed(self.stack):
            if element_id in self.count_text:
                self.count_text[element_id].append(data)
                break


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text_only(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", without_tags).strip()


def main() -> None:
    for path in (GUIDE, SCRIPT, CARD):
        require(path.exists(), f"required file missing: {path.name}")

    html = GUIDE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    methodology = (ROOT / "methodology.html").read_text(encoding="utf-8")
    standard = (ROOT / "GUIDE_STANDARD.md").read_text(encoding="utf-8")
    relations = json.loads(
        (ROOT / "content-relations.json").read_text(encoding="utf-8")
    )
    ledger = json.loads(
        (ROOT / "verification-ledger.json").read_text(encoding="utf-8")
    )

    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicate_ids = sorted({item for item in ids if ids.count(item) > 1})
    require(not duplicate_ids, f"duplicate IDs: {duplicate_ids}")
    id_set = set(ids)
    require(
        'href="#main-content"' in html and 'id="main-content"' in html,
        "skip link target is missing",
    )
    require(html.count("<h1") == 1, "expected exactly one h1")
    heading_levels = [int(level) for level in re.findall(r"<h([1-6])\b", html)]
    for previous, current in zip(heading_levels, heading_levels[1:]):
        require(
            current <= previous + 1,
            f"heading order skips from h{previous} to h{current}",
        )
    section_ids = set(re.findall(r'<section\b[^>]*\bid="([^"]+)"', html))
    require(
        REQUIRED_SECTIONS <= section_ids,
        f"required sections missing: {sorted(REQUIRED_SECTIONS - section_ids)}",
    )
    for fragment in re.findall(r'href="#([^"]+)"', html):
        require(fragment in id_set, f"unresolved guide fragment: #{fragment}")

    require(
        f"<title>{TITLE} | FinCrimeRadar</title>" in html,
        "page title differs",
    )
    require(
        f'<meta name="description" content="{PAGE_DESCRIPTION}">' in html,
        "search description differs",
    )
    required_meta = (
        f'<link rel="canonical" href="{CANONICAL}">',
        f'<meta property="og:title" content="{TITLE}">',
        f'<meta property="og:description" content="{SOCIAL_DESCRIPTION}">',
        f'<meta property="og:url" content="{CANONICAL}">',
        f'<meta property="og:image" content="{CARD_URL}">',
        f'<meta name="twitter:title" content="{TITLE}">',
        f'<meta name="twitter:description" content="{SOCIAL_DESCRIPTION}">',
        f'<meta name="twitter:image" content="{CARD_URL}">',
        '<meta name="twitter:card" content="summary_large_image">',
    )
    for metadata in required_meta:
        require(html.count(metadata) == 1, f"metadata missing or duplicated: {metadata}")
    require(
        '<h1>FATF Recommendation 16:<br><em>The Payment Transparency Reset</em></h1>'
        in html,
        "visible title differs",
    )
    require(
        f'<p class="r16-hero-sub">{LOCKED_SUBTITLE}</p>' in html,
        "locked visible subtitle differs",
    )

    json_ld = re.findall(
        r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S
    )
    require(len(json_ld) == 2, "expected Article and BreadcrumbList JSON-LD")
    structured = [json.loads(block) for block in json_ld]
    article = next(
        (item for item in structured if item.get("@type") == "Article"), None
    )
    breadcrumbs = next(
        (item for item in structured if item.get("@type") == "BreadcrumbList"),
        None,
    )
    require(article is not None, "Article structured data missing")
    require(article.get("headline") == TITLE, "Article headline differs")
    require(article.get("description") == PAGE_DESCRIPTION, "Article description differs")
    require(article.get("image") == CARD_URL, "Article image differs")
    require(article.get("articleSection") == "Intelligence Brief", "Article section differs")
    require(
        article.get("mainEntityOfPage", {}).get("@id") == CANONICAL,
        "Article canonical differs",
    )
    require(
        article.get("datePublished") == "2026-09-13"
        and article.get("dateModified") == "2026-09-14",
        "Article dates differ",
    )
    require(
        breadcrumbs is not None
        and len(breadcrumbs.get("itemListElement", [])) == 3
        and breadcrumbs["itemListElement"][-1].get("item") == CANONICAL,
        "BreadcrumbList is incomplete",
    )

    evidence_states = {
        text_only(match).lower()
        for match in re.findall(r'<div class="r16-legend-label">(.*?)</div>', html, re.S)
    }
    require(
        evidence_states
        == {
            "settled standard",
            "draft guidance",
            "industry position",
            "fincrimeradar assessment",
        },
        f"evidence-state legend differs: {sorted(evidence_states)}",
    )
    require(html.count('<li><time datetime="') == 7, "timeline must contain seven events")
    require(html.count('<article class="r16-radar-card"') == 6, "Implementation Radar must contain six domains")
    require(html.count('<article class="r16-horizon">') == 3, "Decision Horizon must contain three horizons")
    require(html.count('<ul class="r16-preparation-list">') == 4, "operational preparation must contain four workstreams")
    require(
        "FATF final Recommendation 16 implementation guidance" in html
        and "Provisional on implementation mechanics, settled on adopted Recommendation 16 text" in html,
        "update trigger or assessment status is missing",
    )
    require(
        html.count("Evidence checked 14 September 2026") == 1
        and html.count("<dt>Evidence checked</dt><dd>14 September 2026</dd>") == 2
        and "<strong>Last reviewed:</strong> 14 September 2026" in html,
        "visible evidence review dates differ",
    )

    scenarios = re.findall(
        r'<article class="r16-scenario".*?</article>', html, re.S
    )
    require(len(scenarios) == 2, "expected two worked decisions")
    for index, scenario in enumerate(scenarios, start=1):
        require(scenario.count("<fieldset>") == 1, f"scenario {index} fieldset differs")
        require(scenario.count("<legend>") == 1, f"scenario {index} legend differs")
        options = re.findall(r'<input\b[^>]*type="radio"[^>]*>', scenario)
        require(len(options) == 3, f"scenario {index} must contain three options")
        require(
            sum('data-grade="best"' in option for option in options) == 1,
            f"scenario {index} must contain one strongest option",
        )
        require(
            'aria-live="polite" role="status"' in scenario,
            f"scenario {index} feedback semantics missing",
        )
        reasoning = re.search(
            r'<details class="r16-reasoning">(.*?)</details>', scenario, re.S
        )
        require(reasoning is not None, f"scenario {index} reasoning missing")
        for label in ("Source", "Application", "Action"):
            require(label in reasoning.group(1), f"scenario {index} missing {label}")

    patterns: dict[str, list[str]] = {}
    for match in re.finditer(
        r'<(?:aside|article) class="r16-pattern(?: r16-pattern-inline)?" '
        r'data-pattern-id="([^"]+)".*?</(?:aside|article)>',
        html,
        re.S,
    ):
        patterns.setdefault(match.group(1), []).append(text_only(match.group(0)))
    require(len(patterns) == 5, f"expected five pattern families, found {len(patterns)}")
    for pattern_id, copies in patterns.items():
        require(len(copies) == 2, f"{pattern_id} must appear twice")
        require(copies[0] == copies[1], f"{pattern_id} copies differ")

    knowledge_section = re.search(
        r'<section class="r16-section r16-quiz" id="knowledge-check".*?</section>',
        html,
        re.S,
    )
    require(knowledge_section is not None, "knowledge check missing")
    knowledge_html = knowledge_section.group(0)
    fieldsets = re.findall(r'<fieldset>(.*?)</fieldset>', knowledge_html, re.S)
    require(len(fieldsets) == 5, "knowledge check must contain five questions")
    for index, fieldset in enumerate(fieldsets, start=1):
        options = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fieldset)
        require(len(options) == 3, f"question {index} must contain three options")
        require(
            sum('data-correct="true"' in option for option in options) == 1,
            f"question {index} must contain one correct answer",
        )
    require(
        'id="r16KnowledgeFeedback" aria-live="polite" role="status"'
        in knowledge_html,
        "knowledge feedback semantics missing",
    )
    faq = re.search(
        r'<section class="r16-section r16-faq" id="faq".*?</section>',
        html,
        re.S,
    )
    require(faq is not None, "FAQ section missing")
    require(faq.group(0).count("<details>") == 5, "FAQ must contain five items")
    require(
        faq.group(0).count("<details>") == faq.group(0).count("<summary>"),
        "FAQ details and summary counts differ",
    )

    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited_ids = set(re.findall(r'href="#source-(\d+)"', html))
    require(source_ids == set(map(str, range(1, 9))), "expected sources 1 to 8")
    require(cited_ids == source_ids, "every source must be cited and resolved")
    source_urls = set(
        re.findall(r'<li id="source-\d+"><a href="([^"]+)"', html)
    )
    require(len(source_urls) == 8, "expected eight unique source URLs")
    require(not any("%0B" in item for item in source_urls), "malformed source URL remains")
    require("footnote 49" not in html, "stale sanctions footnote remains")
    require("footnote 60" not in html, "stale alignment footnote remains")
    require(html.count("footnote 51") == 3, "sanctions footnote references differ")
    require(html.count("footnote 62") == 1, "alignment footnote reference differs")

    claims = [item for item in ledger if item.get("guide") == GUIDE_NAME]
    require(len(claims) == 8, "expected eight guide ledger entries")
    require(
        all(item.get("status") == "verified" for item in claims),
        "all guide ledger entries must be verified",
    )
    require(
        all(item.get("verifiedOn") == "2026-09-14" for item in claims),
        "all guide ledger entries must record the final review date",
    )
    require(
        {item["source"]["url"] for item in claims} == source_urls,
        "ledger and public source URLs differ",
    )

    card_match = re.search(
        rf'<a href="/{re.escape(GUIDE_NAME)}".*?</a>', knowledge, re.S
    )
    require(card_match is not None, "Knowledge Hub card missing")
    card = card_match.group(0)
    require('data-date="2026-09-13"' in card, "Knowledge Hub date missing")
    require('kh-format-label">Intelligence Brief<' in card, "Knowledge Hub format differs")
    require(f'<div class="kh-item-title">{TITLE}</div>' in card, "Knowledge Hub title differs")
    require(
        "adopted payment transparency standard from draft guidance and industry positions"
        in card,
        "Knowledge Hub evidence distinction differs",
    )
    hub = KnowledgeCountParser()
    hub.feed(knowledge)
    declared_count = hub.standalone + hub.series
    for count_id in ("khHeroCount", "khStatGuides"):
        value = "".join(hub.count_text[count_id]).strip()
        require(
            value.isdigit() and int(value) == declared_count,
            f"{count_id} differs from {declared_count} declared guides",
        )

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_records = [
        node
        for node in sitemap.getroot().findall("s:url", namespace)
        if node.findtext("s:loc", namespaces=namespace) == CANONICAL
    ]
    require(len(sitemap_records) == 1, "sitemap canonical must appear once")
    require(
        sitemap_records[0].findtext("s:priority", namespaces=namespace) == "0.7",
        "sitemap priority differs",
    )

    require(set(relations.get(SLUG, [])) == RELATED, "content relation set differs")
    for target in RELATED:
        require(SLUG in relations.get(target, []), f"relation not reciprocal: {target}")
        target_html = (ROOT / f"{target}.html").read_text(encoding="utf-8")
        require(f'/{GUIDE_NAME}' in target_html, f"rendered backlink missing: {target}")
        require(f'/{target}.html' in html, f"related guide link missing: {target}")

    require(
        "Intelligence Brief | Default Knowledge Hub with temporal and comparison compositions | Accepted composition"
        in standard,
        "Guide Standard maturity differs",
    )
    require("### Intelligence Brief contract" in standard, "GUIDE_STANDARD.md is missing the Intelligence Brief contract heading")
    require(
        "Last updated: 13 September 2026" in methodology
        and f'href="/{GUIDE_NAME}"' in methodology,
        "methodology entry differs",
    )

    require("innerHTML" not in script, "page script must not inject HTML reasoning")
    event_names = re.findall(r"emitAggregateEvent\(\s*'([^']+)'", script)
    require(set(event_names) == ALLOWED_EVENTS, f"telemetry event set differs: {event_names}")
    require("fcr_cookie_consent_v2" in script, "telemetry consent key missing")
    require("consentGranted()" in script, "telemetry consent gate missing")
    for call in re.findall(r"(?:gtag|emitAggregateEvent)\([^)]*\)", script):
        for forbidden in (
            "customer_name",
            "account_number",
            "free_text",
            "selected_text",
            "rationale",
        ):
            require(forbidden not in call.lower(), f"sensitive telemetry field: {forbidden}")
    require(
        'id="r16ClosingPatterns"' in html and "r16ClosingPatterns" in script,
        "summary export is not sourced from the closing DOM",
    )
    require(
        'id="saveR16Status" aria-live="polite" role="status"' in html,
        "export status semantics missing",
    )

    with Image.open(CARD) as image:
        require(image.format == "PNG", "social card must be PNG")
        require(image.size == (1200, 630), "social card must be 1200 by 630")
        require(image.getbbox() is not None, "social card is blank")
    require(CARD.stat().st_size <= 400_000, "social card exceeds 400KB")

    for name, content in ((GUIDE.name, html), (SCRIPT.name, script)):
        require("—" not in content, f"em dash found in {name}")
        require("–" not in content, f"en dash found in {name}")
    require('class="card"' not in html and 'class="btn"' not in html, "generic experimental classes found")
    require("[class*=" not in html, "page CSS contains a broad substring selector")
    require("Experiment 03" not in html, "internal experiment label exposed in guide")
    require("Experiment 03" not in card, "internal experiment label exposed in Hub card")

    print("PASS: Recommendation 16 Intelligence Brief static release contract")
    print(
        f"OK: {len(ids)} IDs, 18 required sections, 2 scenarios, "
        f"5 pattern families, 5 questions, 8 sources and 8 ledger claims"
    )


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration, ET.ParseError) as error:
        fail(str(error))
