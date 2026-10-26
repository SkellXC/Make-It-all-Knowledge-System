import os
print("cwd:", os.getcwd())

from database.database import get_employee_by_email, database_connection
print("db path:", os.path.abspath(database_connection),
      "| exists:", os.path.exists(database_connection))

emp = get_employee_by_email("alex.smith@makeitall.com")
print("employee found:", emp is not None)

if emp:
    stored = emp[5]
    print("stored value starts with:", stored[:20])
    from authentication.authentication import ph
    try:
        print("verify result:", ph.verify(stored, "password"))
    except Exception as error:
        print("verify raised:", type(error).__name__, error)