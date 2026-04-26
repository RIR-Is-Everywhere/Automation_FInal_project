"""
test_TC007_session_logout.py
=============================
Test Scenario : Session & Logout
TC-ID         : TC_007
Title         : Session Management – Logout & Timeout Handling
Preconditions : User logged in
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER
from utils.helpers import ensure_login


def _login(page, base_url) -> LoginPage:
    """Login helper — auto-registers dummy account if VALID_USER fails."""
    from pages.login_page import LoginPage
    ensure_login(page, base_url)
    return LoginPage(page)


class TestTC007SessionLogout:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Manual logout
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_manual_logout_redirects(self, page, base_url):
        """
        Step        : Login → click Logout
        Expected    : Session ends, user is redirected away from dashboard
        """
        lp = _login(page, base_url)
        lp.logout(base_url)
        assert not lp.is_logged_in(), (
            f"After logout, user should not be on an authenticated page. URL: {page.url}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1b – Back button after logout
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1b_back_button_after_logout(self, page, base_url):
        """
        Step        : Login → Logout → press browser Back → reload
        Expected    : Session is not restored via back button
        """
        lp = _login(page, base_url)
        lp.logout(base_url)

        # Go back
        page.go_back()
        page.wait_for_load_state("domcontentloaded")
        # Reload forces a fresh server-side session check
        page.reload(wait_until="domcontentloaded")

        # Attempt to navigate to the protected dashboard
        page.goto(base_url + "/candidate-dashboard/", wait_until="domcontentloaded")
        # If session is truly ended, the dashboard should redirect to login
        has_logout_link = page.locator("a[href*='logout']").count() > 0
        on_dashboard    = "/candidate-dashboard" in page.url and has_logout_link
        assert not on_dashboard, (
            "Session should be destroyed after logout — back button must not restore it."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – New browser context has no session
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_fresh_context_has_no_session(self, page, base_url):
        """
        Step        : Without logging in, navigate to the dashboard
        Expected    : No active session → redirected away from dashboard
        """
        # The page fixture provides a fresh context (no cookies)
        page.goto(base_url + "/candidate-dashboard/", wait_until="domcontentloaded")
        # Expect redirect away from the dashboard (login page or home)
        has_logout_link = page.locator("a[href*='logout']").count() > 0
        on_dashboard    = "/candidate-dashboard" in page.url and has_logout_link
        assert not on_dashboard, (
            f"A fresh session should not grant dashboard access. URL: {page.url}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1c – Re-login after logout
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1c_relogin_after_logout(self, page, base_url):
        """
        Step        : Login → Logout → Login again
        Expected    : Second login succeeds
        """
        lp = _login(page, base_url)
        lp.logout(base_url)

        # Second login — use ensure_login for fallback
        ensure_login(page, base_url)
        lp2 = LoginPage(page)
        assert lp2.is_logged_in(), (
            f"Re-login after logout should succeed. URL: {page.url}"
        )
