from authentication.authentication import verify_password
from database.database import get_employee_by_email, get_permissions_for_role


def login_user(email, password):
    employee = get_employee_by_email(email)

    if employee is None:
        return None

    stored_password = employee[5]

    if not verify_password(stored_password,password):
        return None
        

    return {
        "id":employee[0],
        "first_name":employee[1],
        "second_name":employee[2],
        "email":employee[3],
        "username":employee[4],
        "role":employee[6],
        "icon":employee[7],
        "permissions":get_permissions_for_role(employee[6])
    }


    