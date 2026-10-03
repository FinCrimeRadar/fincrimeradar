#!/usr/bin/env python3
"""Headless Chrome regression checks for the Investment Scam Investigation Handbook only.

Each check maps to one requirement in the guide's Requirement Coverage Matrix (R1 to R18) and is
added in the commit that implements that requirement. The browser launched here is tracked by PID
and only that PID is ever terminated.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

import requests
import websocket
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = "investment-scam-investigation-handbook"
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)
DEVICE_WIDTHS = (320, 375, 390, 428, 768)


class QuietHandler(SimpleHTTPRequestHandler):
    """Serves the repository, and can swap the guide script for one that throws (the script failure probe)."""

    MODE = {"throw": False}

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        if QuietHandler.MODE["throw"] and self.path.split("?")[0] == f"/js/{SLUG}.js":
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


class Context:
    """Everything a check needs: the browser tab, the guide URL and the throwaway download folder."""

    def __init__(self, cdp: CDP, url: str, downloads: Path) -> None:
        self.cdp = cdp
        self.url = url
        self.downloads = downloads


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


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


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate("""(() => {
      const root = document.documentElement;
      // Visually hidden (clipped, absolutely positioned) containers are not on screen, so their children are skipped.
      const hidden = el => { const h = el.closest('thead'); return Boolean(h) && getComputedStyle(h).position === 'absolute'; };
      const offenders = [...document.querySelectorAll('body *')].filter(el => {
        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return !hidden(el) && style.position !== 'fixed' && style.position !== 'absolute' && rect.width > 0 &&
          (rect.left < -1 || rect.right > root.clientWidth + 1);
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: typeof el.className === 'string' ? el.className : ''}));
      const internalOverflows = [...document.querySelectorAll('#main-content *')].filter(el => {
        const style = getComputedStyle(el);
        return !hidden(el) && style.position !== 'absolute' && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 &&
          style.overflowX !== 'auto' && style.overflowX !== 'scroll';
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, className: typeof el.className === 'string' ? el.className : '',
        clientWidth: el.clientWidth, scrollWidth: el.scrollWidth}));
      return {
        clientWidth: root.clientWidth,
        scrollWidth: root.scrollWidth,
        mainHeight: document.getElementById('main-content').getBoundingClientRect().height,
        sourceVisible: document.getElementById('sources').getBoundingClientRect().height > 100,
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


def scroll_through(cdp: CDP) -> None:
    """brand.js reveals sections as they enter the viewport, so scroll the whole page once."""
    total = cdp.evaluate("document.documentElement.scrollHeight")
    for offset in range(0, total + 600, 500):
        cdp.evaluate(f"window.scrollTo(0, {offset})")
        time.sleep(0.12)
    time.sleep(1.2)
    cdp.evaluate("window.scrollTo(0, 0)")


# R8 -----------------------------------------------------------------------------------------------

def check_r8_layout(ctx: Context) -> None:
    """R8: the evidence table is usable at every device width with no page-level overflow."""
    for width in WIDTHS:
        navigate(ctx.cdp, ctx.url, width)
        metrics = page_metrics(ctx.cdp)
        require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{width}px page overflow: {metrics}")
        require(metrics["mainHeight"] > 3000, f"{width}px main content is unexpectedly short")
        require(metrics["sourceVisible"], f"{width}px source section is not rendered")
        require(not metrics["offenders"], f"{width}px clipped or overflowing elements: {metrics['offenders']}")
        require(not metrics["internalOverflows"], f"{width}px internally clipped content: {metrics['internalOverflows']}")
        table = ctx.cdp.evaluate("""(() => {
          const t = document.querySelector('.isi-evidence'), r = t.getBoundingClientRect(), root = document.documentElement;
          const rows = [...t.querySelectorAll('tbody tr')];
          const cells = [...t.querySelectorAll('tbody td')];
          const labelled = cells.filter(td => getComputedStyle(td, '::before').content !== 'none' && getComputedStyle(td, '::before').content !== 'normal');
          return {fits: r.left >= -1 && r.right <= root.clientWidth + 1, rows: rows.length, rowsVisible: rows.filter(x => x.getBoundingClientRect().height > 0).length,
                  cells: cells.length, labelled: labelled.length, stacked: getComputedStyle(rows[0]).display === 'block'};
        })()""")
        require(table["fits"] and table["rows"] == 8 and table["rowsVisible"] == 8, f"{width}px evidence table does not fit or lost rows: {table}")
        if width <= 760:
            require(table["stacked"] and table["labelled"] == table["cells"] == 24, f"{width}px stacked table lacks per-cell labels: {table}")
        else:
            require(not table["stacked"], f"{width}px table should keep its column layout: {table}")
        print(f"OK: {width}px evidence table fits, 8 rows, {'stacked with labels' if width <= 760 else 'columns'}")


def check_r8_device_frames(ctx: Context) -> None:
    """R8: the table also holds up inside real device-width frames."""
    navigate(ctx.cdp, ctx.url, 1440)
    for width in DEVICE_WIDTHS:
        result = ctx.cdp.evaluate(f"""new Promise(resolve => {{
          const old = document.getElementById('__probe'); if (old) old.remove();
          const f = document.createElement('iframe');
          f.id = '__probe'; f.style.cssText = 'position:absolute;left:0;top:0;width:{width}px;height:900px;border:0';
          f.onload = () => setTimeout(() => {{
            const d = f.contentDocument, r = d.documentElement;
            const bad = [...d.querySelectorAll('#main-content *')].filter(el => {{
              const s = f.contentWindow.getComputedStyle(el), b = el.getBoundingClientRect();
              return s.position !== 'fixed' && b.width > 0 && (b.left < -1 || b.right > r.clientWidth + 1);
            }}).length;
            resolve({{client: r.clientWidth, scroll: r.scrollWidth, bad, rows: d.querySelectorAll('.isi-evidence tbody tr').length}});
          }}, 400);
          f.src = '/{SLUG}.html';
          document.body.appendChild(f);
        }})""", True)
        require(result["client"] <= width, f"iframe {width}px width not applied: {result}")
        require(result["scroll"] <= result["client"] + 1, f"iframe {width}px horizontal overflow: {result}")
        require(result["bad"] == 0 and result["rows"] == 8, f"iframe {width}px clipped content or missing rows: {result}")
        print(f"OK: iframe device width {width}px, no horizontal overflow, 8 evidence rows")
    ctx.cdp.evaluate("document.getElementById('__probe') && document.getElementById('__probe').remove()")


def check_r8_zoom_reflow(ctx: Context) -> None:
    """R8: browser zoom reflow. 200 percent of a 1280px window is 640 CSS px, 400 percent is 320 CSS px."""
    for width, label in ((640, "200 percent"), (320, "400 percent")):
        navigate(ctx.cdp, ctx.url, width)
        metrics = page_metrics(ctx.cdp)
        require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"{label} zoom introduced page overflow: {metrics}")
        require(not metrics["offenders"] and not metrics["internalOverflows"], f"{label} zoom clipped content: {metrics}")
        print(f"OK: {label} zoom reflow, no page overflow")
    navigate(ctx.cdp, ctx.url, 375)
    ctx.cdp.evaluate("""document.querySelectorAll('.isi-evidence td, .isi-evidence th').forEach(el => {
      el.textContent += ' Additional explanatory wording added to test long text expansion in a narrow cell.';
    })""")
    expanded = page_metrics(ctx.cdp)
    require(expanded["scrollWidth"] <= expanded["clientWidth"] + 1, f"long text expansion introduced page overflow: {expanded}")
    print("OK: long text expansion in the evidence table, no page overflow")


def check_r8_no_script(ctx: Context) -> None:
    """R8: the whole evidence table is present and readable with JavaScript disabled."""
    ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
    try:
        navigate(ctx.cdp, ctx.url, 375)
        state = ctx.cdp.evaluate("""(() => {
          const rows = [...document.querySelectorAll('.isi-evidence tbody tr')];
          return {jsClass: document.documentElement.classList.contains('js'), rows: rows.length,
                  visible: rows.filter(r => r.getBoundingClientRect().height > 30).length,
                  text: document.querySelector('.isi-evidence').textContent.includes('Legitimacy or authorisation')};
        })()""")
        require(state["jsClass"] is False and state["rows"] == 8 and state["visible"] == 8 and state["text"],
                f"evidence table unavailable without JavaScript: {state}")
        print("OK: no script, all 8 evidence rows visible")
    finally:
        ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})


# R6 -----------------------------------------------------------------------------------------------

FORMS = (("clone-firm", "clone-firm-decision"), ("real-exchange", "real-exchange-decision"))
EXPECTED_OPTION_GRADES = {
    "clone-firm": {"a": "unsupported", "b": "best", "c": "unsupported", "d": "incomplete"},
    "real-exchange": {"a": "unsupported", "b": "best", "c": "incomplete", "d": "unsupported"},
}
GRADE_LABELS = {
    "best": "Best supported by the evidence",
    "incomplete": "Contains a true point, stops short",
    "unsupported": "Not supported by the evidence",
}


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
    for _ in range(300):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == radio_name:
            break
    else:
        raise AssertionError(f"keyboard could not reach the {scenario_id} decision group")
    for _ in range(6):
        if cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] input[data-grade=\"best\"]').checked"):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select the {scenario_id} best-graded option")
    dispatch_key(cdp, "Tab", "Tab", 9)
    focused = cdp.evaluate(f"document.activeElement === document.querySelector('[data-scenario-id=\"{scenario_id}\"] .isi-action')")
    require(focused, f"keyboard could not reach the {scenario_id} submit control")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    feedback = cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .isi-feedback').textContent")
    require(feedback.startswith("Recorded:"), f"{scenario_id} keyboard feedback failed: {feedback!r}")
    state = cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .isi-feedback').dataset.state")
    require(state == "best", f"{scenario_id} feedback state is {state!r}")
    marked = cdp.evaluate(
        f"document.querySelector('[data-scenario-id=\"{scenario_id}\"]').closest('.isi-section')"
        ".querySelectorAll('.isi-optfb[data-selected=\"true\"]').length")
    require(marked == 1, f"{scenario_id} should mark exactly one option analysis, marked {marked}")


def check_r6_keyboard(ctx: Context) -> None:
    """R6: both decisions work by keyboard alone and mark exactly one option analysis."""
    for scenario_id, radio_name in FORMS:
        navigate(ctx.cdp, ctx.url, 390)
        complete_form_by_keyboard(ctx.cdp, scenario_id, radio_name)
        print(f"OK: {scenario_id} decision by keyboard, one option analysis marked")


def check_r6_reveal_and_change(ctx: Context) -> None:
    """R6: with JavaScript on, analyses stay hidden until Record, then all four show with the choice marked."""
    navigate(ctx.cdp, ctx.url, 390)
    result = ctx.cdp.evaluate("""(() => {
      const out = [];
      document.querySelectorAll('[data-decision-form]').forEach(form => {
        const sec = form.closest('.isi-section');
        const set = sec.querySelector('.isi-optfb-set');
        const button = form.querySelector('.isi-action');
        const before = getComputedStyle(set).display;
        const buttonBefore = getComputedStyle(button).display;
        const radios = [...form.querySelectorAll('input[type=radio]')];
        const pick = radios.find(r => r.dataset.grade === 'best');
        pick.checked = true;
        form.dispatchEvent(new Event('change', {bubbles: true}));
        const stillHidden = getComputedStyle(set).display;
        form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        const after = getComputedStyle(set).display;
        const blocks = [...set.querySelectorAll('.isi-optfb')];
        const visible = blocks.filter(b => b.getBoundingClientRect().height > 0).length;
        const marked = blocks.filter(b => b.dataset.selected === 'true').map(b => b.dataset.option);
        const fb = form.querySelector('.isi-feedback');
        const link = fb.querySelector('a');
        const target = blocks.find(b => b.dataset.option === pick.value);
        const linkOk = Boolean(link) && link.getAttribute('href') === '#' + target.id;
        const state = fb.getAttribute('data-state');
        const live = fb.getAttribute('aria-live'), role = fb.getAttribute('role');
        const other = radios.find(r => r !== pick);
        other.checked = true;
        form.dispatchEvent(new Event('change', {bubbles: true}));
        out.push({sid: form.dataset.scenarioId, before, buttonBefore, stillHidden, after, blocks: blocks.length, visible, marked, linkOk, state, live, role,
          cleared: {text: fb.textContent, state: fb.getAttribute('data-state'), optionMarks: form.querySelectorAll('.isi-option[data-selected]').length,
                    blockMarks: set.querySelectorAll('.isi-optfb[data-selected]').length}});
      });
      return out; })()""")
    require(len(result) == 2, f"expected two decision forms, found {len(result)}")
    for item in result:
        sid = item["sid"]
        require(item["before"] == "none", f"{sid} analyses must be hidden before Record with JS on: {item}")
        require(item["buttonBefore"] != "none", f"{sid} Record button must be visible with JS on")
        require(item["stillHidden"] == "none", f"{sid} choosing an option must not reveal the analyses")
        require(item["after"] != "none" and item["visible"] == item["blocks"] == 4, f"{sid} Record must reveal all four analyses: {item}")
        require(item["marked"] == ["b"], f"{sid} the chosen analysis must be marked: {item}")
        require(item["linkOk"], f"{sid} feedback must link to the chosen analysis: {item}")
        require(item["state"] == "best" and item["live"] == "polite" and item["role"] == "status", f"{sid} verdict region semantics: {item}")
        cleared = item["cleared"]
        require(cleared["text"] == "" and cleared["state"] is None and cleared["optionMarks"] == 0 and cleared["blockMarks"] == 0,
                f"{sid} a change after Record must clear feedback, state and marks: {cleared}")
    print("OK: analyses hidden before Record, revealed with the choice marked, verdict region polite, change clears the verdict")


def check_r6_grade_contract(ctx: Context) -> None:
    """R6: every option carries its grade and label, and each scenario has exactly one best option."""
    navigate(ctx.cdp, ctx.url, 390)
    dom = ctx.cdp.evaluate("""(() => Object.fromEntries([...document.querySelectorAll('[data-decision-form]')].map(form => [
      form.dataset.scenarioId,
      Object.fromEntries([...form.querySelectorAll('input[type=radio]')].map(r => [r.value, [r.dataset.grade, r.dataset.gradeLabel]]))
    ])))()""")
    expected = {key: {value: [grade, GRADE_LABELS[grade]] for value, grade in options.items()} for key, options in EXPECTED_OPTION_GRADES.items()}
    require(dom == expected, f"option grades differ from the contract: {dom}")
    unknown = ctx.cdp.evaluate("""(() => {
      const form = document.querySelector('[data-scenario-id="clone-firm"]');
      const radio = form.querySelector('input[value="a"]'), fb = form.querySelector('.isi-feedback');
      radio.dataset.grade = '__proto__'; radio.checked = true;
      form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      return fb.getAttribute('data-state'); })()""")
    require(unknown is None, f"an unknown grade must not set the feedback state: {unknown!r}")
    print("OK: all 8 options carry their grade and label, unknown grade ignored")


def check_r6_empty_submit(ctx: Context) -> None:
    """R6: recording with nothing chosen asks for a choice instead of revealing anything."""
    navigate(ctx.cdp, ctx.url, 390)
    result = ctx.cdp.evaluate("""(() => {
      const form = document.querySelector('[data-scenario-id="real-exchange"]');
      form.querySelectorAll('input').forEach(i => i.checked = false);
      form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const set = form.closest('.isi-section').querySelector('.isi-optfb-set');
      return {text: form.querySelector('.isi-feedback').textContent, display: getComputedStyle(set).display}; })()""")
    require("Choose an option" in result["text"] and result["display"] == "none", f"empty submission must be rejected: {result}")
    print("OK: empty decision rejected without revealing analyses")


# R7 -----------------------------------------------------------------------------------------------

def check_r7_counterfactuals(ctx: Context) -> None:
    """R7: both counterfactuals are on screen without any interaction, and Record does not hide or move them."""
    navigate(ctx.cdp, ctx.url, 390)
    before = ctx.cdp.evaluate("""[...document.querySelectorAll('.isi-counterfactual')].map(c => ({
      id: c.id, display: getComputedStyle(c).display, height: c.getBoundingClientRect().height,
      afterAnalyses: Boolean(c.closest('.isi-section').querySelector('.isi-optfb-set').compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING)}))""")
    require([c["id"] for c in before] == ["counterfactual-clone-firm", "counterfactual-real-exchange"], f"counterfactuals found: {before}")
    require(all(c["display"] != "none" and c["height"] > 60 and c["afterAnalyses"] for c in before), f"counterfactuals must be visible and follow the analyses: {before}")
    ctx.cdp.evaluate("""document.querySelectorAll('[data-decision-form]').forEach(form => {
      form.querySelector('input[data-grade="best"]').checked = true;
      form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
    })""")
    after = ctx.cdp.evaluate("[...document.querySelectorAll('.isi-counterfactual')].map(c => getComputedStyle(c).display)")
    require(all(d != "none" for d in after), "Record must not hide a counterfactual")
    print("OK: both counterfactuals visible before and after Record, positioned after the option analyses")


# R9 -----------------------------------------------------------------------------------------------

def check_r9_cards_and_quiz(ctx: Context) -> None:
    """R9: five cards render, and the knowledge check scores right, wrong, unanswered and guessed paths correctly."""
    navigate(ctx.cdp, ctx.url, 390)
    cards = ctx.cdp.evaluate("""[...document.querySelectorAll('#isiClosingPatterns .isi-pattern')].map(c => ({
      lines: c.querySelectorAll('.isi-lines dt').length, height: c.getBoundingClientRect().height,
      columns: getComputedStyle(c.parentElement).gridTemplateColumns.split(' ').length}))""")
    require(len(cards) == 5 and all(c["lines"] == 3 and c["height"] > 100 for c in cards), f"five closing cards with three lines each expected: {cards}")
    require(all(c["columns"] == 1 for c in cards), f"cards must stack on a 390px screen: {cards}")
    inline = ctx.cdp.evaluate("""[...document.querySelectorAll('.isi-pattern-inline')].map(c => ({
      id: c.dataset.patternId, section: c.closest('.isi-section').id, lines: c.querySelectorAll('.isi-lines dt').length,
      height: c.getBoundingClientRect().height, display: getComputedStyle(c).display}))""")
    require(len(inline) == 5 and all(c["lines"] == 3 and c["height"] > 100 and c["display"] != "none" for c in inline), f"five inline cards expected: {inline}")
    require(sorted(c["id"] for c in inline) == sorted(["borrowed-badge", "screen-money", "scope-verdict", "waiting-room", "second-hook"]), f"inline card ids: {inline}")
    require({c["section"] for c in inline} <= {"streams", "three-decisions", "source-limits"}, f"inline cards must sit where the patterns are introduced: {inline}")
    result = ctx.cdp.evaluate("""(() => {
      const f = document.getElementById('knowledgeForm'), fb = document.getElementById('knowledgeFeedback');
      const submit = () => f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const out = {live: fb.getAttribute('aria-live'), role: fb.getAttribute('role')};
      f.querySelectorAll('input').forEach(i => i.checked = false); submit();
      out.unanswered = [fb.textContent, fb.dataset.state];
      f.querySelectorAll('fieldset').forEach(fs => { fs.querySelector('input:not([data-correct="true"])').checked = true; }); submit();
      out.wrong = [fb.textContent.slice(0, 16), fb.dataset.state];
      f.querySelectorAll('input[data-correct="true"]').forEach(i => i.checked = true); submit();
      out.right = [fb.textContent.slice(0, 16), fb.dataset.state];
      out.guess = {};
      for (const pos of [0, 1, 2]) {
        f.querySelectorAll('input').forEach(i => i.checked = false);
        ['q1','q2','q3','q4','q5'].forEach(q => { f.querySelectorAll('input[name=' + q + ']')[pos].checked = true; });
        submit(); out.guess[pos] = fb.dataset.state;
      }
      f.dispatchEvent(new Event('change', {bubbles: true}));
      out.afterChange = [fb.textContent, fb.getAttribute('data-state')];
      return out; })()""")
    require(result["live"] == "polite" and result["role"] == "status", f"knowledge feedback semantics: {result}")
    require("Answer all five" in result["unanswered"][0] and result["unanswered"][1] == "caution", f"unanswered path: {result}")
    require(result["wrong"] == ["Score: 0 of 5. T", "caution"], f"all-wrong path: {result}")
    require(result["right"] == ["Score: 5 of 5. T", "best"], f"all-right path: {result}")
    require(all(state != "best" for state in result["guess"].values()), f"choosing one position throughout must not score best: {result}")
    require(result["afterChange"] == ["", None], f"a change must clear the score: {result}")
    print("OK: five cards stack at 390px, knowledge check unanswered, wrong, right and guessed paths, change clears the score")


# R10 ----------------------------------------------------------------------------------------------

def check_r10_skip_link(ctx: Context) -> None:
    """R10: the skip link is the first stop, becomes visible, and moves focus into the main content."""
    navigate(ctx.cdp, ctx.url, 390)
    dispatch_key(ctx.cdp, "Tab", "Tab", 9)
    state = ctx.cdp.evaluate("""(() => { const a = document.activeElement;
      return {skip: a.classList.contains('isi-skip'), target: a.getAttribute('href'), visible: a.getBoundingClientRect().top >= 0}; })()""")
    require(state == {"skip": True, "target": "#main-content", "visible": True}, f"skip link is not the first visible keyboard stop: {state}")
    dispatch_key(ctx.cdp, "Enter", "Enter", 13, "\r")
    time.sleep(0.2)
    after = ctx.cdp.evaluate("({hash: location.hash, focusId: document.activeElement && document.activeElement.id})")
    require(after == {"hash": "#main-content", "focusId": "main-content"}, f"skip link did not move focus to the main content: {after}")
    print("OK: skip link first, visible on focus, moves focus to the main content")


def check_r10_faq_keyboard(ctx: Context) -> None:
    """R10: native FAQ disclosures open and close from the keyboard with Enter and Space."""
    navigate(ctx.cdp, ctx.url, 390)
    ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
    try:
        navigate(ctx.cdp, ctx.url, 390)
        for _ in range(400):
            dispatch_key(ctx.cdp, "Tab", "Tab", 9)
            if ctx.cdp.evaluate("document.activeElement && document.activeElement.tagName") == "SUMMARY":
                break
        else:
            raise AssertionError("keyboard could not reach an FAQ summary")
        require(ctx.cdp.evaluate("document.activeElement.parentElement.open") is False, "FAQ item should start closed")
        dispatch_key(ctx.cdp, "Enter", "Enter", 13, "\r")
        require(ctx.cdp.evaluate("document.activeElement.parentElement.open") is True, "Enter must open the FAQ item without JavaScript")
        dispatch_key(ctx.cdp, " ", "Space", 32, " ")
        require(ctx.cdp.evaluate("document.activeElement.parentElement.open") is False, "Space must close the FAQ item without JavaScript")
        dispatch_key(ctx.cdp, "Tab", "Tab", 9)
        require(ctx.cdp.evaluate("document.activeElement.tagName") == "SUMMARY", "Tab should move to the next FAQ summary")
    finally:
        ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})
    print("OK: FAQ opens with Enter, closes with Space and moves on with Tab, with scripts disabled")


def check_r10_tab_walk(ctx: Context) -> None:
    """R10: every keyboard stop shows a visible focus indicator, and each kind of control is reachable."""
    for width in (390, 1440):
        navigate(ctx.cdp, ctx.url, width)
        stops: list[dict[str, Any]] = []
        for _ in range(500):
            dispatch_key(ctx.cdp, "Tab", "Tab", 9)
            stop = ctx.cdp.evaluate("""(() => { const el = document.activeElement;
              if (!el || el === document.body) return null;
              const own = getComputedStyle(el);
              const wrap = el.matches('input[type=radio]') ? getComputedStyle(el.closest('.isi-option')) : null;
              const visible = s => s && s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2;
              return {tag: el.tagName, cls: typeof el.className === 'string' ? el.className : '', type: el.type || '', id: el.id,
                      text: (el.textContent || el.value || '').trim().slice(0, 40), indicator: visible(own) || visible(wrap)}; })()""")
            if stop is None:
                break
            stops.append(stop)
            if len(stops) > 1 and stop == stops[0]:
                break
        missing = [s for s in stops if not s["indicator"]]
        require(not missing, f"{width}px stops without a visible focus indicator: {missing[:3]}")
        kinds = {
            "skip": any("isi-skip" in s["cls"] for s in stops),
            "summary": sum(1 for s in stops if s["tag"] == "SUMMARY") >= 6,
            "record": sum(1 for s in stops if "isi-action" in s["cls"]) >= 3,
            "radio": sum(1 for s in stops if s["type"] == "radio") >= 7,
            "source link": any(s["tag"] == "A" and "teach" in s["text"].lower() or s["tag"] == "A" and s["text"].startswith("Financial") for s in stops),
        }
        if width == 390:
            kinds["menu"] = any(s["id"] == "navHamburger" for s in stops)
        failed = [k for k, ok in kinds.items() if not ok]
        require(not failed, f"{width}px these controls were not reached by keyboard: {failed} in {len(stops)} stops")
        print(f"OK: {width}px {len(stops)} keyboard stops, every one with a visible focus indicator")


# R11 ----------------------------------------------------------------------------------------------

def check_r11_reduced_motion(ctx: Context) -> None:
    """R11: with reduced motion requested, smooth scrolling and transitions are off."""
    ctx.cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
    try:
        navigate(ctx.cdp, ctx.url, 428)
        state = ctx.cdp.evaluate("""(() => ({
          scroll: getComputedStyle(document.documentElement).scrollBehavior,
          transitions: [...document.querySelectorAll('.isi-option, .isi-action, a')].every(el => parseFloat(getComputedStyle(el).transitionDuration) < 0.01),
          animations: [...document.querySelectorAll('body *')].every(el => parseFloat(getComputedStyle(el).animationDuration) < 0.01)
        }))()""")
        require(state == {"scroll": "auto", "transitions": True, "animations": True}, f"reduced motion not honoured: {state}")
    finally:
        ctx.cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "no-preference"}]})
    print("OK: reduced motion switches off smooth scrolling, transitions and animations")


def check_r11_touch_targets(ctx: Context) -> None:
    """R11: every control is at least 44 by 44 CSS pixels on a phone."""
    navigate(ctx.cdp, ctx.url, 390)
    small = ctx.cdp.evaluate("""[...document.querySelectorAll('.isi-action, .isi-option, .isi-details summary, .nav-hamburger')]
      .map(el => ({cls: el.className || el.tagName, rect: el.getBoundingClientRect()}))
      .filter(x => x.rect.width > 0 && (x.rect.height < 44 || x.rect.width < 44))
      .map(x => ({cls: x.cls, w: Math.round(x.rect.width), h: Math.round(x.rect.height)}))""")
    require(not small, f"controls smaller than 44px: {small[:5]}")
    count = ctx.cdp.evaluate("document.querySelectorAll('.isi-action, .isi-option, .isi-details summary, .nav-hamburger').length")
    require(count >= 30, f"expected at least 30 controls to measure, found {count}")
    print(f"OK: {count} controls measured, all at least 44 by 44 CSS pixels at 390px")


def settle_scroll(cdp: CDP, limit: float = 6.0) -> None:
    """Smooth scrolling is animated, so wait until the scroll position stops changing before measuring."""
    deadline = time.time() + limit
    last = None
    while time.time() < deadline:
        position = cdp.evaluate("window.scrollY")
        if position == last:
            return
        last = position
        time.sleep(0.06)


def check_r11_focus_not_obscured(ctx: Context) -> None:
    """R11: a keyboard stop is never hidden under the sticky navigation bar."""
    navigate(ctx.cdp, ctx.url, 1440)
    nav_bottom = ctx.cdp.evaluate("document.querySelector('nav').getBoundingClientRect().bottom")
    hidden = []
    for _ in range(140):
        dispatch_key(ctx.cdp, "Tab", "Tab", 9)
        settle_scroll(ctx.cdp)
        stop = ctx.cdp.evaluate("""(() => { const el = document.activeElement;
          if (!el || el === document.body || el.classList.contains('isi-skip') || el.closest('nav') || el.closest('.isi-toc') || el.closest('#site-footer')) return null;
          const r = el.closest('.isi-option') ? el.closest('.isi-option').getBoundingClientRect() : el.getBoundingClientRect();
          return {text: (el.textContent || el.name || '').trim().slice(0, 30), top: r.top, bottom: r.bottom}; })()""")
        if stop and (stop["top"] < nav_bottom - 1 or stop["bottom"] > 904):
            hidden.append(stop)
    require(not hidden, f"keyboard stops hidden by the sticky nav or off screen: {hidden[:3]}")
    print("OK: keyboard stops through the content stay below the sticky nav")


def luminance(rgb: list[float]) -> float:
    def channel(value: float) -> float:
        value /= 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def check_r11_contrast(ctx: Context) -> None:
    """R11: text and badge colours meet WCAG AA contrast against the background they are drawn on."""
    navigate(ctx.cdp, ctx.url, 1440)
    pairs = ctx.cdp.evaluate("""(() => {
      const parse = c => (c.match(/[\\d.]+/g) || []).map(Number);
      const bgOf = el => { for (let n = el; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor);
        if (c.length >= 3 && (c.length < 4 || c[3] > 0.9)) return c.slice(0, 3); } return [255, 255, 255]; };
      const samples = ['.isi-note', '.isi-illustrative', '.isi-scope dt', '.isi-action', '.isi-state[data-state="established"]', '.isi-state[data-state="assessment"]',
        '.isi-state[data-state="unknown"]', '.isi-grade[data-grade="best"]', '.isi-grade[data-grade="incomplete"]', '.isi-grade[data-grade="unsupported"]',
        '.isi-saa-block h4', '.isi-evidence thead th', '.isi-evidence tbody th', '.isi-lines dt', '.isi-metaphor', '.isi-optfb-head', '.isi-scenario-tag',
        '.isi-stream-no', '.isi-sources li', '.isi-core strong', '.isi-lede'];
      const out = samples.map(sel => { const el = document.querySelector(sel); if (!el) return {sel, missing: true};
        const cs = getComputedStyle(el); return {sel, fg: parse(cs.color).slice(0, 3), bg: bgOf(el), size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight)}; });
      const fb = document.querySelector('.isi-feedback');
      for (const state of ['best', 'incomplete', 'unsupported', 'caution']) { fb.dataset.state = state;
        const cs = getComputedStyle(fb); out.push({sel: 'feedback ' + state, fg: parse(cs.color).slice(0, 3), bg: bgOf(fb), size: parseFloat(cs.fontSize), weight: parseInt(cs.fontWeight)}); }
      return out; })()""")
    failures = []
    for pair in pairs:
        require(not pair.get("missing"), f"contrast sample not found: {pair['sel']}")
        l1, l2 = luminance(pair["fg"]), luminance(pair["bg"])
        ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        large = pair["size"] >= 24 or (pair["size"] >= 18.66 and pair["weight"] >= 700)
        if ratio < (3.0 if large else 4.5):
            failures.append((pair["sel"], round(ratio, 2)))
    require(not failures, f"contrast below WCAG AA: {failures}")
    print(f"OK: {len(pairs)} text and badge colours meet WCAG AA contrast")


def check_r11_live_regions(ctx: Context) -> None:
    """R11: every live region is polite and in the document from the start, so announcements are not lost."""
    navigate(ctx.cdp, ctx.url, 390)
    regions = ctx.cdp.evaluate("""[...document.querySelectorAll('[aria-live]')].map(el => ({live: el.getAttribute('aria-live'), role: el.getAttribute('role'),
      empty: el.textContent === '', id: el.id || (el.closest('form') && el.closest('form').dataset.scenarioId) || ''}))""")
    require(len(regions) == 4 and all(r["live"] == "polite" and r["role"] == "status" and r["empty"] for r in regions), f"live regions: {regions}")
    print("OK: four polite status regions present and empty at load")


# R13 ----------------------------------------------------------------------------------------------

def check_r13_knowledge_hub(ctx: Context) -> None:
    """R13: the live Knowledge Hub shows the card, counts it, and the Fraud filter keeps it."""
    base = ctx.url.rsplit("/", 1)[0]
    navigate(ctx.cdp, f"{base}/knowledge.html", 1440)
    state = ctx.cdp.evaluate(f"""(() => {{
      const card = document.querySelector('a.kh-article-card[href="/{SLUG}.html"]');
      return {{found: Boolean(card), visible: Boolean(card) && card.getBoundingClientRect().height > 0,
              hero: document.getElementById('khHeroCount').textContent, stat: document.getElementById('khStatGuides').textContent,
              cards: document.querySelectorAll('#khArticlesGrid .kh-article-card').length,
              read: card && card.querySelector('.kh-read').textContent, format: card && card.querySelector('.kh-format-label').textContent}};
    }})()""")
    require(state["found"] and state["visible"], f"Knowledge Hub card missing or hidden: {state}")
    require(state["hero"] == state["stat"] and state["read"] == "40 MIN" and state["format"] == "Guide", f"Knowledge Hub card details: {state}")
    navigate(ctx.cdp, f"{base}/knowledge.html?domain=fraud-detection", 1440)
    time.sleep(0.5)
    filtered = ctx.cdp.evaluate(f"""(() => {{ const c = document.querySelector('a.kh-article-card[href="/{SLUG}.html"]');
      return Boolean(c) && getComputedStyle(c).display !== 'none' && c.getBoundingClientRect().height > 0; }})()""")
    require(filtered, "the Fraud domain filter must keep the guide visible")
    print(f"OK: Knowledge Hub card visible, count {state['stat']} matches the hero, Fraud filter keeps it")


# R14 ----------------------------------------------------------------------------------------------

def check_export_layout(image: Image.Image) -> None:
    """Every white surface must end shortly after its last text row, so nothing is clipped or floating."""
    rgb = image.convert("RGB")
    x = 100
    runs = []
    start = None
    for y in range(rgb.height):
        white = rgb.getpixel((x, y)) == (255, 255, 255)
        if white and start is None:
            start = y
        if not white and start is not None:
            if y - 1 - start > 60:  # ignore white glyph strokes in the title
                runs.append((start, y - 1))
            start = None
    require(len(runs) == 6, f"expected the summary panel and five cards in the export, found {len(runs)} white surfaces")
    for top, bottom in runs:
        last_text = top
        for y in range(top, bottom + 1):
            if any(rgb.getpixel((px, y)) != (255, 255, 255) for px in range(112, 1100, 3)):
                last_text = y
        require(bottom - last_text <= 40, f"surface {top}-{bottom} has {bottom - last_text}px of empty space below its text")
        require(bottom - last_text >= 8, f"surface {top}-{bottom} text runs too close to the edge")


def check_r14_image_export(ctx: Context) -> None:
    """R14: Save as image downloads a 1200px PNG holding the summary panel and the five cards, with no clipped text."""
    navigate(ctx.cdp, ctx.url, 390)
    for stale in ctx.downloads.glob(f"{SLUG}-summary*.png"):
        stale.unlink()
    ctx.cdp.evaluate("document.getElementById('saveSummaryImage').click()")
    for _ in range(80):
        if ctx.cdp.evaluate("document.getElementById('saveSummaryStatus').textContent") == "Summary image created.":
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Canvas export did not complete")
    exported: list[Path] = []
    for _ in range(80):
        exported = list(ctx.downloads.glob(f"{SLUG}-summary*.png"))
        if exported and exported[0].stat().st_size > 0:
            break
        time.sleep(0.1)
    else:
        raise AssertionError("Canvas export file was not downloaded")
    time.sleep(0.2)
    with Image.open(exported[0]) as image:
        rendered = image.convert("RGB")
        require(image.format == "PNG" and rendered.width == 1200 and rendered.height > 1500, f"export is {image.format} {rendered.size}")
        require(rendered.getpixel((10, 10)) == (7, 29, 43), "export brand background is missing")
        require(rendered.getpixel((75, 190)) == (15, 118, 110), "export first block accent is missing")
        require(rendered.getpixel((100, 190)) == (255, 255, 255), "export first block surface is missing")
        check_export_layout(image)
    keep = os.environ.get("ISI_EXPORT_COPY")
    if keep:
        shutil.copyfile(exported[0], keep)
    require(ctx.cdp.evaluate("document.querySelectorAll('#saveSummaryStatus[role=\"status\"]').length") == 1, "export status semantics missing or duplicated")
    print(f"OK: exported summary image {rendered.width}x{rendered.height}, six surfaces, no clipped text, status region announced")


# R15 ----------------------------------------------------------------------------------------------

CONTROLS = ".isi-choice .isi-action, #knowledgeForm .isi-action, #saveSummaryImage"
COMPREHENSION_MARKERS = (
    "Legitimate Node Trap", "Source", "Application", "Action", "What would change the assessment", "One-screen summary",
    "Counterfactual: change one fact", "Answer notes", "Risk, Signal, Response", "Sources and methodology",
    "Best supported by the evidence", "Not supported by the evidence",
)


def static_state(ctx: Context) -> dict[str, Any]:
    return ctx.cdp.evaluate(f"""(() => {{
      const shown = el => el.getBoundingClientRect().height > 0 && getComputedStyle(el).display !== 'none' && getComputedStyle(el).visibility !== 'hidden';
      const text = document.body.textContent;
      return {{
        jsClass: document.documentElement.classList.contains('js'),
        controls: [...document.querySelectorAll('{CONTROLS}')].map(b => getComputedStyle(b).display),
        analyses: [...document.querySelectorAll('.isi-optfb')].filter(shown).length,
        counterfactuals: [...document.querySelectorAll('.isi-counterfactual')].filter(shown).length,
        evidenceRows: [...document.querySelectorAll('.isi-evidence tbody tr')].filter(shown).length,
        patterns: [...document.querySelectorAll('.isi-pattern')].filter(shown).length,
        summary: shown(document.getElementById('operational-summary')),
        sources: [...document.querySelectorAll('#sources li')].filter(shown).length,
        faq: document.querySelectorAll('#faq details').length,
        notes: document.querySelectorAll('.isi-answer-notes details p').length,
        mainHeight: document.getElementById('main-content').getBoundingClientRect().height,
        missing: {list(COMPREHENSION_MARKERS)!r}.filter(m => !text.includes(m)),
        href: location.href
      }};
    }})()""")


def require_static_state(state: dict[str, Any], label: str) -> None:
    require(state["jsClass"] is False, f"{label}: the js class must not be set")
    require(state["controls"] and all(d == "none" for d in state["controls"]), f"{label}: action buttons must be hidden: {state['controls']}")
    require(state["analyses"] == 8, f"{label}: all eight option analyses must be visible, found {state['analyses']}")
    require(state["counterfactuals"] == 2 and state["evidenceRows"] == 8 and state["patterns"] == 10, f"{label}: counterfactuals, evidence rows or cards missing: {state}")
    require(state["summary"] and state["sources"] == 8 and state["faq"] == 6 and state["notes"] == 5, f"{label}: summary, sources, FAQ or answer notes missing: {state}")
    require(state["mainHeight"] > 8000, f"{label}: the article is unexpectedly short: {state['mainHeight']}")
    require(not state["missing"], f"{label}: reasoning text missing: {state['missing']}")


def check_r15_no_script(ctx: Context) -> None:
    """R15: with scripts disabled every analysis, verdict explanation, citation and conclusion is on the page."""
    ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
    try:
        for width in (320, 375):
            navigate(ctx.cdp, ctx.url, width)
            state = static_state(ctx)
            require_static_state(state, f"no script {width}px")
            metrics = page_metrics(ctx.cdp)
            require(metrics["scrollWidth"] <= metrics["clientWidth"] + 1, f"no script {width}px page overflow: {metrics}")
        ctx.cdp.evaluate("document.forms[0].requestSubmit()")
        time.sleep(0.4)
        require(ctx.cdp.evaluate("location.href") == state["href"], "a submit without the script must not navigate or add the selection to the URL")
        print("OK: no script, 8 analyses, 2 counterfactuals, table, cards, summary, FAQ, answer notes and sources all visible, no navigation on submit")
    finally:
        ctx.cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})


def check_r15_script_throws(ctx: Context) -> None:
    """R15: a script that throws leaves the page in its fully readable no-script state."""
    QuietHandler.MODE["throw"] = True
    try:
        navigate(ctx.cdp, ctx.url, 375)
        state = static_state(ctx)
        require_static_state(state, "script throws")
        ctx.cdp.evaluate("document.forms[0].requestSubmit()")
        time.sleep(0.4)
        require(ctx.cdp.evaluate("location.href") == state["href"], "a submit after a script failure must not navigate")
    finally:
        QuietHandler.MODE["throw"] = False
    print("OK: script throws: no js class, buttons hidden, all analyses and reasoning visible, no navigation")


def check_r15_no_flash(ctx: Context) -> None:
    """R15: before the js class is set no action button is visible and no option analysis is on screen."""
    for width in (390, 1440):
        navigate(ctx.cdp, ctx.url, width)
        flash = ctx.cdp.evaluate("window.__isiFlash")
        require(flash is not None and flash["jsAt"] is not None, f"{width}px the js class was never set: {flash}")
        require(flash["buttons"] == 0 and flash["analysesInView"] == 0, f"{width}px flash before the js class: {flash}")
        print(f"OK: {width}px no visible flash before the js class ({flash['frames']} frames observed)")


# R16 ----------------------------------------------------------------------------------------------

def check_r16_consent_denied(ctx: Context) -> None:
    """R16: without consent nothing is sent for scenarios, the knowledge check or the image export."""
    navigate(ctx.cdp, ctx.url, 390)
    ctx.cdp.evaluate("""(() => {
      localStorage.removeItem('fcr_cookie_consent_v2');
      window.__ev = []; window.gtag = (...a) => window.__ev.push(a);
      document.querySelectorAll('[data-decision-form]').forEach(f => {
        f.querySelector('input[data-grade="best"]').checked = true;
        f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      });
      document.querySelectorAll('#knowledgeForm input[data-correct="true"]').forEach(i => i.checked = true);
      document.getElementById('knowledgeForm').dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      document.getElementById('saveSummaryImage').click();
    })()""")
    for _ in range(80):
        if ctx.cdp.evaluate("document.getElementById('saveSummaryStatus').textContent") == "Summary image created.":
            break
        time.sleep(0.1)
    else:
        raise AssertionError("export did not complete with consent denied")
    time.sleep(0.2)
    require(ctx.cdp.evaluate("window.__ev.length") == 0, "a telemetry family fired without consent")
    for stale in ctx.downloads.glob(f"{SLUG}-summary*.png"):
        stale.unlink()
    print("OK: consent denied, scenario, knowledge and export telemetry all stay silent")


def check_r16_consented_payloads(ctx: Context) -> None:
    """R16: with consent each event is aggregate only, identical whichever option was chosen, and sent once."""
    navigate(ctx.cdp, ctx.url, 390)
    result = ctx.cdp.evaluate("""(() => {
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      window.__ev = []; window.gtag = (...a) => window.__ev.push(a);
      const net = {fetch: 0, xhr: 0, beacon: 0, storage: 0};
      const f0 = window.fetch; window.fetch = (...a) => { net.fetch += 1; return f0.apply(window, a); };
      const x0 = XMLHttpRequest.prototype.send; XMLHttpRequest.prototype.send = function (...a) { net.xhr += 1; return x0.apply(this, a); };
      navigator.sendBeacon = () => { net.beacon += 1; return true; };
      const s0 = Storage.prototype.setItem; Storage.prototype.setItem = function (...a) { net.storage += 1; return s0.apply(this, a); };
      const submit = (form, value) => {
        form.querySelectorAll('input').forEach(i => i.checked = false);
        form.querySelector('input[value="' + value + '"]').checked = true;
        form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      };
      const clone = document.querySelector('[data-scenario-id="clone-firm"]');
      submit(clone, 'a'); submit(clone, 'b'); submit(clone, 'c');
      const afterRepeat = window.__ev.length;
      const exch = document.querySelector('[data-scenario-id="real-exchange"]');
      submit(exch, 'd');
      const k = document.getElementById('knowledgeForm');
      k.querySelectorAll('input[data-correct="true"]').forEach(i => i.checked = true);
      k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      return {events: window.__ev.map(e => [e[0], e[1], e[2]]), afterRepeat, net,
              fields: document.querySelectorAll('textarea, select, input:not([type=radio])').length};
    })()""")
    require(result["afterRepeat"] == 1, f"repeated Record must send one scenario event: {result}")
    names = [e[1] for e in result["events"]]
    require(names == ["scenario_complete", "scenario_complete", "knowledge_check_complete"], f"events sent: {names}")
    require(all(e[0] == "event" for e in result["events"]), f"only gtag events may be sent: {result['events']}")
    allowed = {"scenario_complete": {"guide_id", "scenario_id"}, "knowledge_check_complete": {"guide_id", "score", "total"}}
    for _, name, params in result["events"]:
        require(set(params) == allowed[name], f"{name} parameters are {sorted(params)}")
        require(params["guide_id"] == "investment_scam_investigation_handbook", f"guide id is {params['guide_id']}")
    require(result["events"][0][2] == {"guide_id": "investment_scam_investigation_handbook", "scenario_id": "clone-firm"}, "the chosen option must not appear in the event")
    require(result["events"][2][2]["score"] == 5 and result["events"][2][2]["total"] == 5, f"knowledge payload: {result['events'][2]}")
    require(result["net"] == {"fetch": 0, "xhr": 0, "beacon": 0, "storage": 0}, f"the guide made network or storage calls: {result['net']}")
    require(result["fields"] == 0, "the page must have no free-text, select or file controls")
    print("OK: consented events are aggregate only, identical whichever option is chosen, sent once, with no network or storage calls")


def check_r16_export_payload(ctx: Context) -> None:
    """R16: the image export event carries only the guide id and the export type."""
    navigate(ctx.cdp, ctx.url, 390)
    ctx.cdp.evaluate("""(() => { localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      window.__ev = []; window.gtag = (...a) => window.__ev.push(a); document.getElementById('saveSummaryImage').click(); })()""")
    for _ in range(80):
        if ctx.cdp.evaluate("window.__ev.length") == 1:
            break
        time.sleep(0.1)
    events = ctx.cdp.evaluate("window.__ev")
    require(events == [["event", "card_export", {"guide_id": "investment_scam_investigation_handbook", "export_type": "summary_and_patterns"}]], f"export event: {events}")
    for stale in ctx.downloads.glob(f"{SLUG}-summary*.png"):
        stale.unlink()
    print("OK: export event carries only the guide id and export type")


def check_r16_consent_timing_and_failure(ctx: Context) -> None:
    """R16: a send that did not happen does not use up the event, and a failing analytics call is contained."""
    navigate(ctx.cdp, ctx.url, 390)
    result = ctx.cdp.evaluate("""(() => {
      window.__ev = []; window.__errs = 0; window.addEventListener('error', () => { window.__errs += 1; });
      window.gtag = (...a) => window.__ev.push(a);
      localStorage.removeItem('fcr_cookie_consent_v2');
      const f = document.querySelector('[data-scenario-id="clone-firm"]');
      f.querySelector('input[value="b"]').checked = true;
      f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const none = window.__ev.length;
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const once = window.__ev.length;
      window.gtag = () => { throw new Error('analytics down'); };
      const g = document.querySelector('[data-scenario-id="real-exchange"]');
      g.querySelector('input[value="b"]').checked = true;
      g.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      return {none, once, errs: window.__errs, feedback: g.querySelector('.isi-feedback').textContent.startsWith('Recorded:')};
    })()""")
    require(result == {"none": 0, "once": 1, "errs": 0, "feedback": True}, f"consent timing or failure handling: {result}")
    print("OK: event sent once after consent is given, analytics failure contained")


BROWSER_CHECKS: list[tuple[str, Callable[[Context], None]]] = [
    ("R16", check_r16_consent_denied),
    ("R16", check_r16_consented_payloads),
    ("R16", check_r16_export_payload),
    ("R16", check_r16_consent_timing_and_failure),
    ("R15", check_r15_no_script),
    ("R15", check_r15_script_throws),
    ("R15", check_r15_no_flash),
    ("R14", check_r14_image_export),
    ("R13", check_r13_knowledge_hub),
    ("R11", check_r11_reduced_motion),
    ("R11", check_r11_touch_targets),
    ("R11", check_r11_focus_not_obscured),
    ("R11", check_r11_contrast),
    ("R11", check_r11_live_regions),
    ("R10", check_r10_skip_link),
    ("R10", check_r10_faq_keyboard),
    ("R10", check_r10_tab_walk),
    ("R9", check_r9_cards_and_quiz),
    ("R7", check_r7_counterfactuals),
    ("R6", check_r6_keyboard),
    ("R6", check_r6_reveal_and_change),
    ("R6", check_r6_grade_contract),
    ("R6", check_r6_empty_submit),
    ("R8", check_r8_layout),
    ("R8", check_r8_device_frames),
    ("R8", check_r8_zoom_reflow),
    ("R8", check_r8_no_script),
]


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    local_variable_audit()

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site_port = server.server_address[1]
    debug_port = free_port()
    profile = Path(tempfile.mkdtemp(prefix="fcr-isi-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="fcr-isi-downloads-"))
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
        cdp.call("Network.enable")
        cdp.call("Network.setCacheDisabled", {"cacheDisabled": True})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__isiFlash = {buttons: 0, analysesInView: 0, frames: 0, jsAt: null};
          (function loop() {
            const flash = window.__isiFlash;
            if (!document.documentElement) { requestAnimationFrame(loop); return; }
            if (document.documentElement.classList.contains('js')) { flash.jsAt = performance.now(); return; }
            flash.frames += 1;
            document.querySelectorAll('.isi-choice .isi-action, #knowledgeForm .isi-action, #saveSummaryImage').forEach(b => {
              if (getComputedStyle(b).display !== 'none') flash.buttons += 1;
            });
            document.querySelectorAll('.isi-optfb-set').forEach(set => {
              const r = set.getBoundingClientRect();
              if (getComputedStyle(set).display !== 'none' && r.height > 0 && r.top < window.innerHeight && r.bottom > 0) flash.analysesInView += 1;
            });
            requestAnimationFrame(loop);
          })();
        """})
        cdp.call("Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(downloads)})
        ctx = Context(cdp, f"http://127.0.0.1:{site_port}/{SLUG}.html", downloads)
        for _, check in BROWSER_CHECKS:
            check(ctx)
        print("PASS: Investment Scam Investigation Handbook browser regression")
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
