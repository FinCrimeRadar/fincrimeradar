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
    for _ in range(4):
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


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    local_variable_audit()

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
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
