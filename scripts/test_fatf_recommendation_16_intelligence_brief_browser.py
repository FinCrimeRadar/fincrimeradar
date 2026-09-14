#!/usr/bin/env python3
"""Headless Chrome release regression for the Recommendation 16 brief."""

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

    def call(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self.message_id += 1
        message_id = self.message_id
        self.socket.send(
            json.dumps({"id": message_id, "method": method, "params": params or {}})
        )
        while True:
            response = json.loads(self.socket.recv())
            if response.get("id") == message_id:
                if "error" in response:
                    raise RuntimeError(f"{method}: {response['error']}")
                return response.get("result", {})

    def evaluate(self, expression: str, await_promise: bool = False) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
        )
        remote = result.get("result", {})
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
        if cdp.evaluate("document.readyState") == "complete":
            cdp.evaluate(
                "document.fonts ? document.fonts.ready.then(() => true) : Promise.resolve(true)",
                True,
            )
            time.sleep(0.2)
            return
        time.sleep(0.1)
    raise TimeoutError("page did not reach readyState complete")


def navigate(cdp: CDP, url: str, width: int) -> None:
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": width < 768,
        },
    )
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)


def dispatch_key(
    cdp: CDP,
    key: str,
    code: str,
    virtual_key: int,
    text: str | None = None,
) -> None:
    key_down: dict[str, Any] = {
        "type": "keyDown",
        "key": key,
        "code": code,
        "windowsVirtualKeyCode": virtual_key,
        "nativeVirtualKeyCode": virtual_key,
    }
    if text is not None:
        key_down["text"] = text
    cdp.call("Input.dispatchKeyEvent", key_down)
    cdp.call(
        "Input.dispatchKeyEvent",
        {
            "type": "keyUp",
            "key": key,
            "code": code,
            "windowsVirtualKeyCode": virtual_key,
            "nativeVirtualKeyCode": virtual_key,
        },
    )


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate(
        """(() => {
          const root = document.documentElement;
          const main = document.getElementById('main-content');
          const sources = document.getElementById('sources');
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
            mainHeight: main.getBoundingClientRect().height,
            sourceHeight: sources.getBoundingClientRect().height,
            sourceOpacity: Number(getComputedStyle(sources).opacity),
            scenarioForms: document.querySelectorAll('[data-scenario-form]').length,
            footerPresent: Boolean(document.querySelector('#site-footer footer')),
            offenders,
            internalOverflows
          };
        })()"""
    )


def complete_scenario_by_keyboard(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    for _ in range(180):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == radio_name:
            break
    else:
        raise AssertionError(f"keyboard could not reach {scenario_id}")

    focus_style = cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle")
    require(focus_style != "none", f"{scenario_id} radio focus is not visible")
    for _ in range(4):
        if cdp.evaluate(
            f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] input[data-grade=\"best\"]').checked"
        ):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select the strongest {scenario_id} option")

    dispatch_key(cdp, "Tab", "Tab", 9)
    require(
        cdp.evaluate(
            f"document.activeElement === document.querySelector('[data-scenario-id=\"{scenario_id}\"] .r16-action')"
        ),
        f"keyboard could not reach the {scenario_id} submit button",
    )
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    result = cdp.evaluate(
        f"""(() => {{
          const form = document.querySelector('[data-scenario-id="{scenario_id}"]');
          return {{
            feedback: form.querySelector('.r16-feedback').textContent,
            reasoningOpen: form.closest('.r16-scenario').querySelector('.r16-reasoning').open
          }};
        }})()"""
    )
    require("Strongest option" in result["feedback"], f"{scenario_id} feedback failed")
    require(result["reasoningOpen"], f"{scenario_id} reasoning did not open")


def capture(cdp: CDP, path: Path) -> None:
    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    path.write_bytes(base64.b64decode(shot["data"]))


def wait_for_export(downloads: Path, cdp: CDP) -> Path:
    for _ in range(60):
        files = list(downloads.glob("fatf-recommendation-16-readiness-patterns*.png"))
        if (
            files
            and files[0].stat().st_size > 0
            and cdp.evaluate("document.getElementById('saveR16Status').textContent")
            == "Summary image created."
        ):
            return files[0]
        time.sleep(0.1)
    raise AssertionError("Canvas export did not complete")


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")

    server = QuietServer(
        ("127.0.0.1", 0),
        lambda *args: QuietHandler(*args, directory=str(ROOT)),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site_port = int(server.server_address[1])
    debug_port = free_port()
    profile = Path(tempfile.mkdtemp(prefix="fcr-r16-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-r16-downloads-"))
    process = subprocess.Popen(
        [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-background-networking",
            f"--remote-debugging-port={debug_port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        for _ in range(80):
            try:
                requests.get(
                    f"http://127.0.0.1:{debug_port}/json/version", timeout=0.5
                ).raise_for_status()
                break
            except requests.RequestException:
                time.sleep(0.15)
        else:
            raise RuntimeError("headless Chrome did not start")

        tab = requests.put(
            f"http://127.0.0.1:{debug_port}/json/new?about:blank", timeout=5
        ).json()
        cdp = CDP(tab["webSocketDebuggerUrl"])
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call(
            "Browser.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": str(downloads)},
        )
        cdp.call(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                  window.__fcrErrors = [];
                  window.__fcrLayoutShift = 0;
                  const originalError = console.error.bind(console);
                  console.error = (...args) => {
                    window.__fcrErrors.push(args.map(String).join(' '));
                    originalError(...args);
                  };
                  addEventListener('error', event => window.__fcrErrors.push(String(event.message || event.error)));
                  addEventListener('unhandledrejection', event => window.__fcrErrors.push(String(event.reason)));
                  if (typeof PerformanceObserver === 'function') {
                    new PerformanceObserver(list => {
                      list.getEntries().forEach(entry => {
                        if (!entry.hadRecentInput) window.__fcrLayoutShift += entry.value;
                      });
                    }).observe({type: 'layout-shift', buffered: true});
                  }
                """
            },
        )

        url = f"http://127.0.0.1:{site_port}/fatf-recommendation-16-intelligence-brief.html"
        for width in WIDTHS:
            navigate(cdp, url, width)
            metrics = page_metrics(cdp)
            require(
                metrics["scrollWidth"] <= metrics["clientWidth"] + 1,
                f"{width}px page overflow: {metrics}",
            )
            require(metrics["mainHeight"] > 8000, f"{width}px main content is too short")
            require(metrics["sourceHeight"] > 250, f"{width}px sources are not rendered")
            require(metrics["scenarioForms"] == 2, f"{width}px scenarios missing")
            require(metrics["footerPresent"], f"{width}px shared footer missing")
            require(not metrics["offenders"], f"{width}px clipped elements: {metrics['offenders']}")
            require(
                not metrics["internalOverflows"],
                f"{width}px internal overflow: {metrics['internalOverflows']}",
            )
            require(
                (cdp.evaluate("window.__fcrLayoutShift || 0") or 0) <= 0.1,
                f"{width}px layout shift exceeded 0.1",
            )
            cdp.evaluate("document.getElementById('sources').scrollIntoView()")
            time.sleep(1.2)
            require(
                cdp.evaluate("Number(getComputedStyle(document.getElementById('sources')).opacity)")
                == 1,
                f"{width}px sources did not reveal when scrolled into view",
            )
            require(not cdp.evaluate("window.__fcrErrors || []"), f"{width}px console errors")
            if width in (390, 1440):
                capture(cdp, Path(rf"C:\tmp\fcr-r16-{width}.png"))
            print(f"OK: {width}px initial layout and content visibility")

        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip = cdp.evaluate(
            """(() => {
              const link = document.activeElement;
              return {
                focused: link.classList.contains('r16-skip'),
                target: link.getAttribute('href'),
                visible: link.getBoundingClientRect().top >= 0
              };
            })()"""
        )
        require(
            skip == {"focused": True, "target": "#main-content", "visible": True},
            "skip link is not the first visible keyboard target",
        )
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        time.sleep(0.1)
        require(
            cdp.evaluate("location.hash") == "#main-content"
            and cdp.evaluate("window.scrollY > 0"),
            "skip link did not activate",
        )
        print("OK: skip link keyboard operation")

        navigate(cdp, url, 390)
        menu = cdp.evaluate(
            """(() => {
              const button = document.getElementById('navHamburger');
              button.click();
              const nav = document.getElementById('mobileNav');
              return {
                open: nav.classList.contains('open'),
                expanded: button.getAttribute('aria-expanded')
              };
            })()"""
        )
        require(
            menu == {"open": True, "expanded": "true"},
            f"mobile navigation state failed: {menu}",
        )
        print("OK: mobile navigation state and disclosure semantics")

        navigate(cdp, url, 390)
        complete_scenario_by_keyboard(
            cdp, "beneficiary_mismatch", "scenario-one"
        )
        print("OK: Scenario 1 keyboard operation and reasoning reveal")
        navigate(cdp, url, 390)
        complete_scenario_by_keyboard(
            cdp, "card_purchase_wallet_funding", "scenario-two"
        )
        print("OK: Scenario 2 keyboard operation and reasoning reveal")

        navigate(cdp, url, 390)
        no_choice = cdp.evaluate(
            """(() => {
              const form = document.querySelector('[data-scenario-id="beneficiary_mismatch"]');
              form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              return form.querySelector('.r16-feedback').textContent;
            })()"""
        )
        require("Choose an option" in no_choice, "scenario empty-state feedback failed")

        incomplete = cdp.evaluate(
            """(() => {
              const form = document.getElementById('r16KnowledgeForm');
              form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              return document.getElementById('r16KnowledgeFeedback').textContent;
            })()"""
        )
        require("Answer all five questions" in incomplete, "knowledge empty state failed")
        incorrect = cdp.evaluate(
            """(() => {
              const form = document.getElementById('r16KnowledgeForm');
              form.querySelectorAll('fieldset').forEach(fieldset => {
                fieldset.querySelector('input:not([data-correct="true"])').checked = true;
              });
              form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              return document.getElementById('r16KnowledgeFeedback').textContent;
            })()"""
        )
        require("0 of 5" in incorrect, "knowledge incorrect path failed")
        correct = cdp.evaluate(
            """(() => {
              const form = document.getElementById('r16KnowledgeForm');
              form.querySelectorAll('input[data-correct="true"]').forEach(input => input.checked = true);
              form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              return document.getElementById('r16KnowledgeFeedback').textContent;
            })()"""
        )
        require("5 of 5" in correct, "knowledge correct path failed")
        print("OK: scenario and knowledge empty, incorrect and correct paths")

        navigate(cdp, url, 390)
        denied = cdp.evaluate(
            """(() => {
              localStorage.removeItem('fcr_cookie_consent_v2');
              window.__fcrEvents = [];
              window.gtag = (...args) => window.__fcrEvents.push(args);
              const scenario = document.querySelector('[data-scenario-id="beneficiary_mismatch"]');
              scenario.querySelector('input[data-grade="best"]').checked = true;
              scenario.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              const knowledge = document.getElementById('r16KnowledgeForm');
              knowledge.querySelectorAll('input[data-correct="true"]').forEach(input => input.checked = true);
              knowledge.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              document.getElementById('saveR16Patterns').click();
              return true;
            })()"""
        )
        require(denied, "denied-consent interaction setup failed")
        denied_export = wait_for_export(downloads, cdp)
        require(cdp.evaluate("window.__fcrEvents.length") == 0, "telemetry fired without consent")
        denied_export.unlink()
        print("OK: all telemetry families denied without consent")

        navigate(cdp, url, 390)
        consented = cdp.evaluate(
            """(() => {
              localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
              window.__fcrEvents = [];
              window.gtag = (...args) => window.__fcrEvents.push(args);
              const scenario = document.querySelector('[data-scenario-id="card_purchase_wallet_funding"]');
              scenario.querySelector('input[data-grade="best"]').checked = true;
              scenario.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              const knowledge = document.getElementById('r16KnowledgeForm');
              knowledge.querySelectorAll('input[data-correct="true"]').forEach(input => input.checked = true);
              knowledge.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              document.getElementById('saveR16Patterns').click();
              return true;
            })()"""
        )
        require(consented, "consented interaction setup failed")
        export_path = wait_for_export(downloads, cdp)
        events = cdp.evaluate("window.__fcrEvents")
        require([event[1] for event in events] == [
            "scenario_complete",
            "knowledge_check_complete",
            "card_export",
        ], f"telemetry event sequence differs: {events}")
        expected_fields = {
            "scenario_complete": {"guide_id", "scenario_id", "decision_grade"},
            "knowledge_check_complete": {"guide_id", "score", "total"},
            "card_export": {"guide_id", "export_type"},
        }
        for event in events:
            require(
                set(event[2]) == expected_fields[event[1]],
                f"unexpected telemetry fields for {event[1]}: {event[2]}",
            )
        with Image.open(export_path) as exported:
            rendered = exported.convert("RGB")
            require(exported.format == "PNG", "Canvas export is not PNG")
            require(rendered.size == (1200, 1510), "Canvas export dimensions differ")
            require(rendered.getpixel((10, 10)) == (7, 29, 43), "export background differs")
            require(rendered.getpixel((64, 190)) == (15, 118, 110), "export accent differs")
            require(rendered.getpixel((100, 190)) == (255, 255, 255), "export card surface differs")
        require(
            cdp.evaluate("document.querySelectorAll('#saveR16Status[role=\"status\"]').length") == 1,
            "export status semantics differ",
        )
        print("OK: consented aggregate telemetry and Canvas export")

        navigate(cdp, url, 390)
        for _ in range(220):
            dispatch_key(cdp, "Tab", "Tab", 9)
            if cdp.evaluate("document.activeElement.matches('#faq summary')"):
                break
        else:
            raise AssertionError("keyboard could not reach the FAQ")
        require(
            cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none",
            "FAQ focus is not visible",
        )
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        require(
            cdp.evaluate("document.activeElement.parentElement.open"),
            "FAQ keyboard disclosure failed",
        )
        print("OK: FAQ keyboard disclosure and visible focus")

        cdp.call(
            "Emulation.setEmulatedMedia",
            {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]},
        )
        navigate(cdp, url, 428)
        reduced = cdp.evaluate(
            """(() => {
              const style = getComputedStyle(document.querySelector('.r16-action'));
              return {animation: style.animationDuration, transition: style.transitionDuration};
            })()"""
        )
        require(
            reduced == {"animation": "1e-05s", "transition": "1e-05s"},
            f"reduced motion override differs: {reduced}",
        )
        print("OK: reduced motion")

        navigate(cdp, url, 768)
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
        zoom = page_metrics(cdp)
        require(
            zoom["scrollWidth"] <= zoom["clientWidth"] + 1,
            "200 percent zoom introduced overflow",
        )
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 1})
        cdp.evaluate(
            """document.querySelectorAll('.r16-option span').forEach(span => {
              span.style.fontSize = '24px';
              span.textContent += ' Additional explanatory wording for text expansion verification.';
            })"""
        )
        expanded = page_metrics(cdp)
        require(
            expanded["scrollWidth"] <= expanded["clientWidth"] + 1,
            "text expansion introduced overflow",
        )
        print("OK: 200 percent zoom and text expansion")

        cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
        navigate(cdp, url, 375)
        no_js = page_metrics(cdp)
        require(
            no_js["mainHeight"] > 8000 and no_js["sourceHeight"] > 250,
            "material content unavailable without JavaScript",
        )
        static_content = cdp.evaluate(
            """document.body.innerText.includes('The Screening Vacuum') &&
              document.body.innerText.includes('Source, Application and Action reasoning') &&
              document.body.innerText.includes('What Would Change Our Assessment') &&
              document.body.innerText.includes('Sources and methodology')"""
        )
        require(static_content, "material static reasoning is missing without JavaScript")
        print("OK: JavaScript-disabled comprehension")
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})

        require(not cdp.evaluate("window.__fcrErrors || []"), "console errors recorded")
        print("PASS: Recommendation 16 Intelligence Brief browser regression")
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
