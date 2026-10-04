#!/usr/bin/env python3
"""Static contract checks for the Financial Crime Information Sharing guide.

Each check maps to one requirement in the guide's Requirement Coverage Matrix (F1 to F15).
Checks for a requirement are added in the commit that implements it.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "financial-crime-information-sharing-guide"
GUIDE = ROOT / f"{SLUG}.html"
SCRIPT = ROOT / "js" / "financial-crime-information-sharing.js"
SITE = "https://fincrimeradar.org"
URL = f"{SITE}/{SLUG}.html"
HEADLINE = "Financial Crime Information Sharing: Can I Tell Another Bank?"


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


def check_f1() -> None:
    """F1: public title, description, canonical, Article and BreadcrumbList metadata agree."""
    html = html_text()
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    require(title == f"{HEADLINE} | FinCrimeRadar", f"unexpected title: {title}")
    description = meta(html, "name", "description")
    canonical = re.search(r'<link rel="canonical" href="([^"]*)"', html).group(1)
    require(canonical == URL, f"canonical is {canonical}")
    require(meta(html, "property", "og:url") == URL, "og:url differs from canonical")
    require(meta(html, "property", "og:title") == HEADLINE, "og:title differs from the headline")
    require(meta(html, "name", "twitter:title") == HEADLINE, "twitter:title differs from the headline")
    require(meta(html, "property", "og:description") == meta(html, "name", "twitter:description"), "og and twitter descriptions differ")
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
    require(article["articleSection"] == "Framework", "articleSection must be Framework")
    items = crumbs["itemListElement"]
    require([i["position"] for i in items] == [1, 2, 3], "breadcrumb positions are not 1, 2, 3")
    require(items[-1]["name"] == HEADLINE and items[-1]["item"] == URL, "breadcrumb leaf differs")
    require(items[0]["item"] == f"{SITE}/knowledge.html", "breadcrumb root differs")
    visible = re.search(r'<div class="fis-breadcrumb".*?</div>', html, re.S).group(0)
    require(HEADLINE in visible and "domain=aml-programme" in visible and items[1]["item"].endswith("domain=aml-programme"),
            "visible breadcrumb differs from the structured breadcrumb")
    h1 = re.search(r"<h1>(.*?)</h1>", html, re.S).group(1)
    require(re.sub(r"<[^>]+>", " ", h1).replace("  ", " ").strip().lower().replace(" :", ":") == HEADLINE.lower().replace("tell another bank", "tell another bank"),
            "h1 text differs from the headline")
    require(html.count("<h1") == 1, "the page must have exactly one h1")
    require('lang="en-GB"' in html.split("<head>")[0], "html lang must be en-GB")
    require('<span class="fis-format">Framework</span>' in html, "the format label must read Framework")


def check_f2() -> None:
    """F2: UK scope, practitioner audience, evidence date and change sensitivity are stated, with the Intelligence Core."""
    html = html_text()
    scope = re.search(r'<dl class="fis-scope-inner">(.*?)</dl>', html, re.S).group(1)
    for needle in ("United Kingdom", "MLRO", "privacy", "operational-risk", "4 October 2026", "under review"):
        require(needle in scope, f"scope strip is missing {needle!r}")
    meta_row = re.search(r'<div class="fis-meta">(.*?)</div>', html, re.S).group(1)
    require("UK" in meta_row and "4 October 2026" in meta_row, "hero meta row is missing UK scope or evidence date")
    question = text_model().section_text("question")
    for needle in ("Intelligence question", "Evidence state", "Decision object", "Uncertainty",
                   "What would change the assessment", "Practitioner outcome", "not legal advice"):
        require(needle in question, f"question section is missing {needle!r}")


ROUTE_ROWS = [
    "ECCTA direct sharing (section 188)",
    "ECCTA indirect sharing (section 189)",
    "POCA joint disclosure route (section 339ZB)",
    "Tipping-off exceptions (sections 333B to 333D)",
    "Ordinary sharing outside these protections",
]
ROUTE_COLUMNS = ["Route", "Who and what it covers", "What triggers it", "What it protects", "What it leaves open"]


def saa_blocks(fragment: str) -> list[tuple[str, str, str]]:
    return re.findall(r'<div class="fis-saa-block"><h4>(\w+) <span class="fis-state" data-state="(\w+)">[^<]*</span></h4><p>(.*?)</p></div>', fragment, re.S)


def check_f3() -> None:
    """F3: the three separate questions and the five routes are stated, with Source, Application and Action kept apart."""
    html = html_text()
    model = text_model()
    shield = re.search(r'<section class="fis-section" id="shield-problem">.*?</section>', html, re.S).group(0)
    stages = re.findall(r'<div class="fis-stage" id="(q-[\w-]+)">\s*<h3><span class="fis-stage-no">(\d)</span> ([^<]+)</h3>', shield)
    require([s[0] for s in stages] == ["q-confidence", "q-data-protection", "q-tipping-off"], f"the three questions are {stages}")
    require([s[2] for s in stages] == ["Confidentiality and civil liability", "Data protection", "Tipping off"], "question headings are wrong")
    blocks = saa_blocks(shield)
    require([b[0] for b in blocks] == ["Source", "Application", "Action"], "shield problem needs Source, Application, Action")
    require([b[1] for b in blocks] == ["established", "assessment", "assessment"], "shield problem evidence states are wrong")
    require(re.search(r'href="#source-\d+"', blocks[0][2]) is not None, "shield problem Source block has no citation")
    require("shield problem" in blocks[1][2] and "not permission to ignore" in blocks[1][2], "the shield problem must be named and stated")
    routes = re.search(r'<section class="fis-section" id="routes">.*?</section>', html, re.S).group(0)
    table = re.search(r'<table class="fis-table".*?</table>', routes, re.S)
    require(table is not None, "routes table is missing from the initial HTML")
    table_html = table.group(0)
    require(re.findall(r'<th scope="col"[^>]*>(.*?)</th>', table_html) == ROUTE_COLUMNS, "route column headings are wrong")
    rows = re.findall(r'<tr role="row"><th scope="row"[^>]*data-label="Route">(.*?)</th>(.*?)</tr>', table_html, re.S)
    require([r[0] for r in rows] == ROUTE_ROWS, f"route rows are {[r[0] for r in rows]}")
    for name, rest in rows:
        cells = re.findall(r'<td[^>]*data-label="([^"]+)">(.*?)</td>', rest, re.S)
        require([c[0] for c in cells] == ROUTE_COLUMNS[1:], f"{name} cell labels are {[c[0] for c in cells]}")
        require(all(len(re.sub(r"<[^>]+>", "", c[1]).strip()) > 40 for c in cells), f"{name} has a thin cell")
        require(all(re.search(r'href="#source-\d+"', c[1]) for c in cells), f"{name} has an uncited cell")
    blocks = saa_blocks(routes)
    require([b[0] for b in blocks] == ["Source", "Application", "Action"], "routes section needs Source, Application, Action")
    require("ECCTA sharing is not a Super SAR" in blocks[1][2], "the Super SAR distinction must be stated")
    require("caption" in table_html and "data-table" not in table_html and "ref-table" not in table_html, "table caption or class problem")
    require("voluntary" in model.section_text("shield-problem") + model.section_text("routes"), "the voluntary nature of the measures must be stated")


STEPS = [
    ("step-purpose", "Purpose"), ("step-route", "Route"), ("step-scope", "Scope"), ("step-data-protection", "Data protection"),
    ("step-protected-data", "Protected data"), ("step-sar-boundary", "SAR boundary"), ("step-recipient-use", "Recipient use"),
    ("step-record", "Record"),
]
OUTCOME_LABELS = [
    "Share under the identified route", "Share after specified controls", "Escalate and do not share yet", "Do not share under this route",
]


def check_f4() -> None:
    """F4: the eight-step sequence and four outcomes are present, each step with Source, Application and Action."""
    html = html_text()
    section = re.search(r'<section class="fis-section" id="sequence">.*?</section>', html, re.S).group(0)
    parts = re.split(r'<div class="fis-stage" id="(step-[\w-]+)">', section)
    steps = list(zip(parts[1::2], parts[2::2]))
    require([s[0] for s in steps] == [s[0] for s in STEPS], f"steps found: {[s[0] for s in steps]}")
    for number, ((step_id, body), (_, title)) in enumerate(zip(steps, STEPS), 1):
        require(f'<span class="fis-stage-no">{number}</span> {title}</h3>' in body, f"{step_id} heading is wrong")
        require('<p class="fis-question">' in body, f"{step_id} needs its question")
        blocks = saa_blocks(body)
        require([b[0] for b in blocks] == ["Source", "Application", "Action"], f"{step_id} needs Source, Application, Action")
        require([b[1] for b in blocks] == ["established", "assessment", "assessment"], f"{step_id} evidence states are wrong")
        require(re.search(r'href="#source-\d+"', blocks[0][2]) is not None, f"{step_id} Source block has no citation")
        require('href="#source-' not in blocks[1][2].replace('<a href="#source-4">[4]</a>', "") or step_id == "step-data-protection",
                f"{step_id} Application block must not cite as if it were the authority")
        require(all(len(re.sub(r"<[^>]+>", "", b[2])) > 100 for b in blocks), f"{step_id} has a thin layer")
    require("our own decision structure" in section, "the sequence must be labelled as our structure")
    outcomes = re.search(r'<section class="fis-section" id="outcomes">.*?</section>', html, re.S).group(0)
    found = re.findall(r"<li><strong>([^<]+)\.</strong>", outcomes)
    require(found == OUTCOME_LABELS, f"outcome labels are {found}")
    require("not legal categories" in outcomes, "outcome labels must be marked as non-legal")


GRADE_LABELS = {
    "best": "Best supported by the evidence",
    "incomplete": "Contains a true point, stops short",
    "unsupported": "Not supported by the evidence",
}
EXPECTED_OPTION_GRADES = {
    "direct-request": {"a": "unsupported", "b": "best", "c": "unsupported", "d": "incomplete"},
    "post-sar": {"a": "unsupported", "b": "best", "c": "unsupported", "d": "incomplete"},
}
BLAME_WORDS = ("negligent", "careless", "gullible", "naive", "complicit", "foolish", "at fault", "guilty", "fraudster", "criminal account holder")
RECORD_FIELDS = ["Facts", "Assumptions", "Indicators", "Mitigants", "Decision", "Rationale"]


def scenario_block(html: str, section_id: str) -> str:
    match = re.search(rf'<section class="fis-section" id="{section_id}" data-scenario="[^"]+">.*?</section>', html, re.S)
    require(match is not None, f"scenario section {section_id} is missing")
    return match.group(0)


def check_scenario(section_id: str, scenario: str) -> None:
    html = html_text()
    block = scenario_block(html, section_id)
    require(f'data-scenario="{scenario}"' in block, f"{section_id} has the wrong scenario id")
    facts = re.search(r'<ul class="fis-facts">(.*?)</ul>', block, re.S).group(1)
    require(facts.count("<li>") >= 4, f"{section_id} needs at least four stated facts")
    require("Composite scenario for teaching" in block, f"{section_id} must say it is synthetic")
    form = re.search(r'<form class="fis-choice" data-decision-form data-scenario-id="([^"]+)".*?</form>', block, re.S)
    require(form is not None and form.group(1) == scenario, f"{section_id} decision form is missing or mislabelled")
    form_html = form.group(0)
    radio_pattern = (r'<input type="radio" name="[^"]+" value="(\w)" data-grade="(\w+)" '
                     r'data-grade-label="([^"]+)"><span><strong>([A-D])\.</strong> (.*?)</span>')
    radios = re.findall(radio_pattern, form_html, re.S)
    require([r[0] for r in radios] == ["a", "b", "c", "d"], f"{section_id} must offer four options in order")
    require({r[0]: r[1] for r in radios} == EXPECTED_OPTION_GRADES[scenario], f"{section_id} option grades differ from the contract")
    require(all(GRADE_LABELS[r[1]] == r[2] for r in radios), f"{section_id} grade labels differ from the contract")
    require(sum(1 for r in radios if r[1] == "best") == 1, f"{section_id} must have exactly one best option")
    require('<p class="fis-feedback" aria-live="polite" role="status"></p>' in form_html, f"{section_id} feedback region needs aria-live and role=status")
    require("<legend>" in form_html and "<fieldset>" in form_html, f"{section_id} options must sit in a fieldset with a legend")
    pieces = re.split(r'<div class="fis-optfb" id="([^"]+)" data-option="(\w)" data-grade="(\w+)">', block)
    analyses = list(zip(pieces[1::4], pieces[2::4], pieces[3::4], pieces[4::4]))
    require([a[1] for a in analyses] == ["a", "b", "c", "d"], f"{section_id} must analyse every option, found {[a[1] for a in analyses]}")
    for (analysis_id, option, grade, body), radio in zip(analyses, radios):
        require(grade == radio[1] and analysis_id == f"optfb-{scenario}-{option}", f"{section_id} analysis {option} does not match its option")
        require(radio[4].strip() in body, f"{section_id} analysis {option} does not restate its option")
        require(f'<span class="fis-grade" data-grade="{grade}">{GRADE_LABELS[grade]}</span>' in body, f"{section_id} analysis {option} badge is wrong")
        layers = re.findall(r'<div class="fis-saa-block"><h4>(\w+)</h4><p>(.*?)</p></div>', body, re.S)
        require([l[0] for l in layers] == ["Source", "Application", "Action"], f"{section_id} analysis {option} needs Source, Application, Action")
        require(all(len(re.sub(r"<[^>]+>", "", l[1])) > 60 for l in layers), f"{section_id} analysis {option} has a thin layer")
        require(re.search(r'href="#source-\d+"', layers[0][1]) is not None, f"{section_id} analysis {option} Source layer is uncited")
    record = re.search(r'<div class="fis-record"[^>]*>(.*?)</div>', block, re.S)
    require(record is not None, f"{section_id} needs a Decision Record")
    require(re.findall(r"<dt[^>]*>(\w+)</dt>", record.group(1)) == RECORD_FIELDS, f"{section_id} Decision Record fields are wrong")
    wwcmd = re.search(r'<div class="fis-wwcmd">(.*?)</div>', block, re.S)
    require(wwcmd is not None and "What Would Change My Decision?" in wwcmd.group(1), f"{section_id} needs a static What Would Change My Decision")
    require("<form" not in wwcmd.group(1) and "<input" not in wwcmd.group(1), f"{section_id} What Would Change My Decision must be static")
    visible = re.sub(r"<[^>]+>", " ", block).lower()
    for word in BLAME_WORDS:
        require(word not in visible, f"{section_id} uses blaming or conclusory wording {word!r}")


def check_f5() -> None:
    """F5: scenario 1 tests the ECCTA request condition, relevant action, data protection and minimisation, with graded options."""
    check_scenario("scenario-one", "direct-request")
    block = scenario_block(html_text(), "scenario-one")
    text = re.sub(r"<[^>]+>", " ", block)
    for needle in ("request condition", "relevant action", "recognised legitimate interest", "criminal offence data", "minimis"):
        require(needle in text.lower() or needle.replace("minimis", "minimi") in text.lower(), f"scenario 1 does not test {needle!r}")
    require("Share after specified controls" in text, "scenario 1 must record its outcome label")


def check_f6() -> None:
    """F6: scenario 2 keeps the operational facts, adds a SAR, and shows ECCTA eligibility does not resolve tipping-off risk."""
    html = html_text()
    check_scenario("scenario-two", "post-sar")
    block = scenario_block(html, "scenario-two")
    counterfactual = re.search(r'<div class="fis-counterfactual" id="counterfactual-post-sar">(.*?)</div>', block, re.S)
    require(counterfactual is not None, "scenario 2 needs its static counterfactual analysis")
    cf = counterfactual.group(1)
    require("<strong>The fact changed.</strong>" in cf and "<strong>What follows.</strong>" in cf and 'data-state="assessment"' in cf, "counterfactual needs the changed fact, its effect and the assessment label")
    require("does not by itself resolve" in cf and "eligibility" in cf, "the counterfactual must state that eligibility does not by itself resolve the SAR boundary")
    require("<form" not in cf and "<input" not in cf, "the counterfactual must be static")
    one = re.sub(r"<[^>]+>", " ", scenario_block(html, "scenario-one"))
    two = re.sub(r"<[^>]+>", " ", block)
    require("Escalate and do not share yet" in two, "scenario 2 must record its outcome label")
    require("Share after specified controls" in one and "Escalate and do not share yet" not in re.search(r'<dt>Decision</dt><dd>(.*?)</dd>', scenario_block(html, "scenario-one"), re.S).group(1),
            "the two scenarios must reach different recorded outcomes")
    for needle in ("section 339ZB", "required notification", "333A", "333C", "nominated officer", "SAR"):
        require(needle in two, f"scenario 2 does not address {needle!r}")
    require(html.count("data-decision-form") == 2, "the guide must have exactly two decision forms")


RED_TEAM_TOPICS = ["Purpose", "Route", "Scope", "Necessity", "Accuracy", "Protected data", "SAR boundary", "Recipient use", "Record"]


def check_f7() -> None:
    """F7: the challenge mechanisms are static: Red Team Questions, and What Would Change My Decision in each scenario."""
    html = html_text()
    section = re.search(r'<section class="fis-section" id="red-team">.*?</section>', html, re.S).group(0)
    items = re.findall(r"<li><strong>([^<]+)\.</strong> (.*?)</li>", re.search(r'<ol class="fis-redteam">(.*?)</ol>', section, re.S).group(1), re.S)
    require([i[0] for i in items] == RED_TEAM_TOPICS, f"Red Team topics are {[i[0] for i in items]}")
    require(all(i[1].strip().endswith("?") for i in items), "every Red Team item must be a question")
    require("make no claim about the law" in section, "Red Team Questions must be labelled as questions, not claims")
    require("<form" not in section and "<input" not in section, "Red Team Questions must be static")
    require(html.count('<div class="fis-wwcmd">') == 2, "each scenario needs a static What Would Change My Decision")


PATTERN_IDS = ["shield-swap", "full-file", "silent-sar", "borrowed-verdict", "missing-minutes"]
CLAIM_VOCABULARY = re.compile(r"ECCTA|POCA|Schedule 1|UK GDPR|SAR|tipping|ICO|Ombudsman|nominated officer|criminal offence", re.I)


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


def check_f8() -> None:
    """F8: the one-screen summary, five Risk, Signal, Response cards in two placements, image export and native FAQ are present."""
    html = html_text()
    summary = re.search(r'<section class="fis-section fis-summary" id="operational-summary">.*?</section>', html, re.S).group(0)
    body = html.replace(summary, "")
    body_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
    lists = re.findall(r'<ol class="fis-summary-list" data-summary="(\w+)">(.*?)</ol>', summary, re.S)
    require([name for name, _ in lists] == ["steps", "outcomes"], "summary needs a steps list and an outcomes list")
    for name, expected in (("steps", 8), ("outcomes", 4)):
        items = re.findall(r"<li><strong>([^<]+)</strong> <span>([^<]+)</span></li>", dict(lists)[name])
        require(len(items) == expected, f"summary {name} list needs {expected} items, found {len(items)}")
        for _, sentence in items:
            require(sentence in body_text, f"summary line is not verbatim body copy: {sentence!r}")
    require("adds no new claim" in summary, "the summary must say it adds no new claim")
    section = re.search(r'<section class="fis-section" id="patterns">.*?</section>', html, re.S).group(0)
    pieces = re.split(r'<div class="fis-pattern" data-pattern-id="([^"]+)">', section)
    cards = list(zip(pieces[1::2], pieces[2::2]))
    require([c[0] for c in cards] == PATTERN_IDS, f"closing cards found: {[c[0] for c in cards]}")
    for number, (pattern_id, card_body) in enumerate(cards, 1):
        require(re.search(rf"<h3>{number}\. [^<]+</h3>", card_body) is not None, f"{pattern_id} needs a numbered metaphor-style name")
        require('<p class="fis-metaphor">' in card_body, f"{pattern_id} needs its one short explanatory line")
        lines = re.findall(r"<div><dt>(\w+)</dt><dd>(.*?)</dd></div>", card_body, re.S)
        require([l[0] for l in lines] == ["Risk", "Signal", "Response"], f"{pattern_id} needs Risk, Signal, Response in order")
    outside = html.replace(section, "")
    inline = re.findall(r'<div class="fis-pattern fis-pattern-inline" data-pattern-id="([^"]+)" data-pattern-placement="inline">(.*?)\n  </div>', outside, re.S)
    require(sorted(i[0] for i in inline) == sorted(PATTERN_IDS), f"inline placements found: {[i[0] for i in inline]}")

    def flat(text: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<h3>\d\. ", "<h3>", text)).strip()

    closing_by_id = dict(cards)
    for pattern_id, inline_body in inline:
        require(flat(inline_body) == flat(closing_by_id[pattern_id].rsplit("\n    </div>", 1)[0]), f"inline {pattern_id} wording differs from the closing card")
    require('id="saveSummaryImage"' in html and 'id="saveSummaryStatus" aria-live="polite" role="status"' in html, "the save button and its status region are required")
    require("#saveSummaryImage{display:none}.js #saveSummaryImage{display:inline-block}" in html, "the save button must stay hidden without JavaScript")
    faq = re.search(r'<section class="fis-section fis-details" id="faq">.*?</section>', html, re.S).group(0)
    items = re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", faq, re.S)
    require(len(items) == 7 and all(len(a) > 100 for _, a in items), f"expected seven substantial FAQ items, found {len(items)}")
    script = SCRIPT.read_text(encoding="utf-8")
    start = script.index("function exportSummary")
    claims = [l for l in js_string_literals(script[start:]) if CLAIM_VOCABULARY.search(l)]
    require(not claims, f"the image export carries wording of its own that looks like a claim: {claims}")
    require("querySelector('h3')" in script and "fisClosingPatterns" in script and "fisOperationalSummary" in script, "the export must read the page's own text")


CLAIM_PREFIX = "financial-crime-information-sharing."
LEDGER = ROOT / "verification-ledger.json"
# claim suffix -> (page source numbers it covers, phrases that must appear in the visible body copy)
CLAIM_PLAN = {
    "eccta-direct-conditions.001": ((1,), ["the information must relate to a customer or former customer of the sender", "the request or warning condition must be met",
        "the disclosure must not be a privileged disclosure", "no civil liability to the customer for the sender", "does not breach confidence"]),
    "eccta-request-warning-conditions.002": ((1,), ["request condition in eccta section 188(4)", "warning condition in section 188(5)",
        "has reason to believe the sender holds information about the customer"]),
    "eccta-relevant-actions.003": ((1,), ["eccta section 191 defines the relevant actions", "to a customer or proposed customer",
        "relevant actions concern a customer or proposed customer of the person carrying them out"]),
    "eccta-data-protection-saving.004": ((1,), ["nothing in section 188 or 189 authorises a disclosure that would contravene the data protection legislation",
        "sections 188(11) and 189(10) provide that nothing in them authorises a disclosure that would contravene the data protection legislation"]),
    "eccta-indirect-sharing.005": ((1,), ["deposit-taking bodies, electronic money institutions, payment institutions, cryptoasset exchange providers and custodian wallet providers",
        "above a revenue threshold", "an agreement that the data will only be handled where the uk gdpr applies"]),
    "eccta-privileged-disclosure.006": ((1,), ["the privileged disclosure exclusion", "the disclosure must not be a privileged disclosure"]),
    "eccta-economic-crime.007": ((2, 1), ["economic crime for eccta sections 188 to 191 means a listed offence in schedule 11", "fraud under section 1 of the fraud act 2006",
        "sections 327 to 329 of poca", "the tipping-off offence in section 333a"]),
    "eccta-explanatory-notes-188-3.008": ((3,), ["the explanatory notes and the government guidance read the provision as covering aml-regulated firms"]),
    "eccta-government-guidance-scope.009": ((4,), ["calls the measures voluntary", "uk-based sharing", "private bodies do not need statutory authority to share information",
        "disclosure for purposes other than those in eccta gets no protection", "sharing personal data for commercial purposes could lead to ico enforcement",
        "verify that the other firm is legitimate"]),
    "eccta-government-guidance-indirect.010": ((4,), ["relies on the sender's decision in section 189(1)(c) and not on the request condition"]),
    "eccta-government-guidance-sar.011": ((4,), ["must not breach the tipping-off or prejudicing-investigation provisions", "uses the term super sar for the joint disclosure report"]),
    "eccta-government-guidance-handling.012": ((4,), ["advises strict handling conditions", "not designed to give sectors additional powers to exclude customers inappropriately",
        "audit trail of all information shared", "accurate, adequate, relevant and limited to what is necessary"]),
    "eccta-government-guidance-stale.013": ((4,), ["will come into force in 2026", "out of date"]),
    "duaa-recognised-legitimate-interest.014": ((5,), ["article 6(1)(ea), processing necessary for a recognised legitimate interest",
        "annex 1 paragraph 5 covers processing necessary for detecting, investigating or preventing crime, or apprehending or prosecuting offenders"]),
    "si-2026-82-commencement.015": ((6,), ["section 70 and schedule 4 came into force on 5 february 2026"]),
    "ico-recognised-legitimate-interest-guidance.016": ((7,), ["the crime condition covers sharing for crime-related purposes, including scams, fraud and money laundering",
        "recognised legitimate interest is a lawful basis and not an exemption", "tell people it relies on this basis and which condition",
        "statutory crime reporting is more likely to rest on legal obligation", "decide whether the use is necessary"]),
    "ico-criminal-offence-data.017": ((7, 10, 9), ["criminal offence data includes suspicion or allegations of criminal activity",
        "a private firm without official authority needs a condition in schedule 1"]),
    "dpa-schedule-1-paragraphs-10-36.018": ((8,), ["paragraph 10 applies where processing is necessary for the prevention, investigation or detection of an unlawful act",
        "removes the appropriate policy document requirement where processing consists of disclosure to a competent authority or is carried out in preparation for such disclosure", "the substantial public interest limb is removed for criminal offence data by paragraph 36"]),
    "dpa-schedule-1-paragraphs-14-15.019": ((8,), ["paragraph 14 covers disclosures as a member of, or under arrangements made by, an anti-fraud organisation",
        "paragraph 15 covers a disclosure in good faith under poca section 339zb"]),
    "dpa-schedule-1-policy-document.020": ((8,), ["a policy document must explain how the article 5 principles are met and the retention and erasure policy, and the record of processing must name the condition"]),
    "ico-criminal-offence-conditions-table.021": ((9,), ["records that paragraphs 10, 14 and 15 all need an appropriate policy document, except for paragraph 10 disclosure to the relevant authorities or preparation for such disclosure"]),
    "ico-scams-sharing-controls.022": ((10,), ["supports a data protection impact assessment for routine sharing, a data sharing agreement where sharing is not ad hoc, and secure handling",
        "an impact assessment is a legal requirement where processing is likely to result in high risk, and good practice for routine sharing and major projects"]),
    "poca-333a-tipping-off.023": ((11,), ["section 333a of poca is an offence where a person discloses that a disclosure under part 7 has been made",
        "likely to prejudice any investigation that might follow"]),
    "poca-333b-333c-exceptions.024": ((11,), ["section 333c permits certain disclosures between credit institutions or between financial institutions only where",
        "for the purpose only of preventing an offence under part 7"]),
    "poca-333d-other-permitted.025": ((11,), ["section 333d includes disclosure for the detection, investigation or prosecution of a criminal offence, and disclosure in good faith under section 339zb",
        "there is no offence where the person does not know or suspect that the disclosure is likely to have that effect"]),
    "poca-339zb-conditions.026": ((12,), ["a required notification made to the nca before the disclosure",
        "will or may assist in determining a matter connected with a suspicion of money laundering"]),
    "poca-339zd-339ze-effect.027": ((12,), ["a joint disclosure report can satisfy the required disclosure duties within set limits"]),
    "poca-339zf-confidence.028": ((12,), ["does not breach an obligation of confidence or any other restriction on disclosure",
        "information obtained from a uk law enforcement agency cannot be included without that agency's consent"]),
    "cfa-2017-section-11.029": ((13,), ["linked to a suspicion that a person is engaged in money laundering"]),
    "nca-required-notification-procedure.030": ((14,), ["obtain a reference number and to include it in any sar submitted as a result",
        "the nca publishes a required notification form and procedure"]),
}
SOURCE_DATES = {4: ("updated 3 October 2025", "2025-10-03"), 6: ("made 29 January 2026", "2026-01-29"), 7: ("published 23 March 2026", "2026-03-23")}
FAMILIES = [
    ("ukpga/2023/56/section/", 1), ("ukpga/2023/56/schedule/11", 2), ("ukpga/2023/56/notes/", 3), ("gov.uk/government/publications/information-sharing", 4),
    ("ukpga/2025/18/", 5), ("uksi/2026/82", 6), ("lawful-basis/a-guide-to-lawful-basis/recognised-legitimate-interest", 7), ("ukpga/2018/12/schedule/1", 8),
    ("lawful-basis/criminal-offence-data/what-are-the-conditions", 9), ("data-sharing/sharing-personal-information-when-preventing", 10),
    ("ukpga/2002/29/section/333", 11), ("ukpga/2002/29/section/339", 12), ("ukpga/2017/22/notes/", 13), ("nationalcrimeagency.gov.uk", 14),
]


def source_family(url: str) -> int:
    for fragment, number in FAMILIES:
        if fragment in url:
            return number
    raise AssertionError(f"url not in any source family: {url}")


def check_f9() -> None:
    """F9: the source list, methodology and ledger agree, every claim is pinned to final body wording, and nothing is cited without a claim."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_ledger as ledger

    html = html_text()
    entries = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = ledger.validate(entries)
    require(not errors, f"ledger does not validate: {errors[:3]}")
    ours = {e["claimId"]: e for e in entries if e["claimId"].startswith(CLAIM_PREFIX)}
    require(sorted(ours) == sorted(CLAIM_PREFIX + key for key in CLAIM_PLAN), f"ledger claim ids differ: {sorted(set(ours) ^ {CLAIM_PREFIX + k for k in CLAIM_PLAN})}")
    sources_html = re.search(r'<section class="fis-section fis-sources" id="sources">.*?</section>', html, re.S).group(0)
    listed = {int(n): (url, li) for n, url, li in re.findall(r'<li id="source-(\d+)"><a href="([^"]+)"[^>]*>.*?</a>(.*?)</li>', sources_html, re.S)}
    require(sorted(listed) == list(range(1, 15)), f"source list holds {sorted(listed)}")
    for number, (url, _) in listed.items():
        require(source_family(url) == number, f"source {number} url sits in family {source_family(url)}")
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    broken = sorted({h for h in re.findall(r'href="#([^"]+)"', html) if h not in ids})
    require(not broken, f"in-page links do not resolve: {broken}")
    body_html = html.split('<section class="fis-section fis-sources"')[0]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body_html)).lower().replace("’", "'")
    for key, (numbers, phrases) in CLAIM_PLAN.items():
        entry = ours[CLAIM_PREFIX + key]
        require(entry["guide"] == GUIDE.name and entry["status"] == "verified" and entry["claimType"] == "regulatory", f"{key} metadata is wrong")
        families = {source_family(entry["source"]["url"])} | {source_family(s["url"]) for s in entry.get("additionalSources", [])}
        require(families == set(numbers), f"{key} ledger sources map to {sorted(families)}, page sources {sorted(numbers)}")
        for phrase in phrases:
            require(phrase in text, f"{key}: body copy is missing the claimed wording {phrase!r}")
        require(entry["reviewDue"] > entry["verifiedOn"], f"{key} reviewDue must follow verifiedOn")
    for number, (printed, iso) in SOURCE_DATES.items():
        require(printed in listed[number][1], f"source {number} list no longer prints {printed!r}")
        for key, (numbers, _) in CLAIM_PLAN.items():
            if numbers[0] == number:
                require(ours[CLAIM_PREFIX + key]["source"]["date"] == iso, f"{key} source date differs from the page")
    covered = {n for numbers, _ in CLAIM_PLAN.values() for n in numbers}
    cited = {int(n) for n in re.findall(r'href="#source-(\d+)"', body_html)}
    require(cited == set(range(1, 15)), f"sources cited in the body: {sorted(cited)}")
    require(cited <= covered, f"sources cited in the body with no ledger claim: {sorted(cited - covered)}")
    require("not legal advice" in sources_html and "Last reviewed" in sources_html and "4 October 2026" in sources_html, "sources section needs scope, review date and the evidence date")
    require("will come into force in 2026" in text and "out of date" in sources_html + text, "the stale government guidance sentence must be disclosed")
    require("under review" in sources_html, "the under-review ICO pages must be disclosed in the sources section")
    # R17 corrections: wording that must not return, and the corrected wording that must stay
    require("same footing" not in html and "for that firm's use for its relevant actions" not in html, "section 189 protections must not be stated as one shared footing")
    require("The eventual recipient's use for its relevant actions does not breach an obligation of confidence." in html, "section 189(6) is a confidence protection only and the page must say so")
    require("only for disclosure to a competent authority" not in html and "Another bank is not a competent authority" not in html, "paragraph 10(2) must include preparation for disclosure")
    require("the paragraph 10(2) exception does not apply" in html and "so an appropriate policy document is required" in html, "Scenario 1 must apply paragraph 10(2) to its own facts")
    require("Question 3 is not engaged" not in html and "no contemplated or current investigation has been identified" in html, "Scenario 1 must not treat the absence of a SAR as excluding a contemplated or current investigation")
    require("has not yet been completed" not in html and "A short recheck of the corrected wording" in html, "the Methodology must record the actual review outcome")


RELATED_SLUGS = ["classification-asymmetry-guide", "sar-guide-part2", "de-risking-judgement-call"]


def check_f10() -> None:
    """F10: Knowledge Hub card, sitemap, content relations, guide counts, reading time and social card are consistent."""
    import struct

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_de_risking_judgement_call import KnowledgeCountParser
    from generate_social_card import extract_title_subtitle
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
    require('data-date="2026-10-04"' in attrs and 'data-cats="aml-programme"' in attrs, "card needs data-date and the AML Programme category")
    require('<span class="kh-format-label">Framework</span>' in inner, "card format label must be Framework")
    minutes = int(re.search(r'<span class="kh-read">(\d+) MIN</span>', inner).group(1))
    hero_minutes = int(re.search(r"(\d+) min read", html).group(1))
    require(minutes == hero_minutes, f"card says {minutes} MIN but the hero says {hero_minutes} min read")
    words = word_count(html)
    require(words / 223 <= minutes <= words / 163, f"{minutes} min is outside the site interquartile reading speed for {words} words")
    require(abs(minutes - round(words / 181)) <= 2, f"{minutes} min differs from the site median speed estimate {round(words / 181)}")
    require(re.search(r'<div class="kh-item-desc">(.*?)</div>', inner, re.S).group(1) == meta(html, "name", "description"), "card description differs from the page description")
    require(re.search(r'<div class="kh-item-title">(.*?)</div>', inner, re.S).group(1) == HEADLINE, "card title differs from the headline")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    block = re.findall(rf"<url>\s*<loc>{re.escape(URL)}</loc>\s*<changefreq>monthly</changefreq>\s*<priority>0\.7</priority>\s*</url>", sitemap)
    require(len(block) == 1 and sitemap.count(URL) == 1, "sitemap needs exactly one entry in the comparable guide format")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    require(relations.get(SLUG) == RELATED_SLUGS, f"relation set is {relations.get(SLUG)}")
    for target in RELATED_SLUGS:
        require(SLUG in relations.get(target, []), f"relation is not reciprocal: {target}")
        require((ROOT / f"{target}.html").exists(), f"related guide {target} does not exist")
    related = re.search(r'<section class="fis-section" id="related">.*?</section>', html, re.S).group(0)
    require(re.findall(r'<a href="/([^"]+)\.html">', related) == RELATED_SLUGS, "the on-page related links must match the relation set")
    card_png = ROOT / f"{SLUG}-social-card.png"
    require(card_png.exists(), "social card is missing")
    data = card_png.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    require(data[:8] == b"\x89PNG\r\n\x1a\n" and (width, height) == (1200, 630), f"social card is {width}x{height}")
    require(len(data) <= 400_000, f"social card is {len(data)} bytes, over the 400KB ceiling")
    title, subtitle = extract_title_subtitle(GUIDE)
    require((title, subtitle) == ("Financial Crime Information Sharing", "Can I tell another bank?"), f"the card source text is {(title, subtitle)}")


CHECKS = [
    ("F1", check_f1),
    ("F2", check_f2),
    ("F3", check_f3),
    ("F4", check_f4),
    ("F5", check_f5),
    ("F6", check_f6),
    ("F7", check_f7),
    ("F8", check_f8),
    ("F9", check_f9),
    ("F10", check_f10),
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
