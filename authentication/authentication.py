from argon2 import PasswordHasher
import re

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
    if not any (char in "!£$%^&*()[]{}:;@'~#<>,.?/|" for char in password):
        return False
    return True

def check_valid_email(email):
    regex_string = "^[A-Za-z0-9.]+@makeitall.com$"
    if re.match(regex_string,email):
        return True
    else:
        return False
        
def password_hash(password):
    return ph.hash(password)  