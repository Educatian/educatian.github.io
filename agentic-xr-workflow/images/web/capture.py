"""Capture web reference screenshots for the Agentic XR workflow guide.

Captures:
- iwsdk.dev landing page (hero region)
- github.com/facebook/immersive-web-sdk repo card
- immersiveweb.dev support table

Run from agentic-xr-workflow/ directory:
  python images/web/capture.py
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUT = Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)

TARGETS = [
    ("iwsdk-dev.png", "https://iwsdk.dev",
     {"width": 1280, "height": 800}, 0),
    ("github-repo.png", "https://github.com/facebook/immersive-web-sdk",
     {"width": 1280, "height": 900}, 0),
    ("immersiveweb-support.png", "https://immersiveweb.dev/",
     {"width": 1280, "height": 1100}, 0),
    ("youtube-dilmer.png",
     "https://www.youtube.com/watch?v=bWxIF903t_I",
     {"width": 1280, "height": 800}, 1500),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for fname, url, viewport, settle_ms in TARGETS:
        try:
            ctx = browser.new_context(viewport=viewport, device_scale_factor=2)
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            if settle_ms:
                page.wait_for_timeout(settle_ms)
            # Hide YouTube cookie/auth dialogs if present
            if "youtube" in url:
                try:
                    page.evaluate("""() => {
                        document.querySelectorAll('tp-yt-paper-dialog, ytd-consent-bump-v2-lightbox, .ytp-pause-overlay').forEach(e => e.remove());
                    }""")
                except Exception:
                    pass
            path = OUT / fname
            page.screenshot(path=str(path), clip={
                "x": 0, "y": 0,
                "width": viewport["width"],
                "height": viewport["height"]
            })
            print(f"  {fname:<28} -> {path.stat().st_size/1024:.0f} KB")
            ctx.close()
        except Exception as e:
            print(f"  {fname:<28} FAILED: {e}")
    browser.close()
