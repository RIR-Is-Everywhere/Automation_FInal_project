"""
helpers.py — Unique candidate / recruiter data generators + shared login helper.
"""

import time
from utils.test_data import (
    VALID_USER, random_password, random_phone,
    unique_email, unique_username,
)


def generate_candidate() -> dict:
    """Return a unique candidate registration payload."""
    ts = int(time.time())
    return {
        "username"        : f"candidate_{ts}",
        "email"           : f"candidate_{ts}@mailinator.com",
        "phone"           : random_phone(),
        "password"        : random_password(),
    }


def generate_recruiter() -> dict:
    """Return a unique recruiter registration payload."""
    ts = int(time.time())
    return {
        "company"   : f"Company_{ts}",
        "email"     : f"recruiter_{ts}@mailinator.com",
        "phone"     : random_phone(),
        "password"  : random_password(),
    }


def ensure_login(page, base_url) -> tuple:
    """
    Guarantee a logged-in session.  Returns (username, password) that worked.

    Strategy:
      1. Try VALID_USER credentials (fast path — works if account exists).
      2. If that fails, register a fresh dummy account then log in with it.
    """
    from pages.login_page import LoginPage
    from pages.registration_page import RegistrationPage

    lp = LoginPage(page)
    lp.open(base_url)
    lp.login(VALID_USER["username"], VALID_USER["password"])
    if lp.is_logged_in():
        return VALID_USER["username"], VALID_USER["password"]

    # ── Fallback: register a new dummy account ─────────────────────────────
    dummy_username = unique_username("qa")
    dummy_email    = unique_email("qa")
    dummy_password = random_password()

    reg = RegistrationPage(page)
    reg.open_candidate(base_url)
    reg.register_candidate(
        username=dummy_username,
        email=dummy_email,
        password=dummy_password,
        confirm_password=dummy_password,
    )
    try:
        page.wait_for_load_state("networkidle", timeout=8_000)
    except Exception:
        page.wait_for_load_state("domcontentloaded")

    # Now login with the new account
    try:
        lp.open(base_url)
    except Exception:
        page.wait_for_load_state("domcontentloaded")
        lp.open(base_url)

    lp.login(dummy_username, dummy_password)
    return dummy_username, dummy_password
