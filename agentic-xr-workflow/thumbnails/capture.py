"""Capture hero OG thumbnail (1200x630) and full-page screenshot for the
Agentic XR workflow guide. Run from the agentic-xr-workflow/ folder.

  python thumbnails/capture.py
"""
from playwright.sync_api import sync_playwright
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT = ROOT / "thumbnails"
OUT.mkdir(exist_ok=True)
URL = INDEX.as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch()
    # ---------- OG hero card 1200x630 ----------
    ctx = browser.new_context(viewport={"width": 1200, "height": 630},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL)
    # crop the hero region: scroll to top, ensure layout settled
    page.wait_for_load_state("networkidle")
    page.evaluate("window.scrollTo(0, 0)")
    # render only the hero by clipping
    page.screenshot(path=str(OUT / "hero_og_1200x630.png"),
                    clip={"x": 0, "y": 0, "width": 1200, "height": 630})
    ctx.close()

    # ---------- full page screenshot (desktop) ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    try:
        page.screenshot(path=str(OUT / "page_full_1280.png"), full_page=True)
    except Exception as e:
        print(f"  page_full_1280.png       FAILED: {e}")
    ctx.close()

    # ---------- pattern catalog section excerpt ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL + "#patterns")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(OUT / "patterns_section_1280.png"))
    ctx.close()

    # ---------- adjacent-work section excerpt ----------
    ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL + "#adjacent")
    page.wait_for_load_state("networkidle")
    try:
        page.locator("#adjacent").scroll_into_view_if_needed()
        page.locator("#adjacent").screenshot(
            path=str(OUT / "adjacent-work-1280.png"))
    except Exception as e:
        print(f"  adjacent-work-1280.png  FAILED: {e}")
    ctx.close()

    ctx = browser.new_context(viewport={"width": 420, "height": 800},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL + "#adjacent")
    page.wait_for_load_state("networkidle")
    try:
        page.locator("#adjacent").scroll_into_view_if_needed()
        page.locator("#adjacent").screenshot(
            path=str(OUT / "adjacent-work-mobile.png"))
    except Exception as e:
        print(f"  adjacent-work-mobile.png FAILED: {e}")
    ctx.close()

    # ---------- mobile rendering ----------
    ctx = browser.new_context(viewport={"width": 420, "height": 800},
                              device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(OUT / "mobile_420.png"), full_page=True)
    ctx.close()

    browser.close()

print(f"saved to {OUT}")
for f in sorted(OUT.glob("*.png")):
    print(" -", f.name, f"{f.stat().st_size / 1024:.1f} KB")
