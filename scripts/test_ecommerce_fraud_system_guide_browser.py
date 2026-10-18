#!/usr/bin/env python3
"""Headless Chrome regression for The E-commerce Fraud System guide.

Starts one headless Chrome, tracks its PID and terminates only that process on exit.
"""

from __future__ import annotations

import base64
import json
import shutil
import socket
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
PAGE = "e-commerce-fraud-system-guide.html"
EXPORT_NAME = "e-commerce-fraud-control-patterns.png"
EXPORT_WIDTH = 1200
EXPORT_HEIGHT = 1371  # pinned after implementation from the closing five-card grid at the current copy and fonts
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)
SCENARIOS = {
    1: {"id": "authenticated_order_fragmented_evidence", "grades": {"A": "weak", "B": "caution", "C": "strongest"}},
    2: {"id": "refund_claims_possible_network", "grades": {"A": "caution", "B": "weak", "C": "strongest"}},
}
QUIZ_KEY = {1: "B", 2: "C", 3: "A", 4: "B", 5: "C"}
EVENT_FIELDS = {
    "scenario_complete": {"guide_id", "scenario_id", "decision_grade", "confidence_band"},
    "counterfactual_complete": {"guide_id", "scenario_id", "reconsidered"},
    "knowledge_check_complete": {"guide_id", "score", "total"},
    "card_export": {"guide_id", "export_type"},
}
GUIDE_ID = "e_commerce_fraud_system_guide"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


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
        result = self.call("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": await_promise})
        remote = result.get("result", {})
        if result.get("exceptionDetails"):
            raise RuntimeError(result["exceptionDetails"].get("exception", {}).get("description", "browser evaluation failed"))
        if remote.get("subtype") == "error":
            raise RuntimeError(remote.get("description", "browser evaluation failed"))
        return remote.get("value")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_ready(cdp: CDP) -> None:
    for _ in range(80):
        if cdp.evaluate("['interactive','complete'].includes(document.readyState)"):
            cdp.evaluate("Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), new Promise(r => setTimeout(r, 2000))]).then(() => true)", True)
            time.sleep(0.2)
            return
        time.sleep(0.1)
    raise TimeoutError("page did not reach an interactive state")


def navigate(cdp: CDP, url: str, width: int, wait_footer: bool = True) -> None:
    cdp.call("Emulation.setDeviceMetricsOverride", {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": width < 768})
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)
    if wait_footer:
        for _ in range(50):
            if cdp.evaluate("Boolean(document.querySelector('#site-footer footer'))"):
                break
            time.sleep(0.1)
    time.sleep(0.4)


def dispatch_key(cdp: CDP, key: str, code: str, virtual_key: int, text: str | None = None) -> None:
    down: dict[str, Any] = {"type": "keyDown", "key": key, "code": code, "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key}
    if text is not None:
        down["text"] = text
    cdp.call("Input.dispatchKeyEvent", down)
    cdp.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": key, "code": code, "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key})


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate(
        """(() => {
          const root = document.documentElement;
          const main = document.getElementById('main-content');
          const sources = document.getElementById('ecf-sources');
          const offenders = [...document.querySelectorAll('body *')].filter(el => {
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.position !== 'fixed' && rect.width > 0 && (rect.left < -1 || rect.right > root.clientWidth + 1);
          }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: String(el.className)}));
          const internal = [...document.querySelectorAll('#main-content *')].filter(el => {
            const style = getComputedStyle(el);
            return el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 && style.overflowX !== 'auto' && style.overflowX !== 'scroll';
          }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: String(el.className)}));
          return {
            clientWidth: root.clientWidth, scrollWidth: root.scrollWidth,
            mainHeight: main.getBoundingClientRect().height, sourceHeight: sources.getBoundingClientRect().height,
            scenarioForms: document.querySelectorAll('[data-scenario-form]').length,
            footerPresent: Boolean(document.querySelector('#site-footer footer')), offenders, internal
          };
        })()"""
    )


def contrast_results(cdp: CDP) -> list[dict[str, Any]]:
    return cdp.evaluate(
        """(() => {
          const channels = value => (value.match(/[\\d.]+/g) || []).map(Number);
          const rgba = value => { const p = channels(value); return {r: p[0] || 0, g: p[1] || 0, b: p[2] || 0, a: p.length > 3 ? p[3] : 1}; };
          const luminance = c => { const v = [c.r, c.g, c.b].map(x => { const s = x / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
          const background = el => { for (let n = el; n; n = n.parentElement) { const c = rgba(getComputedStyle(n).backgroundColor); if (c.a >= 0.99) return c; } return {r: 255, g: 255, b: 255, a: 1}; };
          const seen = new Set();
          const rows = [];
          for (const el of document.querySelectorAll('#main-content :is(p, li, dt, dd, h1, h2, h3, h4, summary, legend, label span, button, a, strong, span)')) {
            if (!el.childNodes.length || ![...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
            const style = getComputedStyle(el);
            if (style.visibility === 'hidden' || el.getBoundingClientRect().width === 0) continue;
            const fg = rgba(style.color), bg = background(el);
            const hi = Math.max(luminance(fg), luminance(bg)), lo = Math.min(luminance(fg), luminance(bg));
            const ratio = (hi + 0.05) / (lo + 0.05);
            const size = parseFloat(style.fontSize), bold = parseInt(style.fontWeight, 10) >= 700;
            const need = size >= 24 || (size >= 18.66 && bold) ? 3 : 4.5;
            const key = el.className + '|' + style.color + '|' + style.backgroundColor;
            if (seen.has(key)) continue;
            seen.add(key);
            rows.push({sel: el.tagName + '.' + el.className, ratio: Math.round(ratio * 100) / 100, need});
          }
          return rows;
        })()"""
    )


def js_select(letter_or_id: str) -> str:
    return f"document.getElementById('{letter_or_id}')"


def reasoning_state(cdp: CDP, n: int) -> dict[str, Any]:
    return cdp.evaluate(
        f"""(() => {{
          const form = document.getElementById('ecf-s{n}-form');
          const cf = document.getElementById('ecf-s{n}-reconsider');
          return {{
            feedback: document.getElementById('ecf-s{n}-feedback').textContent,
            feedbackState: document.getElementById('ecf-s{n}-feedback').dataset.state || '',
            open: document.getElementById('ecf-s{n}-reasoning').open,
            original: document.getElementById('ecf-s{n}-original').textContent,
            originalHidden: document.getElementById('ecf-s{n}-original').hidden,
            confidenceHidden: document.getElementById('ecf-s{n}-confidence-set').hidden,
            checked: [...form.querySelectorAll('.ecf-choice-set input:checked')].map(i => i.value),
            checkedConfidence: [...form.querySelectorAll('.ecf-confidence-set input:checked')].map(i => i.value),
            cfHidden: cf.hidden,
            disabled: form.querySelector('.ecf-choice-set').disabled
          }};
        }})()"""
    )


def install_probes(cdp: CDP) -> None:
    cdp.evaluate(
        """(() => {
          window.__fcrEvents = [];
          window.gtag = (...args) => window.__fcrEvents.push(args);
          return true;
        })()"""
    )


def submit(cdp: CDP, form_id: str) -> None:
    cdp.evaluate(f"document.getElementById('{form_id}').dispatchEvent(new Event('submit', {{bubbles: true, cancelable: true}}))")


def run_scenario_path(cdp: CDP, n: int, letter: str, band: str, reconsider: str) -> None:
    sid = SCENARIOS[n]["id"]
    grade = SCENARIOS[n]["grades"][letter]
    require(reasoning_state(cdp, n)["confidenceHidden"], f"s{n} confidence must stay hidden before a choice")
    cdp.evaluate(f"{js_select(f'ecf-s{n}-{letter.lower()}')}.click()")
    state = reasoning_state(cdp, n)
    require(not state["confidenceHidden"], f"s{n}{letter} confidence did not appear after a choice")
    require(not state["open"], f"s{n}{letter} reasoning opened before submission")
    cdp.evaluate(f"{js_select(f'ecf-s{n}-conf-{band.lower()}')}.click()")
    submit(cdp, f"ecf-s{n}-form")
    state = reasoning_state(cdp, n)
    require(state["open"] and not state["cfHidden"] and not state["originalHidden"], f"s{n}{letter} reasoning not revealed: {state}")
    require(f"option {letter}" in state["feedback"] and grade in state["feedback"] and band.lower() in state["feedback"], f"s{n}{letter} feedback differs: {state['feedback']}")
    require(f"option {letter}, graded {grade}, {band.lower()} confidence" in state["original"], f"s{n}{letter} original answer differs")
    require(state["disabled"], f"s{n}{letter} choice must lock after recording")
    revealed = cdp.evaluate(
        f"""(() => {{
          const d = document.getElementById('ecf-s{n}-reasoning');
          const labels = [...d.querySelectorAll('.ecf-saa strong')].map(x => x.textContent);
          return {{labels, counterfactual: d.querySelector('.ecf-counterfactual').offsetHeight > 0,
                   selectedGrade: d.querySelector('.ecf-grades li[data-selected="true"]').dataset.letter}};
        }})()"""
    )
    require(revealed["labels"] == ["Source", "Application", "Action"] and revealed["counterfactual"] and revealed["selectedGrade"] == letter,
            f"s{n}{letter} revealed reasoning differs: {revealed}")
    # counterfactual: empty first, then answer, original answer must stay
    submit(cdp, f"ecf-s{n}-reconsider")
    empty = cdp.evaluate(f"document.getElementById('ecf-s{n}-cf-status').textContent")
    require("Choose whether you would reconsider" in empty, f"s{n}{letter} counterfactual empty guidance differs: {empty}")
    cdp.evaluate(f"{js_select(f'ecf-s{n}-cf-{reconsider}')}.click()")
    submit(cdp, f"ecf-s{n}-reconsider")
    after = cdp.evaluate(
        f"({{status: document.getElementById('ecf-s{n}-cf-status').textContent, original: document.getElementById('ecf-s{n}-original').textContent, counterfactual: document.querySelector('#ecf-s{n}-counterfactual').textContent}})"
    )
    require(after["original"] == state["original"], f"s{n}{letter} original answer was overwritten")
    require(f"original answer is kept: option {letter}" in after["status"], f"s{n}{letter} counterfactual status differs: {after['status']}")
    require(("would reconsider" if reconsider == "yes" else "would keep your decision") in after["status"], f"s{n}{letter} reconsideration wording differs")
    fact = after["counterfactual"].replace("Counterfactual:", "").strip()
    require(fact[:60] in after["status"], f"s{n}{letter} counterfactual status must explain what changed")
    events = cdp.evaluate("window.__fcrEvents.map(e => [e[1], e[2]])")
    scenario_event = [e for e in events if e[0] == "scenario_complete" and e[1]["scenario_id"] == sid]
    cf_event = [e for e in events if e[0] == "counterfactual_complete" and e[1]["scenario_id"] == sid]
    require(len(scenario_event) == 1 and len(cf_event) == 1, f"s{n}{letter} events differ: {events}")
    require(scenario_event[0][1] == {"guide_id": GUIDE_ID, "scenario_id": sid, "decision_grade": grade, "confidence_band": band.lower()}, f"scenario payload differs: {scenario_event}")
    require(cf_event[0][1] == {"guide_id": GUIDE_ID, "scenario_id": sid, "reconsidered": reconsider == "yes"}, f"counterfactual payload differs: {cf_event}")


def exercise_keyboard_scenario(cdp: CDP, n: int) -> None:
    name = f"ecf-s{n}-choice"
    for _ in range(260):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == name:
            break
    else:
        raise AssertionError(f"keyboard could not reach scenario {n}")
    require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none", f"scenario {n} focus indicator missing")
    for _ in range(4):
        if cdp.evaluate(f"document.getElementById('ecf-s{n}-c').checked"):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select option C in scenario {n}")
    for _ in range(6):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement.name") == f"ecf-s{n}-confidence":
            break
    else:
        raise AssertionError(f"keyboard could not reach confidence in scenario {n}")
    require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none", f"scenario {n} confidence focus missing")
    dispatch_key(cdp, " ", "Space", 32, " ")
    dispatch_key(cdp, "Tab", "Tab", 9)
    require(cdp.evaluate(f"document.activeElement === document.getElementById('ecf-s{n}-submit')"), f"keyboard could not reach submit in scenario {n}")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    state = reasoning_state(cdp, n)
    require("strongest" in state["feedback"] and state["open"], f"scenario {n} keyboard result failed: {state}")
    for _ in range(12):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement.name") == f"ecf-s{n}-cf":
            break
    else:
        raise AssertionError(f"keyboard could not reach reconsideration in scenario {n}")
    dispatch_key(cdp, " ", "Space", 32, " ")
    dispatch_key(cdp, "Tab", "Tab", 9)
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    status = cdp.evaluate(f"document.getElementById('ecf-s{n}-cf-status').textContent")
    require("original answer is kept" in status, f"scenario {n} keyboard reconsideration failed: {status}")


def exercise_quiz_faq_export_by_keyboard(cdp: CDP, downloads: Path) -> None:
    groups: set[str] = set()
    faq_items: set[int] = set()
    submitted = False
    exported = False
    for _ in range(700):
        dispatch_key(cdp, "Tab", "Tab", 9)
        target = cdp.evaluate(
            """(() => { const e = document.activeElement;
              return {id: e.id || '', name: e.name || '', value: e.value || '',
                faq: e.matches('#ecf-faq summary') ? [...document.querySelectorAll('#ecf-faq summary')].indexOf(e) : -1,
                outline: getComputedStyle(e).outlineStyle}; })()"""
        )
        relevant = target["name"].startswith("ecf-q") or target["faq"] >= 0 or target["id"] in {"ecf-kc-submit", "ecf-export-button"}
        if relevant:
            require(target["outline"] != "none", f"keyboard focus indicator missing: {target}")
        if target["name"].startswith("ecf-q") and target["name"] not in groups:
            number = int(target["name"][-1])
            want = QUIZ_KEY[number]
            for _ in range(4):
                if cdp.evaluate(f"document.querySelector('input[name=\"{target['name']}\"]:checked')?.value") == want:
                    break
                dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
            else:
                raise AssertionError(f"keyboard could not select the keyed answer for {target['name']}")
            groups.add(target["name"])
        elif target["id"] == "ecf-kc-submit" and len(groups) == 5 and not submitted:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            submitted = "5 of 5" in cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent")
        elif target["faq"] >= 0 and target["faq"] not in faq_items:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            require(cdp.evaluate("document.activeElement.closest('details').open"), f"FAQ {target['faq'] + 1} did not open by keyboard")
            faq_items.add(target["faq"])
        elif target["id"] == "ecf-export-button" and not exported:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            exported = True
        if submitted and len(faq_items) == 6 and exported:
            break
    require(submitted, "knowledge check was not completed by keyboard")
    require(faq_items == set(range(6)), f"FAQ keyboard coverage differs: {sorted(faq_items)}")
    require(exported, "export control was not activated by keyboard")
    wait_for_export(downloads, cdp)


def wait_for_export(downloads: Path, cdp: CDP) -> Path:
    for _ in range(100):
        files = list(downloads.glob("e-commerce-fraud-control-patterns*.png"))
        if files and files[0].stat().st_size > 0 and cdp.evaluate("document.getElementById('ecf-export-status').textContent") == "Summary image created.":
            return files[0]
        time.sleep(0.1)
    raise AssertionError("Canvas export did not complete")


def check_export(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        require(image.format == "PNG" and image.width == EXPORT_WIDTH, f"export dimensions differ: {image.size}")
        rgb = image.convert("RGB")
        require(image.getbbox() is not None, "export is blank")
        sample = {rgb.getpixel((x, y)) for x in range(80, image.width - 80, 53) for y in range(200, image.height - 80, 61)}
        require(len(sample) >= 3, "export pixels are near-uniform")
        if EXPORT_HEIGHT:
            require(image.height == EXPORT_HEIGHT, f"export height differs: {image.height}")
        return image.size


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site_port = int(server.server_address[1])
    debug_port = free_port()
    profile = Path(tempfile.mkdtemp(prefix="fcr-ecf-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-ecf-downloads-"))
    process = subprocess.Popen(
        [str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-background-networking",
         f"--remote-debugging-port={debug_port}", "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    tracked_pid = process.pid  # the only PID this test may terminate
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
        for domain in ("Page", "Runtime", "Network"):
            cdp.call(f"{domain}.enable")
        cdp.call("Network.setBlockedURLs", {"urls": ["*fundingchoicesmessages.google.com*", "*googletagmanager.com*",
                                                    "*fonts.googleapis.com*", "*fonts.gstatic.com*"]})
        cdp.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__fcrErrors = [];
          window.__fcrNet = [];
          const originalError = console.error.bind(console);
          console.error = (...args) => { window.__fcrErrors.push(args.map(String).join(' ')); originalError(...args); };
          addEventListener('error', event => window.__fcrErrors.push(String(event.message || event.error)));
          addEventListener('unhandledrejection', event => window.__fcrErrors.push(String(event.reason)));
          const nativeFetch = window.fetch;
          window.fetch = function (...args) { window.__fcrNet.push(['fetch', String(args[0])]); return nativeFetch.apply(this, args); };
          const nativeOpen = XMLHttpRequest.prototype.open;
          XMLHttpRequest.prototype.open = function (...args) { window.__fcrNet.push(['xhr', String(args[1])]); return nativeOpen.apply(this, args); };
          if (navigator.sendBeacon) { const nb = navigator.sendBeacon.bind(navigator); navigator.sendBeacon = (...args) => { window.__fcrNet.push(['beacon', String(args[0])]); return nb(...args); }; }
        """})
        url = f"http://127.0.0.1:{site_port}/{PAGE}"

        # A03, A05, V02: layout at every width
        for width in WIDTHS:
            navigate(cdp, url, width)
            metrics = page_metrics(cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
            require(metrics["mainHeight"] > 12000, f"{width}px main content is too short: {metrics['mainHeight']}")
            require(metrics["sourceHeight"] > 250, f"{width}px sources missing")
            require(metrics["scenarioForms"] == 2 and metrics["footerPresent"], f"{width}px scenarios or footer missing")
            require(not metrics["offenders"], f"{width}px clipped elements: {metrics['offenders']}")
            require(not metrics["internal"], f"{width}px internal overflow: {metrics['internal']}")
            require(not cdp.evaluate("window.__fcrErrors"), f"{width}px console errors: {cdp.evaluate('window.__fcrErrors')}")
            flow = cdp.evaluate("""[...document.querySelectorAll('#ecf-flow-list li strong')].map(e => ({w: e.scrollWidth, c: e.clientWidth, t: e.textContent}))""")
            require(all(item["w"] <= item["c"] + 1 for item in flow), f"{width}px lifecycle labels are clipped: {flow}")
            print(f"OK: {width}px layout, no overflow, no console errors")

        # A01: contrast across every distinct text style, A10: target sizes
        navigate(cdp, url, 1440)
        contrast = contrast_results(cdp)
        failing = [item for item in contrast if item["ratio"] < item["need"]]
        require(len(contrast) >= 15, f"contrast sampling too thin: {len(contrast)}")
        require(not failing, f"contrast failures: {failing[:6]}")
        navigate(cdp, url, 390)
        small = cdp.evaluate("""[...document.querySelectorAll('#main-content button, #main-content summary, #main-content .ecf-option, .ecf-primary-nav button')].filter(e => e.getBoundingClientRect().width > 0)
              .map(e => ({id: e.id, h: Math.round(e.getBoundingClientRect().height), w: Math.round(e.getBoundingClientRect().width)})).filter(r => r.h < 44 || r.w < 44)""")
        require(not small, f"touch targets below 44px: {small}")
        # C14: component isolation, computed styles against brand.css generics
        iso = cdp.evaluate(
            """(() => {
              const b = document.getElementById('ecf-export-button');
              const nav = document.querySelector('.ecf-primary-nav'); const crumb = document.querySelector('.ecf-breadcrumb');
              const pattern = document.querySelector('.ecf-pattern');
              return {buttonTransform: getComputedStyle(b).transform, navPos: getComputedStyle(nav).position, crumbPos: getComputedStyle(crumb).position,
                      crumbHeight: getComputedStyle(crumb).height !== '72px', hFont: getComputedStyle(document.querySelector('.ecf-section h2')).fontFamily,
                      htmlOverflowX: getComputedStyle(document.documentElement).overflowX, patternTransition: getComputedStyle(pattern).transitionDuration};
            })()"""
        )
        require(iso["navPos"] == "sticky" and iso["crumbPos"] == "static" and iso["crumbHeight"], f"nav or breadcrumb isolation failed: {iso}")
        require("Playfair" in iso["hFont"], f"heading font differs: {iso}")
        cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 40, "y": 40})
        hovered = cdp.evaluate("""(() => { const b = document.getElementById('ecf-export-button'); b.scrollIntoView({block: 'center'});
              const r = b.getBoundingClientRect(); return {x: r.left + r.width / 2, y: r.top + r.height / 2}; })()""")
        cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": hovered["x"], "y": hovered["y"]})
        time.sleep(0.5)
        require(cdp.evaluate("getComputedStyle(document.getElementById('ecf-export-button')).transform") == "none", "brand.css button hover lift leaks into the export button")
        print(f"OK: contrast ({len(contrast)} distinct text styles, lowest ratio {min(item['ratio'] for item in contrast)}), touch targets and brand.css isolation")

        # reveal check
        navigate(cdp, url, 390)
        revealed = cdp.evaluate(
            """(async () => {
              const sections = [...document.querySelectorAll('#main-content section')];
              for (const s of sections) { s.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, 80)); }
              await new Promise(r => setTimeout(r, 1100));
              return sections.map(s => ({id: s.id, opacity: Number(getComputedStyle(s).opacity), height: s.getBoundingClientRect().height}));
            })()""", True)
        require(len(revealed) == 18 and all(item["opacity"] > 0 and item["height"] > 0 for item in revealed), f"lower-section reveal failed: {revealed}")

        # H03, A08
        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip = cdp.evaluate("({focused: document.activeElement.classList.contains('ecf-skip'), target: document.activeElement.getAttribute('href'), visible: document.activeElement.getBoundingClientRect().top >= 0})")
        require(skip == {"focused": True, "target": "#main-content", "visible": True}, f"skip link is not first: {skip}")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        time.sleep(0.1)
        require(cdp.evaluate("location.hash") == "#main-content", "skip link did not activate")
        navigate(cdp, url, 390)
        for _ in range(60):
            dispatch_key(cdp, "Tab", "Tab", 9)
            if cdp.evaluate("document.activeElement.id") == "navHamburger":
                break
        else:
            raise AssertionError("keyboard could not reach mobile menu")
        require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none", "mobile menu focus missing")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        menu = cdp.evaluate("({open: document.getElementById('mobileNav').classList.contains('open'), expanded: document.getElementById('navHamburger').getAttribute('aria-expanded')})")
        require(menu == {"open": True, "expanded": "true"}, f"mobile menu open state differs: {menu}")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        menu = cdp.evaluate("({open: document.getElementById('mobileNav').classList.contains('open'), expanded: document.getElementById('navHamburger').getAttribute('aria-expanded')})")
        require(menu == {"open": False, "expanded": "false"}, f"mobile menu closed state differs: {menu}")
        print("OK: skip link and mobile menu state")

        # keyboard: both scenarios, quiz, FAQ, export
        navigate(cdp, url, 390)
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
        install_probes(cdp)
        exercise_keyboard_scenario(cdp, 1)
        exercise_keyboard_scenario(cdp, 2)
        exercise_quiz_faq_export_by_keyboard(cdp, downloads)
        for created in downloads.glob("e-commerce-fraud-control-patterns*.png"):
            created.unlink()
        print("OK: both scenarios, confidence, counterfactuals, knowledge check, all FAQs and export work by keyboard")

        # V03: six option paths (all confidence bands, both reconsideration answers), no-selection paths
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
        bands = ["High", "Medium", "Low"]
        path_index = 0
        for n in (1, 2):
            for letter in ("A", "B", "C"):
                navigate(cdp, url, 390)
                cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
                install_probes(cdp)
                run_scenario_path(cdp, n, letter, bands[path_index % 3], "yes" if path_index % 2 == 0 else "no")
                path_index += 1
        print("OK: six scenario option paths with High, Medium and Low confidence and both reconsideration answers")
        navigate(cdp, url, 390)
        install_probes(cdp)
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
        for n in (1, 2):
            submit(cdp, f"ecf-s{n}-form")
            state = reasoning_state(cdp, n)
            require("Choose one of the three options" in state["feedback"] and not state["open"] and state["checked"] == [] and state["confidenceHidden"],
                    f"s{n} no-selection guidance differs: {state}")
            cdp.evaluate(f"document.getElementById('ecf-s{n}-c').click()")
            submit(cdp, f"ecf-s{n}-form")
            state = reasoning_state(cdp, n)
            require("Choose High, Medium or Low confidence" in state["feedback"] and not state["open"] and state["checked"] == ["C"] and not state["confidenceHidden"],
                    f"s{n} no-confidence guidance or state differs: {state}")
            require(not cdp.evaluate("window.__fcrEvents.length"), f"s{n} event fired before a complete decision")
        live = cdp.evaluate("[...document.querySelectorAll('[aria-live]')].every(e => e.getAttribute('aria-live') === 'polite' && e.getAttribute('role') === 'status')")
        require(live, "live regions must be polite status regions")
        print("OK: no-selection and no-confidence guidance keeps state")

        # V04: knowledge check paths
        navigate(cdp, url, 390)
        install_probes(cdp)
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
        submit(cdp, "ecf-kc-form")
        empty = cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent")
        require("Answer all five questions" in empty and "1, 2, 3, 4, 5" in empty, f"knowledge empty path differs: {empty}")
        cdp.evaluate("document.getElementById('ecf-q1-b').click(); document.getElementById('ecf-q3-a').click()")
        submit(cdp, "ecf-kc-form")
        partial = cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent")
        require("Still to answer: 2, 4, 5" in partial and cdp.evaluate("document.getElementById('ecf-q1-b').checked"), f"knowledge partial path differs: {partial}")
        require(not cdp.evaluate("document.getElementById('ecf-kc-answers').open"), "answer key opened before scoring")
        wrong = {1: "A", 2: "A", 3: "B", 4: "A", 5: "A"}
        cdp.evaluate("Object.entries(" + json.dumps(wrong) + ").forEach(([n, l]) => document.getElementById('ecf-q' + n + '-' + l.toLowerCase()).click())")
        submit(cdp, "ecf-kc-form")
        incorrect = cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent")
        require("0 of 5" in incorrect, f"knowledge incorrect path differs: {incorrect}")
        mixed = {1: "B", 2: "C", 3: "A", 4: "A", 5: "A"}
        cdp.evaluate("Object.entries(" + json.dumps(mixed) + ").forEach(([n, l]) => document.getElementById('ecf-q' + n + '-' + l.toLowerCase()).click())")
        submit(cdp, "ecf-kc-form")
        require("3 of 5" in cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent"), "knowledge mixed path differs")
        cdp.evaluate("Object.entries(" + json.dumps(QUIZ_KEY) + ").forEach(([n, l]) => document.getElementById('ecf-q' + n + '-' + l.toLowerCase()).click())")
        submit(cdp, "ecf-kc-form")
        correct = cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent")
        require("5 of 5" in correct and cdp.evaluate("document.getElementById('ecf-kc-answers').open"), f"knowledge correct path differs: {correct}")
        leak = cdp.evaluate("""(() => { const q = document.getElementById('ecf-kc-form'); const attrs = [...q.querySelectorAll('*')].flatMap(e => [...e.attributes].map(a => a.name + '=' + a.value));
              return attrs.filter(a => /correct|answer|key/i.test(a)); })()""")
        require(not leak, f"knowledge DOM leaks correctness: {leak}")
        scores = cdp.evaluate("window.__fcrEvents.filter(e => e[1] === 'knowledge_check_complete').map(e => e[2])")
        require([s["score"] for s in scores] == [0, 3, 5] and all(set(s) == EVENT_FIELDS["knowledge_check_complete"] and s["total"] == 5 for s in scores),
                f"knowledge payloads differ: {scores}")
        print("OK: knowledge check empty, partial, incorrect, mixed and correct paths")

        # V05, J04 to J10: consent states
        def consent_run(value: str | None) -> list[Any]:
            navigate(cdp, url, 390)
            cdp.evaluate("localStorage.removeItem('fcr_cookie_consent_v2')" if value is None else f"localStorage.setItem('fcr_cookie_consent_v2','{value}')")
            install_probes(cdp)
            run_scenario_path_quiet = """(() => {
              document.getElementById('ecf-s1-c').click(); document.getElementById('ecf-s1-conf-high').click();
              document.getElementById('ecf-s1-form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
              document.getElementById('ecf-s1-cf-yes').click();
              document.getElementById('ecf-s1-reconsider').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
              Object.entries(%s).forEach(([n, l]) => document.getElementById('ecf-q' + n + '-' + l.toLowerCase()).click());
              document.getElementById('ecf-kc-form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
              document.getElementById('ecf-export-button').click(); return true; })()""" % json.dumps(QUIZ_KEY)
            cdp.evaluate(run_scenario_path_quiet)
            path = wait_for_export(downloads, cdp)
            check_export(path)
            path.unlink()
            return cdp.evaluate("window.__fcrEvents")

        for denied in (None, "rejected", "denied", ""):
            events = consent_run(denied)
            require(events == [], f"telemetry leaked with consent state {denied!r}: {events}")
        events = consent_run("accepted")
        require([e[1] for e in events] == ["scenario_complete", "counterfactual_complete", "knowledge_check_complete", "card_export"], f"event sequence differs: {events}")
        for event in events:
            require(event[0] == "event" and set(event[2]) == EVENT_FIELDS[event[1]], f"event fields differ: {event}")
        require(events[3][2] == {"guide_id": GUIDE_ID, "export_type": "closing_patterns"}, f"export payload differs: {events[3]}")
        flat = json.dumps(events).lower()
        for term in ("pause the order", "authenticated order", "device", "address", "customer", "rationale", "free_text"):
            require(term not in flat, f"telemetry carries sensitive or textual content: {term}")
        shared_chrome = {"/partials/footer.html"}  # same-origin static footer partial fetched by the shared site-chrome.js, not by this page
        calls = [call for call in cdp.evaluate("window.__fcrNet") if call[1] not in shared_chrome]
        require(calls == [], f"page made a network call: {calls}")
        require(cdp.evaluate("document.querySelectorAll('form[action], form[method]').length") == 0, "form posts to a server")
        require(cdp.evaluate("[localStorage.length, sessionStorage.length]") == [1, 0], "page persisted state beyond the consent key")
        print("OK: accepted, denied, missing and empty consent states, event schemas, no network call and no persisted state")

        # J11: export dimensions, source DOM
        navigate(cdp, url, 1440)
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted')")
        install_probes(cdp)
        cdp.evaluate("document.getElementById('ecf-export-button').click()")
        exported = wait_for_export(downloads, cdp)
        size = check_export(exported)
        print(f"OK: PNG export {size[0]} x {size[1]}")
        exported.unlink()

        # J12: failure paths stay non-destructive
        navigate(cdp, url, 390)
        cdp.evaluate("localStorage.setItem('fcr_cookie_consent_v2','accepted'); window.__fcrEvents = []; window.gtag = undefined; true")
        cdp.evaluate("document.getElementById('ecf-s1-a').click(); document.getElementById('ecf-s1-conf-low').click(); document.getElementById('ecf-s1-form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}))")
        require(reasoning_state(cdp, 1)["open"], "scenario failed without analytics")
        cdp.evaluate("""Object.defineProperty(window, 'localStorage', {get() { throw new Error('storage blocked'); }, configurable: true}); true""")
        cdp.evaluate("document.getElementById('ecf-s2-c').click(); document.getElementById('ecf-s2-conf-medium').click(); document.getElementById('ecf-s2-form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}))")
        require(reasoning_state(cdp, 2)["open"], "scenario failed with blocked storage")
        cdp.evaluate("Object.entries(" + json.dumps(QUIZ_KEY) + ").forEach(([n, l]) => document.getElementById('ecf-q' + n + '-' + l.toLowerCase()).click()); document.getElementById('ecf-kc-form').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}))")
        require("5 of 5" in cdp.evaluate("document.getElementById('ecf-kc-feedback').textContent"), "knowledge check failed with blocked storage")
        cdp.evaluate("HTMLCanvasElement.prototype.getContext = () => null; document.getElementById('ecf-export-button').click()")
        require(cdp.evaluate("document.getElementById('ecf-export-status').textContent") == "Export unavailable.", "Canvas-unavailable message differs")
        require(not cdp.evaluate("window.__fcrErrors"), f"failure paths raised errors: {cdp.evaluate('window.__fcrErrors')}")
        navigate(cdp, url, 390)
        cdp.evaluate("HTMLCanvasElement.prototype.toBlob = function (cb) { cb(null); }; document.getElementById('ecf-export-button').click()")
        time.sleep(0.5)
        require(cdp.evaluate("document.getElementById('ecf-export-status').textContent") == "Export unavailable.", "toBlob failure message differs")
        require(not list(downloads.glob("*.png")), "failed export created a file")
        print("OK: analytics, storage, Canvas and toBlob failures stay non-destructive")

        # A06, A04, A05
        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 428)
        reduced = cdp.evaluate("(() => { const s = getComputedStyle(document.querySelector('.ecf-action')); return {a: s.animationDuration, t: s.transitionDuration}; })()")
        require(reduced == {"a": "1e-05s", "t": "1e-05s"}, f"reduced motion differs: {reduced}")
        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "no-preference"}]})
        for width in (768, 320):
            navigate(cdp, url, width)
            cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
            zoom = page_metrics(cdp)
            require(zoom["scrollWidth"] <= zoom["clientWidth"] + 1, f"200 percent zoom overflow at {width}")
            require(cdp.evaluate("document.getElementById('ecf-s1-submit').getBoundingClientRect().width > 0"), "controls lost at 200 percent zoom")
            cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 1})
        navigate(cdp, url, 320)
        cdp.evaluate("""document.querySelectorAll('.ecf-option span').forEach(x => { x.style.fontSize = '24px'; x.textContent += ' Additional explanatory wording for text expansion verification.'; });
                        document.querySelectorAll('.ecf-saa p, .ecf-pattern-lines dd, .ecf-steps p').forEach(x => { x.style.fontSize = '20px'; });
                        document.getElementById('ecf-s1-reasoning').open = true;
                        document.querySelector('.ecf-sources li').textContent += ' ' + 'LongTitleWithoutSpaces'.repeat(6);""")
        expanded = page_metrics(cdp)
        require(expanded["scrollWidth"] <= expanded["clientWidth"] + 1, "text expansion overflow")
        require(not expanded["internal"], f"text expansion clipped content: {expanded['internal']}")
        print("OK: reduced motion, 200 percent zoom at 768 and 320, and text expansion")

        # A07, H09: JavaScript disabled
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
        navigate(cdp, url, 375, wait_footer=False)
        no_js = page_metrics(cdp)
        require(no_js["mainHeight"] > 12000 and no_js["sourceHeight"] > 250, "material content unavailable without JavaScript")
        text = cdp.evaluate("document.body.innerText")
        for needle in ("The Local Green Light", "The Rights Collapse", "Source, Application and Action reasoning",
                       "What Would Change Our Assessment", "Sources and methodology", "Fraud Evidence Relay", "seven-step backtrace test",
                       "Answer key and explanations", "Does the Fraud Evidence Relay require a new platform or backend?"):
            require(needle in text, f"static content missing without JavaScript: {needle}")
        require(not cdp.evaluate("document.getElementById('ecf-s1-confidence-set').hidden"), "confidence controls must be visible without JavaScript")
        for target in ("ecf-s1-reasoning", "ecf-s2-reasoning", "ecf-kc-answers"):
            focused = cdp.evaluate(f"(() => {{ const s = document.querySelector('#{target} > summary'); s.focus(); return document.activeElement === s; }})()")
            require(focused, f"no-script disclosure could not receive focus: {target}")
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            require(cdp.evaluate(f"document.getElementById('{target}').open"), f"no-script disclosure did not open: {target}")
        opened_text = cdp.evaluate("document.body.innerText")
        require("Counterfactual:" in opened_text and "Correct answer: B." in opened_text and "Your original answer" not in opened_text,
                "reasoning, counterfactual and answer key must read after native disclosure without JavaScript")
        require(cdp.evaluate("document.getElementById('ecf-s1-reconsider').hidden"), "reconsideration form must stay hidden without a recorded decision")
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})
        print("OK: JavaScript-disabled comprehension and native disclosure")

        # H12: reading order of the lifecycle visual
        navigate(cdp, url, 390)
        order = cdp.evaluate("""[...document.getElementById('ecf-lifecycle-figure').children].map(e => e.id || e.className || e.tagName)""")
        require(order[0] == "ecf-lifecycle-caption" and "ecf-flow" in order[2] and order[-1] == "ecf-visual-text", f"visual reading order differs: {order}")
        require(cdp.evaluate("document.querySelector('.ecf-direction').getAttribute('aria-hidden')") == "true", "decorative direction cue must be hidden from assistive technology")
        print("PASS: E-commerce Fraud System browser regression")
    finally:
        server.shutdown()
        server.server_close()
        # Permitted cleanup: only the tracked PID this run launched.
        if process.pid == tracked_pid and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(downloads, ignore_errors=True)


if __name__ == "__main__":
    run()
