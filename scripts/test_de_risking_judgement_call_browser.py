#!/usr/bin/env python3
"""Headless Chrome regression checks for The De-Risking Judgement Call only."""

from __future__ import annotations

import json
import re
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
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = "de-risking-judgement-call"
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)
DEVICE_WIDTHS = (320, 375, 390, 428, 768)
FORMS = (
    ("respondent", "respondent-decision"),
    ("ownership", "ownership-decision"),
    ("residual", "residual-decision"),
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class ProbeHandler(QuietHandler):
    """Serves the repository, and can swap the guide script for one that throws."""

    MODE = {"throw": False}

    def do_GET(self) -> None:
        if ProbeHandler.MODE["throw"] and self.path.split("?")[0] == "/js/de-risking-judgement-call.js":
            body = b"throw new Error('probe: script failure');"
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        return


class CDP:
    def __init__(self, url: str) -> None:
        self.socket = websocket.create_connection(url, timeout=30)
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
    for _ in range(150):
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


def dispatch_key(cdp: CDP, key: str, code: str, virtual_key: int, text: str | None = None) -> None:
    key_down = {
        "type": "keyDown", "key": key, "code": code,
        "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key,
    }
    if text is not None:
        key_down["text"] = text
    cdp.call("Input.dispatchKeyEvent", key_down)
    cdp.call("Input.dispatchKeyEvent", {
        "type": "keyUp", "key": key, "code": code,
        "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key,
    })


def complete_form_by_keyboard(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    for _ in range(200):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == radio_name:
            break
    else:
        raise AssertionError(f"keyboard could not reach {scenario_id} decision group")

    focus_style = cdp.evaluate("getComputedStyle(document.activeElement.closest('.fcr-option')).outlineStyle")
    require(focus_style != "none", f"{scenario_id} keyboard focus indicator is not visible")
    for _ in range(6):
        if cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] input[data-grade=\"best\"]').checked"):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select the {scenario_id} best-graded option")

    dispatch_key(cdp, "Tab", "Tab", 9)
    focused = cdp.evaluate(
        f"document.activeElement === document.querySelector('[data-scenario-id=\"{scenario_id}\"] .fcr-action')"
    )
    require(focused, f"keyboard could not reach {scenario_id} submit control")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    feedback = cdp.evaluate(
        f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .fcr-feedback').textContent"
    )
    require(feedback.startswith("Recorded:"), f"{scenario_id} keyboard feedback failed: {feedback!r}")
    state = cdp.evaluate(
        f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .fcr-feedback').dataset.state"
    )
    require(state == "best", f"{scenario_id} feedback state is {state!r}")
    marked = cdp.evaluate(
        "document.querySelectorAll('[data-scenario-id=\"%s\"]').length && "
        "document.querySelector('[data-scenario-id=\"%s\"]').closest('.fcr-section')"
        ".querySelectorAll('.fcr-optfb[data-selected=\"true\"]').length" % (scenario_id, scenario_id)
    )
    require(marked == 1, f"{scenario_id} should mark exactly one option analysis, marked {marked}")


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate("""(() => {
      const root = document.documentElement;
      const offenders = [...document.querySelectorAll('body *')].filter(el => {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return style.position !== 'fixed' && rect.width > 0 &&
          (rect.left < -1 || rect.right > root.clientWidth + 1);
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: typeof el.className === 'string' ? el.className : ''}));
      const internalOverflows = [...document.querySelectorAll('#main-content *')].filter(el => {
        const style = getComputedStyle(el);
        return el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 &&
          style.overflowX !== 'auto' && style.overflowX !== 'scroll';
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: typeof el.className === 'string' ? el.className : '',
        clientWidth: el.clientWidth, scrollWidth: el.scrollWidth}));
      return {
        clientWidth: root.clientWidth,
        scrollWidth: root.scrollWidth,
        mainHeight: document.getElementById('main-content').getBoundingClientRect().height,
        sourceVisible: document.getElementById('sources').getBoundingClientRect().height > 100,
        decisionForms: document.querySelectorAll('[data-decision-form]').length,
        offenders,
        internalOverflows
      };
    })()""")


def local_variable_audit() -> None:
    """Every var(--x) in the guide's own CSS must be defined in the guide's own :root."""
    html = (ROOT / f"{SLUG}.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    root_block = re.search(r":root\{([^}]*)\}", css).group(1)
    defined = set(re.findall(r"(--[\w-]+)\s*:", root_block))
    used = set(re.findall(r"var\((--[\w-]+)", css))
    missing = sorted(used - defined)
    require(not missing, f"CSS variables used but not defined in the guide's own :root: {missing}")
    inline_leaks = sorted(set(re.findall(r'style="[^"]*var\((--[\w-]+)', html)) - defined)
    require(not inline_leaks, f"inline style variables not defined in the guide's own :root: {inline_leaks}")
    print(f"OK: {len(used)} CSS variables used, all defined in the guide's own :root")


def check_reveal_and_change(cdp: CDP) -> None:
    """Analyses are hidden with JS on until Record, then all revealed with the choice marked; any change clears the verdict."""
    result = cdp.evaluate("""(() => {
      const out = [];
      document.querySelectorAll('[data-decision-form]').forEach(form => {
        const sec = form.closest('.fcr-section');
        const set = sec.querySelector('.fcr-optfb-set');
        const button = form.querySelector('.fcr-action');
        const before = getComputedStyle(set).display;
        const buttonBefore = getComputedStyle(button).display;
        const radios = [...form.querySelectorAll('input[type=radio]')];
        const pick = radios.find(r => r.dataset.grade === 'best');
        pick.checked = true;
        form.dispatchEvent(new Event('change', {bubbles: true}));
        const stillHidden = getComputedStyle(set).display;
        form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        const after = getComputedStyle(set).display;
        const blocks = [...set.querySelectorAll('.fcr-optfb')];
        const visible = blocks.filter(b => b.getBoundingClientRect().height > 0).length;
        const marked = blocks.filter(b => b.dataset.selected === 'true').map(b => b.dataset.option);
        const link = form.querySelector('.fcr-feedback a');
        let focused = null;
        if (link) { link.click(); focused = document.activeElement && document.activeElement.id; }
        const target = blocks.find(b => b.dataset.option === pick.value);
        // change after submit: pick a different option without recording
        const other = radios.find(r => r !== pick);
        other.checked = true;
        form.dispatchEvent(new Event('change', {bubbles: true}));
        const fb = form.querySelector('.fcr-feedback');
        out.push({
          sid: form.dataset.scenarioId, before, buttonBefore, stillHidden, after, blocks: blocks.length, visible, marked,
          linkOk: Boolean(link) && link.getAttribute('href') === '#' + (target && target.id), focusedOk: Boolean(target) && focused === target.id,
          cleared: {
            text: fb.textContent, state: fb.getAttribute('data-state'),
            optionMarks: form.querySelectorAll('.fcr-option[data-selected]').length,
            blockMarks: set.querySelectorAll('.fcr-optfb[data-selected]').length,
            revealed: getComputedStyle(set).display
          }
        });
      });
      return out; })()""")
    for item in result:
        sid = item["sid"]
        require(item["before"] == "none", f"{sid} analyses must be hidden before Record with JS on: {item}")
        require(item["buttonBefore"] != "none", f"{sid} Record button must be visible with JS on")
        require(item["stillHidden"] == "none", f"{sid} choosing an option must not reveal the analyses")
        require(item["after"] != "none" and item["visible"] == item["blocks"] == 4, f"{sid} Record must reveal all four analyses: {item}")
        require(len(item["marked"]) == 1, f"{sid} exactly one analysis must be marked: {item}")
        require(item["linkOk"] and item["focusedOk"], f"{sid} feedback link must lead to and focus the chosen analysis: {item}")
        cleared = item["cleared"]
        require(cleared["text"] == "" and cleared["state"] is None and cleared["optionMarks"] == 0 and cleared["blockMarks"] == 0,
                f"{sid} a change after Record must clear feedback, state and marks: {cleared}")
        require(cleared["revealed"] != "none", f"{sid} analyses stay revealed after a change")
    print("OK: analyses hidden before Record, revealed with the choice marked, focus link works, change clears the verdict")


def check_wait_option_grade(cdp: CDP) -> None:
    """The wait option is graded on the stated facts: badge, feedback and state all agree, and the best option is unchanged."""
    result = cdp.evaluate("""(() => {
      const form = document.querySelector('[data-scenario-id="ownership"]');
      const sec = form.closest('.fcr-section');
      const radio = form.querySelector('input[value="wait"]');
      radio.checked = true;
      form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const fb = form.querySelector('.fcr-feedback');
      const block = sec.querySelector('.fcr-optfb[data-selected="true"]');
      const badge = block && block.querySelector('.fcr-grade');
      const grades = [...form.querySelectorAll('input[type=radio]')].map(r => r.value + ':' + r.dataset.grade);
      return {grade: radio.dataset.grade, label: radio.dataset.gradeLabel, state: fb.dataset.state, feedback: fb.textContent,
              badge: badge && badge.textContent, badgeGrade: badge && badge.dataset.grade, option: block && block.dataset.option, grades};
    })()""")
    require(result["grade"] == "unsupported-facts" and result["label"] == "Not supported on the stated facts", f"wait option grade wrong: {result}")
    require(result["state"] == "unsupported-facts" and "Not supported on the stated facts" in result["feedback"], f"wait feedback wrong: {result}")
    require(result["option"] == "wait" and result["badge"] == "Not supported on the stated facts" and result["badgeGrade"] == "unsupported-facts", f"wait analysis badge wrong: {result}")
    require(sorted(result["grades"]) == sorted(["apply31:best", "enhanced:unsupported", "notice:unsupported", "wait:unsupported-facts"]), f"ownership grades changed unexpectedly: {result['grades']}")
    print("OK: wait option graded Not supported on the stated facts in badge, analysis, feedback and state")


def check_quiz_guessing(cdp: CDP) -> None:
    result = cdp.evaluate("""(() => {
      const f = document.getElementById('knowledgeForm'), fb = document.getElementById('knowledgeFeedback');
      const out = {};
      for (const pos of [0, 1, 2]) {
        f.querySelectorAll('input').forEach(i => i.checked = false);
        ['q1','q2','q3','q4','q5'].forEach(q => { f.querySelectorAll('input[name=' + q + ']')[pos].checked = true; });
        f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        out[pos] = [fb.textContent.slice(0, 14), fb.dataset.state];
      }
      f.dispatchEvent(new Event('change', {bubbles: true}));
      out.afterChange = [fb.textContent, fb.getAttribute('data-state')];
      return out; })()""")
    for pos in ("0", "1", "2"):
        require(result[pos][1] != "best", f"choosing option {int(pos) + 1} everywhere must not score best: {result}")
    require(result["afterChange"] == ["", None], f"a quiz change must clear the score: {result}")
    print("OK: first, second and third option everywhere never score best, quiz change clears the score")


def check_telemetry_once(cdp: CDP) -> None:
    result = cdp.evaluate("""(() => {
      window.__ev = []; window.__errs = 0;
      window.addEventListener('error', () => { window.__errs += 1; });
      window.gtag = (...a) => window.__ev.push(a);
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      const f = document.querySelector('[data-scenario-id="ownership"]');
      const submit = () => f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      f.querySelector('input[data-grade="best"]').checked = true;
      submit(); submit(); f.querySelector('input[data-grade="unsupported"]').checked = true; submit();
      const scenarioEvents = window.__ev.length;
      const k = document.getElementById('knowledgeForm');
      k.querySelectorAll('input[data-correct="true"]').forEach(i => i.checked = true);
      k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const total = window.__ev.length;
      // consent not given first, then given: the event must still be sent once
      localStorage.removeItem('fcr_cookie_consent_v2');
      const r = document.querySelector('[data-scenario-id="respondent"]');
      r.querySelector('input[data-grade="best"]').checked = true;
      r.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const noConsent = window.__ev.length;
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      r.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      r.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const afterConsent = window.__ev.length;
      // analytics that throws must not surface an error or use up the event
      window.gtag = () => { throw new Error('analytics down'); };
      const l = document.querySelector('[data-scenario-id="residual"]');
      l.querySelector('input[data-grade="best"]').checked = true;
      l.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const feedback = l.querySelector('.fcr-feedback').textContent;
      return {scenarioEvents, total, noConsent, afterConsent, errs: window.__errs, feedbackOk: feedback.startsWith('Recorded:')}; })()""")
    require(result["scenarioEvents"] == 1, f"repeated Record must send one scenario event: {result}")
    require(result["total"] == 2, f"repeated scoring must send one knowledge event: {result}")
    require(result["noConsent"] == 2, f"nothing may be sent without consent: {result}")
    require(result["afterConsent"] == 3, f"the event must send once after consent is given: {result}")
    require(result["errs"] == 0 and result["feedbackOk"], f"a failing analytics call must not surface an error or block feedback: {result}")
    print("OK: telemetry once per form per page load, consent respected, analytics failure contained")


def check_export_layout(image: Image.Image) -> None:
    """Every card must end shortly after its last text row (height computed from the drawn fonts)."""
    rgb = image.convert("RGB")
    x = 100
    runs = []
    start = None
    for y in range(rgb.height):
        white = rgb.getpixel((x, y)) == (255, 255, 255)
        if white and start is None:
            start = y
        if not white and start is not None:
            runs.append((start, y - 1))
            start = None
    require(len(runs) == 5, f"expected five card surfaces in the export, found {len(runs)}")
    for top, bottom in runs:
        last_text = top
        for y in range(top, bottom + 1):
            if any(rgb.getpixel((px, y)) != (255, 255, 255) for px in range(112, 1100, 3)):
                last_text = y
        require(bottom - last_text <= 40, f"card {top}-{bottom} has {bottom - last_text}px of empty space below its text")
        require(bottom - last_text >= 8, f"card {top}-{bottom} text runs too close to the card edge")


def check_no_script(cdp: CDP, url: str) -> None:
    """Script unavailable: buttons hidden, analyses visible, and a stray submit navigates nowhere."""
    cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
    navigate(cdp, url, 375)
    state = cdp.evaluate("""(() => ({
      jsClass: document.documentElement.classList.contains('js'),
      buttons: [...document.querySelectorAll('.fcr-choice .fcr-action, #knowledgeForm .fcr-action, #saveFrameworkImage')].map(b => getComputedStyle(b).display),
      sets: [...document.querySelectorAll('.fcr-optfb-set')].map(s => [getComputedStyle(s).display, s.getBoundingClientRect().height > 100]),
      blocks: [...document.querySelectorAll('.fcr-optfb')].filter(b => b.getBoundingClientRect().height > 0).length,
      href: location.href
    }))()""")
    require(state["jsClass"] is False, "the js class must not be set without the script")
    require(state["buttons"] and all(d == "none" for d in state["buttons"]), f"action buttons must be hidden without the script: {state['buttons']}")
    require(len(state["sets"]) == 3 and all(d != "none" and tall for d, tall in state["sets"]), f"analyses must be visible without the script: {state['sets']}")
    require(state["blocks"] == 12, f"all twelve option analyses must be visible without the script: {state['blocks']}")
    dispatch_key(cdp, "Tab", "Tab", 9)
    for _ in range(200):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.type") == "radio":
            break
    cdp.evaluate("document.activeElement.checked = true")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    cdp.evaluate("document.forms[0].requestSubmit()")
    time.sleep(0.4)
    after = cdp.evaluate("({href: location.href, search: location.search, hash: location.hash})")
    require(after["search"] == "" and after["href"] == state["href"], f"a submit without the script must not navigate or add the selection to the URL: {after}")
    cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})
    print("OK: no script: buttons hidden, all analyses visible, stray submit does not navigate")


def wait_scroll_settled(cdp: CDP, limit: float = 12.0) -> None:
    """Smooth scrolling can take a while on a long page, so wait until scrollY stops moving."""
    last = None
    stable = 0
    deadline = time.time() + limit
    while time.time() < deadline:
        current = cdp.evaluate("Math.round(window.scrollY)")
        stable = stable + 1 if current == last else 0
        if stable >= 4:
            return
        last = current
        time.sleep(0.15)
    raise AssertionError("scrolling did not settle")


def check_link_clears_nav(cdp: CDP, url: str) -> None:
    """After 'Read the analysis of your choice', the block must sit at or below the sticky nav."""
    for width in (320, 390, 768):
        navigate(cdp, url, width)
        cdp.evaluate("""(() => {
          const form = document.querySelector('[data-scenario-id="respondent"]');
          form.querySelector('input[data-grade="best"]').checked = true;
          form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
          form.querySelector('.fcr-feedback a').click();
        })()""")
        wait_scroll_settled(cdp)
        # brand.js reveal transitions translate sections while they fade in, which moves getBoundingClientRect.
        time.sleep(1.5)
        geometry = cdp.evaluate("""(() => {
          const block = document.getElementById('optfb-respondent-escalate').getBoundingClientRect();
          const nav = document.querySelector('nav[aria-label="Primary"]') || document.querySelector('nav');
          return {blockTop: block.top, navBottom: nav.getBoundingClientRect().bottom, active: document.activeElement.id,
                  inView: block.top < window.innerHeight};
        })()""")
        require(geometry["active"] == "optfb-respondent-escalate", f"{width}px focus did not reach the analysis: {geometry}")
        require(geometry["blockTop"] >= geometry["navBottom"] - 0.5, f"{width}px analysis top is under the sticky nav: {geometry}")
        require(geometry["inView"], f"{width}px analysis is not in the viewport after the link: {geometry}")
        print(f"OK: {width}px feedback link lands with the analysis below the sticky nav ({geometry['blockTop']:.0f}px >= {geometry['navBottom']:.0f}px)")


def check_no_flash(cdp: CDP, url: str) -> None:
    """Before the js class is set, no action button may be visible and no analysis may be on screen."""
    for width in (390, 1440):
        navigate(cdp, url, width)
        flash = cdp.evaluate("window.__fcrFlash")
        require(flash is not None and flash["jsAt"] is not None, f"{width}px the js class was never set: {flash}")
        require(flash["buttons"] == 0, f"{width}px action buttons were visible before the js class: {flash}")
        require(flash["analysesInView"] == 0, f"{width}px an option analysis was on screen before the js class: {flash}")
        print(f"OK: {width}px no visible flash before the js class ({flash['frames']} frames observed, buttons {flash['buttons']}, analyses on screen {flash['analysesInView']})")


def check_script_throws(cdp: CDP, url: str) -> None:
    """A script that throws leaves the guide in its no-script state."""
    ProbeHandler.MODE["throw"] = True
    try:
        navigate(cdp, url, 375)
        state = cdp.evaluate("""(() => ({
          jsClass: document.documentElement.classList.contains('js'),
          buttons: [...document.querySelectorAll('.fcr-choice .fcr-action, #knowledgeForm .fcr-action, #saveFrameworkImage')].map(b => getComputedStyle(b).display),
          blocks: [...document.querySelectorAll('.fcr-optfb')].filter(b => b.getBoundingClientRect().height > 0).length,
          href: location.href
        }))()""")
        require(state["jsClass"] is False, f"a throwing script must not set the js class: {state}")
        require(state["buttons"] and all(d == "none" for d in state["buttons"]), f"buttons must stay hidden when the script throws: {state}")
        require(state["blocks"] == 12, f"all analyses must stay visible when the script throws: {state}")
        cdp.evaluate("document.forms[0].requestSubmit()")
        time.sleep(0.4)
        require(cdp.evaluate("location.href") == state["href"], "a submit after a script failure must not navigate")
        print("OK: script throws: no js class, buttons hidden, all 12 analyses visible, no navigation")
    finally:
        ProbeHandler.MODE["throw"] = False


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    local_variable_audit()

    server = QuietServer(("127.0.0.1", 0), lambda *args: ProbeHandler(*args, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site_port = server.server_address[1]
    debug_port = 9433
    profile = Path(tempfile.mkdtemp(prefix="fcr-derisk-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-derisk-downloads-"))
    process = subprocess.Popen([
        str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-background-networking",
        f"--remote-debugging-port={debug_port}", "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
        cdp.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__fcrLayoutShift = 0;
          new PerformanceObserver(list => {
            list.getEntries().forEach(entry => { if (!entry.hadRecentInput) window.__fcrLayoutShift += entry.value; });
          }).observe({type: 'layout-shift', buffered: true});
        """})

        cdp.call("Network.enable")
        cdp.call("Network.setCacheDisabled", {"cacheDisabled": True})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__fcrFlash = {buttons: 0, analysesInView: 0, frames: 0, jsAt: null};
          (function loop() {
            const flash = window.__fcrFlash;
            if (!document.documentElement) { requestAnimationFrame(loop); return; }
            if (document.documentElement.classList.contains('js')) { flash.jsAt = performance.now(); return; }
            flash.frames += 1;
            document.querySelectorAll('.fcr-choice .fcr-action, #knowledgeForm .fcr-action, #saveFrameworkImage').forEach(b => {
              if (getComputedStyle(b).display !== 'none') flash.buttons += 1;
            });
            document.querySelectorAll('.fcr-optfb-set').forEach(set => {
              const r = set.getBoundingClientRect();
              if (getComputedStyle(set).display !== 'none' && r.height > 0 && r.top < window.innerHeight && r.bottom > 0) flash.analysesInView += 1;
            });
            requestAnimationFrame(loop);
          })();
        """})

        url = f"http://127.0.0.1:{site_port}/{SLUG}.html"
        for width in WIDTHS:
            navigate(cdp, url, width)
            metrics = page_metrics(cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
            require(metrics["mainHeight"] > 5000, f"{width}px main content is unexpectedly short")
            require(metrics["sourceVisible"], f"{width}px source section is not rendered")
            require(metrics["decisionForms"] == 3, f"{width}px decision forms missing")
            require(not metrics["offenders"], f"{width}px clipped or overflowing elements: {metrics['offenders']}")
            require(not metrics["internalOverflows"], f"{width}px internally clipped content: {metrics['internalOverflows']}")
            require((cdp.evaluate("window.__fcrLayoutShift || 0") or 0) <= 0.1, f"{width}px layout shift exceeded 0.1")
            print(f"OK: {width}px viewport layout, no page overflow")

        # Iframe device-width checks: the page rendered inside a frame of each device width.
        navigate(cdp, url, 1440)
        for width in DEVICE_WIDTHS:
            result = cdp.evaluate(f"""new Promise(resolve => {{
              const old = document.getElementById('__probe'); if (old) old.remove();
              const f = document.createElement('iframe');
              f.id = '__probe'; f.style.cssText = 'position:absolute;left:0;top:0;width:{width}px;height:900px;border:0';
              f.onload = () => setTimeout(() => {{
                const d = f.contentDocument, r = d.documentElement;
                const bad = [...d.querySelectorAll('#main-content *')].filter(el => {{
                  const s = f.contentWindow.getComputedStyle(el), b = el.getBoundingClientRect();
                  return s.position !== 'fixed' && b.width > 0 && (b.left < -1 || b.right > r.clientWidth + 1);
                }}).length;
                resolve({{client: r.clientWidth, scroll: r.scrollWidth, bad, forms: d.querySelectorAll('[data-decision-form]').length}});
              }}, 400);
              f.src = '/{SLUG}.html';
              document.body.appendChild(f);
            }})""", True)
            require(result["client"] == width or result["client"] <= width, f"iframe {width}px width not applied: {result}")
            require(result["scroll"] <= result["client"] + 1, f"iframe {width}px horizontal overflow: {result}")
            require(result["bad"] == 0 and result["forms"] == 3, f"iframe {width}px clipped content or missing forms: {result}")
            print(f"OK: iframe device width {width}px, no horizontal overflow")
        cdp.evaluate("document.getElementById('__probe') && document.getElementById('__probe').remove()")

        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip_link = cdp.evaluate("""(() => {
          const link = document.activeElement;
          return {focused: link.classList.contains('fcr-skip'), target: link.getAttribute('href'),
                  visible: link.getBoundingClientRect().top >= 0};
        })()""")
        require(skip_link == {"focused": True, "target": "#main-content", "visible": True}, "skip link is not the first visible keyboard target")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        time.sleep(0.15)
        skip_result = cdp.evaluate("({hash: location.hash, targetExists: Boolean(document.getElementById('main-content'))})")
        require(skip_result == {"hash": "#main-content", "targetExists": True}, "skip link did not activate its main-content target")
        print("OK: skip link activation and target")

        for scenario_id, radio_name in FORMS:
            navigate(cdp, url, 390)
            complete_form_by_keyboard(cdp, scenario_id, radio_name)
            print(f"OK: {scenario_id} decision keyboard operation, one option analysis marked")

        navigate(cdp, url, 390)
        check_reveal_and_change(cdp)
        check_quiz_guessing(cdp)
        check_wait_option_grade(cdp)
        check_link_clears_nav(cdp, url)
        check_no_flash(cdp, url)
        navigate(cdp, url, 390)
        check_telemetry_once(cdp)

        # Every option in every form carries a grade and the correct one is graded best.
        grades = cdp.evaluate("""[...document.querySelectorAll('[data-decision-form]')].map(f =>
          [...f.querySelectorAll('input[type=radio]')].map(i => i.dataset.grade))""")
        require(all(len(g) == 4 and g.count("best") == 1 for g in grades), f"unexpected grade layout: {grades}")

        navigate(cdp, url, 390)
        cdp.evaluate("""(() => {
          localStorage.removeItem('fcr_cookie_consent_v2');
          window.__fcrTestEvents = [];
          window.gtag = (...args) => window.__fcrTestEvents.push(args);
          const scenario = document.querySelector('[data-scenario-id="respondent"]');
          scenario.querySelector('input[data-grade="best"]').checked = true;
          scenario.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          document.querySelectorAll('#knowledgeForm input[data-correct="true"]').forEach(input => input.checked = true);
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          document.getElementById('saveFrameworkImage').click();
        })()""")
        denied_exports: list[Path] = []
        for _ in range(60):
            denied_exports = list(downloads.glob(f"{SLUG}-summary*.png"))
            if cdp.evaluate("document.getElementById('saveFrameworkStatus').textContent") == "Summary image created." and denied_exports:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("denied-consent export did not complete")
        time.sleep(0.15)
        require(cdp.evaluate("window.__fcrTestEvents.length") == 0, "a telemetry family fired without consent")
        for denied_export in denied_exports:
            denied_export.unlink()
        print("OK: consent denied for scenario, knowledge and export telemetry")

        navigate(cdp, url, 390)
        telemetry = cdp.evaluate("""(() => {
          localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
          window.__fcrTestEvents = [];
          window.gtag = (...args) => window.__fcrTestEvents.push(args);
          const form = document.querySelector('[data-scenario-id="residual"]');
          form.querySelector('input[data-grade="best"]').checked = true;
          form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return window.__fcrTestEvents;
        })()""")
        require(len(telemetry) == 1, "consented aggregate event missing")
        require(set(telemetry[0][2]) == {"guide_id", "scenario_id", "decision_grade"}, "telemetry contains unexpected fields")
        print("OK: consented telemetry remains aggregate")

        empty = cdp.evaluate("""(() => {
          const form = document.querySelector('[data-scenario-id="ownership"]');
          form.querySelectorAll('input').forEach(i => i.checked = false);
          window.__fcrTestEvents = [];
          form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return {text: form.querySelector('.fcr-feedback').textContent, events: window.__fcrTestEvents.length};
        })()""")
        require(empty["events"] == 0 and "Choose an option" in empty["text"], "empty submission must be rejected without telemetry")

        incorrect = cdp.evaluate("""(() => {
          document.querySelectorAll('#knowledgeForm fieldset').forEach(fs => { fs.querySelector('input:not([data-correct="true"])').checked = true; });
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return document.getElementById('knowledgeFeedback').textContent;
        })()""")
        require("Score: 0 of 5" in incorrect, f"knowledge check incorrect-answer path failed: {incorrect!r}")
        correct = cdp.evaluate("""(() => {
          document.querySelectorAll('#knowledgeForm input[data-correct="true"]').forEach(input => input.checked = true);
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return document.getElementById('knowledgeFeedback').textContent;
        })()""")
        require("Score: 5 of 5" in correct, f"knowledge check correct-answer path failed: {correct!r}")
        unanswered = cdp.evaluate("""(() => {
          document.querySelectorAll('#knowledgeForm input').forEach(i => i.checked = false);
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return document.getElementById('knowledgeFeedback').textContent;
        })()""")
        require("Answer all five" in unanswered, "unanswered knowledge check must be rejected")
        print("OK: knowledge check incorrect, all-correct and unanswered paths")

        # Isolation: computed styles against brand.css and brand.js, plus variable equality with :root.
        navigate(cdp, url, 1440)
        # brand.js reveals sections as they enter the viewport, so scroll through in steps.
        total = cdp.evaluate("document.documentElement.scrollHeight")
        for offset in range(0, total + 600, 400):
            cdp.evaluate(f"window.scrollTo(0, {offset})")
            time.sleep(0.2)
        time.sleep(1.5)
        cdp.evaluate("window.scrollTo(0, 0)")
        iso = cdp.evaluate("""(() => {
          const cs = (sel) => { const el = document.querySelector(sel); return el ? getComputedStyle(el) : null; };
          const root = getComputedStyle(document.documentElement);
          const declared = {};
          for (const sheet of document.styleSheets) {
            let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
            for (const rule of rules) {
              if (rule.selectorText === ':root' && rule.style.getPropertyValue('--fcr-navy')) {
                for (const p of rule.style) if (p.startsWith('--fcr-')) declared[p] = rule.style.getPropertyValue(p).trim();
              }
            }
          }
          const mismatched = Object.entries(declared).filter(([k, v]) => root.getPropertyValue(k).trim() !== v).map(([k]) => k);
          const sections = [...document.querySelectorAll('main section')];
          const hiddenSections = sections.filter(s => {
            const st = getComputedStyle(s); return st.opacity !== '1' || (st.transform !== 'none' && st.transform !== '');
          }).map(s => s.id + ':' + s.className + ':' + getComputedStyle(s).opacity + ':' + Math.round(s.getBoundingClientRect().height));
          const action = cs('.fcr-action'), option = cs('.fcr-option'), open = cs('.fcr-open'), pattern = cs('.fcr-pattern');
          const classNames = [...document.querySelectorAll('#main-content [class]')].flatMap(e => [...e.classList]);
          const collisions = classNames.filter(c => /btn|card/i.test(c) && !c.startsWith('kh-')).slice(0, 5);
          return {
            declaredCount: Object.keys(declared).length, mismatched, hiddenSections, collisions,
            action: action && {bg: action.backgroundColor, color: action.color, cursor: action.cursor},
            option: option && {display: option.display, border: option.borderTopStyle},
            open: open && {display: open.display},
            pattern: pattern && {display: pattern.display, bg: pattern.backgroundColor},
            navPosition: cs('nav') && getComputedStyle(document.querySelector('nav')).position,
            footerBg: document.querySelector('footer') && getComputedStyle(document.querySelector('footer')).backgroundColor
          };
        })()""")
        require(iso["declaredCount"] >= 8 and not iso["mismatched"], f"guide :root variables not applied as declared: {iso}")
        require(not iso["hiddenSections"], f"sections left hidden or transformed by global behaviour: {iso['hiddenSections']}")
        require(not iso["collisions"], f"class names that collide with brand selectors: {iso['collisions']}")
        require(iso["action"] and iso["action"]["bg"] not in ("rgba(0, 0, 0, 0)", "transparent"), f"decision action button lost its own background: {iso['action']}")
        print(f"OK: component isolation, computed styles and {iso['declaredCount']} :root variables verified, {iso}")

        navigate(cdp, url, 390)
        cdp.evaluate("document.getElementById('saveFrameworkImage').click()")
        for _ in range(60):
            if cdp.evaluate("document.getElementById('saveFrameworkStatus').textContent") == "Summary image created.":
                break
            time.sleep(0.1)
        else:
            raise AssertionError("Canvas export did not complete")
        exported: list[Path] = []
        for _ in range(60):
            exported = list(downloads.glob(f"{SLUG}-summary*.png"))
            if exported and exported[0].stat().st_size > 0:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("Canvas export file was not downloaded")
        with Image.open(exported[0]) as image:
            rendered = image.convert("RGB")
            require(image.format == "PNG", "Canvas export is not PNG")
            require(rendered.width == 1200 and rendered.height > 1000, "Canvas export dimensions are implausible")
            require(rendered.getpixel((10, 10)) == (7, 29, 43), "Canvas export brand background is missing")
            require(rendered.getpixel((75, 190)) == (15, 118, 110), "Canvas export first pattern accent is missing")
            require(rendered.getpixel((100, 190)) == (255, 255, 255), "Canvas export first pattern content surface is missing")
            check_export_layout(image)
        require(cdp.evaluate("document.querySelectorAll('#saveFrameworkStatus[role=\"status\"]').length") == 1, "export status semantics are missing or duplicated")
        print("OK: closing DOM Canvas export content and status semantics")

        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 428)
        require(cdp.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto", "reduced-motion override did not apply")
        print("OK: reduced motion")

        navigate(cdp, url, 768)
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
        zoom = page_metrics(cdp)
        require(zoom["scrollWidth"] <= zoom["clientWidth"] + 1, "200 percent zoom introduced page overflow")
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 1})
        print("OK: 200 percent zoom")

        cdp.evaluate("""document.querySelectorAll('.fcr-option span').forEach(span => {
          span.style.fontSize = '24px';
          span.textContent += ' Additional explanatory wording for text expansion verification.';
        })""")
        expanded = page_metrics(cdp)
        require(expanded["scrollWidth"] <= expanded["clientWidth"] + 1, "long label expansion introduced page overflow")
        print("OK: long-label expansion")

        check_no_script(cdp, url)
        check_script_throws(cdp, url)
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
        navigate(cdp, url, 375)
        no_js = page_metrics(cdp)
        require(no_js["mainHeight"] > 5000 and no_js["sourceVisible"], "material content unavailable without JavaScript")
        static_ok = cdp.evaluate("""['What Would Change My Decision', 'Red Team', 'Unknown', 'Source', 'Application', 'Recommendation']
          .every(t => document.body.textContent.includes(t))""")
        require(static_ok, "material static reasoning missing with JavaScript disabled")
        print("OK: JavaScript-disabled comprehension")
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})

        print("PASS: De-Risking Judgement Call browser regression")
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
        shutil.rmtree(downloads, ignore_errors=True)


if __name__ == "__main__":
    run()
