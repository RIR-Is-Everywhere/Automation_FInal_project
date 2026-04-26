"""
registration_page.py — Candidate & Recruiter registration forms
for https://labsqajobs.qaharbor.com
"""

from pages.base_page import BasePage


class RegistrationPage(BasePage):

    CANDIDATE_URL = "/candidate-registration/"
    RECRUITER_URL = "/recruiter-registration/"

    # ── Candidate registration selectors ──────────────────────────────────────
    # JetFormBuilder renders fields as input[name="field_name"]
    C_USERNAME    = "input[name='username']"
    C_EMAIL       = "input[name='email']"
    C_PASSWORD    = "input[name='password']"
    C_CONFIRM_PW  = "input[name='conf-pass']"   # actual name on site (no phone field)
    C_SUBMIT      = "button.jet-form-builder__submit"

    # ── Recruiter registration selectors ──────────────────────────────────────
    R_COMPANY     = "input[name='_recruiter-company-name']"
    R_EMAIL       = "input[name='_recruiter-email']"
    R_PHONE       = "input[name='phone']"
    R_PASSWORD    = "input[name='password']"
    R_CONFIRM_PW  = "input[name='confirm-password']"
    R_SUBMIT      = "button.jet-form-builder__submit"

    # ── Common feedback ────────────────────────────────────────────────────────
    ERROR_MSG   = ".jet-form-builder__message--error"
    SUCCESS_MSG = ".jet-form-builder__message--success"

    # ── Helpers ────────────────────────────────────────────────────────────────

    def open_candidate(self, base_url: str):
        self.navigate(base_url + self.CANDIDATE_URL)

    def open_recruiter(self, base_url: str):
        self.navigate(base_url + self.RECRUITER_URL)

    def _safe_fill(self, selector: str, value: str):
        """Fill a field only if it exists; silently skip if not found."""
        loc = self.page.locator(selector)
        if loc.count() > 0:
            loc.first.fill(value)

    def register_candidate(self, username, email, password, confirm_password, phone=None):
        """
        Register a candidate. `phone` is accepted for backward-compat but
        ignored — the form has no phone field.
        """
        self.page.locator(self.C_USERNAME).fill(username)
        self.page.locator(self.C_EMAIL).fill(email)
        self.page.locator(self.C_PASSWORD).fill(password)
        self.page.locator(self.C_CONFIRM_PW).fill(confirm_password)
        
        # Click and wait for navigation or status update
        self.page.locator(self.C_SUBMIT).first.click()
        
        # Wait a bit for the URL to change or for an error/success message to appear
        try:
            self.page.wait_for_url(lambda url: "status=" in url or "/dashboard" in url, timeout=10000)
        except Exception:
            # Fallback: wait for message to appear if URL didn't change
            try:
                self.page.wait_for_selector(f"{self.ERROR_MSG}, {self.SUCCESS_MSG}", timeout=5000)
            except Exception:
                pass

    def has_success_message(self) -> bool:
        if "status=success" in self.page.url:
            return True
        loc = self.page.locator(self.SUCCESS_MSG)
        return loc.count() > 0 and loc.first.is_visible()

    def register_recruiter(self, company, email, phone, password, confirm_password):
        self.page.locator(self.R_COMPANY).fill(company)
        self.page.locator(self.R_EMAIL).fill(email)
        self.page.locator(self.R_PHONE).fill(phone)
        self.page.locator(self.R_PASSWORD).fill(password)
        self.page.locator(self.R_CONFIRM_PW).fill(confirm_password)
        
        self.page.locator(self.R_SUBMIT).first.click()
        
        try:
            self.page.wait_for_url(lambda url: "status=" in url or "/dashboard" in url, timeout=10000)
        except Exception:
            try:
                self.page.wait_for_selector(f"{self.ERROR_MSG}, {self.SUCCESS_MSG}", timeout=5000)
            except Exception:
                pass

    def get_error_message(self) -> str:
        # Check URL for status parameters first
        url = self.page.url
        if "status=password_mismatch" in url:
            return "Passwords do not match."
        if "status=invalid_email" in url:
            return "Invalid email address."
        if "status=validation_failed" in url:
            return "Form validation failed."
        if "status=error" in url:
            return "An error occurred."
        
        loc = self.page.locator(self.ERROR_MSG)
        if loc.count() > 0:
            # Force wait for visibility if it exists but might be fading in
            try:
                loc.first.wait_for(state="visible", timeout=2000)
                return loc.first.inner_text().strip()
            except Exception:
                pass
        return ""

    def get_success_message(self) -> str:
        if "status=success" in self.page.url:
            return "Success"
        loc = self.page.locator(self.SUCCESS_MSG)
        if loc.count() > 0:
            try:
                loc.first.wait_for(state="visible", timeout=2000)
                return loc.first.inner_text().strip()
            except Exception:
                pass
        return ""
