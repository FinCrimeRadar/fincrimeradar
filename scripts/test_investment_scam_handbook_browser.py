#!/usr/bin/env python3
"""Headless Chrome regression checks for the Investment Scam Investigation Handbook only.

Each check maps to one requirement in the guide's Requirement Coverage Matrix (R1 to R18) and is
added in the commit that implements that requirement. The browser launched here is tracked by PID
and only that PID is ever terminated.
"""

from __future__ import annotations

import json
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

ROOT = Path(__file__).resolve().parents[1]
SLUG = "investment-scam-investigation-handbook"
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)
WIDTHS = (320, 375, 390, 428, 768, 1440)
DEVICE_WIDTHS = (320, 375, 390, 428, 768)


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


BROWSER_CHECKS: list[tuple[str, Callable[[Context], None]]] = [
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
