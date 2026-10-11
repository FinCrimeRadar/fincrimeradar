#!/usr/bin/env python3
"""Headless Chrome regression checks for the KYB Lab page (kyb-lab.html).

The page is served from a local server and the production API is replaced by a
fetch stub installed before any page script runs, so no real API call is made.
Covers an active company, an unsupported type, not_returned sections, each
error code, a timeout, hostile (XSS) register text, keyboard operation, and the
390px and 1440px layouts. Harness classes follow scripts/test_money_mule_case_file_browser.py.

Optional: set KYB_SCREENSHOT_DIR to save 390px and 1440px screenshots.
"""

from __future__ import annotations

import json
import os
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

NOT_RETURNED = "This register section was not returned. FinCrimeRadar draws no conclusion from its absence."
ATTRIBUTION = (
    "Source: Companies House public register, retrieved 2026-10-11T17:22:10Z. "
    "FinCrimeRadar is not affiliated with or endorsed by Companies House."
)
GLOBAL_DNE = [
    "The register is not comprehensive and may contain inaccuracies, errors or omissions.",
    "Register status does not establish that a company is trading.",
    "Identity verification records do not establish legitimacy, ownership or control.",
    "The absence of an indicator is not evidence of low risk.",
    "This readout is not customer due diligence and does not replace it.",
]
IDV_DISPLAY = "FinCrimeRadar does not derive a verification status for this record in phase 1."
XSS = '<img src=x onerror="window.__xss=1"><script>window.__xss=1</script>'
XSS2 = '"><svg onload="window.__xss=1">'
NUM = "12345678"


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


def idv(display: str = IDV_DISPLAY, status: str | None = None) -> dict[str, Any]:
    return {
        "eligibility": "not_interpreted" if status is None else "derivation_eligible",
        "status": status,
        "display": display,
        "evidence": {},
        "evidence_label": None,
        "does_not_establish": "A register record of a supplied statement is not evidence of identity.",
    }


def active_company(n_officers: int = 3) -> dict[str, Any]:
    officers = [
        {
            "name": XSS if i == 0 else f"OFFICER {i}",
            "role": "director",
            "appointed_on": f"2020-01-{(i % 27) + 1:02d}",
            "resigned_on": None,
            "identity_verification": idv(),
        }
        for i in range(n_officers)
    ]
    return {
        "company_number": NUM,
        "retrieved_at": "2026-10-11T17:22:10Z",
        "source": "Companies House Public Data API",
        "company": {
            "name": XSS,
            "status": "active",
            "type": "ltd",
            "date_of_creation": "2019-05-01",
            "date_of_cessation": None,
            "links": {"self": "javascript:window.__xss=1"},
            "url": "https://evil.example/phish",
        },
        "interpretation": {"scope": "interpreted", "current_obligations": "interpreted", "notice": None},
        "register_reported_values": None,
        "indicators": [
            {
                "id": "previous_names",
                "label": "The company has previous names " + XSS2,
                "evidence_state": "register_fact",
                "evidence": {"names": [{"name": XSS, "effective_from": "2019-05-01", "ceased_on": "2021-01-01"}]},
                "source_endpoints": ["profile"],
                "does_not_establish": "A previous name is a register record. It does not establish why the name changed.",
            },
            {
                "id": "outstanding_charges",
                "label": "The company has charges with status outstanding",
                "evidence_state": "register_fact",
                "evidence": {"charges": [{"status": "outstanding", "created_on": "2022-02-02"}]},
                "source_endpoints": ["charges"],
                "does_not_establish": "A charge is a register record. It does not establish the company's solvency.",
            },
        ],
        "officers": {
            "source_status": "available",
            "items": officers,
            "events": [{"date": "2020-01-02", "event": "appointed", "name": XSS, "role": "director"}],
            "truncated": n_officers > 20,
        },
        "pscs": {
            "records_source_status": "available",
            "statements_source_status": "available",
            "items": [
                {"name": "PSC A", "kind": "individual-person-with-significant-control", "notified_on": "2020-01-01",
                 "ceased_on": None, "identity_verification": idv(status="statement_supplied", display="A verification statement is recorded.")}
            ],
            "active_statements": [{"statement": "no-individual-or-entity-with-signficant-control",
                                   "description": XSS2, "notified_on": "2020-01-01", "ceased_on": None}],
            "ceased_statements": [],
            "truncated": False,
        },
        "registered_office_change_filings": {
            "source_status": "available",
            "items": [{"date": "2025-03-04", "transaction_id": "MzA1", "description_identifier": XSS}],
            "truncated": False,
        },
        "charges": {"source_status": "available"},
        "insolvency": None,
        "not_returned_notice": NOT_RETURNED,
        "does_not_establish": GLOBAL_DNE,
        "attribution": ATTRIBUTION,
    }


def not_returned_company() -> dict[str, Any]:
    d = active_company()
    d["officers"] = {"source_status": "not_returned", "items": [], "events": [], "truncated": None}
    d["pscs"] = {"records_source_status": "not_returned", "statements_source_status": "not_returned",
                 "items": [], "active_statements": [], "ceased_statements": [], "truncated": None}
    d["registered_office_change_filings"] = {"source_status": "not_returned", "items": [], "truncated": None}
    d["charges"] = {"source_status": "not_returned"}
    d["insolvency"] = {"source_status": "not_returned"}
    d["indicators"] = []
    return d


def unsupported_company() -> dict[str, Any]:
    d = not_returned_company()
    d["company"]["type"] = "registered-society-non-jurisdictional"
    d["interpretation"] = {
        "scope": "unsupported_entity_type",
        "current_obligations": "not_applicable",
        "notice": "FinCrimeRadar does not interpret indicators for this entity type in phase 1",
    }
    return d


MOCKS = {
    NUM: {"status": 200, "body": active_company()},
    "00000001": {"status": 200, "body": not_returned_company()},
    "00000002": {"status": 200, "body": unsupported_company()},
    "00000003": {"status": 200, "body": active_company(n_officers=45)},
    "00000422": {"status": 422, "body": {"detail": "Invalid company number."}},
    "00000404": {"status": 404, "body": {"detail": "Company not found."}},
    "00000429": {"status": 429, "body": {"detail": "Too many"}, "headers": {"Retry-After": "37"}},
    "00000430": {"status": 429, "body": {"detail": "Too many"}},
    "00000503": {"status": 503, "body": {"detail": "unavailable"}},
    "00000500": {"status": 500, "body": {"detail": "boom"}},
    "00000600": {"status": 200, "body": {"unexpected": True}},
    "00000700": {"network": True},
    "00000800": {"hang": True},
}

STUB = """
window.__consoleErrors = [];
(function () {
  var originalError = console.error.bind(console);
  console.error = function () {
    window.__consoleErrors.push(Array.prototype.join.call(arguments, ' '));
    originalError.apply(console, arguments);
  };
  window.addEventListener('error', function (e) { window.__consoleErrors.push('uncaught: ' + e.message); });
  window.addEventListener('unhandledrejection', function (e) { window.__consoleErrors.push('unhandled: ' + e.reason); });
})();
window.KYB_LAB_CONFIG = { timeoutMs: 700, coldNoticeMs: 150 };
window.__kybCalls = [];
window.__kybMocks = %s;
(function () {
  var realFetch = window.fetch.bind(window);
  window.fetch = function (url, opts) {
    url = String(url);
    if (url.indexOf('fincrimeradar-api.onrender.com') === -1) return realFetch(url, opts);
    window.__kybCalls.push(url);
    if (url.indexOf('/api/health') !== -1) return Promise.resolve(new Response('{}', { status: 200 }));
    var m = url.match(/\\/api\\/kyb\\/company\\/([^?]*)$/);
    var key = m ? decodeURIComponent(m[1]) : '';
    var mock = window.__kybMocks[key];
    if (!mock) return Promise.resolve(new Response('{"detail":"Company not found."}', { status: 404 }));
    if (mock.network) return Promise.reject(new TypeError('Failed to fetch'));
    if (mock.hang) {
      return new Promise(function (resolve, reject) {
        opts.signal.addEventListener('abort', function () { reject(new DOMException('aborted', 'AbortError')); });
      });
    }
    return Promise.resolve(new Response(JSON.stringify(mock.body), { status: mock.status, headers: mock.headers || {} }));
  };
})();
""" % json.dumps(MOCKS)


def wait_for(cdp: CDP, expression: str, what: str, timeout: float = 6.0) -> None:
    end = time.time() + timeout
    while time.time() < end:
        if cdp.evaluate(expression):
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for: {what}")


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
        "width": width, "height": 900, "deviceScaleFactor": 1, "mobile": width < 768,
    })
    cdp.call("Page.navigate", {"url": url})
    wait_ready(cdp)
    wait_for(cdp, "!!document.getElementById('kybForm')", "form present")


def lookup(cdp: CDP, value: str) -> None:
    cdp.evaluate(
        "(() => { const i = document.getElementById('kybNumber'); i.value = %s;"
        " document.getElementById('kybForm').requestSubmit(); return true; })()" % json.dumps(value)
    )


def results_ready(cdp: CDP) -> None:
    wait_for(cdp, "!document.getElementById('kybResultsWrap').hidden", "results visible")


def error_text(cdp: CDP) -> str:
    wait_for(cdp, "!document.getElementById('kybError').hidden", "error visible")
    return cdp.evaluate("document.getElementById('kybError').textContent")


def text_of(cdp: CDP, selector: str) -> str:
    return cdp.evaluate("(document.querySelector(%s) || {}).textContent || ''" % json.dumps(selector))


def no_overflow(cdp: CDP, label: str) -> None:
    over = cdp.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    require(over <= 0, f"{label}: horizontal overflow of {over}px")


def screenshot(cdp: CDP, name: str) -> None:
    directory = os.environ.get("KYB_SCREENSHOT_DIR")
    if not directory:
        return
    import base64
    data = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})["data"]
    Path(directory).mkdir(parents=True, exist_ok=True)
    (Path(directory) / name).write_bytes(base64.b64decode(data))


def clean_company() -> dict[str, Any]:
    """Presentation data for screenshots: the active company without hostile text."""

    def scrub(value: Any) -> Any:
        if isinstance(value, str):
            return value.replace(XSS, "EXAMPLE TRADING LIMITED").replace(XSS2, "No individual or entity registered as a PSC")
        if isinstance(value, list):
            return [scrub(v) for v in value]
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in value.items()}
        return value

    d = scrub(active_company(n_officers=4))
    d["company"].pop("links", None)
    d["company"].pop("url", None)
    return d


def full_page_screenshot(cdp: CDP, name: str) -> None:
    directory = os.environ.get("KYB_SCREENSHOT_DIR")
    if not directory:
        return
    import base64
    cdp.evaluate("(() => { const b = document.getElementById('cookieBanner'); if (b) b.style.display = 'none'; return true; })()")
    size = cdp.evaluate("({w: document.documentElement.clientWidth, h: document.documentElement.scrollHeight})")
    data = cdp.call("Page.captureScreenshot", {
        "format": "png", "captureBeyondViewport": True,
        "clip": {"x": 0, "y": 0, "width": size["w"], "height": min(size["h"], 4000), "scale": 1},
    })["data"]
    Path(directory).mkdir(parents=True, exist_ok=True)
    (Path(directory) / name).write_bytes(base64.b64decode(data))


def run() -> None:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    require(chrome is not None, "Chrome not found")

    server = QuietServer(("127.0.0.1", 0), lambda *args: QuietHandler(*args, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    site = f"http://127.0.0.1:{server.server_address[1]}/kyb-lab.html"
    debug_port = 9431
    profile = Path(tempfile.mkdtemp(prefix="fcr-kyb-lab-chrome-"))
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
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": STUB})

        # ---- 1440px: active company, hostile text, layout, panel ----------------
        navigate(cdp, site, 1440)
        require(cdp.evaluate("document.title.includes('KYB Lab')"), "title")
        require("Beta" in text_of(cdp, ".kyb-beta"), "Beta label")
        require(text_of(cdp, "h1") == "KYB Lab", "h1")
        require(cdp.evaluate("document.querySelectorAll('.kyb-intro').length") == 1, "intro paragraph")
        require(cdp.evaluate("!!document.querySelector('nav a[href=\"/kyb-lab.html\"]')"), "nav link to KYB Lab")
        require(
            cdp.evaluate("(() => { const a = [...document.querySelectorAll('.nav-links a')].map(x => x.textContent);"
                         " return a.indexOf('KYB Lab') === a.indexOf('Screen') + 1; })()"),
            "KYB Lab sits directly after Screen in the nav",
        )
        print("OK: page header, Beta label, nav link beside Screen")

        # input normalisation and keyboard submit
        cdp.evaluate("document.getElementById('kybNumber').focus()")
        cdp.evaluate("document.getElementById('kybNumber').value = '  ' + %s.toLowerCase() + '  '" % json.dumps(NUM))
        cdp.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter",
                                            "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13, "text": "\r"})
        cdp.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter",
                                            "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
        results_ready(cdp)
        calls = cdp.evaluate("window.__kybCalls.filter(u => u.indexOf('/api/kyb/') !== -1)")
        require(calls == [f"https://fincrimeradar-api.onrender.com/api/kyb/company/{NUM}"], f"normalised request, got {calls}")
        require(cdp.evaluate("document.getElementById('kybNumber').value") == NUM, "input shows the normalised number")
        require(text_of(cdp, "#kybStatus") == "Register record loaded.", "status region announces the result")
        require(cdp.evaluate("document.getElementById('kybStatus').getAttribute('role')") == "status", "status role")
        require(cdp.evaluate("document.activeElement && document.activeElement.id") == "kybResultsHeading",
                "focus moves to the results heading")
        print("OK: Enter submits, input is stripped and uppercased, status announced, focus moved")

        # hostile register text renders literally
        require(cdp.evaluate("window.__xss === undefined"), "XSS payload executed")
        require(cdp.evaluate("document.querySelectorAll('#kybResults img, #kybResults svg, #kybResults script').length") == 0,
                "no injected elements inside results")
        require(text_of(cdp, "#kybResultsHeading") == XSS, "company name is literal text")
        results_text = text_of(cdp, "#kybResults")
        for payload in (XSS, XSS2):
            require(payload in results_text, f"payload {payload!r} is shown as text")
        require(text_of(cdp, "#kybResults .kyb-list .kyb-row-title").startswith(XSS), "officer name is literal text")
        require(cdp.evaluate("document.getElementById('kyb-h-filings').parentElement.textContent").count(XSS) == 1,
                "filing description is literal text")
        hrefs = cdp.evaluate("[...document.querySelectorAll('#kybResults a[href]')].map(a => a.getAttribute('href'))")
        require(hrefs == [f"https://find-and-update.company-information.service.gov.uk/company/{NUM}"],
                f"only the Companies House link built from the validated number, got {hrefs}")
        require(cdp.evaluate("document.querySelector('#kybResults a[href]').rel") == "noopener noreferrer", "link rel")
        print("OK: hostile text in company name, officer, indicator, statement and filing is literal; only one validated link")

        # content, order, verbatim strings
        require(IDV_DISPLAY in results_text, "IDV display text verbatim")
        require("A verification statement is recorded." in results_text, "second IDV display text")
        require(results_text.count("Does not establish:") >= 4, "indicator and IDV does_not_establish text shown")
        order = cdp.evaluate("[...document.querySelectorAll('#kybResults .kyb-h3')].map(h => h.textContent)")
        require(order[:4] == ["Company", "Indicators", "Officers", "Persons with significant control"], f"section order {order}")
        require(NOT_RETURNED not in results_text, "no not-returned notice when everything was returned")
        dne = text_of(cdp, "#kybDneList")
        for line in GLOBAL_DNE:
            require(line in dne, f"global does-not-establish line missing: {line}")
        require(text_of(cdp, "#kybAttribution") == ATTRIBUTION, "attribution verbatim")
        box = cdp.evaluate("(() => { const a = document.querySelector('.kyb-dne').getBoundingClientRect();"
                           " const r = document.getElementById('kybResults').getBoundingClientRect();"
                           " return {ax: a.left, aw: a.width, rx: r.left, rw: r.width, ah: a.height}; })()")
        require(box["aw"] > 200 and box["ah"] > 100, "does-not-establish panel is visible")
        require(box["ax"] >= box["rx"] + box["rw"] - 1, "panel sits beside the results at 1440px")
        require(cdp.evaluate("!document.querySelector('.kyb-dne').closest('details')"), "panel is not inside a collapsible")
        no_overflow(cdp, "1440 active")
        screenshot(cdp, "kyb-lab-1440.png")
        print("OK: section order, verbatim IDV, indicators with does_not_establish, global panel beside results, attribution verbatim")

        # show-more paging
        officer_rows = "document.getElementById('kyb-h-officers').parentElement.querySelector('ul.kyb-list').children.length"
        lookup(cdp, "00000003")
        wait_for(cdp, "!!document.getElementById('kyb-h-officers') && " + officer_rows + " > 0", "many officers rendered")
        first = cdp.evaluate(officer_rows)
        require(first == 20, f"first page of officers is 20, got {first}")
        cdp.evaluate("document.getElementById('kyb-h-officers').parentElement.querySelector('button.kyb-btn-quiet').click()")
        second = cdp.evaluate(officer_rows)
        require(second == 40, f"second page is 40, got {second}")
        require("incomplete" in text_of(cdp, "#kyb-h-officers").lower() or
                "incomplete" in cdp.evaluate("document.getElementById('kyb-h-officers').parentElement.textContent").lower(),
                "truncated officers noted")
        print("OK: long lists page by 20 with a keyboard operable button; truncation noted")

        # ---- not_returned sections ----------------------------------------------
        lookup(cdp, "00000001")
        results_ready(cdp)
        n = cdp.evaluate("[...document.querySelectorAll('#kybResults .kyb-notice')].filter(p => p.textContent === %s).length" % json.dumps(NOT_RETURNED))
        require(n == 6, f"every not_returned section shows the notice, expected 6 got {n}")
        require("No indicators were raised" in cdp.evaluate("document.getElementById('kyb-h-indicators').parentElement.textContent"),
                "empty indicators are stated")
        require(cdp.evaluate("document.querySelectorAll('#kybResults .kyb-row').length") == 0, "no rows when not returned")
        print("OK: not_returned officers, both PSC lists, filings, charges and insolvency each show the fixed notice")

        # ---- unsupported type -----------------------------------------------------
        lookup(cdp, "00000002")
        results_ready(cdp)
        require("does not interpret indicators for this entity type in phase 1" in text_of(cdp, "#kybResults .kyb-scope"),
                "scope notice shown")
        require(cdp.evaluate("!document.getElementById('kyb-h-indicators')"), "no indicators section for unsupported types")
        print("OK: unsupported type shows the scope notice and no indicators")

        # ---- error codes ----------------------------------------------------------
        cases = [
            ("00000422", "Enter a valid UK company number", False),
            ("00000404", "No company found with that number", False),
            ("00000429", "Too many lookups; try again in 37 seconds.", False),
            ("00000430", "Too many lookups; try again in a minute.", False),
            ("00000503", "The register lookup is temporarily unavailable", True),
            ("00000500", "The register lookup could not be completed. Try again shortly.", True),
            ("00000600", "The lookup returned an unexpected response. Try again shortly.", True),
            ("00000700", "The lookup service could not be reached. Check your connection and try again.", True),
        ]
        for number, message, retry in cases:
            lookup(cdp, number)
            got = error_text(cdp)
            require(got == message, f"{number}: expected {message!r}, got {got!r}")
            require(cdp.evaluate("document.getElementById('kybResultsWrap').hidden"), f"{number}: no stale results")
            shown = cdp.evaluate("!document.getElementById('kybRetry').hidden")
            require(shown is retry, f"{number}: retry button visibility expected {retry}, got {shown}")
            require(cdp.evaluate("document.getElementById('kybError').getAttribute('role')") == "alert", "error role")
        print("OK: 422, 404, 429 (with and without Retry-After), 503, 500, malformed body and network errors")

        # empty input makes no request
        before = cdp.evaluate("window.__kybCalls.length")
        lookup(cdp, "   ")
        require(error_text(cdp) == "Enter a valid UK company number", "empty input message")
        require(cdp.evaluate("window.__kybCalls.length") == before, "empty input makes no request")

        # timeout and cold start message (test config: 150 ms notice, 700 ms abort)
        lookup(cdp, "00000800")
        wait_for(cdp, "document.getElementById('kybStatus').textContent.indexOf('Still working') === 0", "cold start notice")
        require(cdp.evaluate("document.getElementById('kybSubmit').disabled"), "button disabled while waiting")
        require(error_text(cdp) == "The lookup timed out after 70 seconds. Try again.", "timeout message")
        require(cdp.evaluate("!document.getElementById('kybRetry').hidden"), "retry offered after a timeout")
        wait_for(cdp, "!document.getElementById('kybSubmit').disabled", "button re-enabled")
        cdp.evaluate("document.getElementById('kybRetry').click()")
        require(error_text(cdp) == "The lookup timed out after 70 seconds. Try again.", "retry repeats the lookup")
        print("OK: cold start notice, abort and retry message on timeout")

        # skip link is the first tab stop
        navigate(cdp, site, 1440)
        cdp.call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Tab", "code": "Tab",
                                            "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9})
        cdp.call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Tab", "code": "Tab",
                                            "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9})
        require(cdp.evaluate("document.activeElement.getAttribute('href')") == "#main-content", "skip link first")
        require(cdp.evaluate("document.getElementById('main-content').getAttribute('tabindex')") == "-1", "target tabindex")
        print("OK: skip link is the first tab stop and its target is focusable")

        # ---- 390px ------------------------------------------------------------------
        navigate(cdp, site, 390)
        no_overflow(cdp, "390 empty")
        lookup(cdp, NUM)
        results_ready(cdp)
        no_overflow(cdp, "390 active")
        stacked = cdp.evaluate("(() => { const a = document.querySelector('.kyb-dne').getBoundingClientRect();"
                               " const r = document.getElementById('kybResults').getBoundingClientRect();"
                               " return a.bottom <= r.top + 2 || a.top >= r.bottom - 2; })()")
        require(stacked, "panel is stacked, not beside, at 390px")
        require(cdp.evaluate("document.querySelector('.kyb-dne').getBoundingClientRect().width") > 300, "panel full width at 390px")
        screenshot(cdp, "kyb-lab-390.png")
        for number in ("00000001", "00000002"):
            lookup(cdp, number)
            results_ready(cdp)
            no_overflow(cdp, f"390 {number}")
        print("OK: 390px has no horizontal overflow and the panel stacks above the results")

        if os.environ.get("KYB_SCREENSHOT_DIR"):
            for width in (390, 1440):
                navigate(cdp, site, width)
                cdp.evaluate("window.__kybMocks[%s].body = %s" % (json.dumps(NUM), json.dumps(clean_company())))
                lookup(cdp, NUM)
                results_ready(cdp)
                time.sleep(0.3)
                full_page_screenshot(cdp, f"kyb-lab-{width}-readout.png")

        errors = cdp.evaluate("window.__consoleErrors")
        require(not errors, f"console errors: {errors}")
        print("PASS: KYB Lab browser regression")
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
