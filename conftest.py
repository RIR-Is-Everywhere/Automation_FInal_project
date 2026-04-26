"""
conftest.py
Playwright browser fixture.
- Auto-screenshot on test FAILURE  → screenshots/FAIL_<test>.png
- One screenshot per TC module     → screenshots/TC_001_screenshot.png ... TC_010_screenshot.png
"""

import sys
import os
import pytest
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(__file__))

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL     = "https://labsqajobs.qaharbor.com"
BROWSER_TYPE = "chromium"
HEADLESS     = False        # True for CI

# Track which TC modules have already had a screenshot taken (one per TC)
_tc_screenshots_taken: set = set()

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def page(request):
    """
    Fresh Playwright page per test.
    Captures:
      1) One full-page screenshot per TC module (TC_001…TC_010)
      2) A failure screenshot on any failing test
    """
    with sync_playwright() as pw:
        browser = getattr(pw, BROWSER_TYPE).launch(headless=HEADLESS)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        _page   = context.new_page()

        yield _page   # ← test runs here

        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # ── 1. One screenshot per TC module ───────────────────────────────────
        module_name = request.node.module.__name__  # e.g. test_TC001_login
        # Extract TC-ID from module name (test_TC001_... → TC_001)
        tc_id = None
        for segment in module_name.split("_"):
            if segment.upper().startswith("TC") and segment[2:].isdigit():
                # zero-pad to 3 digits
                num   = segment[2:].zfill(3)
                tc_id = f"TC_{num}"
                break

        if tc_id and tc_id not in _tc_screenshots_taken:
            _tc_screenshots_taken.add(tc_id)
            path = os.path.join(SCREENSHOT_DIR, f"{tc_id}_screenshot.png")
            try:
                _page.screenshot(path=path, full_page=True)
            except Exception:
                pass   # page may have closed mid-test; skip silently

        # ── 2. Failure screenshot ─────────────────────────────────────────────
        failed = getattr(getattr(request.node, "rep_call", None), "failed", False)
        if failed:
            safe_name = request.node.name.replace("/", "_").replace(":", "_")
            path = os.path.join(SCREENSHOT_DIR, f"FAIL_{safe_name}.png")
            try:
                _page.screenshot(path=path, full_page=True)
            except Exception:
                pass

        context.close()
        browser.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store call result on node so the page fixture can read it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
