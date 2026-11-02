from authentication.authentication import check_strong_password, check_valid_email
from authentication.login_backend import login_user
from database.database import add_employee, get_employee_by_email, get_employee_by_username

EMAIL_FORMAT_ERROR = "Email must be a valid address ending in makeitall.com"
EMAIL_EXISTS_ERROR = "An account with this email already exists. Please log in."
PASSWORD_ERROR = (
    "Password needs 8+ characters with an uppercase letter, "
    "a lowercase letter, a number and a symbol."
)


def validate_registration(first_name, second_name, email, username, password, confirm_password):
    """Returns {field: error message}. An empty dict means everything is valid.

    Field keys: first_name, second_name, email, username, password, confirm_password.
    """
    errors = {}

    if not first_name:
        errors["first_name"] = "First name is required."
    if not second_name:
        errors["second_name"] = "Last name is required."

    if not email:
        errors["email"] = "Email is required."
    elif not check_valid_email(email):
        errors["email"] = EMAIL_FORMAT_ERROR
    elif get_employee_by_email(email) is not None:
        errors["email"] = EMAIL_EXISTS_ERROR

    if not username:
        errors["username"] = "Username is required."
    elif get_employee_by_username(username) is not None:
        errors["username"] = "That username is already taken."

    if not password:
        errors["password"] = "Password is required."
    elif not check_strong_password(password):
        errors["password"] = PASSWORD_ERROR

    if "password" not in errors and password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    return errors


def register_user(first_name, second_name, email, username, password, confirm_password):
    """Validates the form and, if it is all valid, creates the account.

    Returns (user, errors):
      - success: (user dict in the same shape login_user() returns, {})
      - failure: (None, {field: error message})

    The database assigns the new user id (AUTOINCREMENT), and every new
    account gets the default "employee" role. Roles are never chosen here.
    """
    first_name = first_name.strip()
    second_name = second_name.strip()
    email = email.strip().lower()   # login lowercases emails too, so they must match
    username = username.strip()

    errors = validate_registration(
        first_name, second_name, email, username, password, confirm_password
    )
    if errors:
        return None, errors

    # add_employee() hashes the password with argon2 and returns the new id.
    add_employee(first_name, second_name, email, username, password)

    return login_user(email, password), {}