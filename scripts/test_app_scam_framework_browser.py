#!/usr/bin/env python3
"""Headless Chrome regression checks for Experiment 01 only."""

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
from PIL import Image

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


def complete_scenario_by_keyboard(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    for _ in range(100):
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
        raise AssertionError(f"keyboard could not select {scenario_id} reasoned option")

    dispatch_key(cdp, "Tab", "Tab", 9)
    submit_is_focused = cdp.evaluate(
        f"document.activeElement === document.querySelector('[data-scenario-id=\"{scenario_id}\"] .fcr-action')"
    )
    require(submit_is_focused, f"keyboard could not reach {scenario_id} submit control")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    feedback = cdp.evaluate(
        f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .fcr-feedback').textContent"
    )
    require("Reasoned choice recorded" in feedback, f"{scenario_id} keyboard feedback failed")


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate("""(() => {
      const root = document.documentElement;
      const offenders = [...document.querySelectorAll('body *')].filter(el => {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return style.position !== 'fixed' && rect.width > 0 &&
          (rect.left < -1 || rect.right > root.clientWidth + 1);
      }).slice(0, 8).map(el => ({
        tag: el.tagName,
        id: el.id,
        className: typeof el.className === 'string' ? el.className : ''
      }));
      const internalOverflows = [...document.querySelectorAll('#main-content *')].filter(el => {
        const style = getComputedStyle(el);
        return el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 &&
          style.overflowX !== 'auto' && style.overflowX !== 'scroll';
      }).slice(0, 8).map(el => ({
        tag: el.tagName,
        id: el.id,
        className: typeof el.className === 'string' ? el.className : '',
        clientWidth: el.clientWidth,
        scrollWidth: el.scrollWidth
      }));
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


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site_port = server.server_address[1]
    debug_port = 9422
    profile = Path(tempfile.mkdtemp(prefix="fcr-app-framework-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-app-framework-downloads-"))
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
            list.getEntries().forEach(entry => {
              if (!entry.hadRecentInput) window.__fcrLayoutShift += entry.value;
            });
          }).observe({type: 'layout-shift', buffered: true});
        """})

        url = f"http://127.0.0.1:{site_port}/app-scam-decision-framework.html"
        for width in WIDTHS:
            navigate(cdp, url, width)
            metrics = page_metrics(cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
            require(metrics["mainHeight"] > 3000, f"{width}px main content is unexpectedly short")
            require(metrics["sourceVisible"], f"{width}px source section is not rendered")
            require(metrics["decisionForms"] == 2, f"{width}px decision forms missing")
            require(not metrics["offenders"], f"{width}px clipped or overflowing elements: {metrics['offenders']}")
            require(not metrics["internalOverflows"], f"{width}px internally clipped content: {metrics['internalOverflows']}")
            require((cdp.evaluate("window.__fcrLayoutShift || 0") or 0) <= 0.1, f"{width}px layout shift exceeded 0.1")
            print(f"OK: {width}px initial layout, no page overflow")

        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip_link = cdp.evaluate("""(() => {
          const link = document.activeElement;
          return {
            focused: link.classList.contains('fcr-skip'),
            target: link.getAttribute('href'),
            visible: link.getBoundingClientRect().top >= 0
          };
        })()""")
        require(skip_link == {"focused": True, "target": "#main-content", "visible": True}, "skip link is not the first visible keyboard target")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        time.sleep(0.1)
        skip_result = cdp.evaluate("""({
          hash: location.hash,
          targetExists: Boolean(document.getElementById('main-content')),
          scrolled: window.scrollY > 0
        })""")
        require(skip_result == {"hash": "#main-content", "targetExists": True, "scrolled": True}, "skip link did not activate its main-content target")
        print("OK: skip link activation and target")

        navigate(cdp, url, 390)
        for _ in range(80):
            cdp.call("Input.dispatchKeyEvent", {
                "type": "keyDown", "key": "Tab", "code": "Tab",
                "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
            })
            cdp.call("Input.dispatchKeyEvent", {
                "type": "keyUp", "key": "Tab", "code": "Tab",
                "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
            })
            if cdp.evaluate("document.activeElement && document.activeElement.name") == "contractor-decision":
                break
        else:
            raise AssertionError("keyboard could not reach the scenario decision group")

        focus_style = cdp.evaluate("getComputedStyle(document.activeElement.closest('.fcr-option')).outlineStyle")
        require(focus_style != "none", "keyboard focus indicator is not visible")
        for _ in range(2):
            cdp.call("Input.dispatchKeyEvent", {
                "type": "keyDown", "key": "ArrowDown", "code": "ArrowDown",
                "windowsVirtualKeyCode": 40, "nativeVirtualKeyCode": 40,
            })
            cdp.call("Input.dispatchKeyEvent", {
                "type": "keyUp", "key": "ArrowDown", "code": "ArrowDown",
                "windowsVirtualKeyCode": 40, "nativeVirtualKeyCode": 40,
            })
        require(cdp.evaluate("document.querySelector('[data-scenario-id=\"contractor\"] input[data-grade=\"best\"]').checked"), "keyboard radio selection failed")
        cdp.call("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "Tab", "code": "Tab",
            "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
        })
        cdp.call("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "Tab", "code": "Tab",
            "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
        })
        require(cdp.evaluate("document.activeElement.classList.contains('fcr-action')"), "keyboard could not reach the scenario submit control")
        cdp.call("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "Enter", "code": "Enter",
            "text": "\r", "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13,
        })
        cdp.call("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13,
        })
        require("Reasoned choice recorded" in cdp.evaluate("document.querySelector('[data-scenario-id=\"contractor\"] .fcr-feedback').textContent"), "keyboard scenario feedback failed")
        print("OK: Scenario 1 keyboard operation")

        navigate(cdp, url, 390)
        complete_scenario_by_keyboard(cdp, "warning", "warning-decision")
        print("OK: Scenario 2 keyboard operation")

        navigate(cdp, url, 390)
        cdp.evaluate("""(() => {
          localStorage.removeItem('fcr_cookie_consent_v2');
          window.__fcrTestEvents = [];
          window.gtag = (...args) => window.__fcrTestEvents.push(args);
          const scenario = document.querySelector('[data-scenario-id="contractor"]');
          scenario.querySelector('input[data-grade="best"]').checked = true;
          scenario.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          document.querySelector('#practitioner-lens summary').click();
          document.querySelectorAll('#knowledgeForm input[data-correct="true"]').forEach(input => input.checked = true);
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          document.getElementById('saveFrameworkImage').click();
        })()""")
        denied_exports = []
        for _ in range(40):
            denied_exports = list(downloads.glob("app-scam-decision-framework-summary*.png"))
            if (
                cdp.evaluate("document.getElementById('saveFrameworkStatus').textContent") == "Summary image created."
                and denied_exports
            ):
                break
            time.sleep(0.1)
        else:
            raise AssertionError("denied-consent export did not complete")
        time.sleep(0.15)
        require(cdp.evaluate("window.__fcrTestEvents.length") == 0, "a Framework telemetry family fired without consent")
        for denied_export in denied_exports:
            denied_export.unlink()
        print("OK: consent denied for scenario, lens, knowledge and export telemetry")

        navigate(cdp, url, 390)
        telemetry = cdp.evaluate("""(() => {
          localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
          window.__fcrTestEvents = [];
          window.gtag = (...args) => window.__fcrTestEvents.push(args);
          const form = document.querySelector('[data-scenario-id="warning"]');
          form.querySelector('input[data-grade="best"]').checked = true;
          form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return window.__fcrTestEvents;
        })()""")
        require(len(telemetry) == 1, "consented aggregate event missing")
        event_parameters = telemetry[0][2]
        require(set(event_parameters) == {"guide_id", "scenario_id", "decision_grade"}, "telemetry contains unexpected fields")
        print("OK: consented telemetry remains aggregate")

        incorrect_result = cdp.evaluate("""(() => {
          document.querySelectorAll('#knowledgeForm fieldset').forEach(fieldset => {
            fieldset.querySelector('input:not([data-correct="true"])').checked = true;
          });
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return document.getElementById('knowledgeFeedback').textContent;
        })()""")
        require("0 of 5" in incorrect_result, "knowledge check incorrect-answer path failed")
        correct_result = cdp.evaluate("""(() => {
          document.querySelectorAll('#knowledgeForm input[data-correct="true"]').forEach(input => input.checked = true);
          document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
          return document.getElementById('knowledgeFeedback').textContent;
        })()""")
        require("5 of 5" in correct_result, "knowledge check correct-answer path failed")
        print("OK: knowledge check incorrect and all-correct paths")

        navigate(cdp, url, 390)
        cdp.evaluate("document.querySelector('#practitioner-lens details').open = false")
        for _ in range(120):
            dispatch_key(cdp, "Tab", "Tab", 9)
            if cdp.evaluate("document.activeElement.matches('#practitioner-lens summary')"):
                break
        else:
            raise AssertionError("keyboard could not reach the Practitioner Lens summary")
        lens_outline = cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        require(lens_outline != "none", "Practitioner Lens summary has no visible keyboard focus")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        lens_open = cdp.evaluate("""(() => {
          const detail = document.querySelector('#practitioner-lens details');
          return detail.open && detail.textContent.includes('Separate facts');
        })()""")
        require(lens_open, "keyboard Practitioner Lens disclosure failed")
        print("OK: keyboard Practitioner Lens disclosure")

        cdp.evaluate("document.getElementById('saveFrameworkImage').click()")
        for _ in range(40):
            if cdp.evaluate("document.getElementById('saveFrameworkStatus').textContent") == "Summary image created.":
                break
            time.sleep(0.1)
        else:
            raise AssertionError("Canvas export did not complete")
        exported_files = []
        for _ in range(40):
            exported_files = list(downloads.glob("app-scam-decision-framework-summary*.png"))
            if exported_files and exported_files[0].stat().st_size > 0:
                break
            time.sleep(0.1)
        else:
            raise AssertionError("Canvas export file was not downloaded")
        export_path = exported_files[0]
        with Image.open(export_path) as exported_image:
            rendered = exported_image.convert("RGB")
            require(exported_image.format == "PNG", "Canvas export is not PNG")
            require(rendered.width == 1200 and rendered.height > 1000, "Canvas export dimensions are implausible")
            require(rendered.getpixel((10, 10)) == (7, 29, 43), "Canvas export brand background is missing")
            require(rendered.getpixel((75, 190)) == (15, 118, 110), "Canvas export first pattern accent is missing")
            require(rendered.getpixel((100, 190)) == (255, 255, 255), "Canvas export first pattern content surface is missing")
        require(cdp.evaluate("document.querySelectorAll('#saveFrameworkStatus[role=\"status\"]').length") == 1, "export status semantics are missing or duplicated")
        print("OK: closing DOM Canvas export content and status semantics")

        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 428)
        reduced = cdp.evaluate("getComputedStyle(document.documentElement).scrollBehavior")
        require(reduced == "auto", "reduced-motion override did not apply")
        print("OK: reduced motion")

        navigate(cdp, url, 768)
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
        zoom_metrics = page_metrics(cdp)
        require(zoom_metrics["scrollWidth"] <= zoom_metrics["clientWidth"] + 1, "200 percent zoom introduced page overflow")
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
        require(no_js["mainHeight"] > 3000 and no_js["sourceVisible"], "material content unavailable without JavaScript")
        static_reasoning = cdp.evaluate("""document.body.innerText.includes('The Nominal Performance Trap') &&
          document.body.innerText.includes('What Would Change My Decision?') &&
          document.body.innerText.includes('The Defensibility Layer')""")
        require(static_reasoning, "material static reasoning missing with JavaScript disabled")
        print("OK: JavaScript-disabled comprehension")
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})

        print("PASS: Experiment 01 browser regression")
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
