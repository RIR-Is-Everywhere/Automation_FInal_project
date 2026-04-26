"""
base_page.py — Parent class with shared Playwright actions.
"""


class BasePage:
    def __init__(self, page):
        self.page = page

    # ── Navigation ─────────────────────────────────────────────────────────────

    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")

    def wait_for_url(self, pattern: str, timeout: int = 10_000):
        self.page.wait_for_url(f"**{pattern}**", timeout=timeout)

    # ── Interactions ───────────────────────────────────────────────────────────

    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str):
        self.page.locator(selector).fill(value)

    def select_option(self, selector: str, label: str):
        self.page.locator(selector).select_option(label=label)

    # ── Assertions helpers ─────────────────────────────────────────────────────

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def is_visible(self, selector: str, timeout: int = 5_000) -> bool:
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_url(self) -> str:
        return self.page.url
