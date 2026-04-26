"""
login_page.py — Login page actions for https://labsqajobs.qaharbor.com/login/
"""

from pages.base_page import BasePage


class LoginPage(BasePage):

    URL = "/login/"

    # ── Selectors — scoped to the JetFormBuilder login form ─────────────────────
    # The page has 2 submit buttons (Login + Subscribe); use the specific class
    EMAIL_INPUT    = "#email"
    PASSWORD_INPUT = "#password"
    SUBMIT_BUTTON  = "button.jet-form-builder__submit"
    ERROR_MESSAGE  = ".jet-form-builder__message--error, .woocommerce-error, .login-error, .notice-error"

    # Known post-login URL patterns (the site may redirect to any of these)
    _LOGGED_IN_PATHS = (
        "/candidate-dashboard",
        "/recruiter-dashboard",
        "/my-account",
        "/wp-admin",
        "/dashboard",
        "/jobs",
    )

    def open(self, base_url: str):
        self.navigate(base_url + self.URL)

    def _fill_field(self, selector: str, value: str):
        """Fill a field; if the selector doesn't exist, fall back to nth input."""
        loc = self.page.locator(selector)
        if loc.count() > 0:
            loc.fill(value)
        else:
            # fallback: fill by input order (0=username, 1=password)
            inputs = self.page.locator("input[type='text'], input[type='email'], "
                                       "input[type='tel'], input[type='password']")
            idx = 0 if selector == self.EMAIL_INPUT else 1
            if inputs.count() > idx:
                inputs.nth(idx).fill(value)

    def login(self, username: str, password: str):
        self._fill_field(self.EMAIL_INPUT, username)
        self._fill_field(self.PASSWORD_INPUT, password)

        # Click the JetFormBuilder login submit button specifically
        btn = self.page.locator(self.SUBMIT_BUTTON)
        if btn.count() == 0:
            # fallback: match by button text "Login"
            btn = self.page.get_by_role("button", name="Login")
        btn.first.click()

        # Wait for navigation away from /login/ OR wait for domcontentloaded
        try:
            self.page.wait_for_url(
                lambda url: "/login/" not in url,
                timeout=8_000,
            )
        except Exception:
            self.page.wait_for_load_state("domcontentloaded")

    def get_error_message(self) -> str:
        for sel in self.ERROR_MESSAGE.split(", "):
            loc = self.page.locator(sel.strip())
            if loc.count() > 0 and loc.first.is_visible():
                return loc.first.inner_text().strip()
        if "status" in self.page.url or "error" in self.page.url:
            return "login_error_in_url"
        return ""

    def is_logged_in(self) -> bool:
        """
        True when the current URL indicates a successful login.
        Checks both positive signals (known dashboard paths) and
        negative signals (not still on the login page).
        """
        current = self.page.url.lower()

        # Positive: we're on a known authenticated page
        for path in self._LOGGED_IN_PATHS:
            if path in current:
                return True

        # Positive: we left /login/ and there's no error indicator in URL
        if "/login/" not in current and "error" not in current and "status" not in current:
            # Make sure we're still on the same domain (not a random page)
            if "labsqajobs.qaharbor.com" in current:
                return True

        return False

    def logout(self, base_url: str = None):
        """Click logout link and handle any 'Are you sure?' confirmation pages."""
        # 1. Try to find and click a visible logout link
        logout_selectors = [
            "a[href*='logout']",
            "a:has-text('Logout')",
            "a:has-text('Log out')",
            ".logout-link"
        ]
        
        clicked = False
        for sel in logout_selectors:
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click()
                clicked = True
                break
        
        # 2. If nothing clicked, try a direct navigation to logout (risky due to nonces)
        if not clicked and base_url:
            self.page.goto(base_url + "/wp-login.php?action=logout", wait_until="domcontentloaded")
            clicked = True

        # 3. Handle 'Are you sure you want to log out?' confirmation page
        confirm_link = self.page.locator("a[href*='_wpnonce'], a:has-text('log out')").first
        if confirm_link.count() > 0 and confirm_link.is_visible():
            confirm_link.click()
            
        self.page.wait_for_load_state("networkidle", timeout=5000)
        self.page.wait_for_load_state("domcontentloaded")
