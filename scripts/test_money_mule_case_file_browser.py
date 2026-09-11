#!/usr/bin/env python3
"""Headless Chrome regression checks for the Money Mule or Victim Case File.

Harness classes (QuietHandler, QuietServer, CDP) and the WIDTHS constant are
copied verbatim from scripts/test_app_scam_framework_browser.py, per the
Task 15 brief, so this file drives a different page through a much longer
12-stage interactive flow rather than reinventing the browser-automation
plumbing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import requests
import websocket

ROOT = Path(__file__).resolve().parents[1]
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        return


class CDP:
    def __init__(self, url: str) -> None:
        self.socket = websocket.create_connection(url, timeout=20)
        self.message_id = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.message_id += 1
        message_id = self.message_id
        self.socket.send(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        while True:
            response = json.loads(self.socket.recv())
            if response.get("id") == message_id:
                if "error" in response:
                    raise RuntimeError(f"{method}: {response['error']}")
                return response.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = False) -> Any:
        result = self.call("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": await_promise,
        })
        remote = result.get("result", {})
        if remote.get("subtype") == "error":
            raise RuntimeError(remote.get("description", "browser evaluation failed"))
        return remote.get("value")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def wait_ready(cdp: CDP) -> None:
    for _ in range(80):
        if cdp.evaluate("document.readyState") == "complete":
            cdp.evaluate("document.fonts ? document.fonts.ready.then(() => true) : Promise.resolve(true)", True)
            time.sleep(0.15)
            return
        time.sleep(0.1)
    raise TimeoutError("page did not reach readyState complete")


def navigate(cdp: CDP, url: str, width: int) -> None:
    cdp.call("Emulation.setDeviceMetricsOverride", {
        "width": width,
        "height": 900,
        "deviceScaleFactor": 1,
        "mobile": width < 768,
    })
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)


def reload_page(cdp: CDP) -> None:
    cdp.call("Page.reload", {"ignoreCache": True})
    wait_ready(cdp)


def dispatch_key(cdp: CDP, key: str, code: str, virtual_key: int, text: str | None = None) -> None:
    key_down = {
        "type": "keyDown",
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": virtual_key,
        "nativeVirtualKeyCode": virtual_key,
    }
    if text is not None:
        key_down["text"] = text
    cdp.call("Input.dispatchKeyEvent", key_down)
    cdp.call("Input.dispatchKeyEvent", {
        "type": "keyUp",
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": virtual_key,
        "nativeVirtualKeyCode": virtual_key,
    })


# --- Page-specific fixtures, all taken directly from the task brief. ---

STAGE_HEADINGS = {
    2: "Stage 2: Case Intake and Initial Assessment",
    3: "Stage 3: Evidence Inject 01",
    4: "Stage 4: Evidence Inject 02",
    5: "Stage 5: Decision Point 01",
    6: "Stage 6: Evidence Inject 03",
    7: "Stage 7: Evidence Inject 04",
    8: "Stage 8: Evidence Inject 05",
    9: "Stage 9: Final Hypothesis Assessment",
    10: "Stage 10: Decision Record and Operational Decisions",
    11: "Stage 11: Red Team Review",
    12: "Stage 12: Final FinCrimeRadar Analysis",
}

# Stages 3 to 8 only. Task 14's curated progressive-disclosure markers; there
# is no equivalent single-phrase marker for Stages 9 to 12, so those stages
# rely on the heading-isolation half of assert_stage_view below instead.
MARKERS = {
    3: "Client Settlement Assistant",
    4: "seventeen months",
    5: "own position on the five hypotheses",
    6: "The messages change the picture",
    7: "seventeen attempted calls",
    8: "three year account history",
}

RED_TEAM_KEYS = [
    "transactionBias", "authenticationBias", "outcomeBias", "vulnerabilityBias",
    "culpabilityBias", "narrativeBias", "suspicionThreshold", "corroboration",
    "counterfactual", "proportionality",
]

# One option per Stage 10 dimension, with its id already sanitised the same
# way the shipped code sanitises it: /[^a-zA-Z0-9]+/g replaced by '-'.
DIMENSION_CHOICES = [
    ("activity", "dr-activity-Confirmed"),
    ("control", "dr-control-Strongly-established"),
    ("knowledge", "dr-knowledge-Established-from-entry"),
    ("exploitation", "dr-exploitation-Materially-supported"),
    ("evidence", "dr-evidence-Strong-across-all-dimensions"),
]

STORAGE_KEY = "fcr_case_money_mule_v1"


def click_id(cdp: CDP, element_id: str) -> None:
    result = cdp.evaluate(
        "(() => { const el = document.getElementById(%s); "
        "if (!el) return 'missing'; el.click(); return 'ok'; })()" % json.dumps(element_id)
    )
    require(result == "ok", f"could not find and click #{element_id}")


def continue_disabled(cdp: CDP) -> bool:
    # NOTE: resolves the FIRST '.mmc-action' in DOM order. While a review
    # panel is open, the "Return to current stage" button (also '.mmc-action')
    # renders before the reviewed stage's own (disabled, hidden) continue
    # button, so this and click_continue below would target Return, not the
    # reviewed stage's continue control. Not a defect today, no test calls
    # either helper during review mode, but do not add one without first
    # scoping the selector to '#mmcStageBody > :not(.mmc-review-banner) .mmc-action'
    # or similar.
    return bool(cdp.evaluate("document.querySelector('#caseFileApp .mmc-action').disabled"))


def click_continue(cdp: CDP) -> None:
    cdp.evaluate("document.querySelector('#caseFileApp .mmc-action').click()")


def touch_all_hypotheses(cdp: CDP) -> None:
    for letter, value in zip("ABCDE", ["Leading", "Plausible", "Unresolved", "Weak", "Leading"]):
        click_id(cdp, f"hyp-{letter}-{value}")


def assert_stage_view(cdp: CDP, stage: int) -> None:
    text = cdp.evaluate("document.body.innerText")
    require(STAGE_HEADINGS[stage] in text, f"Stage {stage} heading not present while viewing stage {stage}")
    # Completed (earlier) stages' headings are now expected to appear, as
    # short "Stage N: Title" entries in the persistent CaseProgress nav
    # (this is the historical-review feature's whole point). Only FUTURE,
    # still-locked stages must never have their heading/title leaked.
    for other, heading in STAGE_HEADINGS.items():
        if other > stage:
            require(heading not in text, f"Stage {other} heading leaked while viewing stage {stage} (future stage not yet unlocked)")
    for marker_stage, marker in MARKERS.items():
        if marker_stage == stage:
            require(marker in text, f"Stage {stage} marker missing while viewing stage {stage}: {marker}")
        else:
            require(marker not in text, f"Stage {marker_stage} marker leaked while viewing stage {stage}: {marker}")


def collect_tab_targets(cdp: CDP, presses: int) -> list[dict[str, Any] | None]:
    targets: list[dict[str, Any] | None] = []
    for _ in range(presses):
        dispatch_key(cdp, "Tab", "Tab", 9)
        info = cdp.evaluate("""(() => {
          const el = document.activeElement;
          if (!el) return null;
          return {tag: el.tagName, type: el.type || null, id: el.id || null, name: el.name || null};
        })()""")
        targets.append(info)
    return targets


def assert_no_keyboard_trap(targets: list[dict[str, Any] | None], label: str) -> None:
    require(len(targets) > 1 and any(t != targets[0] for t in targets), f"{label}: focus never moved, possible keyboard trap")


def first_seen_order(targets: list[dict[str, Any] | None], prefix: str) -> list[str]:
    seen: list[str] = []
    for target in targets:
        if target and target.get("name") and target["name"].startswith(prefix) and target["tag"] == "INPUT":
            if target["name"] not in seen:
                seen.append(target["name"])
    return seen


def pull_errors(cdp: CDP, log: list[str], label: str) -> None:
    errors = cdp.evaluate("window.__consoleErrors || []")
    for error in errors:
        log.append(f"{label}: {error}")


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site_port = server.server_address[1]
    debug_port = 9423
    profile = Path(tempfile.mkdtemp(prefix="fcr-money-mule-chrome-"))
    process = subprocess.Popen([
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-background-networking",
        f"--remote-debugging-port={debug_port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={profile}",
        "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    console_error_log: list[str] = []

    try:
        for _ in range(80):
            try:
                requests.get(f"http://127.0.0.1:{debug_port}/json/version", timeout=0.5).raise_for_status()
                break
            except requests.RequestException:
                time.sleep(0.15)
        else:
            raise RuntimeError("headless Chrome did not start")

        tab = requests.put(f"http://127.0.0.1:{debug_port}/json/new?about:blank", timeout=5).json()
        cdp = CDP(tab["webSocketDebuggerUrl"])
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call("Log.enable")
        # Console errors and uncaught exceptions are collected in-page rather
        # than by draining unsolicited CDP events: the shared CDP.call helper
        # only matches responses by message id and drops anything else, so an
        # in-page collector is the simplest way to get a reliable count across
        # a flow with several full page reloads (each reload gets its own
        # fresh array via addScriptToEvaluateOnNewDocument, and pull_errors
        # below is called immediately before every reload to preserve it).
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__consoleErrors = [];
          (function () {
            var originalError = console.error.bind(console);
            console.error = function () {
              window.__consoleErrors.push(Array.prototype.join.call(arguments, ' '));
              originalError.apply(console, arguments);
            };
          })();
          window.addEventListener('error', function (event) {
            window.__consoleErrors.push('error: ' + event.message);
          });
          window.addEventListener('unhandledrejection', function (event) {
            window.__consoleErrors.push('unhandledrejection: ' + String(event.reason));
          });
        """})

        url = f"http://127.0.0.1:{site_port}/money-mule-or-victim-case-file.html"

        for width in WIDTHS:
            navigate(cdp, url, width)
            overflow_ok = cdp.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
            require(overflow_ok, f"{width}px page overflow")
            print(f"OK: {width}px no horizontal overflow")

        # --- Shared site-footer (site-chrome.js partial). #site-footer's
        # content arrives via an async fetch, so poll briefly rather than
        # assuming it is present the instant readyState is 'complete'. ---
        for _ in range(40):
            if cdp.evaluate("!!document.querySelector('#site-footer .site-footer')"):
                break
            time.sleep(0.1)
        else:
            raise AssertionError("shared #site-footer partial did not render a .site-footer component in time")

        footer_link_hrefs = cdp.evaluate("""Array.from(document.querySelectorAll('#site-footer .footer-link')).map(a => {
          const raw = a.getAttribute('href');
          return raw === '#' ? '#' : new URL(raw, location.href).pathname;
        })""")
        expected_destinations = [
            "/", "/knowledge.html", "/screen.html", "/about.html", "/contact.html",
            "/supporters.html", "/privacy.html", "/terms.html",
            "/editorial-standards.html", "/methodology.html", "#",
        ]
        for destination in expected_destinations:
            require(destination in footer_link_hrefs, f"shared footer is missing expected destination {destination!r}: found {footer_link_hrefs}")
        has_sponsor_link = cdp.evaluate("!!document.querySelector('#site-footer a[href*=\"github.com/sponsors\"]')")
        require(has_sponsor_link, "shared footer is missing the Sponsor destination (github.com/sponsors)")
        print("OK: shared footer renders the structured .site-footer component with every required destination")

        footer_legal_text = cdp.evaluate("document.querySelector('#site-footer .site-footer-legal') ? document.querySelector('#site-footer .site-footer-legal').textContent : ''")
        require("FinCrimeRadar Ltd" in footer_legal_text and "17324449" in footer_legal_text, f"shared footer legal line is missing or incomplete: {footer_legal_text!r}")
        print("OK: shared footer preserves the company legal information")

        # Footer links must be real, focusable anchors reachable by keyboard,
        # not inert text: tab from the last link backwards is unnecessary,
        # simply confirm every rendered .footer-link is an <a> with an href
        # and a non-negative tabindex (i.e. not explicitly removed from the
        # tab order), which is what "keyboard reachable" requires in practice.
        footer_link_focusability = cdp.evaluate("""Array.from(document.querySelectorAll('#site-footer .footer-link')).map(a => ({
          tag: a.tagName, hasHref: a.hasAttribute('href'), tabIndex: a.tabIndex
        }))""")
        require(len(footer_link_focusability) >= len(expected_destinations), f"expected at least {len(expected_destinations)} .footer-link elements, found {len(footer_link_focusability)}")
        for link in footer_link_focusability:
            require(link["tag"] == "A" and link["hasHref"] and link["tabIndex"] >= 0, f"footer link is not a keyboard-reachable anchor: {link}")
        print("OK: footer links are real, keyboard-reachable anchors")

        # --- Main interactive flow, desktop width. ---
        navigate(cdp, url, 1440)
        pull_errors(cdp, console_error_log, "initial load")

        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "Open Case File should be visible on a fresh load")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "case file app should be hidden before opening the case")
        click_id(cdp, "openCaseFile")
        assert_stage_view(cdp, 2)
        print("OK: Stage 1 to Stage 2 open")

        # goToStage bypass attempt, while state is still at an early stage.
        before_bypass = cdp.evaluate("CaseFileShell.getState().currentStage")
        cdp.evaluate("CaseFileShell.goToStage(12)")
        after_bypass = cdp.evaluate("CaseFileShell.getState().currentStage")
        require(after_bypass == before_bypass, f"goToStage(12) bypassed highestUnlockedStage: before={before_bypass}, after={after_bypass}")
        require(STAGE_HEADINGS[12] not in cdp.evaluate("document.body.innerText"), "Stage 12 rendered despite being locked")
        print("OK: goToStage(12) bypass attempt refused")

        # Hypothesis Board markup: each of the five fieldsets must carry only
        # the hypothesis name in its <legend>, with the full description as
        # separate paragraph content inside the same fieldset (not appended
        # to the legend, which is what broke the fieldset border rendering).
        hypothesis_names = cdp.evaluate("MMC_DATA ? Object.fromEntries('ABCDE'.split('').map(id => [id, MMC_DATA.hypotheses[id].name])) : {}")
        hypothesis_descriptions = cdp.evaluate("MMC_DATA ? Object.fromEntries('ABCDE'.split('').map(id => [id, MMC_DATA.hypotheses[id].description])) : {}")
        fieldsets = cdp.evaluate("""Array.from(document.querySelectorAll('.mmc-hypothesis-board .mmc-hypothesis')).map(fs => {
          const legend = fs.querySelector('legend');
          const description = fs.querySelector('.mmc-hypothesis-description');
          return {
            legendText: legend ? legend.textContent.trim() : null,
            descriptionText: description ? description.textContent.trim() : null,
            descriptionInFieldset: !!(description && fs.contains(description)),
            legendIsFirstChild: fs.firstElementChild === legend,
          };
        })""")
        require(len(fieldsets) == 5, f"expected 5 hypothesis fieldsets on the Stage 2 board, found {len(fieldsets)}")
        for id_, name in hypothesis_names.items():
            match = next((fs for fs in fieldsets if fs["legendText"] == name), None)
            require(match is not None, f"no fieldset legend equals hypothesis {id_}'s bare name {name!r} (legend must not also carry the description)")
            require(match["descriptionText"] == hypothesis_descriptions[id_], f"hypothesis {id_}'s description paragraph text does not match MMC_DATA: {match['descriptionText']!r}")
            require(match["descriptionInFieldset"], f"hypothesis {id_}'s description paragraph is not inside its fieldset")
            require(match["legendIsFirstChild"], f"hypothesis {id_}'s legend is not the fieldset's first child element")
        print("OK: Hypothesis Board legends contain only the hypothesis name, descriptions are separate paragraphs inside the same fieldset")

        # Radio group semantics: the four hypothesis-state controls under each
        # fieldset are real radios sharing one name per hypothesis, each with
        # a label bound by a matching for/id pair (an accessible name), and
        # every option is reachable, not merely present in the DOM.
        radio_groups = cdp.evaluate("""Array.from(document.querySelectorAll('.mmc-hypothesis-board .mmc-hypothesis')).map(fs => {
          const inputs = Array.from(fs.querySelectorAll('input[type="radio"]'));
          const names = new Set(inputs.map(i => i.name));
          const labelledOk = inputs.every(i => {
            const label = fs.querySelector('label[for="' + i.id + '"]');
            return !!label && label.textContent.trim().length > 0;
          });
          return {count: inputs.length, distinctNames: names.size, labelledOk};
        })""")
        require(len(radio_groups) == 5, "expected 5 radio groups, one per hypothesis fieldset")
        for group in radio_groups:
            require(group["count"] == 4, f"each hypothesis fieldset should have 4 radio controls (Leading/Plausible/Unresolved/Weak), got {group['count']}")
            require(group["distinctNames"] == 1, f"a hypothesis fieldset's 4 radios must share a single name attribute, found {group['distinctNames']} distinct names")
            require(group["labelledOk"], "every radio in a hypothesis fieldset must have a non-empty label bound via for/id")
        print("OK: Hypothesis Board radio groups retain correct name grouping and accessible labels")

        # Desktop: the five hypothesis cards must not visually overlap.
        card_rects = cdp.evaluate("""Array.from(document.querySelectorAll('.mmc-hypothesis-board .mmc-hypothesis')).map(el => {
          const r = el.getBoundingClientRect();
          return {left: r.left, right: r.right, top: r.top, bottom: r.bottom};
        })""")
        for i in range(len(card_rects)):
            for j in range(i + 1, len(card_rects)):
                a, b = card_rects[i], card_rects[j]
                overlap = a["left"] < b["right"] and b["left"] < a["right"] and a["top"] < b["bottom"] and b["top"] < a["bottom"]
                require(not overlap, f"Hypothesis Board cards {i} and {j} visually overlap at desktop width: {a} vs {b}")
        print("OK: Hypothesis Board cards do not overlap at desktop width")

        # Mobile: the board collapses to one column and the page still has no
        # horizontal overflow with all five cards rendered.
        cdp.call("Emulation.setDeviceMetricsOverride", {"width": 375, "height": 900, "deviceScaleFactor": 1, "mobile": True})
        mobile_overflow_ok = cdp.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
        require(mobile_overflow_ok, "375px page overflow with the Hypothesis Board populated")
        mobile_columns = cdp.evaluate("new Set(Array.from(document.querySelectorAll('.mmc-hypothesis-board .mmc-hypothesis')).map(el => Math.round(el.getBoundingClientRect().left))).size")
        require(mobile_columns == 1, f"Hypothesis Board should collapse to a single column at 375px, found {mobile_columns} distinct left offsets")
        cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        print("OK: Hypothesis Board collapses to one column with no overflow at mobile width")

        # Keyboard tab order across the Stage 2 hypothesis board, before it is touched.
        stage2_targets = collect_tab_targets(cdp, 40)
        assert_no_keyboard_trap(stage2_targets, "Stage 2 hypothesis board")
        stage2_order = first_seen_order(stage2_targets, "hyp-")
        require(set(stage2_order) == {"hyp-A", "hyp-B", "hyp-C", "hyp-D", "hyp-E"}, f"Stage 2 tab order did not reach all five hypothesis groups: {stage2_order}")
        require(stage2_order == ["hyp-A", "hyp-B", "hyp-C", "hyp-D", "hyp-E"], f"Stage 2 hypothesis tab order out of sequence: {stage2_order}")
        print("OK: Stage 2 hypothesis board keyboard tab order")

        require(continue_disabled(cdp), "Stage 2 continue should start disabled before any hypothesis is touched")
        click_continue(cdp)
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 2, "clicking a disabled Stage 2 continue button must not advance the stage")
        touch_all_hypotheses(cdp)
        require(not continue_disabled(cdp), "Stage 2 continue should enable once all five hypotheses are touched")
        click_continue(cdp)
        assert_stage_view(cdp, 3)
        print("OK: Stage 2 gate genuinely exercised via real click() calls")

        click_continue(cdp)
        assert_stage_view(cdp, 4)

        # Stage 4 hypothesis snapshot. touch_all_hypotheses alone writes the
        # identical fixed value set every time it is called anywhere in this
        # flow, so a bare "snapshot exists" check would pass even if the
        # snapshot silently held live (not frozen) data. Setting hypothesis A
        # to a distinct marker value here, and to DIFFERENT distinct values
        # at Stage 7 and Stage 9 below, makes the later isolation checks
        # genuinely meaningful: if a snapshot were live rather than frozen,
        # these markers would collide.
        touch_all_hypotheses(cdp)
        click_id(cdp, "hyp-A-Plausible")
        require(not continue_disabled(cdp), "Stage 4 continue should enable once all five hypotheses are touched")
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage4") is None, "Stage 4 hypothesis snapshot should not exist before Stage 4 is confirmed")
        click_continue(cdp)
        assert_stage_view(cdp, 5)
        stage4_snapshot = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage4")
        require(stage4_snapshot is not None and stage4_snapshot["A"] == "Plausible", f"Stage 4 hypothesis snapshot should be captured on confirm with A='Plausible', got {stage4_snapshot}")
        initial_snapshot_after_stage4 = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.initial")
        require(initial_snapshot_after_stage4["A"] == "Leading", f"confirming Stage 4 must not alter the Stage 2 initial snapshot, expected A='Leading', got {initial_snapshot_after_stage4}")
        print("OK: Stage 4 hypothesis snapshot captured on confirm, Stage 2 initial snapshot unaffected")

        click_continue(cdp)
        assert_stage_view(cdp, 6)
        print("OK: Stage 3 to Stage 6 progression, ungated stages have no premature next-stage leakage")

        # Reload immediately on reaching Stage 6, before touching anything, to
        # confirm currentStage survives a real page reload.
        pull_errors(cdp, console_error_log, "before Stage 6 reload")
        reload_page(cdp)
        restored_stage = cdp.evaluate("CaseFileShell.getState().currentStage")
        require(restored_stage == 6, f"reload did not restore currentStage 6, got {restored_stage}")
        assert_stage_view(cdp, 6)
        print("OK: reload at Stage 6 restores currentStage from localStorage")

        # Keyboard tab order across the Stage 6 timeline controls.
        stage6_targets = collect_tab_targets(cdp, 60)
        assert_no_keyboard_trap(stage6_targets, "Stage 6 timeline controls")
        stage6_order = first_seen_order(stage6_targets, "tl-")
        for expected_name in ("tl-entryState", "tl-prePaymentThreeState", "tl-changePoint"):
            require(expected_name in stage6_order, f"Stage 6 tab order never reached {expected_name}: {stage6_order}")
        require(
            stage6_order.index("tl-entryState") < stage6_order.index("tl-prePaymentThreeState") < stage6_order.index("tl-changePoint"),
            f"Stage 6 timeline tab order out of sequence: {stage6_order}",
        )
        print("OK: Stage 6 timeline controls keyboard tab order")

        # Revisiting Stage 6 (highestUnlockedStage is not yet past it) re-imposes
        # the touched gate, so every control must be clicked again even though
        # its prior value is still checked.
        click_id(cdp, "tl-entryState-Unaware")
        click_id(cdp, "tl-prePaymentThreeState-ConcernEmerging")
        click_id(cdp, "tl-changePoint-paymentTwo")
        require(not continue_disabled(cdp), "Stage 6 continue should enable once all three timeline controls are touched again after reload")
        click_continue(cdp)
        assert_stage_view(cdp, 7)
        print("OK: Stage 6 timeline gate and reload-then-retouch behaviour")

        # Stage 7: control/voluntariness genuine independence.
        require(continue_disabled(cdp), "Stage 7 continue should start disabled")
        click_id(cdp, "cq-controlDecision-Yes")
        stage7_state = cdp.evaluate("CaseFileShell.getState()")
        require(stage7_state["controlDecision"] == "Yes" and stage7_state["voluntarinessDecision"] is None,
                "setting controlDecision must not set or affect voluntarinessDecision")
        require(continue_disabled(cdp), "Stage 7 continue should remain disabled with only controlDecision set")
        click_id(cdp, "cq-voluntarinessDecision-No")
        stage7_state = cdp.evaluate("CaseFileShell.getState()")
        require(stage7_state["controlDecision"] == "Yes" and stage7_state["voluntarinessDecision"] == "No",
                "control and voluntariness decisions must be independently persisted")
        require(continue_disabled(cdp), "Stage 7 continue should remain disabled until the hypotheses are also touched")
        touch_all_hypotheses(cdp)
        click_id(cdp, "hyp-A-Weak")  # distinct from Stage 4's marker ('Plausible')
        require(not continue_disabled(cdp), "Stage 7 continue should enable once every gated field is touched")
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage7") is None, "Stage 7 hypothesis snapshot should not exist before Stage 7 is confirmed")
        click_continue(cdp)
        assert_stage_view(cdp, 8)
        print("OK: Stage 7 control/voluntariness genuine independence and combined gate")

        stage7_snapshot = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage7")
        require(stage7_snapshot is not None and stage7_snapshot["A"] == "Weak", f"Stage 7 hypothesis snapshot should be captured on confirm with A='Weak', got {stage7_snapshot}")
        stage4_snapshot_after_stage7 = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage4")
        require(stage4_snapshot_after_stage7["A"] == "Plausible", f"confirming Stage 7 must not alter the Stage 4 snapshot, expected A='Plausible', got {stage4_snapshot_after_stage7}")
        print("OK: Stage 7 hypothesis snapshot captured on confirm, Stage 4 snapshot unaffected")

        # --- CaseProgress historical review. currentStage is 8, so Stages
        # 2-7 are completed/reviewable, Stage 8 is current, Stages 9-12 are
        # locked. Exercises every item the remediation brief lists. ---
        pre_review_state = cdp.evaluate("CaseFileShell.getState()")
        pre_review_highest = pre_review_state["highestUnlockedStage"]
        pre_review_initial_snapshot = pre_review_state["hypothesisSnapshots"]["initial"]

        completed_buttons = cdp.evaluate("document.querySelectorAll('.mmc-progress-step-btn').length")
        require(completed_buttons == 6, f"expected 6 completed/reviewable CaseProgress entries (Stages 2-7) at Stage 8, found {completed_buttons}")

        # Compact rail: every step, completed or locked, shows only its bare
        # number as visible text, never the full stage title.
        step_texts = cdp.evaluate("Array.from(document.querySelectorAll('.mmc-progress-step-btn, .mmc-progress-step-current, .mmc-progress-step-locked')).map(el => el.textContent.trim())")
        require(all(text.isdigit() for text in step_texts), f"CaseProgress rail items must show only a bare stage number, got {step_texts}")
        print("OK: CaseProgress rail items show stage numbers only, never full titles")

        # The live current stage (8) gets its own concise header above the
        # rail, and its own rail item exposes aria-current="step".
        current_index_text = cdp.evaluate("document.querySelector('.mmc-progress-current-index') ? document.querySelector('.mmc-progress-current-index').textContent : ''")
        require("Stage 8 of 12" in current_index_text, f"CaseProgress current-stage header should read 'Stage 8 of 12', got {current_index_text!r}")
        current_title_text = cdp.evaluate("document.querySelector('.mmc-progress-current-title') ? document.querySelector('.mmc-progress-current-title').textContent : ''")
        require(STAGE_HEADINGS[8].split(": ", 1)[1] in current_title_text, f"CaseProgress current-stage header is missing Stage 8's own title, got {current_title_text!r}")
        current_step_aria = cdp.evaluate("document.querySelector('.mmc-progress-step-current[data-stage=\"8\"]') ? document.querySelector('.mmc-progress-step-current[data-stage=\"8\"]').getAttribute('aria-current') : null")
        require(current_step_aria == "step", f"Stage 8's rail item should expose aria-current=\"step\", got {current_step_aria!r}")
        print("OK: CaseProgress current-stage header and aria-current=\"step\" are both present")

        # Future (locked) stages: no button exists at all, so they cannot be
        # opened through the UI; neither their visible text nor their
        # accessible label discloses the real title.
        for locked_stage in (9, 10, 11, 12):
            has_button = cdp.evaluate(f"!!document.querySelector('.mmc-progress-step-btn[data-stage=\"{locked_stage}\"]')")
            require(not has_button, f"Stage {locked_stage} is locked but has a clickable CaseProgress button")
            locked_el = f"document.querySelector('.mmc-progress-step-locked[data-stage=\"{locked_stage}\"]')"
            locked_text = cdp.evaluate(f"{locked_el}.textContent")
            locked_label = cdp.evaluate(f"{locked_el}.getAttribute('aria-label')")
            spoiler = STAGE_HEADINGS[locked_stage].split(": ", 1)[1]
            require(spoiler not in locked_text, f"Stage {locked_stage}'s locked CaseProgress entry leaks its real title in visible text: {locked_text!r}")
            require(spoiler not in (locked_label or ""), f"Stage {locked_stage}'s locked CaseProgress entry leaks its real title in aria-label: {locked_label!r}")
            require(cdp.evaluate(f"{locked_el}.tagName") != "BUTTON", f"Stage {locked_stage}'s locked CaseProgress entry must not be a button")
        print("OK: future stages have no CaseProgress control and no spoiler title in text or aria-label")

        # No decorative text glyphs (▢ ● ◆ ◐ etc.) anywhere in the rail.
        rail_text = cdp.evaluate("document.querySelector('.mmc-progress-nav').textContent")
        for glyph in ("▢", "●", "◆", "◐", "◇", "○"):
            require(glyph not in rail_text, f"CaseProgress rail must not use decorative glyph {glyph!r}")
        print("OK: CaseProgress rail contains no decorative text glyphs")

        # Desktop: rail items must not visually overlap.
        step_rects = cdp.evaluate("""Array.from(document.querySelectorAll('.mmc-progress-step')).map(el => {
          const r = el.getBoundingClientRect();
          return {left: r.left, right: r.right, top: r.top, bottom: r.bottom};
        })""")
        for i in range(len(step_rects)):
            for j in range(i + 1, len(step_rects)):
                a, b = step_rects[i], step_rects[j]
                overlap = a["left"] < b["right"] and b["left"] < a["right"] and a["top"] < b["bottom"] and b["top"] < a["bottom"]
                require(not overlap, f"CaseProgress rail items {i} and {j} visually overlap at desktop width: {a} vs {b}")
        print("OK: CaseProgress rail items do not overlap at desktop width")

        # The main overflow sweep at the top of this run happens before the
        # case is opened, so it never exercises CaseProgress actually
        # populated with several completed entries. Check narrow-width
        # overflow again now, in place (no navigate/reload, so Stage 8
        # progress survives), with 6 real completed entries rendered.
        cdp.call("Emulation.setDeviceMetricsOverride", {"width": 320, "height": 900, "deviceScaleFactor": 1, "mobile": True})
        progress_overflow_ok = cdp.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
        require(progress_overflow_ok, "320px overflow once CaseProgress is populated with completed entries")
        cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        print("OK: 320px no horizontal overflow with CaseProgress populated")

        # Open a completed stage (4) for review through the real UI control.
        click_id_selector = "document.querySelector('.mmc-progress-step-btn[data-stage=\"4\"]').click()"
        cdp.evaluate(click_id_selector)
        require(cdp.evaluate("CaseFileShell.getReviewStage()") == 4, "clicking the Stage 4 CaseProgress entry should enter review mode for Stage 4")
        require(STAGE_HEADINGS[4] in cdp.evaluate("document.body.innerText"), "Stage 4 content should render while reviewing Stage 4")
        require("Read-only review: Stage 4 of 12" in cdp.evaluate("document.body.innerText"), "review banner should name the stage being reviewed")
        print("OK: a completed earlier stage can be opened for review through the user interface")

        # Stage 4 historical review must render the frozen Stage 4 snapshot
        # (hyp-A-Plausible), never the live hypothesisState (which is now
        # 'Weak' for A, since Stage 7 has since been confirmed with a
        # different marker value). This is the real fidelity check the
        # earlier "recently recorded, may have changed" disclosure used to
        # stand in for: the practitioner's hypothesis position at the
        # historical point in the investigation, not the current one.
        stage4_review_a_checked = cdp.evaluate("document.querySelector('.mmc-review-content #hyp-A-Plausible') ? document.querySelector('.mmc-review-content #hyp-A-Plausible').checked : null")
        require(stage4_review_a_checked is True, f"Stage 4 review should show the frozen Stage 4 snapshot (hyp-A-Plausible checked), got {stage4_review_a_checked}")
        stage4_review_a_live_value_checked = cdp.evaluate("document.querySelector('.mmc-review-content #hyp-A-Weak') ? document.querySelector('.mmc-review-content #hyp-A-Weak').checked : null")
        require(stage4_review_a_live_value_checked is False, "Stage 4 review must not show the live (Stage 7's, later) hypothesis value")
        print("OK: Stage 4 historical review renders the Stage 4 snapshot, not the live hypothesis state")

        # Stage 5 introduces no new hypothesis assessment of its own, so its
        # historical review must reuse the Stage 4 snapshot: the diff view
        # compares initial ('Leading' for A) against stage4 ('Plausible'),
        # never against the live value ('Weak').
        cdp.evaluate("document.querySelector('.mmc-progress-step-btn[data-stage=\"5\"]').click()")
        stage5_review_diff_text = cdp.evaluate("document.querySelector('.mmc-review-content .mmc-hypothesis-diff') ? document.querySelector('.mmc-review-content .mmc-hypothesis-diff').textContent : ''")
        require("moved from Leading to Plausible" in stage5_review_diff_text, f"Stage 5 review should show the Stage 4 snapshot in its diff (Leading to Plausible), got: {stage5_review_diff_text!r}")
        require("moved from Leading to Weak" not in stage5_review_diff_text, "Stage 5 review must not show the live (later) hypothesis value in its diff")
        print("OK: Stage 5 historical review uses the Stage 4 snapshot, not the live hypothesis state")

        mid_review_state = cdp.evaluate("CaseFileShell.getState()")
        require(mid_review_state["currentStage"] == 8, f"reviewing Stage 4 must not alter the current investigation stage, still expected 8, got {mid_review_state['currentStage']}")
        require(mid_review_state["highestUnlockedStage"] == pre_review_highest, "reviewing an earlier stage must not change highestUnlockedStage")
        require(mid_review_state["hypothesisSnapshots"]["initial"] == pre_review_initial_snapshot, "reviewing an earlier stage must not mutate hypothesisSnapshots")
        print("OK: historical review does not unlock future stages, alter the current stage, or mutate hypothesis snapshots")

        # Every input inside the reviewed Stage 4 content must be disabled,
        # so nothing can be mutated from the review view.
        enabled_inputs_in_review = cdp.evaluate("document.querySelectorAll('.mmc-review-content input:not([disabled]), .mmc-review-content button:not([disabled])').length")
        require(enabled_inputs_in_review == 0, f"Stage 4 review content has {enabled_inputs_in_review} non-disabled interactive element(s)")
        # Clicking a disabled radio must not change the underlying state
        # (the disabled attribute already prevents the click event from
        # firing at all, this proves it end to end rather than assuming it).
        cdp.evaluate("(() => { const el = document.querySelector('.mmc-review-content input[id^=\"hyp-\"]'); if (el) el.click(); })()")
        require(cdp.evaluate("CaseFileShell.getState().hypothesisState.A") == mid_review_state["hypothesisState"]["A"], "clicking a disabled control inside a review view must not mutate state")
        print("OK: reviewed stage content is genuinely read-only, disabled controls cannot mutate state")

        # Reviewing Stage 6 must show only Stage 6's own 5-point timeline
        # reveal set, never Stage 7's later 9-point expansion: no access to
        # evidence not yet unlocked at that historical point.
        cdp.evaluate("document.querySelector('.mmc-progress-step-btn[data-stage=\"6\"]').click()")
        stage6_review_text = cdp.evaluate("document.body.innerText")
        require("Attempted Exit" not in stage6_review_text, "reviewing Stage 6 must not expose Stage 7's later timeline reveal (Attempted Exit)")
        print("OK: reviewing an earlier stage does not expose evidence unlocked only at a later stage")

        # Stage 7 historical review must render its own frozen snapshot
        # (hyp-A-Weak), independent of both Stage 4's snapshot and whatever
        # hypothesisState currently holds.
        cdp.evaluate("document.querySelector('.mmc-progress-step-btn[data-stage=\"7\"]').click()")
        stage7_review_a_checked = cdp.evaluate("document.querySelector('.mmc-review-content #hyp-A-Weak') ? document.querySelector('.mmc-review-content #hyp-A-Weak').checked : null")
        require(stage7_review_a_checked is True, f"Stage 7 review should show the frozen Stage 7 snapshot (hyp-A-Weak checked), got {stage7_review_a_checked}")
        print("OK: Stage 7 historical review renders the Stage 7 snapshot")

        # Non-colour-only, keyboard-accessible: the Return control is a real
        # button, reachable and activatable by keyboard.
        return_focus_ok = cdp.evaluate("document.activeElement && document.activeElement.id === 'mmcReviewHeading'")
        require(return_focus_ok, "entering review mode should move focus to the review panel's own heading, not leave it stranded")
        review_tab_targets = collect_tab_targets(cdp, 5)
        assert_no_keyboard_trap(review_tab_targets, "Stage 7 review panel controls")
        return_button_reachable = cdp.evaluate("document.querySelector('.mmc-review-return') === document.activeElement || Array.from(document.querySelectorAll('button,input,a')).indexOf(document.querySelector('.mmc-review-return')) >= 0")
        require(return_button_reachable, "the Return to current stage control must be a real, keyboard-reachable element")
        print("OK: review controls are keyboard accessible and focus moves predictably on entry")

        # Return to current stage: state is restored correctly, and focus
        # moves predictably again rather than resetting to <body>.
        cdp.evaluate("document.querySelector('.mmc-review-return').click()")
        require(cdp.evaluate("CaseFileShell.getReviewStage()") is None, "Return to current stage should clear review mode")
        post_return_state = cdp.evaluate("CaseFileShell.getState()")
        require(post_return_state["currentStage"] == 8, "returning from review must restore the correct active stage")
        require(post_return_state["highestUnlockedStage"] == pre_review_highest, "returning from review must leave highestUnlockedStage unchanged")
        assert_stage_view(cdp, 8)
        focus_after_return_ok = cdp.evaluate("document.activeElement && document.activeElement.tagName === 'H2'")
        require(focus_after_return_ok, "returning to the current stage should move focus to its own heading")
        print("OK: returning to current stage restores the correct active stage, state, and predictable focus")

        # Reload persistence: review mode is deliberately not persisted, so a
        # reload while reviewing must resume at the true current stage, not
        # the stage that was being reviewed.
        cdp.evaluate("document.querySelector('.mmc-progress-step-btn[data-stage=\"5\"]').click()")
        require(cdp.evaluate("CaseFileShell.getReviewStage()") == 5, "review mode should be active before the reload check")
        pull_errors(cdp, console_error_log, "before review-mode reload")
        reload_page(cdp)
        require(cdp.evaluate("CaseFileShell.getReviewStage()") is None, "review mode must not survive a reload")
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 8, "reload after using historical review must restore the true current stage, not the reviewed one")
        assert_stage_view(cdp, 8)
        reloaded_snapshots = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots")
        require(reloaded_snapshots["initial"]["A"] == "Leading", f"reload must preserve the Stage 2 initial snapshot, got {reloaded_snapshots['initial']}")
        require(reloaded_snapshots["stage4"]["A"] == "Plausible", f"reload must preserve the Stage 4 snapshot, got {reloaded_snapshots['stage4']}")
        require(reloaded_snapshots["stage7"]["A"] == "Weak", f"reload must preserve the Stage 7 snapshot, got {reloaded_snapshots['stage7']}")
        require(reloaded_snapshots["final"] is None, "the Stage 9 final snapshot should not exist yet at this point in the flow")
        print("OK: reload persistence remains correct after using historical review, all required snapshots preserved")

        click_continue(cdp)

        # Stage 9: classify phase. Full isolation check (own heading present,
        # every other stage's heading and marker absent), not just a presence
        # check on its own heading.
        assert_stage_view(cdp, 9)
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.final") is None, "Stage 9 should start in classify phase with no final snapshot")
        touch_all_hypotheses(cdp)
        click_id(cdp, "hyp-A-Unresolved")  # distinct final marker, different from Stage 4's/Stage 7's
        require(not continue_disabled(cdp), "Stage 9 confirm button should enable once all five hypotheses are re-touched")
        click_continue(cdp)
        final_snapshot = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.final")
        require(final_snapshot is not None and final_snapshot["A"] == "Unresolved", f"confirming Stage 9 should record the final hypothesis snapshot with A='Unresolved', got {final_snapshot}")
        require("What changed?" in cdp.evaluate("document.body.innerText"), "Stage 9 review phase diff view is missing")
        stage7_snapshot_after_stage9 = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.stage7")
        require(stage7_snapshot_after_stage9["A"] == "Weak", f"confirming Stage 9 must not alter the Stage 7 snapshot, expected A='Weak', got {stage7_snapshot_after_stage9}")
        print("OK: Stage 9 final hypothesis snapshot captured on confirm, Stage 7 snapshot unaffected")
        click_continue(cdp)
        assert_stage_view(cdp, 10)
        print("OK: Stage 9 two-phase classify-then-review flow")

        # Stage 7 historical review, re-checked now from Stage 10 (one stage
        # further on than the earlier check from Stage 8), to prove the
        # snapshot keeps rendering correctly as the practitioner continues
        # to progress, not just immediately after it was captured.
        completed_buttons_at_10 = cdp.evaluate("document.querySelectorAll('.mmc-progress-step-btn').length")
        require(completed_buttons_at_10 == 8, f"expected 8 completed/reviewable CaseProgress entries (Stages 2-9) at Stage 10, found {completed_buttons_at_10}")
        cdp.evaluate("document.querySelector('.mmc-progress-step-btn[data-stage=\"7\"]').click()")
        stage7_review_a_checked_later = cdp.evaluate("document.querySelector('.mmc-review-content #hyp-A-Weak') ? document.querySelector('.mmc-review-content #hyp-A-Weak').checked : null")
        require(stage7_review_a_checked_later is True, f"Stage 7 review must still show its own frozen snapshot after Stage 9 has since changed the live value, got {stage7_review_a_checked_later}")
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 10, "reviewing Stage 7 from Stage 10 must not alter the current investigation stage")
        cdp.evaluate("document.querySelector('.mmc-review-return').click()")
        require(cdp.evaluate("CaseFileShell.getReviewStage()") is None, "returning from the second Stage 7 review should clear review mode")
        assert_stage_view(cdp, 10)
        print("OK: Stage 7 historical review remains correct after further progression to Stage 10")

        # Stage 10: per-dimension Decision Record reveal isolation. A count of
        # '.mmc-suggested-board-label' elements alone would not catch a
        # content-swap regression (e.g. dimension B's fieldset rendering
        # dimension A's analysis text), since all five dimensions share the
        # identical label text and the count stays correct regardless of
        # which dimension's text is actually shown. So fetch the five real
        # fincrimeradarAnalysis strings straight from MMC_DATA (same order as
        # DIMENSION_CHOICES: activity, control, knowledge, exploitation,
        # evidence) and assert on their actual presence/absence in the
        # Decision Record section, not just a count.
        analysis_texts = cdp.evaluate("MMC_DATA.stages[10].dimensions.map(d => d.fincrimeradarAnalysis)")
        require(len(analysis_texts) == 5 and len(set(analysis_texts)) == 5,
                "Stage 10 must have five distinct fincrimeradarAnalysis strings for a content isolation check to be meaningful")

        initial_analysis_count = cdp.evaluate("document.querySelectorAll('.mmc-suggested-board-label').length")
        require(initial_analysis_count == 0, f"Stage 10 should show no FinCrimeRadar analysis before any dimension is set, found {initial_analysis_count}")
        for index, (dim_id, element_id) in enumerate(DIMENSION_CHOICES, start=1):
            click_id(cdp, element_id)
            count = cdp.evaluate("document.querySelectorAll('.mmc-suggested-board-label').length")
            require(count == index, f"Stage 10 analysis reveal count mismatch after setting {dim_id}: expected {index}, got {count}")
            record_text = cdp.evaluate("document.querySelector('.mmc-decision-record').innerText")
            for position, text in enumerate(analysis_texts):
                if position < index:
                    require(text in record_text, f"Stage 10 dimension at position {position} analysis text missing after setting {dim_id} (step {index}): {text!r}")
                else:
                    require(text not in record_text, f"Stage 10 setting {dim_id} (step {index}) leaked a not-yet-selected dimension's analysis text: {text!r}")
        require(not continue_disabled(cdp), "Stage 10 continue should enable once all five dimensions are set")
        click_continue(cdp)
        assert_stage_view(cdp, 11)
        print("OK: Stage 10 per-dimension Decision Record reveal isolation")

        # Stage 11: red-team-vs-decision-change gate separation.
        for key in RED_TEAM_KEYS[:-1]:
            click_id(cdp, f"rt-{key}")
        for item_number in range(1, 10):
            click_id(cdp, f"dc-item{item_number}")
        click_id(cdp, "rs-Somewhat")
        require(continue_disabled(cdp), "Stage 11 continue must stay disabled with 9 of 10 red-team boxes checked, even with all nine decision-change boxes checked")
        click_continue(cdp)
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 11, "clicking a disabled Stage 11 continue button must not advance the stage")
        click_id(cdp, f"rt-{RED_TEAM_KEYS[-1]}")
        require(not continue_disabled(cdp), "Stage 11 continue should enable once all ten red-team boxes are checked")
        click_continue(cdp)
        assert_stage_view(cdp, 12)
        print("OK: Stage 11 red-team-vs-decision-change gate separation")

        # Stage 12: terminal state.
        require(cdp.evaluate("CaseFileShell.getState().caseCompleted") is True, "caseCompleted should be true once Stage 12 renders")
        require(cdp.evaluate("document.querySelectorAll('.mmc-radar .mmc-evidence-card').length") == 5, "Radar View should show all five case dimensions")
        require(cdp.evaluate("document.querySelector('#caseFileApp .mmc-action')") is None, "Stage 12 is terminal and must have no further Continue button")
        print("OK: Stage 12 Radar View and terminal state")

        pull_errors(cdp, console_error_log, "end of main flow")
        require(not console_error_log, f"console errors during the main 12-stage flow: {console_error_log}")
        print("OK: zero console errors across the entire 12-stage flow")

        # --- Corrupted localStorage recovery. ---
        pull_errors(cdp, console_error_log, "before corruption reload")
        cdp.evaluate(f"localStorage.setItem({json.dumps(STORAGE_KEY)}, 'not json')")
        reload_page(cdp)
        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "corrupted state should fall back to Stage 1 with Open Case File visible")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "corrupted state should fall back to Stage 1 with the case file app hidden")
        fallback_text = cdp.evaluate("document.body.innerText")
        require(all(heading not in fallback_text for heading in STAGE_HEADINGS.values()), "corrupted state should not render any interactive stage heading")
        require(cdp.evaluate("(window.__consoleErrors || []).length") == 0, "corrupted localStorage recovery produced console errors")
        print("OK: corrupted localStorage falls back to Stage 1 with zero console errors")

        # --- Stale caseVersion recovery, on an otherwise validly shaped state. ---
        pull_errors(cdp, console_error_log, "before stale-version reload")
        cdp.evaluate("""(() => {
          const state = CaseFileShell.getState();
          state.caseVersion = 0;
          localStorage.setItem(%s, JSON.stringify(state));
        })()""" % json.dumps(STORAGE_KEY))
        reload_page(cdp)
        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "stale caseVersion should fall back to Stage 1 with Open Case File visible")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "stale caseVersion should fall back to Stage 1 with the case file app hidden")
        require(cdp.evaluate("CaseFileShell.getState().caseVersion") == 2, "stale caseVersion should fall back to a fresh default state")
        require(cdp.evaluate("(window.__consoleErrors || []).length") == 0, "stale caseVersion recovery produced console errors")
        print("OK: stale caseVersion falls back to a fresh default state with zero console errors")

        # --- Pre-remediation schema (caseVersion 1, hypothesisSnapshots with
        # only initial/final, no stage4/stage7) must also fail safely, not
        # merely a caseVersion number mismatch on an otherwise-current shape:
        # this is the actual real-world incompatible-local-state scenario
        # the historical snapshot remediation itself introduced. ---
        pull_errors(cdp, console_error_log, "before old-schema reload")
        cdp.evaluate("""(() => {
          const oldShapeState = {
            caseVersion: 1,
            currentStage: 6,
            highestUnlockedStage: 6,
            hypothesisState: { A: 'Leading', B: 'Plausible', C: 'Unresolved', D: 'Weak', E: 'Leading' },
            hypothesisSnapshots: { initial: { A: 'Leading', B: 'Plausible', C: 'Unresolved', D: 'Weak', E: 'Leading' }, final: null },
            knowledgeTimeline: { entryState: null, prePaymentThreeState: null, changePoint: null },
            controlDecision: null,
            voluntarinessDecision: null,
            decisionRecord: { activity: null, control: null, knowledge: null, exploitation: null, evidence: null },
            redTeamCompleted: { transactionBias: false, authenticationBias: false, outcomeBias: false, vulnerabilityBias: false, culpabilityBias: false, narrativeBias: false, suspicionThreshold: false, corroboration: false, counterfactual: false, proportionality: false },
            decisionChangeSelections: { item1: false, item2: false, item3: false, item4: false, item5: false, item6: false, item7: false, item8: false, item9: false },
            reasoningShift: null,
            caseCompleted: false
          };
          localStorage.setItem(%s, JSON.stringify(oldShapeState));
        })()""" % json.dumps(STORAGE_KEY))
        reload_page(cdp)
        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "old-schema state should fall back to Stage 1 with Open Case File visible")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "old-schema state should fall back to Stage 1 with the case file app hidden")
        old_schema_fallback_state = cdp.evaluate("CaseFileShell.getState()")
        require(old_schema_fallback_state["caseVersion"] == 2, "old-schema state should fall back to a fresh default state, not be read as-is")
        require(old_schema_fallback_state["hypothesisSnapshots"] == {"initial": None, "stage4": None, "stage7": None, "final": None}, f"old-schema fallback should have the current, complete hypothesisSnapshots shape, got {old_schema_fallback_state['hypothesisSnapshots']}")
        require(cdp.evaluate("(window.__consoleErrors || []).length") == 0, "old-schema recovery produced console errors")
        print("OK: pre-remediation schema (caseVersion 1, no stage4/stage7 snapshots) fails safely to a fresh state")

        # --- Reset Case: confirm row, Cancel leaves state untouched, Yes clears it. ---
        click_id(cdp, "openCaseFile")
        assert_stage_view(cdp, 2)

        # Advance once and confirm Stage 2, so hypothesisSnapshots.initial is
        # genuinely populated before reset: otherwise the "reset clears
        # snapshots" check below would trivially pass against an
        # already-null value and prove nothing.
        touch_all_hypotheses(cdp)
        click_continue(cdp)
        assert_stage_view(cdp, 3)
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.initial") is not None, "hypothesisSnapshots.initial should be populated before testing reset")

        click_id(cdp, "mmcResetCase")
        require(not cdp.evaluate("document.getElementById('mmcResetConfirm').hidden"), "reset confirm row should appear after clicking Reset Case")
        require(cdp.evaluate("document.getElementById('mmcResetCase').hidden"), "Reset Case button should hide while the confirm row is shown")

        click_id(cdp, "mmcResetNo")
        require(cdp.evaluate("document.getElementById('mmcResetConfirm').hidden"), "Cancel should hide the confirm row again")
        require(not cdp.evaluate("document.getElementById('mmcResetCase').hidden"), "Cancel should restore the Reset Case button")
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 3, "Cancel must leave case progress unchanged")
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.initial") is not None, "Cancel must leave hypothesisSnapshots unchanged")
        require(not cdp.evaluate("document.getElementById('caseFileApp').hidden"), "Cancel must leave the case file open")
        print("OK: Reset Case Cancel leaves state, including hypothesis snapshots, unchanged")

        click_id(cdp, "mmcResetCase")
        click_id(cdp, "mmcResetYes")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "Yes, reset should hide the case file app")
        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "Yes, reset should show Open Case File again")
        require(cdp.evaluate(f"localStorage.getItem({json.dumps(STORAGE_KEY)})") is None, "Yes, reset should clear the persisted state")
        post_reset_snapshots = cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots")
        require(
            post_reset_snapshots == {"initial": None, "stage4": None, "stage7": None, "final": None},
            f"Yes, reset should clear all four hypothesis snapshots, got {post_reset_snapshots}",
        )
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 1, "Yes, reset should restore the initial (Stage 1) state")
        print("OK: Reset Case Yes clears state, including all hypothesis snapshots, and returns to Stage 1")

        pull_errors(cdp, console_error_log, "end of run")
        require(not console_error_log, f"console errors were recorded during the run: {console_error_log}")

        print("PASS: Money Mule or Victim Case File browser regression")
    finally:
        server.shutdown()
        server.server_close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    run()
