"""
test_TC006_performance.py
==========================
Test Scenario : Performance
TC-ID         : TC_006
Title         : Performance – Load & Stress Behavior
Preconditions : System active
Site          : https://labsqajobs.qaharbor.com
"""

import time
import pytest
from pages.login_page import LoginPage
from utils.test_data import VALID_USER

MAX_LOAD_TIME_SEC = 5   # pages should load within 5 seconds


class TestTC006Performance:

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1 – Load homepage multiple times
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1_homepage_load_time(self, page, base_url):
        """
        Step        : Load the homepage 3 times, measure average load time
        Expected    : Each load completes within 5 seconds
        """
        load_times = []
        for _ in range(3):
            start = time.time()
            page.goto(base_url, wait_until="domcontentloaded")
            elapsed = time.time() - start
            load_times.append(elapsed)

        avg = sum(load_times) / len(load_times)
        assert avg <= MAX_LOAD_TIME_SEC, (
            f"Average homepage load time {avg:.2f}s exceeds {MAX_LOAD_TIME_SEC}s limit. "
            f"Individual loads: {[f'{t:.2f}s' for t in load_times]}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1b – Login page load time
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1b_login_page_load_time(self, page, base_url):
        """
        Step        : Load the login page and measure time to interactive
        Expected    : Loads within 5 seconds
        """
        start = time.time()
        page.goto(base_url + "/login/", wait_until="domcontentloaded")
        elapsed = time.time() - start
        assert elapsed <= MAX_LOAD_TIME_SEC, (
            f"Login page took {elapsed:.2f}s — exceeds {MAX_LOAD_TIME_SEC}s limit."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1c – Jobs listing page load time
    # ──────────────────────────────────────────────────────────────────────────
    def test_step1c_jobs_page_load_time(self, page, base_url):
        """
        Step        : Load the jobs listing page
        Expected    : Loads within 5 seconds
        """
        start = time.time()
        page.goto(base_url + "/jobs/", wait_until="domcontentloaded")
        elapsed = time.time() - start
        assert elapsed <= MAX_LOAD_TIME_SEC, (
            f"Jobs page took {elapsed:.2f}s — exceeds {MAX_LOAD_TIME_SEC}s limit."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2 – Submit form with heavy / large data
    # ──────────────────────────────────────────────────────────────────────────
    def test_step2_heavy_form_data_handled(self, page, base_url):
        """
        Step        : Submit login form with very long strings in fields
        Expected    : System handles gracefully — no crash or timeout
        Note        : Heavy input (5000 chars) takes longer; allow up to 15s
        """
        login = LoginPage(page)
        login.open(base_url)
        long_string = "A" * 5000
        start = time.time()
        login.login(long_string, long_string)
        elapsed = time.time() - start
        assert elapsed <= 15, (
            f"Long-input login took {elapsed:.2f}s — system too slow or hung."
        )
        assert page.title() is not None, "Page crashed after heavy input."

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3 – Simulate rapid consecutive page loads (stress)
    # ──────────────────────────────────────────────────────────────────────────
    def test_step3_rapid_page_loads_stay_stable(self, page, base_url):
        """
        Step        : Rapidly navigate between 5 pages in sequence
        Expected    : System remains stable, no crash or freeze
        """
        pages_to_visit = [
            base_url + "/",
            base_url + "/login/",
            base_url + "/jobs/",
            base_url + "/candidate-registration/",
            base_url + "/recruiter-registration/",
        ]
        for url in pages_to_visit:
            page.goto(url, wait_until="domcontentloaded", timeout=15_000)
            assert page.title() is not None, f"Page crashed when visiting: {url}"
