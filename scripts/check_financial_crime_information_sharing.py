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


CHECKS = [
    ("F1", check_f1),
    ("F2", check_f2),
    ("F3", check_f3),
    ("F4", check_f4),
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
