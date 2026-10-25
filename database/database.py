import sqlite3
from authentication.authentication import password_hash

database_connection = "database/database.db"

def get_database_connection():
    return(sqlite3.connect(database_connection))


def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    employee_type TEXT NOT NULL 
    CHECK (employee_type IN (
        "employee",
        "team leader",
        "manager",
        "administrator"
        ))
    )
    """
    )
    connection.commit()
    connection.close()

    def get_employee_by_email(email):
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("""
        SELECT * FROM employee WHERE email = ?
        """,
        (email,))
        employee = cursor.fetchall()

        connection.close()

        return employee

    def verify_employee_password(email, password):
        employee = get_employee_by_email(email)

        if employee is None:
            return None

        stored_password = employee[5]

        try:
            password_hash.verify(stored_password,password)
            return employee
        except Exception:
            return None



###Basis to provide test data for the database for testing purposes
def add_simulated_data_to_db():
    connection = get_database_connection()
    cursor = connection.cursor()
    password1 = password_hash("Employee1?")
    password2 = password_hash("TeamLeader1?")
    password3 = password_hash("Administrator1?")
    password4 = password_hash("Manager1?")

    cursor.execute("""
    INSERT INTO employees (first_name, second_name, email,
    username, password, employee_type)
    VALUES (?,?,?,?,?,?)""",
    (
        ("Alex",
         "Smith",
         "alex.smith@makeitall.com",
         "alex_smith",
         password1,
         "employee" 
         
        )
    )
    )
    cursor.execute("""
        INSERT INTO employees (first_name, second_name, email,
        username, password, employee_type)
        VALUES (?,?,?,?,?,?)""",
        (
            ("John",
             "Paul",
             "john.paul@makeitall.com",
             "john_paul",
             password2,
             "team leader" 
             
            )
        )
        )
    cursor.execute("""
       INSERT INTO employees (first_name, second_name, email,
       username, password, employee_type)
       VALUES (?,?,?,?,?,?)""",
       (
           ("Sarah",
            "Jones",
            "sarah.jones@makeitall.com",
            "sarah_jones",
            password3,
            "manager" 
            
           )
       )
       )
    cursor.execute("""
        INSERT INTO employees (first_name, second_name, email,
        username, password, employee_type)
        VALUES (?,?,?,?,?,?)""",
        (
            ("Admin",
             "1",
             "admin@makeitall.com",
             "admin",
             password4,
             "administrator" 
             
            )
        )
        )
    connection.commit()
    connection.close()



create_tables()
#Added the simulated once (23.10.2026 15:10 ANORBS), now commented out
#add_simulated_data_to_db()
def select_all_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * FROM employees
    """)
    data = cursor.fetchall()
    return data

print(select_all_data())

