#!/usr/bin/env python3
"""Static contract checks for Financial Crime Control Testing: A Control Exists, But Does It Work? (Framework)."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "financial-crime-control-testing-framework"
GUIDE = ROOT / f"{SLUG}.html"
SCRIPT = ROOT / "js" / f"{SLUG}.js"
CLAIM_PREFIX = f"{SLUG}."
TITLE = "Financial Crime Control Testing: A Control Exists, But Does It Work?"
GRADES = {"best", "incomplete", "unsupported"}
GRADE_LABELS = {
    "best": "Best supported on the facts",
    "incomplete": "Incomplete",
    "unsupported": "Unsupported on the facts",
}
# One expected grade per option, so a silent regrade of a scenario fails the check.
EXPECTED_OPTION_GRADES = {
    "cddsample": {"effective": "unsupported", "notevidenced": "incomplete", "ineffective": "best", "partial": "unsupported"},
    "vendorscreen": {"replace": "incomplete", "ineffective": "best", "effective": "unsupported", "notevidenced": "incomplete"},
}
SCENARIO_SECTIONS = {"cddsample": "scenario-one", "vendorscreen": "scenario-two"}
# Approved Risk, Signal and Response wording from the design memo, section 8.
EXPECTED_PATTERNS = {
    "policy-mirage": ("Policy Mirage", "A documented control is mistaken for an effective one.", "Test evidence is limited to policy review and interviews.", "Separate design, deployment and operation before concluding."),
    "population-blind-spot": ("Population Blind Spot", "Records outside the test source are never examined.", "The sample denominator comes from the control output rather than an independent population.", "Reconcile the intended population before sampling."),
    "vendor-assurance-substitution": ("Vendor Assurance Substitution", "Third-party assurance is treated as proof of the firm's configuration and data.", "No internal lineage, configuration or scenario testing exists.", "Test the firm's implementation and challenge vendor dependencies."),
    "clean-sample-comfort": ("Clean Sample Comfort", "A small passing sample creates a broad conclusion.", "Selection excludes changes, exceptions, high-risk strata or failed items.", "Match selection to the objective and state sampling limits."),
    "exception-graveyard": ("Exception Graveyard", "Findings are logged but do not change the control.", "Repeated issues, extensions or accepted risks have no root-cause action.", "Link exceptions to owners, interim protection, remediation and governance."),
    "closure-without-retest": ("Closure Without Retest", "An action is closed when implementation is reported.", "No evidence shows the corrected control operated after the change.", "Separate implementation from validation and retest before effectiveness closure."),
}
PROPOSITIONS = ["P01", "P02", "P03", "P04", "P05", "P06", "P10", "P11", "P12", "P13", "P14", "P20", "P21", "P22", "P23",
                "P30", "P31", "P32", "P33", "P34", "P40", "P41", "P42", "P43", "P44", "P45", "P46", "P50", "P51", "P52", "P53", "P54"]
REVIEW_DOCS = (
    "docs/review-queue/financial-crime-control-testing-source-pack.md",
    "docs/review-queue/financial-crime-control-testing-design-memo.md",
    "docs/review-queue/financial-crime-control-testing-external-review-brief.md",
)
FAQ_TOPICS = (
    "How large should the sample be?", "Can the first line test its own controls?", "Does no incident mean a control is effective?",
    "Is vendor assurance enough?", "What is the difference between Partially effective and Not evidenced?",
    "Does an ineffective control prove a regulatory breach?", "How often should a control be tested?",
)


class KnowledgeCountParser(HTMLParser):
    """Mirror the Knowledge Hub's guide-count inputs from its static markup."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, str | None]] = []
        self.text_by_id: dict[str, list[str]] = {"khHeroCount": [], "khStatGuides": []}
        self.standalone = 0
        self.series = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        ancestors = {i for _, i in self.stack}
        if "khArticlesGrid" in ancestors and "kh-article-card" in classes:
            self.standalone += 1
        if "khFlagData" in ancestors and "kh-step-data" in classes:
            self.series += 1
        if tag not in self.VOID:
            self.stack.append((tag, a.get("id")))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for _, i in reversed(self.stack):
            if i in self.text_by_id:
                self.text_by_id[i].append(data)
                break

    def count(self, element_id: str) -> int:
        value = "".join(self.text_by_id[element_id]).strip()
        require(value.isdigit(), f"Knowledge Hub {element_id} is not a numeric static count")
        return int(value)


class RelatedSectionParser(HTMLParser):
    """Collect hrefs inside the element whose id marks a page's related section, tracking nesting depth."""

    VOID = KnowledgeCountParser.VOID
    IDS = {"related", "related-topics", "related-intelligence"}

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.found = False
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth == 0 and a.get("id") in self.IDS and not self.found:
            self.found = True
            self.depth = 1
            return
        if self.depth and tag not in self.VOID:
            self.depth += 1
        if self.depth and tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag):
        if self.depth and tag not in self.VOID:
            self.depth -= 1


def related_section_links(page_html: str) -> list[str] | None:
    parser = RelatedSectionParser()
    parser.feed(page_html)
    return parser.hrefs if parser.found else None


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text_only(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def section(html: str, section_id: str) -> str:
    match = re.search(rf'<section class="fct-section[^"]*"[^>]*id="{section_id}"[^>]*>(.*?)</section>', html, re.S)
    require(match is not None, f"section {section_id} is missing")
    return match.group(1)


def main() -> None:
    html = GUIDE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))
    main_html = re.search(r'<main id="main-content".*?</main>', html, re.S).group(0)
    main_text = text_only(re.sub(r"<script.*?</script>", "", main_html, flags=re.S))

    # ---- structure and metadata
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    require(not duplicates, f"duplicate IDs: {duplicates}")
    require('href="#main-content"' in html and 'id="main-content"' in html, "skip link target is missing")
    require(html.index('class="fct-skip"') < html.index("<nav"), "skip link must be the first focusable element")
    require(html.count("<h1") == 1, "expected exactly one h1")
    require("<h1>Financial Crime Control Testing:<br><em>A Control Exists, But Does It Work?</em></h1>" in html, "h1 does not follow the social card pattern")
    for label in ("Evidence reviewed", "Last reviewed", "Law read as at"):
        require(f"{label}</dt>" in html, f"{label} date must be visible")
    levels = [int(x) for x in re.findall(r"<h([1-6])\b", html)]
    for prev, cur in zip(levels, levels[1:]):
        require(cur <= prev + 1, f"heading order skips from h{prev} to h{cur}")
    require(not re.search(r"<h[1-6][^>]*>\s*</h[1-6]>", html), "empty heading")

    json_ld = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    require(len(json_ld) == 2, "expected Article and BreadcrumbList JSON-LD blocks")
    structured = [json.loads(b) for b in json_ld]
    article = next((i for i in structured if i.get("@type") == "Article"), None)
    crumbs = next((i for i in structured if i.get("@type") == "BreadcrumbList"), None)
    require(article is not None and crumbs is not None, "structured data incomplete")
    for prop in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "mainEntityOfPage", "image"):
        require(prop in article, f"Article property missing: {prop}")
    require(len(crumbs["itemListElement"]) == 3, "BreadcrumbList is incomplete")
    require(article["headline"] == TITLE, "Article headline differs from the title")
    require(f"<title>{TITLE} | FinCrimeRadar</title>" in html, "title tag differs")
    for tag in ("og:title", "twitter:title"):
        require(re.search(rf'(?:property|name)="{tag}" content="{re.escape(TITLE)}"', html), f"{tag} differs from the title")
    desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    require(article["description"] == desc, "description metadata differs from Article description")
    og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', html).group(1)
    tw_desc = re.search(r'<meta name="twitter:description" content="([^"]+)"', html).group(1)
    require(og_desc == tw_desc, "Open Graph and Twitter descriptions differ")
    published = article["datePublished"]
    require(article["dateModified"] == published, "datePublished and dateModified differ")
    require(f'article:published_time" content="{published}"' in html and f'article:modified_time" content="{published}"' in html, "article time metadata differs from JSON-LD")

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)"', html)
    require(canonical and og_url and canonical.group(1) == og_url.group(1) == f"https://fincrimeradar.org/{SLUG}.html", "canonical and Open Graph URL differ")
    require(article["mainEntityOfPage"]["@id"] == canonical.group(1), "structured data page id differs from canonical")
    require(crumbs["itemListElement"][2]["item"] == canonical.group(1) and crumbs["itemListElement"][2]["name"] == TITLE, "breadcrumb target differs")
    require(canonical.group(1) in sitemap and sitemap.count(canonical.group(1)) == 1, "sitemap must list the guide exactly once")
    require(re.search(rf"<loc>{re.escape(canonical.group(1))}</loc>\s*<changefreq>monthly</changefreq>\s*<priority>0.7</priority>", sitemap), "sitemap entry does not match the tier of comparable guides")
    card_png = ROOT / f"{SLUG}-social-card.png"
    require(card_png.exists() and 5_000 < card_png.stat().st_size < 400_000, "social card PNG missing or outside the size ceiling")
    require(card_png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "social card is not a PNG")
    require(html.count(f"https://fincrimeradar.org/{SLUG}-social-card.png") == 3, "social card must be referenced by og:image, twitter:image and JSON-LD")
    require(f"/{SLUG}.html" in knowledge, "Knowledge Hub card missing")
    require(re.search(rf'href="/{SLUG}.html"[^>]*data-date="{published}"', knowledge) is not None, "Knowledge Hub data-date differs from the guide's published date")
    require(re.search(rf'href="/{SLUG}.html".*?kh-format-label">Framework<', knowledge, re.S) is not None, "visible Framework label missing from Knowledge Hub card")
    hub_title = re.search(rf'href="/{SLUG}.html".*?kh-item-title">([^<]+)<', knowledge, re.S).group(1)
    require(hub_title == TITLE, "Knowledge Hub card title differs from the guide title")
    require(re.search(r'<span class="fct-format">\s*Framework\s*</span>', html) is not None, "public Framework label is missing")
    require("Experiment" not in html and "experiment" not in main_text.lower(), "internal experiment terminology exposed in the guide")
    for leak in ("source pack", "design memo", "Claude", "Codex", "review brief", "implementation session", "Requirement Coverage"):
        require(leak.lower() not in main_text.lower(), f"internal terminology exposed in the guide: {leak}")
    require(not re.search(r"\bP\d{2}\b", main_text), "source pack proposition IDs must not appear on the page")
    hub_mins = re.search(rf'href="/{SLUG}.html".*?kh-read">(\d+) MIN', knowledge, re.S).group(1)
    hero_mins = re.search(r"<span>(\d+) min read</span>", html).group(1)
    require(hub_mins == hero_mins, f"hero reading time {hero_mins} differs from the Knowledge Hub {hub_mins}")

    counts = KnowledgeCountParser()
    counts.feed(knowledge)
    declared = counts.standalone + counts.series
    require(counts.count("khHeroCount") == counts.count("khStatGuides") == declared, f"Knowledge Hub guide counts differ: declared={declared}")

    # ---- Intelligence Core, scope and evidence labels
    for label in ("Question", "Evidence state", "Decision object", "Uncertainty", "What would change this", "Practitioner outcome"):
        require(f"<dt>{label}</dt>" in main_html, f"Intelligence Core element missing: {label}")
    for state in ("established", "guidance", "public", "assessment", "unknown"):
        require(f'data-state="{state}"' in main_html, f"evidence label missing: {state}")
    require(main_text.count("FinCrimeRadar assessment") >= 15, "FinCrimeRadar assessment labelling is too sparse")
    require("public bodies" in main_text and "not an FCA rule" in main_text and "does not govern FCA-regulated firms" in main_text, "the GOV.UK framework must be visibly scoped to public bodies")
    for para in re.findall(r"<p>(.*?)</p>", section(html, "authority") + section(html, "design") + section(html, "operation") + section(html, "conclusion"), re.S):
        if 'href="#source-9"' in para:
            require("Public-sector practice" in para or "public-sector" in para.lower() or "GOV.UK" in para, f"a GOV.UK citation lacks its public-sector label: {text_only(para)[:90]}")

    # ---- the analytical model and its three static visuals
    chain = re.search(r'<ol class="fct-chain">(.*?)</ol>', main_html, re.S)
    require(chain is not None and chain.group(1).count("<li>") == 7, "the Control Proof Chain must have seven links")
    for stage in ("Risk", "Control objective", "Design", "Deployment", "Operation", "Exceptions", "Remediation and retest"):
        require(f"<h3>{stage}</h3>" in chain.group(1), f"chain link missing: {stage}")
    proofs = re.search(r'<div class="fct-proofs">(.*?)</figure>', main_html, re.S).group(1)
    require(proofs.count('<div class="fct-proof">') == 3, "three-proof matrix must hold three proofs")
    for proof, false_text in (("Design proof", "A detailed policy proves the control works."), ("Deployment proof", "The system is switched on, so every item is covered."), ("Operating proof", "No incident or clean sample proves effectiveness.")):
        require(f"<h3>{proof}</h3>" in proofs and false_text in proofs, f"proof card incomplete: {proof}")
    require(proofs.count("<dt>Core question</dt>") == 3 and proofs.count("<dt>Evidence examples</dt>") == 3 and proofs.count("<dt>False assurance to reject</dt>") == 3, "each proof needs a question, evidence and false assurance")
    ladder = re.search(r'<ul class="fct-ladder">(.*?)</ul>(.*?)</figure>', main_html, re.S)
    require(ladder is not None and ladder.group(1).count("<li") == 3, "the ladder must hold exactly three rungs")
    for rung in ("Effective", "Partially effective", "Ineffective"):
        require(f"<strong>{rung}</strong>" in ladder.group(1), f"ladder rung missing: {rung}")
    require("Not evidenced" not in ladder.group(1), "Not evidenced must not be a rung of the ladder")
    limit = re.search(r'<div class="fct-limit">(.*?)</div>', ladder.group(2), re.S)
    require(limit is not None and "<h3>Not evidenced</h3>" in limit.group(1), "Not evidenced must sit in its own separate block")
    require("not a weak pass" in limit.group(1) and "not a maturity level" in limit.group(1) and "not a fail" in limit.group(1), "Not evidenced must be stated as neither a pass, a fail nor a maturity level")
    figures = re.findall(r'<figure class="fct-fig" aria-labelledby="([^"]+)">(.*?)</figure>', main_html, re.S)
    require(len(figures) == 3, f"expected three figures, found {len(figures)}")
    for label_id, body in figures:
        require(f'id="{label_id}"' in main_html, f"figure label target missing: {label_id}")
        require("<figcaption>Text equivalent:" in body, f"figure {label_id} has no text equivalent")
        require("<svg" not in body and "<img" not in body and "<canvas" not in body, f"figure {label_id} must be static text and CSS only")
    fields = re.search(r'<ol class="fct-fields">(.*?)</ol>', main_html, re.S)
    require(fields is not None and fields.group(1).count("<li>") == 9, "the conclusion record must list nine fields")
    require("<canvas" not in html and 'type="range"' not in html and 'type="number"' not in html, "no calculator inputs allowed")
    require(not re.search(r"calculator|maturity (?:score|model)|heat ?map|sample-size generator", main_text.lower().replace("not a maturity level", "")), "no calculator, maturity score or heat map is allowed")

    # ---- scenarios: graded decisions, each option with Source, Application, Action
    page_forms = re.findall(r'<form class="fct-choice" data-decision-form data-scenario-id="(\w+)" method="dialog">(.*?)</form>', html, re.S)
    require(sorted(k for k, _ in page_forms) == sorted(EXPECTED_OPTION_GRADES), "expected exactly the two decision forms")
    best_positions = []
    for key, form_html in page_forms:
        require(form_html.count("<fieldset>") == 1 and form_html.count("<legend>") == 1, f"{key} decision is not one native fieldset")
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', form_html)
        require(len(radios) == 4, f"{key} must contain four options")
        require(all(f'name="{key}-decision"' in r for r in radios), f"{key} radio group inconsistent")
        values = [re.search(r'value="([^"]+)"', r).group(1) for r in radios]
        grades = [re.search(r'data-grade="([^"]+)"', r).group(1) for r in radios]
        require(dict(zip(values, grades)) == EXPECTED_OPTION_GRADES[key], f"{key} option grades differ from the contract")
        require(set(grades) <= GRADES and grades.count("best") == 1, f"{key} must contain exactly one best option")
        for r, g in zip(radios, grades):
            require(f'data-grade-label="{GRADE_LABELS[g]}"' in r, f"{key} grade label differs from the contract")
        texts = [text_only(t) for t in re.findall(r"<span>(.*?)</span>", form_html, re.S)]
        best_index = grades.index("best")
        best_positions.append(best_index)
        require(len(texts[best_index]) < max(len(t) for t in texts), f"{key} best option must not be the longest")
        require('class="fct-feedback" aria-live="polite" role="status"' in form_html, f"{key} feedback is not a polite status")
        group = re.search(rf'<div class="fct-optfb-set" data-optfb-for="{key}" role="group" aria-labelledby="optfb-title-{key}">(.*?)\n  </div>\n  <div class="fct-counterfactual">', html, re.S)
        require(group is not None, f"{key} option analysis set missing")
        blocks = re.findall(r'<div class="fct-optfb" id="optfb-[^"]+" data-option="([^"]+)" data-grade="([^"]+)">(.*?)</div>\s*</div>', group.group(1), re.S)
        require(sorted(v for v, _, _ in blocks) == sorted(values), f"{key} analysis blocks do not match the options")
        for value, grade, inner in blocks:
            require(EXPECTED_OPTION_GRADES[key][value] == grade, f"{key}/{value} analysis grade differs")
            head = re.search(r'<p class="fct-optfb-head"><span class="fct-grade" data-grade="(\w+)">([^<]+)</span> (.*?)</p>', inner, re.S)
            require(head and head.group(1) == grade and head.group(2) == GRADE_LABELS[grade], f"{key}/{value} analysis badge differs")
            require(text_only(head.group(3)) == texts[values.index(value)], f"{key}/{value} analysis head does not repeat the option text")
            for label in ("Source", "Application", "Action"):
                m = re.search(rf"<h3>{label}</h3><p>(.*?)</p>", inner, re.S)
                require(m is not None and len(text_only(m.group(1))) > 60, f"{key}/{value} missing substantive {label}")
            require("This is a FinCrimeRadar recommendation." in inner, f"{key}/{value} Action must be labelled as a FinCrimeRadar recommendation")
            if grade == "best":
                for proof in ("Design proof", "Deployment proof", "Operating proof"):
                    require(proof in inner, f"{key} best analysis does not address {proof}")
        scope = section(html, SCENARIO_SECTIONS[key])
        require("Counterfactual: change one fact" in scope, f"{key} counterfactual missing")
        require("Composite scenario for teaching. All names, organisations, counts and dates are fictional." in scope, f"{key} must label its figures as fictional")
        record = re.search(r'<div class="fct-record"[^>]*>(.*?)</div>', scope, re.S)
        require(record is not None and "<dl>" in record.group(1), f"{key} Decision Record missing")
        for field in ("Facts", "Assumptions", "Proofs", "Limitations", "Conclusion", "Response", "Rationale"):
            require(re.search(rf"<dt[^>]*>{field}</dt>", record.group(1)) is not None, f"{key} Decision Record field missing: {field}")
        proofs_dd = re.search(r"<dt>Proofs</dt><dd>(.*?)</dd>", record.group(1), re.S).group(1)
        require(all(w in proofs_dd for w in ("Design:", "Deployment:", "Operation:")), f"{key} Decision Record must state design, deployment and operation separately")
        conclusion_dd = re.search(r"<dt>Conclusion</dt><dd>(.*?)</dd>", record.group(1), re.S).group(1)
        require("Ineffective" in conclusion_dd, f"{key} Decision Record conclusion must match the best grade")
    require(len(set(best_positions)) == 2, f"best option position is too predictable: {best_positions}")
    require(html.count("data-decision-form") == 2, "expected exactly two decision forms")
    one, two = section(html, "scenario-one"), section(html, "scenario-two")
    require("Worked scenario 1 · Deployment" in one and "Worked scenario 2 · Data path" in two, "scenario tags must name distinct risk mechanisms")
    require("CDD" in one and "screening" not in text_only(one.split("How each option grades")[0]).lower().replace("screening objective", ""), "scenario 1 is not distinct from scenario 2 in its facts")
    require("sanction" in two.lower() and "migrated" not in text_only(two.split("How each option grades")[0]), "scenario 2 is not distinct from scenario 1 in its facts")

    # ---- patterns: six cards inline and again in the closing grid, identical, with the approved wording
    patterns: dict[str, list[tuple[int, str]]] = {}
    for m in re.finditer(r'<div class="fct-pattern" data-pattern-id="([^"]+)">(.*?)</dl>\s*</div>', main_html, re.S):
        patterns.setdefault(m.group(1), []).append((m.start(), text_only(m.group(2))))
    require(set(patterns) == set(EXPECTED_PATTERNS), f"pattern ids differ: {sorted(patterns)}")
    closing_start = main_html.index('id="fctClosingPatterns"')
    for pid, copies in patterns.items():
        require(len(copies) == 2, f"{pid} must appear inline and in the closing grid")
        require(copies[0][1] == copies[1][1], f"{pid} inline and closing copies differ")
        require(copies[0][0] < closing_start < copies[1][0], f"{pid} copies are not one inline and one closing")
        name, risk, signal, response = EXPECTED_PATTERNS[pid]
        for needle in (name, f"Risk {risk}", f"Signal {signal}", f"Response {response}"):
            require(needle in copies[0][1], f"{pid} lost approved wording: {needle}")
    require(re.search(r'<div class="fct-patterns" id="fctClosingPatterns">', html) and 'id="saveFrameworkStatus" aria-live="polite" role="status"' in html, "closing grid or export status is not wired")

    # ---- knowledge check, FAQ, challenge
    quiz = section(html, "knowledge-check")
    fieldsets = re.findall(r"<fieldset>(.*?)</fieldset>", quiz, re.S)
    require(len(fieldsets) == 5, "knowledge check must contain five fieldsets")
    expected_correct = ("Deployment proof.", "No. Paragraph (1) applies where appropriate", "That the queue contains the full intended population.", "When the method, population, period or evidence cannot support an effectiveness conclusion.", "Evidence that the action was implemented and that the affected proof was retested")
    positions, longest = [], 0
    for n, fs in enumerate(fieldsets, start=1):
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fs)
        require(len(radios) == 3 and sum('data-correct="true"' in r for r in radios) == 1, f"knowledge question {n} needs three options and one correct answer")
        positions.append(next(i for i, r in enumerate(radios) if 'data-correct="true"' in r))
        spans = [text_only(t) for t in re.findall(r"<span>(.*?)</span>", fs, re.S)]
        longest += len(spans[positions[-1]]) == max(len(t) for t in spans)
        require(spans[positions[-1]].startswith(expected_correct[n - 1]), f"knowledge question {n} correct answer differs from the contract")
    require(max(positions.count(i) for i in range(3)) <= 2, f"correct answer position is too predictable: {positions}")
    require(longest <= 2, f"the correct answer is the longest option in {longest} of 5 questions")
    require(html.count('data-correct="true"') == quiz.count('data-correct="true"'), "correct-answer markers must stay inside the knowledge check")
    require('id="knowledgeFeedback"' in quiz and 'aria-live="polite" role="status"' in quiz, "knowledge feedback is not a polite status")
    require(quiz.count("<em>Source:</em>") == 5 and quiz.count("<em>Application:</em>") == 5 and quiz.count("<em>Action:</em>") == 5, "answer notes must separate Source, Application and Action")
    require("<details><summary>Answer notes</summary>" in quiz, "answer notes must be native details")
    faq = section(html, "faq")
    require(faq.count("<details>") == 7 and faq.count("<summary>") == 7, "FAQ needs seven native details")
    for topic in FAQ_TOPICS:
        require(f"<summary>{topic}</summary>" in faq, f"FAQ topic missing: {topic}")
    require("<h2>Red Team Questions</h2>" in html and section(html, "red-team").count("<li>") == 8, "eight Red Team Questions required")
    require("<h2>One Screen Operational Summary</h2>" in html and section(html, "operational-summary").count("<li>") == 8, "operational summary needs eight items")

    # ---- progressive enhancement and interaction contract
    forms = re.findall(r"<form\b[^>]*>", html)
    require(forms and all('method="dialog"' in f and "action=" not in f for f in forms), "every form must use method=dialog with no action")
    require('.js .fct-optfb-set:not([data-revealed="true"]){display:none}' in html, "option analyses must be hidden only when the js class is set")
    require(".fct-choice .fct-action,#knowledgeForm .fct-action,#saveFrameworkImage{display:none}" in html and ".js .fct-choice .fct-action" in html, "action buttons must be hidden until the js class is set")
    require("@media(prefers-reduced-motion:reduce)" in html, "reduced-motion guard missing")
    require(not re.search(r"@keyframes|animation:", html), "no animation is expected on this page")
    require(all("role=" in tag for tag in re.findall(r'<div[^>]*aria-label=[^>]*>', html)), "aria-label must not sit on a generic div without a role")
    require(html.count('id="optfb-') >= 8, "each option analysis needs an id for the feedback link")
    require("classList.add('js')" in script and script.count("event.preventDefault()") >= 2, "script must set the js class and prevent default on submit")
    require(script.rindex("classList.add('js')") > script.rindex("addEventListener("), "the js class must be set after every handler is attached")
    require(".fct-optfb{scroll-margin-top:120px}" in html, "analysis blocks need a scroll margin")
    require("sentEvents" in script and "setTimeout(function () { URL.revokeObjectURL" in script, "telemetry once-only or delayed revoke missing")
    require("addEventListener('change'" in script, "change handler that clears stale feedback is missing")
    require("javascript:" not in html and "javascript:" not in script, "no javascript: URLs")
    require("var KNOWN_GRADES = ['best', 'incomplete', 'unsupported'];" in script, "the script grade allow-list differs from the contract")
    require("var GUIDE_ID = 'financial_crime_control_testing_framework';" in script, "telemetry guide id differs from the contract")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    for grade in GRADES:
        require(f'[data-grade="{grade}"]' in css, f"missing CSS grade rule for {grade}")
    require("\\n" not in css, "a literal backslash-n in the CSS would swallow the next rule")
    require(".fct-optfb-head{" in css and ".fct-grade{" in css, "analysis head and grade badge rules must be present")

    # ---- script discipline and telemetry
    require("innerHTML" not in script, "page script must not inject HTML reasoning")
    require("crs-" not in script and "customer-risk" not in script.lower(), "script still carries precedent identifiers")
    for phrase in ("regulation", "FCA", "MLR", "Ineffective", "Not evidenced", "population", "deployment", "vendor", "Decision Record"):
        require(phrase.lower() not in script.lower().replace("fcr_cookie_consent_v2", ""), f"material reasoning leaked into JavaScript: {phrase}")
    require("fcr_cookie_consent_v2" in script and "consentGranted()" in script, "telemetry consent gate missing")
    for forbidden in ("customer_name", "account_number", "free_text", "localStorage.setItem", "sessionStorage"):
        require(forbidden not in script, f"sensitive telemetry or storage risk: {forbidden}")
    events = set(re.findall(r"'([a-z_]+_(?:complete|export))'", script))
    require(events == {"scenario_complete", "knowledge_check_complete", "card_export"}, f"unexpected telemetry events: {events}")
    params = set(re.findall(r"\b(guide_id|scenario_id|decision_grade|score|total|export_type)\s*:", script))
    require(params == {"guide_id", "scenario_id", "decision_grade", "score", "total", "export_type"}, f"unexpected telemetry parameters: {params}")

    # ---- sources, quotation limits, editorial constraints
    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited = set(re.findall(r'href="#source-(\d+)"', html))
    require(source_ids == cited == {str(i) for i in range(1, 10)}, f"source references differ: defined={sorted(source_ids)} cited={sorted(cited)}")
    for url in re.findall(r'<li id="source-\d+"><a href="([^"]+)"', html):
        require(url.startswith("https://"), f"source link is not https: {url}")
    require(not re.search("[\u2013\u2014]", html), "em or en dash found in the guide")
    require(not re.search("[\u2013\u2014]", script), "em or en dash found in the script")
    for quote in re.findall(r"“([^”]{3,})”", main_text) + re.findall(r'"([^"]{3,})"', main_text):
        require(len(quote.split()) < 15, f"quotation of fifteen or more words: {quote[:80]}")

    # ---- regulatory contract and negative pins: claims the source pack says must not be made
    require("where appropriate with regard to the size and nature of its business" in main_text, "regulation 21(1) condition is missing")
    require("Regulation 21(6) disapplies paragraphs (1) and (3)" in main_text and "neither employs nor acts in association with any other person" in main_text, "regulation 21(6) exception is missing")
    require("monitor compliance with those recommendations" in main_text, "regulation 21(1)(c) third responsibility must follow the statutory text")
    require("regulation 21(10)" in main_text and "18A(1)" in main_text, "regulation 21(10) factors are missing")
    require(main_text.count("regulation 21") + main_text.count("Regulation 21") >= 5, "regulation 21 appears too rarely to carry its conditional wording")
    require("conditional" in main_text.lower(), "the conditional nature of regulation 21 must be stated in words")
    require("As read, regulations 19 and 21 prescribe no universal test frequency, sample size, pass threshold, rating scale or evidence taxonomy" in main_text, "the no universal test parameters statement is missing")
    require("general guidance" in main_text and "not binding" in main_text, "FCG status statement is missing")
    require("good practice often goes beyond the minimum regulatory requirements" in main_text, "the FCA beyond-minimum caveat is missing")
    require("The percentages the FCA published describe its own testing programme and are not pass thresholds" in main_text, "the FCA percentages must be stated as not thresholds")
    require("the inference is ours" in main_text.lower() or "inference is ours" in main_text.lower(), "the absence-of-incidents inference must be labelled as ours")
    require("Not evidenced is our addition" in main_text, "Not evidenced must be labelled as a FinCrimeRadar addition")
    require("no source read imposes this exact three-part taxonomy" in main_text, "the three-proof taxonomy must be labelled as FinCrimeRadar's")
    require("This guide gives no instructions for bypassing live controls" in main_text and main_text.lower().count("bypass") == 1, "bypass wording must be limited to the single prohibition statement")
    require(not re.search(r"evade|circumvent|defeat the control|get around the control", main_text.lower()), "possible control-bypass wording found")
    require("%" not in main_text, "no percentage sign allowed: the FCA published percentages must not become thresholds")
    forbidden_phrases = (
        "regulation 21 requires an independent audit function in every", "every relevant person must have an independent audit",
        "the FCA requires", "the FCA requires firms to", "must be tested annually", "must be tested quarterly", "minimum sample", "sample size of",
        "pass rate of", "industry standard", "regulator-approved", "FCA-approved", "FCA approved", "compliant method", "required by the FCA",
        "the gov.uk framework applies to", "vendor assurance replaces", "vendor assurance is enough", "no incidents prove", "a clean sample proves",
        "ineffective control is a breach", "ineffective control means a breach", "a rating alone determines residual risk",
    )
    for phrase in forbidden_phrases:
        require(phrase.lower() not in main_text.lower(), f"claim the source pack rules out: {phrase}")
    require(not re.search(r"\b(?:at least|every|each|within) \d+ (?:days|months|years)\b", main_text.replace("Eleven", "")), "an invented frequency or interval appears")
    require(not re.search(r"\b(?:sample|sampling)\b[^.]{0,40}\b\d{2,}\b", re.sub(r"Compliance samples 20 completed reviews|The sample of 20 is a judgemental sample", "", main_text)), "a sample size appears outside the illustrative scenario fact")
    require("Compliance samples 20 completed reviews" in main_text and "sample of 20 is a judgemental sample" in main_text, "the illustrative sample in scenario 1 must be present and limited")

    # ---- ledger
    claims = [c for c in ledger if c.get("guide") == GUIDE.name]
    require(len(claims) >= 40, f"expected at least 40 ledger claims, found {len(claims)}")
    require(all(c["claimId"].startswith(CLAIM_PREFIX) for c in claims), "ledger claimId prefix mismatch")
    require(len({c["claimId"] for c in claims}) == len(claims), "duplicate ledger claimId")
    require(all(c.get("status") == "verified" for c in claims), "unexpected ledger status")
    require(all(c.get("location", "").startswith(GUIDE.name) for c in claims), "ledger locations must name the guide")
    for c in claims:
        for loc in re.findall(r"#([a-z-]+)", c["location"]):
            require(f'id="{loc}"' in html, f"ledger location points to a missing section: #{loc} in {c['claimId']}")
    ledger_urls = {c.get("source", {}).get("url") for c in claims} | {s["url"] for c in claims for s in c.get("additionalSources", [])}
    for url in re.findall(r'<li id="source-\d+"><a href="([^"]+)"', html):
        require(url in ledger_urls, f"cited source has no ledger claim: {url}")
    notes = " ".join(c.get("note", "") for c in claims)
    for pid in PROPOSITIONS:
        require(re.search(rf"\b{pid}\b", notes) is not None, f"source pack proposition {pid} is not mapped in the ledger")
    claim_text = " ".join(c["claimText"] for c in claims)
    for must in ("regulation 21(6)".replace("regulation", "Regulation"), "those recommendations", "18A(1)", "REP-CRIM", "section 139B", "likely or existing", "Not evidenced means", "no universal control test frequency, sample size, pass threshold, rating scale or evidence taxonomy"):
        require(must in claim_text, f"ledger does not carry the claim: {must}")
    reg21 = next(c for c in claims if "reg21-1-independent-audit-conditional" in c["claimId"])
    require("where appropriate with regard to the size and nature" in reg21["claimText"], "regulation 21 ledger claim lost its condition")
    require(any(c["claimType"] == "process-record" and "methodology" in c["claimId"] for c in claims), "methodology process record is missing")
    require(all(c["verifiedOn"] == "2026-11-01" for c in claims), "ledger verifiedOn differs from the evidence date")

    # ---- relations, namespacing and review documents
    require(SLUG in relations, "content-relations entry missing")
    for target in relations[SLUG]:
        require(target in relations and SLUG in relations[target], f"relation is not reciprocal: {SLUG} -> {target}")
        require((ROOT / f"{target}.html").exists(), f"related target has no page: {target}")
        require(f'href="/{target}.html"' in main_html, f"related guide is not linked from the page: {target}")
        target_html = (ROOT / f"{target}.html").read_text(encoding="utf-8")
        section_links = related_section_links(target_html)
        require(section_links is not None, f"{target} has no related section (id related, related-topics or related-intelligence)")
        require(f"/{SLUG}.html" in section_links, f"{target} does not render a backlink to this guide inside its related section")
    classes = {c for attr in re.findall(r'class="([^"]*)"', main_html) for c in attr.split()}
    stray = sorted(c for c in classes if not c.startswith("fct-"))
    require(not stray, f"classes inside the article that are not namespaced: {stray}")
    require("[class*=" not in html and re.search(r'class="[^"]*\b(?:btn|card)\b', html) is None, "class names collide with brand.css and brand.js")
    require(re.search(r"<table\b", html) is None, "no tables: brand.js watches table selectors")
    for doc in REVIEW_DOCS:
        path = ROOT / doc
        require(path.exists() and path.stat().st_size > 2_000, f"review document missing or empty: {doc}")
        require(not re.search("[\u2013\u2014]", path.read_text(encoding="utf-8")), f"em or en dash found in {doc}")
    brief = (ROOT / REVIEW_DOCS[2]).read_text(encoding="utf-8")
    for needle in ("Regulation 19", "Regulation 21", "SYSC 3.2.6", "FCG", "GOV.UK", "Scenario 1", "Scenario 2"):
        require(needle in brief, f"external review brief does not cover: {needle}")

    print("OK: Financial Crime Control Testing static contract passed")
    print(f"OK: {len(ids)} unique IDs, 2 graded decisions, 3 figures, 6 patterns in two placements, {len(claims)} ledger claims, {len(PROPOSITIONS)} source pack propositions mapped")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration, AttributeError) as error:
        fail(f"{type(error).__name__}: {error}")
