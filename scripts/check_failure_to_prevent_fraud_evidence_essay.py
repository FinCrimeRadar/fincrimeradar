#!/usr/bin/env python3
"""Static release-candidate contract checks for the Failure to Prevent
Fraud Evidence Essay (Experiment 04)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "failure-to-prevent-fraud-evidence-essay.html"
SCRIPT = ROOT / "js" / "failure-to-prevent-fraud-evidence-essay.js"
SOCIAL_CARD = ROOT / "failure-to-prevent-fraud-evidence-essay-social-card.png"
CANONICAL_URL = "https://fincrimeradar.org/failure-to-prevent-fraud-evidence-essay.html"
GUIDE_SLUG = "failure-to-prevent-fraud-evidence-essay"

TOC_SECTIONS = [
    "argument", "section-199", "defensibility-chain", "competing-interpretations",
    "worked-decisions", "assessment-change", "practitioner-summary",
    "knowledge-check", "faq", "sources", "related-reading",
]

FORBIDDEN_TERMS = (
    "Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Task 6", "Task 7",
    "Experiment 04", "R01", "R02", "R03", "R04", "R05", "R06", "R07",
    "R08", "R09", "R10", "R11", "R12", "R13", "R14", "R15", "R16",
    "R17", "R18",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def text_only(fragment: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)).strip()


def strip_script_style(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    return html


def main() -> None:
    html = GUIDE.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))

    # --- Metadata consistency ---------------------------------------
    title = re.search(r"<title>([^<]+)</title>", html)
    require(title is not None, "title tag missing")
    canonical = re.search(r'<link rel="canonical" href="([^"]+)">', html)
    og_url = re.search(r'<meta property="og:url" content="([^"]+)">', html)
    og_title = re.search(r'<meta property="og:title" content="([^"]+)">', html)
    og_desc = re.search(r'<meta property="og:description" content="([^"]+)">', html)
    twitter_title = re.search(r'<meta name="twitter:title" content="([^"]+)">', html)
    twitter_desc = re.search(r'<meta name="twitter:description" content="([^"]+)">', html)
    meta_desc = re.search(r'<meta name="description" content="([^"]+)">', html)
    require(canonical is not None and canonical.group(1) == CANONICAL_URL, "canonical URL is wrong or missing")
    require(og_url is not None and og_url.group(1) == CANONICAL_URL, "og:url differs from canonical")
    require(og_title is not None and title.group(1).startswith(og_title.group(1)), "title does not start with og:title")
    require(og_title is not None and twitter_title is not None and og_title.group(1) == twitter_title.group(1),
            "og:title and twitter:title differ")
    require(og_desc is not None and twitter_desc is not None and og_desc.group(1) == twitter_desc.group(1),
            "og:description and twitter:description differ")
    require(canonical.group(1) in sitemap, "canonical URL missing from sitemap.xml")

    json_ld = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    require(len(json_ld) == 2, f"expected 2 JSON-LD blocks, found {len(json_ld)}")
    structured = [json.loads(block) for block in json_ld]
    article = next((item for item in structured if item.get("@type") == "Article"), None)
    breadcrumbs = next((item for item in structured if item.get("@type") == "BreadcrumbList"), None)
    require(article is not None, "Article JSON-LD missing")
    require(breadcrumbs is not None and len(breadcrumbs.get("itemListElement", [])) == 3,
            "BreadcrumbList JSON-LD is incomplete")
    require(meta_desc is not None and article.get("description") == meta_desc.group(1),
            "Article JSON-LD description differs from meta description")
    require(article.get("headline") == og_title.group(1), "Article JSON-LD headline differs from og:title")
    require(article.get("image") == f"https://fincrimeradar.org/{SOCIAL_CARD.name}",
            "Article JSON-LD image does not match the social card filename")
    for prop in ("headline", "description", "datePublished", "dateModified", "author", "publisher", "mainEntityOfPage", "image"):
        require(prop in article, f"Article JSON-LD property missing: {prop}")
    print("OK: metadata (title/canonical/og/twitter/JSON-LD) internally consistent")

    # --- Required sections and ToC -----------------------------------
    for section_id in TOC_SECTIONS:
        require(f'id="{section_id}"' in html, f"section #{section_id} is missing")
    toc = re.search(r'<aside class="ftpf-toc"[^>]*>(.*?)</aside>', html, re.S)
    require(toc is not None, "ToC aside is missing")
    toc_hrefs = re.findall(r'href="#([a-z0-9-]+)"', toc.group(1))
    require(toc_hrefs == TOC_SECTIONS, f"ToC does not list all sections in order: {toc_hrefs}")
    print(f"OK: all {len(TOC_SECTIONS)} required sections present and listed in the ToC in order")

    # --- Scenarios and counterfactuals -------------------------------
    scenario_forms = re.findall(r'<form class="ftpf-decision-form"[^>]*data-scenario-form[^>]*data-scenario-id="([^"]+)"[^>]*>(.*?)</form>',
                                 html, re.S)
    require(len(scenario_forms) == 2, f"expected 2 scenario decision forms, found {len(scenario_forms)}")
    for scenario_id, form_html in scenario_forms:
        best_options = re.findall(r'data-grade="best"', form_html)
        require(len(best_options) == 1, f"scenario {scenario_id} must have exactly one best-graded option, found {len(best_options)}")
        require('aria-live="polite"' in form_html, f"scenario {scenario_id} feedback is not a polite live region")
    counterfactual_blocks = re.findall(r'<details class="ftpf-counterfactual"[^>]*data-counterfactual[^>]*>', html)
    require(len(counterfactual_blocks) == 2, f"expected 2 counterfactual blocks, found {len(counterfactual_blocks)}")
    print("OK: 2 scenario decision forms (one best option each) and 2 counterfactual blocks")

    # --- Knowledge check ----------------------------------------------
    knowledge_form = re.search(r'<form id="ftpfKnowledgeForm">(.*?)</form>', html, re.S)
    require(knowledge_form is not None, "knowledge check form #ftpfKnowledgeForm is missing")
    kform_html = knowledge_form.group(1)
    fieldsets = re.findall(r"<fieldset>(.*?)</fieldset>", kform_html, re.S)
    require(len(fieldsets) == 5, f"expected 5 knowledge-check fieldsets, found {len(fieldsets)}")
    for number, fieldset in enumerate(fieldsets, start=1):
        correct = re.findall(r'data-correct="true"', fieldset)
        require(len(correct) == 1, f"knowledge question {number} must have exactly one correct answer, found {len(correct)}")
    require(kform_html.count('data-correct="true"') == 5, "expected exactly 5 correct answers total in the knowledge check")
    require('id="ftpfKnowledgeFeedback"' in kform_html and 'aria-live="polite"' in kform_html,
            "knowledge feedback is not a polite live region")
    print("OK: 5 knowledge-check questions, each with exactly one correct answer")

    # --- Risk/Signal/Response patterns ---------------------------------
    inline_patterns = re.findall(r'<aside class="ftpf-pattern ftpf-pattern-inline" data-pattern-id="([^"]+)"[^>]*>(.*?)</aside>',
                                  html, re.S)
    closing_patterns = re.findall(r'<article class="ftpf-pattern" data-pattern-id="([^"]+)">(.*?)</article>',
                                   html, re.S)
    require(len(inline_patterns) == 6, f"expected 6 inline patterns, found {len(inline_patterns)}")
    require(len(closing_patterns) == 6, f"expected 6 closing patterns, found {len(closing_patterns)}")
    inline_ids = sorted(pattern_id for pattern_id, _ in inline_patterns)
    closing_ids = sorted(pattern_id for pattern_id, _ in closing_patterns)
    require(inline_ids == closing_ids, f"inline and closing pattern id sets differ: {inline_ids} vs {closing_ids}")
    require(len(set(inline_ids)) == 6, "inline pattern ids are not unique")
    inline_by_id = dict(inline_patterns)
    closing_by_id = dict(closing_patterns)
    for pattern_id in inline_by_id:
        require(text_only(inline_by_id[pattern_id]) == text_only(closing_by_id[pattern_id]),
                f"pattern {pattern_id} text differs between inline and closing placements")
    print("OK: 6 Risk/Signal/Response patterns, identical text inline and in the closing grid")

    # --- FAQ ------------------------------------------------------------
    faq = re.search(r'<div class="ftpf-faq-list">(.*?)</div>\s*</div>', html, re.S)
    require(faq is not None, "FAQ list is missing")
    require(faq.group(1).count("<details>") == 6, f"expected 6 FAQ items, found {faq.group(1).count('<details>')}")
    require(faq.group(1).count("<details>") == faq.group(1).count("<summary>"), "FAQ details/summary counts differ")
    print("OK: 6 native FAQ disclosure items")

    # --- Citations and source records -----------------------------------
    cited_ids = set(re.findall(r'ftpf-cite"[^>]*data-src="(\d+)"', html))
    src_anchor_ids = set(re.findall(r'id="src-(\d+)"', html))
    require(cited_ids <= src_anchor_ids, f"citation markers with no matching Sources entry: {sorted(cited_ids - src_anchor_ids)}")
    require(src_anchor_ids <= cited_ids, f"Sources entries never cited inline: {sorted(src_anchor_ids - cited_ids)}")
    sources_block = re.search(r"var SOURCES = \{(.*?)\n  \};", script, re.S)
    require(sources_block is not None, "JS SOURCES object not found")
    js_source_ids = set(re.findall(r"^\s*'(\d+)':\s*\{", sources_block.group(1), re.M))
    require(js_source_ids == cited_ids, f"JS SOURCES keys {sorted(js_source_ids)} do not match cited ids {sorted(cited_ids)}")
    print(f"OK: {len(cited_ids)} citation markers all map to a Sources entry and a JS source record, with no orphans")

    # --- Component isolation / formatting rules --------------------------
    require(re.search(r'class="[^"]*\bcard\b[^"]*"', html, re.I) is None, "a class name contains the word 'card'")
    require(re.search(r"class\s*=\s*[\"'][^\"']*card", html, re.I) is None, "a class attribute contains 'card' as a substring")
    require("—" not in html and "–" not in html, "em or en dash character found in the HTML")
    require("—" not in script and "–" not in script, "em or en dash character found in the JavaScript")
    style_block = re.search(r"<style>(.*?)</style>", html, re.S)
    require(style_block is None or re.search(r"\bmain\s+section\b", style_block.group(1)) is None,
            "page-local CSS defines a bare 'main section' selector")
    print("OK: no 'card' class collisions, no em/en dash characters, no bare 'main section' selector")

    # --- No internal terminology leakage ----------------------------------
    visible = strip_script_style(html)
    for term in FORBIDDEN_TERMS:
        require(term not in visible, f"internal terminology leaked into visible copy: {term!r}")
    print("OK: no internal task/experiment terminology in visible copy")

    # --- Verification ledger coverage --------------------------------------
    guide_claims = [item for item in ledger if item.get("guide") == GUIDE.name]
    require(len(guide_claims) >= 15, f"expected at least 15 ledger claims for this guide, found {len(guide_claims)}")
    claim_ids = [item["claimId"] for item in guide_claims]
    require(len(claim_ids) == len(set(claim_ids)), "duplicate claimIds found for this guide")
    require(all(item.get("status") == "verified" for item in guide_claims if item.get("claimType") != "process-record"),
            "a non-process-record ledger claim for this guide is not status=verified")
    print(f"OK: {len(guide_claims)} verification-ledger claims for this guide, no duplicates")

    # --- Knowledge Hub, sitemap, content relations, social card ------------
    kh_cards = re.findall(r'<a href="/failure-to-prevent-fraud-evidence-essay\.html" class="kh-article-card"[^>]*data-date="([^"]+)"',
                           knowledge)
    require(len(kh_cards) == 1, f"expected exactly 1 Knowledge Hub card, found {len(kh_cards)}")
    require(kh_cards[0] == "2026-09-16", f"Knowledge Hub card data-date is wrong: {kh_cards[0]}")
    require(sitemap.count(f"<loc>{CANONICAL_URL}</loc>") == 1, "sitemap does not contain exactly one entry for this guide")
    require(GUIDE_SLUG in relations, "content-relations.json has no entry for this guide")
    relation_count = len(relations[GUIDE_SLUG])
    require(3 <= relation_count <= 4, f"content-relations entry should have 3-4 related guides, found {relation_count}")
    require(SOCIAL_CARD.exists(), "social card PNG is missing")
    try:
        from PIL import Image
        with Image.open(SOCIAL_CARD) as image:
            require(image.size == (1200, 630), f"social card dimensions are {image.size}, expected (1200, 630)")
    except ImportError:
        fail("PIL/Pillow is required to check the social card dimensions")
    require(SOCIAL_CARD.stat().st_size < 400_000, "social card exceeds the 400KB working ceiling")
    print("OK: Knowledge Hub card, sitemap entry, content-relations entry and social card all check out")

    # --- Static (no-JS) content presence -------------------------------------
    for scenario_id, form_html in scenario_forms:
        scenario_section = html[html.find(form_html):html.find(form_html) + len(form_html) + 4000]
        require("ftpf-saa" in scenario_section, f"scenario {scenario_id} Source/Application/Action reasoning missing from static HTML")
    counterfactual_bodies = re.findall(r'<details class="ftpf-counterfactual"[^>]*>(.*?)</details>', html, re.S)
    require(sum(len(text_only(body)) > 40 for body in counterfactual_bodies) == 2,
            "counterfactual reasoning is not fully present as static text")
    print("OK: scenario reasoning and counterfactual text present in static HTML (no-JS comprehension)")

    print("OK: Failure to Prevent Fraud Evidence Essay static contract passed")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration) as error:
        fail(str(error))
