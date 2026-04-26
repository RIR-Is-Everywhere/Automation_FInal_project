"""
test_TC004_navigation.py
=========================
Test Scenario : Navigation
TC-ID         : TC_004
Title         : Navigation – Routing, Links, URL Protection
Preconditions : Application loaded
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER

PUBLIC_NAV_LINKS = [
    "/",
    "/jobs/",
    "/login/",
    "/candidate-registration/",
    "/recruiter-registration/",
]

PROTECTED_PATHS = [
    "/candidate-dashboard/",
    "/candidate-dashboard/edit-resume/",
]


class TestTC004Navigation:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Click all menu items
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_main_nav_links_work(self, page, base_url):
        """
        Step        : Visit homepage → inspect main nav links
        Expected    : Each link has a non-empty, valid href
        """
        page.goto(base_url, wait_until="domcontentloaded")
        nav_links = page.locator("nav a[href], header a[href]")
        count = nav_links.count()
        assert count > 0, "No navigation links found on the homepage."

        failed = []
        for i in range(min(count, 8)):
            href = nav_links.nth(i).get_attribute("href") or ""
            if href.startswith("http") and "#" not in href:
                try:
                    resp = page.goto(href, wait_until="domcontentloaded", timeout=10_000)
                    if resp and resp.status >= 400:
                        failed.append(f"{href} → HTTP {resp.status}")
                except Exception as e:
                    failed.append(f"{href} → {e}")

        assert not failed, "Broken nav links found:\n" + "\n".join(failed)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Public pages load
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_public_pages_load_successfully(self, page, base_url):
        """
        Step        : Visit each known public page
        Expected    : All load without HTTP error (200)
        """
        failed = []
        for path in PUBLIC_NAV_LINKS:
            resp = page.goto(base_url + path, wait_until="domcontentloaded", timeout=15_000)
            if resp and resp.status >= 400:
                failed.append(f"{path} → HTTP {resp.status}")
        assert not failed, "Some public pages returned errors:\n" + "\n".join(failed)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Browser back / forward
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_browser_back_forward(self, page, base_url):
        """
        Step        : Navigate to two pages → press Back → press Forward
        Expected    : Correct pages load each time
        """
        page.goto(base_url + "/jobs/", wait_until="domcontentloaded")
        jobs_url = page.url

        page.goto(base_url + "/login/", wait_until="domcontentloaded")
        login_url = page.url

        # Back
        page.go_back()
        page.wait_for_load_state("domcontentloaded")
        assert page.url == jobs_url, (
            f"Back button should return to {jobs_url}. Got: {page.url}"
        )

        # Forward
        page.go_forward()
        page.wait_for_load_state("domcontentloaded")
        assert page.url == login_url, (
            f"Forward button should return to {login_url}. Got: {page.url}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4 – Restricted URLs without login redirect
    # ──────────────────────────────────────────────────────────────────────────
    def test_step4_restricted_url_redirects_without_login(self, page, base_url):
        """
        Step        : Access protected pages without logging in
        Expected    : Redirected to login or homepage (not on the protected page)
        """
        failed = []
        for path in PROTECTED_PATHS:
            page.goto(base_url + path, wait_until="domcontentloaded")
            final_url = page.url
            # A fresh context has no cookies, so dashboard should not be accessible
            is_unprotected = (
                path.rstrip("/") in final_url
                and page.locator("a[href*='logout']").count() > 0
            )
            if is_unprotected:
                failed.append(f"{path} accessible without login → URL: {final_url}")
        assert not failed, "Protected pages accessible without login:\n" + "\n".join(failed)

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4b – Restricted URLs ARE accessible after login
    # ──────────────────────────────────────────────────────────────────────────
    def test_step4b_restricted_url_accessible_after_login(self, page, base_url):
        """
        Step        : Login → navigate to dashboard directly
        Expected    : Dashboard loads (no redirect back to login)
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(VALID_USER["username"], VALID_USER["password"])
        if not login.is_logged_in():
            pytest.skip("Login failed — check credentials. Skipping post-login navigation test.")

        page.goto(base_url + "/candidate-dashboard/", wait_until="domcontentloaded")
        assert "/login/" not in page.url, (
            f"Logged-in user should access dashboard. Got: {page.url}"
        )
