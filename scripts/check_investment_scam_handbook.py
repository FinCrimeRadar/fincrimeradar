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


CHECKS = [
    ("R1", check_r1),
    ("R2", check_r2),
    ("R3", check_r3),
    ("R4", check_r4),
    ("R6", check_r6),
    ("R8", check_r8),
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
