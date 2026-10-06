#!/usr/bin/env python3
"""Headless Chrome regression for the Digital Identity CDD brief."""

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
        if cdp.evaluate("['interactive','complete'].includes(document.readyState)"):
            cdp.evaluate(
                "Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), "
                "new Promise(resolve => setTimeout(resolve, 2000))]).then(() => true)",
                True,
            )
            time.sleep(0.2)
            return
        time.sleep(0.1)
    raise TimeoutError("page did not reach an interactive state")


def navigate(cdp: CDP, url: str, width: int) -> None:
    cdp.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": width < 768},
    )
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)
    time.sleep(0.5)


def dispatch_key(cdp: CDP, key: str, code: str, virtual_key: int, text: str | None = None) -> None:
    down: dict[str, Any] = {
        "type": "keyDown", "key": key, "code": code,
        "windowsVirtualKeyCode": virtual_key, "nativeVirtualKeyCode": virtual_key,
    }
    if text is not None:
        down["text"] = text
    cdp.call("Input.dispatchKeyEvent", down)
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
          const sources = document.getElementById('sources');
          const offenders = [...document.querySelectorAll('body *')].filter(el => {
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.position !== 'fixed' && rect.width > 0 &&
              (rect.left < -1 || rect.right > root.clientWidth + 1);
          }).slice(0, 8).map(el => ({tag:el.tagName,id:el.id,className:String(el.className)}));
          const internal = [...document.querySelectorAll('#main-content *')].filter(el => {
            const style = getComputedStyle(el);
            return el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 &&
              style.overflowX !== 'auto' && style.overflowX !== 'scroll';
          }).slice(0, 8).map(el => ({tag:el.tagName,id:el.id,className:String(el.className)}));
          return {
            clientWidth: root.clientWidth,
            scrollWidth: root.scrollWidth,
            mainHeight: main.getBoundingClientRect().height,
            sourceHeight: sources.getBoundingClientRect().height,
            scenarioForms: document.querySelectorAll('[data-scenario-form]').length,
            footerPresent: Boolean(document.querySelector('#site-footer footer')),
            offenders: offenders,
            internal: internal
          };
        })()"""
    )


def capture(cdp: CDP, path: Path) -> None:
    shot = cdp.call("Page.captureScreenshot", {"format": "png"})
    path.write_bytes(base64.b64decode(shot["data"]))


def complete_scenario_by_keyboard(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    for _ in range(220):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == radio_name:
            break
    else:
        raise AssertionError(f"keyboard could not reach {scenario_id}")
    require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none", f"{scenario_id} focus missing")
    for _ in range(4):
        if cdp.evaluate(f'document.querySelector(\'[data-scenario-id="{scenario_id}"] input[data-grade="best"]\').checked'):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select strongest option for {scenario_id}")
    dispatch_key(cdp, "Tab", "Tab", 9)
    require(
        cdp.evaluate(f'document.activeElement === document.querySelector(\'[data-scenario-id="{scenario_id}"] .dicdd-action\')'),
        f"keyboard could not reach submit for {scenario_id}",
    )
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    result = cdp.evaluate(
        f"""(() => {{
          const form = document.querySelector('[data-scenario-id="{scenario_id}"]');
          return {{
            feedback: form.querySelector('.dicdd-feedback').textContent,
            open: form.closest('.dicdd-scenario').querySelector('.dicdd-reasoning').open
          }};
        }})()"""
    )
    require("Strongest option" in result["feedback"] and result["open"], f"{scenario_id} result failed")


def contrast_results(cdp: CDP) -> list[dict[str, Any]]:
    return cdp.evaluate(
        """(() => {
          const selectors = ['.dicdd-action', '.dicdd-state', '.dicdd-option span', '.dicdd-counterfactual'];
          const channels = value => (value.match(/[\\d.]+/g) || []).map(Number);
          const rgba = value => {
            const parts = channels(value);
            return {r:parts[0] || 0,g:parts[1] || 0,b:parts[2] || 0,a:parts.length > 3 ? parts[3] : 1};
          };
          const luminance = colour => {
            const values = [colour.r, colour.g, colour.b].map(value => {
              const channel = value / 255;
              return channel <= 0.03928 ? channel / 12.92 : Math.pow((channel + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2];
          };
          const background = element => {
            for (let node = element; node; node = node.parentElement) {
              const colour = rgba(getComputedStyle(node).backgroundColor);
              if (colour.a >= 0.99) return colour;
            }
            return {r:255,g:255,b:255,a:1};
          };
          return selectors.map(selector => {
            const element = document.querySelector(selector);
            const foreground = rgba(getComputedStyle(element).color);
            const backdrop = background(element);
            const high = Math.max(luminance(foreground), luminance(backdrop));
            const low = Math.min(luminance(foreground), luminance(backdrop));
            return {selector, ratio:(high + 0.05) / (low + 0.05)};
          });
        })()"""
    )


def exercise_remaining_controls_by_keyboard(cdp: CDP, downloads: Path) -> None:
    knowledge_groups: set[str] = set()
    faq_items: set[int] = set()
    knowledge_submitted = False
    export_started = False
    for _ in range(520):
        dispatch_key(cdp, "Tab", "Tab", 9)
        target = cdp.evaluate(
            """(() => {
              const element = document.activeElement;
              const faq = element.matches('#faq summary') ? [...document.querySelectorAll('#faq summary')].indexOf(element) : -1;
              return {
                id: element.id || '', name: element.name || '', faq,
                knowledgeSubmit: element.matches('#dicddKnowledgeForm button[type="submit"]'),
                exportButton: element.id === 'saveDicddPatterns',
                outline: getComputedStyle(element).outlineStyle
              };
            })()"""
        )
        relevant = target["name"] in {"q1", "q2", "q3", "q4", "q5"} or target["faq"] >= 0 or target["knowledgeSubmit"] or target["exportButton"]
        if relevant:
            require(target["outline"] != "none", f"keyboard focus indicator missing: {target}")
        if target["name"] in {"q1", "q2", "q3", "q4", "q5"}:
            for _ in range(4):
                selected = cdp.evaluate(
                    "document.activeElement.checked && document.activeElement.dataset.correct === 'true'"
                )
                if selected:
                    break
                if cdp.evaluate("document.activeElement.dataset.correct === 'true'"):
                    dispatch_key(cdp, " ", "Space", 32, " ")
                else:
                    dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
            else:
                raise AssertionError(f"keyboard could not select correct answer for {target['name']}")
            knowledge_groups.add(target["name"])
        elif target["knowledgeSubmit"] and knowledge_groups == {"q1", "q2", "q3", "q4", "q5"}:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            knowledge_submitted = "5 of 5" in cdp.evaluate("document.getElementById('dicddKnowledgeFeedback').textContent")
        elif target["faq"] >= 0:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            opened = cdp.evaluate("document.activeElement.closest('details').open")
            require(opened, f"FAQ {target['faq'] + 1} did not open by keyboard")
            faq_items.add(target["faq"])
        elif target["exportButton"] and not export_started:
            dispatch_key(cdp, "Enter", "Enter", 13, "\r")
            export_started = True
        if knowledge_submitted and len(faq_items) == 6 and export_started:
            break
    require(knowledge_submitted, "knowledge check was not completed by keyboard")
    require(faq_items == set(range(6)), f"FAQ keyboard coverage differs: {sorted(faq_items)}")
    require(export_started, "export control was not activated by keyboard")
    wait_for_export(downloads, cdp)


def open_no_script_reasoning_by_keyboard(cdp: CDP) -> None:
    scenario_ids = (
        "verified_identity_unresolved_relationship",
        "verified_director_unresolved_company",
    )
    for scenario_id in scenario_ids:
        focused = cdp.evaluate(
            f"""(() => {{
              const form = document.querySelector('[data-scenario-id="{scenario_id}"]');
              const summary = form.closest('.dicdd-scenario').querySelector('.dicdd-reasoning summary');
              summary.focus();
              return document.activeElement === summary;
            }})()"""
        )
        require(focused, f"no-script reasoning could not receive focus: {scenario_id}")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        opened = cdp.evaluate(
            f'document.querySelector(\'[data-scenario-id="{scenario_id}"]\').closest(\'.dicdd-scenario\').querySelector(\'.dicdd-reasoning\').open'
        )
        require(opened, f"no-script reasoning did not open: {scenario_id}")


def wait_for_export(downloads: Path, cdp: CDP) -> Path:
    for _ in range(80):
        files = list(downloads.glob("digital-identity-cdd-proof-boundary-patterns*.png"))
        if files and files[0].stat().st_size > 0 and cdp.evaluate("document.getElementById('saveDicddStatus').textContent") == "Summary image created.":
            return files[0]
        time.sleep(0.1)
    raise AssertionError("Canvas export did not complete")


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site_port = int(server.server_address[1])
    debug_port = free_port()
    profile = Path(tempfile.mkdtemp(prefix="fcr-dicdd-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-dicdd-downloads-"))
    process = subprocess.Popen(
        [str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-background-networking",
         f"--remote-debugging-port={debug_port}", "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
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
        cdp.call("Network.enable")
        cdp.call(
            "Network.setBlockedURLs",
            {"urls": [
                "*fundingchoicesmessages.google.com*",
                "*googletagmanager.com*",
                "*fonts.googleapis.com*",
                "*fonts.gstatic.com*",
            ]},
        )
        cdp.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__fcrErrors = [];
          const originalError = console.error.bind(console);
          console.error = (...args) => { window.__fcrErrors.push(args.map(String).join(' ')); originalError(...args); };
          addEventListener('error', event => window.__fcrErrors.push(String(event.message || event.error)));
          addEventListener('unhandledrejection', event => window.__fcrErrors.push(String(event.reason)));
        """})
        url = f"http://127.0.0.1:{site_port}/digital-identity-cdd-intelligence-brief.html"

        for width in WIDTHS:
            navigate(cdp, url, width)
            for _ in range(50):
                if cdp.evaluate("Boolean(document.querySelector('#site-footer footer'))"):
                    break
                time.sleep(0.1)
            metrics = page_metrics(cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
            require(metrics["mainHeight"] > 6500, f"{width}px main content is too short")
            require(metrics["sourceHeight"] > 250, f"{width}px sources missing")
            require(metrics["scenarioForms"] == 2, f"{width}px scenarios missing")
            require(metrics["footerPresent"], f"{width}px shared footer missing")
            require(not metrics["offenders"], f"{width}px clipped elements: {metrics['offenders']}")
            require(not metrics["internal"], f"{width}px internal overflow: {metrics['internal']}")
            require(not cdp.evaluate("window.__fcrErrors || []"), f"{width}px console errors")
            if width in (390, 1440):
                capture(cdp, Path(tempfile.gettempdir()) / f"fcr-dicdd-{width}.png")
            print(f"OK: {width}px layout and visibility")

        contrast = contrast_results(cdp)
        require(all(item["ratio"] >= 4.5 for item in contrast), f"representative text contrast failed: {contrast}")
        revealed = cdp.evaluate(
            """(async () => {
              const sections = [...document.querySelectorAll('#main-content > section')];
              for (const section of sections) {
                section.scrollIntoView({block:'center'});
                await new Promise(resolve => setTimeout(resolve, 80));
              }
              await new Promise(resolve => setTimeout(resolve, 1100));
              return sections.map(section => {
                const style = getComputedStyle(section);
                const rect = section.getBoundingClientRect();
                return {id:section.id,opacity:Number(style.opacity),visibility:style.visibility,height:rect.height};
              });
            })()""",
            True,
        )
        require(all(item["opacity"] > 0 and item["visibility"] != "hidden" and item["height"] > 0 for item in revealed), f"lower-section reveal failed: {revealed}")
        print("OK: representative contrast and all lower-section reveals")

        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip = cdp.evaluate("({focused:document.activeElement.classList.contains('dicdd-skip'),target:document.activeElement.getAttribute('href'),visible:document.activeElement.getBoundingClientRect().top>=0})")
        require(skip == {"focused": True, "target": "#main-content", "visible": True}, "skip link is not first")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        time.sleep(0.1)
        require(cdp.evaluate("location.hash") == "#main-content", "skip link did not activate")
        print("OK: skip link keyboard operation")

        navigate(cdp, url, 390)
        for _ in range(60):
            dispatch_key(cdp, "Tab", "Tab", 9)
            if cdp.evaluate("document.activeElement.id") == "navHamburger":
                break
        else:
            raise AssertionError("keyboard could not reach mobile menu")
        require(cdp.evaluate("getComputedStyle(document.activeElement).outlineStyle") != "none", "mobile menu focus missing")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        menu = cdp.evaluate("(() => {const b=document.getElementById('navHamburger');return {open:document.getElementById('mobileNav').classList.contains('open'),expanded:b.getAttribute('aria-expanded')}})()")
        require(menu == {"open": True, "expanded": "true"}, f"mobile menu failed: {menu}")
        print("OK: mobile menu keyboard operation and semantics")

        navigate(cdp, url, 390)
        complete_scenario_by_keyboard(cdp, "verified_identity_unresolved_relationship", "scenario-one-choice")
        navigate(cdp, url, 390)
        complete_scenario_by_keyboard(cdp, "verified_director_unresolved_company", "scenario-two-choice")
        print("OK: both scenarios work by keyboard")

        navigate(cdp, url, 390)
        exercise_remaining_controls_by_keyboard(cdp, downloads)
        for created in downloads.glob("digital-identity-cdd-proof-boundary-patterns*.png"):
            created.unlink()
        print("OK: knowledge check, all FAQs and export work by keyboard")

        navigate(cdp, url, 390)
        no_choice = cdp.evaluate("(() => {const f=document.querySelector('[data-scenario-form]');f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return f.querySelector('.dicdd-feedback').textContent})()")
        require("Choose an option" in no_choice, "scenario empty state failed")
        incomplete = cdp.evaluate("(() => {const f=document.getElementById('dicddKnowledgeForm');f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return document.getElementById('dicddKnowledgeFeedback').textContent})()")
        require("Answer all five questions" in incomplete, "knowledge empty state failed")
        incorrect = cdp.evaluate("(() => {const f=document.getElementById('dicddKnowledgeForm');f.querySelectorAll('fieldset').forEach(x=>x.querySelector('input:not([data-correct=\"true\"])').checked=true);f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return document.getElementById('dicddKnowledgeFeedback').textContent})()")
        require("0 of 5" in incorrect, "knowledge incorrect path failed")
        correct = cdp.evaluate("(() => {const f=document.getElementById('dicddKnowledgeForm');f.querySelectorAll('input[data-correct=\"true\"]').forEach(x=>x.checked=true);f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return document.getElementById('dicddKnowledgeFeedback').textContent})()")
        require("5 of 5" in correct, "knowledge correct path failed")
        print("OK: scenario and knowledge empty, incorrect and correct paths")

        navigate(cdp, url, 390)
        cdp.evaluate("""(() => {
          localStorage.removeItem('fcr_cookie_consent_v2'); window.__fcrEvents=[]; window.gtag=(...args)=>window.__fcrEvents.push(args);
          const s=document.querySelector('[data-scenario-form]');s.querySelector('input[data-grade="best"]').checked=true;s.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
          const k=document.getElementById('dicddKnowledgeForm');k.querySelectorAll('input[data-correct="true"]').forEach(x=>x.checked=true);k.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
          document.getElementById('saveDicddPatterns').click(); return true;
        })()""")
        denied_export = wait_for_export(downloads, cdp)
        require(cdp.evaluate("window.__fcrEvents.length") == 0, "telemetry fired without consent")
        denied_export.unlink()

        navigate(cdp, url, 390)
        cdp.evaluate("""(() => {
          localStorage.setItem('fcr_cookie_consent_v2','accepted'); window.__fcrEvents=[]; window.gtag=(...args)=>window.__fcrEvents.push(args);
          const s=document.querySelectorAll('[data-scenario-form]')[1];s.querySelector('input[data-grade="best"]').checked=true;s.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
          const k=document.getElementById('dicddKnowledgeForm');k.querySelectorAll('input[data-correct="true"]').forEach(x=>x.checked=true);k.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
          document.getElementById('saveDicddPatterns').click(); return true;
        })()""")
        export_path = wait_for_export(downloads, cdp)
        events = cdp.evaluate("window.__fcrEvents")
        require([event[1] for event in events] == ["scenario_complete", "knowledge_check_complete", "card_export"], f"event sequence differs: {events}")
        expected = {
            "scenario_complete": {"guide_id", "scenario_id", "decision_grade"},
            "knowledge_check_complete": {"guide_id", "score", "total"},
            "card_export": {"guide_id", "export_type"},
        }
        for event in events:
            require(set(event[2]) == expected[event[1]], f"event fields differ: {event}")
        with Image.open(export_path) as image:
            require(image.format == "PNG" and image.size == (1200, 1510), "Canvas export dimensions differ")
            require(image.getbbox() is not None, "Canvas export is blank")
        print("OK: consent gate, event schemas and Canvas export")

        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 428)
        reduced = cdp.evaluate("(() => {const s=getComputedStyle(document.querySelector('.dicdd-action'));return {animation:s.animationDuration,transition:s.transitionDuration}})()")
        require(reduced == {"animation": "1e-05s", "transition": "1e-05s"}, f"reduced motion differs: {reduced}")

        navigate(cdp, url, 768)
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 2})
        zoom = page_metrics(cdp)
        require(zoom["scrollWidth"] <= zoom["clientWidth"] + 1, "200 percent zoom overflow")
        cdp.call("Emulation.setPageScaleFactor", {"pageScaleFactor": 1})
        cdp.evaluate("document.querySelectorAll('.dicdd-option span').forEach(x=>{x.style.fontSize='24px';x.textContent+=' Additional explanatory wording for text expansion verification.'})")
        expanded = page_metrics(cdp)
        require(expanded["scrollWidth"] <= expanded["clientWidth"] + 1, "text expansion overflow")
        print("OK: reduced motion, zoom and text expansion")

        cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
        navigate(cdp, url, 375)
        no_js = page_metrics(cdp)
        require(no_js["mainHeight"] > 6500 and no_js["sourceHeight"] > 250, "material content unavailable without JavaScript")
        static = cdp.evaluate("document.body.innerText.includes('The Green Tick Halo') && document.body.innerText.includes('Source, Application and Action reasoning') && document.body.innerText.includes('What Would Change Our Assessment') && document.body.innerText.includes('Sources and methodology')")
        require(static, "static reasoning missing without JavaScript")
        open_no_script_reasoning_by_keyboard(cdp)
        print("OK: JavaScript-disabled comprehension and native scenario reasoning")
        cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})
        print("PASS: Digital Identity CDD Intelligence Brief browser regression")
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
