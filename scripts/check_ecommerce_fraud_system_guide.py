#!/usr/bin/env python3
"""Static release contract for The E-commerce Fraud System guide.

Every assertion is labelled with the Requirement Coverage Matrix ID it proves.
Browser-only requirements are covered by test_ecommerce_fraud_system_guide_browser.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GUIDE_NAME = "e-commerce-fraud-system-guide.html"
SLUG = "e-commerce-fraud-system-guide"
GUIDE = ROOT / GUIDE_NAME
SCRIPT = ROOT / "js" / f"{SLUG}.js"
CARD = ROOT / f"{SLUG}-social-card.png"
CANONICAL = f"https://fincrimeradar.org/{GUIDE_NAME}"
CARD_URL = f"https://fincrimeradar.org/{SLUG}-social-card.png"
TITLE = "The E-commerce Fraud System: How Evidence Changes from Account Creation to Chargeback"
SHORT_TITLE = "The E-commerce Fraud System"
STANDFIRST = (
    "Fraud signals do not keep the same meaning as an account becomes an order, a delivery, a refund and a dispute. "
    "This guide shows what each control may conclude, what it must pass forward and how later losses should change earlier decisions."
)
DESCRIPTION = (
    "Move fraud evidence, uncertainty and decision level together across the e-commerce lifecycle "
    "with the Fraud Evidence Relay and a backtrace test."
)
SECTION_ORDER = [
    "ecf-hero", "ecf-how-to-use", "ecf-executive-assessment", "ecf-lifecycle", "ecf-decision-levels", "ecf-relay",
    "ecf-worked-decision-1", "ecf-broken-handoffs", "ecf-outcome-boundary", "ecf-worked-decision-2", "ecf-backtrace",
    "ecf-checklist", "ecf-assessment-change", "ecf-closing-patterns", "ecf-knowledge-check", "ecf-faq",
    "ecf-sources", "ecf-related",
]
LIFECYCLE = [
    "Account and promotion", "Checkout and authentication", "Order review",
    "Fulfilment and delivery", "Return and refund", "Dispute and outcome",
]
LEVELS = ["Event", "Account", "Order", "Linked network", "Refund", "Dispute"]
RELAY = [
    "Decision level", "Evidence state", "Bounded conclusion", "Action and owner", "Relay package", "Feedback trigger",
]
BACKTRACE = [
    "Fix the outcome", "Rebuild the timeline", "Find the first relevant signal", "Inspect each handoff",
    "Locate the reversible moment", "Separate outcome types", "Return the learning",
]
OUTCOMES = [
    "Merchant fraud assessment", "Consumer-rights outcome", "Payment-service outcome",
    "Scheme dispute outcome", "Criminal conclusion",
]
CHECKLIST = [
    "Account and promotion owner", "Checkout and payments owner", "Order-review owner",
    "Fulfilment and delivery owner", "Returns and customer-service owner", "Dispute owner",
    "Governance and quality-assurance owner",
]
STATUS_LABELS = [
    "Intelligence question", "Evidence checked", "Current assessment", "Evidence status",
    "Jurisdiction boundary", "Next trigger",
]
# Locked pattern text from the design memo section 6.
PATTERNS = {
    "local-green-light": ("The Local Green Light",
        "Each stage makes a reasonable local decision while unresolved cross-stage evidence accumulates into loss.",
        "An order has several approvals, but no owner can state the combined evidence or residual uncertainty.",
        "Complete the Fraud Evidence Relay before the next irreversible action."),
    "level-jump": ("The Level Jump",
        "A signal at one decision level becomes a fraud verdict at another without sufficient evidence.",
        "An event anomaly is used to label an account, network or customer as fraudulent without a documented reasoning step.",
        "Name the decision level and write a bounded conclusion before selecting the action."),
    "relay-drop": ("The Relay Drop",
        "Evidence reaches the next team without its meaning, or a conclusion arrives without the evidence and uncertainty behind it.",
        "The next owner must reconstruct why the case was escalated from raw logs, short labels or free-text notes.",
        "Send the minimum evidence, source, timing, bounded conclusion, open question and required next decision as one relay package."),
    "feedback-sink": ("The Feedback Sink",
        "Refund, dispute and loss outcomes are recorded but do not change the upstream control that could prevent recurrence.",
        "The same loss pattern repeats while the original account, checkout or fulfilment decision remains unreviewed.",
        "Define a named feedback trigger, receiving owner and specific control decision to reassess."),
    "rights-collapse": ("The Rights Collapse",
        "A merchant fraud concern is treated as though it decides consumer rights, payment-service protection, scheme outcomes and criminality.",
        "One fraud label automatically determines refund, dispute and account decisions without separate tests.",
        "Record each outcome separately, apply its own evidence and authority, and preserve uncertainty where the merchant cannot decide it."),
}
RELATED = {"fraud-red-flags-guide", "fraud-investigation-playbook"}
ALLOWED_EVENTS = {"scenario_complete", "counterfactual_complete", "knowledge_check_complete", "card_export"}
EVENT_FIELDS = {
    "scenario_complete": {"guide_id", "scenario_id", "decision_grade", "confidence_band"},
    "counterfactual_complete": {"guide_id", "scenario_id", "reconsidered"},
    "knowledge_check_complete": {"guide_id", "score", "total"},
    "card_export": {"guide_id", "export_type"},
}
# Shared site chrome IDs and classes that every guide inherits from the common nav and footer mounts.
SHARED_IDS = {"main-content", "navHamburger", "mobileNav", "site-footer"}
SHARED_CLASSES = {"nav-brand", "nav-links", "nav-cta", "nav-hamburger", "mobile-nav", "open"}
SHARED_SCRIPTS = {"/js/site-chrome.js", "/brand.js"}
# Facts that belong to existing Scenario Lab cases session-hijack-002 and device-network-006.
CASE_STRINGS = (
    "lagos", "impossible travel", "micro-token", "gift voucher", "empty box", "empty-box", "android",
    "residential proxy", "entrance code", "tampered box", "four accounts", "60 days",
)
NAMESPACES_BANNED = ("dicdd-", "r16-", "ftpf-", "fcdd-", "apps-", "mmv-", "kyb-", "ecom-", "gwb-")
VISA_CAVEAT = "does not replace the Visa Rules, merchant agreements, acquirer requirements or applicable law"

COVERED: set[str] = set()


class KnowledgeCountParser(HTMLParser):
    """Mirror Knowledge Hub declared-card counting."""

    VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.count_text: dict[str, list[str]] = {"khHeroCount": [], "khStatGuides": []}
        self.standalone = 0
        self.series = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
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


class FocusScan(HTMLParser):
    """First focusable element in the body, ignoring noscript, template, script and style content."""

    def __init__(self) -> None:
        super().__init__()
        self.in_body = False
        self.skip_depth = 0
        self.first: tuple[str, dict[str, str | None]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "body":
            self.in_body = True
        if tag in ("noscript", "template", "script", "style"):
            self.skip_depth += 1
            return
        if not self.in_body or self.skip_depth or self.first is not None:
            return
        ti = a.get("tabindex")
        focusable = (tag == "a" and "href" in a) or tag in ("button", "select", "textarea", "summary") or (
            tag == "input" and a.get("type") != "hidden")
        if focusable and ti != "-1" and "disabled" not in a:
            self.first = (tag, a)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("noscript", "template", "script", "style") and self.skip_depth:
            self.skip_depth -= 1


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def req(ids: str, condition: bool, message: str) -> None:
    """Assert a condition and record the requirement IDs it proves."""
    if not condition:
        fail(f"[{ids}] {message}")
    COVERED.update(item.strip() for item in ids.split(","))


def text_only(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", without_tags.replace("&rsquo;", "'").replace("&ldquo;", '"').replace("&rdquo;", '"')
                  .replace("&pound;", "£").replace("&amp;", "&")).strip()


def section(html: str, section_id: str) -> str:
    match = re.search(rf'<section\b[^>]*\bid="{section_id}".*?</section>', html, re.S)
    if match is None:
        fail(f"section missing: {section_id}")
    return match.group(0)


def list_by_id(html: str, list_id: str) -> str:
    match = re.search(rf'<(ol|ul)\b[^>]*\bid="{list_id}"[^>]*>(.*?)</\1>', html, re.S)
    if match is None:
        fail(f"list missing: {list_id}")
    return match.group(0)


def main() -> None:
    for path in (GUIDE, SCRIPT, CARD):
        req("V01", path.exists(), f"required file missing: {path.name}")

    html = GUIDE.read_text(encoding="utf-8").replace("\r\n", "\n")
    script = SCRIPT.read_text(encoding="utf-8").replace("\r\n", "\n")
    knowledge = (ROOT / "knowledge.html").read_text(encoding="utf-8").replace("\r\n", "\n")
    relations = json.loads((ROOT / "content-relations.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "verification-ledger.json").read_text(encoding="utf-8"))
    body_text = text_only(re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S))

    # ---- H: information architecture and semantic HTML ----
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', html)
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    req("H07", not duplicates, f"duplicate IDs: {duplicates}")
    generic = [item for item in ids if not item.startswith("ecf-") and item not in SHARED_IDS]
    req("H07", not generic, f"non-namespaced IDs: {generic}")
    names = re.findall(r'\bname="([^"]+)"', html)
    req("H07", all(name.startswith("ecf-") for name in names if name not in {"viewport", "description", "author", "robots"}
                   and not name.startswith("twitter:") and name != "googlefcPresent"),
        "form control names must be ecf-namespaced")
    id_set = set(ids)
    for fragment in re.findall(r'href="#([^"]+)"', html):
        req("H07, H10", fragment in id_set, f"unresolved fragment: #{fragment}")
    labels_for = re.findall(r'<label\b[^>]*\bfor="([^"]+)"', html)
    req("H07, A01", all(item in id_set for item in labels_for), "label for= target missing")
    req("H02", html.count("<h1") == 1, "expected exactly one h1")
    headings = [int(level) for level in re.findall(r"<h([1-6])\b", html)]
    for previous, current in zip(headings, headings[1:]):
        req("H02", current <= previous + 1, f"heading order skips from h{previous} to h{current}")
    section_ids = re.findall(r'<section\b[^>]*\bid="([^"]+)"', html)
    req("H01", section_ids == SECTION_ORDER, f"section order differs: {section_ids}")
    req("H01", len(section_ids) == 18, "expected 18 sections")

    focus = FocusScan()
    focus.feed(html)
    req("H03", focus.first is not None and focus.first[0] == "a" and focus.first[1].get("href") == "#main-content",
        f"skip link is not the first focusable element: {focus.first}")
    req("H03", re.search(r'<main id="main-content" tabindex="-1">', html) is not None, "skip target must carry tabindex=-1")

    flow = re.findall(r"<strong>([^<]+)</strong>", list_by_id(html, "ecf-flow-list"))
    req("E04", flow == LIFECYCLE and len(set(flow)) == 6, f"lifecycle flow differs: {flow}")
    stage_list = list_by_id(html, "ecf-stage-list")
    stages = re.findall(r'<h3 class="ecf-step-title">([^<]+)</h3>', stage_list)
    req("E04", stages == LIFECYCLE, f"lifecycle detail differs: {stages}")
    levels = re.findall(r"<li><strong>([^<]+)</strong>", list_by_id(html, "ecf-levels-list"))
    req("E05", levels == LEVELS, f"decision levels differ: {levels}")
    relay = re.findall(r'<h3 class="ecf-step-title">([^<]+)</h3>', list_by_id(html, "ecf-relay-list"))
    req("E06", relay == RELAY and len(set(relay)) == 6, f"relay fields differ: {relay}")
    backtrace = re.findall(r'<h3 class="ecf-step-title">([^<]+)</h3>', list_by_id(html, "ecf-backtrace-list"))
    req("E08", backtrace == BACKTRACE and len(set(backtrace)) == 7, f"backtrace steps differ: {backtrace}")
    outcomes = re.findall(r'<h3 class="ecf-step-title">([^<]+)</h3>', list_by_id(html, "ecf-outcome-list"))
    req("E10", outcomes == OUTCOMES, f"outcome boundaries differ: {outcomes}")
    req("E10", "No badge, status or label in this guide merges these five outcomes into one fraud status." in body_text,
        "no-merger statement missing")
    groups = re.findall(r"<li><h3>([^<]+)</h3><ul>(.*?)</ul></li>", section(html, "ecf-checklist"), re.S)
    req("E22", [name for name, _ in groups] == CHECKLIST, f"checklist groups differ: {[name for name, _ in groups]}")
    req("E22", all(bullets.count("<li>") == 3 for _, bullets in groups), "each checklist group needs three bullets")
    for list_id in ("ecf-flow-list", "ecf-stage-list", "ecf-levels-list", "ecf-relay-list", "ecf-backtrace-list",
                    "ecf-outcome-list", "ecf-checklist-groups"):
        req("H04", f'<ol class="ecf-' in list_by_id(html, list_id)[:40] or f'<ul class="ecf-' in list_by_id(html, list_id)[:40],
            f"{list_id} is not a semantic list")

    # H05: fieldsets and legends (2 scenarios x 3, 5 quiz questions)
    fieldsets = re.findall(r"<fieldset\b[^>]*>(.*?)</fieldset>", html, re.S)
    req("H05", len(fieldsets) == 11, f"expected 11 fieldsets, found {len(fieldsets)}")
    req("H05", all(item.lstrip().startswith("<legend>") for item in fieldsets), "every fieldset needs a leading legend")
    req("H06", html.count("<details") == 2 + 6 + 1, "expected 2 reasoning, 6 FAQ and 1 answer-key details")
    req("H06", html.count("<details") == html.count("<summary"), "details and summary counts differ")
    req("H06", "querySelectorAll('details" not in script and "faq" not in script.lower(), "FAQ must use native disclosure, not a script toggle")

    classes = {item for value in re.findall(r'class="([^"]+)"', html) for item in value.split()}
    stray = sorted(c for c in classes if not c.startswith("ecf-") and c not in SHARED_CLASSES)
    req("H08", not stray, f"non-namespaced classes: {stray}")
    req("H08", not any(any(token in c for token in ("card", "btn")) for c in classes),
        "class names must avoid card and btn substrings that brand.css and brand.js watch")
    req("H08", not any(token.startswith(ns) for token in classes | id_set for ns in NAMESPACES_BANNED), "existing subject namespace reused")
    req("H08", 'class="card"' not in html and 'class="btn"' not in html, "generic experimental classes found")

    # H09 and J: script and static-first
    material = ("Bounded conclusion", "Rights Collapse", "Local Green Light", "hindsight", "account takeover", "Visa Rules", "Regulation 7")
    req("H09", not any(item in script for item in material), "script contains material guide copy")
    req("H09", max((len(item) for item in re.findall(r"'([^'\\]*)'", script)), default=0) < 180,
        "script string longer than 180 characters suggests embedded reasoning")
    req("J02", not re.search(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|createContextualFragment|DOMParser", script),
        "script constructs HTML strings")
    req("J03", not re.search(r"fetch\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|import\(", script),
        "script makes a network call")
    req("J03", not re.search(r"<form\b[^>]*\b(action|method)=", html), "form submits to a server")
    scripts = re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', html)
    page_scripts = [item for item in scripts if item.startswith("/js/") and item not in SHARED_SCRIPTS]
    req("J01", page_scripts == [f"/js/{SLUG}.js"], f"page-specific script differs: {page_scripts}")
    inline = re.findall(r"<script>(.*?)</script>", html, re.S)
    req("J01", all("gtag" in item or "googlefcPresent" in item for item in inline), "unexpected inline script")
    events = re.findall(r"emitAggregateEvent\(\s*'([^']+)'", script)
    req("J04", set(events) == ALLOWED_EVENTS and len(events) == 4, f"telemetry event set differs: {events}")
    req("J05", "fcr_cookie_consent_v2" in script and "=== 'accepted'" in script and "consentGranted()" in script
        and re.search(r"function emitAggregateEvent[^{]*\{\s*if \(!consentGranted\(\)", script) is not None,
        "telemetry consent gate missing")
    for event in events:
        call = re.search(rf"emitAggregateEvent\(\s*'{event}',\s*\{{(.*?)\}}\s*\)", script, re.S)
        req("J06, J07, J08, J09", call is not None, f"{event} payload not found")
        keys = set(re.findall(r"(\w+)\s*:", call.group(1)))
        req("J06, J07, J08, J09", keys == EVENT_FIELDS[event], f"{event} fields differ: {keys}")
    for forbidden in ("customer_name", "account_number", "free_text", "selected_text", "rationale", "address", "device_id",
                      "order_id", "textContent", "option_text"):
        payloads = " ".join(re.findall(r"emitAggregateEvent\([^)]*\{.*?\}\s*\)", script, re.S))
        req("J10", forbidden not in payloads, f"sensitive telemetry field found: {forbidden}")
    req("J13", not re.search(r"localStorage\.setItem|sessionStorage|indexedDB|document\.cookie", script),
        "script persists state")
    req("J13", not re.search(r'<textarea|type="text"|type="email"|contenteditable', html), "free-text collection found")
    req("J11, S15", "ecf-closing-patterns-grid" in script and "toBlob" in script and "var width = 1200" in script
        and "image/png" in script, "export must paint the closing grid to a 1200 wide PNG")
    req("J12", "Export unavailable." in script and script.count("try {") >= 2 and "catch (error)" in script,
        "non-destructive failure paths missing")
    node = subprocess.run(["node", "--check", str(SCRIPT)], capture_output=True, text=True)
    req("J14", node.returncode == 0, f"node --check failed: {node.stderr}")

    # H10, E24, E25, E26: citations and sources
    source_ids = re.findall(r'<li id="ecf-source-(\d+)">', html)
    req("E24, H10", source_ids == [str(i) for i in range(1, 11)], f"expected ten numbered sources: {source_ids}")
    cited = set(re.findall(r'href="#ecf-source-(\d+)"', html))
    req("E24, H10", cited == set(source_ids), f"every source must be cited: uncited {set(source_ids) - cited}")
    source_li = {m.group(1): m.group(2) for m in re.finditer(r'<li id="ecf-source-(\d+)">(.*?)</li>', html, re.S)}
    req("E25", "Industry evidence, not regulatory authority" in source_li["1"], "UK Finance label missing")
    req("E25", "Law-enforcement prevention guidance" in source_li["5"], "Europol label missing")
    req("E25", "Scheme guidance" in source_li["6"], "Visa label missing")
    req("E25", "United States public sentencing record" in source_li["10"], "DOJ label missing")
    req("E17", "not a United Kingdom authority or a prevalence measure" in text_only(source_li["10"]), "DOJ boundary missing")
    for number, label in (("2", "European Economic Area scope"),):
        req("E24", label in source_li[number], f"source {number} scope missing")
    public_urls = set(re.findall(r'href="(https://[^"]+)"', " ".join(source_li.values())))
    req("L04", len(public_urls) == 17, f"expected seventeen public source URLs, found {len(public_urls)}")
    req("E24, L04", {"https://www.legislation.gov.uk/uksi/2017/752/regulation/74", "https://handbook.fca.org.uk/technical-standards/provision/s140c1221sn0p1814", "https://handbook.fca.org.uk/technical-standards/s140c1226"} <= public_urls, "regulation 74 or FCA technical standards URL missing from sources")
    req("E24", "regulation 74" in source_li["7"] and "application" in source_li["3"] and "exemptions" in source_li["3"], "source 3 or 7 link labels missing")
    methodology = section(html, "ecf-sources")
    outside = html.replace(methodology, "")
    req("E26", "Microsoft" in methodology and "Stripe" in methodology, "originality note missing")
    req("E26", "Microsoft" not in outside and "Stripe" not in outside and "INFORMS" not in outside,
        "Microsoft, Stripe or INFORMS cited outside methodology")
    req("E26", 'ecf-source-11' not in html and 'ecf-source-12' not in html, "originality sources must not become citations")

    # E: editorial
    visible = body_text
    req("E01", f"<title>{TITLE} | FinCrimeRadar</title>" in html, "page title differs")
    req("E01", f'<h1 id="ecf-title">{TITLE}</h1>' in html, "visible h1 differs")
    req("E01", STANDFIRST in html, "locked standfirst differs")
    req("E01", html.count("<li>Evidence checked 18 October 2026</li>") == 1 and "<dd>18 October 2026.</dd>" in html, "evidence date differs")
    req("E01", '<span class="ecf-format">Guide</span>' in html and "<li>Fraud</li>" in html, "format or category differs")
    status = section(html, "ecf-hero")
    req("E02", re.findall(r"<dt>([^<]+)</dt>", status) == STATUS_LABELS, "evidence status labels differ")
    req("E02", "How should a merchant preserve, qualify and relay fraud evidence across the e-commerce lifecycle when no single stage sees the full pattern?" in visible,
        "intelligence question missing")
    req("E02", "United Kingdom law is used only for the identified payment-service and consumer-rights boundaries" in visible,
        "jurisdiction boundary missing")
    req("E02", "evidence showing that the Fraud Evidence Relay duplicates an authoritative merchant standard" in visible,
        "next trigger missing")
    req("E03", "move the evidence, its uncertainty and its decision level together" in visible, "thesis missing")
    req("E07", "are FinCrimeRadar assessments. They are not legal rules, card-scheme terminology or vendor methods" in visible
        and "FinCrimeRadar control model" in visible
        and "decision-level model and five control patterns are FinCrimeRadar assessments" in visible,
        "FinCrimeRadar attribution missing")
    req("E09", "The backtrace is not hindsight blame. It asks whether the earlier decision was reasonable on the evidence available then, and whether the later evidence should change future controls." in visible,
        "backtrace boundary missing")
    executive = text_only(section(html, "ecf-executive-assessment"))
    for pin in ("£423.5 million", "3.2 million cases for 2025",
                "industry-reported card or account incidents, not total e-commerce fraud or total merchant loss"):
        req("E11", pin in executive, f"UK Finance pin missing: {pin}")
    req("E12", "Authentication can reduce fraud without proving who controlled an account, whether a customer acted honestly, whether goods were delivered, whether a refund is due or whether a later dispute can be answered successfully." in executive,
        "authentication boundary missing from main text")
    faq = text_only(section(html, "ecf-faq"))
    req("E12", "It does not by itself prove who controlled an account, honest intent, delivery, refund legitimacy or the result of a later dispute." in faq,
        "authentication boundary missing from FAQ")
    lifecycle = text_only(section(html, "ecf-lifecycle"))
    req("E13", "Credential stuffing is one route by which reused credentials can give an attacker access to a legitimate account." in lifecycle
        and "a recovery event or new device is not proof of compromise" in lifecycle, "credential stuffing limit missing")
    for sid in re.findall(r'<section\b[^>]*\bid="([^"]+)"', html):
        block = section(html, sid)
        if 'href="#ecf-source-6"' in block:
            req("E14", VISA_CAVEAT in text_only(block), f"Visa caveat missing in {sid}")
    req("E14", VISA_CAVEAT in text_only(source_li["6"]), "Visa caveat missing in source record")
    outcome = text_only(section(html, "ecf-outcome-boundary"))
    req("E15", "payer consent, authentication evidence and payment service provider refund duties are separate matters with statutory conditions and exceptions" in outcome
        and "They are not a universal merchant chargeback rule" in outcome
        and "Regulation 67" in outcome and "Regulation 75" in outcome and "Regulation 76" in outcome
        and "subject to regulations 74 and 75" in outcome, "payment-service boundary missing")
    req("E16", "A merchant fraud concern does not automatically extinguish those rights." in outcome, "consumer-rights qualification missing")
    scenario2 = text_only(section(html, "ecf-worked-decision-2"))
    req("E17", "pleaded guilty" in scenario2 and "United States" in scenario2 and "sentenced" in scenario2, "DOJ status missing")
    req("E18", html.count("Fictional and illustrative.") == 2, "fictional label must appear at both scenarios")
    req("E19", "nisbets" not in html.lower() and "nisbets" not in script.lower(), "employer name present")
    for forbidden in ("my employer", "our client", "employer-specific"):
        req("E19", forbidden not in visible.lower().replace("do not describe any employer or client", ""), f"employer framing: {forbidden}")
    req("E27", "%" not in visible and "per cent" not in visible.lower() and "percent" not in visible.lower(),
        "unsupported percentage figure")
    for pattern in (r"false[- ]positive rate", r"conversion rate", r"chargeback win", r"loss reduction of"):
        req("E27", re.search(pattern, visible, re.I) is None, f"invented metric pattern: {pattern}")
    for banned in ("fraud score", "risk score", "vendor ranking", "best vendor", "recommended vendor", "automatically guilty"):
        req("E28", banned not in visible.lower(), f"banned product claim: {banned}")
    req("E29", "There is no universal answer." in faq and "An internal fraud review does not automatically suspend statutory or scheme timelines." in faq
        and "Use current legal and acquirer guidance before delaying, refusing or reducing a refund." in faq
        and "This guide is practitioner analysis, not legal advice" in faq, "refund-delay qualification missing")
    for case in CASE_STRINGS:
        req("E30", case not in visible.lower(), f"existing Scenario Lab fact reused: {case}")

    # S: scenarios
    scenarios = re.findall(r'<article class="ecf-scenario".*?</article>', html, re.S)
    req("S01", len(scenarios) == 2, "expected two scenarios")
    expected_grades = {1: ["weak", "caution", "strongest"], 2: ["caution", "weak", "strongest"]}
    expected_ids = {1: "authenticated_order_fragmented_evidence", 2: "refund_claims_possible_network"}
    strongest = {
        1: "Pause the order for bounded review, assemble the cross-stage relay, verify the material change through a trusted existing channel, and make an order decision without treating the evidence as an account-level fraud finding.",
        2: "Decide the individual customer's entitlement on its own facts, separately escalate the linked-network hypothesis, preserve the cross-order evidence and apply proportionate account or fulfilment controls without treating the link as proof of fraud.",
    }
    for index, block in enumerate(scenarios, start=1):
        text = text_only(block)
        req("S01", f'data-scenario-id="{expected_ids[index]}"' in block, f"scenario {index} ID differs")
        radios = re.findall(r'<input type="radio" id="ecf-s\d-[abc]"[^>]*>', block)
        req("S04", len(radios) == 3, f"scenario {index} must contain three options")
        grades = [re.search(r'data-grade="(\w+)"', item).group(1) for item in radios]
        req("S04, S05, S06", grades == expected_grades[index], f"scenario {index} grade order differs: {grades}")
        req("S04", sorted(grades) == ["caution", "strongest", "weak"], f"scenario {index} needs one of each grade")
        req("S07, S08", strongest[index] in text, f"scenario {index} strongest option differs")
        req("S09", len(re.findall(r'name="ecf-s\d-confidence"', block)) == 3
            and all(f'value="{band}"' in block for band in ("High", "Medium", "Low")), f"scenario {index} confidence bands differ")
        req("E20", all(f"<strong>{label}</strong>" in block for label in ("Source", "Application", "Action")),
            f"scenario {index} missing Source, Application or Action")
        req("E21", block.count("Counterfactual:") == 1, f"scenario {index} must hold one counterfactual")
        req("E18", "Fictional and illustrative." in text, f"scenario {index} fictional label missing")
        req("S01", 'aria-live="polite" role="status"' in block, f"scenario {index} status semantics missing")
    one, two = text_only(scenarios[0]), text_only(scenarios[1])
    req("S02", all(item in one for item in ("high-value order from an established account", "Payment authentication succeeds",
                                              "recent recovery event", "new device and delivery address",
                                              "address-change request after approval", "What should happen before dispatch?")),
        "Scenario 1 facts differ")
    req("S03", all(item in two for item in ("individually plausible non-delivery or return claims", "linked accounts and repeated refund outcomes",
                                              "shared household or another innocent explanation", "legitimate statutory rights",
                                              "How should the current claim and possible network be handled?")),
        "Scenario 2 facts differ")
    req("S07", "do not yet prove account takeover, dishonest intent or criminal conduct" in one
        and "trusted pre-existing contact route" in one and "without treating the evidence as an account-level fraud finding" in one,
        "Scenario 1 Action reasoning differs")
    req("S08", "does not by itself decide the individual refund entitlement, customer intent, scheme outcome or criminal conclusion" in two
        and "maker-checker review" in two and "Keep the individual refund decision and linked-network assessment separate" in two,
        "Scenario 2 Action reasoning differs")
    req("E21", "They do not make authentication proof of honest intent." in one
        and "without rewriting what was known at the initial decision" in two, "counterfactual outcome language differs")
    req("S12", 'id="ecf-s1-original"' in html and 'data-cf-form' in html and "ecf-cf-status" in html,
        "original-answer and reconsideration markers missing")

    # S13, S14: patterns
    found: dict[str, list[dict[str, str]]] = {}
    for match in re.finditer(r'<(aside|article) class="ecf-pattern(?: ecf-pattern-inline)?" data-pattern-id="([^"]+)">(.*?)</\1>', html, re.S):
        found.setdefault(match.group(2), []).append({"tag": match.group(1), "text": text_only(match.group(3)),
                                                      "inline": "ecf-pattern-inline" in match.group(0)})
    req("S13", set(found) == set(PATTERNS), f"pattern families differ: {set(found)}")
    for pid, (name, risk, signal, response) in PATTERNS.items():
        copies = found[pid]
        req("S14", len(copies) == 2, f"{pid} must appear twice")
        req("S14", copies[0]["text"] == copies[1]["text"], f"{pid} copies differ")
        req("S14", sum(item["inline"] for item in copies) == 1 and sum(not item["inline"] for item in copies) == 1,
            f"{pid} needs one inline and one closing copy")
        for line in (name, f"Risk {risk}", f"Signal {signal}", f"Response {response}"):
            req("S13", line in copies[0]["text"], f"{pid} locked text differs: {line[:40]}")
    grid = section(html, "ecf-closing-patterns")
    req("S14", grid.count('data-pattern-id="') == 5 and 'id="ecf-closing-patterns-grid"' in grid, "closing grid must hold five patterns")

    # K: knowledge check and FAQ
    quiz = section(html, "ecf-knowledge-check")
    questions = re.findall(r"<fieldset><legend>(.*?)</legend>(.*?)</fieldset>", quiz, re.S)
    req("K01", len(questions) == 5, "knowledge check must contain five questions")
    letters = []
    longest_correct = 0
    shortest_correct = 0
    key = re.findall(r"<strong>Correct answer: ([ABC])\.</strong>", quiz)
    req("K02", key == ["B", "C", "A", "B", "C"], f"answer key order differs: {key}")
    for index, (legend, inner) in enumerate(questions, start=1):
        options = re.findall(r'<input type="radio" id="ecf-q\d-[abc]" name="ecf-q\d" value="([ABC])"><span><strong>[ABC]\.</strong> (.*?)</span>', inner)
        req("K01", len(options) == 3 and [letter for letter, _ in options] == ["A", "B", "C"], f"question {index} needs three options")
        lengths = [len(text_only(text)) for _, text in options]
        correct_index = "ABC".index(key[index - 1])
        longest_correct += lengths[correct_index] == max(lengths)
        shortest_correct += lengths[correct_index] == min(lengths)
        letters.append(key[index - 1])
    req("K05", longest_correct <= 2 and shortest_correct <= 2,
        f"correct option is the longest in {longest_correct} and the shortest in {shortest_correct} questions")
    req("K05", "data-correct" not in html and "correct" not in " ".join(re.findall(r'class="([^"]+)"', html))
        and 'aria-label="' not in quiz, "quiz DOM leaks correctness")
    req("K05", not re.search(r"QUIZ_KEY|correct", script.replace("Correct", "")) or "QUIZ_KEY" in script,
        "answer key must live in the script, not the radio DOM")
    req("K03", 'id="ecf-kc-feedback" aria-live="polite" role="status"' in quiz, "knowledge status semantics missing")
    req("K04", "In Scenario 1, the recovery and address change are independently verified through a known channel and the new device fits prior behaviour. What changes?" in text_only(quiz)
        and "The counterfactual changes the order risk, not what authentication proves." in text_only(quiz), "question 5 differs")
    faq_items = re.findall(r"<details><summary>(.*?)</summary>", section(html, "ecf-faq"))
    req("K06", faq_items == [
        "Does strong customer authentication prove that an e-commerce order is genuine?",
        "Is a chargeback outcome the same as a fraud finding?",
        "Can a merchant delay a refund while investigating abuse?",
        "When should device or account links change an individual case decision?",
        "What evidence should move from checkout to fulfilment and disputes?",
        "Does the Fraud Evidence Relay require a new platform or backend?"], f"FAQ questions differ: {faq_items}")
    req("K07", "no universal answer" in faq.lower() and "does not automatically suspend statutory or scheme timelines" in faq
        and "current legal and acquirer guidance" in faq, "refund-delay qualifications missing")
    req("K08", "No. It can be implemented as a governed record in an existing order, case or investigation system, or as a controlled static form." in faq
        and "Any system implementation is a separate design and governance decision." in faq, "no-backend answer differs")
    triggers = re.search(r'<ol class="ecf-triggers" id="ecf-triggers-list">(.*?)</ol>', html, re.S)
    req("E23", triggers is not None and triggers.group(1).count("<li>") == 6, "six assessment triggers required")

    # H11, D: metadata, discovery, relationships
    required_meta = (
        f'<link rel="canonical" href="{CANONICAL}">',
        f'<meta name="description" content="{DESCRIPTION}">',
        f'<meta property="og:title" content="{SHORT_TITLE}">',
        f'<meta property="og:description" content="{DESCRIPTION}">',
        f'<meta property="og:url" content="{CANONICAL}">',
        f'<meta property="og:image" content="{CARD_URL}">',
        '<meta property="article:published_time" content="2026-10-18">',
        '<meta property="article:modified_time" content="2026-10-18">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{SHORT_TITLE}">',
        f'<meta name="twitter:description" content="{DESCRIPTION}">',
        f'<meta name="twitter:image" content="{CARD_URL}">',
    )
    for metadata in required_meta:
        req("D07", html.count(metadata) == 1, f"metadata missing or duplicated: {metadata}")
    req("D07", len(DESCRIPTION) <= 160 and "Fraud Evidence Relay" in DESCRIPTION and "fraud finding" not in DESCRIPTION.lower(),
        "description must be short, keep the relay thesis and not imply a fraud determination")
    json_ld = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
    req("H11", len(json_ld) == 2, "expected Article and BreadcrumbList JSON-LD")
    structured = [json.loads(block) for block in json_ld]
    article = next((item for item in structured if item.get("@type") == "Article"), None)
    breadcrumb = next((item for item in structured if item.get("@type") == "BreadcrumbList"), None)
    req("H11, D09", article is not None and article.get("headline") == TITLE and article.get("description") == DESCRIPTION
        and article.get("image") == CARD_URL and article.get("datePublished") == "2026-10-18"
        and article.get("dateModified") == "2026-10-18" and article.get("mainEntityOfPage", {}).get("@id") == CANONICAL,
        "Article JSON-LD differs from visible metadata")
    req("H11", breadcrumb is not None and breadcrumb["itemListElement"][-1]["item"] == CANONICAL
        and breadcrumb["itemListElement"][1]["name"] == "Fraud", "BreadcrumbList differs")

    card_match = re.search(rf'<a href="/{re.escape(GUIDE_NAME)}".*?</a>', knowledge, re.S)
    req("D01", card_match is not None, "Knowledge Hub card missing")
    card = card_match.group(0)
    req("D01, D09", 'data-date="2026-10-18"' in card and 'kh-cat">Fraud<' in card and 'kh-format-label">Guide<' in card
        and f'<div class="kh-item-title">{TITLE}</div>' in card and "evidence, uncertainty and decision level" in card
        and "Fraud Evidence Relay" in card, "Knowledge Hub card differs")
    req("D01", knowledge.count(f'href="/{GUIDE_NAME}"') == 1, "Knowledge Hub card must appear once")
    hub = KnowledgeCountParser()
    hub.feed(knowledge)
    declared = hub.standalone + hub.series
    for count_id in ("khHeroCount", "khStatGuides"):
        value = "".join(hub.count_text[count_id]).strip()
        req("D02", value.isdigit() and int(value) == declared, f"{count_id} differs from declared total {declared}")
    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    records = [node for node in sitemap.getroot().findall("s:url", namespace)
               if node.findtext("s:loc", namespaces=namespace) == CANONICAL]
    req("D03", len(records) == 1, "sitemap canonical must appear once")
    req("D03", records[0].findtext("s:priority", namespaces=namespace) == "0.7"
        and records[0].findtext("s:changefreq", namespaces=namespace) == "monthly", "sitemap priority or frequency differs")
    req("D04", set(relations.get(SLUG, [])) == RELATED and len(relations[SLUG]) == 2, "content relation set differs")
    req("D06", "synthetic-identity-device-network-guide" not in relations[SLUG], "synthetic identity relation must not be added")
    req("D06", SLUG not in relations.get("synthetic-identity-device-network-guide", []), "synthetic identity guide must not reciprocate")
    for target in RELATED:
        req("D04", SLUG in relations.get(target, []), f"relation not reciprocal: {target}")
        target_html = (ROOT / f"{target}.html").read_text(encoding="utf-8")
        related_block = target_html[target_html.index('id="related-topics"'):]
        req("D04", f"/{GUIDE_NAME}" in related_block[:related_block.index("</ul>")], f"rendered backlink missing: {target}")
    related = section(html, "ecf-related")
    req("D05", sorted(re.findall(r'<li><a href="/([^"]+)\.html">', related)) == sorted(RELATED), "Related Topics items differ")
    with Image.open(CARD) as image:
        req("D08", image.format == "PNG" and image.size == (1200, 630) and image.getbbox() is not None,
            "social card must be a non-blank 1200 by 630 PNG")
    req("D08", CARD.stat().st_size <= 400_000, "social card exceeds 400KB")
    leaks = ("Claude Code", "Codex", "queue state", "READY", "QUALIFIED", "Requirement Coverage", "Content Loop", "source pack", "Part 1",
             "design memo", "review-queue", "Experiment")
    req("D10", not any(item in html for item in leaks), f"internal workflow label exposed: {[i for i in leaks if i in html]}")
    req("D11", "e-commerce-fraud" not in (ROOT / "methodology.html").read_text(encoding="utf-8"), "methodology.html must not mention the guide")
    words = len(text_only(re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)).split())
    minutes = re.search(r"(\d+) min read", html)
    hub_minutes = re.search(r'kh-read">(\d+) MIN', card)
    req("D12", minutes is not None and hub_minutes is not None and minutes.group(1) == hub_minutes.group(1)
        and abs(words / 180 - int(minutes.group(1))) <= 1.5,
        f"reading time {minutes and minutes.group(1)} / {hub_minutes and hub_minutes.group(1)} does not match {words} words at about 180 wpm")

    # L: ledger
    claims = [item for item in ledger if item.get("guide") == GUIDE_NAME]
    req("L02", len(claims) == 14, f"expected fourteen ledger claims, found {len(claims)}")
    req("L03", all(item.get("status") == "verified" and item.get("verifiedOn") == "2026-10-18" and item.get("reviewDue")
                   and item.get("source", {}).get("url", "").startswith("https://") for item in claims), "ledger record incomplete")
    req("L03", len({item["claimId"] for item in claims}) == 14 and all(item["claimId"].startswith("e-commerce-fraud-system.") for item in claims),
        "ledger claim IDs differ")
    topics = " ".join(item["claimText"] for item in claims)
    for needle in ("£423.5 million", "3.2 million", "strong customer authentication remains effective", "regulation 67", "regulation 75",
                   "regulation 74", "regulation 76", "Consumer Rights Act 2015", "Consumer Contracts", "credential stuffing", "Europol", "Visa",
                   "Artemis Refund Group", "payment service providers"):
        req("L02", needle.lower() in topics.lower(), f"ledger claim missing for: {needle}")
    reg_claims = [item for item in claims if "psr-2017-reg" in item["claimId"]]
    req("L02", len(reg_claims) == 4 and len({item["source"]["url"] for item in reg_claims}) == 4, "regulations 67, 74, 75 and 76 need distinct claims")
    ledger_urls = {item["source"]["url"] for item in claims}
    req("L04", ledger_urls <= public_urls, f"ledger URL absent from public sources: {ledger_urls - public_urls}")
    req("L04", {"https://www.legislation.gov.uk/uksi/2013/3134/regulation/34"} <= public_urls, "regulation 34 URL missing from page")
    req("L05", not any(term in topics.lower() for term in ("fraud evidence relay", "backtrace", "level jump", "local green light")),
        "ledger must not record FinCrimeRadar assessments as sourced claims")

    # A and V: static halves of browser requirements
    css = "".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    defined = set(re.findall(r"(--ecf-[\w-]+)\s*:", css))
    used = set(re.findall(r"var\((--[\w-]+)", css))
    req("A01", used <= defined, f"var() without a page :root definition: {sorted(used - defined)}")
    req("A01, A09", ":focus-visible" in css and "outline:3px solid" in css, "visible focus style missing")
    req("A06", "prefers-reduced-motion:reduce" in css, "reduced-motion rule missing")
    req("A08", 'aria-expanded="false" aria-controls="mobileNav"' in html and "aria-expanded" in script, "mobile menu state missing")
    req("A10", "min-height:44px" in css, "touch target size missing")
    req("A02", 'id="ecf-visual-text"' in html and all(name.lower() in text_only(re.search(r'<p class="ecf-visual-text".*?</p>', html, re.S).group(0)).lower()
                                                     for name in LIFECYCLE), "textual equivalent for the lifecycle visual missing")
    req("H12", 'id="ecf-lifecycle-figure"' in html and 'id="ecf-return-path"' in html, "forward relay and reverse feedback visual missing")
    req("H13", html.count("<figure") == 1 and "<svg" not in html and "<canvas" not in html and "<img" == html[html.index("<img"):html.index("<img") + 4]
        and html.count("<img") == 1, "second process diagram found")
    req("A07", "<noscript>" in html, "no-script notice missing")
    req("V01", True, "static checker present")

    for name, content in ((GUIDE.name, html), (SCRIPT.name, script), ("checker", Path(__file__).read_text(encoding="utf-8"))):
        req("V01", chr(0x2014) not in content and chr(0x2013) not in content, f"em or en dash found in {name}")

    print("PASS: E-commerce Fraud System static release contract")
    print(f"OK: {len(ids)} IDs, 18 sections, 2 scenarios, 5 pattern families, 5 questions, 6 FAQs, 10 source records, "
          f"{len(claims)} ledger claims, {declared} Hub guides")
    print(f"COVERED: {len(COVERED)} requirement IDs asserted statically: {' '.join(sorted(COVERED))}")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, OSError, StopIteration, ET.ParseError, ValueError) as error:
        fail(str(error))
