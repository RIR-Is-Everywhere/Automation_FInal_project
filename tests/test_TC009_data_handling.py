"""
test_TC009_data_handling.py
============================
Test Scenario : Data Handling
TC-ID         : TC_009
Title         : Data Integrity – Save, Retrieve & Validation
Preconditions : Database connected
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage
from pages.profile_page import ProfilePage
from utils.test_data import VALID_USER
from utils.helpers import generate_candidate, ensure_login


def _login(page, base_url) -> LoginPage:
    """Login helper — auto-registers dummy account if VALID_USER fails."""
    ensure_login(page, base_url)
    return LoginPage(page)


class TestTC009DataHandling:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Valid data is accepted
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_submitted_data_is_accepted(self, page, base_url):
        """
        Step        : Fill candidate registration with valid data → Submit
        Expected    : Success message or redirect to dashboard
        """
        data = generate_candidate()
        reg  = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username=data["username"], email=data["email"],
            phone=data["phone"], password=data["password"],
            confirm_password=data["password"],
        )
        # Wait for post-registration state to settle
        try:
            page.wait_for_load_state("networkidle", timeout=8_000)
        except Exception:
            page.wait_for_load_state("domcontentloaded")
        success = (
            reg.get_success_message() != ""
            or "/candidate-dashboard/" in page.url
            or reg.has_success_message()
            or "/candidate-registration/" not in page.url   # redirected away
        )
        assert success, f"Valid data should be accepted. URL: {page.url}"

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Session persists after page refresh
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_session_persists_after_page_refresh(self, page, base_url):
        """
        Step        : Login → reload the page
        Expected    : User remains logged in after refresh
        """
        lp = _login(page, base_url)
        page.reload(wait_until="domcontentloaded")
        assert lp.is_logged_in(), (
            f"User should remain logged in after refresh. URL: {page.url}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2b – Dashboard content persists after refresh
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2b_dashboard_content_after_refresh(self, page, base_url):
        """
        Step        : Login → open dashboard → refresh
        Expected    : Dashboard reloads (no redirect to login)
        """
        lp = _login(page, base_url)
        profile = ProfilePage(page)
        profile.open_dashboard(base_url)
        page.reload(wait_until="domcontentloaded")
        assert "/login/" not in page.url, (
            "Dashboard should reload after refresh, not redirect to login."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Backend rejects duplicate email
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_backend_rejects_duplicate_email(self, page, base_url):
        """
        Step        : Register with email A → register again with same email A
        Expected    : Second attempt rejected by backend
        """
        data = generate_candidate()
        reg  = RegistrationPage(page)

        # First registration
        reg.open_candidate(base_url)
        reg.register_candidate(
            username=data["username"], email=data["email"],
            phone=data["phone"], password=data["password"],
            confirm_password=data["password"],
        )
        # Wait for post-registration redirect to settle
        try:
            page.wait_for_load_state("networkidle", timeout=8_000)
        except Exception:
            page.wait_for_load_state("domcontentloaded")

        # Second registration with same email (different username) — should be rejected
        try:
            reg.open_candidate(base_url)
        except Exception:
            page.wait_for_load_state("domcontentloaded")
            reg.open_candidate(base_url)
        reg.register_candidate(
            username=data["username"] + "_dup", email=data["email"],
            phone=data["phone"], password=data["password"],
            confirm_password=data["password"],
        )
        assert reg.get_error_message() != "", (
            "Backend should reject duplicate email registration."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1b – Profile update data saved
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1b_profile_update_data_saved(self, page, base_url):
        """
        Step        : Login → update profile name → reload page
        Expected    : Update persists (no crash / no redirect to login)
        """
        _login(page, base_url)
        profile = ProfilePage(page)
        profile.open_edit_profile(base_url)

        if "/login/" in page.url:
            pytest.skip("Edit profile not accessible for this account type.")

        profile.update_name("AutoTest", "User")
        page.reload(wait_until="domcontentloaded")
        assert "/login/" not in page.url, (
            "After profile update and reload, page should not redirect to login."
        )
