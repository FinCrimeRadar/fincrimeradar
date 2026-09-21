#!/usr/bin/env python3
"""Static contract checks for The De-Risking Judgement Call (second Framework implementation)."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "de-risking-judgement-call"
GUIDE = ROOT / f"{SLUG}.html"
SCRIPT = ROOT / "js" / f"{SLUG}.js"
CLAIM_PREFIX = f"{SLUG}."
GRADES = {"best", "reading", "incomplete", "unsupported", "unsupported-facts"}


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


def section(html: str, section_id: str) -> str:
    match = re.search(rf'<section class="fcr-section"[^>]*id="{section_id}"[^>]*>(.*?)</section>', html, re.S)
    require(match is not None, f"section {section_id} is missing")
    return match.group(1)


def main() -> None:
    html = GUIDE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))

    # ---- structure and metadata
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
    require((ROOT / f"{SLUG}-social-card.png").exists(), "social card PNG is missing")
    require(f"/{SLUG}.html" in knowledge, "Knowledge Hub card missing")
    require(re.search(rf'href="/{SLUG}.html"[^>]*data-date="\d{{4}}-\d{{2}}-\d{{2}}"', knowledge) is not None, "Knowledge Hub card has no data-date")
    require(re.search(rf'href="/{SLUG}.html".*?kh-format-label">Framework<', knowledge, re.S) is not None, "visible Framework label missing from Knowledge Hub card")
    require(re.search(r'<span class="fcr-format">\s*Framework\s*</span>', html) is not None, "public Framework label is missing")
    require("Experiment" not in html, "internal experiment numbering exposed in the guide")

    counts = KnowledgeCountParser()
    counts.feed(knowledge)
    declared = counts.standalone_guides + counts.series_guides
    hero_count = counts.count_text("khHeroCount")
    stat_count = counts.count_text("khStatGuides")
    require(hero_count == stat_count == declared, f"Knowledge Hub guide counts differ: hero={hero_count}, stat={stat_count}, declared={declared}")

    # ---- scenarios: three decisions, graded, each option with Source, Application, Recommendation
    scenario_ids = {"scenario-one": "respondent", "scenario-two-a": "ownership", "scenario-two-b": "residual"}
    best_positions: list[int] = []
    for sid, key in scenario_ids.items():
        body = section(html, sid)
        form = re.search(rf'<form class="fcr-choice" data-decision-form data-scenario-id="{key}" method="dialog">(.*?)</form>', body, re.S)
        require(form is not None, f"{sid} decision form missing")
        form_html = form.group(1)
        require(form_html.count("<fieldset>") == 1 and form_html.count("<legend>") == 1, f"{sid} decision is not one native fieldset")
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', form_html)
        require(len(radios) == 4, f"{sid} must contain four decision options")
        require(all(f'name="{key}-decision"' in radio for radio in radios), f"{sid} radio group inconsistent")
        grades = [re.search(r'data-grade="([^"]+)"', radio).group(1) for radio in radios]
        require(set(grades) <= GRADES, f"{sid} has an unknown grade: {grades}")
        require(grades.count("best") == 1, f"{sid} must contain exactly one best-supported option")
        option_texts = [text_only(t) for t in re.findall(r'<span>(.*?)</span>', form_html, re.S)]
        best_index = grades.index("best")
        best_positions.append(best_index)
        require(len(option_texts[best_index]) < max(len(t) for t in option_texts), f"{sid} best option must not be the longest")
        require(all('data-grade-label="' in radio for radio in radios), f"{sid} grade labels missing")
        require('class="fcr-feedback" aria-live="polite" role="status"' in form_html, f"{sid} feedback is not a polite status")
        values = re.findall(r'value="([^"]+)"', " ".join(radios))
        blocks = re.findall(r'<div class="fcr-optfb" id="optfb-[^"]+" data-option="([^"]+)" data-grade="([^"]+)">(.*?)</div>\s*</div>', body, re.S)
        require(sorted(v for v, _, _ in blocks) == sorted(values), f"{sid} option analysis blocks do not match options")
        for value, grade, inner in blocks:
            for label in ("Source", "Application", "Recommendation"):
                match = re.search(rf'<h3>{label}</h3><p>(.*?)</p>', inner, re.S)
                require(match is not None and len(text_only(match.group(1))) > 40, f"{sid}/{value} missing substantive {label}")
        require("What Would Change My Decision?" in body, f"{sid} missing What Would Change My Decision")
        require("Counterfactual" in body, f"{sid} missing counterfactual")
        record = re.search(r'<div class="fcr-record"[^>]*>(.*?)</div>', body, re.S)
        require(record is not None and "<dl>" in record.group(1), f"{sid} Decision Record missing or not semantic")
        for field in ("Facts", "Assumptions", "Indicators", "Mitigants", "Decision", "Rationale"):
            require(re.search(rf'<dt[^>]*>{field}</dt>', record.group(1)) is not None, f"{sid} Decision Record field missing: {field}")
    require(len(re.findall(r"data-decision-form", html)) == 3, "expected exactly three decision forms")
    require(best_positions.count(3) <= 1 and len(set(best_positions)) >= 2, f"best option position is too predictable: {best_positions}")

    # ---- open points
    open_block = section(html, "open-points")
    cards = re.findall(r'<article class="fcr-open" id="([^"]+)">(.*?)</article>', open_block, re.S)
    require(len(cards) == 5, f"expected five open-point cards, found {len(cards)}")
    for card_id, card in cards:
        require('data-state="unknown"' in card, f"{card_id} is not labelled Unknown")
        require(card.count("<h4>") == 2, f"{card_id} must state both readings")
        require("What both readings agree" in card and "Where they diverge" in card, f"{card_id} missing agree or diverge text")
        require("must decide with legal advice and record why" in card, f"{card_id} missing decision instruction")

    # ---- patterns, quiz, faq, export
    faq = re.search(r'<section class="fcr-section fcr-details" id="faq">(.*?)</section>', html, re.S)
    require(faq is not None and faq.group(1).count("<details>") >= 5, "FAQ native details structure incomplete")
    require(faq.group(1).count("<details>") == faq.group(1).count("<summary>"), "FAQ details and summary counts differ")

    patterns: dict[str, list[str]] = {}
    for match in re.finditer(r'<div class="fcr-pattern" data-pattern-id="([^"]+)">(.*?)</dl>\s*</div>', html, re.S):
        patterns.setdefault(match.group(1), []).append(text_only(match.group(2)))
    require(len(patterns) == 5, f"expected five Risk/Signal/Response patterns, found {len(patterns)}")
    for pattern_id, copies in patterns.items():
        require(len(copies) == 2, f"{pattern_id} must appear inline and in the closing grid")
        require(copies[0] == copies[1], f"{pattern_id} inline and closing copies differ")

    quiz = re.search(r'<section class="fcr-section fcr-quiz" id="knowledge-check">(.*?)</section>', html, re.S)
    require(quiz is not None, "knowledge check section missing")
    quiz_html = quiz.group(1)
    fieldsets = re.findall(r'<fieldset>(.*?)</fieldset>', quiz_html, re.S)
    require(len(fieldsets) == 5, "knowledge check must contain five fieldsets")
    for number, fieldset in enumerate(fieldsets, start=1):
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fieldset)
        require(len(radios) == 3, f"knowledge question {number} must contain three options")
        require(sum('data-correct="true"' in radio for radio in radios) == 1, f"knowledge question {number} must contain one correct option")
    require(html.count('data-correct="true"') == quiz_html.count('data-correct="true"'), "correct-answer markers must stay inside the knowledge check")
    positions = []
    longest = 0
    for fieldset in fieldsets:
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fieldset)
        positions.append(next(i for i, radio in enumerate(radios) if 'data-correct="true"' in radio))
        lengths = [len(text_only(t)) for t in re.findall(r'<span>(.*?)</span>', fieldset, re.S)]
        longest += lengths[positions[-1]] == max(lengths)
    require(max(positions.count(i) for i in range(3)) <= 2, f"correct answer position is too predictable: {positions}")
    require(longest <= 2, f"the correct answer is the longest option in {longest} of 5 questions")
    require('id="knowledgeFeedback"' in quiz_html and 'aria-live="polite" role="status"' in quiz_html, "knowledge feedback is not a polite status")
    require("Answer notes" in quiz_html and quiz_html.count("<em>Source:</em>") == 5, "answer notes must separate Source, Application and Recommendation for each question")
    require('id="saveFrameworkStatus" aria-live="polite" role="status"' in html, "export feedback is not a polite status")
    require('id="fcrClosingPatterns"' in html and "fcrClosingPatterns" in script, "export is not sourced from the closing DOM")

    # ---- external review contract (wording that must not regress)
    require('data-scenario-id="ownership"' in html, "ownership decision missing")
    ownership = section(html, "scenario-two-a")
    wait = re.search(r'value="wait" data-grade="([^"]+)" data-grade-label="([^"]+)"', ownership)
    require(wait is not None and wait.group(1) == "unsupported-facts" and wait.group(2) == "Not supported on the stated facts", "the wait option must be graded Not supported on the stated facts")
    require(re.search(r'<span class="fcr-grade" data-grade="unsupported-facts">Not supported on the stated facts</span>', ownership) is not None, "the wait analysis badge must read Not supported on the stated facts")
    visible = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
    plain = text_only(visible)
    for banned in ("Stop new transactions", "stop new transactions", "turn on purpose", "and nothing else", "no verdict in this guide rests", "No verdict rests", "cannot rest on either reading", "not a lawful ground", "never as a lawful ground"):
        require(banned not in plain, f"superseded wording is still present: {banned}")
    require("“Correspondent relationship”" not in plain, "a quoted defined term must keep its lower-case initial")
    require("sections 333D(3) and 21G(3)" in plain and "333D(1)(b) or 21G(1)(b)" in plain, "both offence exceptions must be stated in the exit section")
    require("subject to 51D(2)" in plain and "without delay" in plain, "51D must be described as substituting notice without delay, subject to 51D(2)")
    for chunk in re.split(r"</(?:p|dd|li)>", visible):
        chunk_text = text_only(chunk)
        if "51C(a)" in chunk_text:
            require("regulation 27" in chunk_text, f"51C(a) is applied without stating the regulation 27 condition: {chunk_text[:120]}")
    require("regulation 27(8)" in text_only(section(html, "scenario-two-a")), "the branch a facts must state the regulation 27 occasion")
    require(re.search(r"51B conditions are met[^.]*\.", plain) is None or "Whether the 51B conditions are met depends on Part 6 applying under regulation 40(1)" in plain, "the charity 51B conclusion must be conditional")
    require("regulation 34(2) or 34(3) does not require non-continuation" in plain, "the urgent exit sentence must carry the 34(2) and 34(3) scope")
    require(plain.count("Recommendation 13") >= 3 and "the refuse or terminate consequence in Recommendation 10 is not engaged" in plain, "R.10 must be confined to complete due diligence, with R.13 separate")

    # ---- progressive enhancement and interaction contract
    require('<form' in html and 'action="' not in " ".join(re.findall(r"<form\b[^>]*>", html)), "forms must not carry an action attribute")
    require(all('method="dialog"' in tag for tag in re.findall(r"<form\b[^>]*>", html)), "every form must use method=dialog so a pre-script submit cannot navigate or leak a selection into the URL")
    require(".js .fcr-optfb-set:not([data-revealed=\"true\"]){display:none}" in html, "option analyses must be hidden only when the js class is set")
    require(".fcr-choice .fcr-action,#knowledgeForm .fcr-action,#saveFrameworkImage{display:none}" in html and ".js .fcr-choice .fcr-action" in html, "action buttons must be hidden until the js class is set")
    require(re.search(r'<div class="fcr-optfb-set"[^>]*aria-label=', html) is None, "aria-label must not sit on a generic div")
    require(len(re.findall(r'<div class="fcr-optfb-set"[^>]* role="group" aria-labelledby="optfb-title-\w+"', html)) == 3, "option analysis sets need role=group and a label")
    require(html.count('id="optfb-') >= 12, "each option analysis needs an id for the feedback link")
    require("classList.add('js')" in script and script.count("event.preventDefault()") >= 2, "script must set the js class and prevent default on submit")
    require(script.rindex("classList.add('js')") > script.rindex("addEventListener("), "the js class must be set after every handler is attached")
    require(".fcr-optfb{scroll-margin-top:120px}" in html, "analysis blocks need a scroll margin so the feedback link clears the sticky nav")
    require("sentEvents" in script and "try {" in script and "setTimeout(function () { URL.revokeObjectURL" in script, "telemetry once-only, gtag guard or delayed revoke missing")
    require("addEventListener('change'" in script, "change handler that clears stale feedback is missing")
    require("javascript:" not in html and "javascript:" not in script, "no javascript: URLs")

    # ---- script discipline
    require("innerHTML" not in script, "page script must not inject HTML reasoning")
    for phrase in ("regulation", "51B", "FATF", "reg 31", "Increased Monitoring", "Call for Action", "shell bank"):
        require(phrase not in script, f"material reasoning leaked into JavaScript: {phrase}")
    require("fcr_cookie_consent_v2" in script and "consentGranted()" in script, "telemetry consent gate missing")
    for forbidden in ("customer_name", "account_number", "free_text", "Decision Record", "record-heading"):
        require(forbidden not in script, f"sensitive telemetry risk: {forbidden}")
    require(re.search(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\s+stages?\b", html, re.I) is None, "the working sequence must not hard-code a stage count in copy")
    require("stages.length" not in script and "stage" not in script.lower(), "the script must not encode the stage sequence")

    # ---- sources
    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited_ids = set(re.findall(r'href="#source-(\d+)"', html))
    require(cited_ids <= source_ids, f"undefined source references: {sorted(cited_ids - source_ids)}")
    require(source_ids <= cited_ids, f"source records never cited: {sorted(source_ids - cited_ids)}")

    # ---- editorial constraints
    require(not re.search("[–—]", html), "em or en dash found in the guide")
    require(not re.search("[–—]", script), "em or en dash found in the script")
    main_text = text_only(re.search(r'<main id="main-content".*?</main>', html, re.S).group(0))
    require(re.search(r"\bReading\s+(?:A|B|1|2)\b", main_text) is None, "Reading A/B or 1/2 label found in prose")
    require("PRIN" not in main_text, "PRIN 2A must stay out of the guide verdicts and prose")
    require(re.search(r"FCTR[^.]{0,120}last updated", main_text, re.I) is None, "FCTR must be cited by paragraph with no last-updated date")
    require(re.search(r"(€|EUR|turnover|balance sheet|fewer than \d+|\d+ (?:staff|employees))", main_text) is None, "micro-enterprise size thresholds must not be stated")
    require("19 June 2026" in main_text and main_text.count("19 June 2026") >= 3, "FATF list status must be date-stamped")
    require("Updated June 2026" in html, "the June 2026 Recommendations edition must be cited")
    require("Explanatory Memorandum" in main_text, "SI 2026/621 purpose must be attributed to the Explanatory Memorandum")
    for quote in re.findall(r"“([^”]{3,})”", main_text):
        require(len(quote.split()) < 15, f"quotation of fifteen or more words: {quote[:80]}")
    for banned in ("INR.10 footnote", "banking customer", "3.2.8R", "2003/361", "awaiting HMT approval"):
        require(banned not in main_text, f"non-citable material used: {banned}")

    # ---- ledger
    guide_claims = [item for item in ledger if item.get("guide") == GUIDE.name]
    require(len(guide_claims) >= 30, f"expected at least 30 ledger claims, found {len(guide_claims)}")
    require(all(item["claimId"].startswith(CLAIM_PREFIX) for item in guide_claims), "ledger claimId prefix mismatch")
    require(all(item.get("status") in {"verified", "needs-review", "retained-as-estimate"} for item in guide_claims), "unexpected ledger status")
    require(not any(item.get("status") == "unverifiable-remove" for item in guide_claims), "unverifiable claim present in guide ledger")

    # ---- relations and namespacing
    require(SLUG in relations, "content-relations entry missing")
    for target in relations[SLUG]:
        require(target in relations and SLUG in relations[target], f"relation is not reciprocal: {SLUG} -> {target}")
        require((ROOT / f"{target}.html").exists(), f"related target has no page: {target}")
    require('class="card"' not in html and 'class="btn"' not in html, "experimental classes must remain namespaced")
    require("[class*=" not in html, "page-local CSS must not add broad substring selectors")
    require(re.search(r'class="[^"]*\b(?:btn|card)[^"]*"', html) is None, "class names containing btn or card collide with brand.css and brand.js")

    print("OK: De-Risking Judgement Call static contract passed")
    print(f"OK: {len(ids)} unique IDs, 3 graded decisions, 5 open points, 5 patterns in two placements, {len(guide_claims)} ledger claims")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration) as error:
        fail(str(error))
