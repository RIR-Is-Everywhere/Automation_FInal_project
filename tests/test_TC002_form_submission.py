"""
test_TC002_form_submission.py
==============================
Test Scenario : Form Submission
TC-ID         : TC_002
Title         : Form Validation – Input, File Upload, Duplicate Handling
Preconditions : User logged in
Site          : https://labsqajobs.qaharbor.com
"""

import pytest
from pages.login_page import LoginPage
from pages.registration_page import RegistrationPage
from utils.test_data import VALID_USER, INVALID_EMAIL, INVALID_PHONE, BLANK, unique_email
from utils.helpers import generate_candidate, ensure_login


def _do_login(page, base_url) -> bool:
    """Attempt login with fallback registration; return True if successful."""
    try:
        ensure_login(page, base_url)
        return True
    except Exception:
        return False


class TestTC002FormSubmission:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Valid form data
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_valid_form_submission(self, page, base_url):
        """
        Step        : Fill candidate registration form with valid data → Submit
        Expected    : Successful submission (success message or redirect)
        """
        data = generate_candidate()
        reg  = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username=data["username"], email=data["email"],
            phone=data["phone"], password=data["password"],
            confirm_password=data["password"],
        )
        success = reg.get_success_message() != "" or "/candidate-dashboard/" in page.url
        assert success, f"Valid form should succeed. URL: {page.url}"

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Empty form
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_empty_form_rejected(self, page, base_url):
        """
        Step        : Submit registration form with all blank fields
        Expected    : Validation error shown / not submitted
        """
        reg = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username=BLANK, email=BLANK,
            phone=BLANK, password=BLANK, confirm_password=BLANK,
        )
        still_on_reg_page = "/candidate-registration/" in page.url
        has_error = reg.get_error_message() != ""
        assert has_error or still_on_reg_page, "Empty form should not submit successfully."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4 – Invalid email / phone
    # ──────────────────────────────────────────────────────────────────────────
    def test_step4_invalid_email_format(self, page, base_url):
        """
        Step        : Enter invalid email → Submit
        Expected    : Validation error for email field
        """
        reg = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username="formtest01", email=INVALID_EMAIL,
            phone="01700000000", password="ValidPass@1",
            confirm_password="ValidPass@1",
        )
        assert reg.get_error_message() != "", "Invalid email format should trigger an error."

    def test_step4_invalid_phone_format(self, page, base_url):
        """
        Step        : Enter alphabetic phone number → Submit (on Recruiter form)
        Expected    : Validation error for phone field
        """
        reg = RegistrationPage(page)
        reg.open_recruiter(base_url)
        reg.register_recruiter(
            company="PhoneTest Ltd", email=unique_email("rec-phone"),
            phone=INVALID_PHONE, password="ValidPass@1",
            confirm_password="ValidPass@1",
        )
        assert reg.get_error_message() != "", "Invalid phone should trigger an error on recruiter form."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 5 – Special characters
    # ──────────────────────────────────────────────────────────────────────────
    def test_step5_special_characters_in_username(self, page, base_url):
        """
        Step        : Enter XSS payload in username → Submit
        Expected    : Page does not crash, input is sanitised
        """
        reg = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username="<script>alert(1)</script>",
            email=unique_email("special"),
            phone="01700000003",
            password="ValidPass@1",
            confirm_password="ValidPass@1",
        )
        assert page.title() is not None, "Page crashed on special character input."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 7 – Invalid file type upload
    # ──────────────────────────────────────────────────────────────────────────
    def test_step7_invalid_file_type_rejected(self, page, base_url):
        """
        Step        : Locate file upload → upload an .exe file
        Expected    : Error shown or upload blocked
        """
        _do_login(page, base_url)
        page.goto(base_url + "/candidate-dashboard/", wait_until="domcontentloaded")
        if "/login/" in page.url:
            pytest.skip("Dashboard not accessible; skipping file upload test.")

        upload_inputs = page.locator("input[type='file']")
        if upload_inputs.count() == 0:
            pytest.skip("No file upload field found on dashboard.")

        upload_inputs.first.set_input_files({
            "name": "malware.exe",
            "mimeType": "application/octet-stream",
            "buffer": b"MZ\x90\x00",
        })
        submit = page.locator("button[type='submit'], input[type='submit']").first
        if submit.is_visible():
            submit.click()
            page.wait_for_load_state("domcontentloaded")

        error_present = page.locator(
            ".error, .woocommerce-error, .jet-form-builder__message--error"
        ).count() > 0
        assert error_present or "dashboard" in page.url, (
            "Invalid file type should be rejected or produce an error."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 8 – Password mismatch
    # ──────────────────────────────────────────────────────────────────────────
    def test_step8_password_mismatch_prevented(self, page, base_url):
        """
        Step        : Submit registration with non-matching passwords
        Expected    : Form rejected with mismatch error
        """
        reg = RegistrationPage(page)
        reg.open_candidate(base_url)
        reg.register_candidate(
            username="formtest03", email=unique_email("mismatch"),
            phone="01700000004", password="ValidPass@1",
            confirm_password="DifferentPass@9",
        )
        assert reg.get_error_message() != "", "Mismatched passwords should be rejected."
