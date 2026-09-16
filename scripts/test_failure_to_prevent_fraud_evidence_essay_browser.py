#!/usr/bin/env python3
"""Headless Chrome release regression for the Failure to Prevent Fraud
Evidence Essay (Experiment 04)."""

from __future__ import annotations

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

ROOT = Path(__file__).resolve().parents[1]
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)
# The source-panel breakpoint is max-width:800px (see .ftpf-source-panel CSS),
# so 768px is mobile-rail behaviour for that specific check, not desktop.
SOURCE_PANEL_MOBILE_WIDTHS = (320, 375, 390, 428, 768)
SOURCE_PANEL_DESKTOP_WIDTHS = (1440,)


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
        result = self.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": await_promise},
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
            cdp.evaluate("document.fonts ? document.fonts.ready.then(() => true) : Promise.resolve(true)", True)
            time.sleep(0.2)
            return
        time.sleep(0.1)
    raise TimeoutError("page did not reach readyState complete")


def navigate(cdp: CDP, url: str, width: int) -> None:
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": width < 768},
    )
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)


def dispatch_key(cdp: CDP, key: str, code: str, virtual_key: int, text: str | None = None) -> None:
    key_down: dict[str, Any] = {
        "type": "keyDown", "key": key, "code": code,
        "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key,
    }
    if text is not None:
        key_down["text"] = text
    cdp.call("Input.dispatchKeyEvent", key_down)
    cdp.call(
        "Input.dispatchKeyEvent",
        {"type": "keyUp", "key": key, "code": code,
         "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key},
    )


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate(
        """(() => {
          const root = document.documentElement;
          const main = document.getElementById('main-content');
          const offenders = [...document.querySelectorAll('body *')].filter(el => {
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.position !== 'fixed' && rect.width > 0 &&
              (rect.left < -1 || rect.right > root.clientWidth + 1);
          }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: typeof el.className === 'string' ? el.className : ''}));
          return {
            clientWidth: root.clientWidth,
            scrollWidth: root.scrollWidth,
            mainPresent: Boolean(main),
            scenarioForms: document.querySelectorAll('[data-scenario-form]').length,
            offenders
          };
        })()"""
    )


def complete_scenario(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    """Select the strongest option via a real label click (not a .checked mutation),
    submit, and confirm the feedback and reasoning reveal."""
    result = cdp.evaluate(
        f"""(() => {{
          const form = document.querySelector('[data-scenario-id="{scenario_id}"]');
          const radio = form.querySelector('input[name="{radio_name}"][data-grade="best"]');
          radio.closest('label.ftpf-option').click();
          form.querySelector('button.ftpf-action').click();
          const article = form.closest('article');
          return {{
            checked: radio.checked,
            feedback: form.querySelector('.ftpf-feedback').textContent,
            reasoningOpen: article.querySelector('.ftpf-reasoning').open
          }};
        }})()"""
    )
    require(result["checked"], f"{scenario_id}: label click did not select the radio")
    require("Strongest option" in result["feedback"], f"{scenario_id}: feedback did not confirm the best option")
    require(result["reasoningOpen"], f"{scenario_id}: reasoning did not auto-open")


def toggle_counterfactual(cdp: CDP, scenario_id: str) -> None:
    result = cdp.evaluate(
        f"""(() => {{
          const details = document.querySelector('.ftpf-counterfactual[data-scenario-id="{scenario_id}"]');
          details.querySelector('summary').click();
          return details.open;
        }})()"""
    )
    require(result, f"{scenario_id}: counterfactual did not open on click")


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    site_port = int(server.server_address[1])
    debug_port = free_port()
    profile = Path(tempfile.mkdtemp(prefix="fcr-ftpf-chrome-"))
    process = subprocess.Popen(
        [
            str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--disable-background-networking", f"--remote-debugging-port={debug_port}",
            "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank",
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Track this exact PID for cleanup. Never terminate by process name/pattern.
    chrome_pid = process.pid

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
        cdp.call(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                  window.__ftpfErrors = [];
                  const originalError = console.error.bind(console);
                  console.error = (...args) => { window.__ftpfErrors.push(args.map(String).join(' ')); originalError(...args); };
                  addEventListener('error', event => window.__ftpfErrors.push(String(event.message || event.error)));
                  addEventListener('unhandledrejection', event => window.__ftpfErrors.push(String(event.reason)));
                """
            },
        )

        url = f"http://127.0.0.1:{site_port}/failure-to-prevent-fraud-evidence-essay.html"

        # --- No-JS comprehension: fetch raw HTML directly, not via the browser ---
        raw_html = requests.get(url, timeout=5).text
        for needle in (
            "Source", "Application", "Action",  # scenario reasoning labels
            "Change one fact: what if validation and sign-off controls had already operated?",
            "Change one fact: what if the agent supplied only a standard product?",
            "Does one instance of fraud mean the procedures were unreasonable?",
            "Are existing anti-money laundering, bribery or whistleblowing controls sufficient?",
            "Does a contract decide whether a third party is an associated person?",
            "Can having no prevention procedures ever be reasonable?",
            "What should be retained as evidence?",
            "Is the Defensibility Chain a statutory test?",
            "1. Beyond the associated person's base offence",
            "2. How is associated-person capacity assessed?",
            "3. Which statement about the intended-benefit element is correct?",
            "4. Who carries the reasonable-procedures defence burden",
            "5. What is the correct relationship between the Home Office guidance",
        ):
            require(needle in raw_html, f"static HTML is missing required no-JS content: {needle!r}")
        print("OK: no-JS comprehension (raw HTML fetch, no browser) contains full scenario, counterfactual, FAQ and knowledge-check text")

        # --- Layout / overflow / console errors across the full width matrix ---
        for width in WIDTHS:
            navigate(cdp, url, width)
            metrics = page_metrics(cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
            require(metrics["mainPresent"], f"{width}px main content region missing")
            require(metrics["scenarioForms"] == 2, f"{width}px scenario forms missing")
            require(not metrics["offenders"], f"{width}px clipped/overflowing elements: {metrics['offenders']}")
            require(not cdp.evaluate("window.__ftpfErrors || []"), f"{width}px console errors: {cdp.evaluate('window.__ftpfErrors')}")
            print(f"OK: {width}px layout, no overflow, no console errors")

        # --- Skip link ---
        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip = cdp.evaluate(
            """(() => {
              const link = document.activeElement;
              return {
                focused: link.classList.contains('ftpf-skip'),
                target: link.getAttribute('href'),
                visibleBefore: link.getBoundingClientRect().top
              };
            })()"""
        )
        require(skip["focused"] and skip["target"] == "#main-content", "skip link is not the first keyboard target")
        require(skip["visibleBefore"] >= -5, "skip link is not visible once focused")
        print("OK: skip link is the first focusable element and becomes visible on focus")

        # --- Scenario 1 and 2, keyboard-independent real-click flow ---
        navigate(cdp, url, 390)
        complete_scenario(cdp, "revenue_linked_misrepresentation", "ftpf-scenario-one")
        print("OK: Scenario 1 real-click decision, feedback and reasoning reveal")
        navigate(cdp, url, 390)
        complete_scenario(cdp, "eligibility_certification_agent", "ftpf-scenario-two")
        print("OK: Scenario 2 real-click decision, feedback and reasoning reveal")

        # --- Counterfactuals ---
        navigate(cdp, url, 390)
        toggle_counterfactual(cdp, "revenue_linked_misrepresentation")
        toggle_counterfactual(cdp, "eligibility_certification_agent")
        print("OK: both counterfactual blocks open on click")

        # --- Knowledge check: empty, incorrect and correct paths ---
        navigate(cdp, url, 390)
        empty_state = cdp.evaluate(
            """(() => {
              const form = document.getElementById('ftpfKnowledgeForm');
              form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
              return document.getElementById('ftpfKnowledgeFeedback').textContent;
            })()"""
        )
        require("Answer all five questions" in empty_state, "knowledge-check empty-state feedback failed")
        correct = cdp.evaluate(
            """(() => {
              const form = document.getElementById('ftpfKnowledgeForm');
              form.querySelectorAll('input[data-correct="true"]').forEach(input => {
                input.closest('label.ftpf-option').click();
              });
              form.querySelector('button.ftpf-action').click();
              return document.getElementById('ftpfKnowledgeFeedback').textContent;
            })()"""
        )
        require("Score: 5 of 5" in correct, f"knowledge-check correct path failed: {correct}")
        print("OK: knowledge check empty-state and 5-of-5 correct-path via real label clicks")

        # --- FAQ keyboard disclosure ---
        navigate(cdp, url, 390)
        for _ in range(260):
            dispatch_key(cdp, "Tab", "Tab", 9)
            if cdp.evaluate("document.activeElement.matches('.ftpf-faq-list summary')"):
                break
        else:
            raise AssertionError("keyboard could not reach the FAQ")
        require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none",
                "FAQ summary focus is not visible")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        require(cdp.evaluate("document.activeElement.parentElement.open"), "FAQ keyboard disclosure failed")
        print("OK: FAQ keyboard focus and disclosure")

        # --- Save as Image ---
        navigate(cdp, url, 390)
        cdp.evaluate("document.getElementById('ftpfSavePatterns').click()")
        status = None
        for _ in range(40):
            status = cdp.evaluate("document.getElementById('ftpfSaveStatus').textContent")
            if status == "Summary image created.":
                break
            time.sleep(0.1)
        require(status == "Summary image created.", f"Save as Image export did not complete: {status!r}")
        print("OK: Save as Image export completes")

        # --- Source panel: desktop, in-place update, no native navigation ---
        for width in SOURCE_PANEL_DESKTOP_WIDTHS:
            navigate(cdp, url, width)
            result = cdp.evaluate(
                """(() => {
                  const panel = document.getElementById('ftpfSourcePanel');
                  const homeParent = panel.parentElement.className;
                  const cite = document.querySelector('.ftpf-cite[data-src="4"]');
                  cite.click();
                  return {
                    hash: location.hash,
                    parentUnchanged: panel.parentElement.className === homeParent,
                    bodyText: document.getElementById('ftpfSourcePanelBody').textContent.slice(0, 30),
                    panelCount: document.querySelectorAll('#ftpfSourcePanel').length
                  };
                })()"""
            )
            require(result["hash"] == "", f"{width}px: citation click changed location.hash to {result['hash']!r}")
            require(result["parentUnchanged"], f"{width}px: source panel was reparented on desktop")
            require(len(result["bodyText"]) > 10, f"{width}px: source panel body did not update")
            require(result["panelCount"] == 1, f"{width}px: more than one source panel node exists")
            print(f"OK: {width}px source panel updates in place, no native navigation, single node")

        # --- Source panel: mobile reparenting ---
        for width in SOURCE_PANEL_MOBILE_WIDTHS:
            navigate(cdp, url, width)
            result = cdp.evaluate(
                """(() => {
                  const cite = document.querySelector('.ftpf-cite[data-src="1"]');
                  const anchor = cite.closest('p, li, dd');
                  cite.click();
                  const panel = document.getElementById('ftpfSourcePanel');
                  return {
                    hash: location.hash,
                    reparented: panel.previousElementSibling === anchor,
                    panelCount: document.querySelectorAll('#ftpfSourcePanel').length
                  };
                })()"""
            )
            require(result["hash"] == "", f"{width}px: citation click changed location.hash to {result['hash']!r}")
            require(result["reparented"], f"{width}px: source panel did not reparent after the clicked citation")
            require(result["panelCount"] == 1, f"{width}px: more than one source panel node exists")
            print(f"OK: {width}px source panel reparents inline after the clicked citation, single node")

        # --- Source panel restoration above 800px, via a real CDP viewport resize ---
        navigate(cdp, url, 390)
        cdp.evaluate(
            """(() => {
              const cite = document.querySelector('.ftpf-cite[data-src="6"]');
              cite.click();
            })()"""
        )
        reparented_ok = cdp.evaluate(
            "document.getElementById('ftpfSourcePanel').parentElement.className !== 'ftpf-layout'"
        )
        require(reparented_ok, "source panel did not reparent before the restoration check")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1024, "height": 900, "deviceScaleFactor": 1, "mobile": False},
        )
        time.sleep(0.5)
        restored = cdp.evaluate(
            """(() => {
              const panel = document.getElementById('ftpfSourcePanel');
              return {
                parentClass: panel.parentElement.className,
                panelCount: document.querySelectorAll('#ftpfSourcePanel').length,
                bodyText: document.getElementById('ftpfSourcePanelBody').textContent.slice(0, 20)
              };
            })()"""
        )
        require(restored["parentClass"] == "ftpf-layout", f"source panel did not restore to the desktop rail: {restored}")
        require(restored["panelCount"] == 1, "more than one source panel node after restoration")
        require(len(restored["bodyText"]) > 10, "source panel content was lost on restoration")
        print("OK: source panel restores to the desktop rail after widening past 800px, content preserved")

        # --- Reduced motion ---
        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 428)
        require(not cdp.evaluate("window.__ftpfErrors || []"), "console errors under prefers-reduced-motion")
        print("OK: reduced motion, clean reload")
        cdp.call("Emulation.setEmulatedMedia", {"features": []})

        print("PASS: Failure to Prevent Fraud Evidence Essay browser regression")
    finally:
        server.shutdown()
        server.server_close()
        # Terminate only the exact tracked PID launched above. Never taskkill/pkill by name.
        if process.poll() is None and process.pid == chrome_pid:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    run()
