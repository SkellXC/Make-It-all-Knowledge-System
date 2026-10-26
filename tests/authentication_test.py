"""Checks on authentication/authentication.py."""
from authentication.authentication import (
    check_strong_password,
    check_valid_email,
    password_hash,
    verify_password,
)


def test_strong_password_accepts_a_good_one():
    assert check_strong_password("Abcdef1!")


def test_strong_password_rejects_each_missing_rule():
    assert not check_strong_password("Abcde1!")      # shorter than 8
    assert not check_strong_password("abcdefg1!")    # no uppercase
    assert not check_strong_password("ABCDEFG1!")    # no lowercase
    assert not check_strong_password("Abcdefgh!")    # no digit
    assert not check_strong_password("Abcdefg12")    # no special character


def test_company_email_is_accepted():
    assert check_valid_email("alex.smith@makeitall.com")


def test_other_domains_are_rejected():
    assert not check_valid_email("alex@gmail.com")
    assert not check_valid_email("alex@makeitall.com.evil.com")
    assert not check_valid_email("@makeitall.com")


def test_hash_is_argon2_and_verifies():
    hashed = password_hash("Password1!")
    assert hashed.startswith("$argon2")
    assert verify_password(hashed, "Password1!")


def test_wrong_password_does_not_verify():
    hashed = password_hash("Password1!")
    assert not verify_password(hashed, "password1!")