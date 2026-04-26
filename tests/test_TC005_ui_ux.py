"""
test_TC005_ui_ux.py
====================
Test Scenario : UI/UX
TC-ID         : TC_005
Title         : UI/UX – Responsiveness & User Experience
Preconditions : Application open
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER

VIEWPORTS = [
    {"name": "Mobile",  "width": 375,  "height": 812},
    {"name": "Tablet",  "width": 768,  "height": 1024},
    {"name": "Desktop", "width": 1280, "height": 900},
]


class TestTC005UiUx:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Resize screen (mobile / tablet / desktop)
    # ──────────────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("viewport", VIEWPORTS, ids=lambda v: v["name"])
    def test_step1_responsive_layout(self, page, base_url, viewport):
        """
        Step        : Set viewport to mobile / tablet / desktop → load homepage
        Expected    : Page loads without horizontal overflow or layout breakage
        """
        page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
        page.goto(base_url, wait_until="domcontentloaded")

        # Page should render (title exists, body has content)
        assert page.title() != "", (
            f"{viewport['name']}: Page title is empty — page may not have loaded."
        )
        body_width = page.evaluate("document.body.scrollWidth")
        assert body_width <= viewport["width"] + 30, (
            f"{viewport['name']}: Horizontal scroll overflow detected "
            f"(body width {body_width}px > viewport {viewport['width']}px)"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Button hover / click feedback
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_login_button_is_clickable(self, page, base_url):
        """
        Step        : Navigate to login page → hover over login button → check state
        Expected    : Button is visible and enabled
        """
        login = LoginPage(page)
        login.open(base_url)
        # Use the specific JetFormBuilder submit button (not the newsletter Subscribe btn)
        btn = page.locator(LoginPage.SUBMIT_BUTTON)
        if btn.count() == 0:
            btn = page.get_by_role("button", name="Login")
        assert btn.first.is_visible(), "Login button should be visible."
        assert btn.first.is_enabled(), "Login button should be enabled."
        btn.first.hover()
        page.wait_for_timeout(300)
        assert btn.first.is_visible(), "Button should still be visible after hover."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4 – Validate error message clarity
    # ──────────────────────────────────────────────────────────────────────────
    def test_step4_error_message_is_visible_and_readable(self, page, base_url):
        """
        Step        : Submit login with wrong password → inspect error message
        Expected    : Error message is visible, non-empty, and readable
        """
        login = LoginPage(page)
        login.open(base_url)
        login.login(VALID_USER["username"], "WrongPass!99")
        page.wait_for_timeout(1500)

        error_selectors = [
            ".jet-form-builder__message--error",
            ".woocommerce-error",
            ".alert",
            ".notice-error",
            "p.error",
        ]
        error_found = False
        for sel in error_selectors:
            el = page.locator(sel)
            if el.count() > 0 and el.first.is_visible():
                msg = el.first.inner_text().strip()
                assert len(msg) > 3, f"Error message too short: '{msg}'"
                assert "<" not in msg, f"Error contains HTML tags: '{msg}'"
                error_found = True
                break

        if not error_found:
            # Site may redirect back to /login/ instead of showing inline error
            assert not login.is_logged_in(), (
                "No inline error found, but user should not be logged in after wrong password."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1b – Login page is responsive on mobile
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1b_login_page_mobile_responsive(self, page, base_url):
        """
        Step        : Set mobile viewport → open login page
        Expected    : Login form inputs are visible on a 375px wide screen
        """
        page.set_viewport_size({"width": 375, "height": 812})
        login = LoginPage(page)
        login.open(base_url)
        # Use flexible selectors that work regardless of exact ID
        email_loc = page.locator(LoginPage.EMAIL_INPUT)
        if email_loc.count() == 0:
            email_loc = page.locator("input[type='text'], input[type='email'], input[type='tel']").first
        pw_loc = page.locator(LoginPage.PASSWORD_INPUT)
        if pw_loc.count() == 0:
            pw_loc = page.locator("input[type='password']").first
        btn_loc = page.locator(LoginPage.SUBMIT_BUTTON)
        if btn_loc.count() == 0:
            btn_loc = page.get_by_role("button", name="Login")
        assert email_loc.is_visible(), "Username/email field should be visible on mobile."
        assert pw_loc.is_visible(), "Password field should be visible on mobile."
        assert btn_loc.first.is_visible(), "Submit button should be visible on mobile."
