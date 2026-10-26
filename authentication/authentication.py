import re

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

ph = PasswordHasher()

def check_strong_password(password):
    if (len(password) < 8):
        return False
        ##logic
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!£$%^&*()[]{}:;@'~#<>,.?/|" for char in password):
        return False
    return True

def check_valid_email(email):
    return re.fullmatch(r"[A-Za-z0-9.]+@makeitall\.com", email) is not None
        
def password_hash(password):
    return ph.hash(password) 
def verify_password(storedpassword, enteredpassword):
    try:
        return ph.verify(storedpassword, enteredpassword)
    except (VerificationError, InvalidHashError):
        return False