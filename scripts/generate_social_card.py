#!/usr/bin/env python3
"""
Generates a guide's Open Graph / social card PNG from
scripts/social-card-template.html, per GUIDE_STANDARD.md's "Social card"
requirement (adopted 2026-09-06, see BACKLOG.md).

Usage:
  python scripts/generate_social_card.py <guide-slug> [--series "Stablecoin Series"] [--number "3"]
                                          [--title "..."] [--subtitle "..."]

<guide-slug> is the HTML filename without extension, e.g. stablecoin-financial-crime-guide.
If --title/--subtitle are omitted, they're extracted from the guide's own
<h1>X<br><em>Y</em></h1> markup. Output: <guide-slug>-social-card.png in the repo root,
standard OG dimensions (1200x630).

Browser process management: launches its own headless Chrome with a fresh
--user-data-dir and --remote-debugging-port, tracks that process's PID from
launch, and terminates only that tracked PID on exit (see docs/QUALITY_INCIDENTS.md
incident 10). Never kills Chrome by process name.
"""
import argparse
import base64
import json
import re
import subprocess
import sys
import time
import tempfile
import shutil
import os
from pathlib import Path

import requests
import websocket

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "scripts" / "social-card-template.html"
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    raise SystemExit("Chrome not found in known install locations.")


def extract_title_subtitle(guide_path):
    html = guide_path.read_text(encoding="utf-8")
    m = re.search(r"<h1>(.*?)<br>\s*<em>(.*?)</em></h1>", html, re.S)
    if not m:
        raise SystemExit(f"Could not extract <h1>X<br><em>Y</em></h1> from {guide_path.name}; pass --title/--subtitle explicitly.")
    title = re.sub(r"<.*?>", "", m.group(1)).strip().rstrip(":")
    subtitle = re.sub(r"<.*?>", "", m.group(2)).strip()
    return title, subtitle


def build_html(title, subtitle, series, number):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if series:
        label = series.upper() if not number else f"{series.upper()} \u00b7 GUIDE {number}"
        pill = f'<div class="pill">{label}</div>'
    else:
        pill = ""
    out = tpl.replace("{{SERIES_PILL}}", pill)
    out = out.replace("{{TITLE}}", title)
    out = out.replace("{{SUBTITLE}}", subtitle)
    return out


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=20)
        self.mid = 0

    def call(self, method, params=None, timeout=20):
        self.mid += 1
        mid = self.mid
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        self.ws.settimeout(timeout)
        start = time.time()
        while time.time() - start < timeout:
            raw = json.loads(self.ws.recv())
            if raw.get("id") == mid:
                return raw
        raise TimeoutError(method)


def render_card(html_path, out_png):
    port = 9411
    profile_dir = tempfile.mkdtemp(prefix="social-card-chrome-")
    chrome = find_chrome()
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         f"--remote-debugging-port={port}", "--remote-allow-origins=*",
         f"--user-data-dir={profile_dir}", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    tracked_pid = proc.pid  # the only PID this script is permitted to terminate
    try:
        # wait for CDP to come up
        for _ in range(40):
            try:
                requests.get(f"http://localhost:{port}/json/version", timeout=1)
                break
            except requests.exceptions.RequestException:
                time.sleep(0.25)
        else:
            raise RuntimeError("headless Chrome did not come up on the tracked PID")

        tab = requests.put(f"http://localhost:{port}/json/new?about:blank").json()
        cdp = CDP(tab["webSocketDebuggerUrl"])
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": 1200, "height": 630, "deviceScaleFactor": 1, "mobile": False
        })
        cdp.call("Page.navigate", {"url": html_path.as_uri()})
        time.sleep(1.2)
        # reposition subtitle below the (possibly wrapped) title, measured live
        cdp.call("Runtime.evaluate", {"expression": """
            (function(){
              var t = document.getElementById('cardTitle');
              var s = document.getElementById('cardSubtitle');
              var bodyTop = document.body.getBoundingClientRect().top;
              var titleBottom = t.getBoundingClientRect().bottom - bodyTop;
              s.style.top = (titleBottom + 28) + 'px';
            })()
        """})
        time.sleep(0.3)
        shot = cdp.call("Page.captureScreenshot", {"format": "png"})
        data = shot["result"]["data"]
        out_png.write_bytes(base64.b64decode(data))
        requests.get(f"http://localhost:{port}/json/close/{tab['id']}")
    finally:
        # Permitted cleanup: only the tracked PID this function itself launched.
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)


def compress_png(path, target_bytes=400_000):
    """Only quantizes if the full-colour PNG exceeds the working ceiling --
    quantizing a smooth gradient background unconditionally introduces
    visible banding for no size benefit once the image is already small."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.save(path, optimize=True)
    if path.stat().st_size <= target_bytes:
        return "full colour"
    for colors in (256, 192, 128, 96, 64):
        quant = im.quantize(colors=colors, method=Image.MAXCOVERAGE, dither=Image.NONE)
        quant.save(path, optimize=True)
        if path.stat().st_size <= target_bytes:
            return colors
    return colors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="guide filename without .html, e.g. stablecoin-financial-crime-guide")
    ap.add_argument("--series", default="")
    ap.add_argument("--number", default="")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    args = ap.parse_args()

    guide_path = REPO_ROOT / f"{args.slug}.html"
    if not guide_path.exists():
        raise SystemExit(f"{guide_path} not found")

    if args.title and args.subtitle:
        title, subtitle = args.title, args.subtitle
    else:
        title, subtitle = extract_title_subtitle(guide_path)

    html = build_html(title, subtitle, args.series, args.number)
    tmp_html = REPO_ROOT / "scripts" / f"_tmp_card_{args.slug}.html"
    tmp_html.write_text(html, encoding="utf-8")
    try:
        out_png = REPO_ROOT / f"{args.slug}-social-card.png"
        render_card(tmp_html, out_png)
        colors = compress_png(out_png)
        size_kb = out_png.stat().st_size / 1000
        print(f"{out_png.name}: {size_kb:.0f}KB ({colors}-color palette) -- title={title!r} subtitle={subtitle!r}")
    finally:
        tmp_html.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
