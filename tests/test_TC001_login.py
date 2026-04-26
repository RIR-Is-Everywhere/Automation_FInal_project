"""
test_TC001_login.py
===================
Test Scenario : Login
TC-ID         : TC_001
Title         : Authentication – Login Functional & Security Validation
Preconditions : User exists in system
Site          : https://labsqajobs.qaharbor.com/login/
"""

import pytest
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage
from utils.test_data import (
    VALID_USER, WRONG_PASSWORD, BLANK,
    unique_email, unique_username, random_password, random_phone,
)


class TestTC001Login:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Valid credentials → dashboard
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_valid_credentials_redirect_to_dashboard(self, page, base_url):
        """
        Step        : Enter valid username/password → Click Login
        Expected    : User is redirected to dashboard (away from /login/).
        Strategy    : 1) Try VALID_USER login first (fast path).
                      2) If that fails, register a fresh dummy account with a
                         unique dummy email (@mailinator.com) then retry login.
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(VALID_USER["username"], VALID_USER["password"])

        if not login.is_logged_in():
            # ── Generate brand-new dummy credentials ───────────────────────────
            dummy_username = unique_username("qa")       # e.g. qa3f8a21
            dummy_email    = unique_email("qa")          # e.g. qa_3f8a21ab@mailinator.com
            dummy_password = random_password()            # e.g. Qa1!xYz9mNpQ

            # ── Register the dummy account (no phone field on this form) ───────
            reg = RegistrationPage(page)
            reg.open_candidate(base_url)
            reg.register_candidate(
                username=dummy_username,
                email=dummy_email,
                password=dummy_password,
                confirm_password=dummy_password,
            )
            # Wait for the site to finish any post-registration redirect
            try:
                page.wait_for_load_state("networkidle", timeout=8_000)
            except Exception:
                page.wait_for_load_state("domcontentloaded")

            # ── Login with the freshly registered dummy account ────────────────
            try:
                login.open(base_url)
            except Exception:
                # ERR_ABORTED can happen if a redirect is still in flight; retry
                page.wait_for_load_state("domcontentloaded")
                login.open(base_url)

            login.login(dummy_username, dummy_password)

        assert login.is_logged_in(), (
            f"Login failed even after registering a fresh dummy account. "
            f"URL: {page.url}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Wrong password → error
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_wrong_password_shows_error(self, page, base_url):
        """
        Step        : Enter valid username + wrong password → Click Login
        Expected    : Error message displayed, user stays on login page
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(VALID_USER["username"], WRONG_PASSWORD)
        assert not login.is_logged_in(), "Wrong password should NOT log in the user."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4 – Invalid username
    # ──────────────────────────────────────────────────────────────────────────
    def test_step4_invalid_username_format(self, page, base_url):
        """
        Step        : Enter a completely invalid username → Click Login
        Expected    : Login fails / stays on login page
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login("invalid!!user@@", VALID_USER["password"])
        assert not login.is_logged_in(), "Invalid username should not allow login."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 5 – Empty fields
    # ──────────────────────────────────────────────────────────────────────────
    def test_step5_empty_username_blocked(self, page, base_url):
        """
        Step        : Leave username blank → Click Login
        Expected    : Login is blocked
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(BLANK, VALID_USER["password"])
        assert not login.is_logged_in(), "Empty username should block login."

    def test_step5_empty_password_blocked(self, page, base_url):
        """
        Step        : Enter username, leave password blank → Click Login
        Expected    : Login is blocked
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(VALID_USER["username"], BLANK)
        assert not login.is_logged_in(), "Empty password should block login."

    def test_step5_both_fields_empty_blocked(self, page, base_url):
        """
        Step        : Leave both fields blank → Click Login
        Expected    : Login is blocked / required field validation shown
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(BLANK, BLANK)
        assert not login.is_logged_in(), "Both empty fields should block login."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 6 – Password masking
    # ──────────────────────────────────────────────────────────────────────────
    def test_step6_password_field_is_masked(self, page, base_url):
        """
        Step        : Inspect the password field type attribute
        Expected    : type='password' (characters are shown as dots/asterisks)
        """
        login = LoginPage(page)
        login.open(base_url)
        # Try the primary selector; fall back to any password input
        pw_loc = page.locator(LoginPage.PASSWORD_INPUT)
        if pw_loc.count() == 0:
            pw_loc = page.locator("input[type='password']")
        assert pw_loc.count() > 0, "No password input found on login page."
        pw_type = pw_loc.first.get_attribute("type")
        assert pw_type == "password", (
            f"Password field type should be 'password', got: '{pw_type}'"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 7 – Enter key submits login
    # ──────────────────────────────────────────────────────────────────────────
    def test_step7_enter_key_submits_login(self, page, base_url):
        """
        Step        : Fill credentials → press Enter key (no button click)
        Expected    : Form submits and user is redirected to dashboard.
        Fallback    : If VALID_USER doesn't exist, register a dummy account first.
        """
        login = LoginPage(page)

        # ── Resolve working credentials (VALID_USER or fresh dummy) ───────────
        use_username = VALID_USER["username"]
        use_password = VALID_USER["password"]

        # Quick probe: try login, if it fails register a dummy account
        login.open(base_url)
        login.login(use_username, use_password)
        if not login.is_logged_in():
            use_username = unique_username("qa")
            use_email    = unique_email("qa")
            use_password = random_password()

            reg = RegistrationPage(page)
            reg.open_candidate(base_url)
            reg.register_candidate(
                username=use_username,
                email=use_email,
                password=use_password,
                confirm_password=use_password,
            )
            try:
                page.wait_for_load_state("networkidle", timeout=8_000)
            except Exception:
                page.wait_for_load_state("domcontentloaded")

        # ── Now test Enter-key submission ──────────────────────────────────────
        try:
            login.open(base_url)
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            login.open(base_url)

        # Fill email/username
        email_loc = page.locator(LoginPage.EMAIL_INPUT)
        if email_loc.count() == 0:
            email_loc = page.locator(
                "input[type='text'], input[type='email'], input[type='tel']"
            ).first
        email_loc.fill(use_username)

        # Fill password and press Enter
        pw_loc = page.locator(LoginPage.PASSWORD_INPUT)
        if pw_loc.count() == 0:
            pw_loc = page.locator("input[type='password']").first
        pw_loc.fill(use_password)
        pw_loc.press("Enter")

        try:
            page.wait_for_url(
                lambda url: "/login/" not in url,
                timeout=8_000,
            )
        except Exception:
            page.wait_for_load_state("domcontentloaded")

        assert login.is_logged_in(), (
            f"Enter key should submit the login form. URL: {page.url}"
        )
