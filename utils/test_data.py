"""
test_data.py — Static credentials and dynamic data generators
for https://labsqajobs.qaharbor.com
"""

import uuid
import random
import string

# ── Valid credentials (provided by QA Harbor) ─────────────────────────────────
VALID_USER = {
    "username": "01625568609",
    "password": "secret",
}

# ── Invalid / edge-case data ───────────────────────────────────────────────────
INVALID_EMAIL    = "not-an-email"
SHORT_PASSWORD   = "123"
WRONG_PASSWORD   = "WrongPass@999"
BLANK            = ""
INVALID_PHONE    = "abc_xyz"

# ── Dynamic generators ─────────────────────────────────────────────────────────

def unique_email(prefix: str = "user") -> str:
    """Generate a unique email using a UUID8 suffix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}@mailinator.com"


def unique_username(prefix: str = "user") -> str:
    uid = uuid.uuid4().hex[:6]
    return f"{prefix}{uid}"


def random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits
    return "Qa1!" + "".join(random.choices(chars, k=length - 4))


def random_phone() -> str:
    return "017" + "".join(random.choices(string.digits, k=8))
