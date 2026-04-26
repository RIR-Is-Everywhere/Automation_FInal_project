"""
test_TC008_error_handling.py
=============================
Test Scenario : Error Handling
TC-ID         : TC_008
Title         : System Error Handling – Network & Server Failures
Preconditions : System active
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER


class TestTC008ErrorHandling:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Offline / blocked network
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_offline_mode_shows_error_not_crash(self, page, base_url):
        """
        Step        : Load page → block all network → attempt navigation
        Expected    : System does NOT freeze; browser recovers after unblock
        """
        page.goto(base_url, wait_until="domcontentloaded")

        page.route("**/*", lambda route: route.abort())
        try:
            page.goto(base_url + "/jobs/", wait_until="domcontentloaded", timeout=5_000)
        except Exception:
            pass   # expected — network blocked

        page.unroute("**/*")

        # Browser should recover and load a page normally
        page.goto(base_url + "/login/", wait_until="domcontentloaded")
        assert page.locator("body").count() > 0, (
            "After network error, browser should recover and load the login page."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – 404 Not Found
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_404_page_handled_gracefully(self, page, base_url):
        """
        Step        : Navigate to a non-existent URL
        Expected    : 404 page shown (not blank or server crash)
        """
        resp = page.goto(
            base_url + "/this-page-does-not-exist-xyz/",
            wait_until="domcontentloaded",
        )
        page_text = page.locator("body").inner_text().lower()
        is_404 = (
            (resp and resp.status == 404)
            or "not found" in page_text
            or "404" in page_text
            or "page not found" in page_text
        )
        assert is_404, (
            f"Expected a 404 page; got HTTP {resp.status if resp else '?'}: {page_text[:200]}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Server error not exposed
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_invalid_login_does_not_expose_server_error(self, page, base_url):
        """
        Step        : Submit login with malformed / injection data
        Expected    : No 5xx HTTP response; no stack trace visible
        """
        login = LoginPage(page)
        login.open(base_url)

        server_errors = []
        def _on_response(resp):
            if resp.status >= 500:
                server_errors.append((resp.url, resp.status))
        page.on("response", _on_response)

        login.login("'; DROP TABLE users; --", "'; DROP TABLE users; --")
        page.wait_for_timeout(1000)

        assert not server_errors, (
            f"Server returned 5xx errors: {server_errors}"
        )
        body = page.locator("body").inner_text().lower()
        assert "traceback" not in body and "fatal error" not in body, (
            "Stack trace or fatal error must NOT be exposed to the user."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3b – Slow network (throttled requests)
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3b_slow_network_does_not_crash(self, page, base_url):
        """
        Step        : Add artificial delay on requests → load login page
        Expected    : Page eventually loads without crash
        """
        import time

        # Use a thread-safe counter to avoid routing multiple times
        _handled = {"done": False}

        def slow_route(route):
            if not _handled["done"]:
                time.sleep(0.3)
            route.continue_()

        page.route("**/*", slow_route)
        try:
            page.goto(base_url + "/login/", wait_until="domcontentloaded", timeout=30_000)
        finally:
            _handled["done"] = True
            page.unroute("**/*")

        assert page.locator("body").count() > 0, (
            "Login page should load even on a slow network."
        )
