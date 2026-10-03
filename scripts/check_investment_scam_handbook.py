#!/usr/bin/env python3
"""Static contract checks for the Investment Scam Investigation Handbook.

Each check maps to one requirement in the guide's Requirement Coverage Matrix (R1 to R18).
Checks for a requirement are added in the commit that implements it.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "investment-scam-investigation-handbook"
GUIDE = ROOT / f"{SLUG}.html"
SCRIPT = ROOT / "js" / f"{SLUG}.js"
SITE = "https://fincrimeradar.org"
URL = f"{SITE}/{SLUG}.html"
HEADLINE = "Investment Scam Investigation Handbook"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def html_text() -> str:
    return GUIDE.read_text(encoding="utf-8")


class TextModel(HTMLParser):
    """Visible text of the page, excluding script and style, with the nearest section id for each run."""

    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.section_stack: list[str | None] = []
        self.chunks: list[tuple[str | None, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "section":
            self.section_stack.append(dict(attrs).get("id"))

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag == "section" and self.section_stack:
            self.section_stack.pop()

    def handle_data(self, data: str) -> None:
        if not self.skip and data.strip():
            self.chunks.append((self.section_stack[-1] if self.section_stack else None, data.strip()))

    def section_text(self, section_id: str) -> str:
        return " ".join(text for sid, text in self.chunks if sid == section_id)

    def all_text(self) -> str:
        return " ".join(text for _, text in self.chunks)


def text_model() -> TextModel:
    model = TextModel()
    model.feed(html_text())
    return model


def meta(html: str, key: str, value: str) -> str:
    match = re.search(rf'<meta\s+{key}="{re.escape(value)}"\s+content="([^"]*)"', html)
    require(match is not None, f"missing <meta {key}=\"{value}\">")
    return match.group(1)


def json_ld(html: str) -> list[dict]:
    blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    return [json.loads(block) for block in blocks]


def check_r1() -> None:
    """R1: public title, description, canonical, Article and BreadcrumbList metadata agree."""
    html = html_text()
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    require(title == f"{HEADLINE} | FinCrimeRadar", f"unexpected title: {title}")
    description = meta(html, "name", "description")
    canonical = re.search(r'<link rel="canonical" href="([^"]*)"', html).group(1)
    require(canonical == URL, f"canonical is {canonical}")
    require(meta(html, "property", "og:url") == URL, "og:url differs from canonical")
    require(meta(html, "property", "og:title") == HEADLINE, "og:title differs from the headline")
    require(meta(html, "name", "twitter:title") == HEADLINE, "twitter:title differs from the headline")
    require(meta(html, "property", "og:description") == meta(html, "name", "twitter:description"),
            "og and twitter descriptions differ")
    image = f"{SITE}/{SLUG}-social-card.png"
    require(meta(html, "property", "og:image") == image == meta(html, "name", "twitter:image"), "social image URLs differ")
    require(meta(html, "name", "twitter:card") == "summary_large_image", "twitter:card is not summary_large_image")
    blocks = json_ld(html)
    article = next((b for b in blocks if b.get("@type") == "Article"), None)
    crumbs = next((b for b in blocks if b.get("@type") == "BreadcrumbList"), None)
    require(article is not None and crumbs is not None, "Article and BreadcrumbList structured data are both required")
    require(article["headline"] == HEADLINE, "Article headline differs")
    require(article["description"] == description, "Article description differs from the meta description")
    require(article["mainEntityOfPage"]["@id"] == URL, "Article mainEntityOfPage differs from canonical")
    require(article["image"] == image, "Article image differs")
    require(article["datePublished"] == meta(html, "property", "article:published_time"), "published date differs")
    require(article["dateModified"] == meta(html, "property", "article:modified_time"), "modified date differs")
    require(article["author"]["name"] == "Pratik Zanke" and article["inLanguage"] == "en-GB", "author or language differs")
    items = crumbs["itemListElement"]
    require([i["position"] for i in items] == [1, 2, 3], "breadcrumb positions are not 1, 2, 3")
    require(items[-1]["name"] == HEADLINE and items[-1]["item"] == URL, "breadcrumb leaf differs")
    require(items[0]["item"] == f"{SITE}/knowledge.html", "breadcrumb root differs")
    visible = re.search(r'<div class="isi-breadcrumb".*?</div>', html, re.S).group(0)
    require(HEADLINE in visible and "domain=fraud-detection" in visible and items[1]["item"].endswith("domain=fraud-detection"),
            "visible breadcrumb differs from the structured breadcrumb")
    h1 = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1)
    require(re.sub(r"<[^>]+>", "", h1).startswith(HEADLINE), "h1 does not start with the headline")
    require(html.count("<h1") == 1, "the page must have exactly one h1")
    require('lang="en-GB"' in html.split("<head>")[0], "html lang must be en-GB")


def check_r2() -> None:
    """R2: UK scope, practitioner audience, evidence date and change sensitivity are stated."""
    html = html_text()
    scope = re.search(r'<dl class="isi-scope-inner">(.*?)</dl>', html, re.S).group(1)
    for needle in ("United Kingdom", "practitioners", "3 October 2026", "change-sensitive"):
        require(needle in scope, f"scope strip is missing {needle!r}")
    meta_row = re.search(r'<div class="isi-meta">(.*?)</div>', html, re.S).group(1)
    require("UK" in meta_row and "3 October 2026" in meta_row, "hero meta row is missing UK scope or evidence date")
    model = text_model()
    question = model.section_text("question")
    for needle in ("Intelligence question", "Evidence state", "Decision object", "Uncertainty",
                   "What would change the assessment", "Practitioner outcome", "not legal advice"):
        require(needle in question, f"question section is missing {needle!r}")


def check_r3() -> None:
    """R3: Legitimate Node Trap and four evidence streams are present and labelled as FinCrimeRadar analysis."""
    html = html_text()
    model = text_model()
    trap = model.section_text("node-trap")
    require("Legitimate Node Trap" in trap and "FinCrimeRadar assessment" in trap, "trap must be named and labelled as our assessment")
    require("what this establishes" in trap and "what this does not establish" in trap, "two-sentence discipline is missing")
    require(re.search(r'<h2>The Legitimate Node Trap</h2>', html) is not None, "trap h2 is missing")
    streams = model.section_text("streams")
    require("our own investigative structure" in streams and "not a legal test" in streams, "streams must be labelled as FinCrimeRadar structure")
    order = [m.start() for m in (re.search(f'id="stream-{name}"', html) for name in ("proposition", "identity", "journey", "money"))
             if m]
    require(len(order) == 4 and order == sorted(order), "the four evidence streams must be present in order")
    for number, name in enumerate(("The proposition", "The identity", "The journey", "The money route"), 1):
        require(re.search(rf'<span class="isi-stream-no">{number}</span> {name}</h3>', html) is not None, f"stream {number} heading missing")
    decisions = model.section_text("three-decisions")
    for label in ("Probable investment scam", "Unresolved but high risk", "Genuine investment loss or dispute", "Insufficient evidence"):
        require(label in decisions, f"classification label {label!r} missing")
    require("not legal categories" in decisions, "classification labels must be marked as non-legal")
    for heading in ("1. Classification", "2. Containment and recovery", "3. Escalation and routing"):
        require(heading in decisions, f"decision heading {heading!r} missing")
    change = re.search(r'<ul class="isi-change">(.*?)</ul>', html, re.S).group(1)
    require(change.count("<li>") == 7, "what-would-change must list seven conditions")


def check_r4() -> None:
    """R4: Source, Application and Action stay visibly separate for each regulatory teaching point, with resolving citations."""
    html = html_text()
    section = re.search(r'<section class="isi-section" id="source-limits">.*?</section>', html, re.S).group(0)
    parts = re.split(r'<div class="isi-teach" id="([^"]+)">', section)
    teaching = list(zip(parts[1::2], parts[2::2]))
    require(len(teaching) == 6, f"expected six regulatory teaching points, found {len(teaching)}")
    for teach_id, body in teaching:
        blocks = re.findall(r'<div class="isi-saa-block"><h4>(\w+) <span class="isi-state" data-state="(\w+)">[^<]*</span></h4><p>(.*?)</p></div>', body, re.S)
        require([b[0] for b in blocks] == ["Source", "Application", "Action"], f"{teach_id} must have Source, Application, Action in order")
        require([b[1] for b in blocks] == ["established", "assessment", "assessment"], f"{teach_id} evidence states are wrong")
        require(re.search(r'href="#source-\d"', blocks[0][2]) is not None, f"{teach_id} Source block has no citation")
        for block in blocks[1:]:
            require('href="#source-' not in block[2], f"{teach_id} {block[0]} block must not cite as if it were the authority")
    # Every in-page link resolves, every source is cited in the body, and the list is complete.
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    broken = sorted({h for h in re.findall(r'href="#([^"]+)"', html) if h not in ids})
    require(not broken, f"in-page links do not resolve: {broken}")
    body_html = html.split('<section class="isi-section isi-sources"')[0]
    cited = set(re.findall(r'href="#source-(\d)"', body_html))
    require(cited == {str(n) for n in range(1, 9)}, f"sources cited in the body: {sorted(cited)}")
    sources = re.search(r'<section class="isi-section isi-sources".*?</section>', html, re.S).group(0)
    entries = re.findall(r'<li id="source-(\d)"><a href="(https://[^"]+)"', sources)
    require([e[0] for e in entries] == [str(n) for n in range(1, 9)], "source list must hold sources 1 to 8 in order")
    require("Last reviewed" in sources and "not legal advice" in sources, "sources section needs its review date and scope note")


EVIDENCE_ROWS = [
    "FCA firm match", "Warning List hit", "No Warning List hit", "Companies House record",
    "Small withdrawal", "Genuine exchange", "Platform balance", "Beneficiary name match",
]
EVIDENCE_COLUMNS = ["Evidence", "What it may establish", "What it cannot establish alone", "Next check"]


def check_r8() -> None:
    """R8: the evidence table is complete in the initial HTML, with a label on every cell for narrow screens."""
    html = html_text()
    section = re.search(r'<section class="isi-section" id="evidence-table">.*?</section>', html, re.S).group(0)
    table = re.search(r'<table class="isi-evidence".*?</table>', section, re.S)
    require(table is not None, "evidence table is missing from the initial HTML")
    table_html = table.group(0)
    head = re.findall(r'<th scope="col"[^>]*>(.*?)</th>', table_html)
    require(head == EVIDENCE_COLUMNS, f"column headings are {head}")
    rows = re.findall(r'<tr role="row"><th scope="row"[^>]*data-label="Evidence">(.*?)</th>(.*?)</tr>', table_html, re.S)
    require([r[0] for r in rows] == EVIDENCE_ROWS, f"evidence rows are {[r[0] for r in rows]}")
    for name, rest in rows:
        cells = re.findall(r'<td[^>]*data-label="([^"]+)">(.*?)</td>', rest, re.S)
        require([c[0] for c in cells] == EVIDENCE_COLUMNS[1:], f"{name} cell labels are {[c[0] for c in cells]}")
        require(all(len(re.sub(r"<[^>]+>", "", c[1]).strip()) > 15 for c in cells), f"{name} has an empty or trivial cell")
    require("caption" in table_html, "the table needs a caption")
    require("Companies House row is a FinCrimeRadar investigative recommendation" in section, "Companies House row must be labelled as our recommendation")
    require('class="isi-evidence"' in section and "data-table" not in section and "ref-table" not in section and "compare-table" not in section,
            "table must not use the classes brand.js wraps")


GRADE_LABELS = {
    "best": "Best supported by the evidence",
    "incomplete": "Contains a true point, stops short",
    "unsupported": "Not supported by the evidence",
}
EXPECTED_OPTION_GRADES = {
    "clone-firm": {"a": "unsupported", "b": "best", "c": "unsupported", "d": "incomplete"},
    "real-exchange": {"a": "unsupported", "b": "best", "c": "incomplete", "d": "unsupported"},
}
BLAME_WORDS = ("negligent", "careless", "gullible", "naive", "complicit", "foolish", "at fault")


def scenario_sections(html: str) -> dict[str, str]:
    found = re.findall(r'(<section class="isi-section" id="scenario-(?:one|two)" data-scenario="([^"]+)">.*?</section>)', html, re.S)
    return {scenario: block for block, scenario in found}


def check_r6() -> None:
    """R6: two distinct scenarios with graded options, complete Source, Application, Action reasoning and accessible feedback."""
    html = html_text()
    scenarios = scenario_sections(html)
    require(sorted(scenarios) == sorted(EXPECTED_OPTION_GRADES), f"scenarios found: {sorted(scenarios)}")
    tags = [re.search(r'isi-scenario-tag">([^<]*)<', block).group(1) for block in scenarios.values()]
    require(len(set(tags)) == 2, "the two scenarios must target different evidence streams")
    for scenario, block in scenarios.items():
        form = re.search(r'<form class="isi-choice" data-decision-form data-scenario-id="([^"]+)".*?</form>', block, re.S)
        require(form is not None and form.group(1) == scenario, f"{scenario} decision form is missing or mislabelled")
        form_html = form.group(0)
        radio_pattern = (r'<input type="radio" name="[^"]+" value="(\w)" data-grade="(\w+)" '
                         r'data-grade-label="([^"]+)"><span><strong>([A-D])\.</strong> (.*?)</span>')
        radios = re.findall(radio_pattern, form_html, re.S)
        require([r[0] for r in radios] == ["a", "b", "c", "d"], f"{scenario} must offer four options in order")
        require({r[0]: r[1] for r in radios} == EXPECTED_OPTION_GRADES[scenario], f"{scenario} option grades differ from the contract")
        require(all(GRADE_LABELS[r[1]] == r[2] for r in radios), f"{scenario} grade labels differ from the contract")
        require(sum(1 for r in radios if r[1] == "best") == 1, f"{scenario} must have exactly one best option")
        require('<p class="isi-feedback" aria-live="polite" role="status"></p>' in form_html, f"{scenario} feedback region needs aria-live and role=status")
        require("<legend>" in form_html and "<fieldset>" in form_html, f"{scenario} options must sit in a fieldset with a legend")
        pieces = re.split(r'<div class="isi-optfb" id="([^"]+)" data-option="(\w)" data-grade="(\w+)">', block)
        analyses = list(zip(pieces[1::4], pieces[2::4], pieces[3::4], pieces[4::4]))
        require([a[1] for a in analyses] == ["a", "b", "c", "d"], f"{scenario} must analyse every option, found {[a[1] for a in analyses]}")
        for (analysis_id, option, grade, body), radio in zip(analyses, radios):
            require(grade == radio[1] and analysis_id == f"optfb-{scenario}-{option}", f"{scenario} analysis {option} does not match its option")
            require(radio[4].strip() in body, f"{scenario} analysis {option} does not restate its option")
            require(f'<span class="isi-grade" data-grade="{grade}">{GRADE_LABELS[grade]}</span>' in body, f"{scenario} analysis {option} badge is wrong")
            layers = re.findall(r'<div class="isi-saa-block"><h4>(\w+)</h4><p>(.*?)</p></div>', body, re.S)
            require([l[0] for l in layers] == ["Source", "Application", "Action"], f"{scenario} analysis {option} needs Source, Application, Action")
            require(all(len(re.sub(r"<[^>]+>", "", l[1])) > 60 for l in layers), f"{scenario} analysis {option} has a thin layer")
            require(re.search(r'href="#source-\d"', layers[0][1]) is not None, f"{scenario} analysis {option} Source layer is uncited")
        visible = re.sub(r"<[^>]+>", " ", block).lower()
        for word in BLAME_WORDS:
            require(word not in visible, f"{scenario} uses blaming wording {word!r}")


def check_r7() -> None:
    """R7: each scenario carries a material counterfactual, and counterfactuals do not stand in for the second scenario."""
    html = html_text()
    scenarios = scenario_sections(html)
    require(len(scenarios) == 2, "two scenarios must remain after adding counterfactuals")
    required = {
        "clone-firm": ("would materially weaken", "distinguish fraud from an investment loss or a service dispute"),
        "real-exchange": ("would materially weaken", "Loss of market value alone would not establish fraud"),
    }
    for scenario, block in scenarios.items():
        found = re.findall(r'<div class="isi-counterfactual" id="counterfactual-([^"]+)">(.*?)</div>', block, re.S)
        require(len(found) == 1 and found[0][0] == scenario, f"{scenario} needs exactly one counterfactual")
        body = found[0][1]
        require("Counterfactual: change one fact" in body and 'data-state="assessment"' in body, f"{scenario} counterfactual heading or label is missing")
        require("<strong>The fact changed.</strong>" in body and "<strong>What follows.</strong>" in body, f"{scenario} counterfactual needs the changed fact and its effect")
        for needle in required[scenario]:
            require(needle in body, f"{scenario} counterfactual is missing {needle!r}")
        require("<form" not in body and "<input" not in body, f"{scenario} counterfactual must be static")
        require(block.index('class="isi-optfb-set"') < block.index("isi-counterfactual"), f"{scenario} counterfactual must follow the option analyses")
    require(html.count('data-decision-form') == 2, "counterfactuals must not add decision forms")


PATTERN_IDS = ["borrowed-badge", "screen-money", "scope-verdict", "waiting-room", "second-hook"]


def check_r9() -> None:
    """R9: five Risk, Signal, Response cards and a five-question knowledge check with visible feedback."""
    html = html_text()
    section = re.search(r'<section class="isi-section" id="patterns">.*?</section>', html, re.S).group(0)
    pieces = re.split(r'<div class="isi-pattern" data-pattern-id="([^"]+)">', section)
    cards = list(zip(pieces[1::2], pieces[2::2]))
    require([c[0] for c in cards] == PATTERN_IDS, f"pattern cards found: {[c[0] for c in cards]}")
    for number, (pattern_id, body) in enumerate(cards, 1):
        require(re.search(rf"<h3>{number}\. [^<]+</h3>", body) is not None, f"{pattern_id} needs a numbered metaphor-style name")
        require('<p class="isi-metaphor">' in body, f"{pattern_id} needs its one short explanatory line")
        lines = re.findall(r"<div><dt>(\w+)</dt><dd>(.*?)</dd></div>", body, re.S)
        require([l[0] for l in lines] == ["Risk", "Signal", "Response"], f"{pattern_id} needs Risk, Signal, Response in order")
        require(all(len(l[1]) > 25 for l in lines), f"{pattern_id} has a thin line")
    # The same card appears a second time, inline, where its pattern is introduced, with identical wording.
    outside = html.replace(section, "")
    inline = re.findall(r'<div class="isi-pattern isi-pattern-inline" data-pattern-id="([^"]+)" data-pattern-placement="inline">(.*?)\n  </div>', outside, re.S)
    require(sorted(i[0] for i in inline) == sorted(PATTERN_IDS), f"inline pattern placements found: {[i[0] for i in inline]}")

    def flat(body: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<h3>\d\. ", "<h3>", body)).strip()

    closing_by_id = dict(cards)
    for pattern_id, body in inline:
        require(flat(body) == flat(closing_by_id[pattern_id].rsplit("\n    </div>", 1)[0]),
                f"inline {pattern_id} wording differs from the closing card")
    quiz = re.search(r'<section class="isi-section isi-quiz" id="knowledge-check">.*?</section>', html, re.S).group(0)
    fieldsets = re.findall(r"<fieldset><legend>(\d)\. (.*?)</legend>(.*?)</fieldset>", quiz, re.S)
    require([f[0] for f in fieldsets] == ["1", "2", "3", "4", "5"], "the knowledge check needs five numbered questions")
    positions = []
    for number, _, body in fieldsets:
        radios = re.findall(r'<input type="radio" name="q(\d)" value="(\w)"( data-correct="true")?>', body)
        require(len(radios) == 3 and all(r[0] == number for r in radios), f"question {number} needs three options in its own group")
        correct = [r[1] for r in radios if r[2]]
        require(len(correct) == 1, f"question {number} needs exactly one correct option")
        positions.append(correct[0])
    require(max(positions.count(p) for p in "abc") < 4, f"correct answers sit in the same position too often: {positions}")
    require('id="knowledgeFeedback" class="isi-feedback" aria-live="polite" role="status"' in quiz, "knowledge check feedback needs aria-live and role=status")
    notes = re.search(r'<details><summary>Answer notes</summary>(.*?)</details>', quiz, re.S).group(1)
    items = re.findall(r"<p><strong>Question (\d)\.</strong>(.*?)</p>", notes, re.S)
    require([i[0] for i in items] == ["1", "2", "3", "4", "5"], "answer notes must cover all five questions")
    for number, text in items:
        require(all(f"<em>{layer}:</em>" in text for layer in ("Source", "Application", "Action")), f"answer note {number} needs Source, Application, Action")


def check_r10() -> None:
    """R10: the FAQ uses native disclosure, with a skip link and visible focus rules for every control."""
    html = html_text()
    faq = re.search(r'<section class="isi-section isi-details" id="faq">.*?</section>', html, re.S).group(0)
    items = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", faq, re.S)
    require(len(items) == 6, f"expected six FAQ items, found {len(items)}")
    require(all(len(answer) > 120 for _, answer in items), "an FAQ answer is too thin")
    body = html.split("<body>", 1)[1]
    first_link = re.search(r"<a [^>]*>", body).group(0)
    require('class="isi-skip"' in first_link and 'href="#main-content"' in first_link, "the skip link must be the first link in the body")
    require('<main id="main-content" class="isi-article" tabindex="-1">' in html, "the skip target must be focusable with tabindex=-1")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    for selector in ("a:focus-visible", "summary:focus-visible", ".isi-action:focus-visible",
                     ".isi-option:has(input:focus-visible)", ".nav-hamburger:focus-visible", "input:focus-visible"):
        require(selector in css, f"missing visible focus rule for {selector}")
    script = SCRIPT.read_text(encoding="utf-8")
    require(not re.search(r"querySelector(?:All)?\(\s*['\"][^'\"]*(?:details|summary)", script) and ".open =" not in script,
            "the FAQ must not depend on JavaScript")
    require(not re.search(r"\sonclick=|\sonkeydown=", html), "inline event handlers are not allowed")


def check_r11() -> None:
    """R11: reduced motion, touch targets, scroll padding under the sticky nav and polite live regions are in place."""
    html = html_text()
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    require("@media(prefers-reduced-motion:reduce)" in css and "transition-duration:.01ms!important" in css and "animation-duration:.01ms!important" in css,
            "a reduced-motion block that neutralises transitions and animations is required")
    require("html{scroll-behavior:smooth}" in css and "html{scroll-behavior:auto}" in css, "smooth scrolling must be switched off under reduced motion")
    require("scroll-padding-top:" in css, "scroll padding is needed so focus is not hidden by the sticky nav")
    for rule in (".isi-action{min-height:44px", ".isi-option{min-height:44px", ".isi-details summary{min-height:44px"):
        require(rule in css, f"touch target rule missing: {rule}")
    live = re.findall(r'<[^>]*aria-live="([^"]+)"[^>]*>', html)
    require(len(live) == 4 and set(live) == {"polite"}, f"expected four polite live regions (two scenarios, the quiz and the image export), found {live}")
    for tag in re.findall(r'<[^>]*aria-live="polite"[^>]*>', html):
        require('role="status"' in tag, f"live region without role=status: {tag}")


CLAIM_PREFIX = "investment-scam-handbook."
LEDGER = ROOT / "verification-ledger.json"
# claim id -> (source numbers it covers, phrases that must appear in the visible body copy)
CLAIM_PLAN = {
    "authorisation-registration-permissions.001": ((1,), [
        "being authorised means a firm must meet certain standards", "being registered means it cannot provide regulated products",
        "firms it authorises can offer both regulated and unregulated products",
        "will greatly reduce the risk of harm but will not remove all risk"]),
    "clone-contact-match.002": ((1,), [
        "a clone firm as a copy of a genuine, authorised firm", "match those on the firm checker",
        "provided and confirmed by the firm", "check with the principal"]),
    "warning-list-non-clearance.003": ((2,), [
        "may still be unauthorised or be a scam", "often change their names", "overseas regulators"]),
    "fake-platform-returns.004": ((4,), [
        "manipulate software to fake prices and investment returns", "until they try to sell"]),
    "crypto-promotion-scope.005": ((5,), [
        "regardless of whether the firm is based overseas or what technology is used",
        "mobile apps, social media posts and online advertising"]),
    "reimbursement-route-scope.006": ((6, 7), [
        "came into force on 7 october 2024",
        "do not cover payments in cryptocurrency or payments to an account under the consumer's control",
        "general guidance that consolidates earlier publications"]),
    "outside-scheme-review.007": ((6,), [
        "will still investigate whether the firm could have done more", "payments to cryptocurrency providers",
        "card payments to a genuine merchant", "payments to an overseas payee", "cash withdrawals"]),
    "report-and-recovery-scam.008": ((3, 4), [
        "tell their bank immediately", "report scams to report fraud", "cannot help a victim get their money back",
        "recovery room scammers", "buy back the investment after a fee is paid"]),
    "preserve-correspondence.009": ((8,), [
        "keep records of all contact and correspondence", "not all disputes are scams"]),
}
# The source list prints these last-updated dates, and the ledger records the same date for the primary source.
PAGE_DATES = {1: "22 September 2026", 2: "30 June 2026", 3: "19 January 2026", 4: "16 February 2026", 5: "6 February 2026"}


def check_r5() -> None:
    """R5: nine ledger claims cover the final wording, with matching sources, dates and no unmapped citation."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_ledger as ledger

    entries = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = ledger.validate(entries)
    require(not errors, f"ledger does not validate: {errors[:3]}")
    ours = {e["claimId"]: e for e in entries if e["claimId"].startswith(CLAIM_PREFIX)}
    require(sorted(ours) == sorted(CLAIM_PREFIX + key for key in CLAIM_PLAN), f"ledger claim ids are {sorted(ours)}")
    html = html_text()
    sources = re.search(r'<section class="isi-section isi-sources".*?</section>', html, re.S).group(0)
    listed = {int(n): (url, li) for n, url, li in re.findall(r'<li id="source-(\d)"><a href="([^"]+)"[^>]*>.*?</a>(.*?)</li>', sources, re.S)}
    body = html.split('<section class="isi-section isi-sources"')[0]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).lower()
    text = text.replace("’", "'")
    for key, (numbers, phrases) in CLAIM_PLAN.items():
        entry = ours[CLAIM_PREFIX + key]
        require(entry["guide"] == GUIDE.name and entry["status"] == "verified" and entry["claimType"] == "regulatory", f"{key} metadata is wrong")
        urls = [entry["source"]["url"]] + [s["url"] for s in entry.get("additionalSources", [])]
        require(urls == [listed[n][0] for n in numbers], f"{key} ledger sources {urls} differ from page sources {numbers}")
        for phrase in phrases:
            require(phrase in text, f"{key}: body copy is missing the claimed wording {phrase!r}")
        date = entry["source"]["date"]
        if numbers[0] in PAGE_DATES:
            printed = PAGE_DATES[numbers[0]]
            require(printed in listed[numbers[0]][1], f"page source list no longer prints {printed}")
            require(date == __import__("datetime").datetime.strptime(printed, "%d %B %Y").strftime("%Y-%m-%d"), f"{key} source date {date} differs from the page")
        require(entry["reviewDue"] > entry["verifiedOn"], f"{key} reviewDue must follow verifiedOn")
    covered = {n for numbers, _ in CLAIM_PLAN.values() for n in numbers}
    cited = {int(n) for n in re.findall(r'href="#source-(\d)"', body)}
    require(cited <= covered, f"sources cited in the body with no ledger claim: {sorted(cited - covered)}")
    flagged = {key.rsplit(".", 1)[1] for key in CLAIM_PLAN}
    for number in ("001", "005", "006", "007"):
        require("independent regulatory review" in ours[next(k for k in ours if k.endswith("." + number))]["note"], f"claim {number} must be flagged for independent review")
    require(flagged == {f"{n:03d}" for n in range(1, 10)}, "claim numbers must run 001 to 009")


SHARED_CLASSES = {"nav-brand", "nav-links", "nav-cta", "nav-hamburger", "mobile-nav", "open", "js"}
ALLOWED_SCRIPT_SOURCES = {
    "https://fundingchoicesmessages.google.com/i/pub-1158691611711023?ers=1",
    "https://www.googletagmanager.com/gtag/js?id=G-FC1VMTE7JH",
    "/js/investment-scam-investigation-handbook.js", "/js/site-chrome.js", "/brand.js",
}
SHARED_FILES = ("brand.css", "brand.js", "js/site-chrome.js", "partials")
FORBIDDEN_JS = ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage.setItem", "sessionStorage", "document.cookie",
                "eval(", "new Function", "indexedDB", "importScripts", "innerHTML")


def check_r12() -> None:
    """R12: no new shared architecture: namespaced classes, standard scripts only, no network or storage in the page script."""
    html = html_text()
    css = re.sub(r"/\*.*?\*/", "", re.search(r"<style>(.*?)</style>", html, re.S).group(1), flags=re.S)
    selectors = re.findall(r"([^{}@]+)\{", css)
    css_classes = {c for sel in selectors for c in re.findall(r"\.([A-Za-z_][\w-]*)", sel)}
    stray = sorted(c for c in css_classes if not c.startswith("isi-") and c not in SHARED_CLASSES)
    require(not stray, f"CSS classes outside the isi- namespace: {stray}")
    used = {c for attr in re.findall(r'\sclass="([^"]*)"', html) for c in attr.split()}
    stray_used = sorted(c for c in used if not c.startswith("isi-") and c not in SHARED_CLASSES)
    require(not stray_used, f"HTML classes outside the isi- namespace: {stray_used}")
    watched = sorted(c for c in used if "card" in c)
    require(not watched, f"class names brand.js reveals by substring: {watched}")
    scripts = re.findall(r'<script[^>]*\ssrc="([^"]+)"', html)
    require(set(scripts) == ALLOWED_SCRIPT_SOURCES, f"unexpected script sources: {sorted(set(scripts) ^ ALLOWED_SCRIPT_SOURCES)}")
    require(len(re.findall(r"<script(?![^>]*\ssrc=)(?![^>]*ld\+json)", html)) == 2, "only the standard consent bootstrap and Funding Choices inline scripts are allowed")
    require(not re.search(r"@import|<link[^>]+rel=\"stylesheet\"[^>]+href=\"(?!/brand\.css|https://fonts\.googleapis\.com)", html), "unexpected stylesheet")
    script = SCRIPT.read_text(encoding="utf-8")
    found = [token for token in FORBIDDEN_JS if token in script]
    require(not found, f"page script uses forbidden capabilities: {found}")
    require(script.count("localStorage") == 1 and "localStorage.getItem('fcr_cookie_consent_v2')" in script, "the script may only read the existing consent key")
    require("window.gtag('event'" in script and script.count("window.gtag(") == 1, "telemetry must go only through the existing gtag")
    require(not (ROOT / "js" / "isi-shared.js").exists(), "no shared helper module may be added")
    try:
        import subprocess
        base = subprocess.run(["git", "log", "--format=%H", "--grep=Investment Scam Handbook foundation"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout.split()
        if base:
            changed = subprocess.run(["git", "diff", "--name-only", f"{base[-1]}~1", "HEAD", "--", *SHARED_FILES], cwd=ROOT,
                                     capture_output=True, text=True, check=True).stdout.split()
            require(not changed, f"shared files changed since the guide work began: {changed}")
    except (OSError, subprocess.CalledProcessError):
        pass


RELATED_SLUGS = [
    "app-scam-decision-framework", "fraud-investigation-playbook",
    "money-mule-or-victim-case-file", "scam-compound-money-laundering-guide",
]


def check_r13() -> None:
    """R13: Knowledge Hub card, sitemap, content relations, guide counts and reading time are consistent."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_de_risking_judgement_call import KnowledgeCountParser
    from word_count import word_count

    html = html_text()
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    counts = KnowledgeCountParser()
    counts.feed(knowledge)
    declared = counts.standalone_guides + counts.series_guides
    require(counts.count_text("khHeroCount") == counts.count_text("khStatGuides") == declared,
            f"Knowledge Hub counts differ: hero={counts.count_text('khHeroCount')}, stat={counts.count_text('khStatGuides')}, declared={declared}")
    cards = re.findall(rf'<a href="/{SLUG}\.html" class="kh-article-card"([^>]*)>(.*?)</a>', knowledge, re.S)
    require(len(cards) == 1, f"expected one Knowledge Hub card, found {len(cards)}")
    attrs, inner = cards[0]
    require('data-date="2026-10-03"' in attrs and 'data-cats="fraud-detection"' in attrs, "card needs data-date and the fraud category")
    require('<span class="kh-format-label">Guide</span>' in inner, "card format label must be Guide")
    minutes = int(re.search(r'<span class="kh-read">(\d+) MIN</span>', inner).group(1))
    hero_minutes = int(re.search(r"(\d+) min read", html).group(1))
    require(minutes == hero_minutes, f"card says {minutes} MIN but the hero says {hero_minutes} min read")
    words = word_count(html)
    require(words / 223 <= minutes <= words / 163, f"{minutes} min is outside the site interquartile reading speed for {words} words")
    require(abs(minutes - round(words / 181)) <= 2, f"{minutes} min differs from the site median speed estimate {round(words / 181)}")
    description = re.search(r'<div class="kh-item-desc">(.*?)</div>', inner, re.S).group(1)
    page_description = meta(html, "name", "description")
    require(description == page_description, "card description differs from the page description")
    title = re.search(r'<div class="kh-item-title">(.*?)</div>', inner, re.S).group(1)
    require(title.startswith(HEADLINE), "card title differs from the headline")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    block = re.findall(rf"<url>\s*<loc>{re.escape(URL)}</loc>\s*<changefreq>monthly</changefreq>\s*<priority>0\.7</priority>\s*</url>", sitemap)
    require(len(block) == 1 and sitemap.count(URL) == 1, "sitemap needs exactly one entry in the comparable guide format")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    require(relations.get(SLUG) == RELATED_SLUGS, f"relation set is {relations.get(SLUG)}")
    for target in RELATED_SLUGS:
        require(SLUG in relations.get(target, []), f"relation is not reciprocal: {target}")
        require((ROOT / f"{target}.html").exists(), f"related guide {target} does not exist")
    related = re.search(r'<section class="isi-section" id="related">.*?</section>', html, re.S).group(0)
    require(re.findall(r'<a href="/([^"]+)\.html">', related) == RELATED_SLUGS, "the on-page related links must match the relation set")


CLAIM_VOCABULARY = re.compile(r"FCA|Ombudsman|PSR|Payment Systems|regulator|authoris|Warning List|reimburs|Report Fraud|Companies House", re.I)


def check_r14() -> None:
    """R14: the social card, the one-screen summary and the saved image carry nothing the reviewed body copy does not."""
    import struct

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_social_card import extract_title_subtitle

    html = html_text()
    summary = re.search(r'<section class="isi-section isi-summary" id="operational-summary">.*?</section>', html, re.S).group(0)
    body = html.replace(summary, "")
    body_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
    lists = re.findall(r'<ol class="isi-summary-list" data-summary="(\w+)">(.*?)</ol>', summary, re.S)
    require([name for name, _ in lists] == ["streams", "decisions"], "summary needs a streams list and a decisions list")
    for name, expected in (("streams", 4), ("decisions", 3)):
        items = re.findall(r"<li><strong>([^<]+)</strong> <span>([^<]+)</span></li>", dict(lists)[name])
        require(len(items) == expected, f"summary {name} list needs {expected} items, found {len(items)}")
        for label, sentence in items:
            require(sentence in body_text, f"summary line is not verbatim body copy: {sentence!r}")
    require("adds no new claim" in summary, "the summary must say it adds no new claim")
    require('id="saveSummaryImage"' in html and 'id="saveSummaryStatus" aria-live="polite" role="status"' in html, "the save button and its status region are required")
    require("#saveSummaryImage{display:none}.js #saveSummaryImage{display:inline-block}" in html, "the save button must stay hidden without JavaScript")
    script = SCRIPT.read_text(encoding="utf-8")
    start = script.index("function exportSummary")
    literals = re.findall(r"'([^'\\]*)'", script[start:]) + re.findall(r'"([^"\\]*)"', script[start:])
    claims = [l for l in literals if CLAIM_VOCABULARY.search(l)]
    require(not claims, f"the image export carries wording of its own that looks like a claim: {claims}")
    require("querySelector('h3')" in script and "isiClosingPatterns" in script and "isiOperationalSummary" in script, "the export must read the page's own text")
    card = ROOT / f"{SLUG}-social-card.png"
    require(card.exists(), "social card is missing")
    data = card.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    require(data[:8] == b"\x89PNG\r\n\x1a\n" and (width, height) == (1200, 630), f"social card is {width}x{height}")
    require(len(data) <= 400_000, f"social card is {len(data)} bytes, over the 400KB ceiling")
    h1_title, h1_subtitle = extract_title_subtitle(GUIDE)
    require((h1_title, h1_subtitle) == (HEADLINE, "Reconstructing the offer, identity and money route"), f"the card source text is {(h1_title, h1_subtitle)}")


def js_string_literals(source: str) -> list[str]:
    """String literals in the page script, skipping comments. The script has no template literals."""
    require("`" not in source, "the page script must not use template literals")
    found, i, n = [], 0, len(source)
    while i < n:
        two = source[i:i + 2]
        if two == "//":
            i = source.find("\n", i)
            i = n if i == -1 else i
        elif two == "/*":
            i = source.find("*/", i) + 2
        elif source[i] in "'\"":
            quote, j, chars = source[i], i + 1, []
            while j < n and source[j] != quote:
                if source[j] == "\\":
                    chars.append(source[j + 1])
                    j += 1
                else:
                    chars.append(source[j])
                j += 1
            found.append("".join(chars))
            i = j + 1
        else:
            i += 1
    return found


ALLOWED_LONG_LITERALS = {
    "investment-scam-investigation-handbook-summary.png",
    "Choose an option before recording the decision.",
    " of 5. The answer notes below the questions set out the Source, Application and Action for each.",
}


def check_r15() -> None:
    """R15: material content is static HTML, the script only reveals and scores, and failure leaves the page readable."""
    html = html_text()
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    for rule in (".isi-choice .isi-action{display:none}.js .isi-choice .isi-action{display:inline-block}",
                 ".js .isi-optfb-set:not([data-revealed=\"true\"]){display:none}",
                 "#knowledgeForm .isi-action{display:none}.js #knowledgeForm .isi-action{display:inline-block}",
                 "#saveSummaryImage{display:none}.js #saveSummaryImage{display:inline-block}"):
        require(rule in css, f"progressive enhancement rule missing: {rule}")
    hidden = [rule for rule in re.findall(r"([^{}]+)\{[^}]*display:none", css)
              if not re.search(r"\.js |\.isi-action|saveSummaryImage|\.isi-evidence thead|\.nav-links|\.nav-hamburger|\.mobile-nav|@media|\.isi-choice|#knowledgeForm", rule)]
    require(not hidden, f"CSS hides content outside the JavaScript-gated controls: {hidden}")
    require("hidden" not in re.sub(r"visibility:hidden|overflow:hidden", "", re.sub(r"<style>.*?</style>", "", html, flags=re.S)).lower().replace("aria-hidden=\"true\"", ""),
            "no element may be hidden through an attribute")
    main = html.split("<main", 1)[1].split("</main>", 1)[0]
    require(main.count("aria-hidden") == 0, "material content must not be aria-hidden")
    require("class=\"js\"" not in html.split("</head>")[0] and 'classList.add(\'js\')' in SCRIPT.read_text(encoding="utf-8"), "the js class is set by the script, last")
    script = SCRIPT.read_text(encoding="utf-8")
    require(script.rstrip().endswith("document.documentElement.classList.add('js');\n}());"), "the js class must be the last statement the script runs")
    long_literals = {literal for literal in js_string_literals(script) if len(literal) > 45}
    require(long_literals <= ALLOWED_LONG_LITERALS, f"the script carries long wording of its own: {sorted(long_literals - ALLOWED_LONG_LITERALS)}")
    require("createElement('p'" not in script and not re.search(r"(?<!feedback)(?<!status)(?<!link)\.textContent = '", script),
            "the script must not build reasoning text")


TELEMETRY_ALLOW_LIST = {
    "scenario_complete": {"guide_id", "scenario_id"},
    "knowledge_check_complete": {"guide_id", "score", "total"},
    "card_export": {"guide_id", "export_type"},
}


def check_r16() -> None:
    """R16: telemetry is consent-gated, aggregate only, and carries no case, customer, wallet, payment, free-text or choice data."""
    script = SCRIPT.read_text(encoding="utf-8")
    html = html_text()
    calls = re.findall(r"emitAggregateEvent\(([^,]+),\s*'([^']+)',\s*\{(.*?)\}\s*\)", script, re.S)
    require(sorted(c[1] for c in calls) == sorted(TELEMETRY_ALLOW_LIST), f"event names are {[c[1] for c in calls]}")
    for _, name, body in calls:
        keys = set(re.findall(r"(\w+):", body))
        require(keys == TELEMETRY_ALLOW_LIST[name], f"{name} sends {sorted(keys)}, allowed {sorted(TELEMETRY_ALLOW_LIST[name])}")
        require(".value" not in body and "dataset.grade" not in body and "textContent" not in body, f"{name} parameters read from a choice or text")
    require(script.count("window.gtag(") == 1, "gtag may only be called from the one gated helper")
    helper = script[script.index("function emitAggregateEvent"):script.index("var menuButton")]
    require("consentGranted()" in helper and "fcr_cookie_consent_v2" in script and "=== 'accepted'" in script, "telemetry must check the existing consent state")
    require("try {" in helper and "catch" in helper, "an analytics failure must be contained")
    require("sentEvents[key]" in helper and "sentEvents[key] = true" in helper, "each event must send at most once per page load")
    require("GUIDE_ID = 'investment_scam_investigation_handbook'" in script, "guide id constant is missing")
    require(not re.search(r'<(textarea|select)\b|type="(text|email|tel|search|url|number|password|file)"|contenteditable', html, re.I),
            "the page must collect no free text, files or personal details")
    require(html.count("<input") == html.count('type="radio"'), "the only form inputs are radio buttons")
    require(not re.search(r"gtag\(['\"]set['\"]|user_id|setUserId|client_id|localStorage\.setItem|document\.cookie", script), "no identifiers or storage may be written")


CHECKS = [
    ("R1", check_r1),
    ("R2", check_r2),
    ("R3", check_r3),
    ("R4", check_r4),
    ("R5", check_r5),
    ("R6", check_r6),
    ("R7", check_r7),
    ("R8", check_r8),
    ("R9", check_r9),
    ("R10", check_r10),
    ("R11", check_r11),
    ("R12", check_r12),
    ("R13", check_r13),
    ("R14", check_r14),
    ("R15", check_r15),
    ("R16", check_r16),
]


def main() -> int:
    failures = 0
    for name, check in CHECKS:
        try:
            check()
            print(f"OK: {name} {check.__doc__.split(':', 1)[1].strip() if check.__doc__ else ''}")
        except AssertionError as error:
            failures += 1
            print(f"FAIL: {name} {error}")
    print("PASS" if not failures else f"{failures} check(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
