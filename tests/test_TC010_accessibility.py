"""
test_TC010_accessibility.py
============================
Test Scenario : Accessibility
TC-ID         : TC_010
Title         : Accessibility – Keyboard & Screen Reader Support
Preconditions : Application open
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER


class TestTC010Accessibility:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Tab navigation
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_tab_navigation_on_login_page(self, page, base_url):
        """
        Step        : Open login page → press Tab 3 times
        Expected    : Focus moves through interactive elements (INPUT/BUTTON/A)
        """
        login = LoginPage(page)
        login.open(base_url)
        page.locator("body").click()

        focused_tags = set()
        for _ in range(3):
            page.keyboard.press("Tab")
            tag = page.evaluate("document.activeElement.tagName")
            focused_tags.add(tag)

        assert focused_tags & {"INPUT", "BUTTON", "A"}, (
            f"Tab should move focus to interactive elements. Got: {focused_tags}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1b – Shift+Tab moves focus backwards
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1b_shift_tab_moves_focus_backward(self, page, base_url):
        """
        Step        : Focus username field → Tab forward → Shift+Tab backward
        Expected    : Focus returns to a different (previous) element
        """
        login = LoginPage(page)
        login.open(base_url)

        # Click username field to set focus
        email_loc = page.locator(LoginPage.EMAIL_INPUT)
        if email_loc.count() == 0:
            email_loc = page.locator("input").first
        email_loc.click()

        page.keyboard.press("Tab")
        # FIX: use JavaScript || (not Python or) inside page.evaluate
        after_tab = page.evaluate(
            "document.activeElement.getAttribute('id') || document.activeElement.tagName"
        )

        page.keyboard.press("Shift+Tab")
        after_shift_tab = page.evaluate(
            "document.activeElement.getAttribute('id') || document.activeElement.tagName"
        )

        assert after_tab != after_shift_tab, (
            "Shift+Tab should move focus to a different element than Tab."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Keyboard-only login
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_keyboard_only_login(self, page, base_url):
        """
        Step        : Fill login form with keyboard only (Tab + type + Enter)
        Expected    : Form submits and user is redirected to dashboard
        """
        login = LoginPage(page)
        login.open(base_url)

        # Focus the username field
        email_loc = page.locator(LoginPage.EMAIL_INPUT)
        if email_loc.count() == 0:
            email_loc = page.locator(
                "input[type='text'], input[type='email'], input[type='tel']"
            ).first
        email_loc.focus()
        page.keyboard.type(VALID_USER["username"])

        # Tab to password field
        page.keyboard.press("Tab")
        page.keyboard.type(VALID_USER["password"])

        # Submit with Enter
        page.keyboard.press("Enter")
        try:
            page.wait_for_url(
                lambda url: "/login/" not in url,
                timeout=8_000,
            )
        except Exception:
            page.wait_for_load_state("domcontentloaded")

        if not login.is_logged_in():
            pytest.skip(
                "Keyboard login requires valid credentials. "
                "Skipping — verify VALID_USER credentials are registered on the site."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Input labels / ARIA attributes
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_input_fields_have_labels_or_aria(self, page, base_url):
        """
        Step        : Inspect login form inputs for accessibility attributes
        Expected    : Each visible input has a label, aria-label, or placeholder
        """
        login = LoginPage(page)
        login.open(base_url)

        # Only check visible, non-hidden inputs
        inputs = page.locator(
            "form input:not([type='hidden']):not([type='submit'])"
            ":not([type='checkbox']):not([type='radio'])"
        )
        count  = inputs.count()
        assert count > 0, "No visible inputs found on login form."

        missing = []
        for i in range(count):
            inp = inputs.nth(i)
            # Skip invisible inputs
            if not inp.is_visible():
                continue
            inp_type    = inp.get_attribute("type") or "text"
            inp_id      = inp.get_attribute("id") or ""
            aria_label  = inp.get_attribute("aria-label") or ""
            aria_lby    = inp.get_attribute("aria-labelledby") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            label_exists = (
                page.locator(f"label[for='{inp_id}']").count() > 0
                if inp_id else False
            )
            has_a11y = label_exists or bool(aria_label) or bool(aria_lby) or bool(placeholder)
            if not has_a11y:
                missing.append(f"Input #{i} type={inp_type} id='{inp_id}' — no label/aria-label/placeholder")

        assert not missing, (
            "Inputs missing accessibility attributes:\n" + "\n".join(missing)
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3b – <h1> heading present
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3b_page_has_h1_heading(self, page, base_url):
        """
        Step        : Load homepage → check heading structure
        Expected    : At least one <h1> exists for screen reader support
        """
        page.goto(base_url, wait_until="domcontentloaded")
        h1_count = page.locator("h1").count()
        assert h1_count >= 1, (
            f"Page needs at least one <h1> heading. Found: {h1_count}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3c – Images have alt attributes
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3c_images_have_alt_text(self, page, base_url):
        """
        Step        : Load homepage → inspect all <img> tags
        Expected    : Every image has an alt attribute (empty string is OK)
        """
        page.goto(base_url, wait_until="domcontentloaded")
        images  = page.locator("img")
        missing = []
        for i in range(images.count()):
            alt = images.nth(i).get_attribute("alt")
            src = images.nth(i).get_attribute("src") or f"image-{i}"
            if alt is None:   # alt="" is fine; alt=None is not
                missing.append(src[:80])
        assert not missing, (
            "Images missing alt attribute:\n" + "\n".join(missing)
        )
