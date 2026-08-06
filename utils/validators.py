"""
validators.py

Reusable validation helpers used across all forms.
"""

import re

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s-]{10,15}$")
STRONG_PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
ROLL_NUMBER_REGEX = re.compile(r"^[A-Za-z0-9/\-]{5,20}$")
RESUME_ALLOWED_EXTENSIONS = {"pdf"}


def is_valid_email(email):
    return bool(email) and bool(EMAIL_REGEX.match(email.strip()))


def is_valid_phone(phone):
    return bool(phone) and bool(PHONE_REGEX.match(phone.strip()))


def is_strong_password(password):
    return bool(password) and bool(STRONG_PASSWORD_REGEX.match(password))


def is_valid_roll_number(roll_number):
    return bool(roll_number) and bool(ROLL_NUMBER_REGEX.match(roll_number.strip()))


def is_valid_cgpa(cgpa):
    return isinstance(cgpa, (int, float)) and 0.0 <= cgpa <= 10.0


def has_pdf_extension(filename):
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in RESUME_ALLOWED_EXTENSIONS


def clean_skills(skills):
    """Normalise a comma-separated skill list into a clean comma string."""
    if not skills:
        return None
    items = [s.strip() for s in skills.split(",") if s.strip()]
    if not items:
        return None
    return ", ".join(items[:50])
