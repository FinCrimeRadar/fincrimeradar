#!/usr/bin/env python3
"""Headless Chrome regression checks for Customer Risk Scores: What the Number Cannot Decide only.

The Chrome-for-testing harness (CDP client, quiet server, device-width emulation, key dispatch) is the one
the De-Risking Judgement Call suite already uses, imported rather than copied a fourth time. Extraction into a
shared helper is approved in docs/GUIDE_PRODUCTION_WORKFLOW.md section 12 for the next time that suite is touched.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_de_risking_judgement_call_browser import (  # noqa: E402
    CDP, CHROME_CANDIDATES, QuietHandler, QuietServer, dispatch_key, navigate, require,
)
from check_customer_risk_score_framework import EXPECTED_OPTION_GRADES, GRADE_LABELS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "customer-risk-score-decision-framework"
WIDTHS = (320, 375, 390, 428, 768, 1440)
DEVICE_WIDTHS = (320, 375, 390, 428, 768)
FORMS = (("newproduct", "newproduct-decision"), ("overridepattern", "overridepattern-decision"))
PAGE_ERROR_HOOK = """
  window.__crsErrors = [];
  window.addEventListener('error', e => window.__crsErrors.push(String(e.message)));
  window.addEventListener('unhandledrejection', e => window.__crsErrors.push(String(e.reason)));
  window.__crsLayoutShift = 0;
  new PerformanceObserver(list => {
    list.getEntries().forEach(entry => { if (!entry.hadRecentInput) window.__crsLayoutShift += entry.value; });
  }).observe({type: 'layout-shift', buffered: true});
"""


def local_variable_audit() -> None:
    """Every var(--x) in the guide's own CSS must be defined in the guide's own :root."""
    html = (ROOT / f"{SLUG}.html").read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)
    defined = set(re.findall(r"(--[\w-]+)\s*:", re.search(r":root\{([^}]*)\}", css).group(1)))
    used = set(re.findall(r"var\((--[\w-]+)", css))
    require(not used - defined, f"CSS variables used but not defined in the guide's own :root: {sorted(used - defined)}")
    require(not set(re.findall(r'style="[^"]*var\((--[\w-]+)', html)) - defined, "inline style variable not defined locally")
    print(f"OK: {len(used)} CSS variables used, all defined in the guide's own :root")


def page_metrics(cdp: CDP) -> dict[str, Any]:
    return cdp.evaluate("""(() => {
      const root = document.documentElement;
      const offenders = [...document.querySelectorAll('body *')].filter(el => {
        const style = getComputedStyle(el), rect = el.getBoundingClientRect();
        return style.position !== 'fixed' && rect.width > 0 && (rect.left < -1 || rect.right > root.clientWidth + 1);
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, cls: typeof el.className === 'string' ? el.className : ''}));
      const clipped = [...document.querySelectorAll('#main-content *')].filter(el => {
        const style = getComputedStyle(el);
        return el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 1 && style.overflowX !== 'auto' && style.overflowX !== 'scroll';
      }).slice(0, 8).map(el => ({tag: el.tagName, id: el.id, cls: typeof el.className === 'string' ? el.className : '',
        client: el.clientWidth, scroll: el.scrollWidth}));
      return {clientWidth: root.clientWidth, scrollWidth: root.scrollWidth,
        mainHeight: document.getElementById('main-content').getBoundingClientRect().height,
        forms: document.querySelectorAll('[data-decision-form]').length, offenders, clipped,
        errors: window.__crsErrors || []};
    })()""")


def check_component_isolation(cdp: CDP, width: int) -> None:
    """Computed styles of the page's own components, so a global brand.css or brand.js rule cannot silently win."""
    r = cdp.evaluate("""(() => {
      const cs = (sel, prop) => { const el = document.querySelector(sel); return el ? getComputedStyle(el)[prop] : null; };
      const chainLi = document.querySelector('.crs-chain > li');
      const after = chainLi ? getComputedStyle(chainLi, '::after').content : null;
      const cols = el => el ? getComputedStyle(el).gridTemplateColumns.split(' ').length : 0;
      return {
        actionBg: cs('.crs-action', 'backgroundColor'), actionWeight: cs('.crs-action', 'fontWeight'),
        actionMinHeight: cs('.crs-action', 'minHeight'),
        h2Font: cs('.crs-section h2', 'fontFamily'), olStyle: cs('.crs-chain', 'listStyleType'),
        stepsDisplay: cs('.crs-steps', 'display'), canDisplay: cs('.crs-can', 'display'),
        canCols: cols(document.querySelector('.crs-can')), contrastCols: cols(document.querySelector('.crs-contrast')),
        figureMargin: cs('.crs-fig', 'marginLeft'), summaryCursor: cs('.crs-details summary', 'cursor'),
        layerOffset: cs('.crs-layers > li:nth-child(5)', 'marginLeft'), arrow: after,
        stateBorder: cs('.crs-state[data-state="unknown"]', 'borderTopColor'),
        outsideStyle: cs('.crs-outside', 'borderTopStyle'), tocPosition: cs('.crs-toc', 'position')
      };
    })()""")
    require(r["actionBg"] == "rgb(15, 118, 110)" and int(r["actionWeight"]) >= 700, f"{width}px action button style was overridden: {r}")
    require(float(r["actionMinHeight"].replace("px", "")) >= 44, f"{width}px action button is below a 44px target: {r}")
    require("Playfair" in r["h2Font"], f"{width}px section heading font was overridden: {r}")
    require(r["olStyle"] == "none" and r["stepsDisplay"] == "grid" and r["canDisplay"] == "grid", f"{width}px list or grid reset failed: {r}")
    require(r["figureMargin"] == "0px", f"{width}px figure kept a browser margin: {r}")
    require(r["outsideStyle"] == "dashed", f"{width}px outside-the-arithmetic band lost its dashed border: {r}")
    require(r["arrow"] in ('"↓"', '"↓"'), f"{width}px chain connector arrow missing: {r}")
    expected_cols = 1 if width <= 640 else 2
    require(r["canCols"] == expected_cols and r["contrastCols"] == expected_cols, f"{width}px can/cannot and contrast columns should be {expected_cols}: {r}")
    if width <= 360:
        require(r["layerOffset"] == "0px", f"{width}px layer offsets must flatten on the narrowest screens: {r}")
    require(r["tocPosition"] == ("sticky" if width > 900 else "static"), f"{width}px contents rail position wrong: {r}")


def complete_form_by_keyboard(cdp: CDP, scenario_id: str, radio_name: str) -> None:
    for _ in range(260):
        dispatch_key(cdp, "Tab", "Tab", 9)
        if cdp.evaluate("document.activeElement && document.activeElement.name") == radio_name:
            break
    else:
        raise AssertionError(f"keyboard could not reach {scenario_id} decision group")
    focus_style = cdp.evaluate("getComputedStyle(document.activeElement.closest('.crs-option')).outlineStyle")
    require(focus_style != "none", f"{scenario_id} keyboard focus indicator is not visible")
    for _ in range(6):
        if cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] input[data-grade=\"best\"]').checked"):
            break
        dispatch_key(cdp, "ArrowDown", "ArrowDown", 40)
    else:
        raise AssertionError(f"keyboard could not select the {scenario_id} best option")
    dispatch_key(cdp, "Tab", "Tab", 9)
    require(cdp.evaluate(f"document.activeElement === document.querySelector('[data-scenario-id=\"{scenario_id}\"] .crs-action')"),
            f"keyboard could not reach {scenario_id} submit control")
    dispatch_key(cdp, "Enter", "Enter", 13, "\r")
    feedback = cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .crs-feedback').textContent")
    require(feedback.startswith("Recorded:"), f"{scenario_id} keyboard feedback failed: {feedback!r}")
    state = cdp.evaluate(f"document.querySelector('[data-scenario-id=\"{scenario_id}\"] .crs-feedback').dataset.state")
    require(state == "best", f"{scenario_id} feedback state is {state!r}")


def check_reveal_and_change(cdp: CDP) -> None:
    result = cdp.evaluate("""(() => {
      const out = [];
      document.querySelectorAll('[data-decision-form]').forEach(form => {
        const sec = form.closest('.crs-section'), set = sec.querySelector('.crs-optfb-set');
        const before = getComputedStyle(set).display, buttonBefore = getComputedStyle(form.querySelector('.crs-action')).display;
        const radios = [...form.querySelectorAll('input[type=radio]')], pick = radios.find(r => r.dataset.grade === 'best');
        pick.checked = true; form.dispatchEvent(new Event('change', {bubbles: true}));
        const stillHidden = getComputedStyle(set).display;
        form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        const blocks = [...set.querySelectorAll('.crs-optfb')];
        const link = form.querySelector('.crs-feedback a');
        const target = blocks.find(b => b.dataset.option === pick.value);
        let focused = null; if (link) { link.click(); focused = document.activeElement && document.activeElement.id; }
        const result = {sid: form.dataset.scenarioId, before, buttonBefore, stillHidden, after: getComputedStyle(set).display,
          blocks: blocks.length, visible: blocks.filter(b => b.getBoundingClientRect().height > 0).length,
          marked: blocks.filter(b => b.dataset.selected === 'true').length,
          focusOk: Boolean(target) && focused === target.id && link.getAttribute('href') === '#' + target.id};
        radios.find(r => r !== pick).checked = true; form.dispatchEvent(new Event('change', {bubbles: true}));
        const fb = form.querySelector('.crs-feedback');
        result.cleared = [fb.textContent, fb.getAttribute('data-state'), form.querySelectorAll('.crs-option[data-selected]').length,
                          set.querySelectorAll('.crs-optfb[data-selected]').length];
        out.push(result);
      });
      return out; })()""")
    for item in result:
        sid = item["sid"]
        require(item["before"] == "none" and item["stillHidden"] == "none", f"{sid} analyses must stay hidden until Record with script on: {item}")
        require(item["buttonBefore"] != "none", f"{sid} Record button must show with script on")
        require(item["after"] != "none" and item["visible"] == item["blocks"] == 4 and item["marked"] == 1, f"{sid} Record must reveal four analyses and mark one: {item}")
        require(item["focusOk"], f"{sid} feedback link must lead to and focus the chosen analysis: {item}")
        require(item["cleared"] == ["", None, 0, 0], f"{sid} a change after Record must clear the verdict: {item}")
    print("OK: analyses hidden until Record, revealed with the choice marked, focus link works, change clears the verdict")


def check_every_option_feedback(cdp: CDP) -> None:
    """Every option of both scenarios records the grade and label the contract expects."""
    result = cdp.evaluate("""(() => {
      const out = {};
      document.querySelectorAll('[data-decision-form]').forEach(form => {
        out[form.dataset.scenarioId] = {};
        form.querySelectorAll('input[type=radio]').forEach(radio => {
          radio.checked = true; form.dispatchEvent(new Event('change', {bubbles: true}));
          form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
          const fb = form.querySelector('.crs-feedback');
          out[form.dataset.scenarioId][radio.value] = [radio.dataset.grade, fb.dataset.state, fb.textContent.startsWith('Recorded: ' + radio.dataset.gradeLabel)];
        });
        form.querySelectorAll('input[type=radio]').forEach(r => { r.checked = false; });
        form.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
        out[form.dataset.scenarioId].__none = form.querySelector('.crs-feedback').dataset.state;
      });
      return out; })()""")
    for key, options in EXPECTED_OPTION_GRADES.items():
        for value, grade in options.items():
            require(result[key][value] == [grade, grade, True], f"{key}/{value} recorded {result[key][value]}, expected grade {grade}")
        require(result[key]["__none"] == "caution", f"{key} submitting with nothing chosen must give the caution state")
    for key, options in EXPECTED_OPTION_GRADES.items():
        for grade in options.values():
            require(grade in GRADE_LABELS, "grade outside the label contract")
    print("OK: all eight options record their contract grade and label, an empty submit asks for a choice")


def check_quiz(cdp: CDP) -> None:
    result = cdp.evaluate("""(() => {
      const f = document.getElementById('knowledgeForm'), fb = document.getElementById('knowledgeFeedback'), out = {};
      const clear = () => f.querySelectorAll('input').forEach(i => { i.checked = false; });
      const submit = () => f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      clear(); f.querySelector('input[name=q1]').checked = true; submit(); out.partial = [fb.textContent, fb.dataset.state];
      clear(); f.querySelectorAll('input[data-correct="true"]').forEach(i => { i.checked = true; }); submit(); out.allCorrect = [fb.textContent.slice(0, 15), fb.dataset.state];
      f.dispatchEvent(new Event('change', {bubbles: true})); out.afterChange = [fb.textContent, fb.getAttribute('data-state')];
      for (const pos of [0, 1, 2]) {
        clear();
        ['q1','q2','q3','q4','q5'].forEach(q => { f.querySelectorAll('input[name=' + q + ']')[pos].checked = true; });
        submit(); out['pos' + pos] = [fb.textContent.slice(0, 14), fb.dataset.state];
      }
      clear();
      ['q1','q2','q3','q4','q5'].forEach(q => { const o = [...f.querySelectorAll('input[name=' + q + ']')].find(i => i.dataset.correct !== 'true'); o.checked = true; });
      submit(); out.allWrong = [fb.textContent.slice(0, 14), fb.dataset.state];
      return out; })()""")
    require(result["partial"] == ["Answer all five questions before scoring.", "caution"], f"incomplete quiz: {result['partial']}")
    require(result["allCorrect"] == ["Score: 5 of 5. ", "best"], f"all correct: {result['allCorrect']}")
    require(result["afterChange"] == ["", None], "a quiz change must clear the score")
    for pos in ("pos0", "pos1", "pos2"):
        require(result[pos][1] != "best", f"choosing one position everywhere must not score best: {result}")
    require(result["allWrong"][0].startswith("Score: 0 of 5") and result["allWrong"][1] == "caution", f"all wrong: {result['allWrong']}")
    print("OK: quiz scores 5 of 5, rejects an incomplete form, guessing a position never scores best, a change clears the score")


def check_telemetry(cdp: CDP) -> None:
    result = cdp.evaluate("""(() => {
      window.__ev = [];
      window.gtag = (...a) => window.__ev.push(a);
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      const f = document.querySelector('[data-scenario-id="newproduct"]');
      const submit = () => f.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      f.querySelector('input[data-grade="best"]').checked = true; submit(); submit();
      f.querySelector('input[data-grade="unsupported"]').checked = true; submit();
      const scenarioEvents = window.__ev.length;
      const k = document.getElementById('knowledgeForm');
      k.querySelectorAll('input[data-correct="true"]').forEach(i => { i.checked = true; });
      k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true})); k.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const total = window.__ev.length;
      localStorage.removeItem('fcr_cookie_consent_v2');
      const o = document.querySelector('[data-scenario-id="overridepattern"]');
      o.querySelector('input[data-grade="best"]').checked = true;
      o.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const noConsent = window.__ev.length;
      localStorage.setItem('fcr_cookie_consent_v2', 'accepted');
      o.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true})); o.dispatchEvent(new Event('submit', {bubbles: true, cancelable: true}));
      const afterConsent = window.__ev.length;
      const names = window.__ev.map(e => e[1]); const params = window.__ev.map(e => Object.keys(e[2]).sort().join(','));
      window.gtag = () => { throw new Error('analytics down'); };
      const x = document.querySelector('[data-scenario-id="newproduct"]'); window.__errsBefore = (window.__crsErrors || []).length;
      return {scenarioEvents, total, noConsent, afterConsent, names, params, errs: (window.__crsErrors || []).length - window.__errsBefore}; })()""")
    require(result["scenarioEvents"] == 1, f"repeated Record must send one scenario event: {result}")
    require(result["total"] == 2, f"repeated scoring must send one knowledge event: {result}")
    require(result["noConsent"] == 2, f"nothing may be sent without consent: {result}")
    require(result["afterConsent"] == 3, f"the event must send once after consent is given: {result}")
    require(result["names"] == ["scenario_complete", "knowledge_check_complete", "scenario_complete"], f"unexpected events: {result['names']}")
    require(result["params"][0] == "decision_grade,guide_id,scenario_id" and result["params"][1] == "guide_id,score,total", f"event parameters differ: {result['params']}")
    print("OK: telemetry once per key per page load, consent respected, aggregate parameters only")


def check_export(cdp: CDP, downloads: Path) -> None:
    for old in downloads.glob("*"):
        old.unlink()
    cdp.evaluate("document.getElementById('saveFrameworkImage').click()")
    target = downloads / f"{SLUG}-summary.png"
    for _ in range(80):
        if target.exists() and not list(downloads.glob("*.crdownload")):
            break
        time.sleep(0.15)
    require(target.exists(), "the export did not download a PNG")
    require(cdp.evaluate("document.getElementById('saveFrameworkStatus').textContent") == "Summary image created.", "export status text missing")
    image = Image.open(target)
    require(image.format == "PNG" and image.width == 1200 and image.height > 1500, f"unexpected export size {image.size}")
    rgb = image.convert("RGB")
    require(rgb.getpixel((5, 5)) == (7, 29, 43), "export background colour is wrong")
    runs, start = [], None
    for y in range(rgb.height):
        white = rgb.getpixel((100, y)) == (255, 255, 255)
        if white and start is None:
            start = y
        if not white and start is not None:
            runs.append((start, y - 1))
            start = None
    # Header letters can also be pure white at x=100, so only runs tall enough to be a card surface count.
    runs = [run for run in runs if run[1] - run[0] > 100]
    require(len(runs) == 6, f"expected six card surfaces in the export, found {len(runs)}")
    for top, bottom in runs:
        last_text = top
        for y in range(top, bottom + 1):
            if any(rgb.getpixel((px, y)) != (255, 255, 255) for px in range(112, 1100, 3)):
                last_text = y
        require(8 <= bottom - last_text <= 40, f"card {top}-{bottom} spacing below its text is {bottom - last_text}px")
    header_ink = sum(1 for y in range(20, runs[0][0] - 10) for px in range(72, 1100, 6) if rgb.getpixel((px, y)) != (7, 29, 43))
    require(header_ink > 300, "the export header (label, wrapped title, subtitle) is blank")
    print(f"OK: export is a {image.width}x{image.height} PNG with six evenly spaced cards and a drawn header")


def check_no_script(cdp: CDP, url: str) -> None:
    cdp.call("Emulation.setScriptExecutionDisabled", {"value": True})
    navigate(cdp, url, 375)
    state = cdp.evaluate("""(() => ({
      jsClass: document.documentElement.classList.contains('js'),
      buttons: [...document.querySelectorAll('.crs-choice .crs-action, #knowledgeForm .crs-action, #saveFrameworkImage')].map(b => getComputedStyle(b).display),
      sets: [...document.querySelectorAll('.crs-optfb-set')].map(s => [getComputedStyle(s).display, s.getBoundingClientRect().height > 100]),
      blocks: [...document.querySelectorAll('.crs-optfb')].filter(b => b.getBoundingClientRect().height > 0).length,
      text: document.getElementById('main-content').innerText.length,
      figures: [...document.querySelectorAll('.crs-fig')].map(f => f.getBoundingClientRect().height > 100),
      href: location.href}))()""")
    require(state["jsClass"] is False, "the js class must not be set without the script")
    require(state["buttons"] and all(d == "none" for d in state["buttons"]), f"action buttons must be hidden without the script: {state['buttons']}")
    require(len(state["sets"]) == 2 and all(d != "none" and tall for d, tall in state["sets"]), f"analyses must be visible without the script: {state['sets']}")
    require(state["blocks"] == 8, f"all eight option analyses must be visible without the script: {state['blocks']}")
    require(all(state["figures"]) and len(state["figures"]) == 5 and state["text"] > 40_000, f"figures or reasoning missing without the script: {state['figures']}, {state['text']}")
    cdp.evaluate("document.forms[0].requestSubmit()")
    time.sleep(0.4)
    after = cdp.evaluate("({href: location.href, search: location.search})")
    require(after["search"] == "" and after["href"] == state["href"], f"a submit without the script must not navigate: {after}")
    cdp.call("Emulation.setScriptExecutionDisabled", {"value": False})
    print("OK: no script: buttons hidden, every analysis and all five figures readable, stray submit does not navigate")


class ProbeHandler(QuietHandler):
    """Serves the repository, and can swap the guide script for one that throws."""

    MODE = {"throw": False}

    def do_GET(self) -> None:
        if ProbeHandler.MODE["throw"] and self.path.split("?")[0] == f"/js/{SLUG}.js":
            body = b"throw new Error('probe: script failure');"
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def check_script_throws(cdp: CDP, url: str) -> None:
    """A script that fails before the js class is set leaves buttons hidden and every analysis visible."""
    ProbeHandler.MODE["throw"] = True
    try:
        navigate(cdp, url, 375)
        state = cdp.evaluate("""(() => ({js: document.documentElement.classList.contains('js'),
          buttons: [...document.querySelectorAll('.crs-choice .crs-action, #knowledgeForm .crs-action, #saveFrameworkImage')].map(b => getComputedStyle(b).display),
          blocks: [...document.querySelectorAll('.crs-optfb')].filter(b => b.getBoundingClientRect().height > 0).length}))()""")
    finally:
        ProbeHandler.MODE["throw"] = False
    require(state["js"] is False and all(d == "none" for d in state["buttons"]) and state["blocks"] == 8, f"failed script left the page unusable: {state}")
    print("OK: a script that throws leaves buttons hidden and every analysis visible")


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")
    local_variable_audit()

    server = QuietServer(("127.0.0.1", 0), lambda *args: ProbeHandler(*args, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site_port = server.server_address[1]
    debug_port = 9435
    profile = Path(tempfile.mkdtemp(prefix="crs-chrome-"))
    downloads = Path(tempfile.mkdtemp(prefix="crs-downloads-"))
    process = subprocess.Popen([
        str(chrome), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-background-networking",
        f"--remote-debugging-port={debug_port}", "--remote-allow-origins=*", f"--user-data-dir={profile}", "about:blank",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tracked_pid = process.pid

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
        cdp.call("Network.enable")
        cdp.call("Network.setCacheDisabled", {"cacheDisabled": True})
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": PAGE_ERROR_HOOK})

        url = f"http://127.0.0.1:{site_port}/{SLUG}.html"
        for width in WIDTHS:
            navigate(cdp, url, width)
            m = page_metrics(cdp)
            require(m["scrollWidth"] <= m["clientWidth"] + 1, f"{width}px page overflow: {m}")
            require(m["mainHeight"] > 8000, f"{width}px main content is unexpectedly short")
            require(m["forms"] == 2, f"{width}px decision forms missing")
            require(not m["offenders"], f"{width}px clipped or overflowing elements: {m['offenders']}")
            require(not m["clipped"], f"{width}px internally clipped content: {m['clipped']}")
            require(not m["errors"], f"{width}px page errors: {m['errors']}")
            require((cdp.evaluate("window.__crsLayoutShift || 0") or 0) <= 0.1, f"{width}px layout shift exceeded 0.1")
            check_component_isolation(cdp, width)
            print(f"OK: {width}px layout, no overflow, no page errors, components isolated")

        navigate(cdp, url, 1440)
        for width in DEVICE_WIDTHS:
            result = cdp.evaluate(f"""new Promise(resolve => {{
              const old = document.getElementById('__probe'); if (old) old.remove();
              const f = document.createElement('iframe'); f.id = '__probe';
              f.style.cssText = 'position:absolute;left:0;top:0;width:{width}px;height:900px;border:0';
              f.onload = () => setTimeout(() => {{
                const d = f.contentDocument, r = d.documentElement;
                const bad = [...d.querySelectorAll('#main-content *')].filter(el => {{
                  const s = f.contentWindow.getComputedStyle(el), b = el.getBoundingClientRect();
                  return s.position !== 'fixed' && b.width > 0 && (b.left < -1 || b.right > r.clientWidth + 1);
                }}).length;
                const small = [...d.querySelectorAll('#main-content .crs-chain h3, #main-content .crs-layers strong, #main-content .crs-steps strong')]
                  .filter(el => parseFloat(f.contentWindow.getComputedStyle(el).fontSize) < 14).length;
                resolve({{client: r.clientWidth, scroll: r.scrollWidth, bad, small, forms: d.querySelectorAll('[data-decision-form]').length}});
              }}, 400);
              f.src = '/{SLUG}.html'; document.body.appendChild(f);
            }})""", True)
            require(result["client"] <= width and result["scroll"] <= result["client"] + 1, f"iframe {width}px overflow: {result}")
            require(result["bad"] == 0 and result["small"] == 0 and result["forms"] == 2, f"iframe {width}px clipped content or tiny diagram text: {result}")
            print(f"OK: iframe device width {width}px, no horizontal overflow, diagram text stays readable")
        cdp.evaluate("document.getElementById('__probe') && document.getElementById('__probe').remove()")

        navigate(cdp, url, 390)
        dispatch_key(cdp, "Tab", "Tab", 9)
        skip = cdp.evaluate("""(() => { const l = document.activeElement;
          return {focused: l.classList.contains('crs-skip'), target: l.getAttribute('href'), visible: l.getBoundingClientRect().top >= 0}; })()""")
        require(skip == {"focused": True, "target": "#main-content", "visible": True}, f"skip link is not the first visible keyboard target: {skip}")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        require(cdp.evaluate("location.hash") == "#main-content", "skip link did not move to the main content")

        navigate(cdp, url, 390)
        check_reveal_and_change(cdp)
        navigate(cdp, url, 390)
        check_every_option_feedback(cdp)
        navigate(cdp, url, 390)
        for scenario_id, radio_name in FORMS:
            complete_form_by_keyboard(cdp, scenario_id, radio_name)
        print("OK: both decisions completed by keyboard alone, focus ring visible, feedback is a polite status")

        navigate(cdp, url, 390)
        cdp.evaluate("document.querySelector('#faq summary').focus()")
        require(cdp.evaluate("document.querySelector('#faq details').open") is False, "FAQ items must start closed")
        dispatch_key(cdp, "Enter", "Enter", 13, "\r")
        require(cdp.evaluate("document.querySelector('#faq details').open") is True, "FAQ details did not open by keyboard")
        dispatch_key(cdp, " ", "Space", 32, " ")
        require(cdp.evaluate("document.querySelector('#faq details').open") is False, "FAQ details did not close with the space key")
        require(cdp.evaluate("getComputedStyle(document.querySelector('#faq summary')).outlineStyle") != "none", "summary has no visible focus indicator")
        live = cdp.evaluate("[...document.querySelectorAll('.crs-feedback, #saveFrameworkStatus')].every(e => e.getAttribute('aria-live') === 'polite' && e.getAttribute('role') === 'status')")
        require(live is True, "verdict, quiz and export containers must be polite live regions")
        print("OK: FAQ is native details, every verdict container is a polite live region")

        navigate(cdp, url, 390)
        check_quiz(cdp)
        navigate(cdp, url, 390)
        check_telemetry(cdp)
        navigate(cdp, url, 1440)
        check_export(cdp, downloads)

        navigate(cdp, url, 390)
        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]})
        navigate(cdp, url, 390)
        motion = cdp.evaluate("""(() => ({scroll: getComputedStyle(document.documentElement).scrollBehavior,
          transition: getComputedStyle(document.querySelector('.crs-action')).transitionDuration}))()""")
        require(motion["scroll"] == "auto", f"reduced motion must disable smooth scrolling: {motion}")
        cdp.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "no-preference"}]})
        print("OK: reduced motion disables smooth scrolling")

        check_no_script(cdp, url)
        check_script_throws(cdp, url)
        print("OK: Customer Risk Scores browser regression passed")
    finally:
        try:
            process.terminate()
            process.wait(timeout=10)
        except Exception:
            # Only the PID this run started is ever signalled, never a process name.
            if process.pid == tracked_pid:
                process.kill()
        server.shutdown()
        shutil.rmtree(profile, ignore_errors=True)
        shutil.rmtree(downloads, ignore_errors=True)


if __name__ == "__main__":
    try:
        run()
    except (AssertionError, RuntimeError, TimeoutError) as error:
        print(f"FAIL: {error}")
        raise SystemExit(1)
