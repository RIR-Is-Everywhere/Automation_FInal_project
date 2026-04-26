"""
jobs_page.py — Job search, filter, and save actions
for https://labsqajobs.qaharbor.com/jobs/
"""

from pages.base_page import BasePage


class JobsPage(BasePage):

    URL = "/jobs/"

    # ── Selectors ──────────────────────────────────────────────────────────────
    SEARCH_INPUT   = "input[name='search_keywords']"
    SEARCH_BUTTON  = "button[type='submit']"
    LOCATION_INPUT = "input[name='search_location']"
    JOB_CARDS      = ".job_listing"
    JOB_TITLE      = ".job_listing .position h3"
    SAVE_BUTTON    = ".job_listing .save-job"
    NO_RESULTS     = ".no_jobs_found"

    def open(self, base_url: str):
        self.navigate(base_url + self.URL)

    def search_by_keyword(self, keyword: str):
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")

    def search_by_location(self, location: str):
        self.fill(self.LOCATION_INPUT, location)
        self.click(self.SEARCH_BUTTON)
        self.page.wait_for_load_state("domcontentloaded")

    def get_job_count(self) -> int:
        return self.page.locator(self.JOB_CARDS).count()

    def save_first_job(self):
        self.page.locator(self.SAVE_BUTTON).first.click()
        self.page.wait_for_load_state("domcontentloaded")

    def has_no_results(self) -> bool:
        return self.is_visible(self.NO_RESULTS)

    def get_first_job_title(self) -> str:
        return self.get_text(self.JOB_TITLE)
