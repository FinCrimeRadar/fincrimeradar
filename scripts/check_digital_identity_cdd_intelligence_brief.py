#!/usr/bin/env python3
"""Static release contract for the Digital Identity CDD Intelligence Brief."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GUIDE_NAME = "digital-identity-cdd-intelligence-brief.html"
GUIDE = ROOT / GUIDE_NAME
SCRIPT = ROOT / "js" / "digital-identity-cdd-intelligence-brief.js"
CARD = ROOT / "digital-identity-cdd-intelligence-brief-social-card.png"
SLUG = "digital-identity-cdd-intelligence-brief"
CANONICAL = f"https://fincrimeradar.org/{GUIDE_NAME}"
CARD_URL = f"https://fincrimeradar.org/{SLUG}-social-card.png"
TITLE = "Digital Identity Is Not the Whole of CDD: What Verification Does and Does Not Prove"
DESCRIPTION = (
    "A practical proof-boundary method for using certified digital identity "
    "results without treating one check as complete customer due diligence."
)
STANDFIRST = (
    "A certified result can establish one identity proposition. It does not decide "
    "who owns a company, why the relationship exists, whether the customer is low "
    "risk or whether the evidence remains current."
)
SECTION_ORDER = [
    "intelligence-status",
    "how-to-read",
    "executive-assessment",
    "intelligence-timeline",
    "what-changed",
    "proof-boundary",
    "proof-record",
    "settled-versus-unresolved",
    "decision-horizon",
    "operational-implementation",
    "assessment-change",
    "worked-decisions",
    "risk-signals",
    "knowledge-check",
    "faq",
    "update-trigger",
    "sources",
    "related-intelligence",
]
RELATED = {"kyc-onboarding-dilemma", "perpetual-kyc-framework-guide"}
ALLOWED_EVENTS = {
    "scenario_complete",
    "knowledge_check_complete",
    "card_export",
}


class KnowledgeCountParser(HTMLParser):
    """Mirror Knowledge Hub declared-card counting."""

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
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))

    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    require(not duplicates, f"duplicate IDs: {duplicates}")
    id_set = set(ids)
    require('href="#main-content"' in html and 'id="main-content"' in html, "skip link target missing")
    require(html.count("<h1") == 1, "expected exactly one h1")
    headings = [int(level) for level in re.findall(r"<h([1-6])\b", html)]
    for previous, current in zip(headings, headings[1:]):
        require(current <= previous + 1, f"heading order skips from h{previous} to h{current}")
    section_ids = re.findall(r'<section\b[^>]*\bid="([^"]+)"', html)
    require(section_ids == SECTION_ORDER, f"section order differs: {section_ids}")
    for fragment in re.findall(r'href="#([^"]+)"', html):
        require(fragment in id_set, f"unresolved fragment: #{fragment}")

    require(f"<title>{TITLE} | FinCrimeRadar</title>" in html, "page title differs")
    require(f'<meta name="description" content="{DESCRIPTION}">' in html, "description differs")
    required_meta = (
        f'<link rel="canonical" href="{CANONICAL}">',
        '<meta property="og:title" content="Digital Identity Is Not the Whole of CDD">',
        f'<meta property="og:url" content="{CANONICAL}">',
        f'<meta property="og:image" content="{CARD_URL}">',
        '<meta property="article:modified_time" content="2026-10-06">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:image" content="{CARD_URL}">',
    )
    for metadata in required_meta:
        require(html.count(metadata) == 1, f"metadata missing or duplicated: {metadata}")
    require(STANDFIRST in html, "locked standfirst differs")
    require("A pass is not a customer verdict. It is a bounded evidence result." in html, "thesis missing")
    contract_pins = {
        "approved-guidance status": "published approved guidance for MLR compliance",
        "Regulation 76 without safe harbour": "Regulation 76 gives approved guidance relevance, but not a safe harbour",
        "qualified unregistered-service boundary": "cannot reliably be deemed suitable under that guidance. This is not presented as a universal statutory ban",
        "attribute separation": "An address attribute answers a different question. PEP and sanctions screening concern different propositions",
        "director boundary": "A director result does not prove the corporate customer, authority, ownership, control or beneficial ownership",
        "residual duties": "Every separate duty still open, including purpose, authority, corporate identity, ownership, beneficial ownership, EDD, monitoring and records where applicable",
        "relationship counterfactual": "The original identity result does not acquire a wider scope",
        "director counterfactual": "not because the director result changed scope",
        "certification transition": "scheme 1.0.1 as live from 2 September 2026",
        "FCA separate observations": "It separately said several firms distinguished standard CDD from EDD and most tailored CDD to customer risk",
    }
    for boundary, wording in contract_pins.items():
        require(wording in html, f"{boundary} wording missing")
    for overstatement in (
        "all unregistered services are prohibited",
        "all unregistered services are illegal",
        "every unregistered electronic verification service is prohibited",
    ):
        require(overstatement not in html.lower(), f"unregistered-service overstatement found: {overstatement}")

    json_ld = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    require(len(json_ld) == 2, "expected Article and BreadcrumbList JSON-LD")
    structured = [json.loads(block) for block in json_ld]
    article = next((item for item in structured if item.get("@type") == "Article"), None)
    breadcrumb = next((item for item in structured if item.get("@type") == "BreadcrumbList"), None)
    require(article is not None and article.get("headline") == TITLE, "Article headline differs")
    require(article.get("description") == DESCRIPTION, "Article description differs")
    require(article.get("image") == CARD_URL, "Article image differs")
    require(article.get("datePublished") == "2026-10-05", "Article date differs")
    require(article.get("dateModified") == "2026-10-06", "Article modification date differs")
    modified_meta = re.search(r'<meta property="article:modified_time" content="([^"]+)">', html)
    require(
        modified_meta is not None and modified_meta.group(1) == article.get("dateModified"),
        "Open Graph and Article modification dates differ",
    )
    require(article.get("mainEntityOfPage", {}).get("@id") == CANONICAL, "Article canonical differs")
    require(breadcrumb is not None and breadcrumb["itemListElement"][-1]["item"] == CANONICAL, "breadcrumb differs")

    evidence_states = {
        text_only(item).lower()
        for item in re.findall(r'<div class="dicdd-legend-label">(.*?)</div>', html, re.S)
    }
    require(evidence_states == {"established", "unresolved", "fincrimeradar assessment"}, f"evidence states differ: {evidence_states}")
    require(html.count('<li><time datetime="') == 4, "timeline must contain four events")
    record_section = re.search(r'<section[^>]+id="proof-record".*?</section>', html, re.S)
    require(record_section is not None, "Proof Boundary Record section missing")
    record_labels = re.findall(r'<h3>(\d\. [^<]+)</h3>', record_section.group(0))
    require(record_labels == [
        "1. Subject", "2. Proposition", "3. Service scope", "4. Assurance",
        "5. Residual duties", "6. Change trigger",
    ], f"Proof Boundary Record order differs: {record_labels}")
    require(html.count('<article class="dicdd-horizon">') == 3, "Decision Horizon must contain three horizons")
    operational = re.search(r'<section[^>]+id="operational-implementation".*?</section>', html, re.S)
    require(operational is not None and operational.group(0).count("<article>") == 5, "operational workstreams differ")
    assessment = re.search(r'<section[^>]+id="assessment-change".*?</section>', html, re.S)
    require(assessment is not None and assessment.group(0).count("<li>") == 6, "assessment triggers differ")
    require(html.count("Evidence checked 6 October 2026") == 1, "hero evidence date differs")
    require(html.count("<dt>Evidence checked</dt><dd>6 October 2026</dd>") == 2, "status evidence dates differ")
    require("<strong>Last reviewed:</strong> 6 October 2026" in html, "last-reviewed date missing")

    scenarios = re.findall(r'<article class="dicdd-scenario".*?</article>', html, re.S)
    require(len(scenarios) == 2, "expected two worked decisions")
    expected_ids = {"verified_identity_unresolved_relationship", "verified_director_unresolved_company"}
    found_ids: set[str] = set()
    for index, scenario in enumerate(scenarios, start=1):
        scenario_id = re.search(r'data-scenario-id="([^"]+)"', scenario)
        require(scenario_id is not None, f"scenario {index} ID missing")
        found_ids.add(scenario_id.group(1))
        options = re.findall(r'<input\b[^>]*type="radio"[^>]*>', scenario)
        require(len(options) == 3, f"scenario {index} must contain three options")
        for grade in ("weak", "caution", "best"):
            require(sum(f'data-grade="{grade}"' in item for item in options) == 1, f"scenario {index} grade {grade} differs")
        require('aria-live="polite" role="status"' in scenario, f"scenario {index} status semantics missing")
        reasoning = re.search(r'<details class="dicdd-reasoning">(.*?)</details>', scenario, re.S)
        require(reasoning is not None, f"scenario {index} reasoning missing")
        for label in ("Source", "Application", "Action", "Counterfactual"):
            require(label in reasoning.group(1), f"scenario {index} missing {label}")
    require(found_ids == expected_ids, f"scenario IDs differ: {found_ids}")

    patterns: dict[str, list[str]] = {}
    for match in re.finditer(
        r'<(?:aside|article) class="dicdd-pattern(?: dicdd-pattern-inline)?" '
        r'data-pattern-id="([^"]+)".*?</(?:aside|article)>',
        html,
        re.S,
    ):
        patterns.setdefault(match.group(1), []).append(text_only(match.group(0)))
    require(len(patterns) == 5, f"expected five pattern families, found {len(patterns)}")
    for pattern_id, copies in patterns.items():
        require(len(copies) == 2, f"{pattern_id} must appear twice")
        require(copies[0] == copies[1], f"{pattern_id} copies differ")

    knowledge_section = re.search(r'<section class="dicdd-section dicdd-quiz" id="knowledge-check".*?</section>', html, re.S)
    require(knowledge_section is not None, "knowledge check missing")
    fieldsets = re.findall(r'<fieldset>(.*?)</fieldset>', knowledge_section.group(0), re.S)
    require(len(fieldsets) == 5, "knowledge check must contain five questions")
    correct_order: list[str] = []
    for index, fieldset in enumerate(fieldsets, start=1):
        options = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fieldset)
        require(len(options) == 3, f"question {index} must contain three options")
        correct = [item for item in options if 'data-correct="true"' in item]
        require(len(correct) == 1, f"question {index} must contain one correct answer")
        value = re.search(r'value="([abc])"', correct[0])
        require(value is not None, f"question {index} correct value missing")
        correct_order.append(value.group(1).upper())
    require(correct_order == ["B", "C", "A", "B", "C"], f"answer order differs: {correct_order}")
    require('id="dicddKnowledgeFeedback" aria-live="polite" role="status"' in knowledge_section.group(0), "knowledge status semantics missing")
    faq = re.search(r'<section class="dicdd-section dicdd-faq" id="faq".*?</section>', html, re.S)
    require(faq is not None and faq.group(0).count("<details>") == 6, "FAQ must contain six items")
    require(faq.group(0).count("<details>") == faq.group(0).count("<summary>"), "FAQ semantics differ")

    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited_ids = set(re.findall(r'href="#source-(\d+)"', html))
    require(source_ids == set(map(str, range(1, 10))), "expected sources 1 to 9")
    require(cited_ids == source_ids, "every source must be cited")
    source_urls = set(re.findall(r'<li id="source-\d+">(.*?)</li>', html, re.S))
    public_urls = set(re.findall(r'href="(https://[^"]+)"', " ".join(source_urls)))
    require(len(public_urls) == 10, f"expected ten unique public source URLs, found {len(public_urls)}")

    claims = [item for item in ledger if item.get("guide") == GUIDE_NAME]
    require(len(claims) == 13, f"expected thirteen ledger claims, found {len(claims)}")
    require(all(item.get("status") == "verified" for item in claims), "ledger claims must be verified")
    verification_dates = [item.get("verifiedOn") for item in claims]
    require(set(verification_dates) == {"2026-10-05", "2026-10-06"}, "ledger verification date set differs")
    require(verification_dates.count("2026-10-06") == 2, "expected two remediation-date ledger claims")
    claim_ids = {item.get("claimId") for item in claims}
    require("digital-identity-cdd.guidance-approved-status.012" in claim_ids, "approved-guidance ledger claim missing")
    require("digital-identity-cdd.certification-scheme-live-transition.013" in claim_ids, "certification transition ledger claim missing")
    ledger_urls = {item["source"]["url"] for item in claims}
    require(ledger_urls <= public_urls, "ledger source URL absent from public sources")

    card_match = re.search(rf'<a href="/{re.escape(GUIDE_NAME)}".*?</a>', knowledge, re.S)
    require(card_match is not None, "Knowledge Hub card missing")
    card = card_match.group(0)
    require('data-date="2026-10-05"' in card, "Knowledge Hub date differs")
    require('kh-format-label">Intelligence Brief<' in card, "Knowledge Hub format differs")
    require(f'<div class="kh-item-title">{TITLE}</div>' in card, "Knowledge Hub title differs")
    require("proof-boundary method" in card, "Knowledge Hub proof-boundary summary missing")
    hub = KnowledgeCountParser()
    hub.feed(knowledge)
    declared_count = hub.standalone + hub.series
    for count_id in ("khHeroCount", "khStatGuides"):
        value = "".join(hub.count_text[count_id]).strip()
        require(value.isdigit() and int(value) == declared_count, f"{count_id} differs from {declared_count}")

    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    records = [
        node for node in sitemap.getroot().findall("s:url", namespace)
        if node.findtext("s:loc", namespaces=namespace) == CANONICAL
    ]
    require(len(records) == 1, "sitemap canonical must appear once")
    require(records[0].findtext("s:priority", namespaces=namespace) == "0.7", "sitemap priority differs")

    require(set(relations.get(SLUG, [])) == RELATED, "content relation set differs")
    for target in RELATED:
        require(SLUG in relations.get(target, []), f"relation not reciprocal: {target}")
        target_html = (ROOT / f"{target}.html").read_text(encoding="utf-8")
        require(f'/{GUIDE_NAME}' in target_html, f"rendered backlink missing: {target}")
        require(f'/{target}.html' in html, f"related link missing: {target}")

    require("innerHTML" not in script, "script must not inject HTML reasoning")
    events = re.findall(r"emitAggregateEvent\(\s*'([^']+)'", script)
    require(set(events) == ALLOWED_EVENTS, f"telemetry event set differs: {events}")
    require("fcr_cookie_consent_v2" in script and "consentGranted()" in script, "telemetry consent gate missing")
    for forbidden in ("customer_name", "account_number", "free_text", "selected_text", "rationale"):
        require(forbidden not in script.lower(), f"sensitive telemetry field found: {forbidden}")
    require('id="dicddClosingPatterns"' in html and "dicddClosingPatterns" in script, "closing-DOM export missing")
    require('id="saveDicddStatus" aria-live="polite" role="status"' in html, "export status semantics missing")

    with Image.open(CARD) as image:
        require(image.format == "PNG", "social card must be PNG")
        require(image.size == (1200, 630), "social card must be 1200 by 630")
        require(image.getbbox() is not None, "social card is blank")
    require(CARD.stat().st_size <= 400_000, "social card exceeds 400KB")

    for name, content in ((GUIDE.name, html), (SCRIPT.name, script)):
        require("—" not in content, f"em dash found in {name}")
        require("–" not in content, f"en dash found in {name}")
        require("r16" not in content, f"stale r16 namespace found in {name}")
    require('class="card"' not in html and 'class="btn"' not in html, "generic experimental classes found")
    require("FATF Recommendation 16" not in html, "stale template copy remains")
    require("Experiment" not in html, "internal experiment label exposed")

    print("PASS: Digital Identity CDD Intelligence Brief static release contract")
    print(
        f"OK: {len(ids)} IDs, 18 sections, 2 scenarios, 5 pattern families, "
        f"5 questions, 6 FAQs, 9 source records and 13 ledger claims"
    )


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration, ET.ParseError) as error:
        fail(str(error))
