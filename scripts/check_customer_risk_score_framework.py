#!/usr/bin/env python3
"""Static contract checks for Customer Risk Scores: What the Number Cannot Decide (Framework)."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "customer-risk-score-decision-framework"
GUIDE = ROOT / f"{SLUG}.html"
SCRIPT = ROOT / "js" / f"{SLUG}.js"
CLAIM_PREFIX = f"{SLUG}."
GRADES = {"best", "incomplete", "unsupported"}
GRADE_LABELS = {
    "best": "Supported by the sources and the facts",
    "incomplete": "Defensible but incomplete",
    "unsupported": "Not supported on the sources",
}
# One expected grade per option, so a silent regrade of a scenario fails the check.
EXPECTED_OPTION_GRADES = {
    "newproduct": {"continue": "unsupported", "stop": "incomplete", "controlled": "best", "highonly": "incomplete"},
    "overridepattern": {"banall": "unsupported", "pattern": "best", "accept": "unsupported", "reverse": "incomplete"},
}
PATTERN_IDS = (
    "false-precision", "double-counted-risk", "threshold-drift",
    "override-shadow-policy", "stale-reassessment", "consequence-mismatch",
)
REVIEW_DOCS = (
    "docs/review-queue/customer-risk-score-decision-framework-source-pack.md",
    "docs/review-queue/customer-risk-score-decision-framework-design-memo.md",
    "docs/review-queue/customer-risk-score-decision-framework-external-review-brief.md",
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


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text_only(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def section(html: str, section_id: str) -> str:
    match = re.search(rf'<section class="crs-section[^"]*"[^>]*id="{section_id}"[^>]*>(.*?)</section>', html, re.S)
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
    require(html.index('class="crs-skip"') < html.index("<nav"), "skip link must be the first focusable element")
    require(html.count("<h1") == 1, "expected exactly one h1")
    require(re.search(r"<h1>Customer Risk Scores:<br><em>What the Number Cannot Decide</em></h1>", html), "h1 does not follow the social card pattern")
    require("Evidence reviewed</dt>" in html and "Last reviewed</dt>" in html and "Law read as at</dt>" in html, "evidence, law-read and last-reviewed dates must be visible")
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
    title = "Customer Risk Scores: What the Number Cannot Decide"
    require(article["headline"] == title, "Article headline differs from the title")
    require(f"<title>{title} | FinCrimeRadar</title>" in html, "title tag differs")
    for tag in ('og:title', 'twitter:title'):
        require(re.search(rf'(?:property|name)="{tag}" content="{re.escape(title)}"', html), f"{tag} differs from the title")
    desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    require(article["description"] == desc, "description metadata differs from Article description")

    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)"', html)
    require(canonical and og_url and canonical.group(1) == og_url.group(1) == f"https://fincrimeradar.org/{SLUG}.html", "canonical and Open Graph URL differ")
    require(canonical.group(1) in sitemap, "canonical URL missing from sitemap")
    require(sitemap.count(canonical.group(1)) == 1, "sitemap lists the guide more than once")
    require(re.search(rf"<loc>{re.escape(canonical.group(1))}</loc>\s*<changefreq>monthly</changefreq>\s*<priority>0.7</priority>", sitemap), "sitemap entry does not match the tier of comparable guides")
    card_png = ROOT / f"{SLUG}-social-card.png"
    require(card_png.exists() and 5_000 < card_png.stat().st_size < 400_000, "social card PNG missing or outside the size ceiling")
    require(card_png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", "social card is not a PNG")
    require(f"/{SLUG}-social-card.png" in html, "social card is not referenced")
    require(f"/{SLUG}.html" in knowledge, "Knowledge Hub card missing")
    require(re.search(rf'href="/{SLUG}.html"[^>]*data-date="2026-10-24"', knowledge) is not None, "Knowledge Hub card has no data-date")
    require(re.search(rf'href="/{SLUG}.html".*?kh-format-label">Framework<', knowledge, re.S) is not None, "visible Framework label missing from Knowledge Hub card")
    require(re.search(r'<span class="crs-format">\s*Framework\s*</span>', html) is not None, "public Framework label is missing")
    require("Experiment" not in html and "experiment" not in main_text.lower(), "internal experiment terminology exposed in the guide")
    hub_mins = re.search(rf'href="/{SLUG}.html".*?kh-read">(\d+) MIN', knowledge, re.S).group(1)
    hero_mins = re.search(r"<span>(\d+) min read</span>", html).group(1)
    require(hub_mins == hero_mins, f"hero reading time {hero_mins} differs from the Knowledge Hub {hub_mins}")

    counts = KnowledgeCountParser()
    counts.feed(knowledge)
    declared = counts.standalone + counts.series
    require(counts.count("khHeroCount") == counts.count("khStatGuides") == declared, f"Knowledge Hub guide counts differ: declared={declared}")

    # ---- originality: boundary against Scenario Lab and no calculator
    require("<canvas" not in html and 'type="range"' not in html and 'type="number"' not in html, "no calculator inputs allowed")
    require("calculator" not in main_text.lower().replace("not a calculator", ""), "the guide must not offer a calculator")
    require("/scenario-lab.html" in main_html, "Scenario Lab boundary link missing")

    # ---- the seven control points and the five visuals
    for number in (1, 2, 3, 4, 5, 6, 7):
        require(f"Control point {number}" in main_html, f"control point {number} is not present")
    cp_list = re.search(r'<ol class="crs-cplist">(.*?)</ol>', main_html, re.S)
    require(cp_list is not None and cp_list.group(1).count("<li>") == 7, "the seven control points must be listed")
    chain = re.search(r'<ol class="crs-chain">(.*?)</ol>', main_html, re.S)
    require(chain is not None and chain.group(1).count("<li>") == 7, "the score-to-decision chain must have seven stages")
    for stage in ("Evidence inputs", "Factor treatment", "Weighting and interaction", "Thresholds", "Operational response", "Override control", "Monitoring and reassessment"):
        require(f"<h3>{stage}</h3>" in chain.group(1), f"chain stage missing: {stage}")
    require("Outside the arithmetic" in main_html, "the outside-the-arithmetic block is missing")
    layers = re.search(r'<ol class="crs-layers">(.*?)</ol>', main_html, re.S)
    require(layers is not None and layers.group(1).count("<li>") == 9 and layers.group(1).count('class="crs-ask"') == 9, "the nine layers, each with a question, are required")
    can = re.search(r'<div class="crs-can">(.*?)</figure>', main_html, re.S).group(1)
    require("Can inform" in can and "Cannot decide alone" in can, "can/cannot panel headings missing")
    require(can.count("crs-state") >= 11, "every can/cannot statement needs its evidence label")
    steps = re.findall(r'<ol class="crs-steps">(.*?)</ol>', main_html, re.S)
    require(len(steps) == 2 and steps[0].count("<li>") == 6 and steps[1].count("<li>") == 7, "override loop (6) and change cycle (7) steps are required")
    require("silent score manipulation" in main_text.lower() and "A controlled override" in main_text, "controlled versus silent override contrast missing")
    for trigger in ("Regulatory change", "A new product", "A new customer type", "A change of data source", "Unexpected band movement", "Repeated overrides", "A control failure"):
        require(f"<li>{trigger}</li>" in main_html, f"change trigger missing: {trigger}")
    figures = re.findall(r'<figure class="crs-fig" aria-labelledby="([^"]+)">(.*?)</figure>', main_html, re.S)
    require(len(figures) == 5, f"expected five figures, found {len(figures)}")
    for label_id, body in figures:
        require(f'id="{label_id}"' in main_html, f"figure label target missing: {label_id}")
        require("<figcaption>Text equivalent:" in body, f"figure {label_id} has no text equivalent")
        require("<svg" not in body or 'role="img"' in body, f"figure {label_id} contains an unlabelled SVG")

    # ---- scenarios: graded decisions, each option with Source, Application, Recommendation
    page_forms = re.findall(r'<form class="crs-choice" data-decision-form data-scenario-id="(\w+)" method="dialog">(.*?)</form>', html, re.S)
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
        require(set(grades) <= GRADES and grades.count("best") == 1, f"{key} must contain exactly one best-supported option")
        for r, g in zip(radios, grades):
            require(f'data-grade-label="{GRADE_LABELS[g]}"' in r, f"{key} grade label differs from the contract")
        texts = [text_only(t) for t in re.findall(r"<span>(.*?)</span>", form_html, re.S)]
        best_index = grades.index("best")
        best_positions.append(best_index)
        require(len(texts[best_index]) < max(len(t) for t in texts), f"{key} best option must not be the longest")
        require('class="crs-feedback" aria-live="polite" role="status"' in form_html, f"{key} feedback is not a polite status")
        group = re.search(rf'<div class="crs-optfb-set" data-optfb-for="{key}" role="group" aria-labelledby="optfb-title-{key}">(.*?)\n  </div>\n  <div class="crs-counterfactual">', html, re.S)
        require(group is not None, f"{key} option analysis set missing")
        blocks = re.findall(r'<div class="crs-optfb" id="optfb-[^"]+" data-option="([^"]+)" data-grade="([^"]+)">(.*?)</div>\s*</div>', group.group(1), re.S)
        require(sorted(v for v, _, _ in blocks) == sorted(values), f"{key} analysis blocks do not match the options")
        for value, grade, inner in blocks:
            require(EXPECTED_OPTION_GRADES[key][value] == grade, f"{key}/{value} analysis grade differs")
            head = re.search(r'<p class="crs-optfb-head"><span class="crs-grade" data-grade="(\w+)">([^<]+)</span> (.*?)</p>', inner, re.S)
            require(head and head.group(1) == grade and head.group(2) == GRADE_LABELS[grade], f"{key}/{value} analysis badge differs")
            option_text = texts[values.index(value)]
            require(text_only(head.group(3)) == option_text, f"{key}/{value} analysis head does not repeat the option text")
            for label in ("Source", "Application", "Recommendation"):
                m = re.search(rf"<h3>{label}</h3><p>(.*?)</p>", inner, re.S)
                require(m is not None and len(text_only(m.group(1))) > 60, f"{key}/{value} missing substantive {label}")
        scope = section(html, "scenario-one" if key == "newproduct" else "scenario-two")
        require("What Would Change My Decision?" in scope and "Counterfactual: change one fact" in scope, f"{key} challenge analyses missing")
        require("Composite scenario for teaching. All figures are fictional." in scope, f"{key} must label its figures as fictional")
        record = re.search(r'<div class="crs-record"[^>]*>(.*?)</div>', scope, re.S)
        require(record is not None and "<dl>" in record.group(1), f"{key} Decision Record missing")
        for field in ("Facts", "Assumptions", "Indicators", "Mitigants", "Decision", "Rationale"):
            require(re.search(rf"<dt[^>]*>{field}</dt>", record.group(1)) is not None, f"{key} Decision Record field missing: {field}")
    require(len(set(best_positions)) == 2, f"best option position is too predictable: {best_positions}")
    require(html.count("data-decision-form") == 2, "expected exactly two decision forms")

    # ---- patterns: six cards inline and again in the closing grid, identical
    patterns: dict[str, list[tuple[str, str]]] = {}
    for m in re.finditer(r'<div class="crs-pattern" data-pattern-id="([^"]+)">(.*?)</dl>\s*</div>', main_html, re.S):
        patterns.setdefault(m.group(1), []).append((m.start(), text_only(m.group(2))))
    require(set(patterns) == set(PATTERN_IDS), f"pattern ids differ: {sorted(patterns)}")
    closing_start = main_html.index('id="crsClosingPatterns"')
    for pid, copies in patterns.items():
        require(len(copies) == 2, f"{pid} must appear inline and in the closing grid")
        require(copies[0][1] == copies[1][1], f"{pid} inline and closing copies differ")
        require(copies[0][0] < closing_start < copies[1][0], f"{pid} copies are not one inline and one closing")
    for pid, copies in patterns.items():
        require(all(w in copies[0][1] for w in ("Risk", "Signal", "Response")), f"{pid} lacks Risk, Signal or Response lines")
    require(re.search(r'<div class="crs-patterns" id="crsClosingPatterns">', html) and 'id="saveFrameworkStatus" aria-live="polite" role="status"' in html, "closing grid or export status is not wired")

    # ---- knowledge check, FAQ
    quiz = section(html, "knowledge-check")
    fieldsets = re.findall(r"<fieldset>(.*?)</fieldset>", quiz, re.S)
    require(len(fieldsets) == 5, "knowledge check must contain five fieldsets")
    positions, longest = [], 0
    for n, fs in enumerate(fieldsets, start=1):
        radios = re.findall(r'<input\b[^>]*type="radio"[^>]*>', fs)
        require(len(radios) == 3 and sum('data-correct="true"' in r for r in radios) == 1, f"knowledge question {n} needs three options and one correct answer")
        positions.append(next(i for i, r in enumerate(radios) if 'data-correct="true"' in r))
        lengths = [len(text_only(t)) for t in re.findall(r"<span>(.*?)</span>", fs, re.S)]
        longest += lengths[positions[-1]] == max(lengths)
    require(max(positions.count(i) for i in range(3)) <= 2, f"correct answer position is too predictable: {positions}")
    require(longest <= 2, f"the correct answer is the longest option in {longest} of 5 questions")
    require(html.count('data-correct="true"') == quiz.count('data-correct="true"'), "correct-answer markers must stay inside the knowledge check")
    require('id="knowledgeFeedback"' in quiz and 'aria-live="polite" role="status"' in quiz, "knowledge feedback is not a polite status")
    require(quiz.count("<em>Source:</em>") == 5 and quiz.count("<em>Application:</em>") == 5 and quiz.count("<em>Recommendation:</em>") == 5, "answer notes must separate Source, Application and Recommendation")
    require("Case Study 17" in fieldsets[0], "a question must test a detail of the named case study")
    faq = section(html, "faq")
    require(faq.count("<details>") >= 6 and faq.count("<details>") == faq.count("<summary>"), "FAQ native details structure incomplete")

    # ---- Intelligence Core and challenge
    for label in ("Question", "Evidence state", "Decision object", "Uncertainty", "What would change this", "Practitioner outcome"):
        require(f"<dt>{label}</dt>" in main_html, f"Intelligence Core element missing: {label}")
    require("<h2>Red Team Questions</h2>" in html and section(html, "red-team").count("<li>") == 8, "eight Red Team Questions required")

    # ---- progressive enhancement and interaction contract
    forms = re.findall(r"<form\b[^>]*>", html)
    require(forms and all('method="dialog"' in f and "action=" not in f for f in forms), "every form must use method=dialog with no action")
    require('.js .crs-optfb-set:not([data-revealed="true"]){display:none}' in html, "option analyses must be hidden only when the js class is set")
    require(".crs-choice .crs-action,#knowledgeForm .crs-action,#saveFrameworkImage{display:none}" in html and ".js .crs-choice .crs-action" in html, "action buttons must be hidden until the js class is set")
    require("@media(prefers-reduced-motion:reduce)" in html, "reduced-motion guard missing")
    require(not re.search(r"@keyframes|animation:", html), "no animation is expected on this page")
    require(re.search(r'<div class="crs-optfb-set"[^>]*aria-label=', html) is None, "aria-label must not sit on a generic div")
    require(html.count('id="optfb-') >= 8, "each option analysis needs an id for the feedback link")
    require("classList.add('js')" in script and script.count("event.preventDefault()") >= 2, "script must set the js class and prevent default on submit")
    require(script.rindex("classList.add('js')") > script.rindex("addEventListener("), "the js class must be set after every handler is attached")
    require(".crs-optfb{scroll-margin-top:120px}" in html, "analysis blocks need a scroll margin")
    require("sentEvents" in script and "setTimeout(function () { URL.revokeObjectURL" in script, "telemetry once-only or delayed revoke missing")
    require("addEventListener('change'" in script, "change handler that clears stale feedback is missing")
    require("javascript:" not in html and "javascript:" not in script, "no javascript: URLs")
    require("var KNOWN_GRADES = ['best', 'incomplete', 'unsupported'];" in script, "the script grade allow-list differs from the contract")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    for grade in GRADES:
        require(f'[data-grade="{grade}"]' in css, f"missing CSS grade rule for {grade}")
    require("\\n" not in css, "a literal backslash-n in the CSS would swallow the next rule")
    require('.crs-optfb-head{' in css and '.crs-grade{' in css, "analysis head and grade badge rules must be present")

    # ---- script discipline
    require("innerHTML" not in script, "page script must not inject HTML reasoning")
    for phrase in ("regulation", "FCA", "Call for Action", "MLRO", "override", "Case Study", "control point"):
        require(phrase.lower() not in script.lower().replace("fcr_cookie_consent_v2", ""), f"material reasoning leaked into JavaScript: {phrase}")
    require("fcr_cookie_consent_v2" in script and "consentGranted()" in script, "telemetry consent gate missing")
    for forbidden in ("customer_name", "account_number", "free_text", "Decision Record", "localStorage.setItem", "sessionStorage"):
        require(forbidden not in script, f"sensitive telemetry or storage risk: {forbidden}")
    events = set(re.findall(r"'(scenario_complete|knowledge_check_complete|card_export|[a-z_]+_complete)'", script))
    require(events <= {"scenario_complete", "knowledge_check_complete", "card_export"}, f"unexpected telemetry events: {events}")

    # ---- sources, quotation limits, editorial constraints
    source_ids = set(re.findall(r'id="source-(\d+)"', html))
    cited = set(re.findall(r'href="#source-(\d+)"', html))
    require(source_ids == cited == {str(i) for i in range(1, 9)}, f"source references differ: defined={sorted(source_ids)} cited={sorted(cited)}")
    for url in re.findall(r'<li id="source-\d+"><a href="([^"]+)"', html):
        require(url.startswith("https://"), f"source link is not https: {url}")
    require(not re.search("[\u2013\u2014]", html), "em or en dash found in the guide")
    require(not re.search("[\u2013\u2014]", script), "em or en dash found in the script")
    for quote in re.findall(r"“([^”]{3,})”", main_text) + re.findall(r'"([^"]{3,})"', main_text):
        require(len(quote.split()) < 15, f"quotation of fifteen or more words: {quote[:80]}")

    # ---- negative pins: claims the source pack says must not be made
    forbidden_phrases = (
        "recommended weighting", "industry standard", "the FCA requires a", "the FCA requires firms to use", "quarterly review is required",
        "must be reviewed quarterly", "compliant formula", "compliant model", "FCA-approved", "FCA approved", "regulator-approved",
        "if the supervisory authority so requires", "Increased Monitoring status is an automatic",
    )
    for phrase in forbidden_phrases:
        require(phrase.lower() not in main_text.lower(), f"claim the source pack rules out: {phrase}")
    require(not re.search(r"product and service\s*(?:\(|at|is|:)?\s*10\s*%", main_text, re.I), "the Case Study 17 percentages must not be reproduced")
    for pct in ("20%", "25%"):
        require(pct not in main_text, f"percentage that belongs to the Case Study 17 weights appears: {pct}")
    require("not a legal minimum" in main_text, "quarterly updating must be stated as not a legal minimum")
    require("one firm" in main_text.lower() and "least transferable" in main_text, "Case Study 17 must be framed as one firm's illustration")
    require("prescribes a scoring method" in main_text, "the no prescribed model statement is missing")
    require("subject to the narrow exception in regulation 33(2)" in main_text, "the regulation 33(2) exception must be named beside the Call for Action trigger")
    # reg 33 contract: (c) listed, exception kept in the application sentence, 33(7) separate from the suspicion and exit claim
    require("correspondent relationships caught by regulation 33(1)(c), in accordance with regulation 34" in main_text, "regulation 33(1)(c) must appear in the fact-based list")
    require("unless the regulation 33(2) exception applies" in main_text, "the regulation 33(2) exception must stay attached to the application sentence")
    require(main_text.count("correspondent relationships caught by regulation 33(1)(c), in accordance with regulation 34") >= 2, "Figure 3 must carry the regulation 34 qualification for paragraph (c)")
    require("correspondent relationships with a credit institution or a financial institution" not in html, "paragraph (c) must not be summarised without the regulation 34 qualification")
    faq = html.split("Does a high rating mean the firm must report a suspicion or exit the customer?</summary>")[1].split("</details>")[0]
    require('data-state="assessment">FinCrimeRadar assessment</span>' in faq, "FAQ 5 must carry the FinCrimeRadar assessment label")
    opener = "FinCrimeRadar assessment</span> A high rating raises"
    require(html.count(opener) == 1, "the high score paragraph must open with the FinCrimeRadar assessment label")
    para = html.split(opener)[1].split("</p>")[0]
    require("Regulation 33(7) is a narrower point" in para and "does not address suspicion or exit" in para, "regulation 33(7) must be described narrowly and separately")
    require("Regulation 33(7) points the same way" not in html, "regulation 33(7) must not be offered as authority for the suspicion or exit claim")
    for needle in ("None of the sources read ties a rating band", "No source read addresses it", "the link to defaults is our application"):
        require(needle in main_text, f"required honesty statement missing: {needle}")
    for pid_needle in ("FinCrimeRadar assessment",):
        require(main_text.count(pid_needle) >= 10, "FinCrimeRadar assessment labelling is too sparse")
    require("PRIN" not in main_text and "Consumer Duty" not in main_text, "out-of-scope regimes are mentioned")

    # ---- ledger
    claims = [c for c in ledger if c.get("guide") == GUIDE.name]
    require(len(claims) >= 30, f"expected at least 30 ledger claims, found {len(claims)}")
    require(all(c["claimId"].startswith(CLAIM_PREFIX) for c in claims), "ledger claimId prefix mismatch")
    require(all(c.get("status") == "verified" for c in claims), "unexpected ledger status")
    require(all(c.get("location", "").startswith(GUIDE.name) for c in claims), "ledger locations must name the guide")
    for c in claims:
        for loc in re.findall(r"#([a-z-]+)", c["location"]):
            require(f'id="{loc}"' in html, f"ledger location points to a missing section: #{loc} in {c['claimId']}")
    ledger_urls = {c.get("source", {}).get("url") for c in claims} | {s["url"] for c in claims for s in c.get("additionalSources", [])}
    for url in re.findall(r'<li id="source-\d+"><a href="([^"]+)"', html):
        require(url in ledger_urls, f"cited source has no ledger claim: {url}")
    claim_text = " ".join(c["claimText"] for c in claims)
    for must in ("10%", "30%", "25%", "regulation 33(2)", "SI 2026/621", "quarterly or triggered", "FCG 1.1.7"):
        require(must in claim_text or must.replace("regulation 33(2)", "Regulation 33(2)") in claim_text, f"ledger does not carry the claim: {must}")

    # ---- relations, namespacing and review documents
    require(SLUG in relations, "content-relations entry missing")
    for target in relations[SLUG]:
        require(target in relations and SLUG in relations[target], f"relation is not reciprocal: {SLUG} -> {target}")
        require((ROOT / f"{target}.html").exists(), f"related target has no page: {target}")
        require(f'href="/{target}.html"' in main_html, f"related guide is not linked from the page: {target}")
    classes = {c for attr in re.findall(r'class="([^"]*)"', main_html) for c in attr.split()}
    stray = sorted(c for c in classes if not c.startswith("crs-"))
    require(not stray, f"classes inside the article that are not namespaced: {stray}")
    require("[class*=" not in html and re.search(r'class="[^"]*\b(?:btn|card)\b', html) is None, "class names collide with brand.css and brand.js")
    require(re.search(r"<table\b", html) is None, "no tables: brand.js watches table selectors")
    for doc in REVIEW_DOCS:
        path = ROOT / doc
        require(path.exists() and path.stat().st_size > 2_000, f"review document missing or empty: {doc}")
        require(not re.search("[\u2013\u2014]", path.read_text(encoding="utf-8")), f"em or en dash found in {doc}")
    brief = (ROOT / REVIEW_DOCS[2]).read_text(encoding="utf-8")
    for needle in ("reg 18", "reg 28", "reg 33", "Case Study 17", "FCG 3.2.3"):
        require(needle in brief, f"external review brief does not cover: {needle}")

    print("OK: Customer Risk Scores static contract passed")
    print(f"OK: {len(ids)} unique IDs, 2 graded decisions, 5 figures, 6 patterns in two placements, {len(claims)} ledger claims")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration, AttributeError) as error:
        fail(f"{type(error).__name__}: {error}")
