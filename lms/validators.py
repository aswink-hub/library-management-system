"""Input validation helpers for the Library Management System."""
import re


class ValidationError(ValueError):
    """Raised when user input fails validation."""


_ISBN_RE = re.compile(r"^\d{10}(\d{3})?$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\d{10}$")


def require_text(value, field, max_len=100):
    """Return a stripped non-empty string no longer than max_len."""
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} cannot be empty.")
    value = str(value).strip()
    if len(value) > max_len:
        raise ValidationError(f"{field} must be at most {max_len} characters.")
    return value


def validate_isbn(isbn):
    """ISBN must be 10 or 13 digits (hyphens and spaces are ignored)."""
    cleaned = str(isbn).replace("-", "").replace(" ", "")
    if not _ISBN_RE.match(cleaned):
        raise ValidationError("ISBN must contain 10 or 13 digits.")
    return cleaned


def validate_copies(copies):
    """Number of copies must be an integer between 1 and 1000."""
    try:
        copies = int(copies)
    except (TypeError, ValueError):
        raise ValidationError("Copies must be a whole number.")
    if not 1 <= copies <= 1000:
        raise ValidationError("Copies must be between 1 and 1000.")
    return copies


def validate_email(email):
    email = require_text(email, "Email", 120).lower()
    if not _EMAIL_RE.match(email):
        raise ValidationError("Email address is not valid.")
    return email


def validate_phone(phone):
    phone = str(phone).strip()
    if not _PHONE_RE.match(phone):
        raise ValidationError("Phone number must be exactly 10 digits.")
    return phone


def validate_id(value, field="ID"):
    try:
        value = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number.")
    if value <= 0:
        raise ValidationError(f"{field} must be a positive number.")
    return value
