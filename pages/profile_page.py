"""
profile_page.py — Profile / My Account actions
for https://labsqajobs.qaharbor.com
"""

from pages.base_page import BasePage


class ProfilePage(BasePage):

    DASHBOARD_URL    = "/candidate-dashboard/"
    EDIT_PROFILE_URL = "/account/update-profile/"  # updated from /candidate-dashboard/edit-resume/

    # ── Selectors (Candidate Profile) ──────────────────────────────────────────
    FIRST_NAME_INPUT    = "#_candidate-first-name"
    LAST_NAME_INPUT     = "#_candidate-last-name"
    EMAIL_INPUT         = "#_candidate-email"
    PHONE_INPUT         = "#phone"
    SAVE_PROFILE_BUTTON = "button.jet-form-builder__submit"

    # Change password fields (WooCommerce-style my-account)
    CURRENT_PW_INPUT    = "input#password_current"
    NEW_PW_INPUT        = "input#password_1"
    CONFIRM_PW_INPUT    = "input#password_2"
    SAVE_PW_BUTTON      = "button[name='save_account_details']"

    SUCCESS_MSG         = ".woocommerce-message"
    ERROR_MSG           = ".woocommerce-error"

    def open_dashboard(self, base_url: str):
        self.navigate(base_url + self.DASHBOARD_URL)

    def open_edit_profile(self, base_url: str):
        self.navigate(base_url + self.EDIT_PROFILE_URL)

    def update_name(self, first_name: str, last_name: str):
        self.fill(self.FIRST_NAME_INPUT, first_name)
        self.fill(self.LAST_NAME_INPUT, last_name)
        self.page.locator(self.SAVE_PROFILE_BUTTON).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def update_email(self, email: str):
        self.fill(self.EMAIL_INPUT, email)
        self.page.locator(self.SAVE_PROFILE_BUTTON).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def change_password(self, current_pw: str, new_pw: str, confirm_pw: str):
        self.fill(self.CURRENT_PW_INPUT, current_pw)
        self.fill(self.NEW_PW_INPUT, new_pw)
        self.fill(self.CONFIRM_PW_INPUT, confirm_pw)
        self.click(self.SAVE_PW_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")

    def get_success_message(self) -> str:
        return self.get_text(self.SUCCESS_MSG) if self.is_visible(self.SUCCESS_MSG) else ""

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MSG) if self.is_visible(self.ERROR_MSG) else ""
