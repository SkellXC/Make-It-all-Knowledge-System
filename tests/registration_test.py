"""Checks on authentication/registration_backend.py and the registration flow."""
import pytest

from authentication.authentication import verify_password
from authentication.registration_backend import (
    EMAIL_EXISTS_ERROR,
    EMAIL_FORMAT_ERROR,
    register_user,
)

GOOD = dict(
    first_name="Jane",
    second_name="Doe",
    email="jane.doe@makeitall.com",
    username="jane_doe",
    password="Password1!",
    confirm_password="Password1!",
)


def test_valid_registration_creates_an_employee_with_a_new_id(db):
    user, errors = register_user(**GOOD)

    assert errors == {}
    assert user["email"] == "jane.doe@makeitall.com"
    assert user["role"] == "employee"
    stored = db.get_employee_by_email("jane.doe@makeitall.com")
    assert stored[0] == user["id"]
    assert stored[5].startswith("$argon2")
    assert verify_password(stored[5], "Password1!")


def test_each_new_account_gets_a_different_id(db):
    first, _ = register_user(**GOOD)
    second, _ = register_user(**{**GOOD, "email": "joe.doe@makeitall.com", "username": "joe"})

    assert first["id"] != second["id"]


def test_email_is_saved_in_lowercase(db):
    user, _ = register_user(**{**GOOD, "email": "  Jane.Doe@MakeItAll.com "})

    assert user["email"] == "jane.doe@makeitall.com"


@pytest.mark.parametrize("email", ["jane@gmail.com", "jane@makeitall.com.evil.com", "jane"])
def test_wrong_email_domain_is_rejected(db, email):
    user, errors = register_user(**{**GOOD, "email": email})

    assert user is None
    assert errors["email"] == EMAIL_FORMAT_ERROR
    assert db.get_employee_by_email(email) is None


def test_existing_email_asks_the_user_to_log_in(accounts):
    user, errors = register_user(**{**GOOD, "email": "alex.smith@makeitall.com"})

    assert user is None
    assert errors["email"] == EMAIL_EXISTS_ERROR


def test_existing_username_is_rejected(accounts):
    user, errors = register_user(**{**GOOD, "username": "Alex_Smith"})

    assert user is None
    assert "username" in errors


def test_weak_password_is_rejected(db):
    user, errors = register_user(**{**GOOD, "password": "weak", "confirm_password": "weak"})

    assert user is None
    assert "password" in errors


def test_mismatched_passwords_are_rejected(db):
    user, errors = register_user(**{**GOOD, "confirm_password": "Different1!"})

    assert user is None
    assert "confirm_password" in errors


def test_empty_fields_are_reported(db):
    user, errors = register_user("", "", "", "", "", "")

    assert user is None
    assert set(errors) == {"first_name", "second_name", "email", "username", "password"}
