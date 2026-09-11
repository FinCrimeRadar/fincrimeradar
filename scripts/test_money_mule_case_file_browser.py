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
    return bool(cdp.evaluate("document.querySelector('#caseFileApp .mmc-action').disabled"))


def click_continue(cdp: CDP) -> None:
    cdp.evaluate("document.querySelector('#caseFileApp .mmc-action').click()")


def touch_all_hypotheses(cdp: CDP) -> None:
    for letter, value in zip("ABCDE", ["Leading", "Plausible", "Unresolved", "Weak", "Leading"]):
        click_id(cdp, f"hyp-{letter}-{value}")


def assert_stage_view(cdp: CDP, stage: int) -> None:
    text = cdp.evaluate("document.body.innerText")
    require(STAGE_HEADINGS[stage] in text, f"Stage {stage} heading not present while viewing stage {stage}")
    for other, heading in STAGE_HEADINGS.items():
        if other != stage:
            require(heading not in text, f"Stage {other} heading leaked while viewing stage {stage}")
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

        touch_all_hypotheses(cdp)
        require(not continue_disabled(cdp), "Stage 4 continue should enable once all five hypotheses are touched")
        click_continue(cdp)
        assert_stage_view(cdp, 5)

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
        require(not continue_disabled(cdp), "Stage 7 continue should enable once every gated field is touched")
        click_continue(cdp)
        assert_stage_view(cdp, 8)
        print("OK: Stage 7 control/voluntariness genuine independence and combined gate")

        click_continue(cdp)

        # Stage 9: classify phase.
        require(STAGE_HEADINGS[9] in cdp.evaluate("document.body.innerText"), "Stage 9 heading missing")
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.final") is None, "Stage 9 should start in classify phase with no final snapshot")
        touch_all_hypotheses(cdp)
        require(not continue_disabled(cdp), "Stage 9 confirm button should enable once all five hypotheses are re-touched")
        click_continue(cdp)
        require(cdp.evaluate("CaseFileShell.getState().hypothesisSnapshots.final") is not None, "confirming Stage 9 should record the final hypothesis snapshot")
        require("What changed?" in cdp.evaluate("document.body.innerText"), "Stage 9 review phase diff view is missing")
        click_continue(cdp)
        assert_stage_view(cdp, 10)
        print("OK: Stage 9 two-phase classify-then-review flow")

        # Stage 10: per-dimension Decision Record reveal isolation.
        initial_analysis_count = cdp.evaluate("document.querySelectorAll('.mmc-suggested-board-label').length")
        require(initial_analysis_count == 0, f"Stage 10 should show no FinCrimeRadar analysis before any dimension is set, found {initial_analysis_count}")
        for index, (dim_id, element_id) in enumerate(DIMENSION_CHOICES, start=1):
            click_id(cdp, element_id)
            count = cdp.evaluate("document.querySelectorAll('.mmc-suggested-board-label').length")
            require(count == index, f"Stage 10 analysis reveal count mismatch after setting {dim_id}: expected {index}, got {count}")
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
        require(cdp.evaluate("CaseFileShell.getState().caseVersion") == 1, "stale caseVersion should fall back to a fresh default state")
        require(cdp.evaluate("(window.__consoleErrors || []).length") == 0, "stale caseVersion recovery produced console errors")
        print("OK: stale caseVersion falls back to a fresh default state with zero console errors")

        # --- Reset Case: confirm row, Cancel leaves state untouched, Yes clears it. ---
        click_id(cdp, "openCaseFile")
        assert_stage_view(cdp, 2)

        click_id(cdp, "mmcResetCase")
        require(not cdp.evaluate("document.getElementById('mmcResetConfirm').hidden"), "reset confirm row should appear after clicking Reset Case")
        require(cdp.evaluate("document.getElementById('mmcResetCase').hidden"), "Reset Case button should hide while the confirm row is shown")

        click_id(cdp, "mmcResetNo")
        require(cdp.evaluate("document.getElementById('mmcResetConfirm').hidden"), "Cancel should hide the confirm row again")
        require(not cdp.evaluate("document.getElementById('mmcResetCase').hidden"), "Cancel should restore the Reset Case button")
        require(cdp.evaluate("CaseFileShell.getState().currentStage") == 2, "Cancel must leave case progress unchanged")
        require(not cdp.evaluate("document.getElementById('caseFileApp').hidden"), "Cancel must leave the case file open")
        print("OK: Reset Case Cancel leaves state unchanged")

        click_id(cdp, "mmcResetCase")
        click_id(cdp, "mmcResetYes")
        require(cdp.evaluate("document.getElementById('caseFileApp').hidden"), "Yes, reset should hide the case file app")
        require(not cdp.evaluate("document.getElementById('openCaseFile').hidden"), "Yes, reset should show Open Case File again")
        require(cdp.evaluate(f"localStorage.getItem({json.dumps(STORAGE_KEY)})") is None, "Yes, reset should clear the persisted state")
        print("OK: Reset Case Yes clears state and returns to Stage 1")

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
